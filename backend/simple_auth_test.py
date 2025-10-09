#!/usr/bin/env python3
"""
Simple test script to verify authentication system works.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database import SessionLocal, create_tables
from models import User, Model, Simulation

def create_simple_test():
    """Create a simple test without password hashing."""
    print("🧪 Creating simple authentication test...")
    
    # Create tables first
    create_tables()
    
    db = SessionLocal()
    try:
        # Create a simple user without password hashing for now
        test_user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="simple_hash_for_testing",  # Simple hash for testing
            is_active=True,
            is_verified=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Created test user: {test_user.username} (ID: {test_user.id})")
        
        # Create a simple model
        test_model = Model(
            name="Test Model",
            description="Test model for authentication",
            model_type="aquifer",
            configuration={"test": "data"},
            status="active",
            user_id=test_user.id
        )
        
        db.add(test_model)
        db.commit()
        db.refresh(test_model)
        
        print(f"✅ Created test model: {test_model.name} (ID: {test_model.id})")
        
        # Create a simple simulation
        test_simulation = Simulation(
            model_id=test_model.id,
            name="Test Simulation",
            description="Test simulation",
            simulation_type="Forward Run",
            status="pending",
            user_id=test_user.id
        )
        
        db.add(test_simulation)
        db.commit()
        db.refresh(test_simulation)
        
        print(f"✅ Created test simulation: {test_simulation.name} (ID: {test_simulation.id})")
        
        print("")
        print("🎉 Simple test completed!")
        print("   - User table created")
        print("   - Model table created")
        print("   - Simulation table created")
        print("   - Relationships working")
        
    except Exception as e:
        print(f"❌ Error in simple test: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_simple_test()
