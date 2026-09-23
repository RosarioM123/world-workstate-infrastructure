"""Interim API-key gate for write endpoints.

Full auth/RBAC is deferred per docs/adr/0006-auth-rbac-shape.md — the
`actor` field is self-asserted and proves nothing today. But a public
demo URL is exactly the ADR's trigger ("a second real party submits
intents"), so this module is the minimal gate: when WORLD_API_KEY is
set, the state-mutating routes (POST /intent, /entities, /rogue-attack)
require it as the X-API-Key header. Reads stay open so the demo remains
viewable.

When the variable is unset (local dev, tests), all routes stay open and
main.lifespan logs a warning. Denied callers get a 401 and no ledger row:
unlike an authenticated actor denied by policy (ADR 0006), an
unauthenticated caller has no identity worth auditing, and writing a row
for them would be the ledger graffiti this gate exists to prevent.
"""

import hmac
import logging
import os

from fastapi import Depends, Header, HTTPException

logger = logging.getLogger(__name__)


def expected_api_key() -> str | None:
    """The configured key, or None when auth is not configured."""
    key = os.environ.get("WORLD_API_KEY", "").strip()
    return key or None


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """FastAPI dependency: reject unauthenticated writes with a 401.

    Attach via ``dependencies=[Depends(require_api_key)]`` on the route
    decorator. Read at request time (not import time) so tests can
    toggle WORLD_API_KEY with monkeypatch.
    """
    expected = expected_api_key()
    if expected is None:
        return  # auth not configured: local dev / tests stay open
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "unauthorized",
                "message": "Missing or invalid X-API-Key header",
            },
        )


# Re-export for the common decorator spelling.
api_key_dependency = Depends(require_api_key)
