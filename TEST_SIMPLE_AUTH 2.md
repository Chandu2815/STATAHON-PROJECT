# Simple Authentication System - Testing Guide

## Overview
The FastAPI backend now includes simple registration and login endpoints without requiring OTP verification.

## Architecture

### Database Setup
- **Tables**: Automatically created on server startup via `Base.metadata.create_all(bind=engine)`
- **Users Table**: Contains id, email, username, hashed_password, full_name, and other fields
- **Connection**: PostgreSQL with SQLAlchemy ORM
- **Error Handling**: All database errors are printed to terminal logs for debugging

### Registration Endpoint

**Endpoint:** `POST /api/v1/auth/register/verify`

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character

**Success Response (201 Created):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "public",
  "is_active": true,
  "credits": 10.0,
  "created_at": "2025-03-25T10:30:00Z",
  "password": "SecurePass123!"
}
```

**Error Responses:**
- `400 Bad Request` - Email or username already registered
- `500 Internal Server Error` - Database error (details printed in terminal)

### Login Endpoint

**Endpoint:** `POST /api/v1/auth/login`

**Request Body (Option 1 - Username):**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Request Body (Option 2 - Email):**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "role": "public",
    "is_active": true,
    "credits": 10.0,
    "created_at": "2025-03-25T10:30:00Z"
  },
  "message": "Login successful. Welcome, John Doe!"
}
```

**Error Responses:**
- `400 Bad Request` - Username or email not provided
- `401 Unauthorized` - Invalid username/password
- `403 Forbidden` - User account is inactive
- `500 Internal Server Error` - Database error (details printed in terminal)

## Database Configuration (database.py)

```python
# Engine Creation
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"connect_timeout": 10}
)

# Session Management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for Models
Base = declarative_base()

# Auto-create tables
Base.metadata.create_all(bind=engine)
```

## User Model (models.py)

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.PUBLIC, nullable=False)
    is_active = Column(Boolean, default=True)
    credits = Column(Float, default=10.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## Error Handling & Debugging

### Terminal Logs
All operations print debug information:

```
[SIMPLE-AUTH] Registering user: johndoe (john@example.com)
[SIMPLE-AUTH] Password hashed successfully
[SIMPLE-AUTH] ✅ User created successfully: johndoe (ID: 1)

[SIMPLE-AUTH] Login attempt: johndoe
[SIMPLE-AUTH] ✅ JWT token generated for user: johndoe

[SIMPLE-AUTH] ❌ Login failed: user not found (nonexistent)
[SIMPLE-AUTH] ❌ Database error: {error details}
[SIMPLE-AUTH] Exception type: {exception type}
```

### Error Levels
- `✅` - Success
- `❌` - Error
- `→` - Progress indicator

### Database Errors
- All SQLAlchemy errors are caught and printed
- Exception types and stack traces are logged
- User receives appropriate HTTP error codes
- No 500 errors crash the server

## Testing with curl

### Register New User
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

### Use JWT Token
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

## Security Features

1. **Password Hashing**: bcrypt with salting
2. **Duplicate Prevention**: Unique email and username constraints
3. **JWT Tokens**: 30-minute expiration (configurable)
4. **Active User Check**: Inactive accounts cannot login
5. **Role-Based Access**: Default PUBLIC role with configurable credits

## Technology Stack

- **Framework**: FastAPI 0.115.6+
- **Database**: PostgreSQL with SQLAlchemy 2.0.36+
- **Authentication**: bcrypt for hashing, python-jose for JWT
- **Server**: Uvicorn with ASGI support
- **Validation**: Pydantic with EmailStr

## Files Modified

1. **app/database.py** - Engine, SessionLocal, Base configured
2. **app/models/user.py** - User model with required fields
3. **app/schemas/user.py** - Request/response schemas
4. **app/api/auth.py** - Simple registration and login endpoints
5. **app/main.py** - Startup event calls init_db()

## Configuration

### Environment Variables (.env)
```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-for-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
```

### Startup
- Tables created automatically when server starts
- Default admin/testuser created on first run (optional, via init_db)
- All errors logged to terminal

## Running the Server

```bash
cd /path/to/project
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access API documentation: `http://localhost:8000/docs`
