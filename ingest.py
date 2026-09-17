"""
WORLD Day 1, Real-world data ingestion (ingest.py)

Pulls LIVE, free, no-key public data and pipes it through the deterministic
state ledger in engine.py.

Pipeline:
    FETCH (live public API) → NORMALIZE → INTENT → engine.execute_deterministic_transition

The mapping from observation → intent is a pure deterministic function.
The agent never touches state directly; the engine's hard constraints
decide COMMITTED vs REJECTED.

Feeds (no API keys, no premium data, no dependencies beyond stdlib):
    - Open-Meteo (https://open-meteo.com): current weather at the hub.
      Rotterdam is a real port city, high winds derate port capacity via a
      fixed, auditable rule. Weather is honest real-world exogenous shock.

Usage:
    python ingest.py            # live fetch → commit one weather-driven intent
    python ingest.py --dry-run  # live fetch → show the intent, write nothing
    python ingest.py --demo     # live fetch → commit intent → rogue agent
                                #   tries to break the rules and gets blocked

If the network is unavailable (e.g. mid-demo on stage), ingest falls back to
a clearly-labeled synthetic observation so the show always goes on.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import (  # noqa: E402
    IntentTransaction,
    connect_db,
    execute_deterministic_transition,
    get_entity,
    init_db,
)

# Rotterdam, NL, the seeded hub node in engine.py
HUB_LAT, HUB_LON = 51.95, 4.14
HUB_ENTITY_ID = "node_rotterdam_hub"
SOURCE = "open-meteo"

# Baseline capacity the derate rules are computed against. Derates are a
# fixed fraction of this baseline (not of current capacity), so repeated
# ingestion ticks accumulate linearly and auditably instead of compounding
# geometrically toward zero.
BASELINE_CAPACITY = 1000.0

# Deterministic derate rules: (min wind km/h, capacity derate fraction,
# cash delta, action label). Pure function of the observation, no LLM,
# no vibes, same input always yields the same intent.
WIND_RULES = [
    (75, 0.30, -5000.0, "STORM_DERATE"),
    (50, 0.15, -2000.0, "WIND_DERATE"),
]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_observations() -> None:
    """Append-only raw observation store. Raw data is never mutated."""
    with closing(connect_db()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_observations (
                observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_at TEXT NOT NULL,
                source TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                synthetic INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


def fetch_rotterdam_weather() -> tuple[dict, bool]:
    """
    Fetch current weather from Open-Meteo (free, no key).
    Returns (raw_payload, synthetic_flag).
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={HUB_LAT}&longitude={HUB_LON}"
        "&current=temperature_2m,wind_speed_10m,weather_code"
        "&wind_speed_unit=kmh&timezone=UTC"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "world-day1-ingest"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        return raw, False
    except (urllib.error.URLError, TimeoutError, OSError,
            json.JSONDecodeError) as exc:
        # Only network and parse failures trigger the offline fallback.
        # Anything else (a programming error) must raise loudly, never hide
        # behind synthetic data mid-demo.
        fallback = {
            "current": {
                "temperature_2m": 12.0,
                "wind_speed_10m": 62.0,
                "weather_code": 3,
                "time": _utcnow(),
            },
            "_fallback_reason": str(exc),
        }
        return fallback, True


def normalize_observation(raw: dict, synthetic: bool) -> dict:
    """Raw API payload → canonical observation. received_at is honest T0."""
    current = raw.get("current", {})
    return {
        "received_at": _utcnow(),  # system knowledge time, not the API's
        "source": SOURCE,
        "entity_id": HUB_ENTITY_ID,
        "location": {"lat": HUB_LAT, "lon": HUB_LON, "name": "Rotterdam"},
        "temperature_c": current.get("temperature_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
        "synthetic": synthetic,
    }


def store_raw_observation(obs: dict) -> int:
    """Append the raw observation. Never updated, never deleted."""
    with closing(connect_db()) as conn:
        cur = conn.execute(
            """
            INSERT INTO raw_observations
                (received_at, source, entity_id, payload, synthetic)
            VALUES (?, ?, ?, ?, ?)
            """,
            (obs["received_at"], obs["source"], obs["entity_id"],
             json.dumps(obs, sort_keys=True), int(obs["synthetic"])),
        )
        obs_id = cur.lastrowid
        conn.commit()
        return obs_id


def weather_to_intent(obs: dict) -> IntentTransaction:
    """
    Deterministic rule: observation → agent intent.
    Same weather in → same intent out, regardless of current capacity,
    because derates are computed against BASELINE_CAPACITY. The engine
    still has final say.
    """
    wind = obs.get("wind_speed_kmh") or 0.0

    for min_wind, derate, cash_delta, action in WIND_RULES:
        if wind >= min_wind:
            return IntentTransaction(
                entity_id=HUB_ENTITY_ID,
                action=action,
                requested_delta_capacity=-round(derate * BASELINE_CAPACITY, 2),
                requested_delta_cash=cash_delta,
            )
    # Calm weather: port earns, capacity untouched.
    return IntentTransaction(
        entity_id=HUB_ENTITY_ID,
        action="REVENUE_TICK",
        requested_delta_capacity=0.0,
        requested_delta_cash=8000.0,
    )


def ingest_live(dry_run: bool = False) -> dict:
    """One full tick: fetch → normalize → store → intent → engine verdict."""
    init_db()
    init_observations()

    raw, synthetic = fetch_rotterdam_weather()
    obs = normalize_observation(raw, synthetic)
    obs_id = None if dry_run else store_raw_observation(obs)
    intent = weather_to_intent(obs)

    result = (
        {"status": "DRY_RUN", "details": {"intent": intent.__dict__}}
        if dry_run
        else execute_deterministic_transition(intent)
    )
    return {
        "observation_id": obs_id,
        "observation": obs,
        "intent": intent.__dict__,
        "engine_result": result,
        "entity": get_entity(HUB_ENTITY_ID),
    }


def rogue_agent_attack() -> list[dict]:
    """
    The showstopper: a rogue agent proposes illegal state changes.
    Every one is REJECTED by hard code, and logged for the audit trail.
    """
    attacks = [
        IntentTransaction(HUB_ENTITY_ID, "ROGUE_DRAIN",
                          requested_delta_capacity=-999999.0,
                          requested_delta_cash=0.0),
        IntentTransaction(HUB_ENTITY_ID, "ROGUE_WITHDRAWAL",
                          requested_delta_capacity=0.0,
                          requested_delta_cash=-99999999.0),
        IntentTransaction("node_does_not_exist", "ROGUE_SPOOF",
                          requested_delta_capacity=10.0,
                          requested_delta_cash=10.0),
    ]
    outcomes = []
    for intent in attacks:
        # The engine never raises for policy violations: every illegal
        # intent comes back REJECTED and is appended to the ledger.
        verdict = execute_deterministic_transition(intent)
        outcomes.append({"intent": intent.__dict__, "verdict": verdict})
    return outcomes


def main() -> None:
    parser = argparse.ArgumentParser(description="WORLD Day 1: real-world ingest")
    parser.add_argument("--dry-run", action="store_true",
                        help="show the intent without writing to the ledger")
    parser.add_argument("--demo", action="store_true",
                        help="ingest live data, then unleash the rogue agent")
    args = parser.parse_args()

    tick = ingest_live(dry_run=args.dry_run)
    obs = tick["observation"]
    tag = "SYNTHETIC (offline fallback)" if obs["synthetic"] else "LIVE"

    print(f"[{tag}] {obs['source']} → {obs['location']['name']}: "
          f"wind {obs['wind_speed_kmh']} km/h, "
          f"{obs['temperature_c']}°C @ {obs['received_at']}")
    print(f"Intent: {tick['intent']['action']} "
          f"(Δcapacity={tick['intent']['requested_delta_capacity']}, "
          f"Δcash={tick['intent']['requested_delta_cash']})")
    print(f"Engine verdict: {tick['engine_result']['status']}")

    if not args.dry_run:
        e = tick["entity"]
        print(f"Ledger state: capacity={e['capacity']}, "
              f"liquidity={e['available_liquidity']}, status={e['status']}")

    if args.demo and not args.dry_run:
        print("\n--- ROGUE AGENT ATTACK (all blocked by hard code) ---")
        for outcome in rogue_agent_attack():
            action = outcome["intent"]["action"]
            verdict = outcome["verdict"]
            reason = verdict["details"].get("reason", "")
            print(f"{action}: {verdict['status']}, {reason}")


if __name__ == "__main__":
    main()
