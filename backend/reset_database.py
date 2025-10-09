#!/usr/bin/env python3
"""
Reset database to new 2-entity architecture.
This script drops all tables and recreates them with the new structure.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database import engine, SessionLocal
from sqlalchemy import text

def reset_database():
    """Reset the database to the new architecture."""
    print("🔄 Resetting database to new 2-entity architecture...")
    
    db = SessionLocal()
    try:
        # Drop all existing tables
        print("   Dropping existing tables...")
        
        # Get all table names
        tables_result = db.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
        """))
        
        tables = [row[0] for row in tables_result.fetchall()]
        print(f"   Found {len(tables)} tables to drop: {tables}")
        
        # Drop tables in reverse dependency order
        for table in reversed(tables):
            try:
                db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"   Dropped table: {table}")
            except Exception as e:
                print(f"   Warning: Could not drop table {table}: {e}")
        
        db.commit()
        print("✅ All tables dropped")
        
        # Create new tables
        print("   Creating new tables...")
        from models import Model, Simulation
        from database import create_tables
        
        create_tables()
        print("✅ New tables created")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function."""
    print("🔄 Database Reset: Old Architecture → New 2-Entity Architecture")
    print("=" * 60)
    
    try:
        reset_database()
        print("")
        print("🎉 Database reset completed!")
        print("   - All old tables have been dropped")
        print("   - New 2-entity tables have been created")
        print("   - Ready for new architecture")
        
    except Exception as e:
        print(f"")
        print(f"❌ Database reset failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
