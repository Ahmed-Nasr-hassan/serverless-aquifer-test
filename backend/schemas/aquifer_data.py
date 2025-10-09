"""
AquiferData schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AquiferDataBase(BaseModel):
    """Base schema for aquifer data."""
    hydraulic_conductivity_layers: List[Dict[str, Any]] = Field(..., description="Array of hydraulic conductivity layer data")
    specific_yield: Optional[float] = Field(None, gt=0, le=1)
    specific_storage: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)


class AquiferDataCreate(AquiferDataBase):
    """Schema for creating aquifer data."""
    simulation_id: int


class AquiferDataUpdate(BaseModel):
    """Schema for updating aquifer data."""
    hydraulic_conductivity_layers: Optional[List[Dict[str, Any]]] = None
    specific_yield: Optional[float] = Field(None, gt=0, le=1)
    specific_storage: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)


class AquiferDataResponse(AquiferDataBase):
    """Schema for aquifer data response."""
    id: int
    simulation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
