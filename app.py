"""
WORLD Day 1, YC demo backend (app.py)

Ties the deterministic engine and the live data ingestor together behind a
FastAPI service with a built-in dark-mode dashboard.

    engine.py  → deterministic, append-only, hash-chained state ledger
    ingest.py  → live real-world feed (Open-Meteo, no API keys)

Run:
    pip install fastapi uvicorn
    uvicorn app:app --reload
    → http://127.0.0.1:8000

Demo flow:
    1. Dashboard shows live node capacity / liquidity.
    2. "Inject Real-World Feed" pulls live Rotterdam weather and pipes it
       through the constraint engine.
    3. "Rogue Agent Attack" fires illegal intents, every one REJECTED in red.
"""

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from engine import (
    IntentTransaction,
    connect_db,
    execute_deterministic_transition,
    init_db,
)
from ingest import ingest_live, init_observations, rogue_agent_attack


SITE_DIR = Path(__file__).resolve().parent / "static" / "site"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_observations()
    app.state.landing_html = _load_landing_page()
    app.state.dashboard_html = _load_dashboard_page()
    yield


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
            "WORLD — landing page not built yet. Run "
            "<code>cd frontend && npm install && npm run build</code>, "
            "or open the <a href='/demo'>live demo</a>.</body></html>"
        )


def _load_dashboard_page() -> str:
    """Load the /demo dashboard from static/dashboard.html.

    The markup lives in a static file so app.py stays Python; it is read
    once at startup like the landing page.
    """
    page_path = Path(__file__).resolve().parent / "static" / "dashboard.html"
    try:
        return page_path.read_text(encoding="utf-8")
    except OSError:
        return (
            "<!DOCTYPE html><html><body style='font-family:monospace'>"
            "WORLD dashboard unavailable — try <a href='/api/state'>/api/state</a>"
            "</body></html>"
        )


app = FastAPI(title="WORLD Deterministic State Kernel", lifespan=lifespan)

# Hashed JS/CSS for the React landing page (static/site/assets/*).
if SITE_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=SITE_DIR / "assets"),
              name="site-assets")


@app.get("/", response_class=HTMLResponse)
def landing():
    """Landing page (React build in static/site/). The live dashboard is at /demo."""
    return app.state.landing_html


@app.get("/health")
def health():
    """Liveness probe for the hosting platform. Touches no database."""
    return {"status": "ok"}


@app.get("/api/state")
def get_world_state():
    """Current materialized state + recent tamper-evident ledger entries."""
    conn = connect_db()
    try:
        conn.row_factory = sqlite3.Row
        entities = [dict(r) for r in conn.execute("SELECT * FROM entities")]
        ledger = [
            dict(r)
            for r in conn.execute(
                "SELECT transaction_id, timestamp, entity_id, action, status,"
                " record_hash FROM state_ledger"
                " ORDER BY transaction_id DESC LIMIT 10"
            )
        ]
    finally:
        conn.close()
    return {"entities": entities, "recent_ledger": ledger}


class IntentRequest(BaseModel):
    entity_id: str = Field(max_length=64)
    action: str = Field(max_length=128)
    delta_capacity: float
    delta_cash: float


@app.post("/api/intent")
def post_intent(req: IntentRequest):
    """Any agent (or human) submits an intent; the math engine decides."""
    try:
        intent = IntentTransaction(
            entity_id=req.entity_id,
            action=req.action,
            requested_delta_capacity=req.delta_capacity,
            requested_delta_cash=req.delta_cash,
        )
        return execute_deterministic_transition(intent)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/trigger-ingest")
def trigger_ingest():
    """Pull the live real-world feed and pipe it through the ledger."""
    tick = ingest_live()
    return {
        "status": "Ingestion cycle complete",
        "source": tick["observation"]["source"],
        "synthetic": tick["observation"]["synthetic"],
        "wind_kmh": tick["observation"]["wind_speed_kmh"],
        "intent": tick["intent"]["action"],
        "engine_verdict": tick["engine_result"]["status"],
    }


@app.post("/api/rogue-attack")
def trigger_rogue_attack():
    """Unleash the rogue agent. Every illegal intent must come back REJECTED."""
    return {"attacks": rogue_agent_attack()}


@app.get("/demo", response_class=HTMLResponse)
def dashboard():
    """High-contrast, YC-ready control center UI."""
    return app.state.dashboard_html
