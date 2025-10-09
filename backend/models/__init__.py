"""
Models package for the aquifer management system.
Imports all models from individual files for better organization.
"""

from .simulation import Simulation
from .aquifer_data import AquiferData
from .optimization_result import OptimizationResult
from .well_data import WellData
from .model_input import ModelInput

__all__ = [
    'Simulation',
    'AquiferData', 
    'OptimizationResult',
    'WellData',
    'ModelInput'
]