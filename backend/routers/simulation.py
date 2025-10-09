"""
API routes for Simulation entity.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.simulation import Simulation
from models.model import Model
from schemas.simulation import SimulationCreate, SimulationUpdate, SimulationResponse

simulation_router = APIRouter()


@simulation_router.post("/", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation(simulation: SimulationCreate, db: Session = Depends(get_db)):
    """Create a new simulation."""
    # Verify that the model exists
    model = db.query(Model).filter(Model.id == simulation.model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
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


@simulation_router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    return None


@simulation_router.get("/model/{model_id}", response_model=List[SimulationResponse])
async def get_simulations_by_model(model_id: int, db: Session = Depends(get_db)):
    """Get all simulations for a specific model."""
    # Verify that the model exists
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    simulations = db.query(Simulation).filter(Simulation.model_id == model_id).all()
    return simulations
