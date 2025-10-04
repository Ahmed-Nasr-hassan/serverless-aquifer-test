#!/usr/bin/env python3
"""
Refactored main.py - contains only the main function
All simulation functions have been moved to ModelSimulator class
Configuration management has been moved to ModelConfig class
"""

import time
import json
import boto3
import os
from classes import ModelSimulator, ModelConfig


def main(config_file="Model_Inputs.json"):
    """Main execution function"""
    start_time = time.time()
    
    # Initialize configuration
    config = ModelConfig(config_file)
    
    # Get basic parameters
    basic_params = config.get_basic_parameters()
    run_type = basic_params['run_type']
    
    print(f"Starting {run_type} simulation...")
    
    # Initialize simulator
    simulator = ModelSimulator(config)
    
    if run_type.startswith("Forward Run"):
        # Run forward model
        hk_profile = config.get_hydraulic_conductivity_profile()
        json_results = simulator.run_forward_model(hk_profile=hk_profile, 
                                   sy=basic_params['sy'], ss=basic_params['ss'])
    else:
        # Run optimization
        json_results = simulator.run_optimization()
    
    # Print JSON results summary
    if json_results:
        print("\n" + "="*60)
        print("SIMULATION RESULTS SUMMARY")
        print("="*60)
        print(f"Simulation Type: {json_results['metadata']['simulation_type']}")
        print(f"Radius of Influence: {json_results['summary']['radius_of_influence_meters']} meters")
        print(f"Total Wells Analyzed: {json_results['summary']['total_wells_analyzed']}")
        
        if 'optimization_results' in json_results:
            print(f"Parameters Optimized: {', '.join(json_results['optimization_results']['parameters_optimized'])}")
        
        print("\nFiles Generated:")
        if 'optimization_results' in json_results:
            print(f"  JSON Results: {json_results['optimization_results']['files_generated']['json_results']}")
        else:
            print(f"  JSON Results: Results/simulation_results.json")
        
        print("="*60)
    # Calculate and print elapsed time
    end_time = time.time()
    elapsed_time = round(end_time - start_time, 3)
    
    if elapsed_time > 60:
        elapsed_time = round(elapsed_time / 60, 2)
        print(f"Elapsed time: {elapsed_time} minutes")
    else:
        print(f"Elapsed time: {elapsed_time} seconds")

    return json_results


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    Processes SQS messages containing Model_Inputs.json data
    """
    try:
        print(f"Lambda function started. Event: {json.dumps(event)}")
        
        # Initialize SQS client
        sqs = boto3.client('sqs')
        
        # Process SQS records
        for record in event.get('Records', []):
            try:
                # Parse SQS message body
                message_body = json.loads(record['body'])
                print(f"Processing message: {message_body}")
                
                # Extract Model_Inputs.json from message
                model_inputs = message_body.get('model_inputs', {})
                
                if not model_inputs:
                    print("No Model_Inputs found in message")
                    continue
                
                # Add hydraulic_conductivity if missing
                if 'hydraulic_conductivity' not in model_inputs:
                    model_inputs['hydraulic_conductivity'] = [
                        {
                            "soil_material": "Sandstone",
                            "layer_top_level_m": 0.0,
                            "layer_bottom_level_m": -700.0,
                            "hydraulic_conductivity_m_per_day": 0.9073948333333328
                        }
                    ]
                
                # Wrap the model_inputs in the expected structure for JsonDataLoader
                wrapped_data = {
                    "data": {
                        "model_inputs": model_inputs,
                        "hydraulic_conductivity": message_body.get('hydraulic_conductivity', [])
                    }
                }
                
                # Write Model_Inputs.json to /tmp/ directory (Lambda writable)
                with open('/tmp/Model_Inputs.json', 'w') as f:
                    json.dump(wrapped_data, f, indent=2)
                
                print("Model_Inputs.json written to /tmp/Model_Inputs.json")
                
                # Run simulation with the /tmp/ config file
                result = main("/tmp/Model_Inputs.json")
                
                # Return results
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "message": "Simulation completed successfully",
                        "results": result,
                        "requestId": context.aws_request_id
                    })
                }
                
            except Exception as e:
                print(f"Error processing record: {str(e)}")
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "error": str(e),
                        "requestId": context.aws_request_id
                    })
                }
        
        # If no records, run with default Model_Inputs.json
        if not event.get('Records'):
            print("No SQS records found, running with default Model_Inputs.json")
            result = main()
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Simulation completed successfully",
                    "results": result,
                    "requestId": context.aws_request_id
                })
            }
            
    except Exception as e:
        print(f"Lambda function error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "requestId": context.aws_request_id if context else "unknown"
            })
        }


if __name__ == "__main__":
    main()