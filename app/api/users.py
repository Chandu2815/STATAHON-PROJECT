"""
User and billing API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UsageStatsResponse,
    TransactionCreate,
    TransactionResponse,
    UserResponse
)
from app.auth import get_current_user
from app.services.access_control import AccessControlService
from app.services.payment import PaymentService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.get("/me/usage", response_model=dict)
def get_my_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage statistics"""
    access_control = AccessControlService(db)
    stats = access_control.get_usage_stats(current_user)
    return stats


@router.post("/me/topup", response_model=TransactionResponse)
def topup_credits(
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add credits to user account"""
    payment_service = PaymentService(db)
    transaction = payment_service.topup_credits(current_user, amount)
    return transaction


@router.post("/me/upgrade-premium", response_model=TransactionResponse)
def upgrade_to_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade to premium subscription"""
    payment_service = PaymentService(db)
    transaction = payment_service.upgrade_to_premium(current_user)
    return transaction


@router.get("/me/transactions", response_model=List[TransactionResponse])
def get_my_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transaction history"""
    from app.models.user import Transaction
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return transactions


@router.get("/pricing")
def get_pricing():
    """Get pricing information"""
    payment_service = PaymentService(None)
    return payment_service.get_pricing_info()
