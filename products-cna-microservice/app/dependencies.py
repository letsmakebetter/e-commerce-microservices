"""FastAPI dependency wiring."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.config import get_session
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService


def get_repository(session: AsyncSession = Depends(get_session)) -> ProductRepository:
    return ProductRepository(session)


def get_product_service(
    repository: ProductRepository = Depends(get_repository),
) -> ProductService:
    return ProductService(repository)
