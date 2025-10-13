"""
Simulation model for storing simulation runs and results.
"""

from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class Simulation(Base):
    """Model for storing simulation runs and results."""
    __tablename__ = "simulations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    
    # Simulation details
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    simulation_type = Column(String(100), nullable=False)  # "Forward Run", "Optimization", etc.
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    # Settings and results as JSON
    simulation_settings = Column(JSON)  # Simulation configuration and parameters
    results = Column(JSON)  # All simulation results and analysis
    
    # Execution metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # User association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    model = relationship("Model", back_populates="simulations")
    user = relationship("User", back_populates="simulations")
    
    def __repr__(self):
        return f"<Simulation(id={self.id}, name='{self.name}', type='{self.simulation_type}')>"
