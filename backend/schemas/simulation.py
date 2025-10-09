"""
Simulation schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SimulationBase(BaseModel):
    """Base schema for simulation data."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    simulation_type: str = Field(..., min_length=1, max_length=100)
    user_id: str = Field(..., min_length=1, max_length=255)


class SimulationCreate(SimulationBase):
    """Schema for creating a new simulation."""
    input_file_path: Optional[str] = None


class SimulationUpdate(BaseModel):
    """Schema for updating a simulation."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    simulation_type: Optional[str] = Field(None, min_length=1, max_length=100)
    radius_of_influence_meters: Optional[float] = Field(None, gt=0)
    total_wells_analyzed: Optional[int] = Field(None, ge=0)
    pumping_length_seconds: Optional[float] = Field(None, gt=0)
    total_simulation_time_steps: Optional[int] = Field(None, ge=0)
    results_file_path: Optional[str] = None


class SimulationResponse(SimulationBase):
    """Schema for simulation response."""
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    radius_of_influence_meters: Optional[float] = None
    total_wells_analyzed: Optional[int] = None
    pumping_length_seconds: Optional[float] = None
    total_simulation_time_steps: Optional[int] = None
    input_file_path: Optional[str] = None
    results_file_path: Optional[str] = None

    class Config:
        from_attributes = True
