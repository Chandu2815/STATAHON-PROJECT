"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/mospi_dpi"
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
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def allowed_origins_list(self) -> list:
        """Convert comma-separated string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
