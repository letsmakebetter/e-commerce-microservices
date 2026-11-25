"""Browsing the catalog: listing, filtering, sorting, paging and the
category lookups. These read from PostgreSQL."""


class TestListing:
    async def test_first_page_with_metadata(self, api):
        body = (await api.get("/api/v1/products")).json()

        assert len(body["data"]) == 12
        assert body["pagination"] == {
            "page": 1,
            "limit": 20,
            "total": 12,
            "totalPages": 1,
            "hasNextPage": False,
            "hasPreviousPage": False,
        }

    async def test_paging(self, api):
        body = (await api.get("/api/v1/products?page=2&limit=5")).json()

        assert len(body["data"]) == 5
        assert body["pagination"]["hasNextPage"] is True
        assert body["pagination"]["hasPreviousPage"] is True

    async def test_product_shape_uses_the_agreed_field_names(self, api):
        product = (await api.get("/api/v1/products/301671")).json()["data"]

        assert product["_id"] == "301671"
        assert product["shortDescription"] == "Evening Platform Pumps"
        assert product["lastUpdated"].startswith("2026-11-01")
        assert product["variants"][0]["sku"] == "sku2441"
        assert product["attributes"]["brand"] == "Guess"

    async def test_filter_by_department(self, api):
        body = (await api.get("/api/v1/products?department=Mobiles")).json()

        assert body["pagination"]["total"] == 2
        assert {item["department"] for item in body["data"]} == {"Mobiles"}

    async def test_category_filter_includes_sub_categories(self, api):
        body = (await api.get("/api/v1/products?category=Electronics")).json()

        assert body["pagination"]["total"] == 2
        assert all(item["category"].startswith("Electronics") for item in body["data"])

    async def test_filter_by_price_range(self, api):
        body = (await api.get("/api/v1/products?minPrice=100&maxPrice=200")).json()

        assert body["pagination"]["total"] > 0
        assert all(100 <= float(item["price"]) <= 200 for item in body["data"])

    async def test_brand_filter_ignores_letter_case(self, api):
        body = (await api.get("/api/v1/products?brand=homechef")).json()

        assert body["pagination"]["total"] == 2

    async def test_in_stock_filter(self, api):
        in_stock = (await api.get("/api/v1/products?inStock=true")).json()
        out_of_stock = (await api.get("/api/v1/products?inStock=false")).json()

        assert in_stock["pagination"]["total"] == 11
        assert out_of_stock["pagination"]["total"] == 1

    async def test_free_text_search(self, api):
        body = (await api.get("/api/v1/products?q=laptop")).json()

        assert [item["title"] for item in body["data"]] == ["UltraBook 14 Laptop"]

    async def test_free_text_search_ignores_letter_case(self, api):
        body = (await api.get("/api/v1/products?q=LAPTOP")).json()

        assert body["pagination"]["total"] == 1

    async def test_sorting_ascending_and_descending(self, api):
        ascending = (await api.get("/api/v1/products?sort=price")).json()["data"]
        descending = (await api.get("/api/v1/products?sort=-price")).json()["data"]

        prices = [float(item["price"]) for item in ascending]
        assert prices == sorted(prices)
        assert [item["_id"] for item in descending] == [
            item["_id"] for item in reversed(ascending)
        ]

    async def test_filters_combine(self, api):
        body = (
            await api.get("/api/v1/products?department=Electronics&minPrice=500&sort=-price")
        ).json()

        assert [item["title"] for item in body["data"]] == ["UltraBook 14 Laptop"]


class TestCatalogEndpoints:
    async def test_categories_are_distinct_and_sorted(self, api):
        data = (await api.get("/api/v1/categories")).json()["data"]

        assert data == sorted(set(data))
        assert "Shoes/Women/Pumps" in data

    async def test_departments(self, api):
        data = (await api.get("/api/v1/departments")).json()["data"]

        assert set(data) == {
            "Appliances",
            "Electronics",
            "Fashion",
            "Home",
            "Mobiles",
            "Shoes",
            "Toys",
        }

    async def test_brands(self, api):
        assert "Guess" in (await api.get("/api/v1/brands")).json()["data"]

    async def test_deals(self, api):
        data = (await api.get("/api/v1/deals")).json()["data"]

        assert len(data) == 6
        assert data[0]["discountPercentage"] == 25
        assert "dealPrice" in data[0]
