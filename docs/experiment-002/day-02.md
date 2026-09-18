# Experiment #002 — Day 2 (2026-09-18): Agent A verification & capture

## Outcome
Agent A's Intel (INTC) research outputs verified **present, complete, and above
all protocol §3 complexity minimums**. No re-run needed. Raw materials captured
into this log and archived as `agent-a-journal.md`, `agent-a-report.md`, and
`agent-a-world-state.md` under `docs/experiment-002/`.

## Verification against protocol §3 (each check executed 2026-09-18)

| Minimum (§3) | Found | Result |
|---|---|---|
| 10–15 meaningful decisions, each with rationale and linked evidence | **14** (D1–D14) | PASS |
| 10+ assumptions, each with explicit confidence level | **13** (A1′–A13; high / medium / medium-low / low) | PASS |
| ≥3 genuine revisions (old → new → triggering evidence) | **3** (R1, R2, R3) | PASS |
| ≥2 decisions later superseded (history preserved) | **2** (D1→D12, D7→D6) | PASS |
| ≥2 explicit constraints/guardrails binding Phase 2 | **4** (G1–G4) | PASS |
| Evidence supporting *and* contradicting key decisions | D5 (foundry margin improvement vs 10%-yield reports), D12/A1′ (real 18A progress vs 95% internal foundry revenue), R2 (NVIDIA partnership vs competitor) | PASS |
| ≥3 unresolved open questions | **6** (Q1–Q6) | PASS |
| ≥1 documented failed research approach | **2** (FA1: official 18A yield disclosure — none exists; FA2: primary 10-Q debt-maturity narrative — aggregators only) | PASS |
| ≥1 decision whose rationale explicitly depends on a previous decision | **D13 depends on D5** (and D12 depends on D5 + supersedes D1) | PASS |
| Provenance (source URLs) for important claims | **32 evidence entries** (E1–E32) | PASS |

Cross-file consistency: report (§2–§9) and world_state (§3–§10) carry the same
decision/assumption/revision/question inventories. The journal pre-registered
Agent A's three naive priors *before* research began (13:30, §13:30 entry: 18A
validates foundry; NVIDIA is purely a threat; government support de-risks) —
all three were later reversed by R1–R3 with named trigger evidence. This is
exactly the revision behavior the experiment requires.

Word counts (verified `wc -w`): journal **3,616** · report **2,376** ·
world_state **3,173** · total **9,165**.

## Captured content (authoritative source: agent-a-report.md)

### Decisions D1–D14 (statement / status / rationale-core)
- **D1 [SUPERSEDED by D12]:** Treat 18A Panther Lake ramp as primary process-turnaround evidence. *Was:* first high-volume leading-edge node in years (E1). *Why superseded:* external-revenue split showed process execution ≠ foundry business validation.
- **D2 (accepted):** NVIDIA = dominant AI competitor AND strategic partner/investor, not pure competitor. $5B stake closed Dec 2025; joint NVLink products (E15, E16).
- **D3 (accepted, procedural):** Source hierarchy SEC filings > Intel PR > reputable press > analyst commentary > aggregators/blogs — prevents overweighting weak figures.
- **D4 (accepted, revised via R3):** US government stake = strategic asset AND structural constraint ($5.7B early CHIPS cash vs 9.9% dilution, warrant, guardrails, foundry-separation barrier; E13, E14).
- **D5 (accepted):** Strictly separate internal 18A execution from external foundry commercial validation — ~$293M of $5.8B Q2 2026 foundry revenue external (E5, E6, E8). *Contradicting evidence recorded:* foundry margin −71.7% → −36.2% YoY, real improvement driven by internal volume.
- **D6 (accepted, SUPERSEDES D7):** Evaluate Intel AI exposure via Xeon/AI PCs/ASICs/packaging/NVIDIA-linked products, not merchant GPU challenger (Falcon Shores cancelled as product; E17, E18).
- **D7 [SUPERSEDED by D6]:** Merchant GPU-accelerator framing of the AI turnaround (Falcon Shores → Jaguar Shores). Invalidated by cancellations/pivot.
- **D8 (accepted):** GAAP net income non-informative without reconciliation; anchor on non-GAAP + cash flow — Q2 2026 GAAP $(11.0)B driven by $12.5B non-cash escrowed-share mark-to-market (E11).
- **D9 (accepted):** Dividend = 0 in any Phase 2 base case absent primary-source reinstatement (suspended Q4 2024; CHIPS guardrails; E13, E19, E20).
- **D10 (accepted):** Leverage on net debt (~$20.8B), not gross; ~$30B liquidity real but encumbered (LT $48.5B + ST $2.0B vs cash+MS $29.7B, 6/30/2026, secondary sources; E29).
- **D11 (accepted):** Server CPU *revenue* share as primary competitive metric, unit share as context (AMD 46.2% revenue share Q1 2026 vs ~34% units — winning the high-value mix; E22).
- **D12 (accepted, SUPERSEDES D1, depends on D5):** Foundry KPI is joint: (a) 18A internal yield/cost trajectory AND (b) significant external 14A customer commitment. Neither alone suffices (E1–E8, E4).
- **D13 (accepted, depends on D5):** Guardrail — never credit internal foundry revenue as merchant validation (~95% internal).
- **D14 (accepted):** Foundry funding is dilution-funded; Phase 2 must capture cumulative dilution (govt 433.3M + NVIDIA 214.7M + reported $20B raise + SoftBank $2B; E13/E14/E16/E24/E30, latter weakly sourced).

### Assumptions A1′–A13 (confidence)
A1′ high · A2′ high · A3′ high · A4 high · A5 medium · A6 high · A7 medium ·
A8 medium · A9 medium-high (figures) / medium (interpretation) · A10 low ·
A11 medium-low · A12 medium · A13 medium.

### Revisions R1–R3
- **R1 (foundry validation):** "18A success validates the foundry turnaround" → "18A validates internal execution only; the commercial test is a significant external 14A customer." Trigger: $293M external of $5.8B (Q2 2026); $307M of $17.8B (FY2025).
- **R2 (NVIDIA):** "NVIDIA purely the competitive threat" → "both dominant competitor and strategic partner/investor." Trigger: FTC clearance + completed $5B purchase, Dec 2025.
- **R3 (government):** "Government support de-risks the foundry" → "asset AND constraint (9.9% + warrant, guardrails, barrier to foundry separation)." Trigger: CHIPS amendment terms.

### Guardrails for Phase 2 (G1–G4)
- G1: No base-case credit for unannounced customers, rumored JVs (e.g., TSMC), or internal foundry revenue as merchant validation.
- G2: Must include an explicit downside case (no significant external 14A customer; foundry losses persist).
- G3: Dividend at zero absent primary-source reinstatement.
- G4: Human retains final buy/hold/sell authority; Phase 2 produces analysis, not a recommendation.

### Open questions Q1–Q6
Q1 Altera–Silver Lake closing/deconsolidation · Q2 SoftBank $2B closing ·
Q3 TSMC JV status since Mar 2025 · Q4 names of "multiple" 2H-2026 foundry
customers CEO Tan expected · Q5 primary 10-Q verification of balance sheet,
debt maturities, Q2 financing flows · Q6 escrowed-share MTM recurrence and
full-year GAAP bridge.

### Failed approaches
- FA1 — No official Intel disclosure of node-level 18A yields exists (10% anonymous claim vs 65–80% analyst estimates irreconcilable). Fallback: margin trajectory + management cost commentary; joint KPI (D12) instead.
- FA2 — Q2 2026 10-Q MD&A debt-maturity narrative unreachable (aggregators only); figures corroborated across 3 sources, interpretation still open.

### Key single facts (for Day 5 answer key)
- External foundry revenue ~$293M of $5.8B (Q2 2026); FY2025 $307M of $17.8B (E5, E6, E8).
- Q2 2026 GAAP loss $(11.0)B = $12.5B escrowed-share MTM (E11).
- Govt 9.9% (433.3M @ $20.47) + 5-yr $20 warrant for 5% more if Intel <51% foundry (E13, E14).
- NVIDIA $5B stake closed Dec 2025 (214.7M @ $23.28) (E16).
- AMD server revenue share record 46.2% (Q1 2026) (E22).
- Net debt ≈ $20.8B mid-2026 (E29).
- Weak/unverified: Aug 2026 $20B raise @ $95 (E30), 18A yield numbers, forward P/E 66, Ireland SCIP buyback.

## Procedural notes
- Agent A authored the WORLD state itself (protocol §10 limitation #5 records this as an improvement over #001).
- Archival note: world_state.md §6 ART table lists artifact paths as `/tmp/exp002/`; the actual staged location was `~/workspace/exp002/agent-a/`. Repo copies live here under canonical names.
- Agent B isolation: Day 2 materials were not shared with any continuation agent. (Known limitation §10 #1 still applies: subagent context inheritance is un-fixable; mitigation on Day 3/4 is blind labels + filename-echo stripping.)

## Next (Day 3, 2026-09-19)
Build three handoffs from Agent A's bundle: (A) structured WORLD state from
`agent-a-world-state.md`, cleaned and schema-conformant; (B) independent
summary writer gets `agent-a-journal.md` + `agent-a-report.md` ONLY — never
the WORLD state file — instructed per protocol §2; (C) raw journal. Measure
words (and tokens if available) and structured-field counts; blind-label X/Y/Z
with the private mapping stored ONLY in experiment-state.md. Write day-03.md. Commit.
