"""
JSON Data Loader for Model Inputs
Replaces pandas.read_excel functionality with JSON-based data loading
Compatible with AWS Lambda and SQS integration
"""

import json
import pandas as pd
from typing import Dict, List, Any, Union, Optional


class JsonDataLoader:
    """
    A class to load model input data from JSON files instead of Excel files.
    This makes the code compatible with AWS Lambda and SQS integration.
    """
    
    def __init__(self, json_file_path: str = None, json_data: Dict = None):
        """
        Initialize the JSON data loader.
        
        Args:
            json_file_path: Path to JSON file (optional if json_data is provided)
            json_data: Dictionary containing the data (optional if json_file_path is provided)
        """
        if json_data is not None:
            self.data = json_data
        elif json_file_path is not None:
            with open(json_file_path, 'r') as f:
                self.data = json.load(f)
        else:
            raise ValueError("Either json_file_path or json_data must be provided")
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the main parameters section.
        
        Args:
            key: The parameter key
            default: Default value if key not found
            
        Returns:
            The parameter value
        """
        return self.data.get('parameters', {}).get(key, default)
    
    def get_hydraulic_conductivity_profile(self) -> Dict[tuple, float]:
        """
        Get hydraulic conductivity profile as a dictionary.
        
        Returns:
            Dictionary with (top_level, bottom_level) tuples as keys and K values as values
        """
        hk_data = self.data.get('hydraulic_conductivity', [])
        hk_profile = {}
        
        for layer in hk_data:
            top_level = layer.get('layer_top_level_m')
            bottom_level = layer.get('layer_bottom_level_m')
            k_value = layer.get('hydraulic_conductivity_m_per_day')
            
            if top_level is not None and bottom_level is not None and k_value is not None:
                hk_profile[(top_level, bottom_level)] = k_value
        
        return hk_profile
    
    def get_observation_wells_data(self) -> pd.DataFrame:
        """
        Get observation wells data as a pandas DataFrame.
        
        Returns:
            DataFrame with observation wells data
        """
        obs_wells = self.data.get('observation_wells', [])
        
        if not obs_wells:
            return pd.DataFrame()
        
        # Convert to DataFrame format similar to Excel reading
        data = []
        for well in obs_wells:
            data.append({
                'Well ID': well.get('well_id'),
                'Observation Well Distance (m)': well.get('distance_m'),
                'Observation Top Screen Level (m)': well.get('top_screen_level_m'),
                'Observation Bottom Screen Level (m)': well.get('bottom_screen_level_m')
            })
        
        return pd.DataFrame(data)
    
    def get_observation_well_ids(self) -> List[str]:
        """
        Get list of observation well IDs.
        
        Returns:
            List of well IDs
        """
        obs_wells = self.data.get('observation_wells', [])
        return [well.get('well_id') for well in obs_wells if well.get('well_id')]
    
    def get_observed_data_file(self) -> str:
        """
        Get the path to the observed data CSV file.
        
        Returns:
            Path to the CSV file
        """
        return self.data.get('parameters', {}).get('observed_data_file', '')
    
    def get_optimization_parameters(self) -> Dict[str, bool]:
        """
        Get which parameters should be optimized.
        
        Returns:
            Dictionary with parameter names as keys and optimization flags as values
        """
        return self.data.get('optimization', {})
    
    def get_run_type(self) -> str:
        """
        Get the type of simulation to run.
        
        Returns:
            'Forward Run' or 'Optimization'
        """
        return self.data.get('parameters', {}).get('simulation_type', 'Forward Run')
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the main parameters to a DataFrame for compatibility with existing code.
        
        Returns:
            DataFrame with the same structure as the Excel file
        """
        parameters = self.data.get('parameters', {})
        
        # Create a list of tuples for DataFrame
        data = []
        for key, value in parameters.items():
            data.append((key, value, '', '', ''))  # Empty columns for compatibility
        
        df = pd.DataFrame(data, columns=['Input', 'Value', 'Unit', 'Unnamed: 3', 'Unnamed: 4'])
        return df
    
    @staticmethod
    def create_sample_json() -> Dict[str, Any]:
        """
        Create a sample JSON structure based on the current Excel file.
        
        Returns:
            Dictionary representing the JSON structure
        """
        return {
            "parameters": {
                "boundary_distance_from_pumping_well_m": 500,
                "column_size_m": 0.01,
                "column_multiplier": 1.1,
                "saturated_top_elevation_m": -121.84,
                "aquifer_bottom_elevation_m": -500,
                "screen_top_cell_thickness_m": 0.01,
                "screen_bottom_cell_thickness_m": 0.01,
                "refinement_above_screen": 1.6,
                "refinement_below_screen": 1.3,
                "refinement_between_screen": 1.1,
                "well_radius_m": 0.22,
                "pumping_rate_m3_per_hr": -141,
                "screen_top_elevation_m": -212,
                "screen_bottom_elevation_m": -378,
                "starting_head_m": -121.84,
                "specified_head_m": -121.84,
                "analysis_period": "Pumping + Recovery",
                "pumping_length_minutes": 720,
                "recovery_length_minutes": 840,
                "number_of_time_steps": 200,
                "time_multiplier": 1.05,
                "time_units": "SECONDS",
                "hydraulic_conductivity_m_per_day": 1,
                "vk_hk_ratio": 1,
                "specific_yield_sy": 0.124808,
                "specific_storage_ss_per_m": 3.84771e-07,
                "observed_data_file": "Al_Monera.csv",
                "simulation_type": "Forward Run"
            },
            "hydraulic_conductivity": [
                {
                    "soil_material": "Sandstone",
                    "layer_top_level_m": 0,
                    "layer_bottom_level_m": -700,
                    "hydraulic_conductivity_m_per_day": 0.777767
                }
            ],
            "observation_wells": [
                {
                    "well_id": "OBS-1",
                    "distance_m": 53,
                    "top_screen_level_m": -212,
                    "bottom_screen_level_m": -300
                }
            ],
            "optimization": {
                "hydraulic_conductivity": True,
                "vk_hk_ratio": False,
                "specific_yield_sy": True,
                "specific_storage_ss": True
            }
        }


def convert_excel_to_json(excel_file_path: str, json_file_path: str):
    """
    Convert an Excel file to JSON format.
    
    Args:
        excel_file_path: Path to the Excel file
        json_file_path: Path where the JSON file should be saved
    """
    # Read the main sheet
    df = pd.read_excel(excel_file_path)
    
    # Extract parameters
    parameters = {}
    for i, row in df.iterrows():
        if pd.notna(row['Input']) and pd.notna(row['Value']):
            # Convert Excel key to JSON key
            key = row['Input'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('³', '3').replace('/', '_per_')
            parameters[key] = row['Value']
    
    # Read hydraulic conductivity sheet
    try:
        hk_df = pd.read_excel(excel_file_path, sheet_name='Hydraulic Conductivity')
        hydraulic_conductivity = []
        for i, row in hk_df.iterrows():
            hydraulic_conductivity.append({
                "soil_material": row['Soil Material'],
                "layer_top_level_m": row['Layer Top Level [m]'],
                "layer_bottom_level_m": row['Layer Bottom Level [m]'],
                "hydraulic_conductivity_m_per_day": row['Hydraulic Conductivity [m/day]']
            })
    except Exception as e:
        print(f"Error reading hydraulic conductivity sheet: {e}")
        hydraulic_conductivity = []
    
    # Read observation wells data
    try:
        obs_well_ids = pd.read_excel(excel_file_path, skiprows=18, nrows=1, header=None).values.flatten()
        obs_well_ids = [id for id in obs_well_ids if not pd.isna(id) and str(id).startswith('OBS')]
        
        obs_wells_data = pd.read_excel(excel_file_path, skiprows=18, usecols=lambda x: 'Unnamed' not in x, nrows=3)
        obs_wells_data = obs_wells_data.T.reset_index(drop=True)
        obs_wells_data = obs_wells_data.iloc[:len(obs_well_ids)+1]
        obs_wells_data.columns = ['Observation Well Distance (m)', 'Observation Top Screen Level (m)', 'Observation Bottom Screen Level (m)']
        obs_wells_data.drop(index=0, inplace=True)
        obs_wells_data.insert(0, 'Well ID', obs_well_ids)
        
        observation_wells = []
        for i, row in obs_wells_data.iterrows():
            observation_wells.append({
                "well_id": row['Well ID'],
                "distance_m": row['Observation Well Distance (m)'],
                "top_screen_level_m": row['Observation Top Screen Level (m)'],
                "bottom_screen_level_m": row['Observation Bottom Screen Level (m)']
            })
    except Exception as e:
        print(f"Error reading observation wells data: {e}")
        observation_wells = []
    
    # Create the JSON structure
    json_data = {
        "parameters": parameters,
        "hydraulic_conductivity": hydraulic_conductivity,
        "observation_wells": observation_wells,
        "optimization": {
            "hydraulic_conductivity": parameters.get("hydraulic_conductivity", "Yes") == "Yes",
            "vk_hk_ratio": parameters.get("vk_hk_ratio", "No") == "Yes",
            "specific_yield_sy": parameters.get("specific_yield_sy", "Yes") == "Yes",
            "specific_storage_ss": parameters.get("specific_storage_ss", "Yes") == "Yes"
        }
    }
    
    # Save to JSON file
    with open(json_file_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"Successfully converted {excel_file_path} to {json_file_path}")


if __name__ == "__main__":
    # Convert the existing Excel file to JSON
    convert_excel_to_json("Model_Inputs.xlsx", "Model_Inputs.json")
