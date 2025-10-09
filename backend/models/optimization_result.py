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
    
    # Optimization parameters
    parameters_optimized = Column(JSON)  # Array of parameter names
    optimal_values = Column(JSON)  # Object of optimal parameter values
    
    # Optimization metrics
    rmse = Column(Float)
    total_residual_error = Column(Float)
    convergence_achieved = Column(Boolean, default=False)
    iterations_completed = Column(Integer)
    
    # Results file path
    results_file_path = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="optimization_results")
    
    def __repr__(self):
        return f"<OptimizationResult(id={self.id}, simulation_id={self.simulation_id})>"
