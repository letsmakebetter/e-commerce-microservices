from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from db.dals.user_dal import UserDAL
from db.models.user import User
from dependencies import get_current_user, get_user_dal
from schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Profile"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]):
    """Return the profile belonging to the access token."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    user_dal: Annotated[UserDAL, Depends(get_user_dal)],
):
    """Update the authenticated user's name, email, or mobile number."""
    changes = update.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide at least one field to update.")

    if "email" in changes:
        changes["email"] = changes["email"].lower()
        existing_user = await user_dal.get_by_email(changes["email"])
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email address is already registered.")

    updated_user = await user_dal.update_user(current_user, **changes)
    return await user_dal.save(updated_user)
