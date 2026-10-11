from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from app.dependencies import get_current_user

from . import crud, service

from .schema import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MessageResponse,
    RegisterUser,
    ResetPasswordRequest,
    ResetTokenResponse,
    TokenResponse,
    UserResponse,
    VerifyResetOTPRequest
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(user_data: RegisterUser):

    username = user_data.username.strip()
    email = str(user_data.email).strip().lower()

    if user_data.confirm_password is not None and user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    if crud.get_user_by_username(username):
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    if crud.get_user_by_email(email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = service.hash_password(
        user_data.password
    )

    try:

        user = crud.create_user(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        print(f"[AUTH] Registered new user id={user.id}, username='{user.username}', email='{user.email}'")
        return user

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database error creating user: {str(e)}"
        )


@router.get(
    "/users",
    response_model=list[UserResponse]
)
def list_users():
    """
    Get all registered users in the database.
    """
    return crud.get_all_users()



@router.post(
    "/login",
    response_model=TokenResponse
)
def login(data: LoginRequest):

    result = service.login_user(
        username=data.username,
        password=data.password
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return result


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse
)
def forgot_password(
    data: ForgotPasswordRequest
):

    email = str(data.email).strip().lower()

    result = service.request_password_reset(
        email=email
    )

    if not result.get("success"):

        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Unable to process password reset")
        )

    return {
        "message": "Password reset OTP has been sent to your registered email address.",
        "otp": None
    }


@router.post(
    "/verify-reset-otp",
    response_model=ResetTokenResponse
)
def verify_reset_otp(
    data: VerifyResetOTPRequest
):

    email = str(data.email).strip().lower()

    result = service.verify_password_reset_otp(
        email=email,
        otp=data.otp
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )

    return {
        "reset_token": result["reset_token"],
        "token_type": "reset",
        "message": (
            "OTP verified successfully. "
            "You can now reset your password."
        )
    }


@router.post(
    "/reset-password",
    response_model=MessageResponse
)
def reset_password(
    data: ResetPasswordRequest,
    token: str | None = None
):

    actual_token = token or data.token

    if not actual_token:
        raise HTTPException(
            status_code=400,
            detail="Reset token is required"
        )

    if data.password != data.confirm_password:

        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    user_id = service.decode_reset_token(actual_token)

    if user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired reset token"
        )

    user = service.reset_password(
        user_id=user_id,
        password=data.password
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": (
            "Password reset successfully. "
            "Please login with your new password."
        )
    }


@router.post(
    "/change-password",
    response_model=MessageResponse
)
def change_password(
    data: ChangePasswordRequest,
    current_user=Depends(get_current_user)
):
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="New passwords do not match"
        )

    if not service.verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    service.reset_password(
        user_id=current_user.id,
        password=data.new_password
    )

    return {
        "message": "Password changed successfully in PostgreSQL database"
    }


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    user=Depends(get_current_user)
):

    return user