"""
Local Cognito mock for development environment.
This simulates AWS Cognito behavior locally.
"""

import jwt
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
from passlib.context import CryptContext

# Mock JWT secret (use environment variable in production)
MOCK_JWT_SECRET = "dev-secret-key-change-in-production"
MOCK_JWT_ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@dataclass
class MockUser:
    """Mock user data structure."""
    user_id: str
    email: str
    username: str
    groups: List[str]
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class LocalCognitoMock:
    """Local mock of AWS Cognito for development."""
    
    def __init__(self):
        self.users: Dict[str, MockUser] = {}
        self._create_default_users()
    
    def _create_default_users(self):
        """Create some default users for testing."""
        default_users = [
            MockUser(
                user_id="dev-user-1",
                email="admin@aquifer.local",
                username="admin",
                groups=["admin", "user"]
            ),
            MockUser(
                user_id="dev-user-2", 
                email="user@aquifer.local",
                username="user",
                groups=["user"]
            ),
            MockUser(
                user_id="dev-user-3",
                email="analyst@aquifer.local", 
                username="analyst",
                groups=["analyst", "user"]
            )
        ]
        
        for user in default_users:
            self.users[user.user_id] = user
    
    def authenticate_user(self, username: str, password: str) -> Optional[MockUser]:
        """Authenticate user with username/password."""
        # For mock, accept any password for existing users
        for user in self.users.values():
            if user.username == username or user.email == username:
                return user
        return None
    
    def create_access_token(self, user: MockUser) -> str:
        """Create JWT access token."""
        payload = {
            "sub": user.user_id,
            "email": user.email,
            "username": user.username,
            "groups": user.groups,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24),
            "token_use": "access"
        }
        return jwt.encode(payload, MOCK_JWT_SECRET, algorithm=MOCK_JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, MOCK_JWT_SECRET, algorithms=[MOCK_JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[MockUser]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def create_user(self, email: str, username: str, groups: List[str] = None) -> MockUser:
        """Create a new user."""
        if groups is None:
            groups = ["user"]
        
        user_id = f"dev-user-{len(self.users) + 1}"
        user = MockUser(
            user_id=user_id,
            email=email,
            username=username,
            groups=groups
        )
        self.users[user_id] = user
        return user

# Global mock instance
cognito_mock = LocalCognitoMock()

# Helper functions for FastAPI integration
def authenticate_user(username: str, password: str) -> Optional[str]:
    """Authenticate user and return JWT token."""
    user = cognito_mock.authenticate_user(username, password)
    if user:
        return cognito_mock.create_access_token(user)
    return None

def verify_access_token(token: str) -> Optional[Dict]:
    """Verify access token and return payload."""
    return cognito_mock.verify_token(token)

def get_current_user(token: str) -> Optional[MockUser]:
    """Get current user from token."""
    payload = verify_access_token(token)
    if payload:
        return cognito_mock.get_user_by_id(payload["sub"])
    return None
