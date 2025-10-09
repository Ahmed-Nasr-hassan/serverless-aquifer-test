"""
ModelInput schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ModelInputBase(BaseModel):
    """Base schema for model input data."""
    user_id: str = Field(..., min_length=1, max_length=255)
    model_id: str = Field(..., min_length=1, max_length=255)
    model_inputs: Dict[str, Any] = Field(..., description="Complete model inputs data")
    hydraulic_conductivity: List[Dict[str, Any]] = Field(..., description="Hydraulic conductivity data")
    description: Optional[str] = None


class ModelInputCreate(ModelInputBase):
    """Schema for creating model input data."""
    simulation_id: int


class ModelInputUpdate(BaseModel):
    """Schema for updating model input data."""
    user_id: Optional[str] = Field(None, min_length=1, max_length=255)
    model_id: Optional[str] = Field(None, min_length=1, max_length=255)
    model_inputs: Optional[Dict[str, Any]] = None
    hydraulic_conductivity: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None


class ModelInputResponse(ModelInputBase):
    """Schema for model input response."""
    id: int
    simulation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
