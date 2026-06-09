from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timedelta
from app.database import Base

class FailedLoginAttempt(Base):
    """Track failed login attempts for security"""
    __tablename__ = "failed_login_attempts"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    attempt_count = Column(Integer, default=1)  # Number of failed attempts
    last_attempt_time = Column(DateTime, default=datetime.utcnow)
    locked_until = Column(DateTime, nullable=True)  # When lockout expires (30-min)
    is_locked = Column(Boolean, default=False)  # Is account currently locked (temporary)
    is_permanently_locked = Column(Boolean, default=False)  # Permanent lock after 5 attempts (admin unlock only)
    locked_by_admin = Column(Boolean, default=False)  # Locked by admin or by system
    ip_address = Column(String(50), nullable=True)
    failure_reason = Column(String(255), nullable=True)  # 'wrong_password', 'wrong_otp', etc

    def is_currently_locked(self):
        """Check if account is currently locked"""
        if not self.is_locked:
            return False
        
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        
        # Lockout expired, reset
        self.is_locked = False
        self.locked_until = None
        self.attempt_count = 0
        return False

    def get_remaining_lockout_seconds(self):
        """Get remaining lockout time in seconds"""
        if not self.is_locked or not self.locked_until:
            return 0
        
        remaining = self.locked_until - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))

    def get_remaining_cooldown_seconds(self):
        """Get remaining cooldown time after failed attempt (30 seconds)"""
        if self.attempt_count >= 4:
            return self.get_remaining_lockout_seconds()
        
        # 30 second cooldown between attempts
        cooldown_end = self.last_attempt_time + timedelta(seconds=30)
        remaining = cooldown_end - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))

    def can_attempt_now(self):
        """Check if user can attempt login now"""
        return self.get_remaining_cooldown_seconds() == 0


class LoginAttemptHistory(Base):
    """Log all login attempts (for audit trail)"""
    __tablename__ = "login_attempt_history"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    attempt_status = Column(String(50), nullable=False)  # 'success', 'failed_password', 'failed_otp', 'locked'
    ip_address = Column(String(50), nullable=True)
    device_info = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    error_message = Column(String(255), nullable=True)
