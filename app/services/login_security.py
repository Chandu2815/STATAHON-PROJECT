from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.security import FailedLoginAttempt, LoginAttemptHistory
from app.models.user import User

class LoginSecurityService:
    """Service for handling login security, failed attempts, and lockouts"""
    
    # Configuration constants
    MAX_ATTEMPTS_BEFORE_LOCKOUT = 4  # 4 wrong attempts = 30-min temporary lockout
    MAX_ATTEMPTS_BEFORE_PERMANENT_LOCK = 5  # 5 wrong attempts = permanent lock (admin unlock only)
    COOLDOWN_SECONDS = 30  # 30 seconds between attempts
    LOCKOUT_DURATION_MINUTES = 30  # Lock for 30 minutes
    
    @staticmethod
    def get_or_create_failed_attempt(db: Session, username: str, user_id: int = None):
        """Get or create failed login attempt record"""
        attempt = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username
        ).first()
        
        if not attempt:
            attempt = FailedLoginAttempt(
                username=username,
                user_id=user_id,
                attempt_count=0,
                is_locked=False
            )
            db.add(attempt)
            db.commit()
            db.refresh(attempt)
        
        return attempt

    @staticmethod
    def check_account_lockout(db: Session, username: str):
        """
        Check if account is locked due to too many failed attempts
        
        Returns:
            {
                "is_locked": bool,
                "reason": str,
                "remaining_seconds": int (if locked),
                "remaining_cooldown": int (if in cooldown)
            }
        """
        attempt = LoginSecurityService.get_or_create_failed_attempt(db, username)
        
        # Check if account is PERMANENTLY locked (after 5 attempts, admin unlock only)
        if attempt.is_permanently_locked:
            return {
                "is_locked": True,
                "is_permanent": True,
                "reason": "Account permanently locked due to repeated failed attempts. Contact admin to unlock.",
                "attempt_count": attempt.attempt_count,
                "locked_by_admin": attempt.locked_by_admin
            }
        
        # Check if currently in cooldown (between failed attempts)
        if attempt.attempt_count > 0 and attempt.attempt_count < 4:
            cooldown_remaining = attempt.get_remaining_cooldown_seconds()
            if cooldown_remaining > 0:
                return {
                    "is_locked": False,
                    "is_cooldown": True,
                    "reason": f"Too many failed attempts. Please try again in {cooldown_remaining} seconds",
                    "remaining_cooldown": cooldown_remaining,
                    "attempt_count": attempt.attempt_count
                }
        
        # Check if account is temporarily locked (30-min lockout after 4 attempts)
        if attempt.is_currently_locked():
            remaining = attempt.get_remaining_lockout_seconds()
            return {
                "is_locked": True,
                "is_permanent": False,
                "reason": f"Account locked due to too many failed attempts. Try again in {remaining} seconds",
                "remaining_seconds": remaining,
                "attempt_count": attempt.attempt_count
            }
        
        return {
            "is_locked": False,
            "is_cooldown": False,
            "attempt_count": attempt.attempt_count
        }

    @staticmethod
    def record_failed_attempt(
        db: Session,
        username: str,
        user_id: int = None,
        ip_address: str = None,
        failure_reason: str = "wrong_password"
    ):
        """
        Record a failed login attempt
        
        Triggers:
        - 1-3 failed attempts: 30 second cooldown before next attempt
        - 4 failed attempts: 30 minute temporary lockout
        - 5+ failed attempts: PERMANENT lock (admin unlock only)
        """
        attempt = LoginSecurityService.get_or_create_failed_attempt(db, username, user_id)
        
        # Increment attempt count
        attempt.attempt_count += 1
        attempt.last_attempt_time = datetime.utcnow()
        attempt.ip_address = ip_address
        attempt.failure_reason = failure_reason
        
        # Check if we've reached PERMANENT lock threshold
        if attempt.attempt_count >= LoginSecurityService.MAX_ATTEMPTS_BEFORE_PERMANENT_LOCK:
            attempt.is_permanently_locked = True
            attempt.is_locked = False  # Not temporarily locked anymore
            attempt.locked_until = None
            
            # Log permanent lockout event
            history = LoginAttemptHistory(
                username=username,
                user_id=user_id,
                attempt_status="locked",
                ip_address=ip_address,
                error_message=f"Account PERMANENTLY locked after {attempt.attempt_count} failed attempts. Admin unlock required."
            )
        # Check if we've reached max temporary lockout threshold
        elif attempt.attempt_count >= LoginSecurityService.MAX_ATTEMPTS_BEFORE_LOCKOUT:
            # Lock the account temporarily for 30 minutes
            attempt.is_locked = True
            attempt.locked_until = datetime.utcnow() + timedelta(
                minutes=LoginSecurityService.LOCKOUT_DURATION_MINUTES
            )
            
            # Log temporary lockout event
            history = LoginAttemptHistory(
                username=username,
                user_id=user_id,
                attempt_status="locked",
                ip_address=ip_address,
                error_message=f"Account temporarily locked for 30 minutes after {attempt.attempt_count} failed attempts"
            )
        else:
            # Still in attempt phase
            history = LoginAttemptHistory(
                username=username,
                user_id=user_id,
                attempt_status="failed_password",
                ip_address=ip_address,
                error_message=f"Failed attempt {attempt.attempt_count}/{LoginSecurityService.MAX_ATTEMPTS_BEFORE_PERMANENT_LOCK}"
            )
        
        db.add(history)
        db.commit()
        db.refresh(attempt)
        
        return attempt

    @staticmethod
    def record_failed_otp_attempt(
        db: Session,
        username: str,
        user_id: int = None,
        ip_address: str = None
    ):
        """Record a failed OTP verification attempt"""
        return LoginSecurityService.record_failed_attempt(
            db,
            username,
            user_id,
            ip_address,
            failure_reason="wrong_otp"
        )

    @staticmethod
    def record_successful_login(db: Session, username: str, user_id: int, ip_address: str = None):
        """Clear failed attempts and log successful login"""
        # Get the attempt record
        attempt = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username
        ).first()
        
        if attempt:
            # Reset failed attempts
            attempt.attempt_count = 0
            attempt.is_locked = False
            attempt.locked_until = None
            db.commit()
        
        # Log successful login
        history = LoginAttemptHistory(
            username=username,
            user_id=user_id,
            attempt_status="success",
            ip_address=ip_address,
            error_message=None
        )
        db.add(history)
        db.commit()

    @staticmethod
    def get_failed_attempt_info(db: Session, username: str):
        """Get detailed info about failed attempts for this user"""
        attempt = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username
        ).first()
        
        if not attempt:
            return {
                "attempt_count": 0,
                "is_locked": False,
                "can_attempt": True,
                "max_attempts": LoginSecurityService.MAX_ATTEMPTS_BEFORE_PERMANENT_LOCK
            }
        
        remaining_cooldown = attempt.get_remaining_cooldown_seconds()
        remaining_lockout = attempt.get_remaining_lockout_seconds()
        
        return {
            "attempt_count": attempt.attempt_count,
            "is_locked": attempt.is_currently_locked(),
            "can_attempt": remaining_cooldown == 0 and not attempt.is_currently_locked(),
            "remaining_cooldown_seconds": remaining_cooldown,
            "remaining_lockout_seconds": remaining_lockout,
            "max_attempts": LoginSecurityService.MAX_ATTEMPTS_BEFORE_PERMANENT_LOCK,
            "lockout_duration_minutes": LoginSecurityService.LOCKOUT_DURATION_MINUTES
        }

    @staticmethod
    def get_login_history(db: Session, username: str = None, limit: int = 50):
        """Get login attempt history for audit"""
        query = db.query(LoginAttemptHistory)
        
        if username:
            query = query.filter(LoginAttemptHistory.username == username)
        
        return query.order_by(
            LoginAttemptHistory.timestamp.desc()
        ).limit(limit).all()

    @staticmethod
    def unlock_account(db: Session, username: str):
        """Manually unlock an account (admin function)"""
        attempt = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username
        ).first()
        
        if attempt:
            attempt.attempt_count = 0
            attempt.is_locked = False
            attempt.locked_until = None
            db.commit()
            return True
        
        return False

    @staticmethod
    def permanently_unlock_account(db: Session, username: str, admin_id: int = None):
        """Permanently unlock an account that was locked after 5 attempts (admin function)"""
        attempt = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username
        ).first()
        
        if attempt:
            # Reset all lock states
            attempt.attempt_count = 0
            attempt.is_locked = False
            attempt.is_permanently_locked = False
            attempt.locked_until = None
            attempt.last_attempt_time = datetime.utcnow()
            db.commit()
            
            # Log the admin unlock action
            user = db.query(LoginAttemptHistory.__table__).filter(
                LoginAttemptHistory.username == username
            ).first()
            
            return True
        
        return False

    @staticmethod
    def get_permanently_locked_accounts(db: Session):
        """Get all accounts that are permanently locked (admin function)"""
        attempts = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.is_permanently_locked == True
        ).all()
        
        result = []
        for attempt in attempts:
            result.append({
                "username": attempt.username,
                "user_id": attempt.user_id,
                "attempt_count": attempt.attempt_count,
                "last_attempt": attempt.last_attempt_time,
                "ip_address": attempt.ip_address,
                "failure_reason": attempt.failure_reason
            })
        
        return result

    @staticmethod
    def reset_all_attempts(db: Session, username: str):
        """Reset all failed attempts for a user (admin function)"""
        attempt = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username
        ).first()
        
        if attempt:
            attempt.attempt_count = 0
            attempt.is_locked = False
            attempt.is_permanently_locked = False
            attempt.locked_until = None
            attempt.last_attempt_time = datetime.utcnow()
            db.commit()
            return True
        
        return False
