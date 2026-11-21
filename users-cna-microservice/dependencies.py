
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.config import async_session
from db.dals.user_dal import UserDAL
from db.models.user import User
from security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_user_dal():
    async with async_session() as session:
        yield UserDAL(session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    user_dal: Annotated[UserDAL, Depends(get_user_dal)],
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized

    user = await user_dal.get_by_id(user_id)
    if user is None:
        raise unauthorized
    return user
