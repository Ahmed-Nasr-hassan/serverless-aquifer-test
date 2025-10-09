"""
Schemas package for request/response validation.
Imports all schemas from individual files for better organization.
"""

from .simulation import SimulationBase, SimulationCreate, SimulationUpdate, SimulationResponse
from .aquifer_data import AquiferDataBase, AquiferDataCreate, AquiferDataUpdate, AquiferDataResponse
from .optimization_result import OptimizationResultBase, OptimizationResultCreate, OptimizationResultResponse
from .well_data import WellDataBase, WellDataCreate, WellDataUpdate, WellDataResponse
from .model_input import ModelInputBase, ModelInputCreate, ModelInputUpdate, ModelInputResponse
from .common import MessageResponse, ErrorResponse
from .simulation_detail import SimulationDetailResponse

__all__ = [
    # Simulation schemas
    'SimulationBase',
    'SimulationCreate', 
    'SimulationUpdate',
    'SimulationResponse',
    'SimulationDetailResponse',
    
    # Aquifer data schemas
    'AquiferDataBase',
    'AquiferDataCreate',
    'AquiferDataUpdate', 
    'AquiferDataResponse',
    
    # Optimization schemas
    'OptimizationResultBase',
    'OptimizationResultCreate',
    'OptimizationResultResponse',
    
    # Well data schemas
    'WellDataBase',
    'WellDataCreate',
    'WellDataUpdate',
    'WellDataResponse',
    
    # Model input schemas
    'ModelInputBase',
    'ModelInputCreate',
    'ModelInputUpdate',
    'ModelInputResponse',
    
    # Common schemas
    'MessageResponse',
    'ErrorResponse'
]