import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./user_profile.db")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "development-only-change-me")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]


settings = Settings()
