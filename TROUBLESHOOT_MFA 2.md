showi# Microsoft Authenticator - Troubleshooting & Debug Guide

## 🔍 Diagnosis Flowchart

```
Is Microsoft Authenticator installed?
├─ NO → Download from App Store / Google Play
└─ YES → Continue ↓

Is server running?
├─ NO → Run: ./start.sh
└─ YES → Check: http://127.0.0.1:8000 (should show home page) ↓

Can you see registration page?
├─ NO → Server not responding. Check logs
└─ YES → Continue ↓

Does QR code appear?
├─ NO → See "5.1 QR Code Not Displaying" section below
└─ YES → Continue ↓

Can you add account to Authenticator?
├─ NO → See "5.2 Account Won't Add" section
└─ YES → Continue ↓

Does 6-digit code appear?
├─ NO → See "5.3 No Code Appearing" section
└─ YES → Continue ↓

Can you register successfully?
├─ NO → See "5.4 Registration Failed" section
└─ YES → Continue ↓

Can you login successfully?
├─ NO → See "5.5 Login Failed" section
└─ YES → ✅ SUCCESS! MFA is working
```

---

## 🛠️ Step-by-Step Troubleshooting

### Check 1: Server Health

**Problem**: "Cannot connect to server"

**Solution**:

```bash
# Check if server is running
curl http://127.0.0.1:8000/health

# Should return:
# {"status":"healthy","message":"Survey AI API is running"}

# If not, start it:
cd "/Users/arunsudhaveni/Desktop/STATAHON PROJECT"
./start.sh

# Check logs for errors
# You should see: "Uvicorn running on http://127.0.0.1:8000"
```

**Debug**:
```bash
# Check port 8000 is in use
lsof -i :8000

# If port is in use by something else:
kill -9 <PID>
./start.sh
```

---

### Check 2: Database Connection

**Problem**: "Database connection failed"

**Solution**:

```bash
# Check PostgreSQL is running
pg_isready -h 127.0.0.1 -p 5432

# Should return: accepting connections

# If not running:
# Start PostgreSQL (depends on your setup)
brew services start postgresql  # macOS
sudo service postgresql start   # Linux
```

**Debug**:
```bash
# Test database connection
python3 << 'EOF'
import psycopg2
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="survey_db",
        user="postgres",
        password="1234"
    )
    print("✅ Database connected successfully")
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
EOF
```

**Check environment variables** (.env file):
```bash
cat /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/.env

# Should have:
# DB_HOST=127.0.0.1
# DB_PORT=5432
# DB_NAME=survey_db
# DB_USER=postgres
# DB_PASSWORD=1234
```

---

### Check 3: TOTP Library Installed

**Problem**: "ModuleNotFoundError: No module named 'pyotp'"

**Solution**:

```bash
# Activate virtual environment
source /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/.venv/bin/activate

# Install required packages
pip install pyotp qrcode

# Verify
python3 -c "import pyotp; print('✅ pyotp installed')"
```

**Check requirements.txt**:
```bash
cat /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT/requirements.txt | grep -i "pyotp\|qr"
```

---

### Check 4: Microsoft Authenticator Setup

**Problem**: "QR code won't scan"

**What to check**:
1. Lighting is good (QR code is clearly visible)
2. Camera lens is clean
3. Hold phone steady for 2-3 seconds
4. Try closer/farther distance

**Alternative - Manual Entry**:
1. On registration page, look for: "Can't scan? Enter manually"
2. Copy the **setup key** (looks like: `JBSWY3DPEHPK3PXP`)
3. In Authenticator app:
   - Tap "+"
   - Select "Other account"
   - Select "Can't scan it?"
   - Paste key
   - Toggle "Time-based" ON
   - Save

---

### Check 5: Detailed Troubleshooting

#### 5.1: QR Code Not Displaying

**Browser console errors?**
```bash
# Open Developer Tools (F12 or Cmd+Option+I)
# Go to Console tab
# Look for red errors
```

**Check API response directly**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser123",
    "full_name": "Test User",
    "password": "SecurePass123!"
  }' | jq .otpauth_url
```

**Should see long URL starting with `otpauth://totp/`**

If not:
- Check server logs for errors
- Verify pyotp is installed
- Try refreshing page

---

#### 5.2: Account Won't Add to Authenticator

**Wrong account type selected?**
- ✅ Correct: "Other account" or "Google/Facebook"
- ❌ Wrong: "Work or school account"

**Setup key format wrong?**
```bash
# Valid key format (base32):
# 26-32 characters, letters A-Z and digits 2-7 only
# Example: JBSWY3DPEHPK3PXP

# Our system generates this format, should work
```

**Try deleting and re-adding**:
1. In Authenticator, swipe left on account
2. Tap "Delete"
3. Try adding again

---

#### 5.3: No Code Appearing in Authenticator

**Time sync issue**:
```bash
# Check your phone's time
# Settings > Date & Time > Should show current time

# Enable Auto-sync:
# iOS: Settings > General > Date & Time > Set Automatically ON
# Android: Settings > Date & Time > Automatic date & time ON
```

**Account added but no code?**
- Wait 10 seconds after adding
- Swipe up/down to refresh
- Try closing and reopening app
- Restart phone

**Verify time via terminal**:
```bash
# Check system time
date

# If off, adjust:
# macOS: System Preferences > Date & Time > Set time automatically
```

---

#### 5.4: Registration Failed

**"User already registered"**:
```bash
# Try different email/username (add timestamp)
# Example: test_1234567890@example.com
```

**"Invalid OTP code"**:
1. Code expired (only valid ~30 seconds)
   - Wait for new code in Authenticator
   - Code changes when previous fades to gray
   
2. Clock sync issue
   - Check phone time
   - Enable auto-sync

3. Wrong code entered
   - Double-check you copied correctly
   - No spaces at start/end

**"MFA not configured"**:
- Account must be added to Authenticator BEFORE submitting code
- If submitted too early, start over

---

#### 5.5: Login Failed

**"Incorrect username or password"**:
```bash
# Make sure exact credentials used
# Usernames are case-sensitive
# Check CAPS LOCK
```

**"Authenticator not configured"**:
```bash
# User was created but authenticator didn't complete setup
# Solution: Create new test account and complete full flow
```

**"MFA verification required" but no code works**:
1. Time sync (87% of MFA issues)
   - Check phone time is accurate
   - Enable auto-sync

2. Code expired
   - Must enter within 30 seconds
   - Get fresh code from Authenticator
   - New code appears when previous fades

3. Used same code twice
   - Each code can only be used once
   - Wait for next code (30 seconds)

---

## 🧪 Manual Testing with cURL

### Complete Flow (Copy & Paste):

```bash
#!/bin/bash

BASE="http://localhost:8000/api/v1"
EMAIL="test_$(date +%s)@example.com"
USER="test_$(date +%s)"
PASS="SecurePass123!"

echo "📝 1. Starting registration..."
REG_RESP=$(curl -s -X POST $BASE/auth/register/start \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"username\": \"$USER\",
    \"full_name\": \"Test User\",
    \"password\": \"$PASS\",
    \"role\": \"PUBLIC\"
  }")

echo $REG_RESP | jq .

CHALLENGE=$(echo $REG_RESP | jq -r '.challenge_id')
SETUP_KEY=$(echo $REG_RESP | jq -r '.setup_key')

echo ""
echo "Challenge ID: $CHALLENGE"
echo "Setup Key: $SETUP_KEY"
echo ""
echo "📱 2. Scanning QR or entering setup key in Microsoft Authenticator..."
echo "   Waiting for you to add account... (give app 5 seconds)"
read -p "Press ENTER when you see 6-digit code in Authenticator app"

echo ""
echo "3️⃣ Enter the 6-digit code from Authenticator:"
read -p "Enter code: " OTP

echo ""
echo "✅ 4. Verifying registration..."
VER_RESP=$(curl -s -X POST $BASE/auth/register/verify \
  -H "Content-Type: application/json" \
  -d "{
    \"challenge_id\": \"$CHALLENGE\",
    \"otp\": \"$OTP\"
  }")

echo $VER_RESP | jq .

# Check if successful
if echo $VER_RESP | jq -e '.id' > /dev/null; then
  echo "✅ Registration successful!"
  
  echo ""
  read -p "Press ENTER to test login..."
  
  echo "🔐 5. Starting login..."
  LOGIN_RESP=$(curl -s -X POST $BASE/auth/login/start \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"$USER\",
      \"password\": \"$PASS\"
    }")
  
  echo $LOGIN_RESP | jq .
  
  CHALLENGE=$(echo $LOGIN_RESP | jq -r '.challenge_id')
  
  echo ""
  echo "6️⃣ Enter NEW 6-digit code from Authenticator:(wait for code to refresh)"
  read -p "Enter code: " OTP
  
  echo ""
  echo "7️⃣ Verifying login..."
  curl -s -X POST $BASE/auth/login/verify \
    -H "Content-Type: application/json" \
    -d "{
      \"challenge_id\": \"$CHALLENGE\",
      \"otp\": \"$OTP\"
    }" | jq .
  
  echo ""
  echo "✅ Full flow complete!"
fi
```

Save as `test_mfa.sh`, then:
```bash
chmod +x test_mfa.sh
./test_mfa.sh
```

---

## 📊 Check Logs

### Server Logs:
```bash
# If running in terminal, look for:
# - "User registered successfully"
# - "MFA setup started"
# - "MFA verified successfully"

# Or check if running from script:
tail -f /var/log/statahon.log  # if configured
```

### Database Audit:
```bash
# Connect to PostgreSQL
psql -U postgres -d survey_db

# Check recent users
SELECT username, email, totp_enabled, created_at FROM "user" ORDER BY created_at DESC LIMIT 5;

# Check MFA challenges
SELECT challenge_id, purpose, email, consumed, attempts FROM otp_challenges ORDER BY created_at DESC LIMIT 5;
```

---

## 🆘 When All Else Fails

### Nuclear Option - Reset Everything:

```bash
# 1. Delete test user data (if needed)
# 2. Stop server (Ctrl+C)
# 3. Clear browser cache (Cmd+Shift+Delete)
# 4. Restart server:
./start.sh
# 5. Try again

# 6. If still fails, reinstall Microsoft Authenticator
# - Delete app
# - Restart phone
# - Reinstall from App Store
# - Try again
```

### Create Debug Report:

```bash
python verify_mfa_system.py --verify

# This will:
# ✅ Check server is running
# ✅ Check database connection
# ✅ Check TOTP library
# ✅ Report any issues found
```

---

## 📞 Still Having Issues?

1. **Check the detailed setup guide**:
   - `MICROSOFT_AUTHENTICATOR_SETUP.md`

2. **Run verification script**:
   - `python verify_mfa_system.py --verify`

3. **Review the test guide**:
   - `MFA_TESTING_GUIDE.md`

4. **Check server logs**:
   - Look for error messages and stack traces

5. **Check browser developer tools** (F12):
   - Console tab for JavaScript errors
   - Network tab to see API responses

---

## ✅ What Should Work

After proper setup:

| Task | Expected Result |
|------|-----------------|
| See QR code on register | ✅ Blue QR code visible |
| Scan with Authenticator | ✅ 6-digit blue code appears |
| Enter code to register | ✅ "User registered successfully" |
| Login with credentials | ✅ "Enter authenticator code" |
| Submit login code | ✅ Redirect to dashboard |
| Wrong code (999999) | ✅ Rejected with error |
| Same code twice | ✅ Second attempt fails |
| Code after 30 sec | ✅ Rejected as expired |

---

**Last Updated**: March 25, 2026  
**Version**: 1.0.1
