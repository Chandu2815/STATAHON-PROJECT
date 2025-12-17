"""
Payment service for micro-payment simulation
"""
from sqlalchemy.orm import Session
from app.models.user import User, Transaction
from fastapi import HTTPException, status
import uuid


class PaymentService:
    """Service for handling micro-payments"""
    
    # Pricing model (in credits)
    PRICING = {
        'query': 0.01,  # Per query
        'data_mb': 0.1,  # Per MB of data
        'premium_subscription': 100.0  # Monthly premium
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def topup_credits(self, user: User, amount: float) -> Transaction:
        """Add credits to user account"""
        
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be positive"
            )
        
        # Simulate payment gateway
        payment_ref = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        
        # Create transaction
        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            transaction_type="topup",
            description=f"Credit topup of {amount} credits",
            status="completed",
            payment_gateway_ref=payment_ref
        )
        
        self.db.add(transaction)
        
        # Update user credits
        user.credits += amount
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def charge_for_query(self, user: User, data_size_bytes: int = 0) -> bool:
        """Charge user for a query"""
        
        # Calculate cost
        query_cost = self.PRICING['query']
        data_cost = (data_size_bytes / (1024 * 1024)) * self.PRICING['data_mb']
        total_cost = query_cost + data_cost
        
        # Premium and admin users don't get charged
        if user.role.value in ['premium', 'admin']:
            return True
        
        # Check if user has enough credits
        if user.credits < total_cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {total_cost:.2f}, Available: {user.credits:.2f}"
            )
        
        # Deduct credits
        user.credits -= total_cost
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            amount=-total_cost,
            transaction_type="charge",
            description=f"Query charge: {query_cost:.4f} + data: {data_cost:.4f}",
            status="completed"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        return True
    
    def upgrade_to_premium(self, user: User) -> Transaction:
        """Upgrade user to premium"""
        
        cost = self.PRICING['premium_subscription']
        
        if user.credits < cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits for premium upgrade. Required: {cost}"
            )
        
        # Deduct credits
        user.credits -= cost
        
        # Upgrade role
        from app.models.user import UserRole
        user.role = UserRole.PREMIUM
        
        # Create transaction
        transaction = Transaction(
            user_id=user.id,
            amount=-cost,
            transaction_type="subscription",
            description="Premium subscription upgrade",
            status="completed"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_pricing_info(self) -> dict:
        """Get current pricing information"""
        return {
            'pricing': self.PRICING,
            'currency': 'credits',
            'description': 'Pay-per-use pricing model for data access'
        }
