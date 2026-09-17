"""
WORLD Day 1 — YC demo backend (app.py)

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
    3. "Rogue Agent Attack" fires illegal intents — every one REJECTED in red.
"""

import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from engine import (
    DB_PATH,
    IntentTransaction,
    execute_deterministic_transition,
    init_db,
)
from ingest import ingest_live, init_observations, rogue_agent_attack


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_observations()
    yield


app = FastAPI(title="WORLD Deterministic State Kernel", lifespan=lifespan)


@app.get("/api/state")
def get_world_state():
    """Current materialized state + recent immutable ledger entries."""
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()
    return {"entities": entities, "recent_ledger": ledger}


class IntentRequest(BaseModel):
    entity_id: str
    action: str
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


@app.get("/", response_class=HTMLResponse)
def dashboard():
    """High-contrast, YC-ready control center UI."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>WORLD | Deterministic State Kernel</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-zinc-950 text-zinc-100 font-mono min-h-screen p-8">
        <div class="max-w-6xl mx-auto space-y-8">
            <div class="flex justify-between items-center border-b border-zinc-800 pb-4">
                <div>
                    <h1 class="text-2xl font-bold tracking-tight text-white">WORLD // State Kernel</h1>
                    <p class="text-xs text-zinc-400">Zero-trust deterministic infrastructure + live real-world ingestion</p>
                </div>
                <div class="space-x-4">
                    <button onclick="triggerIngest()" class="bg-emerald-600 hover:bg-emerald-500 text-white text-sm px-4 py-2 rounded font-semibold transition">
                        ⚡ Inject Real-World Feed
                    </button>
                    <button onclick="fetchState()" class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm px-4 py-2 rounded transition">
                        🔄 Refresh State
                    </button>
                </div>
            </div>

            <div id="banner" class="hidden text-xs px-4 py-3 rounded border"></div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-zinc-900 border border-zinc-800 rounded-lg p-6 space-y-4">
                    <h2 class="text-sm font-semibold uppercase tracking-wider text-zinc-400">Core Node State</h2>
                    <div id="entity-container" class="space-y-3">
                        <p class="text-xs text-zinc-500 animate-pulse">Loading node state...</p>
                    </div>
                </div>

                <div class="bg-zinc-900 border border-zinc-800 rounded-lg p-6 space-y-4">
                    <h2 class="text-sm font-semibold uppercase tracking-wider text-zinc-400">Test Hallucination Guardrail</h2>
                    <p class="text-xs text-zinc-400">Fire intents at the math engine. Illegal ones are blocked and logged as <span class="text-red-400 font-bold">REJECTED</span>.</p>
                    <div class="flex gap-4 pt-2">
                        <button onclick="testIntent(-5000, 0)" class="flex-1 bg-red-950/50 border border-red-800 hover:bg-red-900 text-red-200 text-xs py-2 px-3 rounded transition">
                            Illegal Drain (-5k Cap)
                        </button>
                        <button onclick="testIntent(-50, 1000)" class="flex-1 bg-blue-950/50 border border-blue-800 hover:bg-blue-900 text-blue-200 text-xs py-2 px-3 rounded transition">
                            Valid Reallocation
                        </button>
                    </div>
                    <button onclick="rogueAttack()" class="w-full bg-red-900/60 border border-red-700 hover:bg-red-800 text-red-100 text-xs py-2 px-3 rounded font-bold transition">
                        🤖 Unleash Rogue Agent (3 illegal attacks)
                    </button>
                </div>
            </div>

            <div class="bg-zinc-900 border border-zinc-800 rounded-lg p-6 space-y-4">
                <h2 class="text-sm font-semibold uppercase tracking-wider text-zinc-400">Immutable Ledger Log (T0 appended, hash-chained)</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="border-b border-zinc-800 text-zinc-500">
                            <tr>
                                <th class="pb-2">ID</th>
                                <th class="pb-2">Timestamp (T0)</th>
                                <th class="pb-2">Entity</th>
                                <th class="pb-2">Action</th>
                                <th class="pb-2">Status</th>
                                <th class="pb-2">Hash</th>
                            </tr>
                        </thead>
                        <tbody id="ledger-table" class="divide-y divide-zinc-800/50">
                            <tr><td colspan="6" class="py-3 text-zinc-500 animate-pulse">Connecting to ledger...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            function showBanner(text, ok) {
                const b = document.getElementById('banner');
                b.classList.remove('hidden');
                b.className = 'text-xs px-4 py-3 rounded border ' + (ok
                    ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
                    : 'bg-red-950/60 border-red-800 text-red-300');
                b.textContent = text;
            }

            async function fetchState() {
                const res = await fetch('/api/state');
                const data = await res.json();

                document.getElementById('entity-container').innerHTML = data.entities.map(e => `
                    <div class="bg-zinc-950 p-4 rounded border border-zinc-800 flex justify-between items-center">
                        <div>
                            <span class="text-emerald-400 font-bold">${e.entity_id}</span>
                            <div class="text-xs text-zinc-400 mt-1">Status: <span class="text-white">${e.status}</span></div>
                            <div class="text-[10px] text-zinc-500 mt-1">updated ${e.last_updated}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-sm">Capacity: <span class="text-zinc-200">${Number(e.capacity).toLocaleString()}</span></div>
                            <div class="text-xs text-zinc-400">Liquidity: $${Number(e.available_liquidity).toLocaleString()}</div>
                        </div>
                    </div>
                `).join('');

                document.getElementById('ledger-table').innerHTML = data.recent_ledger.map(tx => `
                    <tr class="hover:bg-zinc-800/20">
                        <td class="py-2 font-mono text-zinc-500">#${tx.transaction_id}</td>
                        <td class="py-2 text-zinc-400">${tx.timestamp}</td>
                        <td class="py-2 text-zinc-300">${tx.entity_id}</td>
                        <td class="py-2 text-zinc-300">${tx.action}</td>
                        <td class="py-2">
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${tx.status === 'COMMITTED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-red-950 text-red-400 border border-red-800'}">
                                ${tx.status}
                            </span>
                        </td>
                        <td class="py-2 font-mono text-zinc-600">${tx.record_hash.slice(0, 8)}</td>
                    </tr>
                `).join('');
            }

            async function triggerIngest() {
                const res = await fetch('/api/trigger-ingest', { method: 'POST' });
                const data = await res.json();
                showBanner(
                    `Feed: ${data.source}${data.synthetic ? ' (synthetic fallback)' : ' (LIVE)'} — wind ${data.wind_kmh} km/h → ${data.intent}: ${data.engine_verdict}`,
                    data.engine_verdict === 'COMMITTED'
                );
                fetchState();
            }

            async function testIntent(deltaCap, deltaCash) {
                const res = await fetch('/api/intent', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        entity_id: "node_rotterdam_hub",
                        action: "MANUAL_TEST_INTENT",
                        delta_capacity: deltaCap,
                        delta_cash: deltaCash
                    })
                });
                const data = await res.json();
                showBanner(
                    `MANUAL_TEST_INTENT (Δcap=${deltaCap}, Δcash=${deltaCash}): ${data.status} — ${data.details.reason}`,
                    data.status === 'COMMITTED'
                );
                fetchState();
            }

            async function rogueAttack() {
                const res = await fetch('/api/rogue-attack', { method: 'POST' });
                const data = await res.json();
                const blocked = data.attacks.filter(a => a.verdict.status === 'REJECTED').length;
                showBanner(
                    `Rogue agent fired ${data.attacks.length} illegal intents — ${blocked} blocked by hard code. ` +
                    data.attacks.map(a => `${a.intent.action}:${a.verdict.status}`).join(' · '),
                    blocked === data.attacks.length
                );
                fetchState();
            }

            fetchState();
            setInterval(fetchState, 5000);
        </script>
    </body>
    </html>
    """
