# Microsoft Authenticator MFA - Quick Reference

## 🚀 5-Minute Setup

### What You Need:
- ✅ Server running (`./start.sh`)
- ✅ Microsoft Authenticator app installed
- ✅ Web browser

### The Process:

```
┌─────────────────────────────────────────────────────┐
│                  Step 1: REGISTER                    │
│                                                     │
│  1. Go to: http://127.0.0.1:8000/register          │
│  2. Fill form with your details                     │
│  3. See QR code on screen                           │
│  4. Scan QR with Microsoft Authenticator            │
│  5. 6-digit code appears in app                     │
│  6. Enter code in browser → REGISTER COMPLETE       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                   Step 2: LOGIN                      │
│                                                     │
│  1. Go to: http://127.0.0.1:8000/login             │
│  2. Enter username + password                       │
│  3. Browser asks for authenticator code             │
│  4. Open Microsoft Authenticator app                │
│  5. Copy 6-digit code                               │
│  6. Paste code in browser → LOGGED IN               │
└─────────────────────────────────────────────────────┘
```

---

## 🔑 Key Points

### Microsoft Authenticator Setup:
1. **When adding account**:
   - Choose: "Other account" (not Work/School)
   - Choose: Scan QR code

2. **What you'll see**:
   - Account name: `your_email@example.com`
   - Blue 6-digit code (changes every 30 sec)
   - Account under "MoSPI DPI"

3. **Using the code**:
   - Valid for ~30 seconds
   - Copy before it expires
   - New code appears when expiring

### Time Sync Important:
- Your phone clock must be accurate
- Go to Settings > Date & Time > Auto-sync ON
- If codes don't work, sync time first

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| QR code not showing | Refresh page / Use manual entry key |
| Code rejected | Wait for new code / Check phone time |
| "Not configured" error | Complete registration fully |
| Account not in app | Select "Other account" not "Work account" |
| Same code rejected twice | Must wait for new code (30 sec) |

---

## 🧪 Test Commands

```bash
# Register & login via API
python verify_mfa_system.py --interactive

# Or use cURL:
curl -X POST http://localhost:8000/api/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePass123!"
  }'
```

---

## 📱 Adding Second Device

1. During registration, **write down the setup key** (or save QR image)
2. On second device:
   - Open Microsoft Authenticator
   - Tap "+"
   - Select "Can't scan? Enter setup details"
   - Paste setup key
   - Both devices now show same code

---

## ✅ Verify It's Working

After setup, you should be able to:
- [ ] See 6-digit code in Microsoft Authenticator
- [ ] Code refreshes every 30 seconds
- [ ] Register successfully with code
- [ ] Login successfully with code
- [ ] Invalid code (999999) is rejected

---

## 🆘 If Still Not Working

Run the verification script:
```bash
python verify_mfa_system.py --verify
```

Check these:
1. Server is running: http://127.0.0.1:8000/health
2. Database connected: Check logs
3. TOTP library installed: Already included
4. Microsoft Authenticator: Version 6.x+

---

**Quick URL Reference**:
- 🏠 Home: http://127.0.0.1:8000/
- 📝 Register: http://127.0.0.1:8000/register
- 🔐 Login: http://127.0.0.1:8000/login
- 📊 Dashboard: http://127.0.0.1:8000/dashboard (after login)
- 🛠️ Admin: http://127.0.0.1:8000/admin
- 📖 API Docs: http://127.0.0.1:8000/docs

---

**Support**: Check `MICROSOFT_AUTHENTICATOR_SETUP.md` for detailed guide
