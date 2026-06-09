# ✅ Microsoft Authenticator Setup Guide - STATAHON PROJECT

## 🎯 Quick Start (5 minutes)

### Step 1: Start Your App
```bash
cd "/Users/arunsudhaveni/Desktop/STATAHON PROJECT"
./start.sh
# Or: python3.13 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

✅ You should see: `Uvicorn running on http://127.0.0.1:8000`

---

### Step 2: Install Microsoft Authenticator
- 📱 **iOS**: Download from [Apple App Store](https://apps.apple.com/us/app/microsoft-authenticator/id983156458)
- 📱 **Android**: Download from [Google Play Store](https://play.google.com/store/apps/details?id=com.azure.authenticator)
- 💻 **Windows/Mac**: Download from [Microsoft website](https://www.microsoft.com/en-us/account/authenticator)

---

### Step 3: Register Your First User

**Option A: Using Browser (Recommended)**

1. Go to: http://127.0.0.1:8000/register
2. Fill in the form:
   - Full Name: `Your Name`
   - Email: `your_email@example.com`
   - Username: `your_username`
   - Password: `SecurePass123!`
3. Click "Register"
4. **IMPORTANT**: You'll see a **QR Code** appear on screen

**Option B: Using cURL**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePass123!"
  }'
```

Expected response includes:
- `challenge_id` 
- `otpauth_url` (contains QR code data)
- `setup_key` (manual entry option)

---

### Step 4: Scan QR Code with Microsoft Authenticator

1. Open **Microsoft Authenticator** app
2. Tap **"+"** (Add Account)
3. Select **"Other account (Google, Facebook, etc.)"**
4. Choose **"Can't scan it? Enter setup details manually"** OR **Scan QR code**
   - If scanning: Point camera at QR code shown on registration page
   - If manual: Enter the `setup_key` shown on screen

5. Account setup window shows:
   - Account: `your_email@example.com`
   - Key: (hidden dots)
   - Click **Save**

✅ **Success**: You should now see a 6-digit code that changes every 30 seconds

---

### Step 5: Complete Registration

1. Your Microsoft Authenticator now shows a **6-digit TOTP code** ✅
2. Back on registration page, enter this code
3. Click "Verify Authentication Code"
4. **✅ Registration Complete!**

You'll see: `"User registered successfully"`

---

### Step 6: Login with Microsoft Authenticator

Now use your credentials to login:

1. Go to: http://127.0.0.1:8000/login
2. Enter:
   - Username: `your_username`
   - Password: `SecurePass123!`
3. Click "Login"
4. You'll see: **"Enter your Microsoft Authenticator code"**
5. Open Microsoft Authenticator app
6. Copy the **6-digit code** (it changes every 30 seconds)
7. Paste into login form
8. Click "Verify"

✅ **Success**: You're now logged in!

---

## 🔍 Troubleshooting

### ❌ Problem: QR Code Not Showing

**Solution:**
1. Check browser console (F12) for errors
2. Try cURL command to see if QR code data is in response
3. Refresh page and try again
4. Use manual entry option instead of QR code

### ❌ Problem: "Invalid authenticator code"

**Possible Causes:**
1. **Time Sync Issue**: Your phone's clock is off
   - Fix: Go to Settings > Date & Time > Auto-sync

2. **Wrong Code**: Code expired (only valid for ~30 seconds)
   - Fix: Wait for new code to appear, then submit

3. **Code Already Used**: You submitted the same code twice
   - Fix: Wait for next code to appear

### ❌ Problem: Account Not Appearing in Microsoft Authenticator

**Solution:**
1. Make sure you selected **"Other account"** (NOT "Work or school account")
2. Check that account name shows correctly
3. Try adding manually instead of scanning QR code
4. Delete and re-add the account

### ❌ Problem: "Authenticator not configured"

**Solution:**
1. Make sure you completed the registration AND Authenticator verification steps
2. Check that 6-digit code is successfully generated in Authenticator app
3. The system requires MFA - no way to login without it

---

## 📱 Microsoft Authenticator Features

### Code Display
- Shows **6-digit code** that changes every 30 seconds
- Codes are **blue** (valid) → **gray** (about to expire) → **refreshes**
- Account shows app name: "MoSPI DPI"

### Best Practices
✅ Enable **PIN or biometric** lock on app for security  
✅ Backup your phone or use multiple devices  
✅ Save backup codes (shown after first login)  
✅ Keep phone's time synchronized  

---

## 🧪 Testing the MFA System

### Test Case 1: Successful Registration & Login
```bash
# 1. Start registration
curl -X POST http://localhost:8000/api/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mfa_test@example.com",
    "username": "mfa_testuser",
    "full_name": "MFA Test User",
    "password": "SecurePass123!",
    "role": "PUBLIC"
  }' | jq .

# 2. Get TOTP code from Microsoft Authenticator
# (Copy 6-digit code from app)

# 3. Get challenge_id from response, then verify:
curl -X POST http://localhost:8000/api/v1/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "PASTE_CHALLENGE_ID_HERE",
    "otp": "PASTE_6_DIGIT_CODE_HERE"
  }' | jq .

# 4. Login start
curl -X POST http://localhost:8000/api/v1/auth/login/start \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mfa_testuser",
    "password": "SecurePass123!"
  }' | jq .

# 5. Get new code from Authenticator, then verify login
curl -X POST http://localhost:8000/api/v1/auth/login/verify \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "PASTE_NEW_CHALLENGE_ID",
    "otp": "PASTE_NEW_6_DIGIT_CODE"
  }' | jq .
```

Expected: `"access_token"` returned ✅

### Test Case 2: Wrong Code (Should Fail)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/verify \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "CHALLENGE_ID",
    "otp": "999999"
  }' | jq .
```

Expected: `"Invalid authenticator code"` ✅

---

## 🛠️ Manual Setup (If QR Code Method Fails)

### Using Manual Entry Instead of QR Code:

1. Open Microsoft Authenticator app
2. Tap **"+"**
3. Select **"Other account"**
4. Select **"Can't scan it? Enter setup details manually"**
5. Fill in:
   - **Account name**: `your_email@example.com`
   - **Key**: `PASTE_SETUP_KEY_FROM_REGISTRATION_PAGE`
   - **Time-based**: Toggle ON ✅
6. Tap **Save**

✅ Code should appear within 5 seconds

---

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STATAHON MFA System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Registration Flow:                                         │
│  ├─ Enter credentials → Generate TOTP Secret                │
│  ├─ Display QR Code (or setup key)                          │
│  ├─ Scan with Microsoft Authenticator                       │
│  ├─ Submit 6-digit code                                     │
│  └─ Account Created ✅                                      │
│                                                              │
│  Login Flow:                                                │
│  ├─ Enter username/password                                 │
│  ├─ System requests authenticator code ("MFA Challenge")    │
│  ├─ Open Microsoft Authenticator → Copy 6-digit code       │
│  ├─ Submit code                                             │
│  └─ JWT Token Issued ✅                                     │
│                                                              │
│  Security Features:                                         │
│  ├─ Time-based codes (30-second window)                     │
│  ├─ Rate limiting (5 attempts per challenge)                │
│  ├─ Challenge expiration (5 minutes)                        │
│  ├─ Code one-time use (consumed after verification)         │
│  └─ Password hashing (bcrypt)                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Verification Checklist

- [ ] App is running on http://127.0.0.1:8000
- [ ] Microsoft Authenticator app is installed
- [ ] Registration page loads at http://127.0.0.1:8000/register
- [ ] QR code displays (or setup key is visible)
- [ ] Account added to Microsoft Authenticator
- [ ] 6-digit code appears in app
- [ ] Registration verification succeeds
- [ ] Login page loads at http://127.0.0.1:8000/login
- [ ] Login challenge requires authenticator code
- [ ] Code verification succeeds
- [ ] Logged-in dashboard appears

---

## 🔗 Useful Links

- Microsoft Authenticator Help: https://support.microsoft.com/en-us/account-billing/authenticator-help
- TOTP Standard: https://tools.ietf.org/html/rfc6238
- Your API Docs: http://127.0.0.1:8000/docs
- Your ReDoc: http://127.0.0.1:8000/redoc

---

## 💡 Next Steps

1. **Register a test account** ✅
2. **Setup Microsoft Authenticator** ✅
3. **Test login/logout cycle** ✅
4. **Share credentials with team** ✅
5. **Monitor logs** for any issues ✅

---

## 📞 Need Help?

Check the project files:
- `MFA_TESTING_GUIDE.md` - Detailed test scenarios
- `COMPLETE_AUTH_SUMMARY.md` - Full auth documentation
- `app/api/auth.py` - Authentication code
- `app/models/user.py` - User & MFA database models

---

**Last Updated**: March 25, 2026  
**Status**: ✅ Production Ready
