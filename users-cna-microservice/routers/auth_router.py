from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from db.dals.user_dal import UserDAL
from dependencies import get_user_dal
from schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_input: UserCreate,
    user_dal: Annotated[UserDAL, Depends(get_user_dal)],
):
    """Create a user account with a hashed password."""
    email = user_input.email.lower()
    if await user_dal.get_by_email(email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email address is already registered.")

    user = await user_dal.create_user(
        name=user_input.name,
        email=email,
        mobile=user_input.mobile,
        password_hash=hash_password(user_input.password),
    )
    return await user_dal.save(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    user_dal: Annotated[UserDAL, Depends(get_user_dal)],
):
    """Authenticate a user and return a bearer JWT access token."""
    user = await user_dal.get_by_email(credentials.email.lower())
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")

    return TokenResponse(access_token=create_access_token(user.id))
