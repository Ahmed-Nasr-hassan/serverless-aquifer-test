"""
API routers for the FastAPI application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Simulation, AquiferData, OptimizationResult
from schemas import (
    SimulationCreate, SimulationUpdate, SimulationResponse,
    AquiferDataCreate, AquiferDataUpdate, AquiferDataResponse,
    OptimizationResultCreate, OptimizationResultResponse,
    MessageResponse
)

# Create router instances
simulation_router = APIRouter()
data_router = APIRouter()
optimization_router = APIRouter()


# Simulation endpoints
@simulation_router.post("/", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation(simulation: SimulationCreate, db: Session = Depends(get_db)):
    """Create a new simulation."""
    db_simulation = Simulation(**simulation.dict())
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation


@simulation_router.get("/", response_model=List[SimulationResponse])
async def get_simulations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all simulations with pagination."""
    simulations = db.query(Simulation).offset(skip).limit(limit).all()
    return simulations


@simulation_router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Get a specific simulation by ID."""
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    return simulation


@simulation_router.put("/{simulation_id}", response_model=SimulationResponse)
async def update_simulation(
    simulation_id: int, 
    simulation_update: SimulationUpdate, 
    db: Session = Depends(get_db)
):
    """Update a simulation."""
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    update_data = simulation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(simulation, field, value)
    
    db.commit()
    db.refresh(simulation)
    return simulation


@simulation_router.delete("/{simulation_id}", response_model=MessageResponse)
async def delete_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Delete a simulation."""
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    db.delete(simulation)
    db.commit()
    return MessageResponse(message="Simulation deleted successfully")


# Aquifer Data endpoints
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


# Optimization endpoints
@optimization_router.post("/", response_model=OptimizationResultResponse, status_code=status.HTTP_201_CREATED)
async def create_optimization_result(result: OptimizationResultCreate, db: Session = Depends(get_db)):
    """Create new optimization result."""
    db_result = OptimizationResult(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


@optimization_router.get("/", response_model=List[OptimizationResultResponse])
async def get_optimization_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all optimization results with pagination."""
    results = db.query(OptimizationResult).offset(skip).limit(limit).all()
    return results


@optimization_router.get("/simulation/{simulation_id}", response_model=List[OptimizationResultResponse])
async def get_optimization_results_by_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Get optimization results for a specific simulation."""
    results = db.query(OptimizationResult).filter(
        OptimizationResult.simulation_id == simulation_id
    ).all()
    return results
