"""
Comprehensive simulation schemas with relationships.
"""

from pydantic import BaseModel
from typing import List
from .simulation import SimulationResponse
from .aquifer_data import AquiferDataResponse
from .optimization_result import OptimizationResultResponse
from .well_data import WellDataResponse
from .model_input import ModelInputResponse


class SimulationDetailResponse(SimulationResponse):
    """Detailed simulation response with all related data."""
    aquifer_data: List[AquiferDataResponse] = []
    optimization_results: List[OptimizationResultResponse] = []
    well_data: List[WellDataResponse] = []
    model_inputs: List[ModelInputResponse] = []

    class Config:
        from_attributes = True
