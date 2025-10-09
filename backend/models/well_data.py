"""
WellData model for storing well information and results.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class WellData(Base):
    """Model for storing well information and results."""
    __tablename__ = "well_data"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # Well identification
    well_id = Column(String(100), nullable=False, index=True)
    well_type = Column(String(50), nullable=False)  # "pumping", "observation"
    
    # Well geometry and configuration
    well_configuration = Column(JSON)  # Complete well configuration data
    
    # Simulation results and observations
    simulation_results = Column(JSON)  # All simulation results data
    
    # Analysis results (RMSE, interpolation, etc.)
    analysis_results = Column(JSON)  # Analysis and comparison results
    
    # Optional metadata
    description = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="well_data")
    
    def __repr__(self):
        return f"<WellData(id={self.id}, well_id='{self.well_id}', simulation_id={self.simulation_id})>"
