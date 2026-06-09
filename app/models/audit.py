"""
Admin audit logging model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AdminAuditLog(Base):
    """Track all admin actions for security and compliance"""
    __tablename__ = "admin_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # CREATE_USER, DELETE_USER, UPLOAD_DATASET, etc.
    target_type = Column(String(50))  # USER, DATASET, SYSTEM
    target_id = Column(Integer)  # ID of affected resource
    description = Column(Text)  # Human-readable description
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    details = Column(Text)  # JSON string with additional details
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship
    admin = relationship("User", foreign_keys=[admin_id])
