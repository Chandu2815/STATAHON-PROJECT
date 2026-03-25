# 🚀 FastAPI Authentication - Quick Reference Card

## Endpoints Summary

### 1. Register New User
```
POST /api/v1/auth/register/verify
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "username": "johndoe",
  "password": "SecurePass123!"
}

✅ 201 Created - User registered successfully
❌ 400 Bad Request - Email/username already taken
❌ 500 Internal Server Error - Database error (logged)
```

### 2. Login & Get JWT Token
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "johndoe",     # OR use email
  "password": "SecurePass123!"
}

✅ 200 OK - Returns JWT token + user info
❌ 401 Unauthorized - Invalid credentials
❌ 403 Forbidden - User account inactive
❌ 500 Internal Server Error - Database error (logged)
```

### 3. Access Protected Endpoint
```
GET /api/v1/auth/me
Authorization: Bearer <JWT_TOKEN>

✅ 200 OK - Returns current user info
❌ 401 Unauthorized - Invalid/expired token
```

---

## curl Examples

### Register
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Alice Smith",
    "email": "alice@example.com",
    "username": "alice_smith",
    "password": "MyPassword123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_smith",
    "password": "MyPassword123!"
  }'
```

### Login with Email
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "MyPassword123!"
  }'
```

### Use Token
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Response Examples

### Successful Registration (201)
```json
{
  "id": 42,
  "email": "alice@example.com",
  "username": "alice_smith",
  "full_name": "Alice Smith",
  "role": "public",
  "is_active": true,
  "credits": 10.0,
  "created_at": "2025-03-25T10:30:00Z"
}
```

### Successful Login (200)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 42,
    "email": "alice@example.com",
    "username": "alice_smith",
    "full_name": "Alice Smith",
    "role": "public",
    "is_active": true,
    "credits": 10.0,
    "created_at": "2025-03-25T10:30:00Z"
  },
  "message": "Login successful. Welcome, Alice Smith!"
}
```

### Error Response (400)
```json
{
  "detail": "Email already registered"
}
```

---

## Password Requirements

✅ Minimum 8 characters
✅ At least 1 UPPERCASE letter (A-Z)
✅ At least 1 number (0-9)
✅ At least 1 special character (!@#$%^&*)

### Valid Passwords
- `SecurePass123!`
- `MyP@ssw0rd`
- `Test#Pass99`

### Invalid Passwords
- `password` - no uppercase, no number, no special char
- `Simple1` - no uppercase, no special char
- `UPPERCASE1!` - all uppercase
- `short1!` - only 7 chars

---

## Token Usage

### How JWT Tokens Work
1. Login → Server returns JWT token
2. Store token in frontend (localStorage, sessionStorage, or cookie)
3. Send token in Authorization header for each request
4. Server validates token and processes request
5. Token expires in 30 minutes (configurable)

### Header Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Contents (encoded)
```json
{
  "sub": "johndoe",      // username
  "exp": 1711352600,     // expiration timestamp
  "iat": 1711350800      // issued at timestamp
}
```

---

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 201 | User created successfully | Registration complete |
| 200 | Login successful | Use token for requests |
| 400 | Bad request / Duplicate | Check email/username availability |
| 401 | Invalid credentials | Verify username/password |
| 403 | Account inactive | Contact support |
| 500 | Server error | Check terminal logs [SIMPLE-AUTH] |

---

## Terminal Logs

### Successful Operations
```
[SIMPLE-AUTH] Registering user: johndoe (john@example.com)
[SIMPLE-AUTH] Password hashed successfully
[SIMPLE-AUTH] ✅ User created successfully: johndoe (ID: 1)

[SIMPLE-AUTH] Login attempt: johndoe
[SIMPLE-AUTH] ✅ JWT token generated for user: johndoe
```

### Error Operations
```
[SIMPLE-AUTH] ❌ Registration failed: Email already registered
[SIMPLE-AUTH] ❌ Login failed: user not found (invalid_user)
[SIMPLE-AUTH] ❌ Login failed: incorrect password for johndoe
[SIMPLE-AUTH] ❌ Database error: IntegrityError...
[SIMPLE-AUTH] Exception type: SQLAlchemy IntegrityError
```

---

## Files Modified

| File | Changes |
|------|---------|
| `app/api/auth.py` | ✅ Added /register/verify and /login endpoints |
| `app/database.py` | ✅ Already configured (no changes needed) |
| `app/models/user.py` | ✅ Already has User model (no changes needed) |
| `app/schemas/user.py` | ✅ Already has schemas (no changes needed) |
| `app/main.py` | ✅ Already calls init_db() (no changes needed) |

---

## Common Tasks

### Reset Admin Password
```bash
curl -X GET http://localhost:8000/api/v1/auth/reset-admin-password
```
Returns: username="admin", password="admin123"

### Check API Documentation
```
http://localhost:8000/docs
```
Interactive Swagger UI for all endpoints

### View Database
```bash
# Connect to PostgreSQL
psql -U user -d mospi_db

# List tables
\dt

# Check users
SELECT id, username, email, role FROM users;
```

---

## Quick Start (2 minutes)

```bash
# 1. Start server
cd /Users/arunsudhaveni/Desktop/STATAHON\ PROJECT
source .venv/bin/activate
python -m uvicorn app.main:app --reload

# 2. Register user (in another terminal)
curl -X POST http://localhost:8000/api/v1/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test","email":"test@test.com","username":"test","password":"Test123!"}'

# 3. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123!"}'

# Done! ✅
```

---

## Security Checklist

- ✅ Passwords hashed with bcrypt (never stored plain)
- ✅ JWT tokens signed with SECRET_KEY
- ✅ Tokens expire after 30 minutes
- ✅ Duplicate email/username prevented
- ✅ Inactive users cannot login
- ✅ All errors caught (no 500 crashes)
- ✅ Database errors logged (no exposure)
- ✅ HTTPS ready (configure in production)

---

## Troubleshooting

### "Email already registered"
- The email is already in use
- Use a different email or reset password

### "Invalid username or password"
- Check username/email spelling
- Verify password (case-sensitive)
- Try with email instead of username

### "Token expired"
- Login again to get new token
- Tokens valid for 30 minutes

### "SQLAlchemy IntegrityError" in logs
- Duplicate email/username detected
- Check database for existing user

### "Connection refused" to PostgreSQL
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Check credentials

---

## Next Steps

1. **Integrate Frontend** - Use JWT tokens in API calls
2. **Add Password Reset** - Email-based password recovery
3. **Email Verification** - Verify user email before login
4. **Rate Limiting** - Prevent brute force attacks
5. **HTTPS Setup** - Enable SSL/TLS for production
6. **Persistent Logging** - Log to file instead of console

---

**Ready to build?** Start your server and create users! 🚀
