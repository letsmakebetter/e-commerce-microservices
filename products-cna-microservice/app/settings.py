"""Configuration for the Product Service, read from the environment."""

import os

from dotenv import load_dotenv

load_dotenv()


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes"}


class Settings:
    service_name: str = "product-service"
    version: str = "1.0.0"

    # PostgreSQL holds the catalog itself (listings, categories, inventory).
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres@localhost:5432/products",
    )

    # Elasticsearch backs the full-text search endpoints.
    elastic_url: str = os.getenv("ELASTIC_URL", "http://localhost:9200")
    elastic_index: str = os.getenv("ELASTIC_INDEX", "products")
    elastic_username: str | None = os.getenv("ELASTIC_USERNAME") or None
    elastic_password: str | None = os.getenv("ELASTIC_PASSWORD") or None
    elastic_api_key: str | None = os.getenv("ELASTIC_APIKEY") or None
    elastic_timeout_seconds: float = _int("ELASTIC_TIMEOUT_MS", 5000) / 1000
    elastic_ping_timeout_seconds: float = _int("ELASTIC_PING_TIMEOUT_MS", 1500) / 1000
    elastic_max_retries: int = _int("ELASTIC_MAX_RETRIES", 1)

    default_page_size: int = _int("DEFAULT_PAGE_SIZE", 20)
    max_page_size: int = _int("MAX_PAGE_SIZE", 100)

    seed_on_start: bool = _bool("SEED_ON_START")

    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]


settings = Settings()
