# User Profile Microservice

FastAPI service for account registration, JWT authentication, and profile management in the e-commerce platform.

## Features

- Account registration with a unique email and bcrypt password hashing
- JWT bearer-token login
- Protected profile read and update endpoints
- Input validation, meaningful HTTP error responses, and CORS support for the React UI
- Configurable SQLite (local default) or PostgreSQL database connection

## Run locally

Requirements: Python 3.12 and Pipenv.

```bash
pipenv sync --dev
pipenv run uvicorn app:app --reload --host 0.0.0.0 --port 9090
```

Open Swagger UI at `http://localhost:9090/docs`.

Copy `.env.example` to `.env` and replace `JWT_SECRET_KEY` before deployment. Environment variables are read when the service starts:

| Variable | Local default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./user_profile.db` | SQLAlchemy async database URL. PostgreSQL example: `postgresql+asyncpg://user:password@host:5432/users` |
| `JWT_SECRET_KEY` | development-only value | JWT signing key; must be changed outside local development |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access-token lifetime |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed frontend origins |

## API

| Method | Route | Authentication | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Service health check |
| `POST` | `/auth/register` | No | Create an account |
| `POST` | `/auth/login` | No | Receive a bearer JWT |
| `GET` | `/users/me` | Bearer token | Read the signed-in user's profile |
| `PUT` | `/users/me` | Bearer token | Update name, email, or mobile number |

Example registration request:

```json
{
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "mobile": "+905551112233",
  "password": "secure-password"
}
```

After login, send `Authorization: Bearer <access_token>` to the profile endpoints.

## Tests

```bash
pipenv run pytest
```

## Docker

```bash
docker build -t user-profile-service .
docker run --rm -p 9090:9090 --env-file .env user-profile-service
```
