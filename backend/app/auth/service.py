from datetime import datetime, timedelta, timezone

from . import crud
from .email import send_otp_email
from .security import (
    create_access_token,
    create_reset_token,
    decode_access_token,
    decode_reset_token,
    generate_otp,
    hash_password,
    validate_password_strength,
    verify_password
)


def request_password_reset(email: str):
    user = crud.get_user_by_email(email)

    if user is None:
        return {
            "success": False,
            "error": "No account found with this email"
        }

    if not user.is_active:
        return {
            "success": False,
            "error": "User account is inactive"
        }

    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    crud.save_reset_otp(
        user_id=user.id,
        otp=otp,
        expires_at=expires_at
    )

    try:
        send_otp_email(
            email=email,
            otp=otp
        )
        return {
            "success": True,
            "message": "Password reset OTP sent to your email",
            "otp": otp
        }
    except Exception as e:
        print(
            f"[OTP EMAIL ERROR] Failed to send email via SMTP ({type(e).__name__}: {e})\n"
            f"[OTP DEV CONSOLE] Use OTP: {otp} for email: {email}"
        )
        return {
            "success": True,
            "message": f"Password reset OTP generated: {otp} (Email delivery failed: {e})",
            "otp": otp
        }


def verify_password_reset_otp(
    email: str,
    otp: str
):
    user = crud.verify_reset_otp(
        email=email,
        otp=otp
    )

    if user is None:
        return None

    reset_token = create_reset_token(user.id)

    return {
        "reset_token": reset_token,
        "user_id": user.id
    }


def reset_password(
    user_id: int,
    password: str
):
    hashed_password = hash_password(password)

    return crud.update_password(
        user_id=user_id,
        hashed_password=hashed_password
    )


def login_user(
    username: str,
    password: str
):
    # Support login with either username or email
    user = crud.get_user_by_username(username)
    if user is None:
        user = crud.get_user_by_email(username)

    if user is None:
        return None

    if not user.is_active:
        return None

    if not user.hashed_password:
        return None

    if not verify_password(
        password,
        user.hashed_password
    ):
        return None

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "email_verified": user.email_verified
        }
    }