"""Test fixtures.

The API tests run against a real PostgreSQL, because the catalog queries use
PostgreSQL features (JSONB columns, ILIKE with escapes, numeric types) that a
SQLite stand-in would not reproduce faithfully.

Set TEST_DATABASE_URL to point at your own instance; the default matches the
docker-compose file in infra/docker.
"""

from __future__ import annotations

import os

os.environ["TESTING"] = "1"
os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres@localhost:5432/products_test",
    ),
)

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.data.seed import seed  # noqa: E402
from app.db.config import Base, async_session, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
async def _seeded():
    """Every test starts from exactly the same 12 products and 6 deals, so one
    test can never leave state behind that changes another one's result."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        await seed(session)
    yield


@pytest.fixture
async def api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
