import os
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Tushle"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # Database - Updated for Vercel deployment
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./automation_dashboard.db")
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    
    # AI Settings - Updated for Vercel
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    ENABLE_LLM_ANALYSIS: bool = True
    NEWS_API_KEY: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    ENABLE_REAL_TRENDING_DATA: bool = False
    ENABLE_LLM_ANALYSIS: bool = False
    DEFAULT_TRENDING_SOURCES: str = "reddit,hackernews,google_trends"
    
    # File Storage
    UPLOAD_FOLDER: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"


settings = Settings()

def get_settings() -> Settings:
    """Get settings instance"""
    return settings
