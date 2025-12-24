"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./mospi_dpi.db"
    DATABASE_ECHO: bool = False
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "MoSPI Data Portal Infrastructure"
    DEBUG: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PUBLIC: str = "100/day"
    RATE_LIMIT_RESEARCHER: str = "1000/day"
    RATE_LIMIT_PREMIUM: str = "10000/day"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Payment
    PAYMENT_GATEWAY_URL: str = "https://mock-payment-gateway.example.com"
    PAYMENT_API_KEY: str = "mock-api-key"
    
    # CORS - Include both HTTP (dev) and HTTPS (prod) origins
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,https://localhost:3000,https://localhost:8000"
    
    # Security
    SECURE_COOKIES: bool = True  # Use secure cookies in production
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def allowed_origins_list(self) -> list:
        """Convert comma-separated string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
