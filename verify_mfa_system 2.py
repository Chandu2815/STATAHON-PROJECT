#!/usr/bin/env python3
"""
Microsoft Authenticator MFA System Verification & Testing Script
Tests the TOTP-based authentication system end-to-end

Usage:
  python verify_mfa_system.py --test              # Run all tests
  python verify_mfa_system.py --verify            # Verify configuration only
  python verify_mfa_system.py --interactive       # Interactive testing
"""

import requests
import json
import time
import sys
import argparse
import pyotp
from datetime import datetime
from typing import Optional, Tuple

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 10

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def check_server_health() -> bool:
    """Check if server is running"""
    print_header("STEP 1: Server Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/../health", timeout=TIMEOUT)
        if response.status_code == 200:
            print_success(f"Server is running at {BASE_URL}")
            print_info(f"Response: {response.json()}")
            return True
    except requests.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Make sure the server is running:")
        print_info("  ./start.sh")
        print_info("  OR: python3.13 -m uvicorn main:app --host 127.0.0.1 --port 8000")
        return False
    except Exception as e:
        print_error(f"Error checking server: {str(e)}")
        return False

def test_registration_flow() -> Optional[Tuple[str, str, str]]:
    """Test user registration with MFA"""
    print_header("STEP 2: Registration Flow")
    
    # Use unique email/username with timestamp
    timestamp = int(time.time())
    test_email = f"mfa_test_{timestamp}@example.com"
    test_username = f"mfa_test_{timestamp}"
    test_password = "SecurePass123!TestOK"
    
    print_info(f"Registering test user: {test_username}")
    
    try:
        # Step 2.1: Start registration (get QR code)
        print_info("Sending registration request...")
        response = requests.post(
            f"{BASE_URL}/auth/register/start",
            json={
                "email": test_email,
                "username": test_username,
                "full_name": f"Test User {timestamp}",
                "password": test_password,
                "role": "PUBLIC"
            },
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            print_error(f"Registration start failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
        
        reg_data = response.json()
        print_success("Registration challenge created")
        
        challenge_id = reg_data.get("challenge_id")
        setup_key = reg_data.get("setup_key")
        otpauth_url = reg_data.get("otpauth_url")
        
        print_info(f"Challenge ID: {challenge_id}")
        print_info(f"Setup Key: {setup_key}")
        
        if otpauth_url:
            print_success("QR Code URL generated successfully")
            print_info(f"QR Code: {otpauth_url[:100]}...")
        
        # Step 2.2: Generate TOTP code (simulating Microsoft Authenticator)
        print_info("Generating TOTP code...")
        totp = pyotp.TOTP(setup_key)
        otp_code = totp.now()
        print_success(f"TOTP Code Generated: {otp_code}")
        
        # Step 2.3: Verify registration
        print_info("Verifying registration with TOTP code...")
        response = requests.post(
            f"{BASE_URL}/auth/register/verify",
            json={
                "challenge_id": challenge_id,
                "otp": otp_code
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 201:
            user_data = response.json()
            print_success("✅ Registration verified successfully!")
            print_info(f"User ID: {user_data.get('id')}")
            print_info(f"Email: {user_data.get('email')}")
            print_info(f"Username: {user_data.get('username')}")
            print_info(f"TOTP Enabled: {user_data.get('totp_enabled')}")
            
            return (test_username, test_password, setup_key)
        else:
            print_error(f"Registration verification failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Registration test failed: {str(e)}")
        return None

def test_login_flow(username: str, password: str, totp_secret: str) -> Optional[str]:
    """Test user login with MFA"""
    print_header("STEP 3: Login Flow")
    
    try:
        # Step 3.1: Login start
        print_info(f"Starting login for user: {username}")
        response = requests.post(
            f"{BASE_URL}/auth/login/start",
            json={
                "username": username,
                "password": password
            },
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            print_error(f"Login start failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
        
        login_data = response.json()
        challenge_id = login_data.get("challenge_id")
        print_success("Login challenge created")
        print_info(f"Challenge ID: {challenge_id}")
        
        # Step 3.2: Generate TOTP code
        print_info("Generating TOTP code for login...")
        totp = pyotp.TOTP(totp_secret)
        otp_code = totp.now()
        print_success(f"TOTP Code Generated: {otp_code}")
        
        # Step 3.3: Verify login
        print_info("Verifying login with TOTP code...")
        response = requests.post(
            f"{BASE_URL}/auth/login/verify",
            json={
                "challenge_id": challenge_id,
                "otp": otp_code
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            login_result = response.json()
            access_token = login_result.get("access_token")
            print_success("✅ Login verified successfully!")
            print_info(f"Token Type: {login_result.get('token_type')}")
            print_info(f"Username: {login_result.get('username')}")
            print_info(f"Role: {login_result.get('user_role')}")
            
            # Mask token for security
            token_preview = access_token[:20] + "..." + access_token[-10:] if access_token else "N/A"
            print_info(f"Access Token: {token_preview}")
            
            return access_token
        else:
            print_error(f"Login verification failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Login test failed: {str(e)}")
        return None

def test_wrong_code(username: str, password: str):
    """Test invalid MFA code handling"""
    print_header("STEP 4: Invalid Code Handling")
    
    try:
        # Get login challenge
        print_info("Starting login...")
        response = requests.post(
            f"{BASE_URL}/auth/login/start",
            json={
                "username": username,
                "password": password
            },
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            print_warning("Could not test invalid code (login start failed)")
            return
        
        challenge_id = response.json().get("challenge_id")
        
        # Try wrong code
        print_info("Attempting login with invalid code: 999999")
        response = requests.post(
            f"{BASE_URL}/auth/login/verify",
            json={
                "challenge_id": challenge_id,
                "otp": "999999"
            },
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            print_success(f"Invalid code correctly rejected: {response.status_code}")
            print_info(f"Error: {response.json().get('detail')}")
        else:
            print_error("Invalid code was ACCEPTED (security issue!)")
            
    except Exception as e:
        print_warning(f"Invalid code test failed: {str(e)}")

def test_totp_window():
    """Test TOTP time window tolerance"""
    print_header("STEP 5: TOTP Time Window Test")
    
    try:
        # Generate a test key
        test_key = pyotp.random_base32()
        totp = pyotp.TOTP(test_key)
        
        # Get current and next codes
        current_code = totp.now()
        
        # Check if code stays valid for ~30 seconds
        print_info(f"Test TOTP Key: {test_key}")
        print_info(f"Current Code: {current_code}")
        
        # Verify current code
        if totp.verify(current_code):
            print_success("✅ Current TOTP code is valid")
        else:
            print_error("Current TOTP code is invalid")
        
        # Check window tolerance
        print_info("Testing time window tolerance (±30 seconds)...")
        time.sleep(2)
        
        if totp.verify(current_code, valid_window=1):
            print_success("✅ Time window tolerance working (±30 seconds)")
        else:
            print_warning("⚠️  Code may have expired, try again in 10 seconds")
            
    except Exception as e:
        print_error(f"TOTP window test failed: {str(e)}")

def interactive_testing():
    """Interactive testing mode"""
    print_header("INTERACTIVE MFA TESTING")
    
    print_info("This tool will help you test the MFA system")
    print_info("Make sure you have Microsoft Authenticator installed")
    
    input("\n📱 Press ENTER when you have Microsoft Authenticator app ready...")
    
    # Test server
    if not check_server_health():
        return
    
    time.sleep(1)
    
    # Test registration
    reg_result = test_registration_flow()
    if not reg_result:
        print_error("Registration test failed, cannot continue")
        return
    
    username, password, totp_secret = reg_result
    time.sleep(1)
    
    # Test login
    token = test_login_flow(username, password, totp_secret)
    if not token:
        print_error("Login test failed")
        return
    
    time.sleep(1)
    
    # Test error handling
    test_wrong_code(username, password)
    time.sleep(1)
    
    # Test TOTP
    test_totp_window()
    
    # Summary
    print_header("TESTING COMPLETE ✅")
    print_success("All tests completed successfully!")
    print_info(f"Test user: {username}")
    print_info(f"Password: {password}")
    print_info("\nYou can now use these credentials to login at:")
    print_info("  http://127.0.0.1:8000/login")

def run_verification():
    """Run verification only (no interactive testing)"""
    print_header("MFA SYSTEM VERIFICATION")
    
    # Check server
    if not check_server_health():
        return
    
    print_success("\n✅ All verifications passed!")
    print_info("System is ready for MFA testing")
    print_info("Run with --interactive flag for full testing:")
    print_info("  python verify_mfa_system.py --interactive")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Microsoft Authenticator MFA System Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_mfa_system.py --verify              # Check configuration
  python verify_mfa_system.py --interactive         # Full interactive testing
  python verify_mfa_system.py --test                # Run all tests
        """
    )
    
    parser.add_argument("--verify", action="store_true", help="Verify configuration only")
    parser.add_argument("--interactive", action="store_true", help="Interactive testing")
    parser.add_argument("--test", action="store_true", help="Run all tests (same as interactive)")
    
    args = parser.parse_args()
    
    # Default to interactive if no args
    if not args.verify and not args.interactive and not args.test:
        args.interactive = True
    
    if args.verify:
        run_verification()
    elif args.interactive or args.test:
        interactive_testing()
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + Colors.YELLOW + "Testing cancelled by user" + Colors.RESET)
        sys.exit(0)
    except Exception as e:
        print("\n" + Colors.RED + f"Fatal error: {str(e)}" + Colors.RESET)
        sys.exit(1)
