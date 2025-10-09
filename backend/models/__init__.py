"""
SQLAlchemy models for the aquifer management system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.sql import func
from database import Base


class Simulation(Base):
    """Model for storing simulation configurations and results."""
    
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Simulation parameters
    aquifer_thickness = Column(Float, nullable=True)
    hydraulic_conductivity = Column(Float, nullable=True)
    porosity = Column(Float, nullable=True)
    pumping_rate = Column(Float, nullable=True)
    
    # Results
    drawdown_data = Column(Text, nullable=True)  # JSON string
    simulation_results = Column(Text, nullable=True)  # JSON string


class AquiferData(Base):
    """Model for storing aquifer measurement data."""
    
    __tablename__ = "aquifer_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    depth = Column(Float, nullable=True)
    hydraulic_conductivity = Column(Float, nullable=True)
    porosity = Column(Float, nullable=True)
    water_level = Column(Float, nullable=True)
    measurement_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OptimizationResult(Base):
    """Model for storing optimization results."""
    
    __tablename__ = "optimization_results"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, nullable=False, index=True)
    objective_function_value = Column(Float, nullable=True)
    optimized_parameters = Column(Text, nullable=True)  # JSON string
    convergence_status = Column(String(50), nullable=True)
    iterations = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
