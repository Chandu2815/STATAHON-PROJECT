"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Assign credits based on role
    credits_by_role = {
        "public": 10.0,
        "researcher": 100.0,
        "premium": 500.0,
        "admin": 999999.0  # Unlimited
    }
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        password=user_data.password,  # Store plain password for admin viewing
        role=user_data.role,
        credits=credits_by_role.get(user_data.role.value if hasattr(user_data.role, 'value') else user_data.role, 10.0)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token with user role"""
    
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Handle role - could be enum or string
    user_role = user.role.value if hasattr(user.role, 'value') else user.role
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_role": user_role,
        "username": user.username
    }


@router.get("/reset-admin-password")
def reset_admin_password(db: Session = Depends(get_db)):
    """Reset admin password to default (temporary endpoint for setup)"""
    from app.models.user import UserRole
    
    # Find admin user
    admin = db.query(User).filter(User.username == "admin").first()
    
    if not admin:
        # Create new admin
        admin = User(
            username="admin",
            email="admin@mospi.gov.in",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            password="admin123",
            role=UserRole.ADMIN,
            is_active=True,
            credits=999999.0
        )
        db.add(admin)
        db.commit()
        return {"message": "Admin created", "username": "admin", "password": "admin123"}
    
    # Reset password
    admin.hashed_password = get_password_hash("admin123")
    admin.password = "admin123"
    admin.is_active = True
    db.commit()
    
    return {"message": "Admin password reset", "username": "admin", "password": "admin123"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
