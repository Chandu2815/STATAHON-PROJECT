# MFA System Testing Guide
## End-to-End Testing for Microsoft Authenticator Integration

### Prerequisites
- FastAPI server running on `http://localhost:8000`
- PostgreSQL database connection active
- Python environment with required packages
- Microsoft Authenticator app installed on a mobile device (or authenticator simulator)

---

## Test Scenarios

### Scenario 1: User Registration and MFA Setup 🔐

#### 1.1: Register New User
```bash
curl -X POST http://localhost:8000/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mfatest@example.com",
    "username": "mfatestuser",
    "password": "SecurePass123!",
    "full_name": "MFA Test User"
  }'
```

**Expected Response:**
```json
{
  "id": 5,
  "email": "mfatest@example.com",
  "username": "mfatestuser",
  "full_name": "MFA Test User",
  "is_active": true,
  "totp_enabled": false,
  "message": "User registered successfully"
}
```

**Validation Checklist:**
- ✅ User created in database
- ✅ Password hashed (not stored in plain text)
- ✅ TOTP enabled = false (MFA not yet setup)
- ✅ Email stored correctly

#### 1.2: Login Without MFA Setup
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "mfatestuser",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... },
  "message": "Login successful. Welcome, MFA Test User!"
}
```

**Validation Checklist:**
- ✅ Direct login allowed (MFA not required until setup)
- ✅ JWT token generated
- ✅ Token valid for 30 minutes

---

### Scenario 2: MFA Setup 📱

#### 2.1: Generate TOTP Secret and QR Code
```bash
curl -X POST http://localhost:8000/auth/mfa/setup \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5
  }'
```

**Expected Response:**
```json
{
  "setup_key": "JBSWY3DP...",
  "qr_code_url": "otpauth://totp/MoSPI%20Data%20Portal:mfatest%40example.com?secret=JBSWY3DP...&issuer=MoSPI%20Data%20Portal",
  "manual_entry_key": "JBSWY3DPEHPK3PXP",
  "message": "MFA setup started. Scan QR code with Microsoft Authenticator or enter manual key.",
  "setup_key": "JBSWY3DP..."
}
```

**Validation Checklist:**
- ✅ TOTP secret generated (32 characters, base32 encoded)
- ✅ QR code URL contains proper provisioning URI
- ✅ Issuer name is "MoSPI Data Portal"
- ✅ Email in QR code is correct
- ✅ Manual entry key provided for users unable to scan

#### 2.2: Add to Microsoft Authenticator App

**Steps:**
1. Open Microsoft Authenticator app
2. Tap "+"  → Add account
3. Choose "Other account"
4. Scan QR code OR paste manual entry key
5. Verify account appears as "MoSPI Data Portal"

**Expected Result:**
- 6-digit code refreshes every 30 seconds
- Code starts with current code (don't verify setup yet)

#### 2.3: Verify MFA Setup
```bash
curl -X POST http://localhost:8000/auth/mfa/verify \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5,
    "otp_code": "123456"  # Use current code from Microsoft Authenticator
  }'
```

**Expected Response:**
```json
{
  "message": "MFA enabled successfully. Save backup codes securely!",
  "backup_codes": [
    "BC001-A1B2C3D4",
    "BC002-E5F6G7H8",
    ...
  ]
}
```

**Validation Checklist:**
- ✅ TOTP code validated successfully
- ✅ User.totp_enabled set to True in database
- ✅ User.totp_secret stored securely
- ✅ Backup codes generated (10 codes)
- ✅ Database reflects MFA is now enabled

---

### Scenario 3: Login with MFA Enabled 🔒

#### 3.1: Initial Login Attempt
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "mfatestuser",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "detail": "MFA verification required",
  "status_code": 403
}
```

**Response Headers:**
```
X-MFA-Challenge: abc123def456ghi789...
X-MFA-Method: microsoft-authenticator
```

**Validation Checklist:**
- ✅ Status code is exactly 403 (Forbidden)
- ✅ Detail message indicates MFA required
- ✅ X-MFA-Challenge header present (contains challenge_id)
- ✅ X-MFA-Method header shows "microsoft-authenticator"
- ⚠️ NO JWT token issued yet
- ✅ OtpChallenge created in database with:
  - Challenge ID matching header
  - Sets to expire in 5 minutes
  - Purpose = LOGIN
  - user_id = 5
  - attempts = 0

#### 3.2: Get TOTP Code from Microsoft Authenticator
**Steps:**
1. Open Microsoft Authenticator app
2. Find "MoSPI Data Portal" entry
3. Note current 6-digit code
4. Code is valid for ~30 seconds
5. Next code appears when current starts fading

#### 3.3: Verify MFA Code Successfully
```bash
curl -X POST http://localhost:8000/auth/login/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "abc123def456ghi789...",
    "otp_code": "123456"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "email": "mfatest@example.com",
    "totp_enabled": true,
    ...
  },
  "message": "MFA verified successfully. Welcome, MFA Test User! 🎉"
}
```

**Validation Checklist:**
- ✅ Status code 200 (Success)
- ✅ JWT token generated
- ✅ User object includes totp_enabled = true
- ✅ Welcome message confirms success
- ✅ OtpChallenge marked as consumed
- ✅ consumed_at timestamp recorded
- ✅ Challenge not deleted (kept for audit log)

#### 3.4: Use JWT Token for Authenticated Request
```bash
curl -X GET http://localhost:8000/protected-endpoint \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Expected Response:**
- ✅ Request succeeds with token from MFA verification
- ✅ Token valid for 30 minutes from MFA completion

---

### Scenario 4: Invalid MFA Code 🚫

#### 4.1: Wrong Code (First Attempt)
```bash
curl -X POST http://localhost:8000/auth/login/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "abc123def456ghi789...",
    "otp_code": "999999"
  }'
```

**Expected Response:**
```json
{
  "detail": "Invalid MFA code. 4 attempts remaining.",
  "status_code": 401
}
```

**Validation Checklist:**
- ✅ Status code 401 (Unauthorized)
- ✅ Error message shows remaining attempts (4)
- ✅ OtpChallenge.attempts incremented to 1
- ⚠️ NO JWT token issued

#### 4.2: Wrong Code (Fifth Attempt - Max)
```bash
# After 4 failed attempts, try again
curl -X POST http://localhost:8000/auth/login/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "abc123def456ghi789...",
    "otp_code": "999999"
  }'
```

**Expected Response:**
```json
{
  "detail": "Maximum verification attempts exceeded. Please login again.",
  "status_code": 429
}
```

**Validation Checklist:**
- ✅ Status code 429 (Too Many Requests)
- ✅ Challenge deleted from database after max attempts
- ✅ User must re-login to get new challenge

---

### Scenario 5: Expired Challenge ⏱️

#### 5.1: Challenge Expires After 5 Minutes
```bash
# Wait 5+ minutes after initial login attempt
curl -X POST http://localhost:8000/auth/login/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "abc123def456ghi789...",
    "otp_code": "123456"
  }'
```

**Expected Response:**
```json
{
  "detail": "MFA challenge expired. Please login again.",
  "status_code": 401
}
```

**Validation Checklist:**
- ✅ Status code 401
- ✅ Challenge deleted from database
- ✅ User must re-login
- ✅ Current time > challenge.expires_at

---

### Scenario 6: TOTP Time Window Tolerance ⏲️

#### 6.1: Test 30-Second Window
**Setup:**
- Get current code from Microsoft Authenticator (e.g., 123456, ~25 seconds remaining)
- Wait for code to change (new code 654321, ~0 seconds old)

**Test 1: Submit last code shortly before it expires**
```bash
curl -X POST http://localhost:8000/auth/login/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "...",
    "otp_code": "123456"  # Code from previous 30-sec window
  }'
```

**Expected Result:**
- ✅ Code accepted (window tolerance = ±30 seconds)
- ✅ Login completes successfully

**Validation Checklist:**
- ✅ Codes near boundary are accepted
- ✅ TOTP validation uses `valid_window=1`
- ✅ Allows for minor device clock drift

---

### Scenario 7: Disable MFA 🔓

#### 7.1: Disable MFA for User
```bash
curl -X POST http://localhost:8000/auth/mfa/disable \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5,
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "message": "MFA disabled successfully. You can enable it again anytime.",
  "totp_enabled": false
}
```

**Validation Checklist:**
- ✅ Status code 200
- ✅ User.totp_enabled set to False in database
- ✅ User.totp_secret cleared (optional for recovery)
- ✅ Password verified before disabling

#### 7.2: Login Without MFA After Disabling
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "mfatestuser",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
- ✅ Direct JWT token issued
- ✅ No MFA challenge required
- ✅ Direct login works again

---

### Scenario 8: Database Audit Trail 📊

#### 8.1: Verify OtpChallenge Records
```python
# Connect to PostgreSQL and check challenges
SELECT * FROM otp_challenges WHERE purpose = 'LOGIN' ORDER BY created_at DESC;
```

**Expected Records Should Show:**
- ✅ challenge_id (unique, 64 char hex)
- ✅ purpose = 'LOGIN'
- ✅ email = 'mfatest@example.com'
- ✅ user_id = 5
- ✅ attempts = 0 (for successful), 5 (for max attempts), 1-4 (for partial failures)
- ✅ consumed = true (for completed challenges)
- ✅ consumed_at = timestamp (for completed challenges)
- ✅ expires_at = created_at + 5 minutes

#### 8.2: Verify User MFA Status in Database
```python
# Check user record
SELECT id, username, email, totp_enabled, totp_secret FROM users WHERE id = 5;
```

**Expected:**
- ✅ totp_enabled = true (after setup)
- ✅ totp_secret = 32-character base32 string (kept secure)
- ✅ Secret starts with valid base32 characters

---

## Automated Testing Script

### Python Test Suite
```python
import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class MFATestSuite:
    def __init__(self):
        self.base_url = BASE_URL
        self.user_data = {
            "email": f"mfatest{int(time.time())}@example.com",
            "username": f"mfatestuser{int(time.time())}",
            "password": "SecurePass123!",
            "full_name": "MFA Test User"
        }
        self.challenge_id = None
        self.access_token = None
        
    def test_register(self):
        """Test 1: User Registration"""
        print("\n[TEST 1] User Registration")
        response = requests.post(
            f"{self.base_url}/auth/register/verify",
            json=self.user_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json()["totp_enabled"] == False
        print("✅ User registered successfully (MFA not enabled)")
        
    def test_login_without_mfa(self):
        """Test 2: Login Without MFA Setup"""
        print("\n[TEST 2] Login Without MFA Setup")
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "username_or_email": self.user_data["username"],
                "password": self.user_data["password"]
            }
        )
        assert response.status_code == 200
        self.access_token = response.json()["access_token"]
        print(f"✅ Direct login successful (no MFA required)")
        
    def test_mfa_setup(self):
        """Test 3: MFA Setup"""
        print("\n[TEST 3] MFA Setup")
        # Get user ID from login
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "username_or_email": self.user_data["username"],
                "password": self.user_data["password"]
            }
        )
        user_id = response.json()["user"]["id"]
        
        # Generate TOTP
        response = requests.post(
            f"{self.base_url}/auth/mfa/setup",
            json={"user_id": user_id}
        )
        assert response.status_code == 200
        setup_data = response.json()
        assert "setup_key" in setup_data
        assert "qr_code_url" in setup_data
        print(f"✅ TOTP Setup Key: {setup_data['setup_key']}")
        
        # Store setup key for manual verification
        self.setup_key = setup_data["setup_key"]
        return setup_data
        
    def test_mfa_verify_setup_with_code(self, otp_code):
        """Test 4: Verify MFA Setup with TOTP Code"""
        print(f"\n[TEST 4] Verify MFA Setup (Code: {otp_code})")
        
        # Get user ID
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "username_or_email": self.user_data["username"],
                "password": self.user_data["password"]
            }
        )
        user_id = response.json()["user"]["id"]
        
        # Verify with code
        response = requests.post(
            f"{self.base_url}/auth/mfa/verify",
            json={"user_id": user_id, "otp_code": otp_code}
        )
        assert response.status_code == 200
        data = response.json()
        assert "backup_codes" in data
        print(f"✅ MFA verified successfully")
        print(f"   Backup codes: {len(data['backup_codes'])} codes generated")
        self.backup_codes = data["backup_codes"]
        
    def test_login_with_mfa(self, otp_code):
        """Test 5: Login with MFA Enabled"""
        print(f"\n[TEST 5] Login with MFA (Code: {otp_code})")
        
        # Initial login
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "username_or_email": self.user_data["username"],
                "password": self.user_data["password"]
            }
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        self.challenge_id = response.headers.get("X-MFA-Challenge")
        assert self.challenge_id, "MFA Challenge header missing"
        print(f"✅ MFA Challenge received: {self.challenge_id}")
        
        # Verify MFA
        response = requests.post(
            f"{self.base_url}/auth/login/verify-mfa",
            json={
                "challenge_id": self.challenge_id,
                "otp_code": otp_code
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["totp_enabled"] == True
        self.access_token = data["access_token"]
        print(f"✅ MFA verification successful")
        print(f"   Token issued: {self.access_token[:50]}...")
        
    def test_invalid_mfa_code(self):
        """Test 6: Invalid MFA Code"""
        print(f"\n[TEST 6] Invalid MFA Code")
        
        # Initial login
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "username_or_email": self.user_data["username"],
                "password": self.user_data["password"]
            }
        )
        challenge_id = response.headers.get("X-MFA-Challenge")
        
        # Try invalid code
        response = requests.post(
            f"{self.base_url}/auth/login/verify-mfa",
            json={
                "challenge_id": challenge_id,
                "otp_code": "999999"
            }
        )
        assert response.status_code == 401
        assert "attempts remaining" in response.json()["detail"]
        print(f"✅ Invalid code rejected properly")
        print(f"   Error: {response.json()['detail']}")

# Run tests
if __name__ == "__main__":
    print("\n" + "="*50)
    print("MFA AUTHENTICATION TEST SUITE")
    print("="*50)
    
    suite = MFATestSuite()
    
    try:
        suite.test_register()
        suite.test_login_without_mfa()
        setup_data = suite.test_mfa_setup()
        
        # MANUAL STEP: User needs to provide TOTP code from Microsoft Authenticator
        print("\n⚠️  Manual Step Required:")
        print(f"   1. Scan this QR code with Microsoft Authenticator:")
        print(f"      {setup_data['qr_code_url'][:80]}...")
        print(f"   2. Or manually enter: {setup_data['manual_entry_key']}")
        otp_code = input("   3. Enter the 6-digit code from Microsoft Authenticator: ")
        
        suite.test_mfa_verify_setup_with_code(otp_code)
        
        # Get next code
        otp_code = input("\n   Enter the next 6-digit code from Microsoft Authenticator: ")
        suite.test_login_with_mfa(otp_code)
        suite.test_invalid_mfa_code()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
```

---

## Manual Testing Checklist

- [ ] Register new user
- [ ] Login without MFA (should succeed immediately)
- [ ] Setup MFA (generate TOTP and QR code)
- [ ] Scan QR code with Microsoft Authenticator
- [ ] Verify MFA with valid code
- [ ] Receive backup codes
- [ ] Login with MFA enabled
- [ ] Receive MFA challenge on login
- [ ] Submit valid TOTP code
- [ ] Receive JWT token
- [ ] Try invalid TOTP code (fails on first attempt)
- [ ] Try 5 invalid codes (locked out)
- [ ] Re-login to get new challenge
- [ ] Test code near refresh boundary (still valid)
- [ ] Wait 5+ minutes and try expired challenge
- [ ] Disable MFA
- [ ] Verify login works without MFA again

---

## Monitoring and Logs

### Terminal Output Format
```
[AUTH] 🔐 User login attempt - Username: mfatestuser
[AUTH] ✅ Password verified for: mfatestuser
[MFA] 🔐 MFA verification attempt - Challenge: abc123def456...
[MFA] ✅ Valid TOTP code for user: mfatestuser
[MFA] ✅ JWT token generated after MFA verification for: mfatestuser
```

### Database Queries for Monitoring
```sql
-- Recent login attempts
SELECT * FROM otp_challenges 
WHERE purpose = 'LOGIN' 
ORDER BY created_at DESC 
LIMIT 10;

-- Failed MFA attempts
SELECT * FROM otp_challenges 
WHERE purpose = 'LOGIN' AND attempts > 0 
ORDER BY created_at DESC;

-- Users with MFA enabled
SELECT id, username, email, totp_enabled, created_at 
FROM users 
WHERE totp_enabled = true;

-- Active challenges (not yet consumed)
SELECT * FROM otp_challenges 
WHERE consumed = false AND expires_at > NOW();
```

---

## Performance Benchmarks

| Operation | Expected Time | Tolerance |
|-----------|--------------|-----------|
| User registration | < 100ms | ±50ms |
| MFA setup (TOTP generation) | < 50ms | ±25ms |
| Login without MFA | < 150ms | ±75ms |
| MFA code verification | < 100ms | ±50ms |
| JWT token generation | < 50ms | ±25ms |
| Database challenge creation | < 100ms | ±50ms |

---

## Related Documentation
- [MFA Setup Guide](MFA_SETUP_GUIDE.md) - Setting up MFA for new users
- [MFA Login Verification](MFA_LOGIN_VERIFICATION_GUIDE.md) - Verifying MFA codes
- [Back Codes Guide](MFA_BACKUP_CODES.md) - Account recovery
