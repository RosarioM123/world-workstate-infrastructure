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
import os
import threading
import time
import uuid
from collections import deque
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


# ---------------------------------------------------------------------------
# Rate limiting: per-IP sliding-window token bucket on the write routes.
#
# stdlib-only by design (the project keeps the server stdlib-pure outside
# fastapi/uvicorn). Buckets live in memory, so limits are per-process: fine
# for the single-worker demo service, not for a multi-worker deployment.
# Set WORLD_RATE_LIMIT_ENABLED=0 to disable (e.g. for load tests).
# ---------------------------------------------------------------------------

_RATE_WINDOW_S = 60.0

# Canonical route -> (env var overriding the limit, default reqs per window).
# The deprecated /api/* aliases are normalized to /api/v1/* before lookup,
# so both mounts share one bucket.
_WRITE_LIMITS: dict[str, tuple[str, int]] = {
    "/api/v1/intent": ("WORLD_RATE_LIMIT_INTENT_PER_MIN", 120),
    "/api/v1/entities": ("WORLD_RATE_LIMIT_ENTITY_PER_MIN", 60),
    "/api/v1/rogue-attack": ("WORLD_RATE_LIMIT_ROGUE_PER_MIN", 5),
}

_rate_buckets: dict[tuple[str, str], deque[float]] = {}
_rate_lock = threading.Lock()


def reset_rate_limiter() -> None:
    """Clear all rate-limit buckets. Used by tests; not part of the API."""
    with _rate_lock:
        _rate_buckets.clear()


def _canonical_write_route(path: str) -> str | None:
    """Map a request path to its canonical write route, or None if unrated."""
    if path.startswith("/api/") and not path.startswith("/api/v1"):
        path = "/api/v1" + path[len("/api") :]
    return path if path in _WRITE_LIMITS else None


def _client_ip(request: Request) -> str:
    # Behind Render (or any proxy) the real client is in X-Forwarded-For.
    # Trusting it lets a hostile client rotate IPs, but the alternative is
    # rate-limiting the whole proxy as one client; for a demo gate this is
    # the standard tradeoff.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()[:64]
    return request.client.host if request.client else "unknown"


def _check_rate_limit(request: Request) -> JSONResponse | None:
    """Return a 429 envelope when the caller is over budget, else None."""
    if os.environ.get("WORLD_RATE_LIMIT_ENABLED", "1") != "1":
        return None
    if request.method != "POST":
        return None
    route = _canonical_write_route(request.url.path)
    if route is None:
        return None
    env_var, default = _WRITE_LIMITS[route]
    try:
        limit = int(os.environ.get(env_var, str(default)))
    except ValueError:
        limit = default
    if limit <= 0:
        return None

    key = (_client_ip(request), route)
    now = time.monotonic()
    with _rate_lock:
        bucket = _rate_buckets.setdefault(key, deque())
        cutoff = now - _RATE_WINDOW_S
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            retry_after = max(1, int(bucket[0] + _RATE_WINDOW_S - now) + 1)
            response = error_envelope(
                "rate_limited",
                "Rate limit exceeded for this endpoint; try again later.",
                429,
            )
            response.headers["Retry-After"] = str(retry_after)
            return response
        bucket.append(now)
        # Opportunistic memory bound: drop fully-expired buckets when the
        # table grows past a few thousand distinct (ip, route) pairs.
        if len(_rate_buckets) > 4096:
            expired = [k for k, b in _rate_buckets.items() if not b or b[-1] <= cutoff]
            for k in expired:
                del _rate_buckets[k]
    return None


def install(app: FastAPI) -> None:
    """Attach middleware and exception handlers to the application."""

    # Registered first so it runs *inside* request_context below: the
    # 429 envelope then carries the request ID like every other failure.
    @app.middleware("http")
    async def rate_limit(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        limited = _check_rate_limit(request)
        if limited is not None:
            return limited
        return await call_next(request)

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
