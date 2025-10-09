"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Base schemas
class SimulationBase(BaseModel):
    """Base schema for simulation data."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    aquifer_thickness: Optional[float] = Field(None, gt=0)
    hydraulic_conductivity: Optional[float] = Field(None, gt=0)
    porosity: Optional[float] = Field(None, gt=0, le=1)
    pumping_rate: Optional[float] = None


class SimulationCreate(SimulationBase):
    """Schema for creating a new simulation."""
    pass


class SimulationUpdate(BaseModel):
    """Schema for updating a simulation."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    aquifer_thickness: Optional[float] = Field(None, gt=0)
    hydraulic_conductivity: Optional[float] = Field(None, gt=0)
    porosity: Optional[float] = Field(None, gt=0, le=1)
    pumping_rate: Optional[float] = None


class SimulationResponse(SimulationBase):
    """Schema for simulation response."""
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    drawdown_data: Optional[str] = None
    simulation_results: Optional[str] = None

    class Config:
        from_attributes = True


# Aquifer Data schemas
class AquiferDataBase(BaseModel):
    """Base schema for aquifer data."""
    location_name: str = Field(..., min_length=1, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    depth: Optional[float] = Field(None, gt=0)
    hydraulic_conductivity: Optional[float] = Field(None, gt=0)
    porosity: Optional[float] = Field(None, gt=0, le=1)
    water_level: Optional[float] = None
    measurement_date: Optional[datetime] = None
    notes: Optional[str] = None


class AquiferDataCreate(AquiferDataBase):
    """Schema for creating aquifer data."""
    pass


class AquiferDataUpdate(BaseModel):
    """Schema for updating aquifer data."""
    location_name: Optional[str] = Field(None, min_length=1, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    depth: Optional[float] = Field(None, gt=0)
    hydraulic_conductivity: Optional[float] = Field(None, gt=0)
    porosity: Optional[float] = Field(None, gt=0, le=1)
    water_level: Optional[float] = None
    measurement_date: Optional[datetime] = None
    notes: Optional[str] = None


class AquiferDataResponse(AquiferDataBase):
    """Schema for aquifer data response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Optimization schemas
class OptimizationResultBase(BaseModel):
    """Base schema for optimization results."""
    simulation_id: int
    objective_function_value: Optional[float] = None
    optimized_parameters: Optional[str] = None
    convergence_status: Optional[str] = None
    iterations: Optional[int] = Field(None, ge=0)


class OptimizationResultCreate(OptimizationResultBase):
    """Schema for creating optimization results."""
    pass


class OptimizationResultResponse(OptimizationResultBase):
    """Schema for optimization result response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Generic response schemas
class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    success: bool = False
