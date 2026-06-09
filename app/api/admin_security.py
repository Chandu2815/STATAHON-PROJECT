"""
Admin endpoints for login security management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.auth import get_current_user
from app.services.login_security import LoginSecurityService

router = APIRouter(prefix="/api/v1/admin/security", tags=["Admin - Security"])


def verify_admin(current_user: User = Depends(get_current_user)):
    """Verify that current user is an admin"""
    admin_roles = {UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.USER_ADMIN, UserRole.SUPPORT_ADMIN}
    if current_user.role not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/login-attempts/{username}")
def get_login_attempts(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    """
    Get failed login attempts for a user
    
    Example: GET /api/v1/admin/security/login-attempts/john_doe
    
    Response:
    {
        "username": "john_doe",
        "attempt_count": 2,
        "is_locked": false,
        "can_attempt": true,
        "remaining_cooldown_seconds": 0,
        "remaining_lockout_seconds": 0,
        "max_attempts": 4,
        "lockout_duration_minutes": 30
    }
    """
    try:
        attempt_info = LoginSecurityService.get_failed_attempt_info(db, username)
        
        if attempt_info["attempt_count"] == 0:
            return {
                "username": username,
                "status": "clean",
                "message": "No failed login attempts"
            }
        
        return {
            "username": username,
            **attempt_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/unlock-account/{username}")
def unlock_account(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    """
    Manually unlock a locked account (admin only)
    
    Example: POST /api/v1/admin/security/unlock-account/john_doe
    
    Response:
    {
        "status": "success",
        "message": "Account unlocked",
        "username": "john_doe"
    }
    """
    try:
        success = LoginSecurityService.unlock_account(db, username)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        return {
            "status": "success",
            "message": f"Account '{username}' has been unlocked",
            "username": username
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-attempts/{username}")
def reset_attempts(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    """
    Reset failed login attempts for a user (admin only)
    
    Example: POST /api/v1/admin/security/reset-attempts/john_doe
    
    Response:
    {
        "status": "success",
        "message": "All failed attempts reset",
        "username": "john_doe",
        "attempt_count": 0
    }
    """
    try:
        success = LoginSecurityService.reset_all_attempts(db, username)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        return {
            "status": "success",
            "message": f"Failed attempts for '{username}' have been reset",
            "username": username,
            "attempt_count": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/login-history/{username}")
def get_login_history(
    username: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    """
    Get login attempt history for a user (admin only)
    
    Example: GET /api/v1/admin/security/login-history/john_doe?limit=100
    
    Response:
    {
        "username": "john_doe",
        "total_records": 50,
        "records": [
            {
                "id": 100,
                "attempt_status": "success",
                "timestamp": "2026-06-03T10:30:00",
                "ip_address": "192.168.1.1",
                "error_message": null
            },
            {
                "id": 99,
                "attempt_status": "failed_password",
                "timestamp": "2026-06-03T10:28:45",
                "ip_address": "192.168.1.1",
                "error_message": "Failed attempt 1/4"
            }
        ]
    }
    """
    try:
        history = LoginSecurityService.get_login_history(db, username, limit)
        
        return {
            "username": username,
            "total_records": len(history),
            "records": [
                {
                    "id": h.id,
                    "attempt_status": h.attempt_status,
                    "timestamp": h.timestamp.isoformat(),
                    "ip_address": h.ip_address,
                    "error_message": h.error_message
                }
                for h in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/all-failed-attempts")
def get_all_failed_attempts(
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    """
    Get all users with failed login attempts (admin only)
    
    Example: GET /api/v1/admin/security/all-failed-attempts
    
    Response:
    {
        "total_locked": 2,
        "total_in_cooldown": 3,
        "locked_accounts": [
            {
                "username": "john_doe",
                "attempt_count": 4,
                "remaining_minutes": 25
            }
        ],
        "cooldown_accounts": [...]
    }
    """
    try:
        from app.models.security import FailedLoginAttempt
        
        # Get all failed attempts
        all_attempts = db.query(FailedLoginAttempt).all()
        
        locked_accounts = []
        cooldown_accounts = []
        
        for attempt in all_attempts:
            if attempt.is_currently_locked():
                locked_accounts.append({
                    "username": attempt.username,
                    "attempt_count": attempt.attempt_count,
                    "remaining_minutes": attempt.get_remaining_lockout_seconds() // 60,
                    "locked_until": attempt.locked_until.isoformat() if attempt.locked_until else None
                })
            elif attempt.attempt_count > 0 and attempt.get_remaining_cooldown_seconds() > 0:
                cooldown_accounts.append({
                    "username": attempt.username,
                    "attempt_count": attempt.attempt_count,
                    "remaining_seconds": attempt.get_remaining_cooldown_seconds()
                })
        
        return {
            "total_locked": len(locked_accounts),
            "total_in_cooldown": len(cooldown_accounts),
            "locked_accounts": locked_accounts,
            "cooldown_accounts": cooldown_accounts
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/unlock-all-expired")
def unlock_all_expired(
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    """
    Automatically unlock all accounts with expired lockouts (admin only)
    
    Example: POST /api/v1/admin/security/unlock-all-expired
    
    Response:
    {
        "status": "success",
        "message": "3 accounts have been unlocked",
        "unlocked_count": 3
    }
    """
    try:
        from app.models.security import FailedLoginAttempt
        from datetime import datetime
        
        all_attempts = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.is_locked == True
        ).all()
        
        unlocked_count = 0
        
        for attempt in all_attempts:
            if attempt.is_currently_locked():
                # Still locked
                continue
            else:
                # Lockout expired - unlock
                attempt.attempt_count = 0
                attempt.is_locked = False
                attempt.locked_until = None
                unlocked_count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"{unlocked_count} account(s) have been unlocked",
            "unlocked_count": unlocked_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/permanently-locked-accounts")
def get_permanently_locked_accounts(
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    """
    Get all accounts that are PERMANENTLY locked (after 5 failed attempts) (admin only)
    
    Example: GET /api/v1/admin/security/permanently-locked-accounts
    
    Response:
    {
        "total_permanently_locked": 2,
        "locked_accounts": [
            {
                "username": "john_doe",
                "user_id": 5,
                "attempt_count": 5,
                "last_attempt": "2026-06-03T10:30:00",
                "ip_address": "192.168.1.1",
                "failure_reason": "wrong_password"
            }
        ]
    }
    """
    try:
        locked_accounts = LoginSecurityService.get_permanently_locked_accounts(db)
        
        return {
            "total_permanently_locked": len(locked_accounts),
            "locked_accounts": locked_accounts
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/permanently-unlock-account/{username}")
def permanently_unlock_account(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    """
    Permanently unlock an account that was locked after 5 failed attempts (admin only)
    
    Example: POST /api/v1/admin/security/permanently-unlock-account/john_doe
    
    Response:
    {
        "status": "success",
        "message": "Account permanently unlocked",
        "username": "john_doe",
        "unlocked_by_admin": true,
        "admin_username": "admin"
    }
    """
    try:
        success = LoginSecurityService.permanently_unlock_account(db, username, admin.id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found or not permanently locked")
        
        return {
            "status": "success",
            "message": f"Account '{username}' has been permanently unlocked by admin",
            "username": username,
            "unlocked_by_admin": True,
            "admin_username": admin.username
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
