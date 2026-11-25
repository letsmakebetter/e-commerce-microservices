"""Product listings, CRUD and inventory."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, Query

from app.core.pagination import pagination_meta, resolve_page
from app.dependencies import get_product_service
from app.schemas import ProductOut, SortOption
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("", summary="List products with filtering, sorting and pagination")
async def list_products(
    service: ProductService = Depends(get_product_service),
    page: int = Query(1, ge=1),
    limit: int | None = Query(None, ge=1),
    q: str | None = Query(None, min_length=1, description="Free text over title and description"),
    category: str | None = Query(None, min_length=1, description="Matches sub-categories too"),
    department: str | None = Query(None, min_length=1),
    brand: str | None = Query(None, min_length=1),
    min_price: Decimal | None = Query(None, ge=0, alias="minPrice"),
    max_price: Decimal | None = Query(None, ge=0, alias="maxPrice"),
    min_rating: Decimal | None = Query(None, ge=0, le=5, alias="minRating"),
    in_stock: bool | None = Query(None, alias="inStock"),
    sort: SortOption = Query(SortOption.last_updated_desc),
) -> dict:
    if min_price is not None and max_price is not None and min_price > max_price:
        from app.core.errors import ApiError

        raise ApiError.bad_request(
            "Request validation failed",
            [{"field": "minPrice", "message": "minPrice cannot be greater than maxPrice"}],
        )

    paging = resolve_page(page, limit)
    products, total = await service.list_products(
        filters={
            "q": q,
            "category": category,
            "department": department,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
            "min_rating": min_rating,
            "in_stock": in_stock,
        },
        sort=sort.value,
        offset=paging.offset,
        limit=paging.limit,
    )

    return {
        "data": [ProductOut.model_validate(product).model_dump(by_alias=True) for product in products],
        "pagination": pagination_meta(paging, total),
    }


@router.get("/{product_id}", summary="Get one product")
async def get_product(
    product_id: str, service: ProductService = Depends(get_product_service)
) -> dict:
    product = await service.get(product_id)
    return {"data": ProductOut.model_validate(product).model_dump(by_alias=True)}
