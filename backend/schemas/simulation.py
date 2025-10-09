"""
Pydantic schemas for Simulation entity.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SimulationBase(BaseModel):
    """Base schema for Simulation."""
    model_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    simulation_type: str = Field(..., min_length=1, max_length=100)
    status: Optional[str] = "pending"  # pending, running, completed, failed
    results: Optional[Dict[str, Any]] = None  # Simulation results
    user_id: str = Field(..., min_length=1, max_length=255)


class SimulationCreate(SimulationBase):
    """Schema for creating a Simulation."""
    pass


class SimulationUpdate(BaseModel):
    """Schema for updating a Simulation."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    simulation_type: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    radius_of_influence_meters: Optional[float] = Field(None, gt=0)
    total_wells_analyzed: Optional[int] = Field(None, ge=0)
    pumping_length_seconds: Optional[float] = Field(None, gt=0)
    total_simulation_time_steps: Optional[int] = Field(None, ge=0)


class SimulationResponse(SimulationBase):
    """Schema for Simulation response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    radius_of_influence_meters: Optional[float] = None
    total_wells_analyzed: Optional[int] = None
    pumping_length_seconds: Optional[float] = None
    total_simulation_time_steps: Optional[int] = None
    
    class Config:
        from_attributes = True
