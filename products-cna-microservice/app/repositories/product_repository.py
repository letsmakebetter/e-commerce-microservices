"""All catalog database access lives here."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Deal, Product, Variant
from app.repositories.filters import build_conditions, build_order_by


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_products(self, *, filters: dict, sort: str | None, offset: int, limit: int):
        conditions = build_conditions(**filters)

        total = await self.session.scalar(
            select(func.count()).select_from(Product).where(*conditions)
        )
        rows = await self.session.scalars(
            select(Product).where(*conditions).order_by(*build_order_by(sort)).offset(offset).limit(limit)
        )
        return list(rows), int(total or 0)

    async def get(self, product_id: str) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_by_sku(self, sku: str) -> Product | None:
        variant = await self.session.get(Variant, sku)
        return await self.get(variant.product_id) if variant else None

    async def sku_owner(self, sku: str) -> str | None:
        """Which product owns this sku, if any."""
        return await self.session.scalar(select(Variant.product_id).where(Variant.sku == sku))

    async def distinct(self, column) -> list[str]:
        rows = await self.session.scalars(
            select(column).where(column.is_not(None)).distinct().order_by(column)
        )
        return [row for row in rows if row]

    async def list_deals(self, limit: int = 50) -> list[Deal]:
        rows = await self.session.scalars(select(Deal).order_by(Deal.id).limit(limit))
        return list(rows)
