"""Loads the demo catalog. Used by `python -m app.data.seed` and by
SEED_ON_START during local development and the demo."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import delete

from app.db.config import Base, async_session, engine
from app.db.models import Deal, Product, Variant

SEED_FILE = Path(__file__).with_name("seed_data.json")


def load_seed_data() -> dict:
    return json.loads(SEED_FILE.read_text(encoding="utf-8"))


async def seed(session=None) -> dict:
    data = load_seed_data()

    own_session = session is None
    session = session or async_session()
    try:
        await session.execute(delete(Deal))
        await session.execute(delete(Variant))
        await session.execute(delete(Product))

        for item in data["products"]:
            session.add(
                Product(
                    id=item["_id"],
                    title=item["title"],
                    description=item["description"],
                    short_description=item["shortDescription"],
                    department=item["department"],
                    category=item["category"],
                    price=item["price"],
                    currency=item["currency"],
                    rating=item["rating"],
                    stock=item["stock"],
                    brand=item["brand"],
                    thumbnail=item["thumbnail"],
                    image=item["image"],
                    attributes=item["attributes"],
                    secondary_attributes=item["secondaryAttributes"],
                    last_updated=datetime.fromisoformat(item["lastUpdated"]),
                    variants=[
                        Variant(
                            sku=variant["sku"],
                            thumbnail=variant.get("thumbnail", ""),
                            image=variant.get("image", ""),
                            attributes=variant.get("attributes", {}),
                            secondary_attributes=variant.get("secondaryAttributes", {}),
                        )
                        for variant in item["variants"]
                    ],
                )
            )

        # Deals reference products, so the products must exist first.
        await session.flush()

        for item in data["deals"]:
            session.add(
                Deal(
                    id=item["_id"],
                    product_id=item["productId"],
                    sku=item["sku"],
                    title=item["title"],
                    thumbnail=item["thumbnail"],
                    original_price=item["originalPrice"],
                    deal_price=item["dealPrice"],
                    discount_percentage=item["discountPercentage"],
                    currency=item["currency"],
                )
            )

        await session.commit()
    finally:
        if own_session:
            await session.close()

    return {"products": len(data["products"]), "deals": len(data["deals"])}


async def _main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    result = await seed()
    print(f"Seeded {result['products']} products and {result['deals']} deals")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(_main())
