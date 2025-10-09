#!/usr/bin/env python3
"""
Initialize database with test users and data for the new authentication system.
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database import SessionLocal, create_tables
from models import User, Model, Simulation
from auth.utils import get_password_hash

def create_test_users():
    """Create test users."""
    print("👤 Creating test users...")
    
    db = SessionLocal()
    try:
        # Test User 1: Admin
        admin_user = User(
            username="admin",
            email="admin@aquifer.local",
            full_name="Admin User",
            hashed_password=get_password_hash("Admin123"),
            is_active=True,
            is_verified=True
        )
        
        # Test User 2: Regular User
        regular_user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("Test123"),
            is_active=True,
            is_verified=True
        )
        
        # Test User 3: Analyst
        analyst_user = User(
            username="analyst",
            email="analyst@aquifer.local",
            full_name="Analyst User",
            hashed_password=get_password_hash("Analyst123"),
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.add(regular_user)
        db.add(analyst_user)
        db.commit()
        
        # Get the user IDs
        admin_user = db.query(User).filter(User.username == "admin").first()
        regular_user = db.query(User).filter(User.username == "testuser").first()
        analyst_user = db.query(User).filter(User.username == "analyst").first()
        
        print(f"✅ Created users:")
        print(f"   - Admin: {admin_user.username} (ID: {admin_user.id})")
        print(f"   - Test User: {regular_user.username} (ID: {regular_user.id})")
        print(f"   - Analyst: {analyst_user.username} (ID: {analyst_user.id})")
        
        return admin_user, regular_user, analyst_user
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_test_models(users):
    """Create test models for users."""
    print("🔬 Creating test models...")
    
    admin_user, regular_user, analyst_user = users
    db = SessionLocal()
    try:
        # Model for regular user
        aquifer_model = Model(
            name="Aquifer Model Alpha",
            description="Primary aquifer simulation model",
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
                    }
                ],
                "simulationConfig": {
                    "simulationTimeDays": 30,
                    "timeStepDays": 0.1,
                    "runType": "forward"
                }
            },
            status="active",
            user_id=regular_user.id
        )
        
        # Model for analyst user
        well_model = Model(
            name="Well Model Beta",
            description="Well optimization model",
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
            user_id=analyst_user.id
        )
        
        db.add(aquifer_model)
        db.add(well_model)
        db.commit()
        
        print(f"✅ Created models:")
        print(f"   - Aquifer Model Alpha (ID: {aquifer_model.id}) for user {regular_user.username}")
        print(f"   - Well Model Beta (ID: {well_model.id}) for user {analyst_user.username}")
        
        return aquifer_model, well_model
        
    except Exception as e:
        print(f"❌ Error creating models: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_test_simulations(models):
    """Create test simulations."""
    print("⚡ Creating test simulations...")
    
    aquifer_model, well_model = models
    db = SessionLocal()
    try:
        # Get users for simulations
        regular_user = db.query(User).filter(User.username == "testuser").first()
        analyst_user = db.query(User).filter(User.username == "analyst").first()
        
        # Simulation for aquifer model
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
            total_wells_analyzed=1,
            pumping_length_seconds=1800.0,
            total_simulation_time_steps=180,
            user_id=regular_user.id
        )
        
        # Simulation for well model
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
            user_id=analyst_user.id
        )
        
        db.add(forward_simulation)
        db.add(optimization_simulation)
        db.commit()
        
        print(f"✅ Created simulations:")
        print(f"   - Aquifer Forward Run (ID: {forward_simulation.id})")
        print(f"   - Well Optimization Run (ID: {optimization_simulation.id})")
        
    except Exception as e:
        print(f"❌ Error creating simulations: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function."""
    print("🌱 Initializing Database with Authentication System")
    print("=" * 50)
    
    try:
        # Create tables first
        create_tables()
        
        # Create test users
        users = create_test_users()
        
        # Create test models
        models = create_test_models(users)
        
        # Create test simulations
        create_test_simulations(models)
        
        print("")
        print("🎉 Database initialization completed!")
        print("")
        print("📋 Test Users Created:")
        print("   Username: admin, Password: Admin123")
        print("   Username: testuser, Password: Test123")
        print("   Username: analyst, Password: Analyst123")
        print("")
        print("🔗 API Endpoints:")
        print("   POST /api/v1/auth/register - Register new user")
        print("   POST /api/v1/auth/login - Login user")
        print("   GET /api/v1/auth/me - Get current user info")
        print("   PUT /api/v1/auth/me - Update user info")
        print("   POST /api/v1/auth/change-password - Change password")
        print("")
        print("🚀 Ready to test the authentication system!")
        
    except Exception as e:
        print(f"")
        print(f"❌ Database initialization failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
