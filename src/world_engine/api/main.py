"""
WORLD Day 1, YC demo backend (world_engine.api.main)

Ties the deterministic engine and the live data ingestor together behind a
FastAPI service with a built-in dark-mode dashboard.

    engine.py  → deterministic, append-only, hash-chained state ledger
    ingest.py  → live real-world feed (Open-Meteo, no API keys)

Run:
    pip install -e ".[test]"
    uvicorn app:app --reload
    → http://127.0.0.1:8000

API versions:
    /api/v1/*  - canonical routes (see world_engine/api/v1.py)
    /api/*     - deprecated aliases kept for the dashboard and existing
                 clients; they log a warning and will be removed in v0.3.0

Every response carries X-Request-ID, and every failure returns the uniform
error envelope defined in world_engine/api/middleware.py.

Demo flow:
    1. Dashboard shows live node capacity / liquidity.
    2. "Inject Real-World Feed" pulls live Rotterdam weather and pipes it
       through the constraint engine.
    3. "Rogue Agent Attack" fires illegal intents, every one REJECTED in red.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from world_engine.api.middleware import install as install_middleware
from world_engine.api.v1 import router as v1_router
from world_engine.core.engine import init_db
from world_engine.ingestion.client import init_observations

REPO_ROOT = Path(__file__).resolve().parents[3]
SITE_DIR = REPO_ROOT / "static" / "site"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    init_observations()
    app.state.landing_html = _load_landing_page()
    app.state.dashboard_html = _load_dashboard_page()
    yield


def serve() -> None:  # pragma: no cover - thin uvicorn wrapper
    """Run the API server. Entry point for the ``world-server`` console script."""
    import uvicorn

    uvicorn.run("world_engine.api.main:app", host="127.0.0.1", port=8000)


def _load_landing_page() -> str:
    """Load the landing page built from frontend/ (React + Sass).

    The page is a static Vite build committed under static/site/, so the
    app serves it with zero Node.js at runtime. To rebuild after editing
    frontend/:  cd frontend && npm install && npm run build
    """
    index = SITE_DIR / "index.html"
    try:
        return index.read_text(encoding="utf-8")
    except OSError:
        return (
            "<!DOCTYPE html><html><body style='font-family:monospace'>"
            "WORLD - landing page not built yet. Run "
            "<code>cd frontend && npm install && npm run build</code>, "
            "or open the <a href='/demo'>live demo</a>.</body></html>"
        )


def _load_dashboard_page() -> str:
    """Load the /demo dashboard from static/dashboard.html.

    The markup lives in a static file so app.py stays Python; it is read
    once at startup like the landing page.
    """
    page_path = REPO_ROOT / "static" / "dashboard.html"
    try:
        return page_path.read_text(encoding="utf-8")
    except OSError:
        return (
            "<!DOCTYPE html><html><body style='font-family:monospace'>"
            "WORLD dashboard unavailable - try <a href='/api/v1/state'>/api/v1/state</a>"
            "</body></html>"
        )


app = FastAPI(title="WORLD Deterministic State Kernel", lifespan=lifespan)

install_middleware(app)

# Canonical versioned routes, plus deprecated unversioned aliases.
app.include_router(v1_router, prefix="/api/v1", tags=["v1"])
app.include_router(v1_router, prefix="/api", tags=["deprecated"], deprecated=True)

# Hashed JS/CSS for the React landing page (static/site/assets/*).
if SITE_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=SITE_DIR / "assets"), name="site-assets")


@app.get("/", response_class=HTMLResponse)
def landing() -> str:
    """Landing page (React build in static/site/). The live dashboard is at /demo."""
    return app.state.landing_html


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe for the hosting platform. Touches no database."""
    return {"status": "ok"}


@app.get("/demo", response_class=HTMLResponse)
def dashboard() -> str:
    """High-contrast, YC-ready control center UI."""
    return app.state.dashboard_html
