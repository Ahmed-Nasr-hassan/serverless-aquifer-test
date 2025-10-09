"""
AquiferData schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AquiferDataBase(BaseModel):
    """Base schema for aquifer data."""
    soil_material: Optional[str] = Field(None, max_length=100)
    layer_top_level_m: Optional[float] = None
    layer_bottom_level_m: Optional[float] = None
    hydraulic_conductivity_m_per_day: Optional[float] = Field(None, gt=0)
    specific_yield: Optional[float] = Field(None, gt=0, le=1)
    specific_storage: Optional[float] = Field(None, gt=0)


class AquiferDataCreate(AquiferDataBase):
    """Schema for creating aquifer data."""
    simulation_id: int


class AquiferDataUpdate(BaseModel):
    """Schema for updating aquifer data."""
    soil_material: Optional[str] = Field(None, max_length=100)
    layer_top_level_m: Optional[float] = None
    layer_bottom_level_m: Optional[float] = None
    hydraulic_conductivity_m_per_day: Optional[float] = Field(None, gt=0)
    specific_yield: Optional[float] = Field(None, gt=0, le=1)
    specific_storage: Optional[float] = Field(None, gt=0)


class AquiferDataResponse(AquiferDataBase):
    """Schema for aquifer data response."""
    id: int
    simulation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
