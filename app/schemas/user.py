"""
Pydantic schemas for users and authentication
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = UserRole.PUBLIC


class UserUpdate(BaseModel):
    """Schema for updating user"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: UserRole
    is_active: bool
    credits: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload schema"""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


class UsageStatsResponse(BaseModel):
    """Usage statistics response"""
    user_id: int
    total_requests: int
    requests_today: int
    total_data_transferred_mb: float
    credits_remaining: float
    last_request: Optional[datetime] = None


class TransactionCreate(BaseModel):
    """Transaction creation schema"""
    amount: float = Field(..., gt=0)
    transaction_type: str


class TransactionResponse(BaseModel):
    """Transaction response schema"""
    id: int
    user_id: int
    amount: float
    transaction_type: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
