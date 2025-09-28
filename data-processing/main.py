#!/usr/bin/env python3
"""
Refactored main.py - contains only the main function
All simulation functions have been moved to ModelSimulator class
Configuration management has been moved to ModelConfig class
"""

import time
from classes import ModelSimulator, ModelConfig


def main():
    """Main execution function"""
    start_time = time.time()
    
    # Initialize configuration
    config = ModelConfig("Model_Inputs.json")
    
    # Get basic parameters
    basic_params = config.get_basic_parameters()
    run_type = basic_params['run_type']
    
    print(f"Starting {run_type} simulation...")
    
    # Initialize simulator
    simulator = ModelSimulator(config)
    
    if run_type.startswith("Forward Run"):
        # Run forward model
        hk_profile = config.get_hydraulic_conductivity_profile()
        simulator.run_forward_model(hk_profile=hk_profile, 
                                   sy=basic_params['sy'], ss=basic_params['ss'])
    else:
        # Run optimization
        simulator.run_optimization()
    
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