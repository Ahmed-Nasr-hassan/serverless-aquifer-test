"""
Authentication middleware and dependencies for FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from .local_cognito import get_current_user, verify_access_token, MockUser

# Security scheme
security = HTTPBearer()

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract token from Authorization header."""
    return credentials.credentials

def get_current_user_dependency(token: str = Depends(get_token)) -> MockUser:
    """Dependency to get current authenticated user."""
    user = get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_groups(required_groups: List[str]):
    """Decorator to require specific user groups."""
    def group_checker(current_user: MockUser = Depends(get_current_user_dependency)) -> MockUser:
        user_groups = set(current_user.groups)
        required_groups_set = set(required_groups)
        
        if not user_groups.intersection(required_groups_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required groups: {required_groups}"
            )
        return current_user
    return group_checker

# Common role dependencies
require_admin = require_groups(["admin"])
require_analyst = require_groups(["analyst", "admin"])
require_user = require_groups(["user", "analyst", "admin"])

# Optional authentication (doesn't fail if no token)
def get_current_user_optional(token: Optional[str] = Depends(get_token)) -> Optional[MockUser]:
    """Optional authentication - returns None if no valid token."""
    if not token:
        return None
    return get_current_user(token)
