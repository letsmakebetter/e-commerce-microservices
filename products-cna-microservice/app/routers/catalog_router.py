"""Categories, departments, brands and the landing page deals."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db.models import Product
from app.dependencies import get_repository
from app.repositories.product_repository import ProductRepository
from app.schemas import DealOut

router = APIRouter(prefix="/api/v1", tags=["Catalog"])


@router.get("/categories")
async def categories(repository: ProductRepository = Depends(get_repository)) -> dict:
    return {"data": await repository.distinct(Product.category)}


@router.get("/departments")
async def departments(repository: ProductRepository = Depends(get_repository)) -> dict:
    return {"data": await repository.distinct(Product.department)}


@router.get("/brands")
async def brands(repository: ProductRepository = Depends(get_repository)) -> dict:
    return {"data": await repository.distinct(Product.brand)}


@router.get("/deals")
async def deals(repository: ProductRepository = Depends(get_repository)) -> dict:
    rows = await repository.list_deals()
    return {"data": [DealOut.model_validate(row).model_dump(by_alias=True) for row in rows]}
