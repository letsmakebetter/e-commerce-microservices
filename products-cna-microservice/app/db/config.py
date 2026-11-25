"""Async SQLAlchemy engine and session factory."""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.settings import settings


class Base(DeclarativeBase):
    pass


# Under pytest each test runs on its own asyncio event loop, and an asyncpg
# connection belongs to the loop that opened it. NullPool hands out a fresh
# connection every time instead of reusing one across loops.
_engine_options: dict = {"future": True}
if os.getenv("TESTING", "").strip().lower() in {"1", "true", "yes"}:
    _engine_options["poolclass"] = NullPool

engine = create_async_engine(settings.database_url, **_engine_options)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    """FastAPI dependency: one session per request."""
    async with async_session() as session:
        yield session
