#!/usr/bin/env python3
"""
ModelSimulator class containing all simulation-related functions
Refactored from main.py to follow separation of concerns
"""

import time
import numpy as np
import flopy
import pandas as pd
import os
from scipy.optimize import fmin

# Local imports
from .VerticalRefinment import VerticalRefinement
from .conversions import ParametersConversions
from .Units import UnitConverter
from .Plotter import ObservedVsSimulatedPlotter
from .ColumnCalculator import ColumnCalculator
from .DrawdownInterpolation import DrawdownInterpolation

class ModelSimulator:
    """Class containing all simulation-related functions"""
    
    def __init__(self, config):
        self.config = config
    
    def calculate_vertical_discretization(self, geometry_params):
        """Calculate vertical discretization using VerticalRefinement"""
        vr = VerticalRefinement(
            geometry_params['ztop'], geometry_params['zbot'],
            geometry_params['sc_top'], geometry_params['sc_bottom'],
            geometry_params['sc_top_thick'], geometry_params['sc_bottom_thick'],
            geometry_params['refine_above_screen'], geometry_params['refine_below_screen'],
            geometry_params['refine_between_screen']
        )
        return vr.calculate_thicknesses()

    def calculate_horizontal_discretization(self, geometry_params):
        """Calculate horizontal discretization using ColumnCalculator"""
        column_calculator = ColumnCalculator(
            geometry_params['col_length'],
            geometry_params['radius_well'],
            geometry_params['cell_size'],
            geometry_params['horizontal_multiplier']
        )
        return column_calculator.calculate_columns()

    def calculate_hydraulic_parameters(self, hk_profile, sy, ss, col_centroids, delr, thickness, converter, top, bottom):
        """Calculate converted hydraulic parameters"""
        # Convert hk_profile to m/sec
        hk_profile_m_sec = {depth_range: converter.meters_per_day_to_meters_per_sec(hk) 
                            for depth_range, hk in hk_profile.items()}
        
        # Calculate hk values for each layer
        hk_values = []
        for i in range(len(top)):
            layer_midpoint = (top[i] + bottom[i]) / 2
            hk_assigned = False
            for depth_range, hk_value in hk_profile_m_sec.items():
                # Check if layer midpoint falls within the depth range
                # depth_range[0] is top level, depth_range[1] is bottom level
                # For negative depths: top >= midpoint > bottom (e.g., 0 >= -142.34 > -700)
                if depth_range[0] >= layer_midpoint > depth_range[1]:
                    hk_values.append(hk_value)
                    hk_assigned = True
                    break
            
            # If no match found, use the first available hk value as default
            if not hk_assigned:
                if hk_profile_m_sec:
                    hk_values.append(list(hk_profile_m_sec.values())[0])
                else:
                    hk_values.append(1e-6)  # Default very low conductivity
        
        # Calculate converted parameters
        par = ParametersConversions(col_centroids, delr, thickness)
        par.set_original_parameters(hk_values, sy, ss)
        return par.calculate_converted_parameters()

    def create_time_discretization(self, sim, time_params, converter):
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

    def create_groundwater_flow_model(self, sim):
        """Create groundwater flow model"""
        return flopy.mf6.ModflowGwf(sim, modelname="ax_model", save_flows=True)

    def create_spatial_discretization(self, gwf, nlay, ncol, delr, ztop, bottom):
        """Create spatial discretization package"""
        return flopy.mf6.ModflowGwfdis(
            gwf, nlay=nlay, nrow=1, ncol=ncol, delr=delr, delc=1.0,
            top=ztop, botm=bottom
        )

    def create_constant_head_package(self, gwf, nlay, ncol, specified_head, Number_Stress_Periods):
        """Create constant head boundary package"""
        chd_data = [[(nlay-1, 0, ncol - 1), specified_head]]
        perioddata = {i: chd_data for i in range(Number_Stress_Periods)}
        return flopy.mf6.ModflowGwfchd(gwf, stress_period_data=perioddata)

    def create_layer_property_flow_package(self, gwf, hk_con, VANI):
        """Create layer property flow package"""
        return flopy.mf6.ModflowGwfnpf(
            gwf, icelltype=3, k33overk=True, k=hk_con, k33=VANI,
            save_flows=True, alternative_cell_averaging="LOGARITHMIC", cvoptions="DEWATERED"
        )

    def create_initial_conditions_package(self, gwf, strt):
        """Create initial conditions package"""
        return flopy.mf6.ModflowGwfic(gwf, strt=strt)

    def create_well_package(self, gwf, geometry_params, time_params, Q, top, bottom, thickness):
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

    def create_storage_package(self, gwf, sy_values, ss_values):
        """Create storage package"""
        return flopy.mf6.ModflowGwfsto(
            gwf, pname="sto", iconvert=1, ss=ss_values, sy=sy_values, transient={0: True}
        )

    def create_observation_package(self, gwf, obs_wells_data, top, bottom, cumulative_distances):
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
            
            # Find screen layer indices - layers that intersect with the screen interval
            screen_layer_indices = [lay for lay, (lay_top, lay_bottom) in enumerate(zip(top, bottom))
                                    if lay_top > obs_sc_bottom and lay_bottom < obs_sc_top]
            
            
            screen_layer_indices_dict[well_id] = screen_layer_indices
            
            # Add observation points
            for lay in screen_layer_indices:
                obs_name = f"{well_id}_L{lay}"
                all_continuous_observation_data.append([obs_name, "head", (lay, 0, obs_col_id)])
        
        return flopy.mf6.ModflowUtlobs(
            gwf, filename="obs", print_input=True,
            continuous=all_continuous_observation_data, pname="obs"
        ), screen_layer_indices_dict

    def create_output_control_package(self, gwf):
        """Create output control package"""
        return flopy.mf6.ModflowGwfoc(
            gwf, budget_filerecord="axisymmetric_model.cbc",
            head_filerecord="axisymmetric_model.hds",
            saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")]
        )

    def create_ims_package(self, sim):
        """Create iterative model solution package"""
        return flopy.mf6.ModflowIms(
            sim, print_option="SUMMARY", complexity="MODERATE",
            outer_hclose=1e-2, inner_hclose=1e-3, outer_maximum=50,
            inner_maximum=100, linear_acceleration="BICGSTAB"
        )

    def run_simulation(self, sim):
        """Run the MODFLOW simulation"""
        sim.write_simulation()
        success, buff = sim.run_simulation(silent=True, pause=False)
        if not success:
            raise RuntimeError("MODFLOW 6 did not terminate normally.")
        return success

    def process_simulation_results(self, obs_wells_data, analysis_period, pumping_length_sec, 
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
            # Skip plot generation - only get data for JSON
            simulated_DD, observed_DD, observed_time = current_plotter.get_obs_DD()
            
            simulated_DD_dict[well_id] = simulated_DD
            observed_DD_dict[well_id] = observed_DD
            observed_time_dict[well_id] = observed_time
            
            # Calculate head vs distance data for JSON (without generating plot)
            current_plotter._calculate_avg_head_at_depth()
        
        # Calculate radius of influence
        first_plotter = next(iter(plotter.values()))
        radius_influence = round(first_plotter.radius_influence(), 2)
        print(f"Radius of Influence: {radius_influence} meters")
        
        # Process drawdown interpolation
        interpolation_results = self.process_drawdown_interpolation(observed_DD_dict, observed_time_dict, simulated_DD_dict,
                                         simulated_times, analysis_period, pumping_length_sec)
        
        # Generate JSON output
        json_results = self.generate_json_results(plotter, simulated_times, radius_influence, 
                                                interpolation_results, analysis_period, pumping_length_sec)
        
        return plotter, simulated_times, json_results

    def process_drawdown_interpolation(self, observed_DD_dict, observed_time_dict, simulated_DD_dict,
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
        output_excel_basepath = self.get_output_path(analysis_period)
        interpolation_results = {}
        
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
            
            # Skip Excel file generation - only store data for JSON
            
            # Store results for JSON output
            interpolation_results[well_id] = {
                'rmse': round(weighted_rmse, 4),
                'total_residual_error': round(total_residual_error, 4),
                'interpolated_times': dd_interpolator.interpolated_times.tolist() if dd_interpolator.interpolated_times is not None else [],
                'interpolated_observed_drawdown': dd_interpolator.interpolated_observed_drawdown.tolist() if dd_interpolator.interpolated_observed_drawdown is not None else [],
                'interpolated_simulated_drawdown': dd_interpolator.interpolated_simulated_drawdown.tolist() if dd_interpolator.interpolated_simulated_drawdown is not None else []
            }
        
        return interpolation_results

    def get_output_path(self, analysis_period):
        """Get output file path based on analysis period"""
        if analysis_period == "Pumping Only":
            return 'Results/DD_vs_Time_Pumping_'
        elif analysis_period == "Recovery Only":
            return 'Results/DD_vs_Time_Recovery_'
        else:
            return 'Results/DD_vs_Time_'
    
    def _format_json_compact(self, obj, indent=0):
        """Custom JSON formatter that puts ALL lists on one line"""
        import json
        
        if isinstance(obj, list):
            # ALL lists on one line, regardless of length
            items = []
            for item in obj:
                if isinstance(item, (list, dict)):
                    items.append(self._format_json_compact(item, indent + 1))
                else:
                    items.append(json.dumps(item, separators=(',', ': ')))
            return '[' + ','.join(items) + ']'
        elif isinstance(obj, dict):
            items = []
            for key, value in obj.items():
                if isinstance(value, list):
                    items.append(f'"{key}":{self._format_json_compact(value, indent + 1)}')
                else:
                    items.append(f'"{key}":{self._format_json_compact(value, indent + 1)}')
            return '{\n' + ',\n'.join('  ' * (indent + 1) + item for item in items) + '\n' + '  ' * indent + '}'
        else:
            return json.dumps(obj, separators=(',', ': '))

    def generate_json_results(self, plotter, simulated_times, radius_influence, 
                            interpolation_results, analysis_period, pumping_length_sec):
        """Generate comprehensive JSON output with all simulation results"""
        import json
        from datetime import datetime
        
        # Convert simulated times to list for JSON serialization
        simulated_times_list = simulated_times.tolist() if hasattr(simulated_times, 'tolist') else list(simulated_times)
        
        # Build results structure
        results = {
            'metadata': {
                'simulation_type': analysis_period,
                'pumping_length_seconds': pumping_length_sec,
                'generated_at': datetime.now().isoformat(),
                'total_simulation_time_steps': len(simulated_times_list)
            },
            'summary': {
                'radius_of_influence_meters': radius_influence,
                'total_wells_analyzed': len(plotter)
            },
            'simulation_times': simulated_times_list,
            'wells': {}
        }
        
        # Process each well's results
        for well_id, current_plotter in plotter.items():
            # Get drawdown data
            simulated_DD, observed_DD, observed_time = current_plotter.get_obs_DD()
            
            # Get head vs distance data
            avg_head_at_depth = getattr(current_plotter, 'avg_head_at_depth', [])
            
            # Get interpolation results for this well
            well_interpolation = interpolation_results.get(well_id, {})
            
            # Build well data structure
            well_data = {
                'well_id': well_id,
                'distance_from_pumping_well_meters': current_plotter.distance,
                'simulation_results': {
                    'simulated_drawdown_meters': simulated_DD,
                    'observed_drawdown_meters': observed_DD,
                    'observed_time_seconds': observed_time,
                    'avg_head_at_distance_meters': avg_head_at_depth
                },
                'interpolation_results': well_interpolation,
                'files_generated': {
                    'json_results': 'Results/simulation_results.json'
                }
            }
            
            results['wells'][well_id] = well_data
        
        return results

    def run_forward_model(self, hk_profile=None, sy=None, ss=None, **kwargs):
        """Run forward model simulation"""
        # Get parameters
        basic_params = self.config.get_basic_parameters()
        geometry_params = self.config.get_model_geometry()
        time_params = self.config.get_time_parameters()
        obs_wells_data = self.config.get_observation_wells_data()
        
        # Use provided parameters or defaults
        if hk_profile is None:
            hk_profile = self.config.get_hydraulic_conductivity_profile()
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
        Q = self.config.converter.cubic_m_per_hour_to_cubic_m_per_sec(geometry_params['Q_m3_hr'])
        
        # Calculate discretization
        top, bottom, thickness = self.calculate_vertical_discretization(geometry_params)
        delr, cumulative_distances, col_centroids, ncol = self.calculate_horizontal_discretization(geometry_params)
        nlay = len(top)
        
        # Calculate hydraulic parameters
        hk_con, sy_con, ss_con = self.calculate_hydraulic_parameters(
            hk_profile, sy, ss, col_centroids, delr, thickness, self.config.converter, top, bottom
        )
        
        # Create MODFLOW simulation
        sim = flopy.mf6.MFSimulation(
            sim_name="axisymmetric_model", exe_name=self.config.mf6_exe, sim_ws=self.config.workspace
        )
        
        # Create packages
        tdis, pumping_length_sec, recovery_length_sec = self.create_time_discretization(sim, time_params, self.config.converter)
        gwf = self.create_groundwater_flow_model(sim)
        dis = self.create_spatial_discretization(gwf, nlay, ncol, delr, geometry_params['ztop'], bottom)
        chd = self.create_constant_head_package(gwf, nlay, ncol, geometry_params['specified_head'], time_params['Number_Stress_Periods'])
        lpf = self.create_layer_property_flow_package(gwf, hk_con, basic_params['VANI'])
        
        # Initial conditions
        strt = geometry_params['starting_head'] * np.ones((nlay, 1, ncol), dtype=np.float32)
        ic = self.create_initial_conditions_package(gwf, strt)
        
        # Well package
        wel = self.create_well_package(gwf, geometry_params, time_params, Q, top, bottom, thickness)
        
        # Storage package
        sy_values = [sy_con for _ in range(nlay)]
        sto = self.create_storage_package(gwf, sy_values, ss_con)
        
        # Observation package
        obs, screen_layer_indices_dict = self.create_observation_package(gwf, obs_wells_data, top, bottom, cumulative_distances)
        
        # Output control
        oc = self.create_output_control_package(gwf)
        
        # IMS
        ims = self.create_ims_package(sim)
        
        # Run simulation
        self.run_simulation(sim)
        print("MODFLOW 6 simulation completed successfully.")
        
        # Process results
        plotter, simulated_times, json_results = self.process_simulation_results(obs_wells_data, time_params['analysis_period'], 
                                      pumping_length_sec, col_centroids, geometry_params['col_length'], 
                                      self.config.workspace, geometry_params['starting_head'],
                                      screen_layer_indices_dict, cumulative_distances)
        
        # Save JSON results to file
        import json
        with open('Results/simulation_results.json', 'w') as f:
            f.write(self._format_json_compact(json_results))
        print("JSON results saved to Results/simulation_results.json")
        
        return json_results

    def objective_function(self, parameter_values):
        """Objective function for optimization"""
        try:
            # Get optimization flags
            flags = self.config.get_optimization_flags()
            
            # Parse parameter values based on what was actually optimized
            hk_profile = self.config.get_hydraulic_conductivity_profile()
            hk_df = self.config.loader.get_hydraulic_conductivity_data()
            
            param_idx = 0
            hk_values_list = []
            sy = self.config.loader.at('Specific Yield (Sy)', 'Value')
            ss = self.config.loader.at('Specific Storage (Ss)', 'Value')
            
            # Extract hk values if they were optimized
            if flags['solve_Hk'] == 'Yes':
                hk_values_list = parameter_values[param_idx:param_idx + len(hk_profile)]
                param_idx += len(hk_profile)
            
            # Extract sy value if it was optimized
            if flags['solve_Sy'] == 'Yes':
                sy = parameter_values[param_idx]
                param_idx += 1
            
            # Extract ss value if it was optimized
            if flags['solve_Ss'] == 'Yes':
                ss = parameter_values[param_idx]
            
            # Update hk_profile with optimized values
            hk_profile_updated = {}
            if len(hk_values_list) > 0:
                for i, (depth_range, _) in enumerate(hk_profile.items()):
                    if i < len(hk_values_list):
                        hk_profile_updated[depth_range] = hk_values_list[i]
                    else:
                        hk_profile_updated[depth_range] = list(hk_profile.values())[i]
            else:
                hk_profile_updated = hk_profile
            
            # Debug: Print parameters being used in optimization
            print(f"DEBUG: Optimization iteration - hk_profile: {hk_profile_updated}, sy: {sy}, ss: {ss}")
            
            # Run forward model with optimized parameters and get objective value
            objective_value = self.run_forward_model_for_optimization(hk_profile=hk_profile_updated, sy=sy, ss=ss)
            
            return objective_value
            
        except Exception as e:
            print(f"MODFLOW failed with parameters: {parameter_values}. Error: {str(e)}")
            return 1e6

    def run_forward_model_for_optimization(self, hk_profile=None, sy=None, ss=None):
        """Run forward model for optimization and return objective function value"""
        # Get parameters
        basic_params = self.config.get_basic_parameters()
        geometry_params = self.config.get_model_geometry()
        time_params = self.config.get_time_parameters()
        obs_wells_data = self.config.get_observation_wells_data()
        
        # Use provided parameters or defaults
        if hk_profile is None:
            hk_profile = self.config.get_hydraulic_conductivity_profile()
        if sy is None:
            sy = basic_params['sy']
        if ss is None:
            ss = basic_params['ss']
        
        # Convert pumping rate
        Q = self.config.converter.cubic_m_per_hour_to_cubic_m_per_sec(geometry_params['Q_m3_hr'])
        
        # Calculate discretization
        top, bottom, thickness = self.calculate_vertical_discretization(geometry_params)
        delr, cumulative_distances, col_centroids, ncol = self.calculate_horizontal_discretization(geometry_params)
        nlay = len(top)
        
        # Calculate hydraulic parameters
        hk_con, sy_con, ss_con = self.calculate_hydraulic_parameters(
            hk_profile, sy, ss, col_centroids, delr, thickness, self.config.converter, top, bottom
        )
        
        # Create MODFLOW simulation
        sim = flopy.mf6.MFSimulation(
            sim_name="axisymmetric_model", exe_name=self.config.mf6_exe, sim_ws=self.config.workspace
        )
        
        # Create packages
        tdis, pumping_length_sec, recovery_length_sec = self.create_time_discretization(sim, time_params, self.config.converter)
        gwf = self.create_groundwater_flow_model(sim)
        dis = self.create_spatial_discretization(gwf, nlay, ncol, delr, geometry_params['ztop'], bottom)
        chd = self.create_constant_head_package(gwf, nlay, ncol, geometry_params['specified_head'], time_params['Number_Stress_Periods'])
        lpf = self.create_layer_property_flow_package(gwf, hk_con, basic_params['VANI'])
        
        # Initial conditions
        strt = geometry_params['starting_head'] * np.ones((nlay, 1, ncol), dtype=np.float32)
        ic = self.create_initial_conditions_package(gwf, strt)
        
        # Well package
        wel = self.create_well_package(gwf, geometry_params, time_params, Q, top, bottom, thickness)
        
        # Storage package
        sy_values = [sy_con for _ in range(nlay)]
        sto = self.create_storage_package(gwf, sy_values, ss_con)
        
        # Observation package
        obs, screen_layer_indices_dict = self.create_observation_package(gwf, obs_wells_data, top, bottom, cumulative_distances)
        
        # Output control
        oc = self.create_output_control_package(gwf)
        
        # IMS
        ims = self.create_ims_package(sim)
        
        # Run simulation with error handling
        try:
            self.run_simulation(sim)
        except Exception as e:
            print(f"MODFLOW simulation failed: {str(e)}")
            return 1e6  # Return large penalty for failed simulation
        
        # Calculate objective function value
        return self.calculate_objective_value(obs_wells_data, time_params['analysis_period'], 
                                           pumping_length_sec, col_centroids, geometry_params['col_length'], 
                                           self.config.workspace, geometry_params['starting_head'],
                                           screen_layer_indices_dict, cumulative_distances)

    def calculate_objective_value(self, obs_wells_data, analysis_period, pumping_length_sec, 
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

    def run_optimization(self):
        """Run parameter optimization"""
        # Get optimization flags
        flags = self.config.get_optimization_flags()
        print(f"DEBUG: Optimization flags: {flags}")
        
        # Setup optimization parameters
        params_to_optimize = []
        initial_guess = []
        
        if flags['solve_Hk'] == 'Yes':
            hk_df = self.config.loader.get_hydraulic_conductivity_data()
            for index, row in hk_df.iterrows():
                params_to_optimize.append(f'hk_layer_{index+1}')
                initial_guess.append(row['Hydraulic Conductivity [m/day]'])
        
        if flags['solve_Sy'] == 'Yes':
            params_to_optimize.append('sy')
            initial_guess.append(self.config.loader.at('Specific Yield (Sy)', 'Value'))
        
        if flags['solve_Ss'] == 'Yes':
            params_to_optimize.append('ss')
            initial_guess.append(self.config.loader.at('Specific Storage (Ss)', 'Value'))
        
        print(f"DEBUG: Parameters to optimize: {params_to_optimize}")
        print(f"DEBUG: Initial guess: {initial_guess}")
        
        if not initial_guess:
            print("ERROR: No parameters selected for optimization!")
            return None
        
        # Run optimization
        result = fmin(lambda x: self.objective_function(x), initial_guess, maxiter=4, disp=True)
        print(result)
        # Process and print optimal results
        json_results = self.process_optimization_results(result, params_to_optimize, flags)
        
        print("Optimization completed.")
        return json_results

    def process_optimization_results(self, result, params_to_optimize, flags):
        """Process and print optimization results"""
        # Get hydraulic conductivity data
        hk_df = self.config.loader.get_hydraulic_conductivity_data()
        hk_profile = self.config.get_hydraulic_conductivity_profile()
        
        # Extract optimal parameters based on what was actually optimized
        param_idx = 0
        hk_results = []
        sy_result = self.config.loader.at('Specific Yield (Sy)', 'Value')
        ss_result = self.config.loader.at('Specific Storage (Ss)', 'Value')
        
        # Extract hk values if they were optimized
        if flags['solve_Hk'] == 'Yes':
            hk_results = result[param_idx:param_idx + len(hk_profile)]
            param_idx += len(hk_profile)
        
        # Extract sy value if it was optimized
        if flags['solve_Sy'] == 'Yes':
            sy_result = result[param_idx]
            param_idx += 1
        
        # Extract ss value if it was optimized
        if flags['solve_Ss'] == 'Yes':
            ss_result = result[param_idx]
        
        # Create hydraulic conductivity results DataFrame
        if len(hk_results) > 0:
            hk_results_df = pd.DataFrame({
                'Layer': [f'Layer {i+1}' for i in range(len(hk_results))],
                'Optimal Hydraulic Conductivity [m/day]': hk_results
            })
        else:
            hk_results_df = pd.DataFrame({
                'Layer': [f'Layer {i+1}' for i in range(len(hk_profile))],
                'Optimal Hydraulic Conductivity [m/day]': list(hk_profile.values())
            })
        
        # Create results dictionary
        results_dict = {}
        
        # Recreate hk_profile from hk_results or use original
        hk_profile_optimized = {}
        if len(hk_results) > 0:
            for index, row in hk_df.iterrows():
                depth_range = (row['Layer Top Level [m]'], row['Layer Bottom Level [m]'])
                hk_value = hk_results[index] if index < len(hk_results) else row['Hydraulic Conductivity [m/day]']
                hk_profile_optimized[depth_range] = hk_value
        else:
            hk_profile_optimized = hk_profile
        
        results_dict['hk_profile'] = hk_profile_optimized
        
        # Add sy and ss to results
        if flags['solve_Sy'] == 'Yes':
            results_dict["Specific Yield (Sy)"] = sy_result
        if flags['solve_Ss'] == 'Yes':
            results_dict["Specific Storage (Ss)"] = ss_result
        
        # Create DataFrame for other results
        other_results_df = pd.DataFrame([{k: v for k, v in results_dict.items() if k != "hk_profile"}])
                
        
        # Skip Excel file generation - only print results
        print("======================================================================")
        print("Optimal Parameter Values:")
        print(hk_results_df)
        print("====================================================================")
        print(other_results_df)
        print("====================================================================")
        
        # Debug: Print the optimal parameters being used
        print("====================================================================")
        print("DEBUG: Optimal parameters being used for final forward run:")
        print(f"hk_profile_optimized: {hk_profile_optimized}")
        print(f"sy_result: {sy_result}")
        print(f"ss_result: {ss_result}")
        print("====================================================================")
        
        # Run forward model with optimal parameters
        print("Running forward model with optimal parameters...")
        json_results = self.run_forward_model(**results_dict)
        
        # Convert hk_profile tuple keys to string keys for JSON serialization
        hk_profile_json = {}
        for (top, bottom), value in hk_profile_optimized.items():
            key = f"layer_{top}m_to_{bottom}m"
            hk_profile_json[key] = value
        
        # Add optimization results to JSON output
        json_results['optimization_results'] = {
            'parameters_optimized': params_to_optimize,
            'optimal_values': {
                'hk_profile': hk_profile_json,
                'specific_yield': sy_result if flags['solve_Sy'] == 'Yes' else None,
                'specific_storage': ss_result if flags['solve_Ss'] == 'Yes' else None
            },
            'files_generated': {
                'json_results': 'Results/optimization_results.json'
            }
        }
        
        # Save updated JSON results
        with open('Results/optimization_results.json', 'w') as f:
            f.write(self._format_json_compact(json_results))
        print("Optimization JSON results saved to Results/optimization_results.json")
        
        return json_results
