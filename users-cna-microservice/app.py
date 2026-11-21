from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.config import Base, engine
from routers import auth_router, user_router
from settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create missing tables without removing existing user data."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="User Profile Service",
    version="1.0.0",
    description="Registration, authentication, and user-profile APIs for the e-commerce platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(user_router.router)


@app.get("/health", tags=["System"])
async def health_check():
    """Return service availability for local checks and container orchestration."""
    return {"status": "ok", "service": "user-profile"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=9090, reload=True)
