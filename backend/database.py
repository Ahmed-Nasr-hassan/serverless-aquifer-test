"""
Database configuration and connection management for FastAPI application.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - can be configured via environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://aquifer_user:aquifer_password@localhost:5432/aquifer_db"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=False           # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database.
    Call this function to initialize the database schema.
    """
    # Import models to ensure they are registered with Base
    from models import Model, Simulation
    Base.metadata.create_all(bind=engine)
