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


def update_simulation_result(simulation_id: str, results_json: dict) -> None:
	"""Update the simulations table: set status=completed and results JSON.
	Reads DATABASE_URL from env, defaults to local DSN.
	"""
	import psycopg2
	from psycopg2.extras import Json

	# Prefer full DATABASE_URL if provided; otherwise compose from parts
	database_url = os.getenv("DATABASE_URL")
	if not database_url:
		db_user = os.getenv("DB_USER", "aquifer_user")
		db_password = os.getenv("DB_PASSWORD", "aquifer_password")
		db_host = os.getenv("DB_HOST", "98.90.146.86")  # Default to current public IP if not provided
		db_port = os.getenv("DB_PORT", "5432")
		db_name = os.getenv("DB_NAME", "aquifer_db")
		database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
	conn = None
	try:
		conn = psycopg2.connect(database_url)
		conn.autocommit = True
		with conn.cursor() as cur:
			cur.execute(
				"""
				UPDATE simulations
				SET status = %s,
				    results = %s,
				    completed_at = NOW()
				WHERE id = %s
				""",
				(
					"completed",
					Json(results_json),
					simulation_id,
				),
			)
	except Exception as e:
		print(f"Failed to update simulation {simulation_id} in database: {e}")
	finally:
		if conn:
			conn.close()


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

	# If a simulation_id was provided in the input data, persist results to DB
	try:
		with open(config_file, 'r') as f:
			root = json.load(f)
		# Support both wrapped {"data": {...}} and flat structures
		payload = root.get('data', root)
		simulation_id = payload.get('simulation_id')
		if simulation_id and json_results:
			update_simulation_result(simulation_id=str(simulation_id), results_json=json_results)
			print(f"Updated simulation {simulation_id} status to completed with results.")
	except Exception as e:
		print(f"Post-processing error (DB update may have been skipped): {e}")

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
				# Updated to accept wrapped format with metadata and data
				wrapped = message_body
				payload = wrapped.get('data', wrapped)
				model_inputs = payload.get('model_inputs', {})
				simulation_id = payload.get('simulation_id')
				
				if not model_inputs:
					print("No Model_Inputs found in message")
					continue
				
				# Add hydraulic_conductivity if missing
				if 'hydraulic_conductivity' not in payload:
					payload['hydraulic_conductivity'] = [
						{
							"soil_material": "Sandstone",
							"layer_top_level_m": 0.0,
							"layer_bottom_level_m": -700.0,
							"hydraulic_conductivity_m_per_day": 0.9073948333333328
						}
					]
				
				# Write Model_Inputs.json to /tmp/ directory (Lambda writable)
				with open('/tmp/Model_Inputs.json', 'w') as f:
					json.dump({"data": payload}, f, indent=2)
				
				print("Model_Inputs.json written to /tmp/Model_Inputs.json")
				
				# Run simulation with the /tmp/ config file
				result = main("/tmp/Model_Inputs.json")
				
				# After run, if we have simulation_id, update DB directly from here as well (belt-and-braces)
				if simulation_id and result:
					update_simulation_result(simulation_id=str(simulation_id), results_json=result)
				
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