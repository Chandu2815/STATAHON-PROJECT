"""
Database configuration and session management
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
import sys
import os

settings = get_settings()

# Global variables for database management
engine = None
SessionLocal = None
Base = declarative_base()
current_db_url = None

def _create_engine(database_url):
    """Create and return a database engine based on the URL"""
    # Only PostgreSQL is supported in this deployment
    return create_engine(
        database_url,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        connect_args={"connect_timeout": 10}
    )

def _initialize_db_engine():
    """Initialize the database engine (PostgreSQL-only)"""
    global engine, SessionLocal, current_db_url
    primary_url = settings.DATABASE_URL

    # Try to connect to the configured PostgreSQL instance only
    try:
        print(f"[DB] Attempting to connect to PostgreSQL database...")
        engine = _create_engine(primary_url)

        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print(f"[DB] ✅ Successfully connected to PostgreSQL database")

        current_db_url = primary_url

    except Exception as e:
        print(f"[DB] ❌ Failed to connect to PostgreSQL database")
        print(f"[DB] Error: {str(e)}")
        # Per policy: do not fallback to any other database. Raise error.
        raise
    
    # Create session factory after engine is initialized
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

# Initialize on module load
SessionLocal = _initialize_db_engine()


def get_db():
    """Database session dependency"""
    if SessionLocal is None:
        print("[DB] get_db called but SessionLocal is not initialized")
        raise RuntimeError("Database engine not initialized. Check database configuration.")

    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"[DB] Session error: {e}")
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables with error handling"""
    db = None  # Track if db session was created
    try:
        print("[DB] Initializing database...")
        
        # Check if engine was initialized
        if engine is None:
            raise RuntimeError("Database engine not initialized. Check database configuration in .env file.")
        
        # Import all models to ensure they're registered
        from app.models import dataset, user
        from app.models.user import User, UserRole, OtpChallenge
        import bcrypt
        import pyotp
        
        # Create all tables
        print("[DB] Creating tables from models...")
        Base.metadata.create_all(bind=engine)
        print("[DB] ✅ Tables created successfully")
        
        # Ensure user auth/account columns exist for backward compatibility
        _ensure_user_totp_columns()
        
        # Create or update default users
        db = SessionLocal()
        try:
            def ensure_user(username, email, full_name, password, role, credits):
                """Create or update user account"""
                try:
                    account_type = "researcher" if role == UserRole.RESEARCHER else "public"
                    default_query_credits = 100 if account_type == "researcher" else 10
                    user = db.query(User).filter(User.username == username).first()
                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    totp_enabled = username != "testuser"
                    if not user:
                        print(f"[USER] Creating {role} user: {username}...")
                        user = User(
                            username=username,
                            email=email,
                            full_name=full_name,
                            hashed_password=hashed,
                            password=password,
                            role=role,
                            is_active=True,
                            credits=credits,
                            account_type=account_type,
                            credits_remaining=default_query_credits,
                            credits_used=0,
                            totp_secret=pyotp.random_base32() if totp_enabled else None,
                            totp_enabled=totp_enabled,
                        )
                        db.add(user)
                        db.commit()
                        print(f"[USER] ✅ Created {username} (Password: {password})")
                    else:
                        # Update password to ensure it's correct
                        user.hashed_password = hashed
                        user.password = password
                        if username == "testuser":
                            user.totp_enabled = False
                        else:
                            if not user.totp_secret:
                                user.totp_secret = pyotp.random_base32()
                            user.totp_enabled = True
                        if not user.account_type:
                            user.account_type = account_type
                        if user.credits_remaining is None:
                            user.credits_remaining = default_query_credits
                        if user.credits_used is None:
                            user.credits_used = 0
                        db.commit()
                        print(f"[USER] ✅ User {username} exists - password reset to: {password}")
                    return user
                except Exception as e:
                    print(f"[USER] ❌ Error creating user {username}: {str(e)}")
                    db.rollback()
                    raise
            
            # Create admin user
            ensure_user(
                username="admin",
                email="admin@mospi.gov.in",
                full_name="System Administrator",
                password="admin123",
                role=UserRole.ADMIN,
                credits=999999.0
            )
            
            # Create test user
            ensure_user(
                username="testuser",
                email="testuser@mospi.gov.in",
                full_name="Test User",
                password="test123",
                role=UserRole.RESEARCHER,
                credits=100.0
            )
            
            # Load CSV data if needed
            load_csv_data_if_needed(db)
            
        except Exception as e:
            print(f"[USER] ❌ Fatal error during user initialization: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
            
        print("[DB] ✅ Database initialization complete")
        
    except Exception as e:
        print(f"[DB] ❌ CRITICAL: Database initialization failed")
        print(f"[DB] Error: {str(e)}")
        print(f"[DB] Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Check if it's a password auth error
        error_str = str(e).lower()
        if "password authentication failed" in error_str:
            print("[DB] ⚠️  PASSWORD AUTHENTICATION FAILED")
            print("[DB] Troubleshooting steps:")
            print("[DB]   1. Check .env DATABASE_URL password is correct")
            print("[DB]   2. Verify PostgreSQL server is running at 187.127.138.4:5432")
            print("[DB]   3. Run: psql -U postgres -h 187.127.138.4 -d statahon_db")
        
        # Don't exit here - let the application handle gracefully
        raise
        
    finally:
        # Only close db if it was actually created
        if db is not None:
            try:
                db.close()
            except Exception as e:
                print(f"[DB] Warning: Error closing database session: {e}")


def load_hces_datasets(db):
    """Load HCES (Household Consumption Expenditure Survey) datasets"""
    from sqlalchemy import text, inspect
    from pathlib import Path
    import pandas as pd
    from app.models.dataset import Dataset
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    base_path = Path(__file__).parent.parent
    
    hces_datasets = [
        {
            'name': 'HCES Household Identification',
            'table_name': 'hces_household_identification',
            'csv_file': 'hces_household_identification_clean.csv',
            'description': 'HCES Household Identification data'
        },
        {
            'name': 'HCES Food Expenditure',
            'table_name': 'hces_food_expenditure',
            'csv_file': 'hces_food_expenditure_clean.csv',
            'description': 'HCES Food Expenditure data'
        },
        {
            'name': 'HCES Non-Food Expenditure',
            'table_name': 'hces_non_food_expenditure',
            'csv_file': 'hces_non_food_expenditure_clean.csv',
            'description': 'HCES Non-Food Expenditure data'
        }
    ]
    
    # CSV loading from local files has been disabled for single-Postgres deployment.
    print("[DB] load_hces_datasets disabled: CSV loading is not permitted in PostgreSQL-only mode.")


def load_csv_data_if_needed(db):
    """Load CSV data into database if tables are empty"""
    try:
        from sqlalchemy import text, inspect
        from pathlib import Path
        import pandas as pd
        from app.models.dataset import Dataset
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Check if household_survey table exists and has data
        base_path = Path(__file__).parent.parent
        
        # CSV-based loading is disabled to enforce single PostgreSQL DB usage.
        print("[DB] load_csv_data_if_needed disabled: CSV loading from local files is not permitted.")
        
    except Exception as e:
        print(f"⚠️ CSV loading skipped due to error: {e}")


def _ensure_user_totp_columns() -> None:
    """Add user auth/account columns for existing databases without running migrations."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    user_columns = {col["name"] for col in inspector.get_columns("users")}

    with engine.begin() as conn:
        if "totp_secret" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN totp_secret VARCHAR(64)"))
        if "totp_enabled" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN totp_enabled BOOLEAN DEFAULT FALSE"))
        if "account_type" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN account_type VARCHAR(32)"))
        if "credits_remaining" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN credits_remaining INTEGER"))
        if "credits_used" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN credits_used INTEGER"))

        conn.execute(text("""
            UPDATE users
            SET account_type = CASE
                WHEN lower(role::text) = 'researcher' THEN 'researcher'
                ELSE 'public'
            END
            WHERE account_type IS NULL OR account_type = ''
        """))
        conn.execute(text("""
            UPDATE users
            SET credits_remaining = CASE
                WHEN account_type = 'researcher' THEN 100
                ELSE 10
            END
            WHERE credits_remaining IS NULL
        """))
        conn.execute(text("UPDATE users SET credits_used = 0 WHERE credits_used IS NULL"))
        conn.execute(text("ALTER TABLE users ALTER COLUMN account_type SET DEFAULT 'public'"))
        conn.execute(text("ALTER TABLE users ALTER COLUMN account_type SET NOT NULL"))
        conn.execute(text("ALTER TABLE users ALTER COLUMN credits_remaining SET DEFAULT 10"))
        conn.execute(text("ALTER TABLE users ALTER COLUMN credits_remaining SET NOT NULL"))
        conn.execute(text("ALTER TABLE users ALTER COLUMN credits_used SET DEFAULT 0"))
        conn.execute(text("ALTER TABLE users ALTER COLUMN credits_used SET NOT NULL"))


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
