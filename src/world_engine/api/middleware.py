"""Request ID, structured access logging, and the JSON error envelope.

Every response carries an X-Request-ID header (echoing the caller's value
when one is supplied). Every failure, including validation errors,
unhandled exceptions, and 404s, returns the same envelope:

    {"error": {"code": "<machine-readable code>",
               "message": "<human-readable text>",
               "request_id": "<id or null>"}}
"""

import json
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

request_id_ctx: ContextVar[str] = ContextVar("world_request_id", default="")

_STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
}


def error_envelope(code: str, message: str, status: int) -> JSONResponse:
    """Build the uniform failure payload for any status code."""
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id_ctx.get() or None,
            }
        },
    )


def install(app: FastAPI) -> None:
    """Attach middleware and exception handlers to the application."""

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request_id_ctx.set(rid)
        path = request.url.path
        if path.startswith("/api/") and not path.startswith("/api/v1"):
            logger.warning(
                json.dumps(
                    {
                        "event": "deprecated_route",
                        "request_id": rid,
                        "method": request.method,
                        "path": path,
                        "hint": "use /api/v1/* instead",
                    }
                )
            )
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = rid
        logger.info(
            json.dumps(
                {
                    "event": "request",
                    "request_id": rid,
                    "method": request.method,
                    "path": path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
        )
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        # Handlers may pass {"code": ..., "message": ...} as the detail to
        # get a semantic error code; otherwise derive one from the status.
        detail = exc.detail
        if isinstance(detail, dict):
            code = str(detail.get("code", "http_error"))
            message = str(detail.get("message", ""))
        else:
            code = _STATUS_CODES.get(exc.status_code, "http_error")
            message = str(detail)
        return error_envelope(code, message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_envelope("validation_error", "Request body failed validation", 422)

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            json.dumps(
                {
                    "event": "unhandled_exception",
                    "request_id": request_id_ctx.get() or None,
                    "path": request.url.path,
                }
            )
        )
        return error_envelope("internal_error", "Internal server error", 500)
