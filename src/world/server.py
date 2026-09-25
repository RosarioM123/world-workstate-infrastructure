"""HTTP server for the WORLD primitive.

Wraps a :class:`~world.core.World` with an API-key gate and per-IP rate
limiting on writes. Invariants are declared once here so every remote writer
is judged by the same rules — the server is the uniform-enforcement point
that in-process callables alone cannot provide.
"""

from __future__ import annotations

import hmac
import logging
import time
from collections import deque
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .core import ConflictError, Invariant, InvariantViolation, World

log = logging.getLogger("world.server")


def create_app(
    name: str,
    *,
    dir: str | None = None,
    invariants: list[Invariant] | tuple[Invariant, ...] = (),
    api_key: str | None = None,
    write_limit_per_min: int = 60,
    trust_forwarded_for: bool = False,
) -> FastAPI:
    work = World(name, dir=dir, invariants=invariants)
    app = FastAPI(title="world", version="0.2.0")

    if api_key:
        log.info("API-key gate enabled for world %r", name)
    else:
        log.warning("WORLD_API_KEY not set: write endpoints are unauthenticated")

    _hits: dict[str, deque[float]] = {}
    _last_sweep = 0.0

    def _client_ip(request: Request) -> str:
        # X-Forwarded-For is client-controlled: honor it only behind a
        # trusted reverse proxy that sets it. Otherwise any client can
        # spoof a fresh IP per request and walk past the rate limit.
        if trust_forwarded_for:
            fwd = request.headers.get("x-forwarded-for")
            if fwd:
                return fwd.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _sweep(now: float) -> None:
        # Bound _hits by dropping IPs with no hits inside the current
        # window. Runs at most once a minute so eviction never becomes a
        # per-request cost.
        nonlocal _last_sweep
        if now - _last_sweep < 60:
            return
        _last_sweep = now
        stale = [ip for ip, dq in _hits.items() if not dq or dq[-1] <= now - 60]
        for ip in stale:
            del _hits[ip]

    def _rate_limited(ip: str) -> bool:
        if write_limit_per_min <= 0:
            return False
        now = time.monotonic()
        _sweep(now)
        dq = _hits.setdefault(ip, deque())
        while dq and dq[0] <= now - 60:
            dq.popleft()
        if len(dq) >= write_limit_per_min:
            return True
        dq.append(now)
        return False

    async def _guard(request: Request) -> JSONResponse | None:
        """Auth + rate limit for write routes. Returns a response to short-circuit."""
        if api_key is not None:
            got = request.headers.get("x-api-key", "")
            if not hmac.compare_digest(got, api_key):
                return JSONResponse(
                    status_code=401,
                    content={"error": "unauthorized", "hint": "provide X-API-Key"},
                )
        if _rate_limited(_client_ip(request)):
            return JSONResponse(
                status_code=429,
                content={"error": "rate_limited", "retry_after": 60},
                headers={"Retry-After": "60"},
            )
        return None

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "world": work.name, "version": work.version}

    @app.get("/v1/state")
    def get_state(
        version: int | None = None, checkpoint: str | None = None
    ) -> JSONResponse:
        if version is not None and checkpoint is not None:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "bad_request",
                    "detail": "version or checkpoint, not both",
                },
            )
        seq = work.version
        if checkpoint is not None:
            cps = {c["name"]: c["seq"] for c in work.checkpoints()}
            if checkpoint not in cps:
                return JSONResponse(
                    status_code=404,
                    content={
                        "error": "not_found",
                        "detail": f"unknown checkpoint {checkpoint!r}",
                    },
                )
            seq = cps[checkpoint]
        elif version is not None:
            seq = version
        try:
            state = work.state(version=seq)
        except KeyError as e:
            return JSONResponse(
                status_code=404, content={"error": "not_found", "detail": str(e)}
            )
        return JSONResponse(status_code=200, content={"version": seq, "state": state})

    @app.post("/v1/update")
    async def post_update(request: Request) -> JSONResponse:
        denied = await _guard(request)
        if denied is not None:
            return denied
        body = await request.json()
        if not isinstance(body.get("state"), dict):
            return JSONResponse(
                status_code=400,
                content={"error": "bad_request", "detail": "state must be an object"},
            )
        try:
            seq = work.update(
                body["state"],
                actor=body.get("actor"),
                note=body.get("note", ""),
                expected_version=body.get("expected_version"),
                idempotency_key=body.get("idempotency_key"),
            )
        except ConflictError as e:
            return JSONResponse(
                status_code=409, content={"error": "conflict", "detail": str(e)}
            )
        except InvariantViolation as e:
            return JSONResponse(
                status_code=422,
                content={"seq": e.seq, "status": "REJECTED", "reason": e.reason},
            )
        return JSONResponse(
            status_code=200, content={"seq": seq, "status": "COMMITTED"}
        )

    @app.post("/v1/checkpoint")
    async def post_checkpoint(request: Request) -> JSONResponse:
        denied = await _guard(request)
        if denied is not None:
            return denied
        body = await request.json()
        cp_name = body.get("name", "")
        try:
            seq = work.checkpoint(cp_name)
        except ValueError as e:
            return JSONResponse(
                status_code=400, content={"error": "bad_request", "detail": str(e)}
            )
        return JSONResponse(status_code=200, content={"name": cp_name, "seq": seq})

    @app.post("/v1/resume")
    async def post_resume(request: Request) -> JSONResponse:
        denied = await _guard(request)
        if denied is not None:
            return denied
        body = await request.json()
        try:
            seq = work.resume(
                body.get("name", ""), actor=body.get("actor"), note=body.get("note")
            )
        except KeyError as e:
            return JSONResponse(
                status_code=404, content={"error": "not_found", "detail": str(e)}
            )
        except InvariantViolation as e:
            return JSONResponse(
                status_code=422,
                content={"seq": e.seq, "status": "REJECTED", "reason": e.reason},
            )
        return JSONResponse(
            status_code=200, content={"seq": seq, "status": "COMMITTED"}
        )

    @app.get("/v1/history")
    def get_history(limit: int | None = None) -> dict[str, Any]:
        return {"history": work.history(limit=limit)}

    @app.get("/v1/proposals/{seq}")
    def get_proposal(seq: int) -> JSONResponse:
        try:
            proposal = work.proposal(seq)
        except KeyError as e:
            return JSONResponse(
                status_code=404, content={"error": "not_found", "detail": str(e)}
            )
        return JSONResponse(status_code=200, content={"proposal": proposal})

    @app.get("/v1/checkpoints")
    def get_checkpoints() -> dict[str, Any]:
        return {"checkpoints": work.checkpoints()}

    @app.get("/v1/verify")
    def get_verify() -> dict[str, Any]:
        return {"ok": work.verify()}

    return app
