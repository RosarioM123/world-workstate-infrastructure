# WORLD — 2-Minute Demo Script

Perform live. Spoken lines are quoted; bracketed lines are stage directions (not spoken). Target pace: unhurried, ~130 words/min. Total spoken: ~270 words.

## Setup (do before the clock starts)

- `pip install -e .` done; run `uvicorn app:app`
- Browser open at `http://127.0.0.1:8000/demo`, scrolled to the intent form
- Second terminal tab ready with the `verify_chain()` one-liner from the README quickstart
- Say on the record that sample data is sample (it is labeled as such in the repo)

## The script

**[0:00 — to camera]**
"AI can generate work. What it can't do is keep a shared, verifiable record of that work as it moves between models, agents, humans, and time. WORLD is that record: a deterministic state ledger for AI agent work."

**[0:18 — to camera]**
"The loop is simple. Anyone — an agent, a human, a script — submits an intent: an entity, an action, and the change it wants. A constraint engine checks it and returns one of two verdicts: COMMITTED, or REJECTED. Every attempt, legal or rogue, is appended to a SHA-256 hash-chained ledger."

**[0:40 — dashboard; submit an ALLOCATE intent]**
"Live. I'll submit an ALLOCATE intent, moving capacity to a node. The engine validates: capacity can't go negative, node locks are respected, deltas must be real numbers — NaN and Infinity get rejected outright. It passes. COMMITTED. And the materialized state rebuilds deterministically from the ledger, so anyone replaying this history arrives at the same state."

**[1:05 — dashboard; fire the rogue-attack simulation]**
"Now the beat that matters. This fires the rogue-attack simulation — an intent engineered to break the rules, like driving liquidity negative. Verdict: REJECTED. But look at the ledger: the rejected attempt is still in there. In WORLD, even the attack is evidence. Nothing happens off the record."

**[1:32 — terminal; run verify_chain()]**
"And the ledger is tamper-evident. One call — verify_chain — walks every row and checks every hash against the one before it. If anyone rewrites history, it names the exact row that broke."

**[1:48 — to camera]**
"Intents in, verdicts out, everything on the record, replayable by anyone. That's WORLD — the shared memory AI work is missing."

## If the live demo breaks

- Dashboard won't load: fall back to the terminal. `POST /api/intent` with curl for the ALLOCATE, `POST /api/rogue-attack` for the rejection, `GET /api/state` to show the ledger. Same story, no visuals lost.
- Keep your energy on the REJECTED beat — the attack staying in the ledger is the memorable moment. That's the line judges repeat back.
