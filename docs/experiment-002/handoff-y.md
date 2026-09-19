# WORLD State — Experiment #002 / Agent A (Phase 1: Intel research)
**Schema:** `docs/state-model.md` (Draft v0.1) | **Generated:** 2026-09-17
**Project status:** active (Phase 1 complete; Phase 2 pending)

> State is a projection over the append-only `StateChange` log (§9). Decisions are never edited in place — D1 and D7 are superseded, history retained.

---

## 1. Project

- **id:** `exp002`
- **name:** Experiment #002 — WORLD vs. conventional research artifacts (Intel Corporation case)
- **goal:** Produce sufficiently complex, provenance-rich raw research and structured state on Intel (3–5 yr horizon) to support a later controlled comparison against an independently produced conventional summary and a transcript condition.
- **scope:** Agent A Phase 1 only: public-source research on INTC (technology, foundry, financials, ownership, competition, leadership). Explicitly out of scope: valuation modeling (DCF/multiples), buy/hold/sell recommendation (human decides), prototype code.
- **constraints:** No prototype development before Experiment #002 completes; do not assume WORLD's hypothesis is true; do not design the experiment to favor WORLD; complexity minimums (≥10 decisions, ≥10 assumptions with confidence, ≥3 revisions, ≥2 superseded decisions, ≥2 guardrails, supporting+contradicting evidence for ≥2 decisions, ≥3 open questions, ≥1 failed approach, ≥1 dependent decision); URLs for every important claim; no invented facts/sources/numbers.
- **definition_of_done:** `agent_a_journal.md`, `agent_a_report.md`, and this `world_state.md` written to `docs/experiment-002/` meeting all complexity minimums.
- **stakeholders:** human (final investment authority), parent agent (experiment coordinator), future Agent B / Phase 2 (consumer of handoff).
- **provenance:** created_by `agent:Muse Spark:exp002-agent-a`, created_at 2026-09-17.

---

## 2. Tasks

| id | title | status | notes |
|---|---|---|---|
| T1 | Research 18A / Panther Lake / process roadmap | done | E1, E2, E3 |
| T2 | Research Q2 2026 financials + GAAP bridge | done | E9, E10, E11, E12 |
| T3 | Research government stake + CHIPS terms | done | E13, E14 |
| T4 | Research NVIDIA partnership + closing | done | E15, E16 |
| T5 | Research AI accelerators (Falcon/Jaguar Shores, Gaudi) | done | E17, E18 |
| T6 | Research foundry external-customer validation | done | E4–E8 |
| T7 | Research leadership change (Gelsinger → Tan) | done | E25, E26, E32, E33 |
| T8 | Research balance sheet / debt / liquidity | done | E19, E20, E29 (primary verification unfinished → T12) |
| T9 | Research competitive position (AMD, TSMC) | done | E22 |
| T10 | Research TSMC JV rumors + Altera + SoftBank | done | E21, E23, E24 (completions unconfirmed → T12) |
| T11 | Write agent_a_journal.md + agent_a_report.md + world_state.md | done | artifacts ART1–ART3 |
| T12 | Phase 2: primary-source verification + open questions | proposed | blocked on: Q1–Q6; assignee: future Agent B / Phase 2 |

---

## 3. Decisions

Format: `id` — statement | status | rationale (compressed) | evidence.

- **D1** — Treat the 18A Panther Lake ramp as the primary evidence of process turnaround. | **superseded** (by D12) | Rationale at the time: first high-volume leading-edge node in years. | E1
- **D2** — Frame NVIDIA as both dominant AI competitor and strategic partner/investor. | accepted | $5B stake closed Dec 2025; joint NVLink products; does not cure the standalone accelerator gap. | E15, E16
- **D3** — Source hierarchy: SEC filings > Intel PR > reputable press > analyst commentary > aggregators/blogs. | accepted | Procedural; prevents overweighting weak sources. | —
- **D4** — Treat the US government stake as both strategic asset and structural constraint. | accepted (revised via R3) | Liquidity + too-important-to-fail vs. dilution, warrant, guardrails, foundry-separation barrier. | E13, E14
- **D5** — Strictly separate internal 18A execution from external foundry commercial validation. | accepted | Only ~$293M of $5.8B Q2 2026 foundry revenue was external. Contradicting evidence: foundry margin −71.7% → −36.2% on internal volume — real improvement, not merchant proof. | E5, E6, E8
- **D6** — Evaluate Intel AI exposure via Xeon/AI PCs/ASICs/packaging/NVIDIA-linked products, not merchant GPUs. | accepted | **Supersedes D7.** Falcon Shores cancelled as product; Gaudi disappointing. | E17, E18
- **D7** — Evaluate Intel's AI turnaround via its merchant GPU roadmap (Falcon → Jaguar Shores). | **superseded** (by D6) | Original "AI turnaround" framing; invalidated by cancellations/pivot. | E17, E18
- **D8** — Treat GAAP net income as non-informative without the bridge; anchor on non-GAAP + cash flow. | accepted | Q2 2026 GAAP $(11.0)B driven by $12.5B non-cash escrowed-share MTM; non-GAAP +$2.2B. | E11
- **D9** — Assume dividend = 0 in any Phase 2 base case absent primary-source reinstatement. | accepted | Suspended Q4 2024; CHIPS guardrails; cash priorities. | E13, E19, E20
- **D10** — Analyze leverage on net debt (~$20.8B), not gross; treat ~$30B liquidity as encumbered. | accepted | LT $48.5B + ST $2.0B vs. cash+MS $29.7B (6/30/2026, secondary sources). | E29
- **D11** — Use server CPU revenue share as primary competitive metric, unit share as context. | accepted | AMD 46.2% revenue share (Q1 2026) vs. ~34% units — winning the high-value mix. | E22
- **D12** — Foundry KPI is joint: (a) 18A internal yield/cost trajectory AND (b) significant external 14A customer commitment. | accepted | **Supersedes D1.** Depends on D5's separation. | E1–E8
- **D13** — Guardrail: never credit internal foundry revenue as merchant validation in Phase 2. | accepted | **Rationale explicitly depends on D5** (~95% of foundry revenue is internal). | E5, E6
- **D14** — Treat foundry funding as dilution-funded; Phase 2 must capture cumulative dilution. | accepted | Govt 433.3M + NVIDIA 214.7M + reported $20B raise + SoftBank $2B. | E13, E14, E16, E24, E30

---

## 4. Assumptions

| id | statement | confidence | status |
|---|---|---|---|
| A1' | 18A validates internal execution only; the commercial test is a significant external 14A customer (revised via R1) | high | active |
| A2' | NVIDIA is both dominant competitor and partner/investor; partnership doesn't cure the accelerator gap (revised via R2) | high | active |
| A3' | Government support is simultaneously liquidity/strategic asset and dilution/governance constraint (revised via R3) | high | active |
| A4 | Panther Lake broadly available from Jan 2026 as guided | high | active |
| A5 | 18A yields commercially viable (~65–80%) by H2 2026 | medium | active |
| A6 | No significant external 14A customer committed as of 2026-09-17 | high | active |
| A7 | Dividend stays suspended through the 3–5 yr base case | medium | active |
| A8 | Intel keeps server unit majority (~65%); AMD keeps gaining revenue share | medium | active |
| A9 | Net debt ≈ $21B mid-2026 (figures med-high; interpretation medium) | medium | active |
| A10 | Restructuring charges materially decline after 2026 | low | active |
| A11 | Intel stays supply-constrained in DCAI through 2026 | medium-low | active |
| A12 | TSMC ~70%+ merchant foundry share; Intel external share negligible | medium | active |
| A13 | Altera–Silver Lake closed H2 2025; Intel retains 49%, deconsolidates | medium | active |

**Revisions (old → new → trigger):**
- **R1:** A1 "18A success validates the foundry turnaround" → A1' (above). Trigger: $293M external of $5.8B Q2 2026 foundry revenue (E5, E6); $307M of $17.8B FY2025 (E8).
- **R2:** A2 "NVIDIA is purely a competitive threat" → A2' (above). Trigger: FTC clearance + completed $5B purchase, Dec 2025 (E16).
- **R3:** A3 "Government support de-risks the foundry" → A3' (above). Trigger: CHIPS amendment terms — 9.9%, warrant, guardrails (E13, E14).

---

## 5. Evidence

| id | kind | reference | summary |
|---|---|---|---|
| E1 | source | https://www.reuters.com/business/intel-outlines-details-first-pc-chip-made-its-new-manufacturing-tech-2025-10-09/ | Panther Lake = first 18A PC chip; >50% uplift claim; ramp 2025, broad availability Jan 2026 |
| E2 | source | https://www.pcgamer.com/hardware/processors/intels-bad-news-year-rolls-on-as-new-18a-chip-manufacturing-node-is-reportedly-in-trouble-with-10-percent-yields-and-doubts-over-profitability-of-the-panther-lake-cpu/ | Anonymous-source 18A ~10% yield claim; CFO: Panther Lake not initially accretive |
| E3 | source | https://www.eetimes.com/intels-confidence-shows-as-it-readies-new-processors-on-18a/ | Clearwater Forest/Xeon 6+ on 18A, H1 2026 |
| E4 | source | https://www.crn.com/news/components-peripherals/2025/intel-future-of-foundry-business-hinges-on-a-significant-external-customer | Foundry future hinges on significant external customer; 14A pause/discontinue warning |
| E5 | source | https://www.eetimes.com/intel-foundry-improves-execution-but-external-customers-remain-the-test/ | Q2 2026 foundry $5.8B rev, −$2.1B op loss, margin −36.2%; only $293M external (CFO Zinsner) |
| E6 | source | https://www.fool.com/investing/2026/08/11/intels-foundry-grew-31-last-quarter-and-lost-21-bi/ | $293M external of $5.8B; Fortinet first named customer (Intel 4); supply-constrained DC |
| E7 | source | https://www.fool.com/investing/2026/01/26/intels-make-or-break-foundry-moment-arrives-this-y/ | Essentially all foundry revenue internal (Jan 2026) |
| E8 | source | https://industry-blog.com/intel-foundry-revenue-external-customers/ | FY2025: $307M external of $17.8B; $10.3B op loss; Q1 2026 external $174M |
| E9 | source | https://www.nasdaq.com/press-release/intel-reports-second-quarter-2026-financial-results-2026-07-23 | Q2 2026: rev $16.1B +25%; GAAP EPS $(2.16); non-GAAP $0.42; Q3 guide |
| E10 | source | https://news.alphastreet.com/intel-corporation-intc-q2-2026-earnings-call-transcript/ | Segment detail: CCPG $8.9B, DCAI $6.3B +59%, foundry $5.8B; yield/cost commentary |
| E11 | document | https://www.businesswire.com/news/home/20260723707213/en/Intel-Reports-Second-Quarter-2026-Financial-Results | GAAP→non-GAAP bridge: $12.529B escrowed-share MTM dominates $(11.0)B GAAP loss |
| E12 | document | https://www.sec.gov/Archives/edgar/data/50863/000005086326000157/intc-20260627.htm | 10-Q MD&A: $797M impairment absence, Gaudi inventory charges absence, 18A cost improvement |
| E13 | source | https://www.reuters.com/technology/intel-amends-chips-act-deal-with-us-commerce-department-gets-57-billion-early-2025-08-29/ | $5.7B early CHIPS cash; 274.6M shares; 240.5M option; guardrails |
| E14 | document | https://businesswire.com/news/home/20250822458848/en/Intel-and-Trump-Administration-Reach-Historic-Agreement-to-Accelerate-American-Technology-and-Manufacturing-Leadership | 433.3M shares @ $20.47 = 9.9%; 5-yr $20 warrant (5%) if <51% foundry; no board seats |
| E15 | source | https://techcrunch.com/2025/09/18/nvidia-buys-5-billion-stake-in-intel-planning-ai-chip-collaboration/ | NVIDIA $5B @ $23.28; NVLink joint products; custom x86; RTX PC SoCs |
| E16 | source | https://www.reuters.com/legal/transactional/nvidia-takes-5-billion-stake-intel-under-september-agreement-2025-12-29/ | FTC cleared Dec 19 2025; purchase completed: 214.7M shares @ $23.28 |
| E17 | source | https://www.techtarget.com/searchdatacenter/news/366618595/Intel-axes-Falcon-Shores-amid-market-challenges | Falcon Shores cancelled as commercial product (test chip only) |
| E18 | source | https://www.tomshardware.com/tech-industry/artificial-intelligence/intel-cancels-falcon-shores-gpu-for-ai-workloads-jaguar-shores-to-be-successor | Pivot to Jaguar Shores / rack-scale |
| E19 | source | https://www.thestreet.com/investing/stocks/intel-dividends | Dividend suspended from Q4 2024 |
| E20 | source | https://www.barchart.com/story/news/2389397/intel-stock-has-risen-sixfold-from-its-2025-lows-but-dont-expect-a-dividend-yet | Still no dividend by 2026; LT debt >$43B; stock ~$100 (weak source for P/E 66) |
| E21 | source | https://www.reuters.com/technology/tsmc-pitched-intel-foundry-jv-nvidia-amd-broadcom-sources-say-2025-03-12/ | TSMC pitched JV to operate Intel fabs (≤50%); early-stage; 2024 net loss $18.8B |
| E22 | data | https://www.webpronews.com/amd-crosses-30-client-cpu-share-as-soaring-memory-costs-crush-desktop-shipments/ ; https://www.techspot.com/news/112419-amd-keeps-gaining-intel-servers-but-desktop-pcs.html ; https://www.theregister.com/systems/2026/06/04/amd-takes-a-third-of-server-cpu-market-as-shipments-grow/5251283 | Mercury Research: AMD server 34.5% units Q2 2026 (46.4% Xeon-SP-vs-EPYC); 46.2% revenue share Q1 2026; client 30.7% |
| E23 | source | https://techcrunch.com/2025/04/14/intel-agrees-to-sell-controlling-stake-in-altera-chip-business/ | Silver Lake 51% of Altera @ $8.75B valuation; Intel keeps 49%; close expected H2 2025 |
| E24 | document | https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-25-000126/0000050863-25-000126.pdf | SoftBank $2B @ $23/share definitive agreement, Aug 18 2025 |
| E25 | document | https://www.businesswire.com/news/home/20241202016400/en/Intel-Announces-Retirement-of-CEO-Pat-Gelsinger | Gelsinger retired effective Dec 1 2024; interim co-CEOs Zinsner + Holthaus |
| E26 | source | https://www.engadget.com/big-tech/intels-ceo-pat-gelsinger-has-suddenly-retired-151410215.html | Bloomberg: board gave retire-or-be-removed option |
| E27 | source | https://www.trendforce.com/news/2026/05/19/news-intel-18a-yields-improve-7-8-monthly-with-2h26-customers-expected-reportedly-pushes-18a-cpus-amid-tight-supply/ | CEO Tan (via CNBC): 18A yields +7–8%/mo; multiple foundry customer commitments expected 2H 2026 |
| E28 | source | https://wccftech.com/intel-14a-production-capacity-tipped-to-sit-at-6000-wafers-per-month-by-2027-end-with-18a-yields-at-80-says-analyst/ | GF Securities/Jeff Pu: 18A ~80% yield; 14A risk production Q1 2027 (analyst estimate) |
| E29 | data | https://www.zacks.com/stock/quote/INTC/balance-sheet ; https://www.barchart.com/stocks/quotes/INTC/balance-sheet/quarterly | 6/30/2026: LT debt $48.549B; ST debt $1.988B; cash $12.874B; marketable securities $16.853B (secondary) |
| E30 | source | https://www.ainvest.com/news/intel-foundry-funding-absorption-test-dilution-funded-turnaround-2609/ | Reported $20B equity raise @ $95 (~210.5M shares, ~4–5% dilution), Aug 2026 — WEAK source, unverified |
| E31 | source | https://www.entrepreneur.com/business-news/intel-is-laying-off-thousands-of-staff-as-part-of-turnaround/495070 ; https://www.nbcpalmsprings.com/business-finance-and-tech/2025/07/24/intel-cuts-15-of-workforce-in-major-restructuring-under-new-ceo | 15% workforce cut; ~75K core target; Tan CEO from Mar 18 2025 |
| E32 | source | https://www.crn.com/news/components-peripherals/2025/intel-to-cut-operating-expenses-by-1-5-billion-through-next-year | Opex targets ~$17B (2025) / ~$16B (2026) |

---

## 6. Artifacts

| id | kind | location | version | produced_by |
|---|---|---|---|---|
| ART1 | report | `docs/experiment-002/agent_a_journal.md` | v1 2026-09-17 | T11 |
| ART2 | report | `docs/experiment-002/agent_a_report.md` | v1 2026-09-17 | T11 |
| ART3 | state | `docs/experiment-002/world_state.md` | v1 2026-09-17 | T11 |

---

## 7. Actions (summarized)

Agent A executed ~14 public-web searches on 2026-09-17 (technology roadmap, Q2 2026 results, government stake, NVIDIA, AI accelerators, dividend, TSMC JV, leadership, foundry external split, AMD share, NVIDIA closing, 18A yields, Gelsinger exit, balance sheet, GAAP bridge, Altera/SoftBank), read the state-model schema, and wrote ART1–ART3. Notable: FA1 — attempted official 18A-yield verification, failed (no Intel disclosure exists); FA2 — attempted primary 10-Q debt-maturity narrative, failed (aggregators only). Full chronological detail in ART1.

---

## 8. Questions

| id | question | status | blocks |
|---|---|---|---|
| Q1 | Did the Altera–Silver Lake deal close in H2 2025; is Altera deconsolidated? | open | T12 (external-revenue interpretation) |
| Q2 | Did SoftBank's $2B investment close? | open | T12 |
| Q3 | Any TSMC-JV developments since March 2025? | open | T12 |
| Q4 | Which "multiple foundry customers" did CEO Tan expect in 2H 2026? | open | T12 |
| Q5 | Primary-source verification: 6/30/2026 balance sheet, debt maturities, Q2 financing flows | open | T12 |
| Q6 | Does the escrowed-share MTM recur; full-year GAAP bridge? | open | T12 |

---

## 9. StateChange log (append-only)

| seq | entity | entity_id | change | actor | timestamp | reason |
|---|---|---|---|---|---|---|
| 1 | Project | exp002 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Phase 1 assignment received |
| 2 | Task | T1 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 3 | Task | T2 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 4 | Task | T3 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 5 | Task | T4 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 6 | Task | T5 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 7 | Task | T6 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 8 | Task | T7 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 9 | Task | T8 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 10 | Task | T9 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 11 | Task | T10 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research plan |
| 12 | Decision | D1 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E1: 18A ramp as turnaround evidence |
| 13 | Decision | D2 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E15: NVIDIA partnership announced |
| 14 | Decision | D3 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Procedural: source hierarchy |
| 15 | Decision | D4 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E13/E14: government stake (naive de-risking frame) |
| 16 | Assumption | A1 | created (active) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Naive: 18A success validates foundry turnaround |
| 17 | Assumption | A2 | created (active) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Naive: NVIDIA purely competitive threat |
| 18 | Assumption | A3 | created (active) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Naive: government support de-risks foundry |
| 19 | Decision | D5 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E5–E8: internal vs external split ($293M) |
| 20 | Decision | D7 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Initial AI-via-GPU framing |
| 21 | Decision | D6 | created (accepted), supersedes D7 | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E17/E18: Falcon Shores cancelled; pivot |
| 22 | Decision | D7 | superseded | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Superseded by D6 |
| 23 | Assumption | A1 | superseded → A1' created (active, high) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | R1: external-revenue evidence |
| 24 | Assumption | A2 | superseded → A2' created (active, high) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | R2: NVIDIA stake closed (E16) |
| 25 | Assumption | A3 | superseded → A3' created (active, high) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | R3: government terms detail (E13/E14) |
| 26 | Decision | D8 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E11: GAAP bridge (escrowed-share MTM) |
| 27 | Decision | D9 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E13/E19/E20: dividend = 0 base case |
| 28 | Decision | D10 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E29: net-debt framing |
| 29 | Decision | D11 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E22: revenue-share metric |
| 30 | Decision | D12 | created (accepted), supersedes D1 | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Joint KPI from D5 + R1 |
| 31 | Decision | D1 | superseded | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Superseded by D12 |
| 32 | Decision | D13 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Guardrail; rationale depends on D5 |
| 33 | Decision | D14 | created (accepted) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | E13/E14/E16/E24/E30: dilution-funded buildout |
| 34 | Assumption | A4–A13 | created (active) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Confidence levels per §4 |
| 35 | Evidence | E1–E32 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Research capture |
| 36 | Question | Q1–Q6 | created (open) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Handoff gaps |
| 37 | Task | T11 | status_changed → done | agent:Muse Spark:exp002-agent-a | 2026-09-17 | ART1–ART3 written |
| 38 | Task | T12 | created (proposed) | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Phase 2 verification work |
| 39 | Artifact | ART1–ART3 | created | agent:Muse Spark:exp002-agent-a | 2026-09-17 | Deliverables |

---

## 10. Handoff bundle

**Context snapshot:** Agent A completed Phase 1 public-source research on Intel (3–5 yr horizon) on 2026-09-17. No valuation, no recommendation, no code — per assignment. Deliverables: `docs/experiment-002/agent_a_journal.md` (raw journal), `docs/experiment-002/agent_a_report.md` (structured report), `docs/experiment-002/world_state.md` (this file).

**Active tasks:** T12 (proposed) — Phase 2 primary-source verification and open-question resolution (Q1–Q6).

**Accepted decisions (14):** D2, D3, D4 (revised), D5, D6, D8, D9, D10, D11, D12 (supersedes D1), D13 (depends on D5), D14. Superseded but retained: D1, D7.

**Active assumptions (13):** A1'–A3' (high), A4 (high), A5 (medium), A6 (high), A7 (medium), A8 (medium), A9 (medium), A10 (low), A11 (medium-low), A12 (medium), A13 (medium). Three genuine revisions recorded (R1–R3).

**Open questions:** Q1 (Altera close), Q2 (SoftBank close), Q3 (TSMC JV status), Q4 (2H-2026 foundry customers), Q5 (10-Q balance-sheet/maturity verification), Q6 (escrowed-share MTM recurrence).

**Key evidence:** E5/E6 (only $293M external of $5.8B foundry revenue — the single most important fact), E11 (GAAP loss = $12.5B escrowed-share MTM), E13/E14 (government 9.9% + warrant + guardrails), E16 (NVIDIA $5B closed), E22 (AMD 46.2% server revenue share), E29 (net debt ~$20.8B).

**Recent changes:** D12 superseded D1 (joint foundry KPI); D6 superseded D7 (AI framing); R1–R3 revised the three naive opening assumptions; T11 done; T12 proposed.

**Guardrails for the next participant:** G1 — no base-case credit for unannounced customers, rumored JVs, or internal foundry revenue as merchant validation; G2 — include an explicit no-external-14A-customer downside case; G3 — dividend at zero absent primary-source reinstatement; G4 — the human decides buy/hold/sell.

**Caveats:** Several figures rest on secondary/weak sources (marked in ART2 §9): the August 2026 $20B equity raise, forward P/E 66, TSMC 72% share, and the 18A yield estimates (no official Intel disclosure exists — FA1). Do not treat any single 18A yield number as fact.
