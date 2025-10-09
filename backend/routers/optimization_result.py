"""
Optimization result router endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import OptimizationResult
from schemas import OptimizationResultCreate, OptimizationResultResponse, MessageResponse

optimization_router = APIRouter()


@optimization_router.post("/", response_model=OptimizationResultResponse, status_code=status.HTTP_201_CREATED)
async def create_optimization_result(result: OptimizationResultCreate, db: Session = Depends(get_db)):
    """Create new optimization result."""
    db_result = OptimizationResult(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


@optimization_router.get("/", response_model=List[OptimizationResultResponse])
async def get_optimization_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all optimization results with pagination."""
    results = db.query(OptimizationResult).offset(skip).limit(limit).all()
    return results


@optimization_router.get("/simulation/{simulation_id}", response_model=List[OptimizationResultResponse])
async def get_optimization_results_by_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """Get optimization results for a specific simulation."""
    results = db.query(OptimizationResult).filter(
        OptimizationResult.simulation_id == simulation_id
    ).all()
    return results


@optimization_router.get("/{result_id}", response_model=OptimizationResultResponse)
async def get_optimization_result_by_id(result_id: int, db: Session = Depends(get_db)):
    """Get specific optimization result by ID."""
    result = db.query(OptimizationResult).filter(OptimizationResult.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization result not found"
        )
    return result


@optimization_router.delete("/{result_id}", response_model=MessageResponse)
async def delete_optimization_result(result_id: int, db: Session = Depends(get_db)):
    """Delete optimization result."""
    result = db.query(OptimizationResult).filter(OptimizationResult.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization result not found"
        )
    
    db.delete(result)
    db.commit()
    return MessageResponse(message="Optimization result deleted successfully")
