"""
SQLAlchemy Database Connection Manager
Provides session management for Survey AI backend.
Connects to the database specified in the .env file.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.url import make_url
from sqlalchemy.pool import QueuePool
from urllib.parse import quote
from fastapi import HTTPException
import os
from dotenv import load_dotenv
import logging

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    logger.info(f"📄 Loading environment variables from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, verbose=True)
else:
    logger.warning(f"⚠️ .env file not found at {dotenv_path}. Relying on system environment variables.")

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

db_url_source = "system"

# If DATABASE_URL is not set but individual variables are present, construct it
if not DATABASE_URL and all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    db_url_source = "constructed from individual variables"
    encoded_password = quote(DB_PASSWORD, safe='')
    DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
elif DATABASE_URL:
    db_url_source = "DATABASE_URL env var"
    # Parse individual values from DATABASE_URL if they are not explicitly set
    try:
        url_info = make_url(DATABASE_URL)
        if not DB_HOST: DB_HOST = url_info.host
        if not DB_PORT: DB_PORT = str(url_info.port or "5432")
        if not DB_NAME: DB_NAME = url_info.database
        if not DB_USER: DB_USER = url_info.username
        if not DB_PASSWORD: DB_PASSWORD = url_info.password
    except Exception as e:
        logger.warning(f"Could not parse details from DATABASE_URL: {e}")
else:
    # Configuration is incomplete
    missing_vars = []
    if not DB_HOST: missing_vars.append("DB_HOST")
    if not DB_NAME: missing_vars.append("DB_NAME")
    if not DB_USER: missing_vars.append("DB_USER")
    if not DB_PASSWORD: missing_vars.append("DB_PASSWORD")
    if not DATABASE_URL: missing_vars.append("DATABASE_URL")
    logger.error(f"❌ Database configuration is incomplete. Missing: {', '.join(missing_vars)}")

# Mask password for logging
masked_url = "None"
if DATABASE_URL:
    try:
        url_info = make_url(DATABASE_URL)
        password_str = "***" if url_info.password else ""
        masked_url = f"{url_info.drivername}://{url_info.username}:{password_str}@{url_info.host}:{url_info.port}/{url_info.database}"
    except Exception as e:
        masked_url = "Error parsing URL for masking"

logger.info(f"📊 DATABASE_URL source: {db_url_source}")
logger.info(f"📊 Database Configuration: {masked_url}")
logger.info(f"   - User: {DB_USER}")
logger.info(f"   - Host: {DB_HOST}")
logger.info(f"   - Database: {DB_NAME}")

# --- SQLAlchemy Engine Setup ---
engine = None
SessionLocal = None
db_connection_error = None

if DATABASE_URL:
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
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Test connection on startup (non-blocking if it fails)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).fetchone()
            logger.info(f"✅ Successfully connected to PostgreSQL at {DB_HOST}:{DB_PORT}")
            logger.info(f"✅ PostgreSQL version: {result[0][:50]}...")
    except Exception as e:
        db_connection_error = e
        logger.error(f"❌ Failed to connect to database: {e}")
else:
    db_connection_error = RuntimeError("Database configuration is missing or incomplete.")

def get_db_status():
    """Checks the current status of the database connection."""
    if db_connection_error:
        return {
            "status": "error",
            "error": str(db_connection_error),
            "host": DB_HOST,
            "database": DB_NAME,
        }
    if not engine:
        return {
            "status": "error",
            "error": "Engine not initialized",
            "host": DB_HOST,
            "database": DB_NAME,
        }
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return {
                "status": "ok",
                "host": DB_HOST,
                "database": DB_NAME,
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "host": DB_HOST,
            "database": DB_NAME,
        }

def get_db() -> Session:
    """FastAPI dependency to get a database session."""
    if db_connection_error:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(db_connection_error)}"
        )
    if not SessionLocal:
        raise HTTPException(
            status_code=500,
            detail="Database session factory not configured."
        )
    
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
    if db_connection_error:
        raise RuntimeError(f"Database connection error: {str(db_connection_error)}")
    if not SessionLocal:
        raise RuntimeError("Database session factory not configured.")
    return SessionLocal()
