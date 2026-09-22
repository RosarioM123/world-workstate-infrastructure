# Day 6 (2026-09-22) — Disney replication (protocol §7)

**Phase:** replication on Disney (DIS), predeclared in protocol §7. Lighter Agent A
research, three handoffs, three blind Agent B continuations, blind grading on the
§6 metrics with a FRESH blind mapping. Protocol not changed; methodological
problems documented instead.

## 1. Agent A: Disney research (lighter, per §7)

One subagent browsed live public sources and produced all three artifacts in
`~/workspace/exp002/day6/`:

- `dis-agent-a-journal.md` — 1,147 words; pre-registered 3 naive priors first
  (P1 streaming is a drag; P2 Orlando dominance unassailable; P3 Iger still CEO,
  succession unresolved).
- `dis-agent-a-report.md` — 1,908 words.
- `dis-agent-a-world-state.md` — 2,199 words, schema `docs/state-model.md` (Draft v0.1).

Complexity verification (lighter targets met): 11 decisions D1-D11 (D3a superseded
by D3b; D7 depends on D2; D10 depends on D3b); 10 assumptions A1-A10, all with
explicit high/medium/low confidence; 3 revisions R1-R3 (old->new->trigger); 3
guardrails G1-G3; 5 open questions Q1-Q5; 2 failed approaches FA1-FA2; 19 evidence
entries E1-E19 with source URLs. Priors disposition: P1 revised (R1), P2 revised
(R3), P3 reversed (R2: D'Amaro named CEO effective March 18, 2026).

Disclosed conflicts kept as conflicts: the WBD acquisition (E9: Reuters Dec 2025,
Netflix $82.7B deal vs E10: Feb 2026, Paramount Skydance $31/share board
recommendation) under guardrail G3. Agent A's explicit caveat: net-debt/EBITDA
1.9x rests on a single third-party note; verify from 10-K before modeling.

## 2. Three handoffs (same Agent A output)

- **A — structured WORLD state** (`dis-handoff-a.md`, 2,200 words): cleaned Agent A
  bundle, typos/whitespace only.
- **B — independent summary** (`dis-handoff-b.md`, 2,523 words): separate subagent,
  journal + report ONLY, never the WORLD state file (compliance confirmed by the
  writer), instructed per §2 to maximize useful information without any structured
  schema. No schema IDs or state-model entities; echo-scan clean.
- **C — raw journal** (`dis-handoff-c.md`, 1,157 words): unedited.

Fresh blind mapping via `python3 random` shuffle, assigned 2026-09-22 (differs from
the Day 5 mapping):
**X->B (independent summary) · Y->C (raw journal) · Z->A (WORLD state).**
The mapping was kept in a local-only private file until grading completed, then
recorded in `experiment-state.md`. (Improvement over the Day 3-4 procedure, where
the mapping sat in `experiment-state.md` from the start; residual imperfection
stands per §10.4.)

## 3. Three Agent B continuations (protocol §5)

Identical brief (protocol §5 objective verbatim), same 8-section output format,
no browsing, each given only its blind handoff file with strict source restriction
(§10.1 limitation disclosed). Leak-scan clean: no run codes, condition names, or
format echoes in any output. Outputs stored with one-line provenance headers as
`docs/experiment-002/dis-agent-b-x.md` (2,998 words), `dis-agent-b-y.md`
(3,189 words), `dis-agent-b-z.md` (3,000 words).

## 4. Answer key and blind grading

`day-06-answer-key.md` was built from Agent A's decisions/assumptions/revisions/
guardrails/questions/evidence BEFORE any grading. Outputs were relabeled
cand-p/q/r via a second fresh random shuffle (X->cand-p, Y->cand-r, Z->cand-q),
identifying headers stripped. The independent evaluator subagent graded all 14
metrics individually against the key and confirmed blinding compliance: no mapping
used, sought, or recovered; no conditions mentioned. Full report committed as
`day-06-grading.md`.

Mapping revealed only after grading: **cand-p = X (summary) · cand-q = Z (WORLD
state) · cand-r = Y (journal).**

## 5. Results (mapping revealed post-grading)

| # | Metric | B (summary) | A (WORLD) | C (journal) |
|---|---|---|---|---|
| 1 | Decision preservation | 5 | 5 | 2 |
| 2 | Decision rationale | 5 | 5 | 3 |
| 3 | Assumption preservation | 5 | 5 | 2 |
| 4 | Confidence preservation | 5 | 5 | 2 |
| 5 | Revision history | 2 | 2 | 4 |
| 6 | Constraint/guardrail preservation | 5 | 5 | 5 |
| 7 | Provenance | 4 | 5 | 2 |
| 8 | Superseded decisions | 0 | 3 | 0 |
| 9 | Open questions | 5 | 5 | 3 |
| 10 | Continuation quality | 5 | 5 | 4 |
| 11 | Unsupported assumptions (count, lower better) | 7 | 6 | 6 |
| 12 | Contradictions (count, lower better) | 0 | 0 | 0 |
| 13 | Information lost | R1-R3 chains; D3a history; E-IDs | R1-R3 formal chains; R3/Epic Universe | Epic thread (D7/A8/Q5); D11; D3a; Q4; confidences; labels |
| 14 | Output efficiency | 4 | 4 | 4 |
| | **Mean (metrics 1-10, 14; reference only)** | **4.09** | **4.45** | **2.82** |

Metric 11 counts are "unverifiable against the key," not confirmed fabrications:
the key is a summary of a larger handoff record, so inherited detail the key omits
cannot be distinguished from invention by a key-only grader. No contradictions
(metric 12) in any condition.

## 6. Analysis — where WORLD helped, where it hurt

- **Headline:** the WORLD-state continuation (A) preserved decision governance best
  (4.45), independent summary (B) second (4.09), raw journal (C) third (2.82).
  Direction of the main-run result replicates; the margin over the summary is modest
  and n=1.
- **Where WORLD helped:** provenance (5 vs 4/2; the only continuation to carry
  evidence IDs throughout), superseded decisions (3 vs 0/0; the only one to name
  D3a), assumption and confidence preservation (5/5, tied with B). The structured
  labels survived into the continuation and kept the Epic thread (D7/A8/Q5) alive
  in A and B.
- **The label-stability finding:** the journal continuation (C) renumbered every
  decision/assumption/question under its own labels, and that is where governance
  items were lost: the entire Epic thread, D11, Q4, all inherited confidence
  levels, formal provenance. The grader's observation stands: "Relabeling is not
  neutral reformatting; it is where items get lost." This is the strongest
  mechanism-level evidence the experiment has produced for stable structured labels.
- **Where WORLD hurt / didn't help (evidence against WORLD, reported honestly):**
  revision history is weak in the WORLD continuation AGAIN (metric 5 = 2, tied with
  B; the journal scored 4). This is now replicated: the structured state does not
  carry old->new->trigger revision chains into the continuation. The D3a->D3b chain
  was only partially preserved (metric 8 = 3). Mild decorative overhead in the
  WORLD continuation: "confidence medium, trending toward a formal downgrade"
  adds second-order precision the key does not contain. No gratuitous bloat.
- **The alternative ranking did NOT replicate:** Day 5 had journal (3.58) ahead of
  summary (3.33); Day 6 has summary (4.09) well ahead of journal (2.82). With n=1
  per run, the ordering of the two conventional alternatives is instance-sensitive.
  The WORLD-best ordering replicated; nothing stronger can be claimed.
- **WBD conflict:** all three continuations preserved the E9/E10 conflict without
  averaging or silently picking a side (G3 held everywhere).

## 7. Methodological notes (do NOT change the protocol)

- Same model family throughout (§10.2); no genuine context isolation (§10.1);
  n=1 replication, not a sample (§10.3); blinding improvements: mapping kept
  local-only pre-grading, double-shuffle relabeling, off-limits instruction,
  compliance confirmed.
- Blinding residual: subagents inherit parent context; the mapping existed in the
  parent transcript. Mitigations are documented; §10.4 stands.
- Grader-reported key gradability limits (preserved verbatim): provenance
  asymmetry (key is a summary; metric 11 cannot distinguish inherited detail from
  invention); label dependence (R's relabeling forced manual re-mapping, injecting
  grader judgment); revision-vs-confirmation ambiguity (key silent on whether
  restating a revision as a confirmation counts as preserving it); change-vs-
  contradiction ambiguity (declared, reasoned changes scored as non-contradictions).
- Procedural incident (minor, documented): the blind-file copy step first failed on
  an uppercase/lowercase filename mismatch and was re-run correctly; no
  contamination, no files lost.
- Day 6 used a lighter Agent A (smaller but meeting all complexity targets); input
  sizes differed across conditions (B summary 2,523 vs C journal 1,157 words), as
  in the main run.

## 8. Files produced today

- `docs/experiment-002/dis-agent-a-journal.md`, `dis-agent-a-report.md`,
  `dis-agent-a-world-state.md`
- `docs/experiment-002/dis-handoff-x.md`, `dis-handoff-y.md`, `dis-handoff-z.md`
- `docs/experiment-002/dis-agent-b-x.md`, `dis-agent-b-y.md`, `dis-agent-b-z.md`
- `docs/experiment-002/day-06-answer-key.md` (predeclared)
- `docs/experiment-002/day-06-grading.md` (blind evaluator report)
- `docs/experiment-002/day-06.md` (this file)
- `docs/experiment-002/experiment-state.md` (updated)
- `docs/development-log.md` (appended)

## 9. Next action

Day 7 (Wed 2026-09-23 ~09:42 ET, cron `world-exp002-daily`): write `results.md`
per protocol §8; update `docs/hypothesis.md` only if evidence warrants; update
development log; write `day-07.md`; commit; then disable the daily schedule.
