"""Catalog tables owned by the Product Service.

The catalog is modelled relationally rather than as one JSON blob: a product
has many variants, and a variant sku is the identifier that the Order Service
and the frontend use. Free-form marketing attributes stay in JSONB, because
they differ per department and would otherwise need a column per attribute.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.config import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    rating: Mapped[float] = mapped_column(Numeric(2, 1), default=0, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    thumbnail: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    image: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    secondary_attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    variants: Mapped[list["Variant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Variant.sku",
    )

    __table_args__ = (
        CheckConstraint("price >= 0", name="products_price_non_negative"),
        CheckConstraint("stock >= 0", name="products_stock_non_negative"),
        CheckConstraint("rating >= 0 AND rating <= 5", name="products_rating_range"),
        Index("products_category_idx", "category"),
        Index("products_department_idx", "department"),
        Index("products_price_idx", "price"),
        Index("products_brand_idx", "brand"),
    )


class Variant(Base):
    """One buyable item. `sku` is unique across the whole catalog."""

    __tablename__ = "variants"

    sku: Mapped[str] = mapped_column(String(64), primary_key=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    thumbnail: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    image: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    secondary_attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    product: Mapped[Product] = relationship(back_populates="variants")

    __table_args__ = (Index("variants_product_id_idx", "product_id"),)


class Deal(Base):
    """Landing-page offers, shown by the frontend."""

    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    thumbnail: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    original_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    deal_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    discount_percentage: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
