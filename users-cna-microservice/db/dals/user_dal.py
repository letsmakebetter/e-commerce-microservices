from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, *, name: str, email: str, mobile: str, password_hash: str) -> User:
        user = User(name=name, email=email, mobile=mobile, password_hash=password_hash)
        self.db_session.add(user)
        await self.db_session.flush()
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db_session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db_session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def update_user(self, user: User, **changes: str) -> User:
        for field, value in changes.items():
            setattr(user, field, value)
        await self.db_session.flush()
        return user

    async def save(self, user: User) -> User:
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user
