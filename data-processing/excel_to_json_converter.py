#!/usr/bin/env python3
"""
Excel to JSON Converter for Model_Inputs.xlsx
Converts Excel file with multiple sheets to structured JSON format
"""

import pandas as pd
import json
import sys
from pathlib import Path

def clean_dataframe(df):
    """Clean the dataframe by removing completely empty rows and columns"""
    # Remove rows where all values are NaN
    df = df.dropna(how='all')
    # Remove columns where all values are NaN
    df = df.dropna(axis=1, how='all')
    return df

def convert_model_inputs_sheet(df):
    """Convert the Model Inputs sheet to a structured dictionary"""
    # Clean the dataframe
    df = clean_dataframe(df)
    
    # Create a structured dictionary
    result = {}
    
    # Group related parameters
    sections = {
        'radial_discretization': ['Boundary distance from pumping well', '2nd Column Size', 'Column Multiplier'],
        'vertical_discretization': ['Saturated top elevation', 'Aquifer bottom elevation', 
                                   'Screen top - Cell thickness', 'Screen bottom- Cell thickness',
                                   'Refinment above screen', 'Refinment below screen', 'Refinment between screen'],
        'pumping_well': ['Well Radius', 'Q', 'Screen Top Elevation', 'Screen Bottom Elevation'],
        'observation_wells': ['Observation Wells', 'Observation Well Distance (m)', 
                             'Observation Top Screen Level (m)', 'Observation Bottom Screen Level (m)'],
        'initial_boundary_conditions': ['Starting Head', 'Specified Head'],
        'stress_periods': ['Analysis Period', 'Pumping length', 'Recovery length', 
                          'Number of time steps', 'Time Multiplier', 'Time Units'],
        'hydraulic_parameters': ['Hydraulic Conductivity', 'Vk/Hk Ratio', 'Specific Yield (Sy)', 'Specific Storage (Ss)'],
        'simulation_settings': ['Choose Type of Simulation', 'Hydraulic Conductivity', 'Vk/Hk Ratio', 
                               'Specific Yield (Sy)', 'Specific Storage (Ss)'],
        'data_files': ['Observed Data']
    }
    
    # Process each row
    for idx, row in df.iterrows():
        if pd.isna(row.iloc[0]):  # Skip empty rows
            continue
            
        param_name = str(row.iloc[0]).strip()
        if param_name == 'nan' or param_name == 'Input':
            continue
            
        # Find which section this parameter belongs to
        section = 'general'
        for sec_name, params in sections.items():
            if param_name in params:
                section = sec_name
                break
        
        # Create section if it doesn't exist
        if section not in result:
            result[section] = {}
        
        # Extract value and unit
        value = row.iloc[1] if len(row) > 1 and not pd.isna(row.iloc[1]) else None
        unit = row.iloc[2] if len(row) > 2 and not pd.isna(row.iloc[2]) else None
        
        # Store the parameter
        param_data = {'value': value}
        if unit:
            param_data['unit'] = unit
        
        result[section][param_name] = param_data
    
    return result

def convert_hydraulic_conductivity_sheet(df):
    """Convert the Hydraulic Conductivity sheet to a structured dictionary"""
    # Clean the dataframe
    df = clean_dataframe(df)
    
    # Convert to list of dictionaries
    result = []
    for idx, row in df.iterrows():
        if pd.isna(row.iloc[0]):  # Skip empty rows
            continue
            
        layer_data = {
            'soil_material': str(row.iloc[0]) if not pd.isna(row.iloc[0]) else None,
            'layer_top_level_m': float(row.iloc[1]) if not pd.isna(row.iloc[1]) else None,
            'layer_bottom_level_m': float(row.iloc[2]) if not pd.isna(row.iloc[2]) else None,
            'hydraulic_conductivity_m_per_day': float(row.iloc[3]) if not pd.isna(row.iloc[3]) else None
        }
        result.append(layer_data)
    
    return result

def convert_excel_to_json(excel_file_path, output_file_path=None):
    """Convert Excel file to JSON format"""
    try:
        # Read the Excel file
        xl = pd.ExcelFile(excel_file_path)
        
        # Initialize the result dictionary
        result = {
            'metadata': {
                'source_file': str(excel_file_path),
                'sheets': xl.sheet_names,
                'conversion_timestamp': pd.Timestamp.now().isoformat()
            },
            'data': {}
        }
        
        # Process each sheet
        for sheet_name in xl.sheet_names:
            print(f"Processing sheet: {sheet_name}")
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            
            if sheet_name == 'Model Inputs':
                result['data']['model_inputs'] = convert_model_inputs_sheet(df)
            elif sheet_name == 'Hydraulic Conductivity':
                result['data']['hydraulic_conductivity'] = convert_hydraulic_conductivity_sheet(df)
            else:
                # Generic conversion for other sheets
                df_clean = clean_dataframe(df)
                result['data'][sheet_name.lower().replace(' ', '_')] = df_clean.to_dict('records')
        
        # Write to JSON file
        if output_file_path is None:
            output_file_path = excel_file_path.with_suffix('.json')
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Successfully converted {excel_file_path} to {output_file_path}")
        return output_file_path
        
    except Exception as e:
        print(f"Error converting Excel file: {e}")
        return None

def main():
    """Main function"""
    excel_file = Path('Model_Inputs.xlsx')
    
    if not excel_file.exists():
        print(f"Error: {excel_file} not found!")
        sys.exit(1)
    
    output_file = convert_excel_to_json(excel_file)
    
    if output_file:
        print(f"Conversion completed successfully!")
        print(f"Output file: {output_file}")
    else:
        print("Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
