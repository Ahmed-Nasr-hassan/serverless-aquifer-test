"""
Pydantic schemas for Simulation entity.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class SimulationBase(BaseModel):
    """Base schema for Simulation."""
    model_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    simulation_type: str = Field(..., min_length=1, max_length=100)
    status: Optional[str] = "pending"  # pending, running, completed, failed
    simulation_settings: Optional[Dict[str, Any]] = None  # Simulation configuration and parameters (format: {"Human Readable Key": {"value": "Setting Value"}})
    results: Optional[Dict[str, Any]] = None  # Simulation results
    user_id: uuid.UUID


class SimulationCreate(SimulationBase):
    """Schema for creating a Simulation."""
    pass


class SimulationUpdate(BaseModel):
    """Schema for updating a Simulation."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    simulation_type: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = None
    simulation_settings: Optional[Dict[str, Any]] = None  # Simulation configuration and parameters (format: {"Human Readable Key": {"value": "Setting Value"}})
    results: Optional[Dict[str, Any]] = None


class SimulationResponse(SimulationBase):
    """Schema for Simulation response."""
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
