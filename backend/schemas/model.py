"""
Pydantic schemas for Model entity based on Model_Inputs.json structure.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal, List
from datetime import datetime
import uuid


class RadialDiscretization(BaseModel):
    """Radial discretization parameters."""
    boundary_distance_from_pumping_well: Dict[str, Any]
    second_column_size: Dict[str, Any]
    column_multiplier: Dict[str, Any]


class VerticalDiscretization(BaseModel):
    """Vertical discretization parameters."""
    saturated_top_elevation: Dict[str, Any]
    aquifer_bottom_elevation: Dict[str, Any]
    screen_top_cell_thickness: Dict[str, Any]
    screen_bottom_cell_thickness: Dict[str, Any]
    refinement_above_screen: Dict[str, Any]
    refinement_below_screen: Dict[str, Any]
    refinement_between_screen: Dict[str, Any]


class PumpingWell(BaseModel):
    """Pumping well parameters."""
    well_radius: Dict[str, Any]
    pumping_rate: Dict[str, Any]
    screen_top_elevation: Dict[str, Any]
    screen_bottom_elevation: Dict[str, Any]


class ObservationWell(BaseModel):
    """Observation well data."""
    well_id: str
    distance_from_well: float
    top_screen_level: float
    bottom_screen_level: float
    data: Dict[str, List[float]]  # time_minutes, water_level, drawdown


class ObservationWells(BaseModel):
    """Observation wells configuration."""
    observation_wells: Dict[str, ObservationWell]


class InitialBoundaryConditions(BaseModel):
    """Initial boundary conditions."""
    starting_head: Dict[str, Any]
    specified_head: Dict[str, Any]


class StressPeriods(BaseModel):
    """Stress periods configuration."""
    analysis_period: Dict[str, Any]
    pumping_length: Dict[str, Any]
    recovery_length: Dict[str, Any]
    number_of_time_steps: Dict[str, Any]
    time_multiplier: Dict[str, Any]
    time_units: Dict[str, Any]


class HydraulicParameters(BaseModel):
    """Hydraulic parameters."""
    hydraulic_conductivity: Dict[str, Any]
    vk_hk_ratio: Dict[str, Any]
    specific_yield: Dict[str, Any]
    specific_storage: Dict[str, Any]


class DataFiles(BaseModel):
    """Data files configuration."""
    observed_data: Dict[str, Any]


class ObservationData(BaseModel):
    """Observation data structure."""
    observation_wells: Dict[str, ObservationWell]


class SimulationSettings(BaseModel):
    """Simulation settings."""
    choose_type_of_simulation: Dict[str, Any]
    hydraulic_conductivity_flag: Dict[str, Any]
    vk_hk_ratio_flag: Dict[str, Any]
    specific_yield_flag: Dict[str, Any]
    specific_storage_flag: Dict[str, Any]


class HydraulicConductivityLayer(BaseModel):
    """Hydraulic conductivity layer."""
    soil_material: str
    layer_top_level_m: float
    layer_bottom_level_m: float
    hydraulic_conductivity_m_per_day: float


class ModelInputs(BaseModel):
    """Complete model inputs structure."""
    radial_discretization: RadialDiscretization
    vertical_discretization: VerticalDiscretization
    pumping_well: PumpingWell
    observation_wells: ObservationWells
    initial_boundary_conditions: InitialBoundaryConditions
    stress_periods: StressPeriods
    hydraulic_parameters: HydraulicParameters
    data_files: DataFiles
    observation_data: ObservationData
    simulation_settings: SimulationSettings


class ModelMetadata(BaseModel):
    """Model metadata."""
    source_file: str
    sheets: List[str]
    conversion_timestamp: str


class ModelConfiguration(BaseModel):
    """Complete model configuration."""
    metadata: ModelMetadata
    data: Dict[str, Any]  # Contains user_id, model_id, model_inputs, hydraulic_conductivity
    model_inputs: ModelInputs
    hydraulic_conductivity: List[HydraulicConductivityLayer]


class ModelBase(BaseModel):
    """Base schema for Model."""
    name: str
    description: Optional[str] = None
    model_type: Literal["aquifer_test", "conceptual", "solute_transport", "seawater_intrusion", "stochastic"]
    # Relax response/input to accept any JSON shape for configuration to avoid 500s on legacy data
    configuration: Optional[Dict[str, Any]] = None
    status: Optional[str] = "active"  # active, inactive, running, error


class ModelCreate(BaseModel):
    """Schema for creating a Model. user_id is inferred from auth."""
    name: str
    description: Optional[str] = None
    model_type: Literal["aquifer_test", "conceptual", "solute_transport", "seawater_intrusion", "stochastic"]
    configuration: Optional[Dict[str, Any]] = None
    status: Optional[str] = "active"


class ModelUpdate(BaseModel):
    """Schema for updating a Model."""
    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[Literal["aquifer_test", "conceptual", "solute_transport", "seawater_intrusion", "stochastic"]] = None
    configuration: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ModelResponse(ModelBase):
    """Schema for Model response."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
