"""
ModelInput model for storing model input parameters.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class ModelInput(Base):
    """Model for storing model input parameters."""
    __tablename__ = "model_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # General parameters
    run_type = Column(String(100), nullable=False)
    model_name = Column(String(255))
    description = Column(Text)
    
    # Geometry parameters
    ztop = Column(Float)  # Top elevation
    zbot = Column(Float)  # Bottom elevation
    col_length = Column(Float)  # Column length
    radius_well = Column(Float)  # Well radius
    cell_size = Column(Float)  # Cell size
    horizontal_multiplier = Column(Float)  # Horizontal multiplier
    
    # Discretization parameters
    sc_top = Column(Float)  # Screen top
    sc_bottom = Column(Float)  # Screen bottom
    sc_top_thick = Column(Float)  # Screen top thickness
    sc_bottom_thick = Column(Float)  # Screen bottom thickness
    refine_above_screen = Column(Boolean)
    refine_below_screen = Column(Boolean)
    refine_between_screen = Column(Boolean)
    
    # Pumping parameters
    pumping_rate_m3_per_day = Column(Float)
    pumping_start_time_seconds = Column(Float)
    pumping_end_time_seconds = Column(Float)
    
    # Time parameters
    simulation_start_time_seconds = Column(Float)
    simulation_end_time_seconds = Column(Float)
    time_step_size_seconds = Column(Float)
    
    # Storage parameters
    specific_yield = Column(Float)
    specific_storage = Column(Float)
    
    # Raw input data (for reference)
    raw_input_data = Column(JSON)  # Complete input data as JSON
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="model_inputs")
    
    def __repr__(self):
        return f"<ModelInput(id={self.id}, simulation_id={self.simulation_id}, run_type='{self.run_type}')>"
