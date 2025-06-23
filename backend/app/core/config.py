from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, AnyHttpUrl
import secrets


class Settings(BaseSettings):
    GROQ_API_KEY: str
    
    ENVIRONMENT: str = "production"
    PROJECT_NAME: str = "EgoAI"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = "http://localhost:8000/api/v1/auth/google/callback"
    
    DATABASE_URL: PostgresDsn

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='ignore')


settings = Settings()
