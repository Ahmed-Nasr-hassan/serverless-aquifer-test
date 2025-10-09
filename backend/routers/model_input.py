"""
Model input router endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import ModelInput
from schemas import ModelInputCreate, ModelInputUpdate, ModelInputResponse, MessageResponse

model_input_router = APIRouter()


@model_input_router.post("/", response_model=ModelInputResponse, status_code=status.HTTP_201_CREATED)
async def create_model_input(model_input: ModelInputCreate, db: Session = Depends(get_db)):
    """Create new model input data."""
    db_input = ModelInput(**model_input.dict())
    db.add(db_input)
    db.commit()
    db.refresh(db_input)
    return db_input


@model_input_router.get("/", response_model=List[ModelInputResponse])
async def get_model_inputs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all model inputs with pagination."""
    inputs = db.query(ModelInput).offset(skip).limit(limit).all()
    return inputs


@model_input_router.get("/simulation/{simulation_id}", response_model=List[ModelInputResponse])
async def get_model_inputs_by_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Get model inputs for a specific simulation."""
    inputs = db.query(ModelInput).filter(ModelInput.simulation_id == simulation_id).all()
    return inputs


@model_input_router.get("/{input_id}", response_model=ModelInputResponse)
async def get_model_input_by_id(input_id: int, db: Session = Depends(get_db)):
    """Get specific model input by ID."""
    model_input = db.query(ModelInput).filter(ModelInput.id == input_id).first()
    if not model_input:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model input not found"
        )
    return model_input


@model_input_router.put("/{input_id}", response_model=ModelInputResponse)
async def update_model_input(
    input_id: int, 
    input_update: ModelInputUpdate, 
    db: Session = Depends(get_db)
):
    """Update model input data."""
    model_input = db.query(ModelInput).filter(ModelInput.id == input_id).first()
    if not model_input:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model input not found"
        )
    
    update_data = input_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model_input, field, value)
    
    db.commit()
    db.refresh(model_input)
    return model_input


@model_input_router.delete("/{input_id}", response_model=MessageResponse)
async def delete_model_input(input_id: int, db: Session = Depends(get_db)):
    """Delete model input data."""
    model_input = db.query(ModelInput).filter(ModelInput.id == input_id).first()
    if not model_input:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model input not found"
        )
    
    db.delete(model_input)
    db.commit()
    return MessageResponse(message="Model input deleted successfully")
