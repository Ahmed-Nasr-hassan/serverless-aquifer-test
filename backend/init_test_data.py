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
            results={
                "drawdownData": [
                    {"time": 0, "drawdown": 0},
                    {"time": 5, "drawdown": 0.5},
                    {"time": 10, "drawdown": 1.0},
                    {"time": 15, "drawdown": 1.4},
                    {"time": 20, "drawdown": 1.8}
                ],
                "analysisResults": {
                    "rmse": 0.15,
                    "totalError": 2.3,
                    "radiusOfInfluence": 150.5,
                    "convergenceAchieved": True
                },
                "performanceMetrics": {
                    "simulationTime": 45.2,
                    "memoryUsage": "128MB",
                    "cpuUsage": "15%"
                }
            },
            radius_of_influence_meters=150.5,
            total_wells_analyzed=2,
            pumping_length_seconds=1800.0,
            total_simulation_time_steps=180,
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
            results={
                "optimizationResults": {
                    "optimalParameters": {
                        "hydraulicConductivity": 8.5,
                        "specificYield": 0.18
                    },
                    "convergenceAchieved": True,
                    "iterationsCompleted": 15,
                    "finalRMSE": 0.12,
                    "parameterHistory": [
                        {"iteration": 1, "hydraulicConductivity": 5.0, "specificYield": 0.2, "rmse": 0.25},
                        {"iteration": 5, "hydraulicConductivity": 7.2, "specificYield": 0.19, "rmse": 0.18},
                        {"iteration": 10, "hydraulicConductivity": 8.1, "specificYield": 0.18, "rmse": 0.14},
                        {"iteration": 15, "hydraulicConductivity": 8.5, "specificYield": 0.18, "rmse": 0.12}
                    ]
                },
                "analysisResults": {
                    "parameterSensitivity": {
                        "hydraulicConductivity": 0.85,
                        "specificYield": 0.65
                    },
                    "confidenceIntervals": {
                        "hydraulicConductivity": {"lower": 7.8, "upper": 9.2},
                        "specificYield": {"lower": 0.16, "upper": 0.20}
                    }
                }
            },
            radius_of_influence_meters=120.3,
            total_wells_analyzed=1,
            pumping_length_seconds=900.0,
            total_simulation_time_steps=90,
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
