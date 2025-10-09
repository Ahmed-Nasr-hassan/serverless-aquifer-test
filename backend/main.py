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

# Include routers
from routers import simulation_router, data_router, optimization_router

app.include_router(simulation_router, prefix="/api/v1/simulations", tags=["simulations"])
app.include_router(data_router, prefix="/api/v1/data", tags=["aquifer-data"])
app.include_router(optimization_router, prefix="/api/v1/optimization", tags=["optimization"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
