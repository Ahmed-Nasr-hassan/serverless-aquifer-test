"""
OptimizationResult schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class OptimizationResultBase(BaseModel):
    """Base schema for optimization results."""
    simulation_id: int
    parameters_optimized: Optional[List[str]] = None
    optimal_values: Optional[Dict[str, Any]] = None
    rmse: Optional[float] = Field(None, ge=0)
    total_residual_error: Optional[float] = Field(None, ge=0)
    convergence_achieved: Optional[bool] = False
    iterations_completed: Optional[int] = Field(None, ge=0)
    results_file_path: Optional[str] = None


class OptimizationResultCreate(OptimizationResultBase):
    """Schema for creating optimization results."""
    pass


class OptimizationResultResponse(OptimizationResultBase):
    """Schema for optimization result response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
