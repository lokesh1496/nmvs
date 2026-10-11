from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from database.database import SessionLocal
from app.users.model import User


def get_user_by_username(username: str):
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .filter(User.username == username.strip())
            .first()
        )
    finally:
        db.close()


def get_user_by_email(email: str):
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .filter(User.email == email.strip().lower())
            .first()
        )
    finally:
        db.close()


def get_user_by_id(user_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    finally:
        db.close()


def create_user(
    username: str,
    email: str,
    hashed_password: str
):
    db = SessionLocal()

    try:
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            hashed_password=hashed_password,
            is_active=True,
            email_verified=False,
            email_otp=None,
            otp_expires_at=None
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Username or email already exists"
        )

    except Exception as e:
        db.rollback()
        print(f"DATABASE CREATE USER ERROR: {type(e).__name__}: {e}")
        raise

    finally:
        db.close()


def get_all_users():
    db = SessionLocal()
    try:
        return (
            db.query(User)
            .order_by(User.id.desc())
            .all()
        )
    finally:
        db.close()


def save_reset_otp(
    user_id: int,
    otp: str,
    expires_at: datetime
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return None

        user.email_otp = otp
        user.otp_expires_at = expires_at

        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def verify_reset_otp(
    email: str,
    otp: str
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == email.strip().lower())
            .first()
        )

        if user is None:
            return None

        if user.email_otp != otp:
            return None

        if user.otp_expires_at is None:
            return None

        expires_at = user.otp_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        if now > expires_at:
            return None

        # OTP can only be used once.
        user.email_otp = None
        user.otp_expires_at = None

        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def update_password(
    user_id: int,
    hashed_password: str
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return None

        user.hashed_password = hashed_password

        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()