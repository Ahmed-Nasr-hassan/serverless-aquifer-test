"""
ModelInput model for storing model input parameters.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class ModelInput(Base):
    """Model for storing model input parameters."""
    __tablename__ = "model_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # Core identifiers from JSON
    user_id = Column(String(255), nullable=False, index=True)
    model_id = Column(String(255), nullable=False, index=True)
    
    # Main data containers from JSON
    model_inputs = Column(JSON)  # Complete model_inputs object from JSON
    hydraulic_conductivity = Column(JSON)  # Array of hydraulic conductivity data
    
    # Optional metadata
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="model_inputs")
    
    def __repr__(self):
        return f"<ModelInput(id={self.id}, simulation_id={self.simulation_id}, model_id='{self.model_id}')>"
