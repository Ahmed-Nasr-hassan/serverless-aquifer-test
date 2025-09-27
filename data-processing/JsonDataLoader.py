#!/usr/bin/env python3
"""
JSON Data Loader for Model_Inputs.json
Provides a pandas-like interface for accessing JSON data
"""

import json
import pandas as pd
from pathlib import Path

class JsonDataLoader:
    """A class to load and access JSON data in a pandas-like manner"""
    
    def __init__(self, json_file_path):
        """Initialize the loader with a JSON file path"""
        self.json_file_path = Path(json_file_path)
        self.data = self._load_json()
        self._create_flat_mapping()
    
    def _load_json(self):
        """Load JSON data from file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise FileNotFoundError(f"Could not load JSON file {self.json_file_path}: {e}")
    
    def _create_flat_mapping(self):
        """Create a flat mapping for easy access similar to pandas DataFrame"""
        self.flat_data = {}
        self.row_mapping = {}
        
        # Map the JSON structure to row indices similar to the original Excel
        row_index = 0
        
        # Model Inputs section
        model_inputs = self.data['data']['model_inputs']
        
        # Add general parameters
        for param_name, param_data in model_inputs.get('general', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add radial discretization parameters
        for param_name, param_data in model_inputs.get('radial_discretization', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add vertical discretization parameters
        for param_name, param_data in model_inputs.get('vertical_discretization', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add pumping well parameters
        for param_name, param_data in model_inputs.get('pumping_well', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add observation wells parameters
        for param_name, param_data in model_inputs.get('observation_wells', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add initial boundary conditions parameters
        for param_name, param_data in model_inputs.get('initial_boundary_conditions', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add stress periods parameters
        for param_name, param_data in model_inputs.get('stress_periods', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add hydraulic parameters
        for param_name, param_data in model_inputs.get('hydraulic_parameters', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add data files parameters
        for param_name, param_data in model_inputs.get('data_files', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
        
        # Add simulation settings parameters
        for param_name, param_data in model_inputs.get('simulation_settings', {}).items():
            self.flat_data[row_index] = {
                'Input': param_name,
                'Value': param_data.get('value'),
                'Unit': param_data.get('unit')
            }
            self.row_mapping[param_name] = row_index
            row_index += 1
    
    def at(self, row, column):
        """Pandas-like at accessor for getting values by row and column"""
        if isinstance(row, str):
            # If row is a string, find the row index
            if row in self.row_mapping:
                row_idx = self.row_mapping[row]
            else:
                raise KeyError(f"Parameter '{row}' not found in data")
        else:
            row_idx = row
        
        if row_idx not in self.flat_data:
            raise KeyError(f"Row {row_idx} not found in data")
        
        if column not in self.flat_data[row_idx]:
            raise KeyError(f"Column '{column}' not found in row {row_idx}")
        
        return self.flat_data[row_idx][column]
    
    def get_hydraulic_conductivity_data(self):
        """Get hydraulic conductivity data as a pandas DataFrame"""
        hk_data = self.data['data']['hydraulic_conductivity']
        
        # Convert to DataFrame format
        df_data = []
        for layer in hk_data:
            df_data.append({
                'Layer Top Level [m]': layer['layer_top_level_m'],
                'Layer Bottom Level [m]': layer['layer_bottom_level_m'],
                'Hydraulic Conductivity [m/day]': layer['hydraulic_conductivity_m_per_day'],
                'Soil Material': layer['soil_material']
            })
        
        return pd.DataFrame(df_data)
    
    def get_observation_wells_data(self):
        """Get observation wells data as a pandas DataFrame"""
        # Extract observation well data from the flat mapping
        obs_data = []
        
        # Get observation well IDs and distances
        well_ids = self.at('Observation Wells', 'Value')
        distances = self.at('Observation Well Distance (m)', 'Value')
        top_levels = self.at('Observation Top Screen Level (m)', 'Value')
        bottom_levels = self.at('Observation Bottom Screen Level (m)', 'Value')
        
        # Handle multiple wells if they exist
        if isinstance(well_ids, str) and well_ids.startswith('OBS'):
            # Single well case
            obs_data.append({
                'Well ID': well_ids,
                'Observation Well Distance (m)': distances,
                'Observation Top Screen Level (m)': top_levels,
                'Observation Bottom Screen Level (m)': bottom_levels
            })
        
        return pd.DataFrame(obs_data)
    
    def get_observation_well_files(self):
        """Get observation well file paths"""
        obs_well_path = self.at('Observation Well Path', 'Value')
        observed_data_file = self.at('Observed Data', 'Value')
        
        # Return as dictionary similar to the original Excel reading
        return {obs_well_path: observed_data_file}
    
    def to_dataframe(self):
        """Convert the flat data to a pandas DataFrame"""
        df_data = []
        for row_idx in sorted(self.flat_data.keys()):
            df_data.append(self.flat_data[row_idx])
        
        return pd.DataFrame(df_data)
    
    def __getitem__(self, key):
        """Allow dictionary-like access"""
        return self.flat_data[key]
    
    def __len__(self):
        """Return the number of rows"""
        return len(self.flat_data)
    
    def keys(self):
        """Return the keys (row indices)"""
        return self.flat_data.keys()
    
    def values(self):
        """Return the values"""
        return self.flat_data.values()
    
    def items(self):
        """Return the items"""
        return self.flat_data.items()
