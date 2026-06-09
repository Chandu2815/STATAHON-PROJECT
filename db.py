import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1234@127.0.0.1:5432/survey_db"
)

# Create SQLAlchemy engine with connection pooling
# QueuePool helps manage multiple connections efficiently
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Additional connections when pool is exhausted
    pool_pre_ping=True,  # Test connections before using them
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get a database session.
    Used with FastAPI dependency injection.
    
    Yields:
        Session: SQLAlchemy database session
    
    Example:
        @app.get("/data")
        def get_data(db: Session = Depends(get_db)):
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """
    Test the database connection.
    
    Returns:
        dict: Connection status and details
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        return {
            "status": "success",
            "message": "Database connection successful",
            "database_url": DATABASE_URL
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Database connection failed: {str(e)}",
            "database_url": DATABASE_URL,
            "error": str(e)
        }


# Optional: Create tables if needed
def init_db():
    """
    Initialize database tables.
    Call this once at startup if using SQLAlchemy ORM models.
    """
    from sqlalchemy.orm import declarative_base
    
    Base = declarative_base()
    # Base.metadata.create_all(bind=engine)
    print("Database initialized")


if __name__ == "__main__":
    # Test the connection
    result = test_connection()
    print(result)
