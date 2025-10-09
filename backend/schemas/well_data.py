"""
WellData schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WellDataBase(BaseModel):
    """Base schema for well data."""
    well_id: str = Field(..., min_length=1, max_length=100)
    well_type: str = Field(..., min_length=1, max_length=50)
    distance_from_pumping_well_meters: Optional[List[float]] = None
    well_radius_meters: Optional[float] = Field(None, gt=0)
    screen_top_meters: Optional[float] = None
    screen_bottom_meters: Optional[float] = None
    simulated_drawdown_meters: Optional[List[float]] = None
    observed_drawdown_meters: Optional[List[float]] = None
    observed_time_seconds: Optional[List[float]] = None
    avg_head_at_distance_meters: Optional[List[float]] = None
    interpolated_times: Optional[List[float]] = None
    interpolated_observed_drawdown: Optional[List[float]] = None
    interpolated_simulated_drawdown: Optional[List[float]] = None
    rmse: Optional[float] = Field(None, ge=0)
    total_residual_error: Optional[float] = Field(None, ge=0)


class WellDataCreate(WellDataBase):
    """Schema for creating well data."""
    simulation_id: int


class WellDataUpdate(BaseModel):
    """Schema for updating well data."""
    well_id: Optional[str] = Field(None, min_length=1, max_length=100)
    well_type: Optional[str] = Field(None, min_length=1, max_length=50)
    distance_from_pumping_well_meters: Optional[List[float]] = None
    well_radius_meters: Optional[float] = Field(None, gt=0)
    screen_top_meters: Optional[float] = None
    screen_bottom_meters: Optional[float] = None
    simulated_drawdown_meters: Optional[List[float]] = None
    observed_drawdown_meters: Optional[List[float]] = None
    observed_time_seconds: Optional[List[float]] = None
    avg_head_at_distance_meters: Optional[List[float]] = None
    interpolated_times: Optional[List[float]] = None
    interpolated_observed_drawdown: Optional[List[float]] = None
    interpolated_simulated_drawdown: Optional[List[float]] = None
    rmse: Optional[float] = Field(None, ge=0)
    total_residual_error: Optional[float] = Field(None, ge=0)


class WellDataResponse(WellDataBase):
    """Schema for well data response."""
    id: int
    simulation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
