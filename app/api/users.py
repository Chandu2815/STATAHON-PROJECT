"""
User and billing API endpoints with enhanced validation and security
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UsageStatsResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    UserResponse,
    TopupRequest,
    DeductCreditsRequest,
    CreditBalanceResponse,
    RateLimitResponse,
    PricingTier,
    PricingResponse
)
from app.auth import get_current_user
from app.services.access_control import AccessControlService
from app.services.payment import PaymentService
import logging

# Configure logging for audit trail
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (Admin only)
    
    Requires admin privileges to access user list
    """
    # Check if user is admin
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get all users
    users = db.query(User).all()
    logger.info(f"Admin {current_user.username} retrieved {len(users)} users")
    return users


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.get("/me/usage", response_model=UsageStatsResponse)
def get_my_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's detailed usage statistics
    
    Returns comprehensive metrics including:
    - Total and daily request counts
    - Data transfer volumes
    - Credits used and remaining
    - Rate limit status
    
    **Example Response:**
    ```json
    {
        "user_id": 1,
        "total_requests": 250,
        "requests_today": 45,
        "total_data_mb": 125.5,
        "credits_used": 500,
        "credits_remaining": 500,
        "rate_limit_status": "active",
        "daily_limit": 1000,
        "requests_remaining_today": 955
    }
    ```
    """
    try:
        access_control = AccessControlService(db)
        stats = access_control.get_usage_stats(current_user)
        logger.info(f"Usage stats retrieved for user {current_user.id}")
        return stats
    except Exception as e:
        logger.error(f"Error retrieving usage stats for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics"
        )


@router.get("/me/credits", response_model=CreditBalanceResponse)
def get_credit_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current credit balance only
    
    Quick endpoint to check available credits without full usage stats.
    
    **Example Response:**
    ```json
    {
        "credits": 1500.0,
        "last_topup": "2025-12-17T10:30:00Z"
    }
    ```
    """
    try:
        from app.models.user import Transaction
        last_topup = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "topup"
        ).order_by(Transaction.created_at.desc()).first()
        
        return CreditBalanceResponse(
            credits=current_user.credits,
            last_topup=last_topup.created_at if last_topup else None
        )
    except Exception as e:
        logger.error(f"Error retrieving credit balance for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit balance"
        )


@router.get("/me/rate-limits", response_model=RateLimitResponse)
def get_rate_limit_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current rate limit status
    
    Shows daily request limits and remaining quota.
    
    **Example Response:**
    ```json
    {
        "daily_limit": 1000,
        "requests_today": 45,
        "requests_remaining": 955,
        "reset_at": "2025-12-18T00:00:00Z",
        "rate_limit_exceeded": false
    }
    ```
    """
    try:
        access_control = AccessControlService(db)
        limit_info = access_control.get_rate_limit_info(current_user)
        logger.info(f"Rate limit status retrieved for user {current_user.id}")
        return limit_info
    except Exception as e:
        logger.error(f"Error retrieving rate limits for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve rate limit status"
        )


@router.post("/me/topup", response_model=TransactionResponse)
def topup_credits(
    request: TopupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add credits to user account with validation
    
    **Requirements:**
    - Amount must be between 10 and 100,000
    - Valid payment method required
    - Rate limited to 5 requests per hour
    
    **Example Request:**
    ```json
    {
        "amount": 500.0,
        "payment_method": "credit_card"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "id": 123,
        "user_id": 1,
        "amount": 500.0,
        "transaction_type": "topup",
        "status": "completed",
        "payment_method": "credit_card",
        "created_at": "2025-12-17T10:30:00Z"
    }
    ```
    """
    # Rate limiting check (max 5 topups per hour)
    try:
        from app.models.user import Transaction
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_topups = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "topup",
            Transaction.created_at >= one_hour_ago
        ).count()
        
        if recent_topups >= 5:
            logger.warning(f"Rate limit exceeded for topup by user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many topup requests. Maximum 5 per hour. Please try again later."
            )
        
        # Validate amount
        if request.amount < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum topup amount is 10 credits"
            )
        
        if request.amount > 100000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum topup amount is 100,000 credits"
            )
        
        # Process topup
        payment_service = PaymentService(db)
        transaction = payment_service.topup_credits(current_user, request.amount)
        
        # Audit log
        logger.info(
            f"Credit topup successful: User {current_user.id}, "
            f"Amount {request.amount}, Transaction {transaction.id}"
        )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Topup failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Payment processing failed: {str(e)}"
        )


@router.post("/me/deduct-credits", response_model=TransactionResponse)
def deduct_credits(
    request: DeductCreditsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deduct credits from user account (Internal use)
    
    Used for API usage billing and administrative adjustments.
    
    **Example Request:**
    ```json
    {
        "amount": 50.0,
        "reason": "API usage for advanced query"
    }
    ```
    """
    try:
        # Check sufficient balance
        if current_user.credits < request.amount:
            logger.warning(
                f"Insufficient credits for user {current_user.id}: "
                f"Required {request.amount}, Available {current_user.credits}"
            )
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {request.amount}, Available: {current_user.credits}"
            )
        
        # Deduct credits
        payment_service = PaymentService(db)
        transaction = payment_service.deduct_credits(
            current_user, 
            request.amount, 
            request.reason
        )
        
        # Audit log
        logger.info(
            f"Credits deducted: User {current_user.id}, "
            f"Amount {request.amount}, Reason: {request.reason}"
        )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deduct credits failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deduct credits"
        )


@router.post("/me/upgrade-premium", response_model=TransactionResponse)
def upgrade_to_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user to PREMIUM tier
    
    **Benefits:**
    - Daily limit increased to 10,000 requests
    - Access to advanced analytics
    - Priority support
    - Cost: 5,000 credits
    
    **Example Response:**
    ```json
    {
        "id": 124,
        "user_id": 1,
        "amount": 5000.0,
        "transaction_type": "upgrade",
        "description": "Upgraded to PREMIUM tier",
        "status": "completed",
        "created_at": "2025-12-17T10:30:00Z"
    }
    ```
    """
    try:
        UPGRADE_COST = 5000.0
        
        # Check if already premium or admin
        if current_user.role in ["premium", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User already has {current_user.role.upper()} access"
            )
        
        # Check sufficient credits
        if current_user.credits < UPGRADE_COST:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {UPGRADE_COST}, Available: {current_user.credits}"
            )
        
        # Upgrade user
        from app.models.user import UserRole
        current_user.role = UserRole.PREMIUM
        current_user.credits -= UPGRADE_COST
        
        # Create transaction record
        from app.models.user import Transaction
        transaction = Transaction(
            user_id=current_user.id,
            amount=UPGRADE_COST,
            transaction_type="upgrade",
            description="Upgraded to PREMIUM tier",
            status="completed"
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Audit log
        logger.info(
            f"User {current_user.id} upgraded to PREMIUM tier. "
            f"Transaction {transaction.id}"
        )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Upgrade failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upgrade failed. Please try again."
        )


@router.get("/me/transactions", response_model=TransactionListResponse)
def get_my_transactions(
    skip: int = 0,
    limit: int = 100,
    transaction_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's transaction history with filters
    
    **Query Parameters:**
    - `skip`: Number of records to skip (pagination)
    - `limit`: Max records to return (default: 100)
    - `transaction_type`: Filter by type (topup, deduct, upgrade, refund)
    - `status_filter`: Filter by status (completed, pending, failed)
    - `start_date`: Filter from date (ISO format)
    - `end_date`: Filter to date (ISO format)
    
    **Example Response:**
    ```json
    {
        "total": 45,
        "page": 1,
        "page_size": 10,
        "transactions": [...]
    }
    ```
    """
    try:
        from app.models.user import Transaction
        
        # Build query with filters
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
        
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        transactions = query.order_by(
            Transaction.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        logger.info(
            f"Retrieved {len(transactions)} transactions for user {current_user.id} "
            f"(Total: {total}, Filters: type={transaction_type}, status={status_filter})"
        )
        
        return TransactionListResponse(
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=limit,
            transactions=transactions
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve transactions for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction history"
        )


@router.get("/pricing", response_model=PricingResponse)
def get_pricing():
    """
    Get comprehensive pricing information
    
    Returns details about all subscription tiers, topup rates, and overage pricing.
    
    **Example Response:**
    ```json
    {
        "tiers": [
            {
                "name": "PUBLIC",
                "daily_limit": 100,
                "price_per_month": 0.0,
                "features": ["Basic API access", "100 requests/day"],
                "recommended": false
            },
            {
                "name": "RESEARCHER",
                "daily_limit": 1000,
                "price_per_month": 29.99,
                "features": ["Extended API access", "1000 requests/day", "Data exports"],
                "recommended": true
            }
        ],
        "topup_rates": {
            "100_credits": 9.99,
            "500_credits": 44.99,
            "1000_credits": 79.99
        },
        "overage_rate": 0.10
    }
    ```
    """
    try:
        pricing_data = PricingResponse(
            tiers=[
                PricingTier(
                    name="PUBLIC",
                    daily_limit=100,
                    price_per_month=0.0,
                    features=[
                        "Basic API access",
                        "100 requests per day",
                        "Standard support",
                        "1,000 initial credits"
                    ],
                    recommended=False
                ),
                PricingTier(
                    name="RESEARCHER",
                    daily_limit=1000,
                    price_per_month=29.99,
                    features=[
                        "Extended API access",
                        "1,000 requests per day",
                        "Data export capabilities",
                        "Email support",
                        "1,000 initial credits"
                    ],
                    recommended=True
                ),
                PricingTier(
                    name="PREMIUM",
                    daily_limit=10000,
                    price_per_month=99.99,
                    features=[
                        "Advanced API access",
                        "10,000 requests per day",
                        "Advanced analytics",
                        "Priority support",
                        "Bulk data downloads",
                        "Custom integrations",
                        "5,000 upgrade cost (one-time)"
                    ],
                    recommended=False
                ),
                PricingTier(
                    name="ADMIN",
                    daily_limit=999999,
                    price_per_month=0.0,
                    features=[
                        "Unlimited API access",
                        "Full system access",
                        "Administrative tools",
                        "Unlimited credits"
                    ],
                    recommended=False
                )
            ],
            topup_rates={
                "100_credits": 9.99,
                "500_credits": 44.99,
                "1000_credits": 79.99,
                "5000_credits": 349.99,
                "10000_credits": 649.99
            },
            overage_rate=0.10
        )
        
        logger.info("Pricing information retrieved")
        return pricing_data
        
    except Exception as e:
        logger.error(f"Failed to retrieve pricing info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pricing information"
        )


@router.get("/me/analytics", response_model=dict)
def get_usage_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed usage analytics with charts data
    
    Returns usage patterns, spending trends, and activity metrics over time.
    
    **Query Parameters:**
    - `days`: Number of days to analyze (default: 30, max: 365)
    
    **Example Response:**
    ```json
    {
        "period_days": 30,
        "total_requests": 1250,
        "total_spend": 450.0,
        "average_daily_requests": 41.67,
        "daily_activity": [
            {"date": "2025-12-01", "requests": 45, "credits_spent": 15.0},
            {"date": "2025-12-02", "requests": 38, "credits_spent": 12.0}
        ],
        "top_endpoints": [
            {"endpoint": "/plfs/district-codes", "count": 450},
            {"endpoint": "/plfs/item-codes", "count": 320}
        ]
    }
    ```
    """
    try:
        if days > 365:
            days = 365
        
        from app.models.user import UsageLog, Transaction
        from datetime import date, timedelta
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get usage logs
        logs = db.query(UsageLog).filter(
            UsageLog.user_id == current_user.id,
            UsageLog.timestamp >= start_date
        ).all()
        
        # Get transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.created_at >= start_date
        ).all()
        
        # Calculate metrics
        total_requests = len(logs)
        total_spend = sum(t.amount for t in transactions if t.transaction_type == "deduct")
        avg_daily_requests = total_requests / days if days > 0 else 0
        
        # Daily activity breakdown
        daily_activity = {}
        for log in logs:
            day = log.timestamp.date().isoformat()
            if day not in daily_activity:
                daily_activity[day] = {"date": day, "requests": 0, "credits_spent": 0.0}
            daily_activity[day]["requests"] += 1
        
        # Add transaction amounts to days
        for transaction in transactions:
            if transaction.transaction_type == "deduct":
                day = transaction.created_at.date().isoformat()
                if day in daily_activity:
                    daily_activity[day]["credits_spent"] += transaction.amount
        
        # Top endpoints
        endpoint_counts = {}
        for log in logs:
            endpoint = log.endpoint if hasattr(log, 'endpoint') else "unknown"
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
        
        top_endpoints = [
            {"endpoint": k, "count": v}
            for k, v in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        analytics_data = {
            "period_days": days,
            "total_requests": total_requests,
            "total_spend": total_spend,
            "average_daily_requests": round(avg_daily_requests, 2),
            "daily_activity": sorted(daily_activity.values(), key=lambda x: x["date"]),
            "top_endpoints": top_endpoints,
            "credits_remaining": current_user.credits
        }
        
        logger.info(f"Analytics retrieved for user {current_user.id} ({days} days)")
        return analytics_data
        
    except Exception as e:
        logger.error(f"Failed to retrieve analytics for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage analytics"
        )


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    updates: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user details (Admin only)"""
    # Check if user is admin
    if not current_user.can_manage_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user to update
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update allowed fields
    if 'username' in updates:
        # Check if username is already taken by another user
        existing = db.query(User).filter(
            User.username == updates['username'],
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = updates['username']
        
    if 'email' in updates:
        # Check if email is already taken by another user
        existing = db.query(User).filter(
            User.email == updates['email'],
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = updates['email']
        
    if 'full_name' in updates:
        user.full_name = updates['full_name']
        
    if 'role' in updates:
        from app.models.user import UserRole
        try:
            user.role = UserRole(updates['role'])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {updates['role']}"
            )
            
    if 'is_active' in updates:
        user.is_active = updates['is_active']
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Admin {current_user.username} updated user {user_id}")
    return {"message": "User updated successfully", "user": user}


@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    password_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset user password (Admin only)"""
    # Check if user is admin
    if not current_user.can_manage_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get new password
    new_password = password_data.get('new_password')
    if not new_password or len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Update password
    from app.auth import get_password_hash
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    logger.info(f"Admin {current_user.username} reset password for user {user_id}")
    return {"message": "Password reset successfully"}
