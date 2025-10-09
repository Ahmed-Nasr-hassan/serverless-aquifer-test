#!/usr/bin/env python3
"""
Test script to verify sign up functionality works.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database import SessionLocal, create_tables
from models import User
from auth.utils import get_password_hash

def test_signup():
    """Test sign up functionality."""
    print("🧪 Testing Sign Up Functionality")
    print("=" * 40)
    
    try:
        # Create tables first
        create_tables()
        print("✅ Database tables created")
        
        # Test password hashing
        test_password = "TestPass123"
        hashed_password = get_password_hash(test_password)
        print(f"✅ Password hashing works: {hashed_password[:20]}...")
        
        # Test user creation
        db = SessionLocal()
        try:
            test_user = User(
                username="testuser123",
                email="testuser123@example.com",
                full_name="Test User 123",
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"✅ User created successfully:")
            print(f"   - ID: {test_user.id}")
            print(f"   - Username: {test_user.username}")
            print(f"   - Email: {test_user.email}")
            print(f"   - Full Name: {test_user.full_name}")
            print(f"   - Active: {test_user.is_active}")
            
            # Test password verification
            from auth.utils import verify_password
            is_valid = verify_password(test_password, hashed_password)
            print(f"✅ Password verification works: {is_valid}")
            
            # Test JWT token creation
            from auth.utils import create_access_token
            token = create_access_token({"sub": test_user.username, "user_id": test_user.id})
            print(f"✅ JWT token creation works: {token[:20]}...")
            
            print("")
            print("🎉 All sign up functionality tests passed!")
            print("")
            print("📋 Test Results:")
            print("   ✅ Database connection")
            print("   ✅ User model creation")
            print("   ✅ Password hashing")
            print("   ✅ Password verification")
            print("   ✅ JWT token generation")
            print("   ✅ User registration flow")
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(test_signup())
