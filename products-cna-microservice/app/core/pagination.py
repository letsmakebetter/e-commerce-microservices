"""Shared page/limit handling, identical to the other services."""

from __future__ import annotations

from dataclasses import dataclass

from app.settings import settings


@dataclass(frozen=True)
class Page:
    page: int
    limit: int
    offset: int


def resolve_page(page: int | None, limit: int | None) -> Page:
    resolved_page = max(1, page or 1)
    resolved_limit = min(max(1, limit or settings.default_page_size), settings.max_page_size)
    return Page(
        page=resolved_page,
        limit=resolved_limit,
        offset=(resolved_page - 1) * resolved_limit,
    )


def pagination_meta(page: Page, total: int) -> dict:
    total_pages = (total + page.limit - 1) // page.limit if page.limit else 0
    return {
        "page": page.page,
        "limit": page.limit,
        "total": total,
        "totalPages": total_pages,
        "hasNextPage": page.page < total_pages,
        "hasPreviousPage": page.page > 1 and total > 0,
    }
