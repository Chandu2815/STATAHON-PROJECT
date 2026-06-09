#!/usr/bin/env python3
"""
Startup Verification Script
Verifies all components are connected and working
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_success(msg):
    """Print success message"""
    print(f"✅ {msg}")

def print_error(msg):
    """Print error message"""
    print(f"❌ {msg}")

def print_info(msg):
    """Print info message"""
    print(f"ℹ️  {msg}")

def check_environment():
    """Check environment and configuration"""
    print_header("Environment Check")
    
    # Load environment variables
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        print_success(f"Found .env file: {env_file.absolute()}")
    else:
        print_error(".env file not found!")
        return False
    
    # Check database URL
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print_success(f"DATABASE_URL configured")
        print_info(f"Database: {db_url.split('/')[-1]}")
    else:
        print_error("DATABASE_URL not configured in .env!")
        return False
    
    return True

def check_database_connection():
    """Check database connection"""
    print_header("Database Connection Check")
    
    try:
        import psycopg2
        print_success("psycopg2 module available")
    except ImportError:
        print_error("psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    
    try:
        from db import engine
        from sqlalchemy import text
        print_success("SQLAlchemy engine initialized")
        
        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print_success(f"Connected to PostgreSQL: {version[:50]}...")
            
            # Check table exists
            result = conn.execute(text(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='survey_data');"
            ))
            if result.scalar():
                print_success("survey_data table exists")
                
                # Count rows
                result = conn.execute(text("SELECT COUNT(*) FROM survey_data;"))
                count = result.scalar()
                print_success(f"survey_data table has {count:,} rows")
            else:
                print_info("survey_data table does not exist yet (will be created on first use)")
        
        return True
    
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False

def check_fastapi():
    """Check FastAPI setup"""
    print_header("FastAPI Check")
    
    try:
        import fastapi
        print_success(f"FastAPI {fastapi.__version__} loaded")
    except ImportError:
        print_error("FastAPI not installed. Run: pip install fastapi uvicorn")
        return False
    
    try:
        from main import app
        print_success("main.py application loaded")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print_success(f"Endpoints configured: {', '.join(routes)}")
        
        return True
    except Exception as e:
        print_error(f"Failed to load main.py: {str(e)}")
        return False

def check_csv_uploader():
    """Check CSV uploader"""
    print_header("CSV Uploader Check")
    
    csv_file = Path("/Users/arunsudhaveni/Desktop/DataSet1.csv")
    if csv_file.exists():
        size_mb = csv_file.stat().st_size / (1024 * 1024)
        print_success(f"DataSet1.csv found ({size_mb:.2f} MB)")
    else:
        print_error(f"DataSet1.csv not found at {csv_file}")
        return False
    
    try:
        from csv_uploader import CSVUploader
        print_success("CSV Uploader module loaded")
        return True
    except Exception as e:
        print_error(f"Failed to load csv_uploader: {str(e)}")
        return False

def check_dependencies():
    """Check all Python dependencies"""
    print_header("Dependencies Check")
    
    required = {
        "pandas": "Data processing",
        "sqlalchemy": "ORM and database",
        "fastapi": "Web framework",
        "uvicorn": "ASGI server",
        "psycopg2": "PostgreSQL driver",
        "dotenv": "Environment configuration",
        "pydantic": "Data validation"
    }
    
    all_good = True
    for package, description in required.items():
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package:20} - {description}")
        except ImportError:
            print_error(f"{package:20} - {description} (NOT INSTALLED)")
            all_good = False
    
    return all_good

def main():
    """Run all checks"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   STATAHON PROJECT - STARTUP VERIFICATION               ║")
    print("║   Database Connection & API Status                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Database", check_database_connection),
        ("FastAPI", check_fastapi),
        ("CSV Uploader", check_csv_uploader),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Unexpected error in {name} check: {str(e)}")
            results[name] = False
    
    # Summary
    print_header("Summary")
    all_passed = all(results.values())
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20} {status}")
    
    print("\n")
    if all_passed:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║  ✅ ALL CHECKS PASSED - System is ready to use!          ║")
        print("║                                                          ║")
        print("║  To start the API server:                               ║")
        print("║  $ uvicorn main:app --reload                            ║")
        print("║                                                          ║")
        print("║  API will be available at: http://localhost:8000        ║")
        print("║  Docs: http://localhost:8000/docs                       ║")
        print("╚══════════════════════════════════════════════════════════╝")
        return 0
    else:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║  ⚠️  SOME CHECKS FAILED - See errors above              ║")
        print("║                                                          ║")
        print("║  To install missing dependencies:                       ║")
        print("║  $ pip install -r requirements.txt                      ║")
        print("╚══════════════════════════════════════════════════════════╝")
        return 1

if __name__ == "__main__":
    sys.exit(main())
