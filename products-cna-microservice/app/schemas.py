"""Request and response models. These define the public API contract."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VariantOut(BaseModel):
    sku: str
    thumbnail: str
    image: str
    attributes: dict[str, Any]
    secondary_attributes: dict[str, Any] = Field(serialization_alias="secondaryAttributes")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProductOut(BaseModel):
    id: str = Field(serialization_alias="_id")
    title: str
    description: str
    short_description: str = Field(serialization_alias="shortDescription")
    department: str
    category: str
    price: Decimal
    currency: str
    rating: Decimal
    stock: int
    brand: str | None
    thumbnail: str
    image: str
    attributes: dict[str, Any]
    secondary_attributes: dict[str, Any] = Field(serialization_alias="secondaryAttributes")
    variants: list[VariantOut]
    last_updated: datetime = Field(serialization_alias="lastUpdated")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DealOut(BaseModel):
    id: str = Field(serialization_alias="_id")
    product_id: str = Field(serialization_alias="productId")
    sku: str
    title: str
    thumbnail: str
    original_price: Decimal = Field(serialization_alias="originalPrice")
    deal_price: Decimal = Field(serialization_alias="dealPrice")
    discount_percentage: int = Field(serialization_alias="discountPercentage")
    currency: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SortOption(str, Enum):
    price = "price"
    price_desc = "-price"
    rating = "rating"
    rating_desc = "-rating"
    title = "title"
    title_desc = "-title"
    last_updated = "lastUpdated"
    last_updated_desc = "-lastUpdated"
