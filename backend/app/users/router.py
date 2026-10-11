from fastapi import APIRouter, HTTPException, status
from app.auth import crud
from app.auth.schema import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_all_users():
    """
    Retrieve all registered users from the database.
    """
    return crud.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user_by_id(user_id: int):
    """
    Retrieve a specific user by their ID.
    """
    user = crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
