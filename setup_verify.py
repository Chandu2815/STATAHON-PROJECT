#!/usr/bin/env python3
"""
Quick Setup & Verification Script
Run this once to verify everything is configured correctly
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n▶ {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Success")
            if result.stdout:
                print(f"  {result.stdout[:200]}")
        else:
            print(f"  ✗ Failed")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Exception: {str(e)}")
        return False
    return True

print("=" * 80)
print("FASTAPI + POSTGRESQL SETUP VERIFICATION")
print("=" * 80)

print("\n[1] Checking Python Version")
print("-" * 80)
result = subprocess.run(["python", "--version"], capture_output=True, text=True)
print(f"Python: {result.stdout.strip()}")

print("\n[2] Checking Required Packages")
print("-" * 80)
packages = ["sqlalchemy", "psycopg2", "fastapi", "uvicorn", "pydantic", "python-dotenv"]
all_installed = True
for package in packages:
    try:
        __import__(package)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - NOT INSTALLED")
        all_installed = False

if not all_installed:
    print("\n⚠ Missing packages! Run:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

print("\n[3] Environment Configuration")
print("-" * 80)
if os.path.exists(".env"):
    print("  ✓ .env file found")
else:
    print("  ✗ .env file NOT found - creating...")
    with open(".env", "w") as f:
        f.write("DATABASE_URL=postgresql://postgres:NewPassword123@187.127.138.4:5432/statahon_db\n")
        f.write("DEBUG=True\n")
    print("  ✓ Created .env file")

print("\n[4] Testing Database Connection")
print("-" * 80)
run_command("python test_db_connection.py", "Running database connection test")

print("\n" + "=" * 80)
print("SETUP COMPLETE!")
print("=" * 80)

print("\nNext Steps:")
print("  1. Start the API server:")
print("     python main.py")
print("")
print("  2. Access the API:")
print("     - Main:   http://localhost:8000/")
print("     - Docs:   http://localhost:8000/docs")
print("     - Health: http://localhost:8000/health")
print("")
print("  3. Test an endpoint (in another terminal):")
print("     curl -X POST http://localhost:8000/add \\")
print("       -H 'Content-Type: application/json' \\")
print("       -d '{\"data\": {\"test\": \"value\"}}'")
print("")
print("=" * 80)
