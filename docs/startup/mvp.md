# WORLD — MVP Definition

**Date:** 2026-09-21 · **Mission:** Day 4 of 10, startup validation program (WORLD)
**Builds on:** `docs/startup/wedge-research.md` (09-18, the Maya wedge), `docs/startup/week1-review.md` (09-20, verdict: convention before infrastructure)
**Status:** Definition document. Nothing in this doc is a build instruction for platform code. The MVP below is deliberately *not* the backend already in this repo (`app.py`, ingest, dashboard) — the week-1 review demoted that backend to **experiment harness** until the convention earns its keep.

## TL;DR

The smallest possible WORLD MVP is a **file convention, not a platform**: a structured handoff bundle (`WORLD.md` + `world-state.json`) that lives in the developer's repo, written by the agent at session end, read by every successor session before anything else. It carries only the governance that narrative formats lose — decisions with rationale, assumptions with confidence, open questions, binding guardrails — projected from a minimal subset of the v0.1 state model. If the convention alone beats summary and transcript baselines in a real coding workflow, *that* earns the right to build infrastructure. If not, the honest outcome is a documented convention or nothing.

---

## 1. The user

**Maya, senior backend engineer at a 12-person startup** (per the wedge doc — a persona, not an interviewed customer; that gap is marked in §8). She pair-programs with an AI coding agent 3–6 sessions a day on a real repo, across days and weeks, sometimes switching agent tools, sometimes handing branches to teammates. She already pays for agent tooling and loses ~20 minutes of re-orientation per new session plus mid-session derailments after context compaction.

The MVP serves Maya **in the single session boundary**: the end of one session writing state, the start of the next session reading it.

## 2. The input

At session end, the input is **what happened in the session**: the agent's own working memory of the conversation, tool calls, and code changes. The MVP defines one capture contract:

- The agent emits **state-change events**, not a narrative: new decisions made, decisions superseded, assumptions added/validated/invalidated, questions opened/answered, guardrails set.
- No new tooling is required for the MVP: the agent reads the session transcript and produces the events. The contract is a *prompt/format spec*, not an API.
- If the agent cannot derive events reliably from the transcript, that is itself the falsifying signal (see §8): the write side is the existential risk and it must be tested, not assumed.

## 3. Canonical state (the smallest ontology that preserves governance)

The MVP uses a **subset** of `docs/state-model.md` v0.1 — only the entities experiment #001 proved load-bearing. Everything else is deferred until a handoff experiment shows it prevents loss.

| Entity | Kept? | MVP fields |
|---|---|---|
| `Decision` | **Yes** | `id`, `statement`, `rationale`, `status` (accepted \| superseded \| reversed), `supersedes_id?`, provenance (`created_by`, `created_at`, `source`) |
| `Assumption` | **Yes** | `id`, `statement`, `confidence` (low \| medium \| high), `status` (active \| validated \| invalidated \| stale), provenance |
| `Question` | **Yes** | `id`, `question`, `status` (open \| answered \| dropped), `blocks_task_id?`, provenance |
| `Guardrail` (binding constraint) | **Yes** | `id`, `rule`, `set_by`, `scope`, provenance — experiment #001's transcript condition dropped a guardrail; this entity exists because of that measured failure |
| `StateChange` (append-only log) | **Yes, minimal** | `seq`, `entity_id`, `change`, `before?`, `after`, `actor`, `timestamp`, `reason?` — current state is a projection; nothing overwrites |
| `Project` context | **Yes, partial** | `goal`, `scope`, `constraints[]`, `definition_of_done` — enough for a successor to orient |
| `Task` | **No** — the repo's issue tracker/branch already carries task state; duplicating it adds write-side burden with no measured handoff value |
| `Evidence`, `Artifact`, `Action` | **No** — defer until a handoff experiment shows their absence causes loss |

Design rules inherited from the state model: provenance on every entity, supersede-don't-overwrite, state derived from history.

## 4. State transitions

The MVP has exactly four transitions. No more until usage demands them.

1. **Session start → `read`:** the agent loads `WORLD.md` (human-readable bundle) and `world-state.json` (machine bundle) before any other context work. The bundle is the handoff projection: context snapshot, accepted decisions, active assumptions, open questions, guardrails, recent state changes.
2. **Session end → `record`:** the agent appends state-change events for the session and regenerates the bundle from the log. Target: under one minute of agent time, no human editing.
3. **`supersede`:** a decision is never edited in place. A new decision references `supersedes_id` and the old one flips to `superseded`. The revision trail is the product.
4. **`invalidate` / `validate`:** an assumption flips status when evidence arrives. Stale assumptions are the silent rot; the confidence label makes staleness auditable.

Anything beyond these four (branching, multi-user merge, verification layers, hash-chaining) is infrastructure waiting for evidence.

## 5. The output

Two files in the repo root (or `.world/`):

- **`WORLD.md`** — the human-readable handoff bundle: what this project is, what's decided and why, what's assumed and how confidently, what's still open, what rules bind the next session. This is what Maya skims on Tuesday morning.
- **`world-state.json`** — the machine bundle: the full entity set and the append-only log, so any agent and any tool can consume it programmatically.

Success criterion for the output, straight from experiment #001's yardstick: a successor agent given only these two files must (a) not re-litigate a settled decision, (b) not violate a recorded guardrail, (c) be able to name the rationale and confidence behind the decisions and assumptions it inherits. That is the whole product, stated as a test.

## 6. Why the user would return

The loop is daily and the payoff is immediate:

- **Tuesday morning:** instead of 20 minutes of re-orientation, Maya's new session reads the bundle in seconds and starts from where Monday left off.
- **Wednesday's compaction:** when context compacts mid-session, the bundle is the durable anchor — the guardrails survive the compaction that currently wipes them.
- **Teammate handoff:** a colleague on a different agent tool reads the same two files. Cross-vendor portability is the wedge's defense against vendor-native memory features (wedge doc §7.5).

She returns because the pain recurs every session and the fix is felt the next morning. There is no network effect to bootstrap and no platform lock-in to sell — the retention mechanism is the daily recurrence of the pain itself.

## 7. What can be tested without building a full platform

Everything that matters about this MVP is testable with files and measurement:

1. **Coding-domain handoff experiment** (feeds the 09-23 benchmark mission): run the `docs/experiment-handoff.md` protocol on a real multi-session coding task, three conditions — bundle vs. strong auto-summary vs. transcript. Metrics: re-litigated decisions, violated guardrails, lost confidence labels, re-orientation time. No backend, no auth, no hosting.
2. **Write-side trial** (the existential risk, wedge doc §7.3): hand-maintain the bundle on one real project for a week across real sessions; log what rots, what the agent skips, what goes stale. This is the cheapest possible test of whether agent-driven writes survive contact with reality.
3. **5 developer interviews** (wedge doc §9.2): ask the adoption question directly — *would you let an agent write to a state file every session?* — and check whether the §2 workflow matches real re-orientation pain.
4. **Summary-parity falsification** (falsifiability criterion #1 in `docs/hypothesis.md`): if a strong auto-summary matches the bundle on (a)–(c) in §5, the MVP collapses to a prompt convention and no infrastructure is justified. Run this test before writing any platform code.

**Explicitly not built for this MVP:** the FastAPI backend, ingest pipeline, dashboard, ledger-as-service, multi-user auth, hosted deployment, hash-chaining or enforcement layers, any new dependency. The repo's existing backend remains an **experiment harness** for running the handoff experiments, nothing more.

## 8. What we don't know (unchanged from the wedge doc, still load-bearing)

1. **No customer interviews.** Maya is a persona. Adoption willingness is untested.
2. **Experiment #001 was n=1, one domain, one model family.** Cross-domain transfer to coding is hypothesized, not measured — the 09-23 benchmark exists to close this.
3. **The write side is a hope, not a fact.** Test #2 above is the single most important validation in this program. A bundle nobody maintains is worse than none: stale authority misleads successor sessions.
4. **Vendor capture.** If an agent vendor ships native cross-session memory that preserves decisions as well as the bundle, the wedge collapses; our only defense is cross-vendor portability, itself untested.

## 9. What would graduate this MVP to infrastructure

Infrastructure earns its keep only when a measured result demands what files can't provide: e.g., the bundle format works but goes stale because writes aren't enforced (→ hash-chained ledger with write verification), or handoffs need to cross repos/users with access control (→ ledger-as-service with auth). Until a falsification-safe experiment names the gap, the repo's backend stays a harness.

---

## Evidence grounding

- `docs/startup/wedge-research.md` — the Maya wedge, current-solution failures, falsifiability criteria
- `docs/startup/week1-review.md` — "convention before infrastructure"; backend as experiment harness
- `docs/state-model.md` — v0.1 ontology; this MVP is a measured subset (§3)
- `docs/hypothesis.md` — core thesis, falsifiability criteria #1 (summary parity) and #2 (Git+docs+prompt suffices)
- `docs/experiment-001-results.md` — the governance-retention gap that defines the output test (§5)
- `docs/experiment-handoff.md` — protocol reused for the coding-domain test (§7.1)
- `docs/thesis-challenge.md` — adversarial objections (§2, §4, §6, §7) the MVP is scoped to survive
