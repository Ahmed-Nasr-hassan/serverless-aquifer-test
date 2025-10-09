"""
API routes for Model entity.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.model import Model
from schemas.model import ModelCreate, ModelUpdate, ModelResponse

models_router = APIRouter()


@models_router.post("/", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(model: ModelCreate, db: Session = Depends(get_db)):
    """Create a new model."""
    db_model = Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@models_router.get("/", response_model=List[ModelResponse])
def get_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all models."""
    models = db.query(Model).offset(skip).limit(limit).all()
    return models


@models_router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    """Get a specific model by ID."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    return model


@models_router.put("/{model_id}", response_model=ModelResponse)
def update_model(model_id: int, model_update: ModelUpdate, db: Session = Depends(get_db)):
    """Update a model."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    update_data = model_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    db.commit()
    db.refresh(model)
    return model


@models_router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    """Delete a model."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    db.delete(model)
    db.commit()
    return None
