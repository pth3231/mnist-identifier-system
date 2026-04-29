import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Gateway config
    GATEWAY_PORT: int = os.getenv("GATEWAY_PORT")

    # Authentication Service - User management
    AUTH_URL: str = os.getenv("AUTH_URL")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Next.js Server Side - CORS Allowance
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")


settings = Settings()
