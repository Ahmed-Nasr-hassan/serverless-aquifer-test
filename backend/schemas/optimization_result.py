"""
OptimizationResult schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class OptimizationResultBase(BaseModel):
    """Base schema for optimization results."""
    optimization_config: Dict[str, Any] = Field(..., description="Optimization configuration and parameters")
    optimization_results: Optional[Dict[str, Any]] = Field(None, description="Optimal values and convergence info")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="RMSE, errors, convergence data")
    description: Optional[str] = Field(None, max_length=500)


class OptimizationResultCreate(OptimizationResultBase):
    """Schema for creating optimization results."""
    simulation_id: int


class OptimizationResultUpdate(BaseModel):
    """Schema for updating optimization results."""
    optimization_config: Optional[Dict[str, Any]] = None
    optimization_results: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=500)


class OptimizationResultResponse(OptimizationResultBase):
    """Schema for optimization result response."""
    id: int
    simulation_id: int
    created_at: datetime

    class Config:
        from_attributes = True
