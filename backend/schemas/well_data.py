"""
WellData schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class WellDataBase(BaseModel):
    """Base schema for well data."""
    well_id: str = Field(..., min_length=1, max_length=100)
    well_type: str = Field(..., min_length=1, max_length=50)
    well_configuration: Dict[str, Any] = Field(..., description="Complete well configuration data")
    simulation_results: Optional[Dict[str, Any]] = Field(None, description="All simulation results data")
    analysis_results: Optional[Dict[str, Any]] = Field(None, description="Analysis and comparison results")
    description: Optional[str] = Field(None, max_length=500)


class WellDataCreate(WellDataBase):
    """Schema for creating well data."""
    simulation_id: int


class WellDataUpdate(BaseModel):
    """Schema for updating well data."""
    well_id: Optional[str] = Field(None, min_length=1, max_length=100)
    well_type: Optional[str] = Field(None, min_length=1, max_length=50)
    well_configuration: Optional[Dict[str, Any]] = None
    simulation_results: Optional[Dict[str, Any]] = None
    analysis_results: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=500)


class WellDataResponse(WellDataBase):
    """Schema for well data response."""
    id: int
    simulation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
