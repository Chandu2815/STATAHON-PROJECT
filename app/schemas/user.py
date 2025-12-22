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
    plain_password: Optional[str] = None  # Include plain password for admin viewing
    
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
    """Enhanced usage statistics response with detailed metrics"""
    user_id: int
    total_requests: int
    requests_today: int
    total_data_mb: float = Field(alias="total_data_transferred_mb")
    credits_used: float
    credits_remaining: float
    rate_limit_status: str
    daily_limit: int
    requests_remaining_today: int
    last_request: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class TopupRequest(BaseModel):
    """Request model for credit topup with validation"""
    amount: float = Field(
        ..., 
        gt=10, 
        le=100000,
        description="Amount to add (min: 10, max: 100,000)"
    )
    payment_method: Optional[str] = Field(default="credit_card", description="Payment method")
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 500.0,
                "payment_method": "credit_card"
            }
        }


class DeductCreditsRequest(BaseModel):
    """Internal request for deducting credits"""
    amount: float = Field(..., gt=0, description="Amount to deduct")
    reason: str = Field(..., description="Reason for deduction")


class TransactionCreate(BaseModel):
    """Transaction creation schema"""
    amount: float = Field(..., gt=0)
    transaction_type: str


class TransactionResponse(BaseModel):
    """Enhanced transaction response with full details"""
    id: int
    user_id: int
    amount: float
    transaction_type: str
    description: Optional[str] = None
    status: str
    payment_method: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Paginated transaction list with metadata"""
    total: int
    page: int
    page_size: int
    transactions: list[TransactionResponse]


class CreditBalanceResponse(BaseModel):
    """Credit balance only response"""
    credits: float
    last_topup: Optional[datetime] = None


class RateLimitResponse(BaseModel):
    """Rate limit status response"""
    daily_limit: int
    requests_today: int
    requests_remaining: int
    reset_at: datetime
    rate_limit_exceeded: bool


class PricingTier(BaseModel):
    """Pricing tier information"""
    name: str
    daily_limit: int
    price_per_month: float
    features: list[str]
    recommended: bool = False


class PricingResponse(BaseModel):
    """Complete pricing information"""
    tiers: list[PricingTier]
    topup_rates: dict
    overage_rate: float
