# Handoff Experiment: Investment Research

The experiment that decides whether WORLD is worth building. It directly
tests thesis-challenge objections 7 (compression) and 4 (memory/RAG).

## Setup

**Domain:** investment research on a single public company (pick one with
rich public filings, e.g., an S&P 500 constituent).

**Participants:**
- A human (project creator, decision maker).
- Agent A (model M1): researches the company — reads filings, builds a
  thesis, records structured state.
- Agent B (model M2, **different model family**): enters mid-project with no
  access to Agent A's conversation history.
- A later agent (model M3 or M1 again): resumes after the human's decision.

**Conditions** (Agent B's starting material varies; everything else fixed):
1. **WORLD state**: the structured handoff bundle from `state-model.md`.
2. **Summary baseline**: a strong-model summary of Agent A's work (~same
   token budget as the WORLD bundle).
3. **Transcript baseline**: Agent A's full conversation history (tests
   whether structure beats raw context).

## Protocol

1. Human creates the investment research project in WORLD (context: goal,
   scope, constraints, definition of done).
2. Agent A researches the company. WORLD records: tasks, evidence (filings,
   quotes), assumptions, decisions (preliminary thesis), open questions.
3. Agent A stops. Its conversation history is sealed — Agent B never sees it
   (except in condition 3).
4. Agent B enters under one of the three conditions and continues the
   research: validates/invalidates assumptions, answers open questions,
   records new evidence.
5. Human makes an investment decision (buy/hold/sell + rationale). WORLD
   records the decision with supporting evidence.
6. A later agent resumes the project from WORLD state alone and produces a
   status brief.

## What we measure

**Information retention** (the core metric). After step 4, quiz Agent B —
without giving it additional context — on:
- Key facts Agent A established (with sources).
- Decisions Agent A made and their rationale.
- Assumptions Agent A recorded, and their confidence levels.
- Open questions Agent A left.

Score each as retained / partially retained / lost, graded against ground
truth by the human. Report retention rate per condition.

**Decision auditability.** Can the human trace the final investment decision
back through decisions → evidence → actions? Binary pass/fail per
condition, plus time-to-trace.

**Continuation consistency.** Do Agents B under different conditions produce
substantively consistent research continuations (same open questions
pursued, no repeated dead ends)? Graded by the human on a 1–5 scale.

**Handoff cost.** Tokens and wall-clock time to bring Agent B to
productivity under each condition.

## Interpreting results

- **WORLD wins** if condition 1 beats condition 2 on retention and
  auditability at comparable or lower handoff cost. → Proceed to prototype.
- **Summary parity** (condition 2 ≈ condition 1): the compression objection
  holds. WORLD should be re-scoped as a convention/checklist, not
  infrastructure. Do not build the app.
- **Transcript wins** (condition 3 best): structure is premature
  optimization; invest in longer contexts and better retrieval instead.
- **Nobody retains enough**: the problem is real but this isn't the
  solution; revisit the state model before building anything.

## Controls and honesty notes

- Same company, same starting context, same human grader across conditions.
- Token budgets for conditions 1 and 2 must be comparable — otherwise the
  comparison is meaningless.
- Run each condition at least twice; single runs prove nothing.
- The human grader must not know which condition produced which output
  (blind grading) where feasible.
- Pre-register the scoring rubric *before* running. No moving goalposts.
