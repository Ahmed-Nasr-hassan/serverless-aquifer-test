#!/usr/bin/env python3
"""
Migration script to add simulation_settings column to simulations table.

This script adds the simulation_settings JSON column to the existing simulations table.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from database import engine, SessionLocal
from sqlalchemy import text

def add_simulation_settings_column():
    """Add simulation_settings column to simulations table."""
    print("🔄 Adding simulation_settings column to simulations table...")
    
    db = SessionLocal()
    try:
        # Check if column already exists
        check_column_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'simulations' 
            AND column_name = 'simulation_settings'
        """)
        
        result = db.execute(check_column_query)
        existing_column = result.fetchone()
        
        if existing_column:
            print("✅ simulation_settings column already exists")
            return True
        
        # Add the column
        add_column_query = text("""
            ALTER TABLE simulations 
            ADD COLUMN simulation_settings JSON
        """)
        
        db.execute(add_column_query)
        db.commit()
        
        print("✅ simulation_settings column added successfully")
        
        # Verify the column was added
        verify_query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'simulations' 
            AND column_name = 'simulation_settings'
        """)
        
        result = db.execute(verify_query)
        column_info = result.fetchone()
        
        if column_info:
            print(f"✅ Column verified: {column_info[0]} ({column_info[1]})")
            return True
        else:
            print("❌ Column verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main migration function."""
    print("🚀 Adding simulation_settings column to simulations table")
    print("=" * 50)
    
    try:
        if add_simulation_settings_column():
            print("")
            print("🎉 Migration completed successfully!")
            print("   - simulation_settings column added to simulations table")
            print("   - Column is ready to store JSON simulation configuration data")
        else:
            print("")
            print("❌ Migration failed!")
            return 1
            
    except Exception as e:
        print(f"")
        print(f"❌ Migration failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
