"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from datetime import datetime
import hashlib
import json
import random
import smtplib
from email.message import EmailMessage
from uuid import uuid4
import pyotp
from app.database import get_db
from app.models.user import User, UserRole, OtpChallenge, OtpPurpose
from app.schemas.user import (
    UserResponse,
    LoginStartRequest,
    LoginVerifyRequest,
    RegisterStartRequest,
    RegisterVerifyRequest,
    OtpChallengeResponse,
)
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


def _send_otp_or_raise(email: str, otp: str, purpose: OtpPurpose) -> None:
    """Send OTP and convert SMTP errors into user-facing HTTP errors."""
    try:
        _send_otp_email(email, otp, purpose)
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Email authentication failed. Check SMTP username, app password, and 2-step verification settings."
            ),
        )
    except smtplib.SMTPException:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to send OTP email right now. Please verify SMTP settings and try again.",
        )


def _mask_email(email: str) -> str:
    """Mask email for safe UI display"""
    username, domain = email.split("@", 1)
    if len(username) <= 2:
        return f"{username[0]}***@{domain}"
    return f"{username[:2]}***@{domain}"


def _hash_otp(challenge_id: str, otp: str) -> str:
    """Hash OTP with challenge ID and secret key"""
    payload = f"{settings.SECRET_KEY}:{challenge_id}:{otp}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _generate_otp() -> str:
    """Generate a 6 digit OTP"""
    return f"{random.randint(0, 999999):06d}"


def _send_otp_email(recipient_email: str, otp: str, purpose: OtpPurpose) -> None:
    """Send OTP email using SMTP or log in local development"""
    subject = "MoSPI Login OTP" if purpose == OtpPurpose.LOGIN else "MoSPI Registration OTP"
    body = (
        "Dear User,\n\n"
        f"Your OTP for {purpose.value} verification is: {otp}\n"
        f"This OTP expires in {settings.OTP_EXPIRE_MINUTES} minutes.\n\n"
        "If you did not request this, please ignore this email.\n\n"
        "MoSPI DPI Security Team"
    )

    if not settings.SMTP_ENABLED:
        print(f"[OTP-DEBUG] {recipient_email} ({purpose.value}): {otp}")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = recipient_email
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)


def _challenge_response(
    challenge_id: str,
    email: str,
    otp: str | None = None,
    otp_method: str = "totp",
    otpauth_url: str | None = None,
    setup_key: str | None = None,
) -> OtpChallengeResponse:
    """Build consistent challenge response"""
    return OtpChallengeResponse(
        challenge_id=challenge_id,
        message="Authenticator challenge created successfully",
        email=_mask_email(email),
        expires_in_seconds=settings.OTP_EXPIRE_MINUTES * 60,
        otp=otp if (settings.DEBUG and otp) else None,
        otp_method=otp_method,
        otpauth_url=otpauth_url,
        setup_key=setup_key,
    )


def _create_otp_challenge(
    db: Session,
    purpose: OtpPurpose,
    email: str,
    user_id: int | None = None,
    payload: dict | None = None,
) -> tuple[OtpChallenge, str]:
    """Create and persist OTP challenge"""
    otp = _generate_otp()
    challenge_id = uuid4().hex
    challenge = OtpChallenge(
        challenge_id=challenge_id,
        purpose=purpose,
        email=email,
        user_id=user_id,
        otp_hash=_hash_otp(challenge_id, otp),
        payload=json.dumps(payload) if payload else None,
        attempts=0,
        consumed=False,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge, otp


def _verify_and_consume_challenge(
    db: Session,
    challenge_id: str,
    otp: str,
    purpose: OtpPurpose,
) -> OtpChallenge:
    """Verify OTP challenge (TOTP) and mark it consumed"""
    challenge = db.query(OtpChallenge).filter(OtpChallenge.challenge_id == challenge_id).first()

    if not challenge or challenge.purpose != purpose:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid challenge")

    if challenge.consumed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP already used")

    if challenge.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

    if challenge.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many OTP attempts")

    totp_secret = None
    if purpose == OtpPurpose.REGISTER and challenge.payload:
        payload = json.loads(challenge.payload)
        totp_secret = payload.get("totp_secret")
    elif purpose == OtpPurpose.LOGIN and challenge.user_id:
        login_user = db.query(User).filter(User.id == challenge.user_id).first()
        totp_secret = login_user.totp_secret if login_user else None

    if not totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authenticator is not configured")

    is_valid = pyotp.TOTP(totp_secret).verify(otp, valid_window=1)
    if not is_valid:
        challenge.attempts += 1
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authenticator code")

    challenge.consumed = True
    db.commit()
    db.refresh(challenge)
    return challenge


def _credits_for_role(role: UserRole) -> float:
    """Return default credits by role"""
    credits_by_role = {
        UserRole.PUBLIC: 10.0,
        UserRole.RESEARCHER: 100.0,
        UserRole.PREMIUM: 500.0,
        UserRole.ADMIN: 999999.0,
        UserRole.SUPER_ADMIN: 999999.0,
        UserRole.DATA_ADMIN: 999999.0,
        UserRole.USER_ADMIN: 999999.0,
        UserRole.SUPPORT_ADMIN: 999999.0,
    }
    return credits_by_role.get(role, 10.0)


@router.post("/register/start", response_model=OtpChallengeResponse)
def register_start(user_data: RegisterStartRequest, db: Session = Depends(get_db)):
    """Start registration by creating authenticator setup challenge"""

    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    totp_secret = pyotp.random_base32()
    provisioning_uri = pyotp.TOTP(totp_secret).provisioning_uri(
        name=user_data.email,
        issuer_name="MoSPI DPI"
    )

    challenge, _ = _create_otp_challenge(
        db=db,
        purpose=OtpPurpose.REGISTER,
        email=user_data.email,
        payload={
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "password": user_data.password,
            "role": user_data.role.value if hasattr(user_data.role, "value") else user_data.role,
            "totp_secret": totp_secret,
        },
    )

    return _challenge_response(
        challenge_id=challenge.challenge_id,
        email=user_data.email,
        otp_method="totp",
        otpauth_url=provisioning_uri,
        setup_key=totp_secret,
    )


@router.post("/register/verify", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_verify(payload: RegisterVerifyRequest, db: Session = Depends(get_db)):
    """Verify registration OTP and create user account"""
    challenge = _verify_and_consume_challenge(
        db=db,
        challenge_id=payload.challenge_id,
        otp=payload.otp,
        purpose=OtpPurpose.REGISTER,
    )

    if not challenge.payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid registration payload")

    user_payload = json.loads(challenge.payload)

    existing_user = db.query(User).filter(
        (User.email == user_payload["email"]) | (User.username == user_payload["username"])
    ).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")

    role_value = user_payload.get("role", UserRole.PUBLIC.value)
    role = UserRole(role_value)
    user = User(
        email=user_payload["email"],
        username=user_payload["username"],
        full_name=user_payload.get("full_name"),
        hashed_password=get_password_hash(user_payload["password"]),
        password=user_payload["password"],
        role=role,
        credits=_credits_for_role(role),
        is_active=True,
        totp_secret=user_payload.get("totp_secret"),
        totp_enabled=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login/start", response_model=OtpChallengeResponse)
def login_start(payload: LoginStartRequest, db: Session = Depends(get_db)):
    """Start login by validating credentials and requesting authenticator code"""
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    if not user.totp_secret or not user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authenticator is not configured for this account",
        )

    challenge, _ = _create_otp_challenge(
        db=db,
        purpose=OtpPurpose.LOGIN,
        email=user.email,
        user_id=user.id,
    )
    return _challenge_response(challenge.challenge_id, user.email, otp_method="totp")


@router.post("/authenticator/setup")
def authenticator_setup(payload: LoginStartRequest, db: Session = Depends(get_db)):
    """Provision or return authenticator setup key for an existing account."""
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.totp_secret:
        user.totp_secret = pyotp.random_base32()
    user.totp_enabled = True
    db.commit()

    provisioning_uri = pyotp.TOTP(user.totp_secret).provisioning_uri(
        name=user.email,
        issuer_name="MoSPI DPI"
    )

    return {
        "message": "Authenticator setup key generated successfully",
        "username": user.username,
        "setup_key": user.totp_secret,
        "otpauth_url": provisioning_uri,
    }


@router.post("/login/verify")
def login_verify(payload: LoginVerifyRequest, db: Session = Depends(get_db)):
    """Verify login OTP and issue JWT token"""
    challenge = _verify_and_consume_challenge(
        db=db,
        challenge_id=payload.challenge_id,
        otp=payload.otp,
        purpose=OtpPurpose.LOGIN,
    )

    if not challenge.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid login challenge")

    user = db.query(User).filter(User.id == challenge.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    user_role = user.role.value if hasattr(user.role, 'value') else user.role

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user_role,
        "username": user.username
    }


@router.post("/register", response_model=OtpChallengeResponse)
def register_backward_compatible(user_data: RegisterStartRequest, db: Session = Depends(get_db)):
    """Backward-compatible endpoint that starts OTP registration"""
    return register_start(user_data, db)


@router.post("/login")
def login_backward_compatible():
    """Backward-compatible endpoint for legacy clients"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Use /api/v1/auth/login/start and /api/v1/auth/login/verify for OTP login",
    )


@router.get("/reset-admin-password")
def reset_admin_password(db: Session = Depends(get_db)):
    """Reset admin password to default (temporary endpoint for setup)"""
    from app.models.user import UserRole
    
    # Find admin user
    admin = db.query(User).filter(User.username == "admin").first()
    
    if not admin:
        # Create new admin
        admin = User(
            username="admin",
            email="admin@mospi.gov.in",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            password="admin123",
            role=UserRole.ADMIN,
            is_active=True,
            credits=999999.0
        )
        db.add(admin)
        db.commit()
        return {"message": "Admin created", "username": "admin", "password": "admin123"}
    
    # Reset password
    admin.hashed_password = get_password_hash("admin123")
    admin.password = "admin123"
    admin.is_active = True
    db.commit()
    
    return {"message": "Admin password reset", "username": "admin", "password": "admin123"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
