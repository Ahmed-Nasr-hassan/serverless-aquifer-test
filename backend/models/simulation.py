"""
Simulation model for storing simulation configurations and results.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Simulation(Base):
    """Model for storing simulation configurations and results."""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    simulation_type = Column(String(100), nullable=False)  # "Forward Run", "Optimization", etc.
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Results summary
    radius_of_influence_meters = Column(Float)
    total_wells_analyzed = Column(Integer)
    pumping_length_seconds = Column(Float)
    total_simulation_time_steps = Column(Integer)
    
    
    # User association
    user_id = Column(String(255), nullable=False, index=True)
    
    # Relationships
    aquifer_data = relationship("AquiferData", back_populates="simulation", cascade="all, delete-orphan")
    optimization_results = relationship("OptimizationResult", back_populates="simulation", cascade="all, delete-orphan")
    well_data = relationship("WellData", back_populates="simulation", cascade="all, delete-orphan")
    model_inputs = relationship("ModelInput", back_populates="simulation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Simulation(id={self.id}, name='{self.name}', type='{self.simulation_type}')>"
