"""
SQLAlchemy Database Connection Manager
Provides session management for Survey AI backend
Connects exclusively to VPS PostgreSQL database via environment variables
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv
import logging
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(verbose=True)

# Database Configuration - NO FALLBACK DEFAULTS (read from .env only)
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default port only
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Validate required configuration
missing_vars = []
if not DB_HOST:
    missing_vars.append("DB_HOST")
if not DB_NAME:
    missing_vars.append("DB_NAME")
if not DB_USER:
    missing_vars.append("DB_USER")
if not DB_PASSWORD:
    missing_vars.append("DB_PASSWORD")

if missing_vars:
    error_msg = f"❌ FATAL: Missing required environment variables: {', '.join(missing_vars)}. Please check .env file."
    logger.error(error_msg)
    raise RuntimeError(error_msg)

# URL encode password to handle special characters
encoded_password = quote(DB_PASSWORD, safe='')

# SQLAlchemy Database URL - VPS connection only
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Log connection details (without password)
safe_url = f"postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}"
logger.info(f"📊 Database Configuration: {safe_url}")
print(f"Connected DB: postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    # Create engine with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_pre_ping=True,  # Test connections before using them
        pool_recycle=3600,  # Recycle connections every hour
        echo=os.getenv("DB_ECHO_SQL", "false").lower() == "true",
        connect_args={
            "connect_timeout": int(os.getenv("DB_POOL_TIMEOUT", "10")),
        }
    )
    
    # Test connection on startup
    with engine.connect() as conn:
        result = conn.execute("SELECT version()").fetchone()
        logger.info(f"✅ Successfully connected to PostgreSQL at {DB_HOST}:{DB_PORT}")
        logger.info(f"✅ PostgreSQL version: {result[0][:50]}...")
        
except Exception as e:
    error_msg = f"❌ FATAL: Failed to create database engine. Connection error: {str(e)}"
    logger.error(error_msg)
    raise RuntimeError(error_msg) from e

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """
    Dependency to get database session.
    
    Usage in FastAPI:
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync() -> Session:
    """
    Synchronous version to get database session.
    
    Usage:
        db = get_db_sync()
        try:
            # Use db
        finally:
            db.close()
    """
    return SessionLocal()
