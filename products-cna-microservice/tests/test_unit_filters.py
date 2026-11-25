"""Unit tests for the catalog filter and sort builders. No database needed."""

from decimal import Decimal

from app.core.pagination import pagination_meta, resolve_page
from app.repositories.filters import build_conditions, build_order_by, _escape_like


class TestBuildConditions:
    def test_no_parameters_means_no_filtering(self):
        assert build_conditions() == []

    def test_each_parameter_adds_one_condition(self):
        assert len(build_conditions(q="laptop")) == 1
        assert len(build_conditions(category="Shoes")) == 1
        assert len(build_conditions(min_price=Decimal("5"), max_price=Decimal("9"))) == 2

    def test_price_bounds_are_independent(self):
        assert len(build_conditions(min_price=Decimal("5"))) == 1
        assert len(build_conditions(max_price=Decimal("9"))) == 1

    def test_in_stock_both_ways(self):
        assert len(build_conditions(in_stock=True)) == 1
        assert len(build_conditions(in_stock=False)) == 1

    def test_in_stock_none_is_not_a_filter(self):
        assert build_conditions(in_stock=None) == []


class TestEscaping:
    def test_like_wildcards_from_the_client_are_escaped(self):
        # Otherwise a search for "100%" would match everything.
        assert _escape_like("100%") == "100\\%"
        assert _escape_like("a_b") == "a\\_b"
        assert _escape_like("back\\slash") == "back\\\\slash"

    def test_escaping_leaves_ordinary_text_alone(self):
        assert _escape_like("Evening Pumps") == "Evening Pumps"


class TestBuildOrderBy:
    def test_default_is_newest_first(self):
        assert [str(clause) for clause in build_order_by(None)] == [
            "products.last_updated DESC",
            "products.id ASC",
        ]

    def test_leading_minus_sorts_descending(self):
        assert str(build_order_by("-price")[0]) == "products.price DESC"
        assert str(build_order_by("price")[0]) == "products.price ASC"

    def test_unknown_field_falls_back_instead_of_crashing(self):
        assert "last_updated" in str(build_order_by("nonsense")[0])

    def test_id_is_always_the_tie_breaker(self):
        # Without this, two products with the same price can swap places
        # between page 1 and page 2, so one is shown twice and another never.
        for sort in ["price", "-price", "rating", "title", "-lastUpdated", None]:
            assert str(build_order_by(sort)[-1]) == "products.id ASC"


class TestPagination:
    def test_defaults(self):
        page = resolve_page(None, None)
        assert (page.page, page.limit, page.offset) == (1, 20, 0)

    def test_offset_follows_page_and_limit(self):
        assert resolve_page(3, 10).offset == 20

    def test_limit_is_capped(self):
        assert resolve_page(1, 100_000).limit == 100

    def test_nonsense_values_fall_back_to_defaults(self):
        assert resolve_page(-5, 0).page == 1
        assert resolve_page(0, None).page == 1

    def test_meta_for_a_middle_page(self):
        assert pagination_meta(resolve_page(2, 10), 35) == {
            "page": 2,
            "limit": 10,
            "total": 35,
            "totalPages": 4,
            "hasNextPage": True,
            "hasPreviousPage": True,
        }

    def test_meta_for_an_empty_result(self):
        meta = pagination_meta(resolve_page(1, 10), 0)
        assert meta["totalPages"] == 0
        assert meta["hasNextPage"] is False
        assert meta["hasPreviousPage"] is False
