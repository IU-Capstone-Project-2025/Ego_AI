from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, AnyHttpUrl
import secrets


class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    PROJECT_NAME: str = "EgoAI"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    ML_SERVICE_URL: str = "http://ego-ai-ml-service:8001/chat"
    
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = "http://localhost:8000/api/v1/auth/google/callback"
    
    DATABASE_URL: PostgresDsn
    MONGO_URL: Optional[str] = None

    GROQ_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='ignore')

    @property
    def backend_cors_origins_list(self) -> List[str]:
        origins = []
        if self.BACKEND_CORS_ORIGINS.startswith("["):
            import json
            origins = json.loads(self.BACKEND_CORS_ORIGINS)
        else:
            origins = [self.BACKEND_CORS_ORIGINS]
        
        # Ensure we have the production origins
        production_origins = ["http://egoai.duckdns.org", "https://egoai.duckdns.org"]
        for origin in production_origins:
            if origin not in origins:
                origins.append(origin)
                
        return origins


settings = Settings()
