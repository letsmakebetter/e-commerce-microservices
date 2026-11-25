"""Product Service - catalog, categories, inventory and search.

SFWE415 Group 4. Owner: Deniz Sismanyazici (2103060009).
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.errors import register_error_handlers
from app.core.request_id import RequestIdMiddleware
from app.db.config import Base, engine
from app.routers import health_router
from app.settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    if settings.seed_on_start:
        from app.data.seed import seed

        result = await seed()
        print(f"Seeded {result['products']} products and {result['deals']} deals")

    yield

    await engine.dispose()


app = FastAPI(
    title="Product Service",
    version=settings.version,
    description=(
        "Product catalog, categories, inventory and search for the e-commerce "
        "platform. PostgreSQL holds the catalog."
    ),
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(health_router.router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
