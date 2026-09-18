# WORLD — Customer Wedge Research

**Date:** 2026-09-18 · **Mission:** Day 1 of 10, startup validation program
**Status:** Hypothesis — partially evidenced (see §7 for what is and isn't supported)

## TL;DR

The strongest narrow wedge for WORLD is **developers doing multi-session AI-assisted development on real projects** — the "context rot" problem: every new agent session re-derives decisions, re-litigates settled choices, and silently drops constraints set in earlier sessions. Our own experiment #001 showed structured work-state preserves exactly what summaries and transcripts lose — decisions with rationale, assumptions with confidence, and binding guardrails. External demand signals (Sonar, cross-tool community digests, VentureBeat) confirm the pain is acute, current, and unsolved by static prompt files or vendor memory features.

---

## 1. The specific user

**Maya, senior backend engineer at a 12-person startup.** She builds a billing/payment service with an AI coding agent (Claude Code / Codex class) as her daily pair programmer: 3–6 sessions a day, a real repo, a real roadmap, work spanning weeks. She is technical, already pays for agent tooling, and feels the pain *daily* — not as an abstract concept but as 20 minutes of re-orientation every morning and mid-session derailments after context compaction.

Why her, specifically:

- **Identifiable and reachable:** she lives on GitHub, in agent-tool communities, in the open. No enterprise sales cycle to reach her.
- **Acute, recurring pain:** the cost hits every single session, so the value of a fix is felt immediately and repeatedly — the precondition for a habit-forming wedge.
- **Pays for tools already:** no need to create a new budget category.
- **Her workflow is the thesis, instantiated:** work moves between sessions, models (she switches between agent tools), and time. Exactly the handoff problem WORLD claims to solve.

---

## 2. The painful workflow

Monday: Maya starts a multi-day refactor of the billing module with her agent. Over the session they make real decisions — *split invoicing from dunning because the retry semantics differ; use Stripe webhooks, not polling, because idempotency keys already exist; no new dependencies without her approval (a hard constraint after a supply-chain scare).*

Tuesday: new session. The agent doesn't know any of this. Maya re-explains the architecture, re-states the constraint, re-derives the webhook decision from first principles. Twenty minutes gone before productive work starts.

Wednesday: context compacts mid-session. The working plan evaporates. The agent, now amnesiac, proposes polling for webhook delivery — **re-litigating a decision that was settled and rationale'd on Monday** — and in another session quietly adds a new dependency, violating the constraint nobody recorded anywhere durable.

Thursday: a teammate picks up the branch with a different agent tool. None of Monday's reasoning is visible to them. The decisions exist only in Maya's head and in dead chat transcripts.

The unit of loss is not facts — Maya can re-read the code. The unit of loss is **governance**: what was decided, why, what was assumed, what is still open, and what rules bind the next session.

---

## 3. Current solutions

| Solution | What it is | Who provides it |
|---|---|---|
| Prompt/context files (`CLAUDE.md`, `AGENTS.md`, rules) | Hand-maintained project instructions checked into the repo | Developer |
| Session summaries / auto-compact | Model-generated narrative summary carried into the next session | Agent vendors |
| Agent memory products (Mem0, Zep, framework built-ins) | Cross-session recall for one agent stack | Vendors / OSS |
| Orchestrator checkpoints (LangGraph, Temporal) | Resumable execution state across agent steps | Frameworks |
| Git + docs folder | Versioned files, ADRs, hand-written notes | Developer |
| Full transcript / chat history | Raw prior conversation as context | Agent vendors |

---

## 4. Why current solutions fail

**The core finding, from our own evidence:** narrative formats preserve *facts*; only structured state preserves *governance*. Experiment #001 (2026-09-17, investment-research handoff, three conditions, blind-graded) found:

- All three continuations recovered all 13 key facts. Facts are not the problem.
- The **summary** condition lost a real decision (D-002, the bitcoin enterprise-value call) as an explicit decision — it survived as prose, not as a committable, auditable choice.
- The **transcript** condition recovered only 1 of 5 decisions canonically, 0 of 7 canonical confidence labels, and **dropped a binding guardrail** ("no buy thesis without a stress case") — the exact failure mode in Maya's Wednesday story.
- The **WORLD structured state** recovered 5/5 decisions with rationales, 7/7 assumptions with confidence levels, and the full revision trail, at +17% input overhead — and produced the shortest faithful output.

Per-solution failures:

1. **Prompt files are static; the project isn't.** Sonar (Sept 2026): they "are static and must be maintained as the codebase changes," and "drift out of date the moment your architecture moves." They also can't carry what actually prevents drift — the live decision history and its rationale.
2. **Summaries are lossy in exactly the wrong dimension.** Strong-model summaries compress away decision-ness: rationale, confidence, supersession. The compression objection (`thesis-challenge.md` §7) cuts against us too — the summary baseline gets stronger every model generation — but experiment #001 measured the gap as real, not theoretical.
3. **Memory products optimize for one agent's recall, not team continuity.** Per `thesis-challenge.md` §4: their state is model/framework-tied and opaque to humans. Maya's teammate on a different tool gets nothing.
4. **Checkpoints save execution, not work.** LangGraph can resume a crashed run; it cannot tell Wednesday's compacted session why Monday chose webhooks (`thesis-challenge.md` §6).
5. **Git versions files, not decisions.** A diff shows what changed, not that "Decision D-14 was made on Evidence E-3 and supersedes Assumption A-7" (`thesis-challenge.md` §2).

**External demand confirms the pain is real and unsolved:**

- Community feature-request tracking across Claude Code, Gemini CLI, Copilot, OpenCode, and Pi: "The demand for 'Persistent Memory' is deafening… Users are frustrated when long-running agents lose context or crash upon resume." "Context is lost when Claude suggests restarting" is a flagged critical workflow flaw.
- Practitioner guides estimate developers spend **15–20% of time re-explaining context** to agents; "multi-day features lose critical context"; "AI forgets architectural choices made earlier."
- VentureBeat (2026): the "context layer" is enterprise AI's next production problem — "the same underlying data produces different answers depending on which agent, tool or system asks the question."

---

## 5. The smallest product that could solve it

Not a platform. Not an app. **A handoff bundle + decision ledger that lives in the repo, maintained by the agent, read by every successor session.**

Concretely:

- **Write path (end of session):** the agent records *decisions* (statement + rationale + what they supersede), *assumptions* (statement + confidence), *open questions*, and *binding constraints/guardrails* into a small structured file in the repo (markdown for humans, JSON for machines — the `state-model.md` ontology, v0.1). Cost target: under a minute of session time, mostly agent-driven.
- **Read path (start of session):** any agent, any model, any tool reads the bundle first. Maya's Tuesday re-orientation drops from 20 minutes to seconds; Wednesday's compacted session inherits the guardrails instead of re-litigating them.
- **Why she returns:** the pain recurs daily, and the fix is felt the next morning. The loop is tight: record once, benefit every session after.
- **What can be tested without building a full platform:** the bundle format itself. Run the handoff experiment in the coding domain (same protocol as `experiment-handoff.md`, new domain): does a successor agent given the bundle avoid re-litigating settled decisions and violating recorded constraints, versus summary and transcript baselines? No backend, no auth, no hosting — a file convention plus a measurement. If the convention alone wins, WORLD's first product *is* the convention, and infrastructure comes later only if the convention needs enforcement (hash-chaining, verification) that files can't provide.

Deliberately out of scope for the wedge: the FastAPI backend, the dashboard, multi-user auth, the ledger-as-service. All of that is premature until the bundle format earns its keep.

---

## 6. Why this wedge, not the alternatives

- **Investment research teams.** Strongest *direct* evidence (it's experiment #001's domain) — but enterprise sales cycles, existing compliance/audit tooling, and a small buyer pool make it a terrible wedge. Also risks overfitting to n=1.
- **Enterprise "AI context layer"** (Snowflake Horizon et al.). Crowded, well-funded incumbents; requires enterprise sales motion we don't have.
- **Agent framework builders.** The buyer is diffuse and builds in-house; we'd be a feature request, not a product.
- **Non-technical AI users.** The pain exists but the value (governance preservation) is invisible to them; adoption friction is high, willingness to maintain state is low.

The developer wedge wins on: pain frequency (daily), buyer reachability (open communities, no sales cycle), willingness to try tools, and direct mapping to our measured evidence.

---

## 7. What we don't know (unsupported assumptions — stated plainly)

1. **No customer interviews have been conducted.** Willingness to adopt — and to let an agent write to a state file every session — is untested. Everything in §1–§2 about Maya is a persona, not a quote.
2. **Experiment #001 was one domain, one model family, n=1.** The transfer from investment research to coding workflows is hypothesized from the mechanism (governance loss), not measured. Experiment #002 may speak to this; its results are pending and out of scope for this doc.
3. **Write-side adoption is the existential risk.** The read-side value is evidenced; whether developers/agents reliably *maintain* the bundle is not. A state file nobody updates is worse than none — it's stale authority.
4. **The "convention vs. infrastructure" question is open.** Falsifiability criterion #2 in `hypothesis.md`: if Git + a docs folder + a good prompt achieves the same handoff fidelity, WORLD should be re-scoped as a convention, not built as infrastructure. The smallest product above is deliberately designed to test exactly this.
5. **Vendor capture risk.** The "deafening" demand for persistent memory means agent vendors will ship native solutions. If a vendor's native cross-session memory preserves decisions as well as our bundle, the wedge collapses. Our defense would have to be cross-vendor portability (Maya's teammate on a different tool) — itself untested.

---

## 8. Falsifiability

This wedge thesis is wrong if:

1. **Summary parity in the coding domain:** successor agents given a strong auto-summary re-orient just as fast, with no repeated decisions and no violated constraints. → WORLD is a convention, not infrastructure. Do not build the backend.
2. **Write-side failure:** in a real trial, the bundle goes stale within a week because nobody maintains it. → The product dies regardless of read-side value; the problem may need a vendor-level (automatic) solution instead.
3. **Nobody will switch tools for this:** developers try it, acknowledge the value, but won't change session habits. → Distribution problem, not a technology problem; the wedge is wrong even if the thesis is right.

---

## 9. Suggested next validation steps

1. **Coding-domain handoff experiment** (feeds the 09-23 benchmark mission): same three-condition protocol as experiment #001, applied to a multi-session coding task. Measures decision retention and constraint violations, not just facts.
2. **5 developer interviews** on session re-orientation: how they restart work today, what they re-derive, what they've tried. (Uncovers whether §2's workflow matches reality.)
3. **Bundle-format prototype as pure convention:** hand-author the bundle for one real project, use it across sessions for a week, log what rots. Cheapest possible test of write-side adoption.

---

## Evidence grounding

- `docs/hypothesis.md` — core thesis, definitions, falsifiability criteria
- `docs/thesis-challenge.md` — adversarial objections (§2 Git, §4 memory, §6 orchestration, §7 compression, §8 ontology)
- `research/comparisons.md` — capability matrix vs. RDBMS, event sourcing, Git, RAG, memory products, MCP, orchestration
- `docs/state-model.md` — the ontology the bundle format derives from (draft v0.1)
- `docs/experiment-001-results.md` — the governance-retention finding (2026-09-17)
- `docs/experiment-handoff.md` — the experimental protocol this wedge reuses
- External: Sonar on static prompt files (Sept 2026); cross-tool CLI digest on session-continuity demand; VentureBeat on the enterprise context layer
