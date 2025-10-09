"""
AquiferData model for storing aquifer parameter data.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class AquiferData(Base):
    """Model for storing aquifer parameter data."""
    __tablename__ = "aquifer_data"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # Hydraulic conductivity data as JSON array
    hydraulic_conductivity_layers = Column(JSON)  # Array of layer data
    
    # Storage parameters (can be stored per layer or globally)
    specific_yield = Column(Float)
    specific_storage = Column(Float)
    
    # Optional metadata
    description = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="aquifer_data")
    
    def __repr__(self):
        return f"<AquiferData(id={self.id}, simulation_id={self.simulation_id})>"
