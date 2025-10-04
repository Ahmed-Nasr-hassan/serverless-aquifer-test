#!/usr/bin/env python3
"""
ModelConfig class for managing model configuration and parameters
"""

import os
from .JsonDataLoader import JsonDataLoader
from .Units import UnitConverter


class ModelConfig:
    """Configuration class to hold all model parameters and provide data access"""
    
    def __init__(self, json_file_path="Model_Inputs.json"):
        self.loader = JsonDataLoader(json_file_path)
        self.converter = UnitConverter()
        
        # Check if running in Lambda (environment variables present)
        if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
            # Running in Lambda - use /tmp for writable directories
            self.workspace = '/tmp/workspace'
            self.mf6_exe = "/tmp/bin/mf6"
            # Create writable directories
            os.makedirs('/tmp/Results', exist_ok=True)
            os.makedirs(self.workspace, exist_ok=True)
        else:
            # Running locally
            self.workspace = 'workspace'
            self.mf6_exe = "./bin/mf6"
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
        import pandas as pd
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
