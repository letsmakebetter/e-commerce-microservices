"""Catalog business rules, between the routers and the repository."""

from __future__ import annotations

from app.core.errors import ApiError
from app.db.models import Product
from app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def list_products(self, *, filters: dict, sort: str | None, offset: int, limit: int):
        return await self.repository.list_products(
            filters=filters, sort=sort, offset=offset, limit=limit
        )

    async def get(self, product_id: str) -> Product:
        product = await self.repository.get(product_id)
        if product is None:
            raise ApiError.not_found(f"Product '{product_id}' was not found")
        return product
