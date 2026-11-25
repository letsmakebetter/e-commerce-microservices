"""The error envelope every service of the platform returns.

Documented in docs/api-contracts/error-format.md.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    """An error with an HTTP status and a stable, machine readable code."""

    def __init__(self, status: int, code: str, message: str, details=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details

    @classmethod
    def bad_request(cls, message: str, details=None) -> "ApiError":
        return cls(400, "VALIDATION_ERROR", message, details)

    @classmethod
    def not_found(cls, message: str = "Resource not found") -> "ApiError":
        return cls(404, "NOT_FOUND", message)

    @classmethod
    def conflict(cls, message: str, details=None) -> "ApiError":
        return cls(409, "CONFLICT", message, details)

    @classmethod
    def service_unavailable(cls, message: str = "A dependency is unavailable") -> "ApiError":
        return cls(503, "SERVICE_UNAVAILABLE", message)


def error_body(request: Request, code: str, message: str, details=None) -> dict:
    body: dict = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    body["requestId"] = getattr(request.state, "request_id", None)
    return body


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status,
            content=error_body(request, exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError):
        details = [
            {
                # Drop the "body"/"query" prefix so the field name matches the
                # one the client sent.
                "field": ".".join(str(part) for part in error["loc"][1:]) or str(error["loc"][0]),
                "message": error["msg"],
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content=error_body(request, "VALIDATION_ERROR", "Request validation failed", details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException):
        code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(request, code, str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception):
        # Never leak a driver message or a stack trace to the client.
        return JSONResponse(
            status_code=500,
            content=error_body(
                request, "INTERNAL_SERVER_ERROR", "An unexpected error occurred"
            ),
        )
