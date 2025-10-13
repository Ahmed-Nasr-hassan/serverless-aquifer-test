"""
API routes for Simulation entity with authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from database import get_db
from models.simulation import Simulation
from models.model import Model
from models.user import User
from schemas.simulation import SimulationCreate, SimulationUpdate, SimulationResponse
from auth.utils import get_current_active_user
import boto3
import os
import json

simulation_router = APIRouter()


@simulation_router.post("/", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation(
    simulation: SimulationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new simulation."""
    # Verify that the model exists and belongs to the current user
    model = db.query(Model).filter(
        Model.id == simulation.model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Override user_id with current user's ID
    simulation_data = simulation.dict()
    simulation_data["user_id"] = current_user.id
    
    db_simulation = Simulation(**simulation_data)
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation


@simulation_router.get("/", response_model=List[SimulationResponse])
async def get_simulations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all simulations for the current user."""
    simulations = db.query(Simulation).filter(
        Simulation.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return simulations


@simulation_router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific simulation by ID."""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    return simulation


@simulation_router.put("/{simulation_id}", response_model=SimulationResponse)
async def update_simulation(
    simulation_id: uuid.UUID, 
    simulation_update: SimulationUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a simulation."""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    update_data = simulation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(simulation, field, value)
    
    db.commit()
    db.refresh(simulation)
    return simulation


@simulation_router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    simulation_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a simulation."""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    db.delete(simulation)
    db.commit()
    return None


@simulation_router.get("/model/{model_id}", response_model=List[SimulationResponse])
async def get_simulations_by_model(
    model_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all simulations for a specific model."""
    # Verify that the model exists and belongs to the current user
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    simulations = db.query(Simulation).filter(
        Simulation.model_id == model_id,
        Simulation.user_id == current_user.id
    ).all()
    return simulations


@simulation_router.post("/{simulation_id}/run")
async def run_simulation(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Builds a simulation run message using the model configuration and
    the simulation settings, prints it on the backend, and returns it.
    """
    # Fetch simulation owned by current user
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()

    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )

    # Fetch the related model (must be owned by current user too)
    model = db.query(Model).filter(
        Model.id == simulation.model_id,
        Model.user_id == current_user.id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    model_configuration = model.configuration or {}
    simulation_settings = simulation.simulation_settings or {}

    # If configuration already wraps the inputs under "model_inputs", use that inner dict.
    base_inputs = model_configuration.get("model_inputs", model_configuration)
    # Work on a shallow copy to avoid mutating stored config
    model_inputs = dict(base_inputs)

    # Normalize hydraulic_parameters keys and labels
    hp = model_inputs.get("hydraulic_parameters", {}) or {}
    normalized_hp = {}
    # Preserve already-correct labels if present
    if "Vk/Hk Ratio" in hp:
        val = hp.get("Vk/Hk Ratio")
        normalized_hp["Vk/Hk Ratio"] = val
    elif "vk_hk_ratio" in hp:
        val = hp.get("vk_hk_ratio")
        normalized_hp["Vk/Hk Ratio"] = {"value": val.get("value")} if isinstance(val, dict) else {"value": val}

    if "Specific Yield (Sy)" in hp:
        val = hp.get("Specific Yield (Sy)")
        normalized_hp["Specific Yield (Sy)"] = val
    elif "specific_yield" in hp:
        val = hp.get("specific_yield")
        normalized_hp["Specific Yield (Sy)"] = {"value": val.get("value")} if isinstance(val, dict) else {"value": val}

    if "Specific Storage (Ss)" in hp:
        val = hp.get("Specific Storage (Ss)")
        normalized_hp["Specific Storage (Ss)"] = val
    elif "specific_storage" in hp:
        val = hp.get("specific_storage")
        normalized_hp["Specific Storage (Ss)"] = {"value": val.get("value")} if isinstance(val, dict) else {"value": val}

    # Replace hydraulic_parameters with normalized mapping (drop inner hydraulic_conductivity from this section)
    if normalized_hp:
        model_inputs["hydraulic_parameters"] = normalized_hp

    # Always attach simulation_settings into model_inputs
    if simulation_settings:
        model_inputs["simulation_settings"] = simulation_settings

    # Normalize radial_discretization keys
    rd = model_inputs.get("radial_discretization")
    if isinstance(rd, dict):
        # boundary_distance_from_pumping_well -> "Boundary distance from pumping well"
        if "boundary_distance_from_pumping_well" in rd and "Boundary distance from pumping well" not in rd:
            rd["Boundary distance from pumping well"] = rd.pop("boundary_distance_from_pumping_well")
        model_inputs["radial_discretization"] = rd

    # Top-level hydraulic_conductivity (keep separate if provided in configuration)
    hydraulic_conductivity = model_configuration.get("hydraulic_conductivity", [])

    # Additional human-readable key normalizations per section
    # radial_discretization
    rd = model_inputs.get("radial_discretization")
    if isinstance(rd, dict):
        # second_column_size -> "2nd Column Size"
        if "second_column_size" in rd and "2nd Column Size" not in rd:
            rd["2nd Column Size"] = rd.pop("second_column_size")
        # column_multiplier -> "Column Multiplier"
        if "column_multiplier" in rd and "Column Multiplier" not in rd:
            rd["Column Multiplier"] = rd.pop("column_multiplier")
        model_inputs["radial_discretization"] = rd

    # vertical_discretization
    vd = model_inputs.get("vertical_discretization")
    if isinstance(vd, dict):
        mapping_vd = {
            "saturated_top_elevation": "Saturated top elevation",
            "aquifer_bottom_elevation": "Aquifer bottom elevation",
            "screen_top_cell_thickness": "Screen top - Cell thickness",
            "screen_bottom_cell_thickness": "Screen bottom- Cell thickness",
            "refinement_above_screen": "Refinment above screen",
            "refinement_below_screen": "Refinment below screen",
            "refinement_between_screen": "Refinment between screen",
        }
        for old_key, new_key in mapping_vd.items():
            if old_key in vd and new_key not in vd:
                vd[new_key] = vd.pop(old_key)
        model_inputs["vertical_discretization"] = vd

    # pumping_well
    pw = model_inputs.get("pumping_well")
    if isinstance(pw, dict):
        mapping_pw = {
            "well_radius": "Well Radius",
            "pumping_rate": "Q",
            "screen_top_elevation": "Screen Top Elevation",
            "screen_bottom_elevation": "Screen Bottom Elevation",
        }
        for old_key, new_key in mapping_pw.items():
            if old_key in pw and new_key not in pw:
                pw[new_key] = pw.pop(old_key)
        model_inputs["pumping_well"] = pw

    # initial_boundary_conditions
    ibc = model_inputs.get("initial_boundary_conditions")
    if isinstance(ibc, dict):
        mapping_ibc = {
            "starting_head": "Starting Head",
            "specified_head": "Specified Head",
        }
        for old_key, new_key in mapping_ibc.items():
            if old_key in ibc and new_key not in ibc:
                ibc[new_key] = ibc.pop(old_key)
        model_inputs["initial_boundary_conditions"] = ibc

    # stress_periods
    sp = model_inputs.get("stress_periods")
    if isinstance(sp, dict):
        mapping_sp = {
            "analysis_period": "Analysis Period",
            "pumping_length": "Pumping length",
            "recovery_length": "Recovery length",
            "number_of_time_steps": "Number of time steps",
            "time_multiplier": "Time Multiplier",
            "time_units": "Time Units",
        }
        for old_key, new_key in mapping_sp.items():
            if old_key in sp and new_key not in sp:
                sp[new_key] = sp.pop(old_key)
        model_inputs["stress_periods"] = sp

    # data_files
    df = model_inputs.get("data_files")
    if isinstance(df, dict):
        if "observed_data" in df and "Observed Data" not in df:
            df["Observed Data"] = df.pop("observed_data")
        model_inputs["data_files"] = df

    # Build final message with metadata wrapper
    from datetime import datetime, timezone
    message = {
            "user_id": str(current_user.id),
            "model_id": str(model.id),
            "model_inputs": model_inputs,
            "hydraulic_conductivity": hydraulic_conductivity,
    }

    # Print for now (server stdout)
    try:
        print(json.dumps(message, indent=2))
    except Exception:
        print(str(message))

    # Send to SQS if configured
    queue_url = os.getenv("SIMULATION_SQS_URL", "https://sqs.us-east-1.amazonaws.com/835410374509/aquifer-test-simulation-queue")
    try:
        sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
    except Exception as e:
        # Log and continue; still return message to client
        print(f"Failed to send SQS message: {e}")

    return message
