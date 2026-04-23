from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PredictionRequest(BaseModel):
    canvas_data: bytes = Field(..., description="96x96 grayscale image data")

class PredictionResult(BaseModel):
    character: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class PredictionResponse(BaseModel):
    predictions: list[PredictionResult]
