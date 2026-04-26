import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/mnist_identifier")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ML Model
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/mnist_identifier.pth")
    NUM_CLASSES: int = 10
    INPUT_SIZE: int = 784  # 28 * 28

    # WebSocket
    MAX_PREDICTIONS: int = 15
    MIN_PREDICTIONS: int = 5

    # API
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")


settings = Settings()
