# Experiment #002 — Day 5: blind evaluation (protocol §6)

**Date:** 2026-09-21 · **Phase:** blind grading of the three Day 4 Agent B continuations.

## 1. Answer key (predeclared BEFORE grading)

Built from Agent A's Phase 1 record (decisions/assumptions/revisions/guardrails/questions/
evidence) before any grading began. Committed as `docs/experiment-002/day-05-answer-key.md`:
14 decisions (D1–D14; D1 superseded by D12, D7 superseded by D6, D13 depends on D5),
13 assumptions with confidence (A1'–A3', A4–A13), 3 revisions (R1–R3, old→new→trigger),
4 guardrails (G1–G4), 6 open questions (Q1–Q6), 2 failed approaches (FA1, FA2),
provenance anchors (E5/E6, E11, E13/E14, E16, E22, E29), and Agent A's explicit caveats
(weak/unverified claims flagged).

## 2. Evaluator and blinding procedure

- **Independent evaluator:** a dedicated subagent graded all three continuations against the
  key on the 14 protocol metrics individually (0–5 scales with anchored definitions;
  counts for metrics 11/12; itemized list for metric 13), plus WORLD-overhead observations.
- **Blinding:** outputs were relabeled cand-p/q/r via a fresh `python3 random` shuffle
  (private mapping kept local-only, never committed), identifying headers stripped, and
  the grader was explicitly instructed that any label→condition mapping in its inherited
  context was off-limits — grade on content vs. the key only. The grader confirmed
  compliance: no mapping was used, sought, or recovered; no handoff condition is mentioned
  in the grading report.
- **Residual blinding imperfection (documented, not hidden):** subagents inherit the parent
  transcript, which contained the blind mapping because the full `experiment-state.md` is
  returned whole on fetch at run start. Mitigations above are the best available in this
  architecture; protocol §10.4 already discloses that blinding is imperfect.
- The X/Y/Z → condition mapping was applied to the scores only AFTER grading completed.

## 3. Results (mapping revealed post-grading)

Private relabel: cand-p→Y, cand-q→X, cand-r→Z.
Control-file mapping: **X→C (raw journal) · Y→A (WORLD state) · Z→B (independent summary).**

| # | Metric | X (journal) | Y (WORLD) | Z (summary) |
|---|---|---|---|---|
| 1 | Decision preservation | 4 | 4 | 3 |
| 2 | Decision rationale | 4 | 4 | 3 |
| 3 | Assumption preservation | 3 | **5** | 3 |
| 4 | Confidence preservation | 4 | **5** | 3 |
| 5 | Revision history | 3 | 2 | 2 |
| 6 | Constraint/guardrail preservation | 5 | 5 | 4 |
| 7 | Provenance | 4 | 4 | 4 |
| 8 | Superseded decisions | 4 | 4 | 4 |
| 9 | Open questions | 4 | 5 | 5 |
| 10 | Continuation quality | 5 | 5 | 5 |
| 11 | Unsupported assumptions (count, lower better) | 0 | 0 | 0 |
| 12 | Contradictions (count, lower better) | 0 | 0 | 0 |
| 13 | Information lost | see below | see below | see below |
| 14 | Output efficiency | 3 | 4 | 4 |
| | **Mean (metrics 1–10, 14; reference only)** | **3.58** | **3.92** | **3.33** |

Word counts (headers stripped): X = 2,736 · Y = 2,494 · Z = 2,604.

**Information lost (metric 13, headline items):**
- X (journal): D2, D4 never explicitly dispositioned; assumptions A6–A13 (~half) not revisited;
  Q6 (MTM recurrence) dropped; R1–R3 triggers not fully spelled out.
- Y (WORLD): R1–R3 revision chains absent; D1/D7 never referenced as history; evidence-ID
  labels not carried.
- Z (summary): D5, D6, D9, D10 never explicitly dispositioned (largest decision gap); G3
  dividend-zero base case dropped with D9; assumptions A1', A2', A4, A6, A7, A8, A9, A12
  not revisited; R1–R3 chains absent.

## 4. Analysis — where WORLD helped, where it hurt

- **Headline:** the WORLD-state continuation (Y) preserved decision governance best (3.92),
  raw journal (X) second (3.58), independent summary (Z) third (3.33). Direction supports
  the hypothesis; the margin is modest and n=1.
- **Where WORLD helped:** assumption preservation (5 vs 3/3) and confidence preservation
  (5 vs 4/3) — Y was the only continuation to revisit all 13 assumptions with explicit
  CONFIRMED/REVISED verdicts and to carry every inherited confidence level (including
  honest downgrades A5'→low, A9'→medium-low, A13'→low). The mild schema echo in Y's
  decision/assumption tables paid for itself in that explicit confidence bookkeeping.
- **Where WORLD hurt / didn't help:** revision history (metric 5) was weak in ALL
  conditions (Y=2, X=3, Z=2) — even the WORLD-state continuation lost the R1–R3
  old→new→trigger chains. The structured state did not preserve revision records in the
  continuation. This is evidence against WORLD on that dimension and must survive into
  the Day 7 verdict.
- **WORLD overhead:** no gratuitous overhead found. Y's echo was mild and functional; X
  (journal) had the most repetition despite the longest output; Z (summary) had the
  lowest echo but the largest preservation gaps — absence of structure correlated with
  dropped decisions/assumptions. Overhead did not explain any condition's score.
- **Discipline held everywhere:** 0 unsupported assumptions and 0 contradictions in all
  three — no condition fabricated or contradicted the record. Continuation quality was
  5/5/5 across the board; every run genuinely advanced the research (dated falsifiable
  checks, downside branch, dilution inventory, warrant-as-boundary analysis).
- **Input efficiency ≠ retention:** the summary was the most input-efficient handoff
  (2,446 words) but produced the weakest preservation; the journal was the longest input
  (3,616) and longest output (2,736) with middle preservation. Efficiency of the handoff
  did not translate into governance retention.

## 5. Validity notes

- Answer key is experimenter-built (protocol §10.6); no grading corrections to the key
  were required — all key items were gradable as written.
- Same model family throughout (§10.2); single task, n=1 (§10.3); replication (Disney,
  Day 6) is n=1 more, not a sample.
- Blinding residual imperfection documented in §2 above; filename-echo stripping and
  post-grading mapping disclosure (§10.4) were followed.
- No protocol changes were made on the basis of these results (§7 rule respected).

## 6. Next

Day 6 (2026-09-22): Disney (DIS) replication per protocol §7 — lighter Agent A, three
handoffs, three Agent B continuations, blind grading on the §6 metrics with a FRESH
blind mapping. Record whether the result replicates. Do not change the protocol.
