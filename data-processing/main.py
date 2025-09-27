#!/usr/bin/env python3
"""
Complete refactored main.py following DRY principles
Modular structure with reusable functions and complete functionality
"""

import time
import numpy as np
import flopy
import pandas as pd
import os
from scipy.optimize import fmin

# Local imports
from VerticalRefinment import VerticalRefinement
from conversions import ParametersConversions
from Units import UnitConverter
from Plotter import ObservedVsSimulatedPlotter
from ColumnCalculator import ColumnCalculator
from DrawdownInterpolation import DrawdownInterpolation
from JsonDataLoader import JsonDataLoader


class ModelConfig:
    """Configuration class to hold all model parameters and provide data access"""
    
    def __init__(self, json_file_path="Model_Inputs.json"):
        self.loader = JsonDataLoader(json_file_path)
        self.converter = UnitConverter()
        self.workspace = 'workspace'
        self.mf6_exe = "./mf6"
        
        # Create Results folder if it doesn't exist
        os.makedirs('Results', exist_ok=True)
    
    def get_basic_parameters(self):
        """Get basic model parameters"""
        return {
            'run_type': self.loader.at('Choose Type of Simulation', 'Value'),
            'VANI': self.loader.at('Vk/Hk Ratio', 'Value'),
            'sy': self.loader.at('Specific Yield (Sy)', 'Value'),
            'ss': self.loader.at('Specific Storage (Ss)', 'Value')
        }
    
    def get_model_geometry(self):
        """Get model geometry parameters"""
        return {
            'nrow': 1,
            'col_length': self.loader.at('Boundary distance from pumping well', 'Value'),
            'ztop': self.loader.at('Saturated top elevation', 'Value'),
            'zbot': self.loader.at('Aquifer bottom elevation', 'Value'),
            'sc_top': self.loader.at('Screen Top Elevation', 'Value'),
            'sc_bottom': self.loader.at('Screen Bottom Elevation', 'Value'),
            'sc_top_thick': self.loader.at('Screen top - Cell thickness', 'Value'),
            'sc_bottom_thick': self.loader.at('Screen bottom- Cell thickness', 'Value'),
            'refine_above_screen': self.loader.at('Refinment above screen', 'Value'),
            'refine_below_screen': self.loader.at('Refinment below screen', 'Value'),
            'refine_between_screen': self.loader.at('Refinment between screen', 'Value'),
            'radius_well': self.loader.at('Well Radius', 'Value'),
            'cell_size': self.loader.at('2nd Column Size', 'Value'),
            'horizontal_multiplier': self.loader.at('Column Multiplier', 'Value'),
            'specified_head': self.loader.at('Specified Head', 'Value'),
            'Q_m3_hr': self.loader.at('Q', 'Value'),
            'starting_head': self.loader.at('Starting Head', 'Value')
        }
    
    def get_time_parameters(self):
        """Get time-related parameters"""
        analysis_period = self.loader.at('Analysis Period', 'Value')
        
        # Determine pumping and recovery flags
        if analysis_period == "Pumping Only":
            include_pumping, include_recovery = True, False
        elif analysis_period == "Recovery Only":
            include_pumping, include_recovery = False, True
        else:  # "Pumping + Recovery"
            include_pumping, include_recovery = True, True
        
        # Calculate stress periods
        if analysis_period == "Pumping Only":
            Number_Stress_Periods = 1
        elif analysis_period == "Recovery Only":
            Number_Stress_Periods = 1
        else:  # "Pumping + Recovery"
            Number_Stress_Periods = 2
        
        return {
            'analysis_period': analysis_period,
            'include_pumping': include_pumping,
            'include_recovery': include_recovery,
            'Number_Stress_Periods': Number_Stress_Periods,
            'pumping_length_min': self.loader.at('Pumping length', 'Value'),
            'recovery_length_min': self.loader.at('Recovery length', 'Value'),
            'NTSP': self.loader.at('Number of time steps', 'Value'),
            'TSMULT': self.loader.at('Time Multiplier', 'Value'),
            'T_Unit': self.loader.at('Time Units', 'Value')
        }
    
    def get_hydraulic_conductivity_profile(self):
        """Get hydraulic conductivity profile"""
        hk_df = self.loader.get_hydraulic_conductivity_data()
        return {(row['Layer Top Level [m]'], row['Layer Bottom Level [m]']): row['Hydraulic Conductivity [m/day]']
                for index, row in hk_df.iterrows() if not pd.isnull(row['Layer Top Level [m]'])}
    
    def get_observation_wells_data(self):
        """Get observation wells data"""
        obs_wells_data = self.loader.get_observation_wells_data()
        return {
            'data': obs_wells_data,
            'ids': obs_wells_data['Well ID'].tolist(),
            'files': self.loader.get_observation_well_files()
        }
    
    def get_optimization_flags(self):
        """Get optimization flags"""
        return {
            'solve_Hk': self.loader.at('Hydraulic Conductivity Flag', 'Value'),
            'solve_Sy': self.loader.at('Specific Yield (Sy) Flag', 'Value'),
            'solve_Ss': self.loader.at('Specific Storage (Ss) Flag', 'Value')
        }


def calculate_vertical_discretization(geometry_params):
    """Calculate vertical discretization using VerticalRefinement"""
    vr = VerticalRefinement(
        geometry_params['ztop'], geometry_params['zbot'],
        geometry_params['sc_top'], geometry_params['sc_bottom'],
        geometry_params['sc_top_thick'], geometry_params['sc_bottom_thick'],
        geometry_params['refine_above_screen'], geometry_params['refine_below_screen'],
        geometry_params['refine_between_screen']
    )
    return vr.calculate_thicknesses()


def calculate_horizontal_discretization(geometry_params):
    """Calculate horizontal discretization using ColumnCalculator"""
    column_calculator = ColumnCalculator(
        geometry_params['col_length'],
        geometry_params['radius_well'],
        geometry_params['cell_size'],
        geometry_params['horizontal_multiplier']
    )
    return column_calculator.calculate_columns()


def calculate_hydraulic_parameters(hk_profile, sy, ss, col_centroids, delr, thickness, converter, top, bottom):
    """Calculate converted hydraulic parameters"""
    # Convert hk_profile to m/sec
    hk_profile_m_sec = {depth_range: converter.meters_per_day_to_meters_per_sec(hk) 
                        for depth_range, hk in hk_profile.items()}
    
    # Calculate hk values for each layer
    hk_values = []
    for i in range(len(top)):
        layer_midpoint = (top[i] + bottom[i]) / 2
        for depth_range, hk_value in hk_profile_m_sec.items():
            if depth_range[0] >= layer_midpoint > depth_range[1]:
                hk_values.append(hk_value)
                break
    
    # Calculate converted parameters
    par = ParametersConversions(col_centroids, delr, thickness)
    par.set_original_parameters(hk_values, sy, ss)
    return par.calculate_converted_parameters()


def create_time_discretization(sim, time_params, converter):
    """Create time discretization package"""
    # Convert time to seconds
    pumping_length_sec = converter.minutes_to_sec(time_params['pumping_length_min'])
    recovery_length_sec = converter.minutes_to_sec(time_params['recovery_length_min'])
    
    # Setup period data
    perioddata = []
    if time_params['include_pumping'] and not time_params['include_recovery']:
        perioddata.append((pumping_length_sec, time_params['NTSP'], time_params['TSMULT']))
    elif time_params['include_recovery'] and not time_params['include_pumping']:
        perioddata.append((recovery_length_sec, time_params['NTSP'], time_params['TSMULT']))
    else:
        perioddata = [
            (pumping_length_sec, time_params['NTSP'], time_params['TSMULT']),
            (recovery_length_sec, time_params['NTSP'], time_params['TSMULT'])
        ]
    
    tdis = flopy.mf6.ModflowTdis(
        sim, pname="tdis", time_units=time_params['T_Unit'],
        nper=time_params['Number_Stress_Periods'], perioddata=perioddata
    )
    
    return tdis, pumping_length_sec, recovery_length_sec


def create_groundwater_flow_model(sim):
    """Create groundwater flow model"""
    return flopy.mf6.ModflowGwf(sim, modelname="ax_model", save_flows=True)


def create_spatial_discretization(gwf, nlay, ncol, delr, ztop, bottom):
    """Create spatial discretization package"""
    return flopy.mf6.ModflowGwfdis(
        gwf, nlay=nlay, nrow=1, ncol=ncol, delr=delr, delc=1.0,
        top=ztop, botm=bottom
    )


def create_constant_head_package(gwf, nlay, ncol, specified_head, Number_Stress_Periods):
    """Create constant head boundary package"""
    chd_data = [[(nlay-1, 0, ncol - 1), specified_head]]
    perioddata = {i: chd_data for i in range(Number_Stress_Periods)}
    return flopy.mf6.ModflowGwfchd(gwf, stress_period_data=perioddata)


def create_layer_property_flow_package(gwf, hk_con, VANI):
    """Create layer property flow package"""
    return flopy.mf6.ModflowGwfnpf(
        gwf, icelltype=3, k33overk=True, k=hk_con, k33=VANI,
        save_flows=True, alternative_cell_averaging="LOGARITHMIC", cvoptions="DEWATERED"
    )


def create_initial_conditions_package(gwf, strt):
    """Create initial conditions package"""
    return flopy.mf6.ModflowGwfic(gwf, strt=strt)


def create_well_package(gwf, geometry_params, time_params, Q, top, bottom, thickness):
    """Create well package for pumping/recovery"""
    sc_top = geometry_params['sc_top']
    sc_bottom = geometry_params['sc_bottom']
    
    # Find screen layers
    sc_top_id = top.index(sc_top)
    sc_bottom_id = bottom.index(sc_bottom)
    
    # Calculate layer fluxes
    layer_fluxes = []
    for thick in thickness[sc_top_id:sc_bottom_id+1]:
        layer_flux = Q * (thick / (sc_top - sc_bottom))
        layer_fluxes.append(layer_flux)
    
    # Setup stress period data
    stress_period_data = {}
    if time_params['analysis_period'] == "Pumping Only":
        stress_period_data = {0: []}
    elif time_params['analysis_period'] == "Recovery Only":
        stress_period_data = {0: []}
    else:  # "Pumping + Recovery"
        stress_period_data = {0: [], 1: []}
    
    # Add well entries
    for lay, lay_flux in enumerate(layer_fluxes):
        lay += sc_top_id
        if time_params['analysis_period'] in ["Pumping Only", "Pumping + Recovery"]:
            stress_period_data[0].append([lay, 0, 0, lay_flux])
        if time_params['analysis_period'] == "Pumping + Recovery":
            stress_period_data[1].append([lay, 0, 0, 0])
        if time_params['analysis_period'] == "Recovery Only":
            stress_period_data[0].append([lay, 0, 0, 0])
    
    return flopy.mf6.ModflowGwfwel(
        gwf, print_input=True, print_flows=True, mover=True,
        stress_period_data=stress_period_data, save_flows=False, pname="WEL-1"
    )


def create_storage_package(gwf, sy_values, ss_values):
    """Create storage package"""
    return flopy.mf6.ModflowGwfsto(
        gwf, pname="sto", iconvert=1, ss=ss_values, sy=sy_values, transient={0: True}
    )


def create_observation_package(gwf, obs_wells_data, top, bottom, cumulative_distances):
    """Create observation package"""
    all_continuous_observation_data = []
    screen_layer_indices_dict = {}
    
    for index, row in obs_wells_data['data'].iterrows():
        well_id = row['Well ID']
        obs_distance = row['Observation Well Distance (m)']
        obs_sc_top = row['Observation Top Screen Level (m)']
        obs_sc_bottom = row['Observation Bottom Screen Level (m)']
        
        # Calculate column id
        obs_col_id = None
        for i, num in enumerate(cumulative_distances):
            if num >= obs_distance:
                obs_col_id = i
                break
        
        if obs_col_id is None:
            continue
        
        # Find screen layer indices
        screen_layer_indices = [lay for lay, (lay_top, lay_bottom) in enumerate(zip(top, bottom))
                                if lay_top <= obs_sc_top and lay_bottom >= obs_sc_bottom]
        
        screen_layer_indices_dict[well_id] = screen_layer_indices
        
        # Add observation points
        for lay in screen_layer_indices:
            obs_name = f"{well_id}_L{lay}"
            all_continuous_observation_data.append([obs_name, "head", (lay, 0, obs_col_id)])
    
    return flopy.mf6.ModflowUtlobs(
        gwf, filename="obs", print_input=True,
        continuous=all_continuous_observation_data, pname="obs"
    ), screen_layer_indices_dict


def create_output_control_package(gwf):
    """Create output control package"""
    return flopy.mf6.ModflowGwfoc(
        gwf, budget_filerecord="axisymmetric_model.cbc",
        head_filerecord="axisymmetric_model.hds",
        saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")]
    )


def create_ims_package(sim):
    """Create iterative model solution package"""
    return flopy.mf6.ModflowIms(
        sim, print_option="SUMMARY", complexity="MODERATE",
        outer_hclose=1e-2, inner_hclose=1e-3, outer_maximum=50,
        inner_maximum=100, linear_acceleration="BICGSTAB"
    )


def run_simulation(sim):
    """Run the MODFLOW simulation"""
    sim.write_simulation()
    success, buff = sim.run_simulation(silent=True, pause=False)
    if not success:
        raise RuntimeError("MODFLOW 6 did not terminate normally.")
    return success


def process_simulation_results(config, obs_wells_data, analysis_period, pumping_length_sec, 
                              col_centroids, col_length, workspace, str_hd, 
                              screen_layer_indices_dict, cumulative_distances):
    """Process simulation results and create plots"""
    # Load head file
    head_file = flopy.utils.HeadFile(os.path.join(workspace, "axisymmetric_model.hds"))
    simulated_times = head_file.get_times()
    
    # Save final heads for recovery only scenario
    if analysis_period == "Pumping Only":
        headobj = flopy.utils.HeadFile(os.path.join(workspace, "axisymmetric_model.hds"))
        last_time_step_heads = headobj.get_data(totim=headobj.get_times()[-1])
        final_heads_filename = os.path.join(workspace, "final_heads_pumping.npy")
        np.save(final_heads_filename, last_time_step_heads)
    
    # Process observation wells
    plotter = {}
    obs_wells_distances = obs_wells_data['data']['Observation Well Distance (m)'].astype(float).tolist()
    
    def find_closest_col_index(distances, target_distance):
        return min(range(len(distances)), key=lambda i: abs(distances[i] - target_distance))
    
    obs_well_col_indices = {}
    for well_id, well_distance in zip(obs_wells_data['ids'], obs_wells_distances):
        obs_well_col_indices[well_id] = find_closest_col_index(cumulative_distances, well_distance)
    
    for well_id, file_name in obs_wells_data['files'].items():
        obs_path = file_name
        head_file_path = os.path.join(workspace, "axisymmetric_model.hds")
        obs_id = obs_well_col_indices[well_id]
        specific_screen_layer_indices = screen_layer_indices_dict[well_id]
        
        plotter[well_id] = ObservedVsSimulatedPlotter(
            head_file_path, specific_screen_layer_indices, obs_id, str_hd,
            obs_path, col_centroids, analysis_period, pumping_length_sec,
            col_length, workspace, well_id
        )
    
    # Process results for each well
    simulated_DD_dict = {}
    observed_DD_dict = {}
    observed_time_dict = {}
    
    for well_id, current_plotter in plotter.items():
        current_plotter.plot_obs_simulated()
        simulated_DD, observed_DD, observed_time = current_plotter.get_obs_DD()
        
        simulated_DD_dict[well_id] = simulated_DD
        observed_DD_dict[well_id] = observed_DD
        observed_time_dict[well_id] = observed_time
        
        current_plotter.plot_avg_head_vs_distance()
        current_plotter.save_avg_head_vs_distance_to_excel(f'Results/radius_influence_{well_id}.xlsx')
    
    # Calculate radius of influence
    first_plotter = next(iter(plotter.values()))
    radius_influence = round(first_plotter.radius_influence(), 2)
    print(f"Radius of Influence: {radius_influence} meters")
    
    # Process drawdown interpolation
    process_drawdown_interpolation(observed_DD_dict, observed_time_dict, simulated_DD_dict,
                                 simulated_times, analysis_period, pumping_length_sec)
    
    return plotter, simulated_times


def process_drawdown_interpolation(observed_DD_dict, observed_time_dict, simulated_DD_dict,
                                 simulated_times, analysis_period, pumping_length_sec):
    """Process drawdown interpolation for all wells"""
    # Filter data based on analysis period
    filtered_observed_time_dict = {}
    filtered_observed_DD_dict = {}
    
    for well_id in observed_DD_dict.keys():
        if analysis_period == "Pumping Only":
            mask = np.array(observed_time_dict[well_id]) <= pumping_length_sec
            filtered_observed_time_dict[well_id] = np.array(observed_time_dict[well_id])[mask]
            filtered_observed_DD_dict[well_id] = np.array(observed_DD_dict[well_id])[mask]
        elif analysis_period == "Recovery Only":
            mask = np.array(observed_time_dict[well_id]) > pumping_length_sec
            filtered_observed_time_dict[well_id] = np.array(observed_time_dict[well_id])[mask]
            filtered_observed_DD_dict[well_id] = np.array(observed_DD_dict[well_id])[mask]
    
    # Use filtered or original data
    if analysis_period in ["Pumping Only", "Recovery Only"]:
        final_observed_time_dict = filtered_observed_time_dict
        final_observed_DD_dict = filtered_observed_DD_dict
    else:
        final_observed_time_dict = observed_time_dict
        final_observed_DD_dict = observed_DD_dict
    
    # Process each well
    output_excel_basepath = get_output_path(analysis_period)
    
    for well_id in final_observed_time_dict.keys():
        dd_interpolator = DrawdownInterpolation(
            final_observed_time_dict[well_id], final_observed_DD_dict[well_id],
            simulated_times, simulated_DD_dict[well_id], analysis_period, pumping_length_sec
        )
        
        dd_interpolator.interpolate_to_smallest_time_step()
        dd_interpolator.interpolate_simulated_to_observed()
        
        weighted_rmse = dd_interpolator.calculate_rmse()
        total_residual_error = dd_interpolator.calculate_total_residual_error()
        
        print(f"RMSE for {well_id}: {round(weighted_rmse, 2)}")
        print(f"Total Residual Error for {well_id}: {round(total_residual_error, 2)}")
        
        output_excel_path = output_excel_basepath + f"{well_id}.xlsx"
        dd_interpolator.save_results_to_excel(output_excel_path)
        print(f"Results for {well_id} saved to {output_excel_path}")


def get_output_path(analysis_period):
    """Get output file path based on analysis period"""
    if analysis_period == "Pumping Only":
        return 'Results/DD_vs_Time_Pumping_'
    elif analysis_period == "Recovery Only":
        return 'Results/DD_vs_Time_Recovery_'
    else:
        return 'Results/DD_vs_Time_'


def run_forward_model(config, hk_profile=None, sy=None, ss=None, **kwargs):
    """Run forward model simulation"""
    # Get parameters
    basic_params = config.get_basic_parameters()
    geometry_params = config.get_model_geometry()
    time_params = config.get_time_parameters()
    obs_wells_data = config.get_observation_wells_data()
    
    # Use provided parameters or defaults
    if hk_profile is None:
        hk_profile = config.get_hydraulic_conductivity_profile()
    if sy is None:
        sy = basic_params['sy']
    if ss is None:
        ss = basic_params['ss']
    
    # Handle additional keyword arguments (for optimization results)
    if 'hk_profile' in kwargs:
        hk_profile = kwargs['hk_profile']
    if 'Specific Yield (Sy)' in kwargs:
        sy = kwargs['Specific Yield (Sy)']
    if 'Specific Storage (Ss)' in kwargs:
        ss = kwargs['Specific Storage (Ss)']
    
    # Convert pumping rate
    Q = config.converter.cubic_m_per_hour_to_cubic_m_per_sec(geometry_params['Q_m3_hr'])
    
    # Calculate discretization
    top, bottom, thickness = calculate_vertical_discretization(geometry_params)
    delr, cumulative_distances, col_centroids, ncol = calculate_horizontal_discretization(geometry_params)
    nlay = len(top)
    
    # Calculate hydraulic parameters
    hk_con, sy_con, ss_con = calculate_hydraulic_parameters(
        hk_profile, sy, ss, col_centroids, delr, thickness, config.converter, top, bottom
    )
    
    # Create MODFLOW simulation
    sim = flopy.mf6.MFSimulation(
        sim_name="axisymmetric_model", exe_name=config.mf6_exe, sim_ws=config.workspace
    )
    
    # Create packages
    tdis, pumping_length_sec, recovery_length_sec = create_time_discretization(sim, time_params, config.converter)
    gwf = create_groundwater_flow_model(sim)
    dis = create_spatial_discretization(gwf, nlay, ncol, delr, geometry_params['ztop'], bottom)
    chd = create_constant_head_package(gwf, nlay, ncol, geometry_params['specified_head'], time_params['Number_Stress_Periods'])
    lpf = create_layer_property_flow_package(gwf, hk_con, basic_params['VANI'])
    
    # Initial conditions
    strt = geometry_params['starting_head'] * np.ones((nlay, 1, ncol), dtype=np.float32)
    ic = create_initial_conditions_package(gwf, strt)
    
    # Well package
    wel = create_well_package(gwf, geometry_params, time_params, Q, top, bottom, thickness)
    
    # Storage package
    sy_values = [sy_con for _ in range(nlay)]
    sto = create_storage_package(gwf, sy_values, ss_con)
    
    # Observation package
    obs, screen_layer_indices_dict = create_observation_package(gwf, obs_wells_data, top, bottom, cumulative_distances)
    
    # Output control
    oc = create_output_control_package(gwf)
    
    # IMS
    ims = create_ims_package(sim)
    
    # Run simulation
    run_simulation(sim)
    print("MODFLOW 6 simulation completed successfully.")
    
    # Process results
    process_simulation_results(config, obs_wells_data, time_params['analysis_period'], 
                              pumping_length_sec, col_centroids, geometry_params['col_length'], 
                              config.workspace, geometry_params['starting_head'],
                              screen_layer_indices_dict, cumulative_distances)


def objective_function(parameter_values, config):
    """Objective function for optimization"""
    try:
        # Get optimization flags
        flags = config.get_optimization_flags()
        
        # Parse parameter values
        hk_profile = config.get_hydraulic_conductivity_profile()
        hk_df = config.loader.get_hydraulic_conductivity_data()
        
        # Update hk_profile with optimized values
        hk_values_list = parameter_values[:len(hk_profile)]
        remaining_values = parameter_values[len(hk_profile):]
        
        # Update hk_profile
        hk_profile_updated = {}
        for i, (depth_range, _) in enumerate(hk_profile.items()):
            if i < len(hk_values_list):
                hk_profile_updated[depth_range] = hk_values_list[i]
            else:
                hk_profile_updated[depth_range] = list(hk_profile.values())[i]
        
        # Get sy and ss values
        param_idx = 0
        sy = config.loader.at('Specific Yield (Sy)', 'Value')
        ss = config.loader.at('Specific Storage (Ss)', 'Value')
        
        if flags['solve_Sy'] == 'Yes':
            sy = remaining_values[param_idx]
            param_idx += 1
        
        if flags['solve_Ss'] == 'Yes':
            ss = remaining_values[param_idx]
        
        # Run forward model with optimized parameters and get objective value
        objective_value = run_forward_model_for_optimization(config, hk_profile=hk_profile_updated, sy=sy, ss=ss)
        
        return objective_value
        
    except Exception as e:
        print(f"MODFLOW failed with parameters: {parameter_values}. Error: {str(e)}")
        return 1e6


def run_forward_model_for_optimization(config, hk_profile=None, sy=None, ss=None):
    """Run forward model for optimization and return objective function value"""
    # Get parameters
    basic_params = config.get_basic_parameters()
    geometry_params = config.get_model_geometry()
    time_params = config.get_time_parameters()
    obs_wells_data = config.get_observation_wells_data()
    
    # Use provided parameters or defaults
    if hk_profile is None:
        hk_profile = config.get_hydraulic_conductivity_profile()
    if sy is None:
        sy = basic_params['sy']
    if ss is None:
        ss = basic_params['ss']
    
    # Convert pumping rate
    Q = config.converter.cubic_m_per_hour_to_cubic_m_per_sec(geometry_params['Q_m3_hr'])
    
    # Calculate discretization
    top, bottom, thickness = calculate_vertical_discretization(geometry_params)
    delr, cumulative_distances, col_centroids, ncol = calculate_horizontal_discretization(geometry_params)
    nlay = len(top)
    
    # Calculate hydraulic parameters
    hk_con, sy_con, ss_con = calculate_hydraulic_parameters(
        hk_profile, sy, ss, col_centroids, delr, thickness, config.converter, top, bottom
    )
    
    # Create MODFLOW simulation
    sim = flopy.mf6.MFSimulation(
        sim_name="axisymmetric_model", exe_name=config.mf6_exe, sim_ws=config.workspace
    )
    
    # Create packages
    tdis, pumping_length_sec, recovery_length_sec = create_time_discretization(sim, time_params, config.converter)
    gwf = create_groundwater_flow_model(sim)
    dis = create_spatial_discretization(gwf, nlay, ncol, delr, geometry_params['ztop'], bottom)
    chd = create_constant_head_package(gwf, nlay, ncol, geometry_params['specified_head'], time_params['Number_Stress_Periods'])
    lpf = create_layer_property_flow_package(gwf, hk_con, basic_params['VANI'])
    
    # Initial conditions
    strt = geometry_params['starting_head'] * np.ones((nlay, 1, ncol), dtype=np.float32)
    ic = create_initial_conditions_package(gwf, strt)
    
    # Well package
    wel = create_well_package(gwf, geometry_params, time_params, Q, top, bottom, thickness)
    
    # Storage package
    sy_values = [sy_con for _ in range(nlay)]
    sto = create_storage_package(gwf, sy_values, ss_con)
    
    # Observation package
    obs, screen_layer_indices_dict = create_observation_package(gwf, obs_wells_data, top, bottom, cumulative_distances)
    
    # Output control
    oc = create_output_control_package(gwf)
    
    # IMS
    ims = create_ims_package(sim)
    
    # Run simulation
    run_simulation(sim)
    
    # Calculate objective function value
    return calculate_objective_value(config, obs_wells_data, time_params['analysis_period'], 
                                   pumping_length_sec, col_centroids, geometry_params['col_length'], 
                                   config.workspace, geometry_params['starting_head'],
                                   screen_layer_indices_dict, cumulative_distances)


def calculate_objective_value(config, obs_wells_data, analysis_period, pumping_length_sec, 
                            col_centroids, col_length, workspace, str_hd, 
                            screen_layer_indices_dict, cumulative_distances):
    """Calculate objective function value for optimization"""
    # Load head file
    head_file = flopy.utils.HeadFile(os.path.join(workspace, "axisymmetric_model.hds"))
    simulated_times = head_file.get_times()
    
    # Process observation wells
    plotter = {}
    obs_wells_distances = obs_wells_data['data']['Observation Well Distance (m)'].astype(float).tolist()
    
    def find_closest_col_index(distances, target_distance):
        return min(range(len(distances)), key=lambda i: abs(distances[i] - target_distance))
    
    obs_well_col_indices = {}
    for well_id, well_distance in zip(obs_wells_data['ids'], obs_wells_distances):
        obs_well_col_indices[well_id] = find_closest_col_index(cumulative_distances, well_distance)
    
    for well_id, file_name in obs_wells_data['files'].items():
        obs_path = file_name
        head_file_path = os.path.join(workspace, "axisymmetric_model.hds")
        obs_id = obs_well_col_indices[well_id]
        specific_screen_layer_indices = screen_layer_indices_dict[well_id]
        
        plotter[well_id] = ObservedVsSimulatedPlotter(
            head_file_path, specific_screen_layer_indices, obs_id, str_hd,
            obs_path, col_centroids, analysis_period, pumping_length_sec,
            col_length, workspace, well_id
        )
    
    # Process results for each well
    simulated_DD_dict = {}
    observed_DD_dict = {}
    observed_time_dict = {}
    
    for well_id, current_plotter in plotter.items():
        simulated_DD, observed_DD, observed_time = current_plotter.get_obs_DD()
        
        simulated_DD_dict[well_id] = simulated_DD
        observed_DD_dict[well_id] = observed_DD
        observed_time_dict[well_id] = observed_time
    
    # Filter data based on analysis period
    filtered_observed_time_dict = {}
    filtered_observed_DD_dict = {}
    
    for well_id in observed_DD_dict.keys():
        if analysis_period == "Pumping Only":
            mask = np.array(observed_time_dict[well_id]) <= pumping_length_sec
            filtered_observed_time_dict[well_id] = np.array(observed_time_dict[well_id])[mask]
            filtered_observed_DD_dict[well_id] = np.array(observed_DD_dict[well_id])[mask]
        elif analysis_period == "Recovery Only":
            mask = np.array(observed_time_dict[well_id]) > pumping_length_sec
            filtered_observed_time_dict[well_id] = np.array(observed_time_dict[well_id])[mask]
            filtered_observed_DD_dict[well_id] = np.array(observed_DD_dict[well_id])[mask]
    
    # Use filtered or original data
    if analysis_period in ["Pumping Only", "Recovery Only"]:
        final_observed_time_dict = filtered_observed_time_dict
        final_observed_DD_dict = filtered_observed_DD_dict
    else:
        final_observed_time_dict = observed_time_dict
        final_observed_DD_dict = observed_DD_dict
    
    # Calculate objective function
    total_weighted_rmse = 0
    total_residual_error_sum = 0
    num_wells = len(final_observed_time_dict.keys())
    
    for well_id in final_observed_time_dict.keys():
        dd_interpolator = DrawdownInterpolation(
            final_observed_time_dict[well_id], final_observed_DD_dict[well_id],
            simulated_times, simulated_DD_dict[well_id], analysis_period, pumping_length_sec
        )
        
        dd_interpolator.interpolate_to_smallest_time_step()
        dd_interpolator.interpolate_simulated_to_observed()
        
        total_weighted_rmse += dd_interpolator.calculate_rmse()
        total_residual_error_sum += dd_interpolator.calculate_total_residual_error()
    
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
    
    return objective_value


def run_optimization(config):
    """Run parameter optimization"""
    # Get optimization flags
    flags = config.get_optimization_flags()
    
    # Setup optimization parameters
    params_to_optimize = []
    initial_guess = []
    
    if flags['solve_Hk'] == 'Yes':
        hk_df = config.loader.get_hydraulic_conductivity_data()
        for index, row in hk_df.iterrows():
            params_to_optimize.append(f'hk_layer_{index+1}')
            initial_guess.append(row['Hydraulic Conductivity [m/day]'])
    
    if flags['solve_Sy'] == 'Yes':
        params_to_optimize.append('sy')
        initial_guess.append(config.loader.at('Specific Yield (Sy)', 'Value'))
    
    if flags['solve_Ss'] == 'Yes':
        params_to_optimize.append('ss')
        initial_guess.append(config.loader.at('Specific Storage (Ss)', 'Value'))
    
    # Run optimization
    result = fmin(lambda x: objective_function(x, config), initial_guess, maxiter=4, disp=True)
    
    # Process and print optimal results
    process_optimization_results(config, result, params_to_optimize, flags)
    
    print("Optimization completed.")
    return result


def process_optimization_results(config, result, params_to_optimize, flags):
    """Process and print optimization results"""
    # Get hydraulic conductivity data
    hk_df = config.loader.get_hydraulic_conductivity_data()
    hk_profile = config.get_hydraulic_conductivity_profile()
    
    # Extract optimal parameters
    hk_results = result[:len(hk_profile)]  # First N results for hk values
    remaining_results = result[len(hk_profile):]
    
    # Get sy and ss results
    sy_result = remaining_results[0] if flags['solve_Sy'] == 'Yes' else config.loader.at('Specific Yield (Sy)', 'Value')
    ss_result = remaining_results[1] if flags['solve_Ss'] == 'Yes' else config.loader.at('Specific Storage (Ss)', 'Value')
    
    # Create hydraulic conductivity results DataFrame
    hk_results_df = pd.DataFrame({
        'Layer': [f'Layer {i+1}' for i in range(len(hk_results))],
        'Optimal Hydraulic Conductivity [m/day]': hk_results
    })
    
    # Create results dictionary
    results_dict = {}
    
    # Recreate hk_profile from hk_results
    hk_profile_optimized = {}
    for index, row in hk_df.iterrows():
        depth_range = (row['Layer Top Level [m]'], row['Layer Bottom Level [m]'])
        hk_value = hk_results[index] if index < len(hk_results) else row['Hydraulic Conductivity [m/day]']
        hk_profile_optimized[depth_range] = hk_value
    
    results_dict['hk_profile'] = hk_profile_optimized
    
    # Add sy and ss to results
    if flags['solve_Sy'] == 'Yes':
        results_dict["Specific Yield (Sy)"] = sy_result
    if flags['solve_Ss'] == 'Yes':
        results_dict["Specific Storage (Ss)"] = ss_result
    
    # Create DataFrame for other results
    other_results_df = pd.DataFrame([{k: v for k, v in results_dict.items() if k != "hk_profile"}])
    
    # Get analysis period for file naming
    analysis_period = config.loader.at('Analysis Period', 'Value')
    
    # Determine output file paths
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
    
    # Save results to Excel files
    hk_results_df.to_excel(output_excel_path_hk, index=False)
    print("======================================================================")
    print(f"Hydraulic conductivity results saved to {output_excel_path_hk}")
    
    other_results_df.to_excel(output_excel_path_other, index=False)
    print(f"Other results saved to {output_excel_path_other}")
    
    # Print the results
    print("====================================================================")
    print("Optimal Parameter Values:")
    print(hk_results_df)
    print("====================================================================")
    print(other_results_df)
    print("====================================================================")
    
    # Run forward model with optimal parameters
    print("Running forward model with optimal parameters...")
    run_forward_model(config, **results_dict)


def main():
    """Main execution function"""
    start_time = time.time()
    
    # Initialize configuration
    config = ModelConfig("Model_Inputs.json")
    
    # Get basic parameters
    basic_params = config.get_basic_parameters()
    run_type = basic_params['run_type']
    
    print(f"Starting {run_type} simulation...")
    
    if run_type.startswith("Forward Run"):
        # Run forward model
        hk_profile = config.get_hydraulic_conductivity_profile()
        run_forward_model(config, hk_profile=hk_profile, 
                         sy=basic_params['sy'], ss=basic_params['ss'])
    else:
        # Run optimization
        run_optimization(config)
    
    # Calculate and print elapsed time
    end_time = time.time()
    elapsed_time = round(end_time - start_time, 3)
    
    if elapsed_time > 60:
        elapsed_time = round(elapsed_time / 60, 2)
        print(f"Elapsed time: {elapsed_time} minutes")
    else:
        print(f"Elapsed time: {elapsed_time} seconds")


if __name__ == "__main__":
    main()
