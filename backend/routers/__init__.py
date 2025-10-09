"""
Routers package for API endpoints.
Imports all routers from individual files for better organization.
"""

from .simulation import simulation_router
from .aquifer_data import data_router
from .optimization_result import optimization_router
from .well_data import well_router
from .model_input import model_input_router

__all__ = [
    'simulation_router',
    'data_router',
    'optimization_router', 
    'well_router',
    'model_input_router'
]