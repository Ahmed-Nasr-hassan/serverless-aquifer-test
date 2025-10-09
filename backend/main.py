"""
FastAPI application main entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables
import os

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown
    pass

# Create FastAPI instance
app = FastAPI(
    title="Aquifer Management API",
    description="API for managing aquifer data and simulations",
    version="1.0.0",
    lifespan=lifespan
)

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure this properly for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Aquifer Management API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "aquifer-api"}

# Also expose versioned health for clients using API prefix
@app.get("/api/v1/health")
async def health_check_v1():
    return {"status": "healthy", "service": "aquifer-api"}

@app.get("/test-db")
async def test_database():
    """Test database connection."""
    from database import SessionLocal
    from models import Simulation
    db = SessionLocal()
    try:
        simulations = db.query(Simulation).all()
        return {"count": len(simulations), "status": "ok"}
    except Exception as e:
        return {"error": str(e), "status": "error"}
    finally:
        db.close()

# Include routers
from routers.models import models_router
from routers.simulation import simulation_router
from auth.routes import auth_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(models_router, prefix="/api/v1/models", tags=["models"])
app.include_router(simulation_router, prefix="/api/v1/simulations", tags=["simulations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)
