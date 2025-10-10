"""
Model entity for storing aquifer model configurations.
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class Model(Base):
    """Model for storing aquifer model configurations."""
    __tablename__ = "models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    model_type = Column(String(50), nullable=False)  # aquifer, well, optimization
    
    # Complete model configuration as JSON
    configuration = Column(JSON)  # All ModelConfig data from frontend
    
    # Model status and metadata
    status = Column(String(50), default="active")  # active, inactive, running, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    simulations = relationship("Simulation", back_populates="model", cascade="all, delete-orphan")
    user = relationship("User", back_populates="models")
    
    def __repr__(self):
        return f"<Model(id={self.id}, name='{self.name}', type='{self.model_type}')>"
