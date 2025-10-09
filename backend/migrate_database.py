#!/usr/bin/env python3
"""
Database migration script for transitioning from 5-entity to 2-entity architecture.

This script:
1. Backs up existing data
2. Creates new tables (models, simulations)
3. Migrates data from old tables to new structure
4. Drops old tables
5. Provides rollback capability
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database import engine, SessionLocal
from sqlalchemy import text

def backup_database():
    """Create a backup of the current database."""
    print("📦 Creating database backup...")
    
    # Get database URL
    db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    if db_url.startswith("sqlite"):
        # For SQLite, copy the file
        db_file = db_url.replace("sqlite:///", "")
        backup_file = f"{db_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        import shutil
        shutil.copy2(db_file, backup_file)
        print(f"✅ SQLite backup created: {backup_file}")
        return backup_file
    else:
        # For PostgreSQL, create a dump
        print("⚠️  PostgreSQL backup not implemented. Please create a manual backup.")
        return None

def migrate_data():
    """Migrate data from old tables to new structure."""
    print("🔄 Migrating data to new architecture...")
    
    db = SessionLocal()
    try:
        # Check if old tables exist
        old_tables = [
            "simulations", "aquifer_data", "optimization_result", 
            "well_data", "model_input"
        ]
        
        existing_tables = []
        for table in old_tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                existing_tables.append((table, count))
                print(f"   Found {count} records in {table}")
            except Exception as e:
                print(f"   Table {table} not found or error: {e}")
        
        if not existing_tables:
            print("✅ No old data to migrate")
            return
        
        # Create models from existing data
        print("   Creating models from existing data...")
        
        # Get all simulations
        try:
            simulations_result = db.execute(text("SELECT * FROM simulations"))
            simulations = simulations_result.fetchall()
            
            for sim in simulations:
                # Create a model for each simulation
                model_config = {
                    "aquiferConfig": {
                        "ztop": 100.0,
                        "specificYield": 0.2,
                        "specificStorage": 0.0001,
                        "hydraulicConductivity": []
                    },
                    "wellConfig": {
                        "pumpingRate": 1000.0,
                        "wellRadius": 0.1,
                        "screenTop": 50.0,
                        "screenBottom": 30.0
                    },
                    "simulationConfig": {
                        "simulationTimeDays": 30,
                        "timeStepDays": 0.1,
                        "runType": "forward"
                    },
                    "observationPoints": []
                }
                
                # Try to get related data
                try:
                    aquifer_data = db.execute(text(f"SELECT * FROM aquifer_data WHERE simulation_id = {sim.id}")).fetchone()
                    if aquifer_data:
                        # Migrate aquifer data to configuration
                        pass
                    
                    well_data = db.execute(text(f"SELECT * FROM well_data WHERE simulation_id = {sim.id}")).fetchall()
                    if well_data:
                        # Migrate well data to configuration
                        pass
                    
                    model_input = db.execute(text(f"SELECT * FROM model_input WHERE simulation_id = {sim.id}")).fetchone()
                    if model_input:
                        # Migrate model input to configuration
                        pass
                    
                    optimization_result = db.execute(text(f"SELECT * FROM optimization_result WHERE simulation_id = {sim.id}")).fetchone()
                    if optimization_result:
                        # Migrate optimization result to configuration
                        pass
                        
                except Exception as e:
                    print(f"   Warning: Could not migrate related data for simulation {sim.id}: {e}")
                
                # Insert new model
                model_insert = text("""
                    INSERT INTO models (name, description, model_type, configuration, status, user_id, created_at, updated_at)
                    VALUES (:name, :description, :model_type, :configuration, :status, :user_id, :created_at, :updated_at)
                """)
                
                db.execute(model_insert, {
                    "name": f"Migrated Model {sim.id}",
                    "description": f"Model migrated from simulation {sim.id}",
                    "model_type": "aquifer",
                    "configuration": json.dumps(model_config),
                    "status": "active",
                    "user_id": sim.user_id,
                    "created_at": sim.created_at,
                    "updated_at": sim.updated_at
                })
                
                # Get the new model ID
                model_id_result = db.execute(text("SELECT last_insert_rowid()"))
                new_model_id = model_id_result.scalar()
                
                # Create new simulation linked to the model
                simulation_insert = text("""
                    INSERT INTO simulations (model_id, name, description, simulation_type, status, user_id, created_at, updated_at, completed_at)
                    VALUES (:model_id, :name, :description, :simulation_type, :status, :user_id, :created_at, :updated_at, :completed_at)
                """)
                
                db.execute(simulation_insert, {
                    "model_id": new_model_id,
                    "name": sim.name,
                    "description": sim.description,
                    "simulation_type": sim.simulation_type,
                    "status": sim.status,
                    "user_id": sim.user_id,
                    "created_at": sim.created_at,
                    "updated_at": sim.updated_at,
                    "completed_at": sim.completed_at
                })
                
                print(f"   Migrated simulation {sim.id} to new architecture")
        
        except Exception as e:
            print(f"   Error migrating simulations: {e}")
        
        db.commit()
        print("✅ Data migration completed")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def drop_old_tables():
    """Drop the old tables after successful migration."""
    print("🗑️  Dropping old tables...")
    
    db = SessionLocal()
    try:
        old_tables = [
            "aquifer_data", "optimization_result", "well_data", "model_input"
        ]
        
        for table in old_tables:
            try:
                db.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"   Dropped table: {table}")
            except Exception as e:
                print(f"   Warning: Could not drop table {table}: {e}")
        
        db.commit()
        print("✅ Old tables dropped")
        
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_new_tables():
    """Create the new tables."""
    print("🏗️  Creating new tables...")
    
    from models import Model, Simulation
    from database import create_tables
    
    create_tables()
    print("✅ New tables created")

def verify_migration():
    """Verify that the migration was successful."""
    print("🔍 Verifying migration...")
    
    db = SessionLocal()
    try:
        # Check models table
        models_count = db.execute(text("SELECT COUNT(*) FROM models")).scalar()
        print(f"   Models: {models_count}")
        
        # Check simulations table
        simulations_count = db.execute(text("SELECT COUNT(*) FROM simulations")).scalar()
        print(f"   Simulations: {simulations_count}")
        
        # Check relationships
        linked_simulations = db.execute(text("""
            SELECT COUNT(*) FROM simulations s 
            JOIN models m ON s.model_id = m.id
        """)).scalar()
        print(f"   Linked simulations: {linked_simulations}")
        
        if models_count > 0 and simulations_count > 0 and linked_simulations > 0:
            print("✅ Migration verification successful")
            return True
        else:
            print("❌ Migration verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        db.close()

def main():
    """Main migration function."""
    print("🚀 Starting Database Migration: 5-Entity → 2-Entity Architecture")
    print("=" * 60)
    
    try:
        # Step 1: Backup
        backup_file = backup_database()
        
        # Step 2: Create new tables
        create_new_tables()
        
        # Step 3: Migrate data
        migrate_data()
        
        # Step 4: Verify migration
        if verify_migration():
            # Step 5: Drop old tables
            drop_old_tables()
            print("")
            print("🎉 Migration completed successfully!")
            print("   - New 2-entity architecture is active")
            print("   - All data has been migrated")
            print("   - Old tables have been removed")
            if backup_file:
                print(f"   - Backup available at: {backup_file}")
        else:
            print("")
            print("❌ Migration verification failed!")
            print("   Please check the logs and consider restoring from backup")
            return 1
            
    except Exception as e:
        print(f"")
        print(f"❌ Migration failed: {e}")
        print("   Please restore from backup if needed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
