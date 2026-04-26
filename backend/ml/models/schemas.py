from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class PredictionRequest(BaseModel):
    canvas_data: bytes = Field(..., description="32x32 grayscale image data")

class PredictionResult(BaseModel):
    character: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class PredictionResponse(BaseModel):
    predictions: list[PredictionResult]
