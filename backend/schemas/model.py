"""
Pydantic schemas for Model entity.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ModelBase(BaseModel):
    """Base schema for Model."""
    name: str
    description: Optional[str] = None
    model_type: str  # aquifer, well, optimization
    configuration: Dict[str, Any]  # Complete model configuration
    status: Optional[str] = "active"  # active, inactive, running, error
    user_id: str


class ModelCreate(ModelBase):
    """Schema for creating a Model."""
    pass


class ModelUpdate(BaseModel):
    """Schema for updating a Model."""
    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ModelResponse(ModelBase):
    """Schema for Model response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
