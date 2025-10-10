"""
API routes for Model entity with authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.model import Model
from models.user import User
from schemas.model import ModelCreate, ModelUpdate, ModelResponse
from auth.utils import get_current_active_user

models_router = APIRouter()


@models_router.post("/", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(
    model: ModelCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new model."""
    # Build create payload with defaults; user_id from auth
    model_data = model.dict()
    if model_data.get("configuration") is None:
        # Provide minimal default configuration to satisfy DB JSON column
        model_data["configuration"] = {}
    if model_data.get("status") is None:
        model_data["status"] = "active"
    model_data["user_id"] = current_user.id
    
    # Convert configuration to dict if it's a Pydantic model
    if hasattr(model_data["configuration"], 'dict'):
        model_data["configuration"] = model_data["configuration"].dict()
    
    db_model = Model(**model_data)
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@models_router.get("/", response_model=List[ModelResponse])
def get_models(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all models for the current user."""
    models = db.query(Model).filter(Model.user_id == current_user.id).offset(skip).limit(limit).all()
    return models


@models_router.get("/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific model by ID."""
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    return model


@models_router.put("/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: int, 
    model_update: ModelUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a model."""
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    update_data = model_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        # Convert configuration to dict if it's a Pydantic model
        if field == "configuration" and hasattr(value, 'dict'):
            value = value.dict()
        setattr(model, field, value)
    
    db.commit()
    db.refresh(model)
    return model


@models_router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a model."""
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    db.delete(model)
    db.commit()
    return None
