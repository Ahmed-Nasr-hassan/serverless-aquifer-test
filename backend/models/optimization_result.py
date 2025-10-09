"""
OptimizationResult model for storing optimization results.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class OptimizationResult(Base):
    """Model for storing optimization results."""
    __tablename__ = "optimization_results"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # Optimization configuration and results
    optimization_config = Column(JSON)  # Parameters optimized, constraints, etc.
    optimization_results = Column(JSON)  # Optimal values, convergence info, etc.
    
    # Performance metrics
    performance_metrics = Column(JSON)  # RMSE, errors, convergence data
    
    # Optional metadata
    description = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="optimization_results")
    
    def __repr__(self):
        return f"<OptimizationResult(id={self.id}, simulation_id={self.simulation_id})>"
