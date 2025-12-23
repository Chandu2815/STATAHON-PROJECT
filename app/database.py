"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create database engine
# Support both PostgreSQL and SQLite
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args=connect_args
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import all models to ensure they're registered
    from app.models import dataset, user
    from app.models.user import User, UserRole
    import bcrypt
    
    Base.metadata.create_all(bind=engine)
    
    # Create default admin if not exists
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            admin = db.query(User).filter(User.username == 'admin').first()
        
        if not admin:
            print("Creating default admin user...")
            password = "admin123"
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            admin = User(
                username="admin",
                email="admin@mospi.gov.in",
                full_name="System Administrator",
                hashed_password=hashed.decode('utf-8'),
                password=password,  # Store plain password for admin viewing
                role=UserRole.ADMIN,
                is_active=True,
                credits=999999.0
            )
            db.add(admin)
            db.commit()
            print(f"✅ Default admin created - Username: admin, Password: admin123")
        else:
            print(f"✅ Admin user exists: {admin.username}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
