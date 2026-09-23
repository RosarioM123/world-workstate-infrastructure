# Experiment #002: Results (Day 7, 2026-09-23)

**Repo:** `RosarioM123/world` · **Experiment:** structured work-state vs summary vs raw journal for cross-agent handoffs
**Runs:** main run on Intel (INTC), 2026-09-17 to 2026-09-21; replication on Disney (DIS), 2026-09-22
**Design:** 7-day protocol, blind grading against a predeclared answer key, 14 individual metrics, no premature score collapse

**Verdict in brief:** The WORLD-state continuation preserved decision governance best in both runs (Intel: 3.92 vs 3.58 vs 3.33; Disney: 4.45 vs 4.09 vs 2.82, reference means), but the advantage is narrow, the summary came within 0.36 in the replication, and the WORLD continuation failed on revision history in both runs. The thesis is partially supported and specifically scoped; prototype development is justified only for the demonstrated advantage, not the full vision.

## 1. Protocol

The hypothesis under test (protocol §1):

> Structured persistent work-state preserves decision governance, revision history, constraints, and provenance better than conventional summaries or raw transcripts when complex work is handed from one agent to another.

The protocol required the hypothesis to earn its keep: the experiment was designed to give conventional alternatives their strongest fair showing, and states that if the evidence says WORLD is unnecessary, the results must say so.

Three handoff conditions were built from the same Agent A research output:

- **A, structured WORLD state:** the current WORLD state representation, per `docs/state-model.md`, authored by Agent A itself (a documented improvement over Experiment #001, where the experimenter authored it).
- **B, independently written conventional summary:** a high-quality natural-language handoff by a separate, independent context that received only Agent A's journal and report, instructed to maximize useful information for a successor without any structured schema, and never shown the WORLD state file.
- **C, raw transcript/journal:** Agent A's unedited running journal.

Agent B ran three isolated continuations (same model, identical brief, no browsing, blinded, filename and format echoes stripped), which an independent evaluator scored on 14 individual metrics against an answer key predeclared *before* grading. Means of metrics 1-10 plus 14 were reported in the day logs and are reproduced here labeled **reference only**, exactly as the protocol forbids collapsing into a single score prematurely. The critical research rule (§9): do not assume WORLD is correct; no application built during the experiment; prototype development moves forward only if the evidence justifies it.

## 2. Tasks

**Agent A (main run):** investment research on Intel Corporation (NASDAQ: INTC), 3-5 year horizon, with live public sources only, no invented numbers or quotes, conflicts disclosed. Coverage: foundry strategy (IFS), process roadmap (18A+), product divisions (Client, Data Center and AI), AI positioning vs NVIDIA/AMD, financial health (cash, debt, dividend, restructuring), competitive position vs AMD/NVIDIA/TSMC, government relationship (CHIPS Act, 2025 US equity stake), leadership changes, credible M&A and partnership developments. Out of scope: valuation modeling, the final buy/hold/sell recommendation, application code.

**Agent A (replication):** the same task shape on Disney (DIS), lighter per §7.

**Why Intel:** the foundry bet, leadership turnover, dividend suspension, 2025 US government equity stake, and 18A execution risk give the decision and revision density the §3 complexity minimums require. **Why Disney:** predeclared in protocol §7 (2026-09-17), before any results existed, specifically to prevent cherry-picking; different sector (media and streaming vs semiconductors).

## 3. Agent A research

**Intel (verified 2026-09-18, above all §3 minimums):**

- 14 decisions D1-D14 (D1 superseded by D12; D7 superseded by D6; D13 depends on D5; D12 depends on D5)
- 13 assumptions A1'-A13, each with explicit confidence (high, medium, medium-low, low)
- 3 genuine revisions R1-R3 (old to new to triggering evidence); 2 superseded decisions preserved as history
- 4 guardrails G1-G4 binding Phase 2; 6 open questions Q1-Q6; 2 failed approaches FA1 (no official 18A yield disclosure exists) and FA2 (no primary 10-Q debt-maturity narrative); 32 evidence entries E1-E32 with source URLs
- The journal pre-registered three naive priors before research (18A validates the foundry; NVIDIA is purely a threat; government support de-risks); all three were later reversed by R1-R3 with named trigger evidence
- Artifact sizes: journal 3,616 words, report 2,376 words, WORLD state 3,173 words (total 9,165)

**Disney (lighter, per §7, 2026-09-22):**

- 11 decisions D1-D11 (D3a superseded by D3b; D7 depends on D2; D10 depends on D3b)
- 10 assumptions A1-A10 with explicit high/medium/low confidence; 3 revisions R1-R3
- 3 guardrails G1-G3; 5 open questions Q1-Q5; 2 failed approaches FA1-FA2; 19 evidence entries E1-E19 with source URLs
- The journal pre-registered three naive priors (P1: streaming is a drag; P2: Orlando dominance unassailable; P3: Iger still CEO, succession unresolved); P1 and P2 were revised via R1/R3 and P3 reversed via R2 (D'Amaro named CEO effective March 18, 2026)
- Artifact sizes: journal 1,147 words, report 1,908 words, WORLD state 2,199 words

## 4. All three handoffs

Built from the same Agent A output in each run. Cleaning of the WORLD state was minimal and mechanical only (path references updated); no substantive content added or removed.

| Run | Handoff X | Handoff Y | Handoff Z |
|---|---|---|---|
| Main (Intel) | C, raw journal: 3,616 words (~4,821 tokens) | A, WORLD state: 3,173 words (~4,230 tokens) | B, independent summary: 2,446 words (~3,261 tokens) |
| Replication (Disney) | B, independent summary: 2,523 words | C, raw journal: 1,157 words | A, WORLD state: 2,200 words |

Blind mappings (X/Y/Z to conditions, assigned by `python3 random` shuffle):

- **Main run (2026-09-19):** X → C (raw journal), Y → A (WORLD state), Z → B (independent summary).
- **Replication (2026-09-22, fresh shuffle, differs from main):** X → B (independent summary), Y → C (raw journal), Z → A (WORLD state).

Token estimates use the day-3 heuristic of words x 4/3 for English prose. The summary was the most input-efficient handoff in the main run (32% shorter than the journal, 23% shorter than the WORLD state). Structured-field counts in the Intel WORLD state handoff: 14 decision entries, 13 assumptions with confidence, 3 revisions, 32 evidence entries, 6 open questions, 4 guardrails, 12 tasks, 39 changelog rows. Independence of summary B was verified in both runs: the summary writer received journal plus report only, never the WORLD state file (in the main run the writer was spawned before the parent had read the state file; in the replication the writer confirmed it never opened or referenced it). Echo scans found no schema IDs, no state-model references, no blind labels. The raw journal (C) was a byte-identical copy of Agent A's unedited journal; day-3 working copies of journal and report were verified byte-identical to the archived Day 2 versions (no drift). The WORLD state carried the only machine-readable governance structure: decision supersession graph (D1 left-arrow D12, D7 left-arrow D6), revision chain R1-R3, dependency D13 to D5, append-only changelog.

## 5. Agent B outputs

Identical protocol §5 brief in all runs (continue the research, resolve open questions, revisit assumptions, perform the next analysis, update the thesis, make the next research decisions while respecting inherited constraints and prior decisions), same 8-section output format, no browsing, each run given only its blind handoff file, filename and format echoes stripped before storing. Blinding leak scans were clean in both runs. Because browsing was forbidden, all runs worked from handoff content alone, so the measurement stays on handoff retention (matching #001). One style caveat for the record: run X's main-run output framed itself as a "blind continuation," run Y as a "Phase 2 continuation," run Z neutrally; the difference was stylistic, not procedural.

- **Main run (headers stripped):** X (journal) 2,760 words (~3,680 tokens), Y (WORLD) 2,518 words (~3,357 tokens), Z (summary) 2,628 words (~3,504 tokens). Lengths within about 10% of each other, so continuation effort was comparable. Headers-stripped counts per the grading pass: X 2,736, Y 2,494, Z 2,604.
- **Replication:** X (summary) 2,998 words, Y (journal) 3,189 words, Z (WORLD) 3,000 words.

## 6. Blind grading

- Answer keys were built from Agent A's decisions, assumptions, revisions, guardrails, questions, evidence, and explicit caveats **before any grading began** (`day-05-answer-key.md`, `day-06-answer-key.md`). The main-run key covered: 14 decisions (D1-D14; D1 superseded by D12, D7 superseded by D6, D13 depends on D5), 13 assumptions with confidence (A1'-A3', A4-A13), 3 revisions (R1-R3, old to new to trigger), 4 guardrails (G1-G4), 6 open questions (Q1-Q6), 2 failed approaches (FA1, FA2), provenance anchors (E5/E6, E11, E13/E14, E16, E22, E29), and Agent A's explicit caveats (weak and unverified claims flagged). The replication key covered the equivalent Disney inventory (11 decisions, 10 assumptions, R1-R3, G1-G3, 5 questions, 2 failed approaches, E1-E19).
- An independent evaluator context graded all 14 protocol metrics individually against the key, plus WORLD-overhead observations.
- Outputs were relabeled cand-p/q/r via a fresh `python3 random` shuffle (main: cand-p → Y, cand-q → X, cand-r → Z; replication: cand-p → X (summary), cand-q → Z (WORLD), cand-r → Y (journal)), identifying headers stripped, and the grader was explicitly instructed that any label-to-condition mapping in its inherited context was off-limits. In both runs the grader confirmed compliance: no mapping was used, sought, or recovered, and no conditions were mentioned.
- The X/Y/Z to condition mapping was revealed to the scoring process only **after grading completed**.
- Day 6 improved the procedure: the fresh blind mapping was kept in a local-only private file until grading completed, then recorded in experiment-state.md (in Days 3-4 it sat in the control file from the start).

## 7. Individual metrics

Means of metrics 1-10 plus 14 are **reference only**; the protocol forbids premature collapse into a single score. Metrics 1-10 and 14 use 0-5 scales with anchored definitions; metrics 11 and 12 are counts (lower is better); metric 13 is an itemized loss list; metric 14 is output efficiency.

**Main run (Intel), mapping X → journal, Y → WORLD, Z → summary:**

| # | Metric | C (journal) | A (WORLD) | B (summary) |
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
| 13 | Information lost | see §9 | see §9 | see §9 |
| 14 | Output efficiency | 3 | 4 | 4 |
| | **Mean (1-10, 14; reference only)** | **3.58** | **3.92** | **3.33** |

**Replication (Disney), mapping X → summary, Y → journal, Z → WORLD:**

| # | Metric | A (WORLD) | B (summary) | C (journal) |
|---|---|---|---|---|
| 1 | Decision preservation | 5 | 5 | 2 |
| 2 | Decision rationale | 5 | 5 | 3 |
| 3 | Assumption preservation | 5 | 5 | 2 |
| 4 | Confidence preservation | 5 | 5 | 2 |
| 5 | Revision history | 2 | 2 | 4 |
| 6 | Constraint/guardrail preservation | 5 | 5 | 5 |
| 7 | Provenance | 5 | 4 | 2 |
| 8 | Superseded decisions | 3 | 0 | 0 |
| 9 | Open questions | 5 | 5 | 3 |
| 10 | Continuation quality | 5 | 5 | 4 |
| 11 | Unsupported assumptions (count, lower better) | 6 | 7 | 6 |
| 12 | Contradictions (count, lower better) | 0 | 0 | 0 |
| 13 | Information lost | see §9 | see §9 | see §9 |
| 14 | Output efficiency | 4 | 4 | 4 |
| | **Mean (1-10, 14; reference only)** | **4.45** | **4.09** | **2.82** |

Metric 11 counts in the replication are "unverifiable against the key," not confirmed fabrications: the key is a summary of a larger handoff record, so inherited detail the key omits cannot be distinguished from invention by a key-only grader.

## 8. Token and input comparison

Input efficiency did not translate into governance retention, in both runs:

| Run | Condition | Handoff input (words) | Continuation output (words) | Preservation mean (ref only) |
|---|---|---|---|---|
| Main | C journal | 3,616 | 2,760 | 3.58 |
| Main | A WORLD state | 3,173 | 2,518 | 3.92 |
| Main | B summary | 2,446 | 2,628 | 3.33 |
| Replication | B summary | 2,523 | 2,998 | 4.09 |
| Replication | A WORLD state | 2,200 | 3,000 | 4.45 |
| Replication | C journal | 1,157 | 3,189 | 2.82 |
- Constraint preservation was perfect or near-perfect everywhere (main: 5/5/4; replication: 5/5/5), so carrying structure imposed no penalty on guardrail fidelity, and no gratuitous WORLD bloat was found in the main run.

## 9. Information loss (metric 13, headline items)

**Main run.** Journal continuation: D2 and D4 never explicitly dispositioned; assumptions A6-A13 (about half) not revisited; Q6 (MTM recurrence) dropped; R1-R3 triggers not fully spelled out. WORLD continuation: R1-R3 revision chains absent; D1/D7 never referenced as history; evidence-ID labels not carried. Summary continuation: D5, D6, D9, D10 never explicitly dispositioned (the largest decision gap); G3 dividend-zero base case dropped with D9; assumptions A1', A2', A4, A6, A7, A8, A9, A12 not revisited; R1-R3 chains absent.

**Replication.** Summary continuation: R1-R3 chains, D3a history, evidence IDs lost. WORLD continuation: R1-R3 formal chains and the R3/Epic Universe thread lost. Journal continuation: the entire Epic thread (D7/A8/Q5), D11, D3a, Q4, all inherited confidence levels, formal provenance labels lost.

**Cross-condition discipline (both runs).** Main run: 0 unsupported assumptions and 0 contradictions in all three continuations; continuation quality 5/5/5 across the board; every run genuinely advanced the research (dated falsifiable checks, downside branch, dilution inventory, warrant-as-boundary analysis). Replication: 0 contradictions in all three; all three continuations preserved the WBD E9/E10 conflict without averaging or silently picking a side (G3 held everywhere). No condition fabricated or contradicted the record; the differences were in retention, not honesty.

**Grader-reported key gradability limits (replication, preserved verbatim from the evaluator):** provenance asymmetry (the key is a summary, so metric 11 cannot distinguish inherited detail from invention); label dependence (the journal continuation's relabeling forced manual re-mapping, injecting grader judgment); revision-vs-confirmation ambiguity (the key is silent on whether restating a revision as a confirmation counts as preserving it); change-vs-contradiction ambiguity (declared, reasoned changes were scored as non-contradictions).

The journal's information loss is structural, not length-related: with the shortest input in the replication it still lost the most, because its governance content sits in chronological narrative, recoverable but not indexed, and the continuation relabeled everything (see §12).

## 10. Failure cases, deviations, and limitations

- **Day 4 placeholder spawn incident (documented, recovered):** the first spawn for run X was created with a placeholder (`[handoff-x content to be inserted]`) where the handoff sourcing should have been. It was closed at pending_init before producing any output; all three runs were re-spawned with identical briefs sourcing handoffs from disk. No contamination.
- **Day 6 filename-case copy incident (documented, recovered):** the blind-file copy step first failed on an uppercase/lowercase filename mismatch and was re-run correctly. No contamination, no files lost.
- **Blinding residual (documented, not hidden):** in the main run, the evaluator subagent inherited the parent transcript, which contained the blind mapping because the full experiment-state.md returns whole on fetch at run start. Mitigated by relabeling to cand-p/q/r via a fresh shuffle, stripping identifying headers, and an explicit off-limits instruction; the grader confirmed compliance. Day 6 improved this by keeping the mapping in a local-only private file until grading completed. Residual imperfection stands per §10.4.
- **Protocol §10 limitations, disclosed:** (§10.1) subagents inherit parent-conversation context, so there is no genuine context isolation between Agent A and Agent B; (§10.2) same model family throughout; (§10.3) single task n=1 for the main run, the replication is n=1 more, not a sample; (§10.4) blinding is imperfect; (§10.5) Agent A authors the WORLD state (an improvement over #001, where the experimenter authored both); (§10.6) the evaluator's answer key is experimenter-built, though no grading corrections to the key were required in either run.
- **Other documented deviations:** Agent A research was launched during Day 1 setup, before the 7-day plan arrived; Day 2 verified the outputs against §3 rather than re-running them. The Day 6 Agent A was deliberately lighter per §7.

## 11. Replication results

The WORLD-best direction **replicated**: main run Y (WORLD) 3.92 > X (journal) 3.58 > Z (summary) 3.33; replication A (WORLD) 4.45 > B (summary) 4.09 > C (journal) 2.82. The alternative ordering did **not** replicate: in the main run the journal (3.58) beat the summary (3.33); in the replication the summary (4.09) beat the journal (2.82) by a wide margin. With n=1 per run, the ordering of the two conventional alternatives is instance-sensitive; the only stable claim is that the WORLD-state continuation preserved decision governance best in both runs. The protocol was not changed between runs (§7 rule respected).

## 12. Where WORLD helped

- **Assumption and confidence governance (main run):** 5/5 vs 3/3 on both assumption preservation and confidence preservation. The WORLD continuation was the only one to revisit all 13 assumptions with explicit CONFIRMED/REVISED verdicts and to carry every inherited confidence level, including honest downgrades (A5' to low, A9' to medium-low, A13' to low). The mild schema echo in its decision and assumption tables paid for itself in explicit confidence bookkeeping.
- **Provenance and supersession (replication):** provenance 5 vs 4/2 (the only continuation to carry evidence IDs throughout) and superseded decisions 3 vs 0/0 (the only continuation to name D3a). Structured labels survived into the continuation.
- **The label-stability mechanism (replication, the strongest mechanism-level finding):** the journal continuation renumbered every decision, assumption, and question under its own labels, and that is exactly where governance items were lost: the entire Epic thread (D7/A8/Q5), D11, Q4, inherited confidences, provenance IDs. The structured labels survived into the WORLD continuation and kept the Epic thread alive there (and in the summary continuation, which inherited the thread through narrative). The grader's observation stands: "Relabeling is not neutral reformatting; it is where items get lost." This is concrete evidence for *why* stable structured labels matter, not just that they correlate with better scores.
- **Guardrail discipline everywhere:** constraint preservation scored 5/5/4 and 5/5/5, so structure adds no penalty on the dimension both formats already handle well.

## 13. Where WORLD hurt

- **Revision history is weak in the WORLD continuation in BOTH runs (evidence against WORLD):** metric 5 scored 2 for the WORLD continuation twice. In the main run revision history was weak in all conditions (WORLD 2, journal 3, summary 2); in the replication the journal continuation scored 4 while the WORLD continuation scored 2, tied with the summary. The structured state does not carry old-to-new-to-trigger revision chains into the continuation. This is now a replicated finding.
- **Superseded decisions only partially preserved (replication):** 3 for the WORLD continuation, with D3a named but the formal D3a-to-D3b chain not spelled out; the other two conditions scored 0.
- **Mild decorative overhead (replication):** "confidence medium, trending toward a formal downgrade" adds second-order precision the key does not contain. No gratuitous bloat was found in the main run, and overhead did not explain any condition's score in either run.

## 14. Strongest evidence AGAINST WORLD

Three items, in order of weight:

1. **The replicated revision-history weakness.** The WORLD continuation scored 2 on metric 5 in both runs, losing the R1-R3 old-to-new-to-trigger chains it was explicitly built to preserve. The journal continuation beat it on this metric in the replication (4 vs 2). A structured state representation that does not transmit revision chains into the continuation fails on one of the four things the hypothesis claims it preserves.
2. **Near summary-parity in the Disney run (4.09 vs 4.45).** An independent, schema-free summary written by a separate context came within 0.36 of the WORLD continuation on the reference mean. This keeps the hypothesis's falsifiability condition 1 (summary parity) open: if a well-written summary can get this close, the case for infrastructure over convention is narrow.
3. **Information loss in every condition.** No handoff was lossless; the WORLD continuation dropped revision chains, superseded-decision history (main run), evidence IDs (main run), and part of the Epic thread (replication).

## 15. Strongest evidence FOR WORLD

1. **The WORLD-best direction replicated twice,** in a harder design than #001 (blinded, predeclared key, independently written summary, 14 individual metrics): 3.92 > 3.58 > 3.33 on Intel, 4.45 > 4.09 > 2.82 on Disney.
2. **Assumption and confidence governance:** the WORLD continuation was the only one in the main run to revisit all 13 assumptions with explicit verdicts and carry every confidence level, and tied for best on both metrics in the replication.
3. **Label stability as a concrete mechanism:** the journal continuation's relabeling is where its governance items were lost, in the exact shape ("relabeling is not neutral reformatting") that structured stable labels prevent.
4. **Constraint preservation perfect everywhere:** structure imposed no fidelity penalty and no meaningful overhead, so the advantage costs nothing on the dimension summaries already handle.

## 16. Whether Experiment #001 replicated

Experiment #001 (manual run, Block/SQ, 2026-09-17) found a narrow WORLD win on ten protocol measures, with inputs of A = WORLD state 1,450 words, B = summary 1,241 words, C = journal 1,054 words:

| #001 measure | A (WORLD) | B (summary) | C (journal) |
|---|---|---|---|
| Overall | 5/5 | 5/5 | 4/5 |
| Facts | 13/13 | all survived | all survived |
| Decisions with rationale | 5/5 | 5/5, but lost D-002 as an explicit decision | 1/5 |
| Assumptions with confidence | 7/7 | not itemized separately | decision taxonomy lost |
| Revision trail | full | not itemized separately | dropped the D-004 guardrail ("no buy thesis without a stress case") |
| Errors / information loss | zero / zero | none reported | not itemized separately |
| Continuation output length | 1,902 words (shortest) | not recorded | not recorded |

Headline: "facts survive every format; governance survives only where stated explicitly."

**Verdict: the direction replicated; the specifics did not.** In the harder #002 design (blinded, predeclared answer key, independent summary writer, 14 metrics instead of 10), the WORLD-state continuation preserved decision governance best in two more runs. But #001's clean sweep did not repeat: in #002 the WORLD continuation lost revision chains in both runs, the summary came within 0.36 in the replication, and the journal-vs-summary ordering flipped between the two #002 runs. The #002 design is the stronger instrument, and its verdict is narrower than #001's.

## 17. Updated WORLD hypothesis

The evidence supports a narrower, specifically scoped thesis:

> Structured work-state with stable labels preserves decision-governance items, assumptions with confidence levels, provenance, and supersession records, across agent handoffs better than raw transcripts or independently written summaries. **But the current state representation does not preserve revision old-to-new-to-trigger chains in the continuation**, and the demonstrated advantage over a strong summary is modest (within 0.36 on the reference mean in one run).

The thesis is therefore **partially supported, specifically scoped, and not yet generalizable**:

- Supported: stable labeled governance records (assumptions with confidence, provenance IDs, superseded decisions) survive handoffs better; the mechanism is label stability.
- Not supported: revision history preservation, one of the four claimed advantages.
- **Untested:** success criterion 2 (human auditability: no human traced a decision to its evidence through the state) and criterion 3 (cross-model consistency: the same model family was used throughout). Falsifiability condition 1 (summary parity) remains open given the near-parity result in the replication; conditions 2 (tool sufficiency: Git plus docs plus MCP), 3 (ontology collapse), and 4 (verification irrelevance) were not tested by this experiment at all.

## 18. Whether another experiment is needed

Yes. This experiment answered one question and opened several it cannot close:

1. **A targeted revision-history experiment:** the replicated metric-5 weakness is the most important open item. Test whether an explicit revision-chain schema (old, new, trigger, evidence links) survives into a continuation, or whether the failure is in how continuations read the state rather than in the state itself.
2. **Cross-model handoffs (criterion 3):** run Agent A in one model family and Agent B in another to test whether the advantage is model-agnostic, as the thesis requires.
3. **Human auditability (criterion 2):** have a human trace a decision from the state to its evidence and record where the trail breaks.
4. **Writing FROM state, not just reading it:** #002 tested continuations reading the state; test whether requiring Agent B to author state updates changes retention.
5. **n > 1 replication:** two runs cannot separate a stable advantage from instance sensitivity, as the flipped journal-vs-summary ordering shows.

Sequencing: run the revision-history experiment first (item 1), since that is the one dimension where the current representation demonstrably fails and where the prototype's value proposition lives or dies. Cross-model handoffs (item 2) and human auditability (item 3) test the two success criteria this experiment left untouched.

## 19. Whether prototype development is justified

Per the critical research rule (§9), the honest verdict is **a narrow yes, scoped to the demonstrated advantage, not the full vision.**

What the evidence justifies: a small prototype of stable labeled governance records for cross-agent handoffs (decisions, assumptions with confidence, provenance links, supersession markers), with **revision-history preservation as the prototype's first test**, since that is exactly where the current representation failed. What it does not justify: the full WORLD infrastructure vision (canonical state per project, verifiable audit, cross-model continuity), because criteria 2 and 3 are untested, summary parity nearly held in one run, and the revision mechanism is broken in the exact place a prototype would need to work. Build the narrow thing, test the revision chain first, and let the next experiments decide whether the broader claim earns its infrastructure.

## Repo files referenced

- `docs/experiment-002/protocol.md`, `experiment-state.md` (control files)
- `docs/experiment-002/day-01.md` through `day-06.md` (day logs)
- `docs/experiment-002/agent-a-journal.md`, `agent-a-report.md`, `agent-a-world-state.md` (Intel Agent A)
- `docs/experiment-002/handoff-x.md`, `handoff-y.md`, `handoff-z.md` (Intel blind handoffs)
- `docs/experiment-002/agent-b-x.md`, `agent-b-y.md`, `agent-b-z.md` (Intel continuations)
- `docs/experiment-002/day-05-answer-key.md` (predeclared grading key)
- `docs/experiment-002/dis-agent-a-journal.md`, `dis-agent-a-report.md`, `dis-agent-a-world-state.md` (Disney Agent A)
- `docs/experiment-002/dis-handoff-x.md`, `dis-handoff-y.md`, `dis-handoff-z.md` (Disney blind handoffs)
- `docs/experiment-002/dis-agent-b-x.md`, `dis-agent-b-y.md`, `dis-agent-b-z.md` (Disney continuations)
- `docs/experiment-002/day-06-answer-key.md`, `day-06-grading.md` (predeclared key, blind evaluator report)
