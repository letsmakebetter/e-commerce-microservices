"""Translates catalog query parameters into SQLAlchemy conditions.

Kept free of database access so the filter logic can be unit tested.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ColumnElement, asc, desc, func

from app.db.models import Product


def build_conditions(
    *,
    q: str | None = None,
    category: str | None = None,
    department: str | None = None,
    brand: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_rating: Decimal | None = None,
    in_stock: bool | None = None,
) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []

    if q:
        # Case-insensitive contains over the fields a shopper would type into.
        pattern = f"%{_escape_like(q)}%"
        conditions.append(
            Product.title.ilike(pattern, escape="\\")
            | Product.short_description.ilike(pattern, escape="\\")
            | Product.description.ilike(pattern, escape="\\")
        )
    if category:
        # Categories are hierarchical ("Shoes/Women/Pumps"), so a prefix match
        # also returns every sub-category.
        conditions.append(Product.category.ilike(f"{_escape_like(category)}%", escape="\\"))
    if department:
        conditions.append(func.lower(Product.department) == department.lower())
    if brand:
        conditions.append(func.lower(Product.brand) == brand.lower())
    if min_price is not None:
        conditions.append(Product.price >= min_price)
    if max_price is not None:
        conditions.append(Product.price <= max_price)
    if min_rating is not None:
        conditions.append(Product.rating >= min_rating)
    if in_stock is True:
        conditions.append(Product.stock > 0)
    if in_stock is False:
        conditions.append(Product.stock <= 0)

    return conditions


_SORT_COLUMNS = {
    "price": Product.price,
    "rating": Product.rating,
    "title": Product.title,
    "lastUpdated": Product.last_updated,
}


def build_order_by(sort: str | None) -> list:
    """`-price` sorts descending.

    The product id is always appended as a tie breaker. Without it, rows that
    share a sort value can come back in a different order for each page, so a
    client paging through the catalog would see some products twice and miss
    others entirely.
    """
    key = sort or "-lastUpdated"
    descending = key.startswith("-")
    column = _SORT_COLUMNS.get(key[1:] if descending else key, Product.last_updated)
    return [desc(column) if descending else asc(column), asc(Product.id)]


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
