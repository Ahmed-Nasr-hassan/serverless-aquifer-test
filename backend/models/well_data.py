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
    
    # Well geometry
    distance_from_pumping_well_meters = Column(JSON)  # Array of distances
    well_radius_meters = Column(Float)
    screen_top_meters = Column(Float)
    screen_bottom_meters = Column(Float)
    
    # Simulation results
    simulated_drawdown_meters = Column(JSON)  # Array of drawdown values
    observed_drawdown_meters = Column(JSON)  # Array of observed values
    observed_time_seconds = Column(JSON)  # Array of time values
    avg_head_at_distance_meters = Column(JSON)  # Array of head values
    
    # Interpolation results
    interpolated_times = Column(JSON)
    interpolated_observed_drawdown = Column(JSON)
    interpolated_simulated_drawdown = Column(JSON)
    rmse = Column(Float)
    total_residual_error = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="well_data")
    
    def __repr__(self):
        return f"<WellData(id={self.id}, well_id='{self.well_id}', simulation_id={self.simulation_id})>"
