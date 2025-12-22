"""
Access control service for role-based permissions
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.user import User, UsageLog, UserRole
from app.config import get_settings

settings = get_settings()


class AccessControlService:
    """Service for managing access control and rate limiting"""
    
    # Rate limits per role (requests per day)
    RATE_LIMITS = {
        UserRole.PUBLIC: 100,
        UserRole.RESEARCHER: 1000,
        UserRole.PREMIUM: 10000,
        UserRole.ADMIN: 999999
    }
    
    # Data volume limits (MB per day)
    VOLUME_LIMITS = {
        UserRole.PUBLIC: 10,
        UserRole.RESEARCHER: 100,
        UserRole.PREMIUM: 1000,
        UserRole.ADMIN: 999999
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_rate_limit(self, user: User) -> bool:
        """Check if user has exceeded rate limit"""
        
        # Get usage count for today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        usage_count = self.db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.timestamp >= today_start
        ).count()
        
        rate_limit = self.RATE_LIMITS.get(user.role, 100)
        
        if usage_count >= rate_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Your limit is {rate_limit} requests per day."
            )
        
        return True
    
    def check_volume_limit(self, user: User, response_size: int) -> bool:
        """Check if user has exceeded data volume limit"""
        
        # Get total data transferred today (in bytes)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_bytes = self.db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.timestamp >= today_start
        ).with_entities(UsageLog.response_size).all()
        
        total_mb = sum([size[0] or 0 for size in total_bytes]) / (1024 * 1024)
        volume_limit = self.VOLUME_LIMITS.get(user.role, 10)
        
        if total_mb >= volume_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Data volume limit exceeded. Your limit is {volume_limit} MB per day."
            )
        
        return True
    
    def log_usage(
        self,
        user: User,
        endpoint: str,
        method: str,
        dataset_name: Optional[str] = None,
        query_params: Optional[str] = None,
        response_size: int = 0
    ):
        """Log API usage"""
        
        usage_log = UsageLog(
            user_id=user.id,
            endpoint=endpoint,
            method=method,
            dataset_name=dataset_name,
            query_params=query_params,
            response_size=response_size
        )
        
        self.db.add(usage_log)
        self.db.commit()
    
    def get_usage_stats(self, user: User) -> dict:
        """Get usage statistics for a user"""
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Total requests
        total_requests = self.db.query(UsageLog).filter(
            UsageLog.user_id == user.id
        ).count()
        
        # Requests today
        requests_today = self.db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.timestamp >= today_start
        ).count()
        
        # Total data transferred
        total_bytes = self.db.query(UsageLog).filter(
            UsageLog.user_id == user.id
        ).with_entities(UsageLog.response_size).all()
        
        total_mb = sum([size[0] or 0 for size in total_bytes]) / (1024 * 1024)
        
        # Calculate credits used (from transactions)
        from app.models.user import Transaction
        credits_used = sum([
            abs(t.amount) for t in self.db.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type.in_(["charge", "deduct"])
            ).all()
        ])
        
        # Get rate limit
        rate_limit = self.RATE_LIMITS.get(user.role, 100)
        requests_remaining = max(0, rate_limit - requests_today)
        
        # Determine rate limit status
        if requests_today >= rate_limit:
            rate_limit_status = "exceeded"
        elif requests_today >= rate_limit * 0.8:
            rate_limit_status = "warning"
        else:
            rate_limit_status = "active"
        
        # Last request
        last_log = self.db.query(UsageLog).filter(
            UsageLog.user_id == user.id
        ).order_by(UsageLog.timestamp.desc()).first()
        
        return {
            'user_id': user.id,
            'total_requests': total_requests,
            'requests_today': requests_today,
            'total_data_transferred_mb': round(total_mb, 2),
            'total_data_mb': round(total_mb, 2),  # Alias for schema compatibility
            'credits_used': credits_used,
            'credits_remaining': user.credits,
            'rate_limit_status': rate_limit_status,
            'daily_limit': rate_limit,
            'requests_remaining_today': requests_remaining,
            'last_request': last_log.timestamp if last_log else None,
            'rate_limit': rate_limit,
            'volume_limit_mb': self.VOLUME_LIMITS.get(user.role, 10)
        }
    
    def get_rate_limit_info(self, user: User) -> dict:
        """Get rate limit status information"""
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)
        
        # Requests today
        requests_today = self.db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.timestamp >= today_start
        ).count()
        
        # Get rate limit
        daily_limit = self.RATE_LIMITS.get(user.role, 100)
        requests_remaining = max(0, daily_limit - requests_today)
        rate_limit_exceeded = requests_today >= daily_limit
        
        return {
            'daily_limit': daily_limit,
            'requests_today': requests_today,
            'requests_remaining': requests_remaining,
            'reset_at': tomorrow_start,
            'rate_limit_exceeded': rate_limit_exceeded
        }
    
    def check_permission(self, user: User, required_role: UserRole) -> bool:
        """Check if user has required role"""
        
        role_hierarchy = {
            UserRole.PUBLIC: 0,
            UserRole.RESEARCHER: 1,
            UserRole.PREMIUM: 2,
            UserRole.ADMIN: 3
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return True
