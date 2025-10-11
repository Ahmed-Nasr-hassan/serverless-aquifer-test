#!/usr/bin/env python3
"""
Initialize database with test data for the new 2-entity architecture.
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database import SessionLocal, create_tables
from models import Model, Simulation

def create_test_data():
    """Create test data for the new architecture."""
    print("🌱 Creating test data for new architecture...")
    
    # Create tables first
    create_tables()
    
    db = SessionLocal()
    try:
        # Test Model 1: Aquifer Model
        aquifer_model = Model(
            name="Test Aquifer Model",
            description="A test aquifer model for development and testing",
            model_type="aquifer",
            configuration={
                "aquiferConfig": {
                    "ztop": 100.0,
                    "specificYield": 0.2,
                    "specificStorage": 0.0001,
                    "hydraulicConductivity": [
                        {"layer": 1, "top": 100.0, "bottom": 80.0, "k": 10.0},
                        {"layer": 2, "top": 80.0, "bottom": 60.0, "k": 5.0},
                        {"layer": 3, "top": 60.0, "bottom": 40.0, "k": 2.0}
                    ]
                },
                "wellConfig": {
                    "pumpingRate": 1000.0,
                    "wellRadius": 0.1,
                    "screenTop": 50.0,
                    "screenBottom": 30.0,
                    "distanceFromWell": 10.0
                },
                "observationPoints": [
                    {
                        "id": "OBS-1",
                        "name": "Observation Well 1",
                        "distanceFromWell": 53.0,
                        "topScreenLevel": -212.0,
                        "bottomScreenLevel": -300.0,
                        "dataPoints": [
                            {"timeMinutes": 0, "waterLevel": 45.3, "drawdown": 0},
                            {"timeMinutes": 5, "waterLevel": 45.82, "drawdown": 0.52},
                            {"timeMinutes": 10, "waterLevel": 46.32, "drawdown": 1.02},
                            {"timeMinutes": 15, "waterLevel": 46.78, "drawdown": 1.48},
                            {"timeMinutes": 20, "waterLevel": 47.15, "drawdown": 1.85}
                        ]
                    },
                    {
                        "id": "OBS-2",
                        "name": "Observation Well 2",
                        "distanceFromWell": 75.0,
                        "topScreenLevel": -150.0,
                        "bottomScreenLevel": -210.0,
                        "dataPoints": [
                            {"timeMinutes": 0, "waterLevel": 45.3, "drawdown": 0},
                            {"timeMinutes": 5, "waterLevel": 45.65, "drawdown": 0.35},
                            {"timeMinutes": 10, "waterLevel": 45.95, "drawdown": 0.65},
                            {"timeMinutes": 15, "waterLevel": 46.20, "drawdown": 0.90},
                            {"timeMinutes": 20, "waterLevel": 46.40, "drawdown": 1.10}
                        ]
                    }
                ],
                "simulationConfig": {
                    "simulationTimeDays": 30,
                    "timeStepDays": 0.1,
                    "runType": "forward"
                }
            },
            status="active",
            user_id="test-user-123"
        )
        
        db.add(aquifer_model)
        db.flush()  # Get the ID
        
        # Test Model 2: Well Model
        well_model = Model(
            name="Test Well Model",
            description="A test well model for optimization studies",
            model_type="well",
            configuration={
                "wellConfig": {
                    "pumpingRate": 2000.0,
                    "wellRadius": 0.15,
                    "screenTop": 40.0,
                    "screenBottom": 20.0,
                    "distanceFromWell": 15.0
                },
                "simulationConfig": {
                    "simulationTimeDays": 15,
                    "timeStepDays": 0.05,
                    "runType": "optimization"
                },
                "optimizationConfig": {
                    "parametersToOptimize": ["hydraulicConductivity", "specificYield"],
                    "parameterBounds": {
                        "hydraulicConductivity": {"min": 1.0, "max": 20.0},
                        "specificYield": {"min": 0.1, "max": 0.3}
                    },
                    "targetRMSE": 0.1,
                    "maxIterations": 50
                }
            },
            status="active",
            user_id="test-user-123"
        )
        
        db.add(well_model)
        db.flush()  # Get the ID
        
        # Test Simulation 1: Forward Run
        forward_simulation = Simulation(
            model_id=aquifer_model.id,
            name="Aquifer Forward Run",
            description="Forward simulation run for aquifer model",
            simulation_type="Forward Run",
            status="completed",
            simulation_settings={
                "Choose Type of Simulation": {
                    "value": "Forward Run"
                },
                "Hydraulic Conductivity Flag": {
                    "value": "Yes"
                },
                "Vk/Hk Ratio Flag": {
                    "value": "No"
                },
                "Specific Yield (Sy) Flag": {
                    "value": "Yes"
                },
                "Specific Storage (Ss) Flag": {
                    "value": "Yes"
                }
            },
            results={
                "metadata": {
                    "simulation_type": "Pumping + Recovery",
                    "pumping_length_seconds": 177960,
                    "generated_at": "2025-01-04T20:59:25.241926",
                    "total_simulation_time_steps": 400
                },
                "summary": {
                    "radius_of_influence_meters": 195.65,
                    "total_wells_analyzed": 2
                },
                "simulation_times": [0.5145856873998947, 1.0549006591697843, 1.6222313795281682, 2.2179286359044714, 2.84341075509959, 3.5001669802544644],
                "wells": {
                    "OBS-1": {
                        "well_id": "OBS-1",
                        "distance_from_pumping_well_meters": [0.11, 0.225, 0.23550000000000001, 0.24705000000000005, 0.25975500000000007],
                        "simulation_results": {
                            "simulated_drawdown_meters": [-3.655990961625043e-06, -3.5547425368697027e-06, -3.2148930490589264e-06, -2.296674255417328e-06],
                            "observed_drawdown_meters": [0, 0.52, 1.02, 1.17, 1.27],
                            "observed_time_seconds": [0, 300, 600, 900, 1200, 1500, 1800],
                            "avg_head_at_distance_meters": [-143.07964404261162, -140.41935299597378, -140.25016407225218, -140.07295579250209, -139.8877866733983]
                        },
                        "interpolation_results": {
                            "rmse": 0.3871,
                            "total_residual_error": 316.1503,
                            "interpolated_times": [0, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300],
                            "interpolated_observed_drawdown": [0.0, 0.52, 1.02, 1.17, 1.27, 1.33, 1.39],
                            "interpolated_simulated_drawdown": [-3.752418032820605e-06, 0.25951029899853684, 0.47364193480655914, 0.628128751613359]
                        },
                        "files_generated": {
                            "json_results": "Results/simulation_results.json"
                        }
                    },
                    "OBS-2": {
                        "well_id": "OBS-2",
                        "distance_from_pumping_well_meters": [0.11, 0.225, 0.23550000000000001, 0.24705000000000005, 0.25975500000000007],
                        "simulation_results": {
                            "simulated_drawdown_meters": [-3.655990961625043e-06, -3.5547425368697027e-06, -3.2148930490589264e-06, -2.296674255417328e-06],
                            "observed_drawdown_meters": [0, 0.52, 1.02, 1.17, 1.27],
                            "observed_time_seconds": [0, 300, 600, 900, 1200, 1500, 1800],
                            "avg_head_at_distance_meters": [-143.07964404261162, -140.41935299597378, -140.25016407225218, -140.07295579250209, -139.8877866733983]
                        },
                        "interpolation_results": {
                            "rmse": 0.63871,
                            "total_residual_error": 210.1503,
                            "interpolated_times": [0, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300],
                            "interpolated_observed_drawdown": [0.0, 0.52, 1.02, 1.17, 1.27, 1.33, 1.39],
                            "interpolated_simulated_drawdown": [-3.752418032820605e-06, 0.25951029899853684, 0.47364193480655914, 0.628128751613359]
                        },
                        "files_generated": {
                            "json_results": "Results/simulation_results.json"
                        }
                    }
                }
            },
            radius_of_influence_meters=195.65,
            total_wells_analyzed=2,
            pumping_length_seconds=177960.0,
            total_simulation_time_steps=400,
            user_id="test-user-123"
        )
        
        db.add(forward_simulation)
        
        # Test Simulation 2: Optimization Run
        optimization_simulation = Simulation(
            model_id=well_model.id,
            name="Well Optimization Run",
            description="Optimization simulation for well model",
            simulation_type="Optimization",
            status="completed",
            simulation_settings={
                "Choose Type of Simulation": {
                    "value": "Optimization"
                },
                "Hydraulic Conductivity Flag": {
                    "value": "Yes"
                },
                "Vk/Hk Ratio Flag": {
                    "value": "Yes"
                },
                "Specific Yield (Sy) Flag": {
                    "value": "Yes"
                },
                "Specific Storage (Ss) Flag": {
                    "value": "No"
                }
            },
            results={
                "metadata": {
                    "simulation_type": "Pumping + Recovery",
                    "pumping_length_seconds": 177960,
                    "generated_at": "2025-01-04T20:59:25.241926",
                    "total_simulation_time_steps": 400
                },
                "summary": {
                    "radius_of_influence_meters": 195.65,
                    "total_wells_analyzed": 2
                },
                "simulation_times": [0.5145856873998947, 1.0549006591697843, 1.6222313795281682, 2.2179286359044714, 2.84341075509959, 3.5001669802544644],
                "wells": {
                    "OBS-1": {
                        "well_id": "OBS-1",
                        "distance_from_pumping_well_meters": [0.11, 0.225, 0.23550000000000001, 0.24705000000000005, 0.25975500000000007],
                        "simulation_results": {
                            "simulated_drawdown_meters": [-3.655990961625043e-06, -3.5547425368697027e-06, -3.2148930490589264e-06, -2.296674255417328e-06],
                            "observed_drawdown_meters": [0, 0.52, 1.02, 1.17, 1.27],
                            "observed_time_seconds": [0, 300, 600, 900, 1200, 1500, 1800],
                            "avg_head_at_distance_meters": [-143.07964404261162, -140.41935299597378, -140.25016407225218, -140.07295579250209, -139.8877866733983]
                        },
                        "interpolation_results": {
                            "rmse": 0.3871,
                            "total_residual_error": 316.1503,
                            "interpolated_times": [0, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300],
                            "interpolated_observed_drawdown": [0.0, 0.52, 1.02, 1.17, 1.27, 1.33, 1.39],
                            "interpolated_simulated_drawdown": [-3.752418032820605e-06, 0.25951029899853684, 0.47364193480655914, 0.628128751613359]
                        },
                        "files_generated": {
                            "json_results": "Results/simulation_results.json"
                        }
                    },
                    "OBS-2": {
                        "well_id": "OBS-2",
                        "distance_from_pumping_well_meters": [0.11, 0.225, 0.23550000000000001, 0.24705000000000005, 0.25975500000000007],
                        "simulation_results": {
                            "simulated_drawdown_meters": [-3.655990961625043e-06, -3.5547425368697027e-06, -3.2148930490589264e-06, -2.296674255417328e-06],
                            "observed_drawdown_meters": [0, 0.52, 1.02, 1.17, 1.27],
                            "observed_time_seconds": [0, 300, 600, 900, 1200, 1500, 1800],
                            "avg_head_at_distance_meters": [-143.07964404261162, -140.41935299597378, -140.25016407225218, -140.07295579250209, -139.8877866733983]
                        },
                        "interpolation_results": {
                            "rmse": 0.63871,
                            "total_residual_error": 210.1503,
                            "interpolated_times": [0, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300],
                            "interpolated_observed_drawdown": [0.0, 0.52, 1.02, 1.17, 1.27, 1.33, 1.39],
                            "interpolated_simulated_drawdown": [-3.752418032820605e-06, 0.25951029899853684, 0.47364193480655914, 0.628128751613359]
                        },
                        "files_generated": {
                            "json_results": "Results/simulation_results.json"
                        }
                    }
                },
                "optimization_results": {
                    "parameters_optimized": ["hk_layer_1", "hk_layer_2", "sy", "ss"],
                    "optimal_values": {
                        "hk_profile": {
                            "layer_0.0m_to_-350.0m": 0.8166553499999993,
                            "layer_-350.0m_to_-700.0m": 51.875
                        },
                        "specific_yield": 0.12099988999999994,
                        "specific_storage": 4.1261751785416686e-07
                    },
                    "files_generated": {
                        "json_results": "Results/optimization_results.json"
                    }
                }
            },
            radius_of_influence_meters=195.65,
            total_wells_analyzed=2,
            pumping_length_seconds=177960.0,
            total_simulation_time_steps=400,
            user_id="test-user-123"
        )
        
        db.add(optimization_simulation)
        
        # Test Simulation 3: Pending Run
        pending_simulation = Simulation(
            model_id=aquifer_model.id,
            name="Aquifer Sensitivity Analysis",
            description="Sensitivity analysis simulation (pending)",
            simulation_type="Sensitivity Analysis",
            status="pending",
            user_id="test-user-123"
        )
        
        db.add(pending_simulation)
        
        db.commit()
        
        print("✅ Test data created successfully!")
        print(f"   - Created {db.query(Model).count()} models")
        print(f"   - Created {db.query(Simulation).count()} simulations")
        print(f"   - Aquifer model ID: {aquifer_model.id}")
        print(f"   - Well model ID: {well_model.id}")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function."""
    print("🌱 Initializing Database with Test Data")
    print("=" * 40)
    
    try:
        create_test_data()
        print("")
        print("🎉 Database initialization completed!")
        print("   You can now run the API tests or start the frontend.")
        
    except Exception as e:
        print(f"")
        print(f"❌ Database initialization failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
