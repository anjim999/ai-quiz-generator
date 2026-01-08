"""
Core Configuration Module
=========================
Centralized configuration management using Pydantic Settings.
All environment variables are validated and typed.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic for validation and type coercion.
    """
    
    # ===========================================
    # Server Configuration
    # ===========================================
    PORT: int = Field(default=5000, description="Server port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    
    # ===========================================
    # Database Configuration
    # ===========================================
    DATABASE_URL: str = Field(
        ..., 
        description="PostgreSQL connection string"
    )
    DB_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    
    # ===========================================
    # JWT Authentication
    # ===========================================
    JWT_SECRET: str = Field(..., description="JWT signing secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRY_DAYS: int = Field(default=30, description="JWT token expiry in days")
    
    # ===========================================
    # Google Gemini API (LangChain)
    # ===========================================
    GEMINI_API_KEY: Optional[str] = Field(
        default=None, 
        description="Google Gemini API key for LangChain"
    )
    
    # ===========================================
    # Google OAuth
    # ===========================================
    GOOGLE_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="Google OAuth client ID"
    )
    
    # ===========================================
    # Email Service (Brevo)
    # ===========================================
    BREVO_API_KEY: Optional[str] = Field(
        default=None,
        description="Brevo API key for sending emails"
    )
    EMAIL_FROM: str = Field(
        default="AI Quiz Generator <noreply@example.com>",
        description="Email sender address"
    )
    
    # ===========================================
    # CORS Configuration
    # ===========================================
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed origins"
    )
    
    # ===========================================
    # Feature Flags
    # ===========================================
    ENABLE_URL_CACHE: bool = Field(
        default=True,
        description="Enable caching to prevent duplicate URL scraping"
    )
    
    # ===========================================
    # Rate Limiting
    # ===========================================
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Maximum requests per minute per IP"
    )
    
    # ===========================================
    # Computed Properties
    # ===========================================
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string to list."""
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Export settings instance for easy access
settings = get_settings()
