"""
Aquifer data router endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import AquiferData
from schemas import AquiferDataCreate, AquiferDataUpdate, AquiferDataResponse, MessageResponse

data_router = APIRouter()


@data_router.post("/", response_model=AquiferDataResponse, status_code=status.HTTP_201_CREATED)
async def create_aquifer_data(data: AquiferDataCreate, db: Session = Depends(get_db)):
    """Create new aquifer data."""
    db_data = AquiferData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


@data_router.get("/", response_model=List[AquiferDataResponse])
async def get_aquifer_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all aquifer data with pagination."""
    data = db.query(AquiferData).offset(skip).limit(limit).all()
    return data


@data_router.get("/simulation/{simulation_id}", response_model=List[AquiferDataResponse])
async def get_aquifer_data_by_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Get aquifer data for a specific simulation."""
    data = db.query(AquiferData).filter(AquiferData.simulation_id == simulation_id).all()
    return data


@data_router.get("/{data_id}", response_model=AquiferDataResponse)
async def get_aquifer_data_by_id(data_id: int, db: Session = Depends(get_db)):
    """Get specific aquifer data by ID."""
    data = db.query(AquiferData).filter(AquiferData.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aquifer data not found"
        )
    return data


@data_router.put("/{data_id}", response_model=AquiferDataResponse)
async def update_aquifer_data(
    data_id: int, 
    data_update: AquiferDataUpdate, 
    db: Session = Depends(get_db)
):
    """Update aquifer data."""
    data = db.query(AquiferData).filter(AquiferData.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aquifer data not found"
        )
    
    update_data = data_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(data, field, value)
    
    db.commit()
    db.refresh(data)
    return data


@data_router.delete("/{data_id}", response_model=MessageResponse)
async def delete_aquifer_data(data_id: int, db: Session = Depends(get_db)):
    """Delete aquifer data."""
    data = db.query(AquiferData).filter(AquiferData.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aquifer data not found"
        )
    
    db.delete(data)
    db.commit()
    return MessageResponse(message="Aquifer data deleted successfully")
