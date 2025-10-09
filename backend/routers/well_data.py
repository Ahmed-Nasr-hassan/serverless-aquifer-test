"""
Well data router endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import WellData
from schemas import WellDataCreate, WellDataUpdate, WellDataResponse, MessageResponse

well_router = APIRouter()


@well_router.post("/", response_model=WellDataResponse, status_code=status.HTTP_201_CREATED)
async def create_well_data(well_data: WellDataCreate, db: Session = Depends(get_db)):
    """Create new well data."""
    db_well = WellData(**well_data.dict())
    db.add(db_well)
    db.commit()
    db.refresh(db_well)
    return db_well


@well_router.get("/", response_model=List[WellDataResponse])
async def get_well_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all well data with pagination."""
    wells = db.query(WellData).offset(skip).limit(limit).all()
    return wells


@well_router.get("/simulation/{simulation_id}", response_model=List[WellDataResponse])
async def get_well_data_by_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Get well data for a specific simulation."""
    wells = db.query(WellData).filter(WellData.simulation_id == simulation_id).all()
    return wells


@well_router.get("/{well_id}", response_model=WellDataResponse)
async def get_well_data_by_id(well_id: int, db: Session = Depends(get_db)):
    """Get specific well data by ID."""
    well = db.query(WellData).filter(WellData.id == well_id).first()
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Well data not found"
        )
    return well


@well_router.put("/{well_id}", response_model=WellDataResponse)
async def update_well_data(
    well_id: int, 
    well_update: WellDataUpdate, 
    db: Session = Depends(get_db)
):
    """Update well data."""
    well = db.query(WellData).filter(WellData.id == well_id).first()
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Well data not found"
        )
    
    update_data = well_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(well, field, value)
    
    db.commit()
    db.refresh(well)
    return well


@well_router.delete("/{well_id}", response_model=MessageResponse)
async def delete_well_data(well_id: int, db: Session = Depends(get_db)):
    """Delete well data."""
    well = db.query(WellData).filter(WellData.id == well_id).first()
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Well data not found"
        )
    
    db.delete(well)
    db.commit()
    return MessageResponse(message="Well data deleted successfully")
