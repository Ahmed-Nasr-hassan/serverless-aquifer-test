"""
Models package for the aquifer management system.
Imports all models from individual files for better organization.
"""

from .model import Model
from .simulation import Simulation

__all__ = [
    'Model',
    'Simulation'
]