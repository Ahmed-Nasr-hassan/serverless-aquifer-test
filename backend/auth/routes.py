"""
Authentication endpoints for local development.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .local_cognito import authenticate_user, cognito_mock
from . import get_current_user_dependency, MockUser

auth_router = APIRouter()

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    username: str
    groups: List[str]

class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    groups: List[str]
    is_active: bool

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    groups: Optional[List[str]] = ["user"]

@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint for local development."""
    token = authenticate_user(request.username, request.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Get user info
    user = get_current_user_dependency(token)
    
    return LoginResponse(
        access_token=token,
        user_id=user.user_id,
        email=user.email,
        username=user.username,
        groups=user.groups
    )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: MockUser = Depends(get_current_user_dependency)):
    """Get current user information."""
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        username=current_user.username,
        groups=current_user.groups,
        is_active=current_user.is_active
    )

@auth_router.post("/users", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    current_user: MockUser = Depends(get_current_user_dependency)
):
    """Create a new user (admin only)."""
    # Check if user is admin
    if "admin" not in current_user.groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if username/email already exists
    for user in cognito_mock.users.values():
        if user.username == request.username or user.email == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
    
    # Create new user
    new_user = cognito_mock.create_user(
        email=request.email,
        username=request.username,
        groups=request.groups
    )
    
    return UserResponse(
        user_id=new_user.user_id,
        email=new_user.email,
        username=new_user.username,
        groups=new_user.groups,
        is_active=new_user.is_active
    )

@auth_router.get("/users", response_model=List[UserResponse])
async def list_users(current_user: MockUser = Depends(get_current_user_dependency)):
    """List all users (admin only)."""
    if "admin" not in current_user.groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = []
    for user in cognito_mock.users.values():
        users.append(UserResponse(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            groups=user.groups,
            is_active=user.is_active
        ))
    
    return users

@auth_router.get("/dev-users")
async def get_dev_users():
    """Get development users for testing (no auth required)."""
    return {
        "message": "Development users for testing",
        "users": [
            {"username": "admin", "email": "admin@aquifer.local", "password": "any"},
            {"username": "user", "email": "user@aquifer.local", "password": "any"},
            {"username": "analyst", "email": "analyst@aquifer.local", "password": "any"}
        ]
    }
