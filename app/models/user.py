"""
User and authentication models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    PUBLIC = "public"
    RESEARCHER = "researcher"
    PREMIUM = "premium"
    ADMIN = "admin"


class User(Base):
    """User model for authentication and access control"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.PUBLIC, nullable=False)
    is_active = Column(Boolean, default=True)
    credits = Column(Float, default=0.0)  # For micro-payment system
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")


class UsageLog(Base):
    """Track API usage for metering"""
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    dataset_name = Column(String(255))
    query_params = Column(String(1000))
    response_size = Column(Integer)  # Size in bytes
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")


class Transaction(Base):
    """Track payment transactions"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # topup, charge
    description = Column(String(500))
    status = Column(String(50), default="pending")  # pending, completed, failed
    payment_gateway_ref = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
