import time

# Record the start time
start_time = time.time()

# Import necessary libraries
import numpy as np
import flopy
from VerticalRefinment import VerticalRefinement
from conversions import ParametersConversions
import pandas as pd
from Units import UnitConverter
from Plotter import ObservedVsSimulatedPlotter
import os
from ColumnCalculator import ColumnCalculator
from scipy.optimize import fmin
from DrawdownInterpolation import DrawdownInterpolation

converter = UnitConverter()

# Create Results folder if it doesn't exist
os.makedirs('Results', exist_ok=True)

calib_df=pd.read_excel(r"Model_Inputs.xlsx")

# Add a flag to control the mode (forward run or optimization)
run_type = calib_df.at[39,'Value']  # Set to True for forward run, False for optimization
# Hydraulic Parameters
# Primary Hydraulic properties
VANI = calib_df.at[33, 'Value']  # Vertical anisotropy (Vk/Hk)
sy = calib_df.at[34, 'Value'] # Specific yield
ss = calib_df.at[35, 'Value']  # Specific storage

# Function to run the forward model
def run_forward_model(**kwargs):
    # Model Inputs
    input_df=pd.read_excel(r"Model_Inputs.xlsx")
    #Original values from excel sheet
    default_values ={'sy': input_df.at[34, 'Value'], 'ss': input_df.at[35, 'Value']}
    # Read hydraulic conductivity values from a separate sheet
    hk_df = pd.read_excel(r"Model_Inputs.xlsx", sheet_name='Hydraulic Conductivity')
    hk_profile = {(row['Layer Top Level [m]'], row['Layer Bottom Level [m]']): row['Hydraulic Conductivity [m/day]']
                  for index, row in hk_df.iterrows() if not pd.isnull(row['Layer Top Level [m]'])}

    # Update kwargs with the hk_profile if it's not already provided
    kwargs.setdefault('hk_profile', hk_profile)
    
    # Update defaults with any parameters passed to the function
    params = {**default_values, **kwargs}    
    
    # Extract the specific parameters from the params dictionary
    sy = params['sy']
    ss = params['ss']
    hk_profile = params['hk_profile']

    # Define the Model Extent, Grid Resolution, and Characteristics for Axisymmetric Flow
    nrow = 1  # Number of rows
    col_length = input_df.at[1, 'Value']   # Distance of boundary from pumping well
    # Define the vertical properties
    ztop = input_df.at[5, 'Value']  # Top elevation of top layer
    zbot = input_df.at[6, 'Value']  # Bottom elevation of the last layer
    sc_top = input_df.at[15, 'Value']
    sc_bottom = input_df.at[16, 'Value']
    sc_top_thick = input_df.at[7, 'Value']
    sc_bottom_thick = input_df.at[8, 'Value']
    refine_above_screen=input_df.at[9, 'Value']
    refine_below_screen=input_df.at[10, 'Value']
    refine_between_screen=input_df.at[11, 'Value']
    # Define horizontal desctritization data
    radius_well=input_df.at[13, 'Value']
    cell_size=input_df.at[2, 'Value']
    horizontal_multiplier=input_df.at[3, 'Value']
    #Specified Head
    specified_head = input_df.at[23, 'Value']  # Head value for the specified head boundary
    # Pumng Rate
    Q_m3_hr = input_df.at[14, 'Value'] #m³/hr
    Q = converter.cubic_m_per_hour_to_cubic_m_per_sec(Q_m3_hr)
    
    ##################################################################################################
    # Define Observation Wells
    # Read the Excel file to determine the number of observation wells
    # For this, read only the relevant row where the observation well IDs are located (assuming this is row 18)
    obs_well_ids = pd.read_excel(r"Model_Inputs.xlsx", skiprows=18, nrows=1, header=None).values.flatten()
    # Filter out non-observation well entries (like NaNs)
    obs_well_ids = [id for id in obs_well_ids if not pd.isna(id) and str(id).startswith('OBS')] 
    # Read the observation wells data
    obs_wells_data = pd.read_excel(r"Model_Inputs.xlsx", skiprows=18, usecols=lambda x: 'Unnamed' not in x, nrows=3)
    # The above usecols argument with lambda function will skip columns with 'Unnamed' in the header
    # Transpose the DataFrame to have wells as rows and reset index
    obs_wells_data = obs_wells_data.T.reset_index(drop=True) 
    # Slice the DataFrame to only include existing wells based on the IDs detected
    obs_wells_data = obs_wells_data.iloc[:len(obs_well_ids)+1]
    obs_wells_data.columns = ['Observation Well Distance (m)', 'Observation Top Screen Level (m)', 'Observation Bottom Screen Level (m)']
    #drop index zero
    obs_wells_data.drop(index=0, inplace=True)
    # Insert a column with well IDs at the beginning of the DataFrame
    obs_wells_data.insert(0, 'Well ID', obs_well_ids)
    #################################################################################################################
    
    # Analysis Period => Pumping Only or Recovery Only or Pumping+Recovery
    analysis_period = input_df.at[25, 'Value']  # New cell location might need adjustment
    if analysis_period == "Pumping Only":
        include_pumping = True
        include_recovery = False
    elif analysis_period == "Recovery Only":
        include_pumping = False
        include_recovery = True
    else:  # "Pumping + Recovery"
        include_pumping = True
        include_recovery = True
        
    # Adjust the number of stress periods based on the selected analysis period
    if analysis_period == "Pumping Only":
        Number_Stress_Periods = 1  # Only pumping period
    elif analysis_period == "Recovery Only":
        Number_Stress_Periods = 1  # Only recovery period, but you might need special handling to set this up correctly
    elif analysis_period == "Pumping + Recovery":  # "Pumping + Recovery"
        Number_Stress_Periods = 2  # Both pumping and recovery periods
        
    length_min=input_df.at[26, 'Value']  # Time in minutes
    length_stress_period_pumping =converter.minutes_to_sec(length_min)   # Length of pumping time in days
    length_recovery_min = input_df.at[27, 'Value']  # Adjust the length for recovery
    length_stress_period_recovery =converter.minutes_to_sec(length_recovery_min)   # Length of pumping time in days
    NTSP = input_df.at[28, 'Value']  # Number of time steps
    TSMULT = input_df.at[29, 'Value']  # Multiplier
    T_Unit = input_df.at[30, 'Value'] #Units of time (“seconds”, “minutes”, “hours”, “days”, or “years”.)

    # Create an instance for vertical refinment
    vr = VerticalRefinement(ztop, zbot, sc_top, sc_bottom, sc_top_thick, sc_bottom_thick,
                            refine_above_screen, refine_below_screen, refine_between_screen)
    top, bottom, thickness = vr.calculate_thicknesses()
    # Number of layers
    nlay=len(top)

    # Create an instance of the ColumnCalculator class
    column_calculator = ColumnCalculator(col_length,radius_well ,cell_size, horizontal_multiplier)

    # Calculate Number of columns and column parameters
    delr, cumulative_distances, col_centroids, ncol = column_calculator.calculate_columns()

    #Define hydraulic parameters
    # Iterate through hk_profile and update the Hk values to m/sec
    hk_profile_m_sec = {depth_range: converter.meters_per_day_to_meters_per_sec(hk) for depth_range, hk in hk_profile.items()}
    laytyp = 3  # Layer type (1 for unconfined)
    
    #################################################################################################################################
    # Initialize a list to store Hk values for each layer
    hk_values = []  # Initialize a list to store Hk values for each layer
    
    # Calculate the midpoint depth of each layer and assign an Hk value
    for i in range(len(top)):
        layer_midpoint = (top[i] + bottom[i]) / 2
        
        for depth_range, hk_value in hk_profile_m_sec.items():
            if depth_range[0] >= layer_midpoint > depth_range[1]:
                hk_values.append(hk_value)
                break  # Exit the loop once a match is found

####################################################################################################################################

    # Calculated converted parameters to convert to Axisymmetric grid
    par=ParametersConversions(col_centroids, delr, thickness)
    par.set_original_parameters(hk_values, sy, ss)
    hk_con, sy_con, ss_con=par.calculate_converted_parameters()
    # Define values for hk, sy, and ss
    sy_values=[]

    # Create a list of lists for Sy where each sub-list represents layer values
    for lay in range(nlay):
        sy_values.append(sy_con)
    ss_values = ss_con
      
    # Path for the workspace and mf6.exe
    workspace = r'workspace'  # Specify your desired directory path
    mf6_exe = "./mf6"  # Path to mf6.exe

    # Create a MODFLOW 6 simulation object
    sim = flopy.mf6.MFSimulation(
        sim_name="axisymmetric_model", exe_name=mf6_exe, sim_ws=workspace
    )

# Define the time discretization (tdis) for stress periods based on analysis_period
    perioddata1 = []
    if include_pumping and not include_recovery:
        perioddata1.append((length_stress_period_pumping, NTSP, TSMULT))
    elif include_recovery and not include_pumping:
        perioddata1.append((length_stress_period_recovery, NTSP, TSMULT))
    else:
        perioddata1=[
            (length_stress_period_pumping, NTSP, TSMULT),  # Stress period 1 (pumping)
            (length_stress_period_recovery, NTSP, TSMULT),  # Stress period 2 (recovery)
        ]
    tdis = flopy.mf6.ModflowTdis(
        sim,
        pname="tdis",
        time_units = T_Unit, 
        nper=Number_Stress_Periods,  # Define 2 stress periods
        perioddata=perioddata1
        
    )

    # Create a MODFLOW 6 groundwater flow (gwf) model within the simulation
    gwf = flopy.mf6.ModflowGwf(
        sim,
        modelname="ax_model",
        save_flows=True,
    )

    # Well Screen
    sc_top_id=top.index(sc_top)
    sc_bottom_id=bottom.index(sc_bottom)
    sc_layers=(sc_bottom_id-sc_top_id)+1


    # Initialize a list to store the flux for each layer
    layer_fluxes = []

    # Distribute the flux based on transmissivity ratios
    for thick in thickness[sc_top_id:sc_bottom_id+1]:
        layer_flux = Q * (thick / (sc_top - sc_bottom))
        layer_fluxes.append(layer_flux)

    # Define the initial head conditions
    str_hd = input_df.at[22, 'Value'] # Initial Condition (Starting Head)
    observed_drawdown_end_of_pumping = input_df.at[37, 'Value']
    # Adjusting the initial condition for "Recovery Only" scenario
    if analysis_period == "Recovery Only":
        final_heads_filename = os.path.join(workspace, "final_heads_pumping.npy")
    
        if os.path.exists(final_heads_filename):
            # Load the saved heads as initial conditions
            strt = np.load(final_heads_filename)
        else:
            print("Pumping period run should be done first...")
            return
    else:
        # For other analysis periods, use the specified starting head
        strt = str_hd * np.ones((nlay, nrow, ncol), dtype=np.float32)
        

    # Define the spatial discretization (the grid)
    dis = flopy.mf6.ModflowGwfdis(
        gwf,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=1.0,  # Adjust delc for 1 column
        top=ztop,
        botm=bottom  # Define layer bottoms
    )

    # Define the basic package
    ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
    
    # Create the constant head boundary condition for the last layer in the last column
    chd_data = []
    # Create the constant head boundary condition for the last column
    chd_data.append([(nlay-1, 0, ncol - 1), specified_head]) #assign specified head for the last layer only

    #for stress_period in range(Number_Stress_Priods):
        #chd_data.append([(nlay-1, 0, ncol - 1), specified_head])

    # Define the stress period data using perioddata
    perioddata = {i: chd_data for i in range(Number_Stress_Periods)}

    chd = flopy.mf6.ModflowGwfchd(gwf, stress_period_data=perioddata)

    # Define the LPF package
    VANI = input_df.at[33, 'Value']  # Vertical anisotropy (Vk/Hk)
    lpf = flopy.mf6.ModflowGwfnpf(
        gwf, 
        icelltype=laytyp,
        k33overk=True,
        k=hk_con, 
        k33=VANI, 
        save_flows=True,
        alternative_cell_averaging = "LOGARITHMIC",
        cvoptions="DEWATERED",
    )

    # Define the initial condition package
    ic = flopy.mf6.ModflowGwfic(gwf, strt=strt)
    # Create the well package
    # Define the column and layer for the well
    col = 0  # First column (0-based index)
    layer_start = sc_top_id  # Starting layer number
    layer_end = sc_bottom_id    # Ending layer number

   # Determine the analysis period and initialize stress_period_data accordingly
    analysis_period = input_df.at[25, 'Value']
    if analysis_period == "Pumping Only":
        stress_period_data = {0: []}  # Only pumping period
    elif analysis_period == "Recovery Only":
        stress_period_data = {0: []}  # Only recovery period; you might simulate it as a single period for simplicity
    elif analysis_period == "Pumping + Recovery":
        stress_period_data = {0: [], 1: []}  # Both pumping and recovery periods

# Loop through the layers and create entries in stress_period_data
    for lay, lay_flux in enumerate(layer_fluxes):
        lay += sc_top_id  # Adjust the layer index to start from the screen layer
    
        if analysis_period in ["Pumping Only", "Pumping + Recovery"]:
            # Specify the well coordinates and rate for each layer in stress period 1 (pumping)
            stress_period_entry_pumping = [lay, 0, col, lay_flux]  # m³/sec for pumping period
            stress_period_data[0].append(stress_period_entry_pumping)  # Add to stress period 1
    
        if analysis_period == "Pumping + Recovery":
            # Specify the well coordinates and rate for each layer in stress period 2 (recovery)
            stress_period_entry_recovery = [lay, 0, col, 0]  # No pumping during recovery
            stress_period_data[1].append(stress_period_entry_recovery)  # Add to stress period 2
    
        if analysis_period == "Recovery Only":
            # For recovery only, you might need special handling to simulate the system's state at the start of recovery.
            # This could involve adjusting initial conditions or other parts of the model setup.
            # Here, we're adding a placeholder for recovery with no pumping rate.
            stress_period_entry_recovery_only = [lay, 0, col, 0]  # No pumping during recovery only scenario
            stress_period_data[0].append(stress_period_entry_recovery_only)  # Add to stress period 1 as a placeholder


    # Create the well package
    wel = flopy.mf6.ModflowGwfwel(
        gwf,
        print_input=True,
        print_flows=True,
        mover=True,
        stress_period_data=stress_period_data,
        save_flows=False,
        pname="WEL-1",
    )

    # Define Transient Hydraulic Parameters
    sto = flopy.mf6.ModflowGwfsto(
        gwf,
        pname="sto",
        iconvert=1,
        ss=ss_values,
        sy=sy_values,
        transient={0:True}
    )

    # Add observation points at column id
    # ###################################################################################################### #
    # Initialize a list to store all continuous observation data for all wells
    all_continuous_observation_data = []
    screen_layer_indices_dict = {}
    # Loop through each row in the obs_wells_data DataFrame to process each observation well
    for index, row in obs_wells_data.iterrows():
        well_id = row['Well ID']
        obs_distance = row['Observation Well Distance (m)']
        obs_sc_top = row['Observation Top Screen Level (m)']
        obs_sc_bottom = row['Observation Bottom Screen Level (m)']
    
        # Calculate the column id for this observation well based on its distance
        obs_col_id = None
        for i, num in enumerate(cumulative_distances):
            if num >= obs_distance:
                obs_col_id = i
                break
        
        # Check if a valid column was found; if not, continue to next well
        if obs_col_id is None:
            continue
    
        # Find the corresponding layer indices for the screen levels of this well
        # Find the corresponding layer indices for the screen levels of this well
        screen_layer_indices = [lay for lay, (lay_top, lay_bottom) in enumerate(zip(top, bottom))
                                if lay_top <= obs_sc_top and lay_bottom >= obs_sc_bottom]

        # Store the layer indices for each well in a dictionary for later use
        screen_layer_indices_dict[well_id] = screen_layer_indices
        # Loop through the screen layer indices and create observation points for this well
        for lay in screen_layer_indices:
            # Use well_id in the observation name to distinguish between wells
            obs_name = f"{well_id}_L{lay}"
            all_continuous_observation_data.append([obs_name, "head", (lay, 0, obs_col_id)])
    
    # Now, all_continuous_observation_data contains observation points for all wells
    # #################################################################################################### #

    # Define Observation Well in MODFLOW
    flopy.mf6.ModflowUtlobs(
        gwf,
        filename="obs",
        print_input=True,
        continuous=all_continuous_observation_data,
        pname="obs"
    )

    # Define the output control package
    oc = flopy.mf6.ModflowGwfoc(
        gwf, budget_filerecord="{}.cbc".format("axisymmetric_model"), head_filerecord="{}.hds".format("axisymmetric_model"), saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")]
    )

    # IMS
    ims = flopy.mf6.ModflowIms(
        sim,
        print_option="SUMMARY",  # Print convergence summary
        complexity="MODERATE",     # Set solver complexity
        outer_hclose=1e-2,      # Outer iteration closure criterion
        inner_hclose=1e-3,      # Inner iteration closure criterion
        outer_maximum=50,       # Maximum number of outer iterations
        inner_maximum=100,      # Maximum number of inner iterations
        linear_acceleration="BICGSTAB"  # Linear acceleration method
    )

    # Write the simulation input files
    sim.write_simulation()

    # Run the model
    success, buff = sim.run_simulation(silent=True, pause=False)
    assert success, "MODFLOW 6 did not terminate normally."

    print("MODFLOW 6 simulation completed successfully.")
    print("==============================================")

    # # Load the heads data from the head file
    head_file = flopy.utils.HeadFile(os.path.join(workspace, "axisymmetric_model.hds"))
    simulated_times = head_file.get_times()
    
    # # Save head of the final time step of pumping period
    if analysis_period == "Pumping Only":
        # Load the head file and extract the last timestep's heads
        headobj = flopy.utils.HeadFile(os.path.join(workspace, "axisymmetric_model.hds"))
        last_time_step_heads = headobj.get_data(totim=headobj.get_times()[-1])
    
        # Save the final heads to a numpy file for later use
        final_heads_filename = os.path.join(workspace, "final_heads_pumping.npy")
        np.save(final_heads_filename, last_time_step_heads)
            
    ################################################################################################
    # Read the observation well paths
    obs_well_files = pd.read_excel(r"Model_Inputs.xlsx", skiprows=37, usecols="B:E", nrows=1)
    obs_well_files = obs_well_files.iloc[0].dropna().to_dict()  # Convert to a dictionary and drop any NaN values
    
    # Assuming obs_wells_data is already correctly set up from earlier steps
    obs_wells_distances = obs_wells_data['Observation Well Distance (m)'].astype(float).tolist()
    
    def find_closest_col_index(distances, target_distance):
    # Find the column index in the model that is closest to the target distance
        closest_index = min(range(len(distances)), key=lambda i: abs(distances[i] - target_distance))
        return closest_index

    # Dictionary to store observation well column indices
    obs_well_col_indices = {}

# Calculate the column index for each observation well based on its distance
    for well_id, well_distance in zip(obs_well_ids, obs_wells_distances):
        obs_well_col_indices[well_id] = find_closest_col_index(cumulative_distances, well_distance)

# Now obs_well_col_indices contains a mapping from each well ID to its column index in the MODFLOW model.

    # Dictionary to store plotters for each observation well
    plotter = {}

    # Loop over each observation well ID and its corresponding file name
    for well_id, file_name in obs_well_files.items():
        obs_path = file_name  # Modify as needed
        head_file_path = os.path.join(workspace, "axisymmetric_model.hds")
        # Retrieve the column index for the current observation well
        obs_id = obs_well_col_indices[well_id]
        # Retrieve the specific screen layer indices for the current observation well
        specific_screen_layer_indices = screen_layer_indices_dict[well_id]
        # Create an instance of the plotter for each well
        plotter[well_id] = ObservedVsSimulatedPlotter(
            head_file_path,
            specific_screen_layer_indices,
            obs_id,
            str_hd,
            obs_path,
            col_centroids,
            analysis_period,
            length_stress_period_pumping,
            col_length,
            workspace,
            well_id
        )
        
    # Dictionaries to store drawdown and time data for each well
    simulated_DD_dict = {}
    observed_DD_dict = {}
    observed_time_dict = {}
        
    # Loop through each plotter instance and perform operations
# Loop through each plotter instance and perform operations
    for well_id, current_plotter in plotter.items():
        # Perform plotting for observed vs. simulated
        current_plotter.plot_obs_simulated()
        
        # Get observed drawdown, simulated drawdown, and observed time for the current well
        simulated_DD, observed_DD, observed_time = current_plotter.get_obs_DD()
        
        # Store the data in the respective dictionaries
        simulated_DD_dict[well_id] = simulated_DD
        observed_DD_dict[well_id] = observed_DD
        observed_time_dict[well_id] = observed_time
        
        # Plot average head vs. distance and save results to Excel for each well
        current_plotter.plot_avg_head_vs_distance()
        current_plotter.save_avg_head_vs_distance_to_excel(f'Results/radius_influence_{well_id}.xlsx')
            
    # Assuming radius of influence is the same for all wells, calculate it using the first plotter
    # You can access the first plotter using next(iter(plotters.values())) or by knowing a specific well ID
    first_plotter = next(iter(plotter.values()))
    radius_influence = first_plotter.radius_influence()
    radius_influence=round(radius_influence,2) 
    # Print the radius of influence
    print("==============================================")
    print(f"Radius of Influence: {radius_influence} meters")
    print("==============================================")
    # Dictionaries to store filtered data for each observation well
    filtered_observed_time_dict = {}
    filtered_observed_DD_dict = {}

    # Loop over each well to apply the analysis period conditions
    for well_id in observed_DD_dict.keys():
        if analysis_period == "Pumping Only":
            # Limit data to the pumping period
            mask = np.array(observed_time_dict[well_id]) <= length_stress_period_pumping
            filtered_observed_time_dict[well_id] = np.array(observed_time_dict[well_id])[mask]
            filtered_observed_DD_dict[well_id] = np.array(observed_DD_dict[well_id])[mask]
        elif analysis_period == "Recovery Only":
            # Limit data to the recovery period
            mask = np.array(observed_time_dict[well_id]) > length_stress_period_pumping
            filtered_observed_time_dict[well_id] = np.array(observed_time_dict[well_id])[mask]
            filtered_observed_DD_dict[well_id] = np.array(observed_DD_dict[well_id])[mask]
        # If it's "Pumping + Recovery", no filtering is needed as we want the full dataset
    # Initialize dictionaries to hold the filtered or original data for further analysis
    final_observed_time_dict = {}
    final_observed_DD_dict = {}
    
    # Determine which set of dictionaries to use based on the analysis period
    if analysis_period in ["Pumping Only", "Recovery Only"]:
        # Use the filtered data for "Pumping Only" or "Recovery Only"
        final_observed_time_dict = filtered_observed_time_dict
        final_observed_DD_dict = filtered_observed_DD_dict
    else:
        # Use the original data for "Pumping + Recovery"
        final_observed_time_dict = observed_time_dict
        final_observed_DD_dict = observed_DD_dict
    
    # Now filtered_observed_time_dict and filtered_observed_DD_dict contain the time and drawdown data 
    # filtered according to the analysis period for each observation well.
    
    # Output excel file paths based on analysis period
    if analysis_period == "Pumping Only":
        output_excel_basepath = 'Results/DD_vs_Time_Pumping_'
    elif analysis_period == "Recovery Only":
        output_excel_basepath = 'Results/DD_vs_Time_Recovery_'
    else:
        output_excel_basepath = 'Results/DD_vs_Time_'
    
    # Loop over each observation well to perform drawdown interpolation and save results
    for well_id in final_observed_time_dict.keys():
        # Initialize the DrawdownInterpolation class for the current well
        dd_interpolator = DrawdownInterpolation(
            final_observed_time_dict[well_id], 
            final_observed_DD_dict[well_id], 
            simulated_times, 
            simulated_DD_dict[well_id],
            analysis_period,
            length_stress_period_pumping
        )
        
        # Interpolate observed drawdown to the smallest time step
        dd_interpolator.interpolate_to_smallest_time_step()
        
        # Interpolate simulated drawdown to match the interpolated observed time step
        dd_interpolator.interpolate_simulated_to_observed()
        
        # Calculate the weighted RMSE for the current well
        weighted_rmse = dd_interpolator.calculate_rmse()
        print(f"RMSE for {well_id}:", round(weighted_rmse, 2))
        
        # Calculate total residual error for the current well
        total_residual_error = dd_interpolator.calculate_total_residual_error()
        print(f"Total Residual Error for {well_id}:", round(total_residual_error, 2))
        
        # Generate and save the drawdown comparison to Excel
        output_excel_path = output_excel_basepath + f"{well_id}.xlsx"
        dd_interpolator.save_results_to_excel(output_excel_path)
        print(f"Results for {well_id} saved to {output_excel_path}")
        print("==============================================")
        

# ========================================================================================================================= #

# ========================================================================================================================= #

# ========================================================================================================================= #
# Function to define the objective function for optimization
def objective_function(parameter_values):
    # Model Inputs
    input_df=pd.read_excel(r"Model_Inputs.xlsx")
    # Read hydraulic conductivity values from a separate sheet
    hk_df = pd.read_excel(r"Model_Inputs.xlsx", sheet_name='Hydraulic Conductivity')
    hk_profile = {(row['Layer Top Level [m]'], row['Layer Bottom Level [m]']): row['Hydraulic Conductivity [m/day]']
                  for index, row in hk_df.iterrows() if not pd.isnull(row['Layer Top Level [m]'])}
    # Assume the first n values in parameter_values correspond to hk values for n layers
    num_hk_layers = len(hk_profile)
    
    # Separate hk values and other parameters (sy, ss)
    hk_values_list = parameter_values[:num_hk_layers]  # First n values for hk
    remaining_values = parameter_values[num_hk_layers:]  # Remaining values for sy, ss, etc.
    
    # Update the hk_profile with the new hk values
    hk_profile_updated = {depth_range: hk for depth_range, hk in zip(hk_profile.keys(), hk_values_list)}
    
    # Initialize defaults
    initial_sy = input_df.at[34, 'Value']
    initial_ss = input_df.at[35, 'Value']
    # Use a dictionary to map parameter names to their corresponding initial values
    param_initial_values = {
        'sy': initial_sy,
        'ss': initial_ss
    }
    # Update the dictionary with the optimized values
    for param, value in zip(params_to_optimize, parameter_values):
        if param in param_initial_values:
            param_initial_values[param] = value
    
    # Now, use the updated values from the dictionary
    initial_sy = param_initial_values['sy']
    initial_ss = param_initial_values['ss']
    
    
    # param_dict = dict(zip(params_to_optimize, parameter_values))
    # initial_hk = param_dict.get('hk', input_df.at[32, 'Value'])  # default_hk should be defined if hk is not being optimized
    # initial_sy = param_dict.get('sy', input_df.at[34, 'Value'])
    # initial_ss = param_dict.get('ss', input_df.at[35, 'Value'])
    # #initial_hk, initial_sy, initial_ss = parameter_values

    # Define the Model Extent, Grid Resolution, and Characteristics for Axisymmetric Flow
    nrow = 1  # Number of rows
    col_length = input_df.at[1, 'Value']   # Number of columns
    # Define the vertical properties
    ztop = input_df.at[5, 'Value']  # Top elevation of top layer
    zbot = input_df.at[6, 'Value']  # Bottom elevation of the last layer
    sc_top = input_df.at[15, 'Value']
    sc_bottom = input_df.at[16, 'Value']
    sc_top_thick = input_df.at[7, 'Value']
    sc_bottom_thick = input_df.at[8, 'Value']
    refine_above_screen=input_df.at[9, 'Value']
    refine_below_screen=input_df.at[10, 'Value']
    refine_between_screen=input_df.at[11, 'Value']
    # Define horizontal desctritization data
    radius_well=input_df.at[13, 'Value']
    cell_size=input_df.at[2, 'Value']
    horizontal_multiplier=input_df.at[3, 'Value']

    #Specified Head
    specified_head = input_df.at[23, 'Value']  # Head value for the specified head boundary
    # Pumng Rate
    Q_m3_hr = input_df.at[14, 'Value'] #m³/hr
    Q = converter.cubic_m_per_hour_to_cubic_m_per_sec(Q_m3_hr)
    # Define Observation Wells

    ##################################################################################################
    # Define Observation Wells
    # Read the Excel file to determine the number of observation wells
    # For this, read only the relevant row where the observation well IDs are located (assuming this is row 18)
    obs_well_ids = pd.read_excel(r"Model_Inputs.xlsx", skiprows=18, nrows=1, header=None).values.flatten()
    # Filter out non-observation well entries (like NaNs)
    obs_well_ids = [id for id in obs_well_ids if not pd.isna(id) and str(id).startswith('OBS')] 
    # Read the observation wells data
    obs_wells_data = pd.read_excel(r"Model_Inputs.xlsx", skiprows=18, usecols=lambda x: 'Unnamed' not in x, nrows=3)
    # The above usecols argument with lambda function will skip columns with 'Unnamed' in the header
    # Transpose the DataFrame to have wells as rows and reset index
    obs_wells_data = obs_wells_data.T.reset_index(drop=True) 
    # Slice the DataFrame to only include existing wells based on the IDs detected
    obs_wells_data = obs_wells_data.iloc[:len(obs_well_ids)+1]
    obs_wells_data.columns = ['Observation Well Distance (m)', 'Observation Top Screen Level (m)', 'Observation Bottom Screen Level (m)']
    #drop index zero
    obs_wells_data.drop(index=0, inplace=True)
    # Insert a column with well IDs at the beginning of the DataFrame
    obs_wells_data.insert(0, 'Well ID', obs_well_ids)
    #################################################################################################################
    
    # Stress Periods
    analysis_period = calib_df.at[25, 'Value']  # New cell location might need adjustment
    if analysis_period == "Pumping Only":
        include_pumping = True
        include_recovery = False
    elif analysis_period == "Recovery Only":
        include_pumping = False
        include_recovery = True
    else:  # "Pumping + Recovery"
        include_pumping = True
        include_recovery = True
    
    # Adjust the number of stress periods based on the selected analysis period
    if analysis_period == "Pumping Only":
        Number_Stress_Periods = 1  # Only pumping period
    elif analysis_period == "Recovery Only":
        Number_Stress_Periods = 1  # Only recovery period, but you might need special handling to set this up correctly
    elif analysis_period == "Pumping + Recovery":  # "Pumping + Recovery"
        Number_Stress_Periods = 2  # Both pumping and recovery periods
        
        
    length_min=input_df.at[26, 'Value']  # Time in minutes
    length_stress_period_pumping =converter.minutes_to_sec(length_min)   # Length of pumping time in days
    length_recovery_min = input_df.at[27, 'Value']  # Adjust the length for recovery
    length_stress_period_recovery =converter.minutes_to_sec(length_recovery_min)   # Length of pumping time in days
    NTSP = input_df.at[28, 'Value']  # Number of time steps
    TSMULT = input_df.at[29, 'Value']  # Multiplier
    T_Unit = input_df.at[30, 'Value'] #Units of time (“seconds”, “minutes”, “hours”, “days”, or “years”.)

    # Create an instance for vertical refinment
    vr = VerticalRefinement(ztop, zbot, sc_top, sc_bottom, sc_top_thick, sc_bottom_thick,
                            refine_above_screen, refine_below_screen, refine_between_screen)
    top, bottom, thickness = vr.calculate_thicknesses()
    # Number of layers
    nlay=len(top)

    # Create an instance of the ColumnCalculator class
    column_calculator = ColumnCalculator(col_length,radius_well ,cell_size, horizontal_multiplier)

    # Calculate Number of columns and column parameters
    delr, cumulative_distances, col_centroids, ncol = column_calculator.calculate_columns()

    # Primary Hydraulic properties
    # Iterate through hk_profile and update the Hk values to m/sec
    hk_profile_m_sec = {depth_range: converter.meters_per_day_to_meters_per_sec(hk) for depth_range, hk in hk_profile_updated.items()}

    VANI = input_df.at[33, 'Value']  # Vertical anisotropy (Vk/Hk)
    sy = initial_sy # Specific yield
    ss = initial_ss  # Specific storage
    laytyp = 3  # Layer type (1 for unconfined)
    
    #################################################################################################################################
    # Initialize a list to store Hk values for each layer
    hk_values = []  # Initialize a list to store Hk values for each layer

    
    # Calculate the midpoint depth of each layer and assign an Hk value
    for i in range(len(top)):
        layer_midpoint = (top[i] + bottom[i]) / 2
        matched = False  # Flag to check if we've matched the depth range
        
        for depth_range, hk_value in hk_profile_m_sec.items():
            if depth_range[0] >= layer_midpoint > depth_range[1]:
                hk_values.append(hk_value)
                matched = True
                break  # Exit the loop once a match is found
        
        if not matched:
            print(f"Layer {i}: Midpoint {layer_midpoint} did not match any range.")
    
    if not hk_values:
        print("No Hk values were matched. Check your depth ranges and layer midpoints.")

####################################################################################################################################

    # Calculated converted parameters to convert to Axisymmetric grid
    par=ParametersConversions(col_centroids, delr, thickness)
    par.set_original_parameters(hk_values, sy, ss)
    hk_con, sy_con, ss_con=par.calculate_converted_parameters()
    # Define values for hk, sy, and ss
    hk_values = []
    sy_values=[]

    # Create a list of lists for hk where each sub-list represents layer values
    for lay in range(nlay):
        hk_values.append(hk_con)
    # Create a list of lists for Sy where each sub-list represents layer values
    for lay in range(nlay):
        sy_values.append(sy_con)
    ss_values = ss_con
      
    # Path for the workspace and mf6.exe
    workspace = r'workspace'  # Specify your desired directory path
    mf6_exe = r"C:\Program Files\GMS 10.8 64-bit\Mesa\python\Lib\site-packages\xms\executables\modflow6\mf6.exe"  # Path to mf6.exe

    # Create a MODFLOW 6 simulation object
    sim = flopy.mf6.MFSimulation(
        sim_name="axisymmetric_model", exe_name=mf6_exe, sim_ws=workspace
    )


# Define the time discretization (tdis) for stress periods based on analysis_period
    perioddata1 = []
    if include_pumping and not include_recovery:
        perioddata1.append((length_stress_period_pumping, NTSP, TSMULT))
    elif include_recovery and not include_pumping:
        perioddata1.append((length_stress_period_recovery, NTSP, TSMULT))
    else:
        perioddata1=[
            (length_stress_period_pumping, NTSP, TSMULT),  # Stress period 1 (pumping)
            (length_stress_period_recovery, NTSP, TSMULT),  # Stress period 2 (recovery)
        ]
    tdis = flopy.mf6.ModflowTdis(
        sim,
        pname="tdis",
        time_units = T_Unit, 
        nper=Number_Stress_Periods,  # Define 2 stress periods
        perioddata=perioddata1
        
    )

    # Create a MODFLOW 6 groundwater flow (gwf) model within the simulation
    gwf = flopy.mf6.ModflowGwf(
        sim,
        modelname="ax_model",
        save_flows=True,
    )

    # Well Screen
    sc_top_id=top.index(sc_top)
    sc_bottom_id=bottom.index(sc_bottom)
    sc_layers=(sc_bottom_id-sc_top_id)+1
    # Well dischagrge using  "Weighting by Transmissivity" approach


    # Initialize a list to store the flux for each layer
    layer_fluxes = []

    # Distribute the flux based on transmissivity ratios
    for thick in thickness[sc_top_id:sc_bottom_id+1]:
        layer_flux = Q * (thick / (sc_top - sc_bottom))
        layer_fluxes.append(layer_flux)

    # Define the spatial discretization (the grid)
    dis = flopy.mf6.ModflowGwfdis(
        gwf,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=1.0,  # Adjust delc for 1 column
        top=ztop,
        botm=bottom  # Define layer bottoms
    )
    
    # Initial Condition (Starting Head)
    # Define the initial head conditions
    str_hd = input_df.at[22, 'Value'] # Initial Condition (Starting Head)
    observed_drawdown_end_of_pumping = input_df.at[37, 'Value']
    # Adjusting the initial condition for "Recovery Only" scenario
    if analysis_period == "Recovery Only":
        final_heads_filename = os.path.join(workspace, "final_heads_pumping.npy")
    
        if os.path.exists(final_heads_filename):
            # Load the saved heads as initial conditions
            strt = np.load(final_heads_filename)
        else:
            print("Pumping period run should be done first...")
            return
    else:
        # For other analysis periods, use the specified starting head
        strt = str_hd * np.ones((nlay, nrow, ncol), dtype=np.float32)


    # Define the basic package
    ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)

    # Create the constant head boundary condition for the last layer in the last column
    chd_data = []
    # Create the constant head boundary condition for the last column
    chd_data.append([(nlay-1, 0, ncol - 1), specified_head]) #assign specified head for the last layer only

    #for stress_period in range(Number_Stress_Priods):
        #chd_data.append([(nlay-1, 0, ncol - 1), specified_head])

    # Define the stress period data using perioddata
    perioddata = {i: chd_data for i in range(Number_Stress_Periods)}

    chd = flopy.mf6.ModflowGwfchd(gwf, stress_period_data=perioddata)

    # Define the LPF package
    lpf = flopy.mf6.ModflowGwfnpf(
        gwf, 
        icelltype=laytyp,
        k33overk=True,
        k=hk_con, 
        k33=VANI, 
        save_flows=True,
        alternative_cell_averaging = "LOGARITHMIC",
        cvoptions="DEWATERED",
    )

    # Define the initial condition package
    ic = flopy.mf6.ModflowGwfic(gwf, strt=strt)

    # Create the well package
    # Define the column and layer for the well
    col = 0  # First column (0-based index)
    layer_start = sc_top_id  # Starting layer number
    layer_end = sc_bottom_id    # Ending layer number
    
    # Determine the analysis period and initialize stress_period_data accordingly
    analysis_period = input_df.at[25, 'Value']
    if analysis_period == "Pumping Only":
        stress_period_data = {0: []}  # Only pumping period
    elif analysis_period == "Recovery Only":
        stress_period_data = {0: []}  # Only recovery period; you might simulate it as a single period for simplicity
    elif analysis_period == "Pumping + Recovery":
        stress_period_data = {0: [], 1: []}  # Both pumping and recovery periods

# Loop through the layers and create entries in stress_period_data
    for lay, lay_flux in enumerate(layer_fluxes):
        lay += sc_top_id  # Adjust the layer index to start from the screen layer
    
        if analysis_period in ["Pumping Only", "Pumping + Recovery"]:
            # Specify the well coordinates and rate for each layer in stress period 1 (pumping)
            stress_period_entry_pumping = [lay, 0, col, lay_flux]  # m³/sec for pumping period
            stress_period_data[0].append(stress_period_entry_pumping)  # Add to stress period 1
    
        if analysis_period == "Pumping + Recovery":
            # Specify the well coordinates and rate for each layer in stress period 2 (recovery)
            stress_period_entry_recovery = [lay, 0, col, 0]  # No pumping during recovery
            stress_period_data[1].append(stress_period_entry_recovery)  # Add to stress period 2
    
        if analysis_period == "Recovery Only":
            # For recovery only, you might need special handling to simulate the system's state at the start of recovery.
            # This could involve adjusting initial conditions or other parts of the model setup.
            # Here, we're adding a placeholder for recovery with no pumping rate.
            stress_period_entry_recovery_only = [lay, 0, col, 0]  # No pumping during recovery only scenario
            stress_period_data[0].append(stress_period_entry_recovery_only)  # Add to stress period 1 as a placeholder


    # Create the well package with two stress periods
    wel = flopy.mf6.ModflowGwfwel(
        gwf,
        print_input=True,
        print_flows=True,
        mover=True,
        stress_period_data=stress_period_data,
        save_flows=False,
        pname="WEL-1",
    )

    # Define Transient Hydraulic Parameters
    sto = flopy.mf6.ModflowGwfsto(
        gwf,
        pname="sto",
        iconvert=1,
        ss=ss_values,
        sy=sy_values,
        transient={0:True}
    )

    # ###################################################################################################### #
    # Initialize a list to store all continuous observation data for all wells
    all_continuous_observation_data = []
    screen_layer_indices_dict={}
    # Loop through each row in the obs_wells_data DataFrame to process each observation well
    for index, row in obs_wells_data.iterrows():
        well_id = row['Well ID']
        obs_distance = row['Observation Well Distance (m)']
        obs_sc_top = row['Observation Top Screen Level (m)']
        obs_sc_bottom = row['Observation Bottom Screen Level (m)']
    
        # Calculate the column id for this observation well based on its distance
        obs_col_id = None

        # Add observation points at column id
        for i, num in enumerate(cumulative_distances):
            if num >= obs_distance:
                obs_col_id = i
                break
            # Check if a valid column was found; if not, continue to next well
            if obs_col_id is None:
                continue
    
        # Find the corresponding layer indices for the screen levels of this well
        screen_layer_indices = [lay for lay, (lay_top, lay_bottom) in enumerate(zip(top, bottom))
                                if lay_top <= obs_sc_top and lay_bottom >= obs_sc_bottom]
        # Store the layer indices for each well in a dictionary for later use
        screen_layer_indices_dict[well_id] = screen_layer_indices
        
            # Loop through the screen layer indices and create observation points for this well


        for lay in screen_layer_indices:
            # Use well_id in the observation name to distinguish between wells
            obs_name = f"{well_id}_L{lay}"
            all_continuous_observation_data.append([obs_name, "head", (lay, 0, obs_col_id)])
    
    # Now, all_continuous_observation_data contains observation points for all wells
    # #################################################################################################### #
    # Define Observation Well in MODFLOW
    flopy.mf6.ModflowUtlobs(
        gwf,
        filename="obs",
        print_input=True,
        continuous=all_continuous_observation_data,
        pname="obs"
    )

    # Define the output control package
    oc = flopy.mf6.ModflowGwfoc(
        gwf, budget_filerecord="{}.cbc".format("axisymmetric_model"), head_filerecord="{}.hds".format("axisymmetric_model"), saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")]
    )

    # IMS
    ims = flopy.mf6.ModflowIms(
        sim,
        print_option="SUMMARY",  # Print convergence summary
        complexity="MODERATE",     # Set solver complexity
        outer_hclose=1e-2,      # Outer iteration closure criterion
        inner_hclose=1e-3,      # Inner iteration closure criterion
        outer_maximum=50,       # Maximum number of outer iterations
        inner_maximum=100,      # Maximum number of inner iterations
        linear_acceleration="BICGSTAB"  # Linear acceleration method
    )

    # Write the simulation input files
    sim.write_simulation()

    # Run the model
    # success, buff = sim.run_simulation(silent=True, pause=False)
    # assert success, "MODFLOW 6 did not terminate normally."
    # Run the model with error handling
    try:
        success, buff = sim.run_simulation(silent=True, pause=False)
        assert success, "MODFLOW 6 did not terminate normally."
    except Exception as e:
        print(f"MODFLOW failed with parameters: {parameter_values}. Error: {str(e)}")
        return 1e6  # Large penalty for failed simulation
    print("MODFLOW 6 simulation completed successfully.")


    # # Load the heads data from the head file
    head_file = flopy.utils.HeadFile(os.path.join(workspace, "axisymmetric_model.hds"))
    simulated_times = head_file.get_times()

    # # Save head of the final time step of pumping period
    if analysis_period == "Pumping Only":
        # Load the head file and extract the last timestep's heads
        headobj = flopy.utils.HeadFile(os.path.join(workspace, "axisymmetric_model.hds"))
        last_time_step_heads = headobj.get_data(totim=headobj.get_times()[-1])
    
        # Save the final heads to a numpy file for later use
        final_heads_filename = os.path.join(workspace, "final_heads_pumping.npy")
        np.save(final_heads_filename, last_time_step_heads)
        
    # # Plot Simulated VS Observed 
    ################################################################################################
    # Read the observation well paths
    obs_well_files = pd.read_excel(r"Model_Inputs.xlsx", skiprows=37, usecols="B:E", nrows=1)
    obs_well_files = obs_well_files.iloc[0].dropna().to_dict()  # Convert to a dictionary and drop any NaN values
    
    # Assuming obs_wells_data is already correctly set up from earlier steps
    obs_wells_distances = obs_wells_data['Observation Well Distance (m)'].astype(float).tolist()
    
    def find_closest_col_index(distances, target_distance):
    # Find the column index in the model that is closest to the target distance
        closest_index = min(range(len(distances)), key=lambda i: abs(distances[i] - target_distance))
        return closest_index

    # Dictionary to store observation well column indices
    obs_well_col_indices = {}

# Calculate the column index for each observation well based on its distance
    for well_id, well_distance in zip(obs_well_ids, obs_wells_distances):
        obs_well_col_indices[well_id] = find_closest_col_index(cumulative_distances, well_distance)

# Now obs_well_col_indices contains a mapping from each well ID to its column index in the MODFLOW model.

    # Dictionary to store plotters for each observation well
    plotter = {}

    # Loop over each observation well ID and its corresponding file name
    for well_id, file_name in obs_well_files.items():
        obs_path = file_name  # Modify as needed
        head_file_path = os.path.join(workspace, "axisymmetric_model.hds")
        # Retrieve the column index for the current observation well
        obs_id = obs_well_col_indices[well_id]
        # Retrieve the specific screen layer indices for the current observation well
        specific_screen_layer_indices = screen_layer_indices_dict[well_id]
        # Create an instance of the plotter for each well
        plotter[well_id] = ObservedVsSimulatedPlotter(
            head_file_path,
            specific_screen_layer_indices,
            obs_id,
            str_hd,
            obs_path,
            col_centroids,
            analysis_period,
            length_stress_period_pumping,
            col_length,
            workspace,
            well_id
        )
        
    # Dictionaries to store drawdown and time data for each well
    simulated_DD_dict = {}
    observed_DD_dict = {}
    observed_time_dict = {}
        
    # Loop through each plotter instance and perform operations
# Loop through each plotter instance and perform operations
    for well_id, current_plotter in plotter.items():
        # Perform plotting for observed vs. simulated
        #current_plotter.plot_obs_simulated()
        
        # Get observed drawdown, simulated drawdown, and observed time for the current well
        simulated_DD, observed_DD, observed_time = current_plotter.get_obs_DD()
        
        # Store the data in the respective dictionaries
        simulated_DD_dict[well_id] = simulated_DD
        observed_DD_dict[well_id] = observed_DD
        observed_time_dict[well_id] = observed_time
        
    # Dictionaries to store filtered data for each observation well
    filtered_observed_time_dict = {}
    filtered_observed_DD_dict = {}

    # Loop over each well to apply the analysis period conditions
    for well_id in observed_DD_dict.keys():
        if analysis_period == "Pumping Only":
            # Limit data to the pumping period
            mask = np.array(observed_time_dict[well_id]) <= length_stress_period_pumping
            filtered_observed_time_dict[well_id] = np.array(observed_time_dict[well_id])[mask]
            filtered_observed_DD_dict[well_id] = np.array(observed_DD_dict[well_id])[mask]
        elif analysis_period == "Recovery Only":
            # Limit data to the recovery period
            mask = np.array(observed_time_dict[well_id]) > length_stress_period_pumping
            filtered_observed_time_dict[well_id] = np.array(observed_time_dict[well_id])[mask]
            filtered_observed_DD_dict[well_id] = np.array(observed_DD_dict[well_id])[mask]
        # If it's "Pumping + Recovery", no filtering is needed as we want the full dataset
    # Initialize dictionaries to hold the filtered or original data for further analysis
    final_observed_time_dict = {}
    final_observed_DD_dict = {}
    
    # Determine which set of dictionaries to use based on the analysis period
    if analysis_period in ["Pumping Only", "Recovery Only"]:
        # Use the filtered data for "Pumping Only" or "Recovery Only"
        final_observed_time_dict = filtered_observed_time_dict
        final_observed_DD_dict = filtered_observed_DD_dict
    else:
        # Use the original data for "Pumping + Recovery"
        final_observed_time_dict = observed_time_dict
        final_observed_DD_dict = observed_DD_dict

    # Initialize variables to accumulate RMSE and total residual error across all wells
    total_weighted_rmse = 0
    total_residual_error_sum = 0
    num_wells = len(final_observed_time_dict.keys())
    # Loop over each observation well to perform drawdown interpolation and save results
    # Loop over each observation well to perform drawdown interpolation
    for well_id in final_observed_time_dict.keys():
        dd_interpolator = DrawdownInterpolation(
            final_observed_time_dict[well_id], 
            final_observed_DD_dict[well_id], 
            simulated_times, 
            simulated_DD_dict[well_id],
            analysis_period,
            length_stress_period_pumping
        )
        dd_interpolator.interpolate_to_smallest_time_step()
        dd_interpolator.interpolate_simulated_to_observed()
    
        # Sum up the RMSE and total residual error across all wells
        total_weighted_rmse += dd_interpolator.calculate_rmse()
        total_residual_error_sum += dd_interpolator.calculate_total_residual_error()
        
        # Optionally, print RMSE and total residual error for the current well
        print("=================================================")
        print(f"RMSE for {well_id}: {dd_interpolator.calculate_rmse():.3f}")
        print(f"Total Residual Error for {well_id}: {dd_interpolator.calculate_total_residual_error():.3f}")
        
            
    # Average RMSE and total residual error across all observation wells
    average_rmse = total_weighted_rmse / num_wells
    average_total_residual_error = total_residual_error_sum / num_wells
    # Normalization (example approach, assuming you know the max possible values)
    max_rmse = 1  # Hypothetical maximum RMSE
    max_total_residual = 100  # Hypothetical maximum total residual
    normalized_rmse = average_rmse / max_rmse
    normalized_total_residual = average_total_residual_error / max_total_residual
    
    # Weighting
    weight_rmse = 0.2  # Weight of RMSE in the objective function
    weight_total_residual = 0.8  # Weight of total residual head in the objective function
    
    # Weighted Sum Objective Function
    objective_value = (weight_rmse * normalized_rmse) + (weight_total_residual * normalized_total_residual)
   
    # Print the objective function value for the current iteration
    print("=================================================")
    print(f"Objective Function Value: {objective_value:.3f}")
    print("=================================================")
    # return the weighted objective function to represent the total residual error and RMSE
    return objective_value

if run_type=="Forward Run":
    # Define depth-based Hk values (depth ranges in meters, Hk in m/day)
    # Read the 'Hydraulic Conductivity' sheet from the Excel file
    df_hk = pd.read_excel('Model_Inputs.xlsx', sheet_name='Hydraulic Conductivity')
    # Initialize an empty dictionary to store the hk values
    hk_profile = {}

    # Convert the DataFrame to the hk_profile dictionary
    for index, row in df_hk.iterrows():
        top_level = row['Layer Top Level [m]']
        bottom_level = row['Layer Bottom Level [m]']
        hk_value = row['Hydraulic Conductivity [m/day]']
        
        # Check for missing values and skip if any key values are missing
        if pd.isna(top_level) or pd.isna(bottom_level) or pd.isna(hk_value):
            continue

        # Add to the hk_profile dictionary
        hk_profile[(top_level, bottom_level)] = hk_value
    # Run the forward model
    run_forward_model(hk_profile=hk_profile, sy=calib_df.at[34, 'Value'], ss=calib_df.at[35, 'Value'])
else:
    # Read the 'Hydraulic Conductivity' sheet from the Excel file
    df_hk = pd.read_excel('Model_Inputs.xlsx', sheet_name='Hydraulic Conductivity')
    hk_profile = {}

    # Convert the DataFrame to the hk_profile dictionary
    for index, row in df_hk.iterrows():
        top_level = row['Layer Top Level [m]']
        bottom_level = row['Layer Bottom Level [m]']
        hk_value = row['Hydraulic Conductivity [m/day]']
        
        # Check for missing values and skip if any key values are missing
        if pd.isna(top_level) or pd.isna(bottom_level) or pd.isna(hk_value):
            continue

        # Add to the hk_profile dictionary
        hk_profile[(top_level, bottom_level)] = hk_value

    # Define the parameters to optimize based on flags in the Excel file
    params_to_optimize = []
    initial_guess = []
    solve_Hk= calib_df.at[41,'Value']
    solve_Sy= calib_df.at[43,'Value']
    solve_Ss= calib_df.at[44,'Value']
    #initial_guess = [calib_df.at[32, 'Value'],  calib_df.at[34, 'Value'], calib_df.at[35, 'Value']]  # Example initial parameter values
    # Add parameters based on flags
    if solve_Hk == 'Yes':
        hk_df = pd.read_excel(r"Model_Inputs.xlsx", sheet_name='Hydraulic Conductivity')
        for index, row in hk_df.iterrows():
            params_to_optimize.append(f'hk_layer_{index+1}')
            initial_guess.append(row['Hydraulic Conductivity [m/day]'])
        
    if solve_Sy == 'Yes':
        params_to_optimize.append('sy')
        initial_guess.append(calib_df.at[34, 'Value'])
        
    if solve_Ss == 'Yes':
        params_to_optimize.append('ss')
        initial_guess.append(calib_df.at[35, 'Value'])

    # Optimize parameters
    result = fmin(objective_function, initial_guess, maxiter=20, disp=True)
    
    # Extract the optimal parameters
    # Store the results for hydraulic conductivity in a list
    hk_results = result[:hk_df.shape[0]]  # Assuming the first N results correspond to hk values for N layers
    sy_result = result[-2] if solve_Sy == 'Yes' else calib_df.at[34, 'Value']
    ss_result = result[-1] if solve_Ss == 'Yes' else calib_df.at[35, 'Value']
    
    # Create a DataFrame for hydraulic conductivity results
    hk_results_df = pd.DataFrame({
        'Layer': [f'Layer {i+1}' for i in range(len(hk_results))],
        'Optimal Hydraulic Conductivity [m/day]': hk_results
        })
    
    # Initialize a dictionary to hold the results
    results_dict = {}
    # Recreate hk_profile from hk_results
    hk_profile_optimized = {}
    for index, row in hk_df.iterrows():
        depth_range = (row['Layer Top Level [m]'], row['Layer Bottom Level [m]'])
        hk_value = hk_results[index]  # Assuming hk_results is in the same order as your layers
        hk_profile_optimized[depth_range] = hk_value
        # Run forward model with optimal parameters

    # Include the optimized hydraulic conductivity profile in results_dict
    results_dict['hk_profile'] = hk_profile_optimized
    
    # Read the number of layers or zones you have for hydraulic conductivity
    num_hk_layers = len(hk_profile)  # Assuming hk_profile is already defined as shown previously
    
    # Initialize a list to store the optimized hk values
    optimal_hk_values = []
    
    # Iterate over the optimized parameters and their results
    for param_name, value in zip(params_to_optimize, result):
        # Check if the parameter name is for hydraulic conductivity
        if 'hk_layer_' in param_name:
            layer_index = int(param_name.split('_')[-1])  # Get the layer index from the parameter name
            optimal_hk_values.append((layer_index, value))  # Append a tuple of layer index and value
    
        # Otherwise, check for sy and ss
        elif param_name == 'sy':
            results_dict["Specific Yield (Sy)"] = value
        elif param_name == 'ss':
            results_dict["Specific Storage (Ss)"] = value
    
    # Sort the hydraulic conductivity values based on layer index
    optimal_hk_values.sort(key=lambda x: x[0])
    
    # Create a DataFrame for hydraulic conductivity results
    hk_results_df = pd.DataFrame(optimal_hk_values, columns=['Layer Number', 'Hydraulic Conductivity [m/day]'])
      
    # Output excel file path based on analysis period
    analysis_period = calib_df.at[25, 'Value']
    base_output_excel_path = 'Results/Optimal_Values'
    if analysis_period == "Pumping Only":
        output_excel_path_hk = base_output_excel_path + '_Hk_Pumping.xlsx'
        output_excel_path_other = base_output_excel_path + '_Pumping.xlsx'
    elif analysis_period == "Recovery Only":
        output_excel_path_hk = base_output_excel_path + '_Hk_Recovery.xlsx'
        output_excel_path_other = base_output_excel_path + '_Recovery.xlsx'
    else:
        output_excel_path_hk = base_output_excel_path + '_Hk.xlsx'
        output_excel_path_other = base_output_excel_path + '.xlsx'
    
    # Output hydraulic conductivity to excel
    hk_results_df.to_excel(output_excel_path_hk, index=False)
    print("======================================================================")
    print(f"Hydraulic conductivity results saved to {output_excel_path_hk}")
    
    # Create DataFrame from non-hk results dictionary
    other_results_df = pd.DataFrame([{k: v for k, v in results_dict.items() if k != "hk_profile"}])
    
    # Output other results to excel
    other_results_df.to_excel(output_excel_path_other, index=False)
    print(f"Other results saved to {output_excel_path_other}")
    
    # Print the results
    print("====================================================================")
    print("Optimal Parameter Values:")
    print(hk_results_df)
    print("====================================================================")
    print(other_results_df)
    print("====================================================================")

    
    # Assume run_forward_model function can handle a dictionary as input
    run_forward_model(**results_dict)
        
# Record the end time
end_time = time.time()
# Calculate the elapsed time in seconds
elapsed_time =round( end_time - start_time,3)
if elapsed_time > 60:
    elapsed_time=round(elapsed_time/60,2)
    print(f"Elapsed time: {elapsed_time} minutes")
else:  
    # Print the elapsed time
    print(f"Elapsed time: {elapsed_time} seconds")