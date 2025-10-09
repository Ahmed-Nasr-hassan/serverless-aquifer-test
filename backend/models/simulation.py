"""
Simulation model for storing simulation runs and results.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Simulation(Base):
    """Model for storing simulation runs and results."""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)
    
    # Simulation details
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    simulation_type = Column(String(100), nullable=False)  # "Forward Run", "Optimization", etc.
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    # Results as JSON
    results = Column(JSON)  # All simulation results and analysis
    
    # Execution metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Results summary (for quick access without parsing JSON)
    radius_of_influence_meters = Column(Float)
    total_wells_analyzed = Column(Integer)
    pumping_length_seconds = Column(Float)
    total_simulation_time_steps = Column(Integer)
    
    # User association
    user_id = Column(String(255), nullable=False, index=True)
    
    # Relationships
    model = relationship("Model", back_populates="simulations")
    
    def __repr__(self):
        return f"<Simulation(id={self.id}, name='{self.name}', type='{self.simulation_type}')>"
