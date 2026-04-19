import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/japanese_identifier")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/japanese_classifier.pth")
    NUM_CLASSES: int = 3036
    INPUT_SIZE: int = 9216  # 96 * 96
    
    # WebSocket
    MAX_PREDICTIONS: int = 15
    MIN_PREDICTIONS: int = 5
    
    # API
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    class Config:
        env_file = ".env"

settings = Settings()
