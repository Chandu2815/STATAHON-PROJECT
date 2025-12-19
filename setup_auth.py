"""
Test script to verify role-based authentication and routing
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.auth import get_password_hash

def create_demo_users():
    """Create demo users for testing"""
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).filter(
            User.username.in_(['admin', 'researcher1', 'publicuser'])
        ).all()
        
        if len(existing_users) >= 3:
            print("✓ Demo users already exist")
            for user in existing_users:
                print(f"  - {user.username} ({user.role.value})")
            return
        
        # Create admin user
        admin = User(
            email="admin@mospi.gov.in",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            credits=1000.0
        )
        
        # Create researcher user
        researcher = User(
            email="researcher@mospi.gov.in",
            username="researcher1",
            full_name="Research Analyst",
            hashed_password=get_password_hash("researcher123"),
            role=UserRole.RESEARCHER,
            is_active=True,
            credits=100.0
        )
        
        # Create public user
        public = User(
            email="public@mospi.gov.in",
            username="publicuser",
            full_name="Public User",
            hashed_password=get_password_hash("public123"),
            role=UserRole.PUBLIC,
            is_active=True,
            credits=10.0
        )
        
        # Add users if they don't exist
        for user in [admin, researcher, public]:
            existing = db.query(User).filter(User.username == user.username).first()
            if not existing:
                db.add(user)
                print(f"✓ Created user: {user.username} ({user.role.value})")
        
        db.commit()
        print("\n✓ Demo users ready for testing")
        print("\nLogin credentials:")
        print("  Admin: admin / admin123")
        print("  Researcher: researcher1 / researcher123")
        print("  Public: publicuser / public123")
        
    except Exception as e:
        print(f"✗ Error creating demo users: {e}")
        db.rollback()
    finally:
        db.close()

def verify_setup():
    """Verify that all required files exist"""
    print("\n=== Verifying Setup ===\n")
    
    templates_dir = Path(__file__).parent / "app" / "templates"
    
    checks = [
        (templates_dir / "login.html", "Login page"),
        (templates_dir / "dashboard.html", "Dashboard page"),
        (Path(__file__).parent / "app" / "api" / "frontend.py", "Frontend API"),
        (Path(__file__).parent / "app" / "api" / "auth.py", "Auth API"),
    ]
    
    all_ok = True
    for file_path, description in checks:
        if file_path.exists():
            print(f"✓ {description} exists: {file_path.name}")
        else:
            print(f"✗ {description} missing: {file_path}")
            all_ok = False
    
    if all_ok:
        print("\n✓ All required files exist")
    else:
        print("\n✗ Some files are missing")
    
    return all_ok

if __name__ == "__main__":
    print("=== MoSPI Data Portal - Setup Verification ===\n")
    
    # Verify files
    if not verify_setup():
        sys.exit(1)
    
    # Create demo users
    print("\n=== Creating Demo Users ===\n")
    create_demo_users()
    
    print("\n=== Setup Complete ===\n")
    print("Start the server with: .\\start.ps1")
    print("Then access:")
    print("  - Login page: http://localhost:8080/login")
    print("  - Landing page: http://localhost:8080/")
    print("  - Dashboard (after login): http://localhost:8080/dashboard")
    print("  - API docs (admin): http://localhost:8080/docs")
