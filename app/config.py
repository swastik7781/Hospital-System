import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Utkal Hospital & Medical Research Centre"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = Field(default="development", alias="ENVIRONMENT")
    DEBUG: bool = True
    
    # Database
    # Defaults to SQLite async for instant local run; in docker/prod uses postgresql+asyncpg
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./hospital.db",
        alias="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL"
    )
    
    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        alias="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        alias="CELERY_RESULT_BACKEND"
    )
    
    # JWT Auth
    SECRET_KEY: str = Field(
        default="hospital-super-secure-production-secret-key-change-in-prod-1234567890",
        alias="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for convenience
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # Rate Limiting
    RATE_LIMIT_AUTH: str = "20/minute"
    RATE_LIMIT_STANDARD: str = "120/minute"
    
    # Uploads
    UPLOAD_DIR: str = "uploads"
    
    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if os.environ.get("VERCEL"):
            # On Vercel, if using local SQLite, place in writable temp directory
            if "sqlite" in url and "tmp" not in url:
                import tempfile
                tmp_db = os.path.join(tempfile.gettempdir(), "hospital.db").replace("\\", "/")
                return f"sqlite+aiosqlite:///{tmp_db}"
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def effective_upload_dir(self) -> str:
        if os.environ.get("VERCEL"):
            import tempfile
            return os.path.join(tempfile.gettempdir(), "hospital_uploads")
        return self.UPLOAD_DIR
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
try:
    os.makedirs(settings.effective_upload_dir, exist_ok=True)
except Exception:
    pass
