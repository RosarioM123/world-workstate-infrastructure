# Experiment #002 — Day 5 blind-grading answer key

**Predeclared:** 2026-09-21, BEFORE any grading. Source: Agent A's Phase 1 record
(`agent-a-world-state.md` + `agent-a-report.md`, authored 2026-09-17, verified 2026-09-18).
This key is neutral: it describes Agent A's record only and contains no information
about which handoff condition any continuation was built from.

## Decisions (14)

| id | statement | status | key rationale | key evidence |
|---|---|---|---|---|
| D1 | Treat the 18A Panther Lake ramp as the primary evidence of process turnaround | **SUPERSEDED by D12** | first high-volume leading-edge node in years | E1 (Reuters Oct 2025) |
| D2 | Frame NVIDIA as both dominant AI competitor and strategic partner/investor | accepted | $5B stake closed Dec 2025; joint NVLink products; does not cure standalone accelerator gap | E15, E16 |
| D3 | Source hierarchy: SEC filings > Intel PR > reputable press > analyst commentary > aggregators/blogs | accepted (procedural) | prevents overweighting weak sources | — |
| D4 | Treat the US government stake as both strategic asset and structural constraint | accepted (revised via R3) | $5.7B early CHIPS cash + too-important-to-fail vs 9.9% dilution, warrant, guardrails, foundry-separation barrier | E13, E14 |
| D5 | Strictly separate internal 18A execution from external foundry commercial validation | accepted | only ~$293M of $5.8B Q2 2026 foundry revenue was external | E5, E6, E8; tension: margin −71.7%→−36.2% is real improvement but internal-volume-driven |
| D6 | Evaluate Intel AI via Xeon/AI PCs/ASICs/packaging/NVIDIA-linked products, not merchant GPUs | accepted; **supersedes D7** | Falcon Shores cancelled as product; Gaudi disappointing | E17, E18 |
| D7 | Evaluate Intel AI turnaround via merchant GPU roadmap (Falcon → Jaguar Shores) | **SUPERSEDED by D6** | original "AI turnaround" framing, invalidated by cancellations/pivot | E17, E18 |
| D8 | Treat GAAP net income as non-informative without the bridge; anchor on non-GAAP + cash flow | accepted | Q2 2026 GAAP $(11.0)B driven by $12.5B non-cash escrowed-share MTM; non-GAAP +$2.2B; MTM is a real economic cost of the deal structure | E11 |
| D9 | Dividend = 0 in any Phase 2 base case absent primary-source reinstatement | accepted | suspended Q4 2024; CHIPS guardrails; cash priorities | E13, E19, E20 |
| D10 | Analyze leverage on net debt (~$20.8B), not gross; treat ~$30B liquidity as encumbered | accepted | LT $48.5B + ST $2.0B vs cash+MS $29.7B (6/30/2026, secondary sources; primary 10-Q verification unfinished) | E29 |
| D11 | Use server CPU revenue share as primary competitive metric, unit share as context | accepted | AMD 46.2% revenue share Q1 2026 vs ~34% units — winning the high-value mix | E22 |
| D12 | Foundry KPI is joint: (a) 18A internal yield/cost trajectory AND (b) significant external 14A customer | accepted; **supersedes D1; depends on D5** | neither alone suffices | E1–E8 |
| D13 | Guardrail: never credit internal foundry revenue as merchant validation in Phase 2 | accepted; **rationale explicitly depends on D5** | ~95% of foundry revenue is internal | E5, E6 |
| D14 | Treat foundry funding as dilution-funded; Phase 2 must capture cumulative dilution | accepted | govt 433.3M + NVIDIA 214.7M + reported $20B raise + SoftBank $2B | E13, E14, E16, E24, E30 (the $20B raise is weakly sourced) |

## Assumptions (13, with confidence)

- **A1'** — 18A validates internal execution only; the commercial test is a significant external 14A customer (revised via R1). **high**
- **A2'** — NVIDIA is both dominant competitor and partner/investor; partnership doesn't cure the accelerator gap (revised via R2). **high**
- **A3'** — Government support is simultaneously liquidity/strategic asset and dilution/governance constraint (revised via R3). **high**
- **A4** — Panther Lake broadly available from Jan 2026 as guided. **high**
- **A5** — 18A yields commercially viable (~65–80%) by H2 2026. **medium** (10% anonymous claim vs 65–80% analyst estimates; Intel discloses no official figure)
- **A6** — No significant external 14A customer committed as of 2026-09-17. **high**
- **A7** — Dividend stays suspended through the 3–5 yr base case. **medium**
- **A8** — Intel keeps server unit majority (~65%); AMD keeps gaining revenue share. **medium**
- **A9** — Net debt ≈ $21B mid-2026. **medium-high on figures / medium on interpretation** (primary 10-Q verification unfinished)
- **A10** — Restructuring charges materially decline after 2026. **low**
- **A11** — Intel stays supply-constrained in DCAI through 2026. **medium-low** (management claim via secondary sources; underinvestment is an alternative explanation)
- **A12** — TSMC ~70%+ merchant foundry share; Intel external share negligible. **medium**
- **A13** — Altera–Silver Lake closed H2 2025; Intel retains 49%, deconsolidates. **medium** (completion unconfirmed)

## Revisions (old → new → trigger)

- **R1:** A1 "18A success validates the foundry turnaround" → A1'. Trigger: $293M external of $5.8B Q2 2026 foundry revenue (E5, E6); $307M of $17.8B FY2025 (E8); first named customer (Fortinet) on mature Intel 4.
- **R2:** A2 "NVIDIA is purely the competitive threat" → A2'. Trigger: FTC clearance + completed $5B purchase, Dec 2025 (E16).
- **R3:** A3 "Government support de-risks the foundry" → A3'. Trigger: CHIPS amendment terms — 9.9%, 5-yr $20 warrant (5%) if <51% foundry ownership, guardrails (E13, E14).

## Guardrails / constraints for Phase 2

- **G1.** No Phase 2 base case may credit unannounced customers, rumored JVs (e.g., TSMC), or internal foundry revenue as merchant-foundry validation. Only binding, disclosed commercial terms count.
- **G2.** Phase 2 must include an explicit downside case: no significant external 14A customer materializes and foundry operating losses persist.
- **G3.** Model the dividend at zero unless primary-source evidence of reinstatement appears.
- **G4.** The human retains final buy/hold/sell authority; Phase 2 produces analysis, not a recommendation.
- **Scope exclusions (binding):** no valuation modeling (no DCF/multiples), no buy/hold/sell recommendation, no prototype code.

## Open questions (6)

- **Q1.** Did the Altera–Silver Lake transaction close in H2 2025, and is Altera deconsolidated? (Blocks clean interpretation of "external" foundry revenue.)
- **Q2.** Did SoftBank's $2B investment (announced Aug 2025) close?
- **Q3.** Any developments in the TSMC foundry-JV talks since March 2025? None found.
- **Q4.** Which "multiple foundry customers" did CEO Tan expect to commit in 2H 2026? Only Fortinet (Intel 4) named.
- **Q5.** Primary-source verification of the 6/30/2026 balance sheet, debt maturity schedule, and Q2 2026 financing flows from the 10-Q.
- **Q6.** Does the escrowed-share mark-to-market recur, and what is the full-year GAAP→non-GAAP bridge?

## Failed approaches (2)

- **FA1.** Official 18A yield verification: FAILED. Intel has never publicly disclosed node-level yields. Lesson: any thesis depending on a specific yield number is building on sand; use the joint KPI (D12).
- **FA2.** Primary-source 10-Q debt narrative: FAILED (partial). Aggregators only; maturity schedule and Q2 financing flows unverified.

## Provenance anchors (key evidence)

- **E5/E6** — only $293M external of $5.8B Q2 2026 foundry revenue (single most important fact).
- **E11** — GAAP $(11.0)B loss dominated by $12.5B escrowed-share MTM.
- **E13/E14** — government 9.9% stake + warrant + guardrails.
- **E16** — NVIDIA $5B stake closed Dec 2025.
- **E22** — AMD 46.2% server revenue share (Q1 2026).
- **E29** — net debt ~$20.8B (6/30/2026, secondary sources).

## Explicit caveats (weak/conflicting claims flagged by Agent A)

- Do NOT treat any single 18A yield number as fact (10% anonymous vs 65–80% analyst; no official figure).
- The August 2026 $20B equity raise @ $95 is weakly sourced (single low-credibility aggregator); treat as unverified.
- "Forward P/E 66," "Ireland SCIP 49% buyback," "Q1 2026 operating FCF −$2.5B" are secondary/weak sources; directional use only.

## Dependencies / history rules

- D13's rationale explicitly depends on D5. D12 supersedes D1 and depends on D5. D6 supersedes D7.
- D1 and D7 are superseded but their history is retained; they must be referenced as history, never as live decisions.
- R1–R3 record genuine reversals of the three naive opening priors (A1/A2/A3); the naive forms must not be resurrected.
