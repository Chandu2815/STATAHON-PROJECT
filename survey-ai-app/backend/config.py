"""
Configuration for Survey AI Backend
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database - Use same database as MoSPI
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1234@127.0.0.1:5432/mospi_db"  # Shared with MoSPI
)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Database echo (set to True for debugging)
DATABASE_ECHO = False

class Settings:
    database_url: str = DATABASE_URL
    secret_key: str = SECRET_KEY
    algorithm: str = ALGORITHM
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
    database_echo: bool = DATABASE_ECHO

def get_settings():
    return Settings()
