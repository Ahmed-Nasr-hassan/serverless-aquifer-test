"""
Common schemas for generic responses and errors.
"""

from pydantic import BaseModel
from typing import Optional


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    success: bool = False
