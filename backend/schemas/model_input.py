"""
ModelInput schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ModelInputBase(BaseModel):
    """Base schema for model input data."""
    run_type: str = Field(..., min_length=1, max_length=100)
    model_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    ztop: Optional[float] = None
    zbot: Optional[float] = None
    col_length: Optional[float] = Field(None, gt=0)
    radius_well: Optional[float] = Field(None, gt=0)
    cell_size: Optional[float] = Field(None, gt=0)
    horizontal_multiplier: Optional[float] = Field(None, gt=0)
    sc_top: Optional[float] = None
    sc_bottom: Optional[float] = None
    sc_top_thick: Optional[float] = Field(None, gt=0)
    sc_bottom_thick: Optional[float] = Field(None, gt=0)
    refine_above_screen: Optional[bool] = None
    refine_below_screen: Optional[bool] = None
    refine_between_screen: Optional[bool] = None
    pumping_rate_m3_per_day: Optional[float] = None
    pumping_start_time_seconds: Optional[float] = Field(None, ge=0)
    pumping_end_time_seconds: Optional[float] = Field(None, ge=0)
    simulation_start_time_seconds: Optional[float] = Field(None, ge=0)
    simulation_end_time_seconds: Optional[float] = Field(None, ge=0)
    time_step_size_seconds: Optional[float] = Field(None, gt=0)
    specific_yield: Optional[float] = Field(None, gt=0, le=1)
    specific_storage: Optional[float] = Field(None, gt=0)
    raw_input_data: Optional[Dict[str, Any]] = None


class ModelInputCreate(ModelInputBase):
    """Schema for creating model input data."""
    simulation_id: int


class ModelInputUpdate(BaseModel):
    """Schema for updating model input data."""
    run_type: Optional[str] = Field(None, min_length=1, max_length=100)
    model_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    ztop: Optional[float] = None
    zbot: Optional[float] = None
    col_length: Optional[float] = Field(None, gt=0)
    radius_well: Optional[float] = Field(None, gt=0)
    cell_size: Optional[float] = Field(None, gt=0)
    horizontal_multiplier: Optional[float] = Field(None, gt=0)
    sc_top: Optional[float] = None
    sc_bottom: Optional[float] = None
    sc_top_thick: Optional[float] = Field(None, gt=0)
    sc_bottom_thick: Optional[float] = Field(None, gt=0)
    refine_above_screen: Optional[bool] = None
    refine_below_screen: Optional[bool] = None
    refine_between_screen: Optional[bool] = None
    pumping_rate_m3_per_day: Optional[float] = None
    pumping_start_time_seconds: Optional[float] = Field(None, ge=0)
    pumping_end_time_seconds: Optional[float] = Field(None, ge=0)
    simulation_start_time_seconds: Optional[float] = Field(None, ge=0)
    simulation_end_time_seconds: Optional[float] = Field(None, ge=0)
    time_step_size_seconds: Optional[float] = Field(None, gt=0)
    specific_yield: Optional[float] = Field(None, gt=0, le=1)
    specific_storage: Optional[float] = Field(None, gt=0)
    raw_input_data: Optional[Dict[str, Any]] = None


class ModelInputResponse(ModelInputBase):
    """Schema for model input response."""
    id: int
    simulation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
