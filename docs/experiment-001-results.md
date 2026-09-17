# Experiment #001: Cross-Agent Work-State Handoff — Results

**Date:** 2026-09-17
**Repository:** RosarioM123/world (docs only; no application code built)
**Status:** Complete — all three conditions run, blind-graded, results recorded.

## Verdict (up front)

**WORLD state (Condition A) won — narrowly, but on the dimensions that matter most to the thesis.**

All three continuations recovered all 13 key facts with zero evidence errors and zero contradictions. The differences appeared in *structure*: only the WORLD-conditioned Agent B recovered all five decisions with rationales intact, all seven assumptions with correct confidence levels, and the full revision trail (including the original and superseding change-log entries). It also produced the shortest faithful output (1,902 words vs 2,785 and 2,863) despite receiving the longest input.

- **Condition A (WORLD state):** blind quality 5/5 — decisions 5/5, assumptions 7/7, zero errors, zero unsupported claims, nothing lost.
- **Condition B (conventional summary):** blind quality 5/5 — facts 13/13, assumptions 7/7, but lost D-002 (bitcoin enterprise-value decision) as an explicit decision; 1 continuation-neutral note.
- **Condition C (raw transcript):** blind quality 4/5 — facts 13/13, but rebuilt the decision/assumption taxonomy in its own terms: recovered only 1/5 decisions canonically, 0/7 canonical confidence labels, and dropped D-004's binding guardrail ("no buy thesis without a stress case").

**The headline finding:** narrative formats preserve *facts*; the structured state preserved *governance* — decisions, their rationale, confidence levels, and the guardrails that constrain the successor. The WORLD overhead was real but small: +209 words (+17%) over the summary-length input, and the extra structure paid for itself in a shorter, more faithful output.

**Recommendation:** proceed to Experiment #002 with a larger, more adversarial design. Do not yet conclude WORLD is production-warranted — n=1, one task, one model family, and imperfect blinding (see §9 Limitations).

---

## 1. Setup

**Objective (from `docs/experiment-handoff.md`):** measure whether a structured WORLD state preserves more of the information an incoming agent needs — findings, assumptions, decisions, open questions, and especially the *revision trail* — than a conventional summary or a raw transcript, without costing more than it returns.

**Research task (identical across conditions):** Continue Phase 1 investment research on Block, Inc. (NYSE SQ; ticker rebranded to XYZ) for a 3–5 year horizon — toward a preliminary memo with valuation modeling and a credit-cycle stress test. The final buy/hold/sell recommendation is reserved for the human per protocol.

**Agent A (Phase 1):** completed 2026-09-17T21:26:01Z. Researched segments, financials, competition, risks, bitcoin; produced findings, evidence with URLs, 7 assumptions with confidence levels, 5 preliminary decisions with rationale, 8 open questions, and one genuine correction (the lending assumption revision). Deferred valuation modeling, the credit stress test, and the recommendation.

**Agent B (Phase 2 continuation, identical brief across conditions):** each run received exactly one handoff file as its sole source of project context, was forbidden from browsing, and was asked to produce four sections: (1) inherited state, (2) assumption check, (3) open questions answered as far as the handoff allows, (4) continuation brief with concrete next steps. The exact brief is reproduced in §5.

**Constants held:** same research task and objective; same starting information (all three handoffs derived from the same Agent A output); same Agent B model; no browsing for any run; identical output structure requested; same evaluator and answer key for all three.

**Handoff preparation:** all three handoffs were authored/assembled in one sitting on 2026-09-17 (~20 minutes of authoring time total):
- **A — WORLD state** (`handoff_1.md`): structured per `docs/state-model.md` — project context, task table, decisions with rationale, assumptions with confidence, evidence IDs, action log, immutable state-change log, open questions, artifacts, handoff bundle. 1,450 words.
- **B — Conventional summary** (`handoff_2.md`): carefully written natural-language summary with the same substantive information, deliberately given every decision, assumption, confidence level, and the revision narrative. 1,241 words.
- **C — Transcript** (`handoff_3.md`): Agent A's unedited working journal (9 entries), preserving chronology, doubts, and the revision as it happened. 1,054 words.

WORLD structuring overhead vs the summary: **+209 words (+17%)** of input.

**Timing (UTC, 2026-09-17):** B runs spawned ~21:26:30Z; completions 21:27:13Z (A), 21:27:17Z (B), 21:27:20Z (C) — roughly one minute each, no meaningful difference in latency. Grader completed 21:28:11Z. No browsing in any run, so token costs were dominated by input+output length (see §8).

## 2. Agent A task (exact brief, condensed)

Research Block, Inc. (NYSE: SQ — Agent A noted the ticker had been rebranded to XYZ) for a 3–5 year investment horizon: business segments (Square, Cash App, Afterpay, TIDAL, bitcoin initiatives), financial health, competitive position, risks and catalysts. Produce a running journal, findings with sources, assumptions with confidence, preliminary decisions, open questions, at least one genuine correction, and explicitly leave valuation modeling, the credit-cycle stress test, and the final buy/hold/sell recommendation unfinished for Phase 2. Public sources only; no application code.

## 3. Agent A final report (verbatim ground truth)

# Block, Inc. (NYSE: SQ / ticker now XYZ) — Phase 1 Research
**Analyst:** Agent A | **Date:** 2026-09-17 | **Horizon:** 3–5 years | **Scope:** research only; valuation model and buy/hold/sell recommendation explicitly deferred to Phase 2.

## (a) Key Findings

1. **2026 is a genuine operating turnaround, not just cost cuts.** Q2 2026: gross profit $3.17B (+25% YoY), Cash App GP +31%, Square GP and GPV both +13% with US GPV at its strongest growth since Q2 2023. FY2026 guidance raised across the board (GP $12.51B, +21%; adj EPS $3.85–4.02). This follows a rough 2025 (Q3 revenue miss, stock −24% YTD at one point). Source: Reuters 2026-08-05; TheStreet 2026-08-05; Fool earnings transcript 2026-08-12.
2. **Cash App has pivoted from user growth to monetization depth.** Monthly transacting actives grew only 3% (June 2026), but inflows per active +9%, primary banking actives +17%, monetization rate 1.53%→1.65%, and Cash App Borrow originations +59% YoY to $18.9B. Growth is engagement-led. Source: Zacks 2026-08-21; Fool transcript.
3. **Cash App Borrow is the highest-upside, highest-risk engine.** FDIC approval unlocked scaling (15M+ users); Q1 2026 risk loss rates of 2.67–3.16% by cohort look disciplined. But Q3 2025 showed the downside: transaction/loan/consumer-receivable losses spiked 89% to $363.5M. Untested in a recession. Sources: American Banker (Borrow/FDIC); FinancialContent 2025-11-07 (loss spike).
4. **Square is successfully moving upmarket.** Mid-market sellers (>$500k/yr GPV) now 45% of GPV (vs 41% two years ago); international GPV +26% vs US +9% (Q3 2025); 200+ ISO partners; dedicated restaurant push. Competitive set: Fiserv Clover (~$300B GPV), Toast ($215B, 180k locations), Stripe, PayPal, Adyen. Sources: PYMNTS 2025; Zacks 2026-08-27; Coinlaw POS stats.
5. **The 40% headcount cut (Feb 2026) is the pivotal strategic bet.** 10,000+ → <6,000, framed as "AI-native" restructuring; stock +20% on the news; record 27% adj. operating income margin in Q2 2026. Critics call it "AI-washing" of pandemic-era bloat (headcount 3,835 in 2019 → 12,430 in 2022). Execution risk: product quality and velocity with half the staff is unproven beyond ~2 quarters. Sources: CNN, VentureBeat, Entrepreneur, eWeek (all Feb–Mar 2026).
6. **Regulatory overhang is material but bounded.** ~$300M+ in settlements: CFPB Jan 2025 ($120M redress + $55M penalty), $80M to states (BSA/AML), $45M to 46 state AGs (July 2026, requires 24/7 live support). Ongoing compliance obligations raise the cost of operating Cash App. Sources: Bloomberg Law; American Banker; ConsumerAffairs.
7. **Bitcoin is ideology + optionality, not the P&L driver.** 28,355 BTC held (~$2.2B, Q1 2026 proof-of-reserves; ~$692M corporate treasury). New: Bitkey wallet revamp, Square bitcoin acceptance via NFC/Lightning (zero fees through 2026, 4M+ sellers eligible), Proto mining hardware, on-chain proof-of-reserves. But bitcoin revenue is ~1/3 of total revenue at near-zero margin — it moves headlines, not gross profit. Sources: The Block 2026-04-28; Bitcoin Magazine; Cointelegraph; Motley Fool.
8. **Afterpay is healthy but not a growth engine; BNPL is commoditizing.** GMV +13% to $10.3B, GP +14% (Q1 2025). Competitive pressure from Klarna, Affirm (now GAAP profitable), PayPal Pay Later, and bank-issued installments. Sources: FinancialContent 2025-07-31; PYMNTS BNPL study; Fool 2026-06-02.
9. **Multi-year targets set a high bar.** Investor Day 2025: mid-teens GP growth to ~$15.8B by 2028, adj. operating income ~30%/yr to $4.6B, adj. EPS low-30s% to $5.50, Rule of 40 in 2026 sustained through 2028. Consensus analyst target ~$95.42 (Moderate Buy, 42 analysts) vs ~$76–79 current. Whether the price already discounts the 2028 targets is THE valuation question for Phase 2. Sources: Morningstar/BusinessWire 2025-11-18; MarketBeat; Stockopedia.

## (b) Evidence with Source URLs

- Q2 2026 results & guidance raise: https://www.reuters.com/business/blocks-second-quarter-profit-rises-consumer-spending-stays-resilient-2026-08-05/
- Q2 2026 earnings call transcript (Ahuja on Square/Cash App metrics): https://www.fool.com/earnings/call-transcripts/2026/08/12/block-xyz-q2-2026-earnings-call-transcript/
- Q2 2026 live recap: https://www.thestreet.com/latest-news/block-inc-xyz-q2-2026-earnings-call-updates
- Cash App deep dive (Borrow $18.9B, monetization 1.65%): https://www.zacks.com/stock/news/2978319/blocks-q226-cash-app-profit-jumps-31-can-it-sustain-growth
- Q1 2026 beat & AI restructuring narrative: https://siliconangle.com/2026/05/07/block-raises-2026-outlook-first-quarter-earnings-beat-accelerating-gross-profit-growth/
- Q3 2025 stumble (revenue miss, 89% loss spike, Square margin compression): https://markets.financialcontent.com/stocks/article/marketminute-2025-11-7-block-sq-stumbles-fintech-giant-struggles-to-move-markets-amid-profitability-concerns
- Q3 2025 analysis (Square upmarket, Cash App +24% GP): https://pymnts.com/earnings/2025/blocks-third-quarter-puts-spotlight-on-fintech-realities-not-crypto-dreams/
- Segment financials (Q2 2026 investor presentation PDF): https://s29.q4cdn.com/628966176/files/doc_financials/2026/q2/Block-Investor-Presentation-Q2-2026.pdf
- Investor Day 2025 financial outlook: https://block.xyz/documents/block-investor-day-2025-financial-outlook.pdf
- 3-year outlook summary: https://www.morningstar.com/news/business-wire/20251118908846/block-shares-multi-year-financial-outlook-at-investor-day
- 40% layoffs / AI-native reset: https://www.cnn.com/2026/02/26/business/block-layoffs-ai-jack-dorsey?cid=external-feeds_iluminar_meta
- Layoff analysis + Q4 metrics (Rule of 40, Borrow +223%): https://venturebeat.com/orchestration/jack-dorseys-block-cuts-40-of-staff-4-000-people-and-yes-its-because-of-ai
- "AI-washing" critique: https://www.entrepreneur.com/business-news/jack-dorseys-block-cuts-4000-jobs-critics-claim/503108
- CFPB $175M settlement: https://news.bloomberglaw.com/crypto/block-to-pay-175-million-for-cash-app-customer-service-failures
- $45M state AG settlement (July 2026): https://www.americanbanker.com/news/block-to-pay-45m-to-states-for-fraud-on-cash-app
- Cash App Borrow after FDIC approval (loss rates, 15M users): https://www.americanbanker.com/payments/news/blocks-cash-app-borrow-jumps-after-fdic-lending-approval
- Bitcoin proof-of-reserves (28,355 BTC): https://www.theblock.co/news/business/2026-04-28-block-q1-bitcoin-399123
- Bitcoin ecosystem revamp (Bitkey, Square NFC bitcoin, 5% Bitcoin Back): https://bitcoinmagazine.com/news/block-bitcoin-ecosystem-with-bitkey-wallet
- Square bitcoin acceptance analysis: https://www.fool.com/investing/2026/06/13/fintech-stock-ultimate-cryptocurrency-use-case/
- Square competition / restaurant push: https://www.zacks.com/stock/news/2981398/block-pushes-square-further-into-restaurants-can-growth-accelerate
- POS competitive scale (Clover, Toast, Shift4): https://coinlaw.io/point-of-sale-statistics/
- BNPL competitive dynamics (Afterpay 58% of subprime users): https://www.pymnts.com/study_posts/beyond-pay-in-4-how-bnpl-providers-compete-for-first-choice/
- Affirm vs Klarna 2026: https://www.fool.com/coverage/better-buy/2026/06/02/affirm-vs-klarna-which-technology-stock-is-a-better-buy-in-2026/
- Analyst consensus ($95.42 target, Moderate Buy): http://marketbeat.com/stocks/NYSE/XYZ/forecast/
- Segment overview (Q1 2025 baseline): https://markets.financialcontent.com/winslow/article/marketminute-2025-7-31-blocks-journey-from-mobile-payments-to-a-financial-ecosystem-powerhouse

## (c) Assumptions (with confidence)

1. **Cash App's monetization-deepening can compound for 3–5 years without user growth re-accelerating.** (medium) — Engagement metrics support it, but actives growth of 3% is a thin base; Borrow/lending saturation is the binding constraint.
2. **Cash App Borrow credit quality stays within the 2.7–3.2% loss-rate band through a normal credit environment.** (low) — Only ~2 quarters of scaled data post-FDIC approval; Q3 2025's 89% loss spike is the cautionary precedent. A recession would invalidate this fast.
3. **The 40% headcount cut was mostly removal of pandemic bloat, and AI tooling sustains product velocity.** (medium-low) — Early evidence positive (margins, velocity claims) but only ~2 quarters; critics' "AI-washing" case has real numbers behind it (headcount 3,835→12,430, 2019–2022).
4. **Square's upmarket/international expansion continues to outpace competitive pressure from Toast, Clover, Stripe.** (medium) — 45% mid-market GPV mix and +26% international GPV are strong, but vertical specialists are entrenched and well-funded.
5. **Regulatory costs are now bounded (~$300M sunk) with compliance obligations manageable, not structural.** (medium) — Settlements resolved without admission; but 24/7 support mandates and BSA/AML scrutiny are permanent cost layers on Cash App.
6. **Bitcoin initiatives remain a small, optional part of enterprise value; BTC treasury (~$692M) is immaterial to a ~$48B market cap.** (high) — Treasury is ~1.4% of market cap; bitcoin revenue is high-volume, near-zero-margin. Dorsey's ideological commitment is the main risk of this assumption breaking (e.g., a large debt-funded BTC purchase).
7. **Management's 2028 targets (GP $15.8B, EPS $5.50, Rule of 40 sustained) are achievable but back-half loaded.** (low-medium) — Requires ~mid-teens GP growth compounding; 2026's +21% helps, but Square's 2025 deceleration shows how quickly the flywheel can wobble.

## (d) Preliminary Decisions (with rationale)

- **D-001: Treat Cash App Borrow credit performance as the #1 leading indicator for the thesis.** Rationale: it is simultaneously the largest growth contributor and the largest unquantified risk; every other segment's trajectory is better evidenced.
- **D-002: Do not assign material enterprise value to bitcoin initiatives in Phase 2 modeling; treat as optionality.** Rationale: near-zero-margin revenue, immaterial treasury, but real strategic option value if merchant bitcoin payments scale.
- **D-003: Frame the investment question as "execution on lending + operating leverage" rather than "fintech growth."** Rationale: the 2025–2026 arc shows the story is no longer about user acquisition; it's about monetization depth and cost discipline.
- **D-004: Require a downside case with a 2027–2028 credit-cycle stress before any buy thesis.** Rationale: assumption (2) is low-confidence and thesis-critical; no recommendation is responsible without it.
- **D-005: TIDAL excluded from further analysis.** Rationale: no material financial contribution found in any source; immaterial to a 3–5 year investment case.

## (e) Open Questions

1. What does Cash App Borrow's loss rate look like at 2–3x current scale, and in a rising-unemployment scenario?
2. Is the current ~$76–79 price already discounting the 2028 targets ($15.8B GP, $5.50 EPS)? (valuation — Phase 2)
3. Do AI-driven productivity gains persist, or do quality incidents/velocity decay appear 12–18 months post-layoffs?
4. Can Square hold mid-market share gains against Toast (restaurants), Clover (scale), and Adyen/Stripe (enterprise)?
5. Will Afterpay remain a standalone brand advantage or get commoditized into checkout stacks?
6. Does Dorsey's bitcoin ideology risk a large balance-sheet bet that changes the risk profile?
7. What is the steady-state compliance cost of the CFPB/state settlement obligations?
8. Who replaces key-man risk around Dorsey/Ahuja execution?

## (f) Unfinished Business (explicitly out of scope for Agent A)

- Full valuation model (DCF / multiples vs. 2028 targets) — **Phase 2**
- Final buy/hold/sell recommendation — **Phase 2, human decision per protocol**
- Credit-cycle stress test on the lending book — **Phase 2**
- TIDAL: confirmed immaterial, no further work needed

## 4. The three handoff representations (verbatim)

### Handoff A — WORLD state

# WORLD State Bundle — EXP-001
`format_version: 0.1` | `project_id: proj-block-001` | `generated_at: 2026-09-17` | `for_actor: incoming agent (Phase 2)` | `generated_from: Agent A Phase 1 research`

## 1. Project context
- **id:** proj-block-001
- **name:** Block, Inc. (SQ / ticker now XYZ) investment research
- **goal:** Produce a preliminary investment memo with a buy/hold/sell recommendation for a 3–5 year horizon.
- **scope:** Business segments, financial health, competitive position, risks/catalysts (Phase 1, complete). Valuation modeling, credit-cycle stress test, final recommendation (Phase 2, open).
- **constraints:** Public sources only. Final recommendation is a human decision per protocol.
- **definition_of_done:** Memo containing valuation vs 2028 targets, a downside credit-stress case, and a human-signed buy/hold/sell.
- **status:** active — Phase 1 complete, Phase 2 not started.

## 2. Tasks
| id | title | status | assignee | notes |
|---|---|---|---|---|
| task-001 | Phase 1: business/financial/competitive research | done | agent-a-exp001 | Report recorded as ART-001 |
| task-002 | Phase 2a: valuation modeling vs 2028 targets | proposed | unassigned | Needs Q-2 |
| task-003 | Phase 2b: credit-cycle stress test on lending book | proposed | unassigned | Required by D-004 before any buy thesis |
| task-004 | Phase 2c: final memo + human decision | proposed | human | Human decides per protocol |

## 3. Decisions (status: accepted)
- **D-001:** Treat Cash App Borrow credit performance as the #1 leading indicator for the thesis. Rationale: it is simultaneously the largest growth contributor and the largest unquantified risk; every other segment's trajectory is better evidenced. Evidence: E-04, E-05, E-06.
- **D-002:** Assign no material enterprise value to bitcoin initiatives in Phase 2 modeling; treat as optionality. Rationale: near-zero-margin revenue; ~$692M treasury is ~1.4% of a ~$48B market cap. Evidence: E-09, E-10.
- **D-003:** Frame the investment question as "execution on lending + operating leverage," not "fintech growth." Rationale: the 2025–2026 arc shows the story is monetization depth and cost discipline, not user acquisition. Evidence: E-01, E-02, E-08.
- **D-004:** Require a downside 2027–2028 credit-cycle stress case before any buy thesis. Rationale: ASM-2 is low-confidence and thesis-critical; no recommendation is responsible without it. Evidence: E-05.
- **D-005:** Exclude TIDAL from further analysis. Rationale: no material financial contribution found in any source.

## 4. Assumptions (status: active)
- **ASM-1** (medium): Cash App monetization-deepening compounds for 3–5 years without user growth re-accelerating. Basis: inflows/active +9%, primary banking actives +17%, Borrow originations +59% YoY — but monthly actives only +3%.
- **ASM-2** (low): Borrow loss rates stay in the 2.7–3.2% band in a normal credit environment. **REVISED** — originally "consumer lending is a clean growth lever" (high confidence); corrected after the Q3 2025 loss spike (+89% to $363.5M). Untested in a recession.
- **ASM-3** (medium-low): The 40% headcount cut was mostly pandemic-bloat removal and AI tooling sustains product velocity. Confidence dented from higher initial level after the "AI-washing" critique (headcount 3,835 → 12,430 from 2019–2022). Only ~2 quarters of evidence.
- **ASM-4** (medium): Square's upmarket/international expansion outpaces competitive pressure from Toast, Clover, Stripe. Basis: 45% mid-market GPV mix, +26% international GPV (Q3 2025).
- **ASM-5** (medium): Regulatory costs are bounded (~$300M sunk) with manageable ongoing compliance. Basis: settlements reached without admission; but 24/7 support mandates and BSA/AML scrutiny are permanent cost layers on Cash App.
- **ASM-6** (high): Bitcoin initiatives remain immaterial to enterprise value. Basis: treasury ~1.4% of market cap; bitcoin revenue ~1/3 of total at near-zero margin. Break risk: a Dorsey-led debt-funded BTC purchase.
- **ASM-7** (low-medium): Management's 2028 targets (GP $15.8B, EPS $5.50, Rule of 40 sustained) are achievable but back-half loaded. Basis: requires sustained mid-teens GP growth; Square's 2025 deceleration shows how quickly the flywheel can wobble.

## 5. Evidence
- **E-01:** Q2 2026 results — revenue $6.618B (beat), adj. EPS $1.02, gross profit $3.17B (+25% YoY); Cash App GP +31%, Square GP and GPV +13%. Reuters 2026-08-05.
- **E-02:** FY2026 guidance raised — GP $12.51B (+21%), adj. operating income ~$3.47B, EPS $4.02. Earnings call transcript, Fool 2026-08-12.
- **E-03:** Cash App engagement — monthly actives +3%, inflows/active +9%, primary banking actives +17%, monetization rate 1.53%→1.65%, Borrow originations +59% YoY to $18.9B. Zacks 2026-08-21.
- **E-04:** Borrow scale post-FDIC approval — 15M+ users accessed Borrow; Q1 2026 cohort risk loss rates 2.67–3.16%. American Banker.
- **E-05:** Q3 2025 loss spike — transaction/loan/consumer-receivable losses +89% to $363.5M; revenue $6.11B missed ~$6.3B estimate; stock fell 10–15%. FinancialContent 2025-11-07.
- **E-06:** 2025 context — Square GP growth slowed to 9%, lagging GPV growth (margin compression); S&P 500 inclusion July 2025; Investor Day Nov 2025 three-year outlook. PYMNTS 2025.
- **E-07:** Feb 2026 layoffs — 4,000+ cut (10,000+ → <6,000), "AI-native" framing, stock +20%; Dorsey claims: code velocity per engineer +2.5x, Builderbot reviewing 90% of changes, incidents −70%. CNN; VentureBeat.
- **E-08:** "AI-washing" critique — headcount tripled 2019–2022 (3,835 → 12,430); cost pressure real regardless of AI narrative. Entrepreneur.
- **E-09:** Regulatory settlements — CFPB Jan 2025 ($120M redress + $55M penalty); $80M to states (BSA/AML); $45M to 46 state AGs July 2026 with 24/7 live-support mandate. Bloomberg Law; American Banker.
- **E-10:** Bitcoin — 28,355 BTC (~$2.2B, Q1 2026 proof-of-reserves; ~$692M corporate treasury); Bitkey wallet revamp; Square bitcoin acceptance via NFC/Lightning, zero fees through 2026 (4M+ sellers eligible); bitcoin revenue ~1/3 of total at near-zero margin. The Block; Bitcoin Magazine.
- **E-11:** Square competition — FY2024 GPV $228B across 4M+ sellers; Fiserv Clover ~$300B annualized GPV; Toast $215B+ GPV across ~180k locations; Adyen–Toast US partnership Aug 2026. Coinlaw; PYMNTS; Zacks.
- **E-12:** Afterpay/BNPL — GMV +13% to $10.3B, GP +14% (Q1 2025); Afterpay reaches 58% of subprime BNPL users; pressure from Klarna, Affirm (GAAP profitable), PayPal Pay Later; BNPL commoditizing. FinancialContent; PYMNTS.
- **E-13:** Multi-year targets — GP ~$15.8B by 2028, adj. operating income ~$4.6B, adj. EPS $5.50, Rule of 40 in 2026 sustained through 2028; consensus target ~$95.42 (Moderate Buy, 42 analysts) vs ~$76–79 current. BusinessWire/Morningstar 2025-11-18; MarketBeat.
- Key URLs: reuters.com (Q2 2026 results), fool.com (Q2 2026 transcript), zacks.com (Cash App deep dive), americanbanker.com (Borrow; $45M settlement), news.bloomberglaw.com (CFPB $175M), theblock.co (proof-of-reserves), block.xyz + block-investor-day-2025-financial-outlook.pdf (targets).

## 6. Actions (Agent A, condensed from working record)
- ACT-001: Framed research plan (segments → financials → competition → risks → bitcoin → leadership); noted ticker SQ→XYZ.
- ACT-002: Researched segments + Q2 2026 earnings; formed initial assumption "Borrow is the highest-octane growth engine."
- ACT-003: Researched 2025 context (Q3 stumble, S&P inclusion, Investor Day); questioned whether 2026 rebound is real leverage or cost cuts + easy comps.
- ACT-004: Investigated Feb 2026 layoffs; dented "AI-native efficiency" assumption on bloat data.
- ACT-005: Researched Square competition; concluded ecosystem-breadth moat with mid-market share gains.
- ACT-006: Researched credit + regulatory; **revised lending assumption** (clean lever → highest-upside/highest-risk); logged ~$300M+ regulatory settlements.
- ACT-007: Researched bitcoin strategy; concluded optionality, not P&L driver.
- ACT-008: Researched Afterpay/BNPL + valuation; noted commoditization and consensus targets.
- ACT-009: Synthesized bull/bear cases; deferred valuation and final recommendation to Phase 2.

## 7. State changes (immutable log, key entries)
- CHG-001: ASM-lending created ("consumer lending is a clean growth lever", confidence high) — ACT-002.
- CHG-002: ASM-lending SUPERSEDED → ASM-2 ("highest-upside AND highest-risk engine", confidence low). Reason: E-05 (89% loss spike) contradicts "clean." — ACT-006.
- CHG-003: ASM-ai-efficiency confidence lowered (high → medium-low) on E-08. — ACT-004.
- CHG-004: D-001…D-005 accepted. — ACT-009.
- CHG-005: task-001 → done; task-002/003/004 → proposed. — ACT-009.

## 8. Open questions
- **Q-1:** Borrow loss rates at 2–3x scale, or in a rising-unemployment scenario? (blocks task-003; relates ASM-2)
- **Q-2:** Is ~$76–79 already discounting the 2028 targets ($15.8B GP, $5.50 EPS)? (valuation; blocks task-002)
- **Q-3:** Do AI productivity gains persist 12–18 months post-layoffs, or do quality incidents appear? (relates ASM-3)
- **Q-4:** Can Square hold mid-market share gains vs Toast (restaurants), Clover (scale), Adyen/Stripe (enterprise)? (relates ASM-4)
- **Q-5:** Does Afterpay remain a standalone brand advantage or get commoditized into checkout stacks?
- **Q-6:** Does Dorsey's bitcoin ideology risk a large balance-sheet bet that changes the risk profile? (break risk for ASM-6)
- **Q-7:** What is the steady-state compliance cost of the CFPB/state settlement obligations?
- **Q-8:** Key-man risk around Dorsey/Ahuja execution?

## 9. Artifacts
- **ART-001:** Agent A Phase 1 final report (findings, evidence with URLs, assumptions, decisions, open questions; recorded in project file).

## 10. Handoff bundle for the incoming agent
- **Context snapshot:** Block (SQ/XYZ), 3–5y investment research. Phase 1 complete. Phase 2 = valuation modeling, credit-cycle stress test, final memo. Human makes the final call.
- **Do next:** task-002 (valuation vs 2028 targets), task-003 (credit stress; required by D-004), then task-004.
- **Must know:** D-001 (lending is the #1 leading indicator), D-002 (bitcoin = optionality, not value), D-003 (frame: execution on lending + operating leverage), D-004 (no buy thesis without a stress case), D-005 (TIDAL excluded).
- **Watch:** ASM-2 (low confidence, thesis-critical), ASM-3 (only ~2 quarters of evidence), ASM-7 (targets back-half loaded).
- **Start from:** Q-1 and Q-2 — they block everything downstream.


### Handoff B — Conventional summary

# Handoff: Block, Inc. (SQ / ticker now XYZ) investment research — Phase 1 summary

An analyst has completed Phase 1 research on Block, Inc. for a 3–5 year buy/hold/sell decision. Valuation modeling and the final recommendation are explicitly deferred to Phase 2 (you). What follows is a careful summary of everything Phase 1 established.

## The story so far

2025 was rough for Block: a Q3 revenue miss ($6.11B vs ~$6.3B expected, only +2% YoY) sent the stock down 10–15%, Square's gross-profit growth slowed to 9% and lagged GPV growth for the first time since early 2023 (margin compression), and losses on transactions, loans, and consumer receivables spiked 89% to $363.5M on higher short-term consumer borrowing. Partial offsets: S&P 500 inclusion in July 2025 and an Investor Day in November 2025 that laid out ambitious three-year targets.

2026 looks like a genuine operating turnaround, not just cost cuts. Q2 2026 (reported Aug 5, 2026) beat expectations: revenue $6.618B vs $6.485B expected, adjusted EPS $1.02 vs $0.87, gross profit $3.17B up 25% YoY. Cash App gross profit grew 31%; Square gross profit and GPV both grew 13%, with US GPV at its strongest growth since Q2 2023. Management raised full-year 2026 guidance: gross profit $12.51B (+21%), adjusted operating income ~$3.47B, EPS $4.02. Sources: Reuters 2026-08-05, TheStreet, Fool earnings transcript 2026-08-12.

## Cash App: from user growth to monetization depth

Monthly transacting actives grew only 3% (June 2026) — but inflows per active rose 9%, primary banking actives rose 17%, the monetization rate ticked from 1.53% to 1.65%, and Cash App Borrow originations jumped 59% YoY to $18.9B. Growth is now engagement-led. After FDIC approval, Borrow scaled to 15M+ users with Q1 2026 cohort risk loss rates of 2.67–3.16%, which looks disciplined for short-term consumer credit. Source: Zacks 2026-08-21, American Banker.

The analyst's important revision: they started out viewing consumer lending as a clean growth lever, then corrected themselves after the Q3 2025 loss spike. The corrected view: **lending is simultaneously the highest-upside engine and the highest-risk one** — credit quality in a downturn is the single variable that will make or break the 3–5 year thesis, and it is untested at this scale in a recession.

## Square: moving upmarket

Mid-market sellers (over $500k/year GPV) are now 45% of GPV, up from 41% two years ago; international GPV grew 26% vs 9% in the US (Q3 2025); 200+ ISO partners; a dedicated restaurant push. Scale context: Square did $228B GPV in FY2024 across 4M+ sellers, vs Fiserv's Clover at ~$300B annualized and Toast at $215B+ across ~180k restaurant locations. Adyen partnered with Toast in the US in August 2026. The analyst's read: Square is no longer a tiny-merchant-only story but a mid-market share-gainer; its moat is ecosystem breadth, not dominance — and it faces entrenched vertical specialists. Sources: PYMNTS 2025, Zacks 2026-08-27, Coinlaw.

## The 40% headcount cut

In February 2026 Block cut over 4,000 people (10,000+ → under 6,000), framed as an "AI-native" restructuring; the stock rose 20% on the news and Q2 2026 posted a record 27% adjusted operating income margin. Dorsey claims code velocity per engineer is up 2.5x, an internal tool (Builderbot) reviews 90% of code changes, and incident rates are down 70%. Critics call it "AI-washing" of pandemic-era bloat — headcount tripled from 3,835 in 2019 to 12,430 in 2022 while the stock fell ~40% — so cost pressure was real regardless of the AI narrative. The analyst dented their initial confidence here: the cuts were probably necessary de-bloating with AI as partial cover, and the efficiency claims have only ~2 quarters of evidence. What would restore confidence: sustained product velocity and margin expansion through 2027 without quality incidents. Sources: CNN, VentureBeat, Entrepreneur, eWeek (Feb–Mar 2026).

## Regulatory overhang: material but bounded

Roughly $300M+ in settlements: CFPB consent order January 2025 ($120M redress + $55M penalty) over Cash App fraud and customer-service failures; $80M to states over BSA/AML; $45M to 46 state attorneys general in July 2026, which requires 24/7 live customer support. Ongoing compliance obligations raise the permanent cost of operating Cash App. Sources: Bloomberg Law, American Banker, ConsumerAffairs.

## Bitcoin: ideology and optionality, not the P&L

Q1 2026 proof-of-reserves: 28,355 BTC (~$2.2B), of which ~$692M is corporate treasury — about 1.4% of a ~$48B market cap. New initiatives: a revamped Bitkey hardware wallet, Square merchants accepting bitcoin via NFC/Lightning with zero fees through 2026 (4M+ sellers eligible — a genuinely large distribution move), 5% "Bitcoin Back" rewards, Proto mining hardware shipping, on-chain proof-of-reserves. But bitcoin ecosystem revenue is roughly a third of total revenue at near-zero margin (Q2 2025: $2.17B revenue on $2.06B costs) — it moves headlines, not gross profit. The analyst's judgment: do not assign material enterprise value to bitcoin in Phase 2 modeling; treat it as optionality. The main risk to that view is Dorsey's ideological commitment leading to a large debt-funded BTC purchase. Sources: The Block 2026-04-28, Bitcoin Magazine, Motley Fool.

## Afterpay and BNPL

Afterpay is healthy but not a growth engine: GMV +13% to $10.3B, gross profit +14% (Q1 2025). It reaches 58% of subprime BNPL users with the highest Pay-in-4 ceiling ($5,000) and monthly plans to $20k — but Klarna (100M+ users, IPO'd), Affirm (now GAAP profitable, with Amazon/Apple/Shopify partnerships), and PayPal Pay Later are pressing hard, and BNPL is consolidating into checkout/wallet stacks with shrinking standalone differentiation. Sources: FinancialContent 2025-07-31, PYMNTS BNPL study, Fool 2026-06-02.

## Targets and valuation setup

Investor Day 2025 targets: mid-teens gross-profit growth to ~$15.8B by 2028, adjusted operating income ~30%/year to $4.6B, adjusted EPS growing low-30s% to $5.50, Rule of 40 in 2026 sustained through 2028. Consensus analyst target ~$95.42 (Moderate Buy, 42 analysts) vs a ~$76–79 current price. Whether the price already discounts the 2028 targets is the central valuation question for Phase 2. Note: insider selling by Grassadonia (10b5-1, scheduled). Sources: Morningstar/BusinessWire 2025-11-18, MarketBeat.

## The analyst's preliminary judgments

1. Treat Cash App Borrow credit performance as the #1 leading indicator — biggest growth contributor and biggest unquantified risk.
2. Frame the investment question as "execution on lending + operating leverage," not "fintech growth."
3. Require a downside 2027–2028 credit-cycle stress case before any buy thesis — the lending assumption is low-confidence and thesis-critical.
4. TIDAL was investigated and excluded: no material financial contribution; no further work needed.

## Key assumptions and confidence

- Cash App monetization-deepening compounds 3–5 years without user growth re-accelerating (medium confidence; actives only +3% is a thin base).
- Borrow loss rates stay in the 2.7–3.2% band in a normal credit environment (low confidence; untested in recession).
- The headcount cut was mostly bloat removal; AI sustains velocity (medium-low; ~2 quarters of evidence).
- Square upmarket/international expansion outpaces competitive pressure (medium).
- Regulatory costs bounded at ~$300M sunk with manageable ongoing compliance (medium).
- Bitcoin immaterial to enterprise value (high confidence).
- 2028 targets achievable but back-half loaded (low-medium).

## Open questions for Phase 2

1. Borrow loss rates at 2–3x scale, or in a rising-unemployment scenario?
2. Is ~$76–79 already discounting the 2028 targets? (the valuation question)
3. Do AI productivity gains persist 12–18 months post-layoffs?
4. Can Square hold mid-market share vs Toast, Clover, Adyen/Stripe?
5. Does Afterpay stay differentiated or get commoditized?
6. Could Dorsey make a large balance-sheet bitcoin bet?
7. What is the steady-state compliance cost of the settlements?
8. Key-man risk around Dorsey/Ahuja?

## What's unfinished

Valuation modeling (DCF/multiples vs 2028 targets), the credit-cycle stress test, and the final buy/hold/sell recommendation — the recommendation is a human decision. That's your job now.


### Handoff C — Raw transcript (Agent A journal, unedited)

# Agent A working journal — Block, Inc. (SQ) Phase 1 research, 2026-09-17 (unedited)

[Entry 1 — framing] Starting Phase 1. Task: research Block, Inc. (NYSE: SQ — note: the company rebranded its ticker to XYZ at some point; current listings show "XYZ" on NYSE, Finnhub shows both. I'll note this in the report but it doesn't change the substance). Horizon 3–5 years, no buy/hold/sell from me. Plan: segments → financials → competition → risks → bitcoin → leadership. Beginning with business segments and latest earnings.

[Entry 2 — segments + Q2 2026] Searched "Block Inc SQ business segments Square Cash App Afterpay revenue breakdown 2025" and "Block Inc second quarter 2026 earnings results gross profit Cash App Square". Big early finding: Q2 2026 (Aug 5, 2026) was a genuine beat — revenue $6.618B vs $6.485B expected, adj EPS $1.02 vs $0.87, gross profit $3.17B +25% YoY. Cash App gross profit +31%, Square +13% with US GPV accelerating to its strongest since Q2 2023. Management raised FY2026 guidance: gross profit $12.51B (+21%), adj operating income $3.47B-ish, EPS $4.02. Zacks notes Cash App Borrow originations +59% YoY to $18.9B, monetization rate 1.53%→1.65%, but also loan-related losses rising and Bitcoin ecosystem gross profit declining. Early read: this is a Cash-App-led growth story with a lending kicker. My working assumption forming: "Cash App Borrow is the highest-octane growth engine."

[Entry 3 — 2025 context] Found the contrast: 2025 was rough. Q3 2025: revenue $6.11B missed ($6.31–6.34B est.), only +2% YoY, stock plunged 10–15%, YTD losses ~24%. Square gross profit growth slowed to 9%, first time lagging GPV growth since Q1 2023 (margin compression). Then S&P 500 inclusion July 2025, Investor Day Nov 2025 gave 3-year outlook (mid-teens GP growth to $15.8B by 2028, Rule of 40 in 2026). So the narrative arc: 2025 stumble → Feb 2026 layoffs → 2026 acceleration. Suspicion forming: is the 2026 rebound real operating leverage or just cost cuts + easy comps?

[Entry 4 — the layoff test] Searched the 40% layoffs. Feb 2026: >4,000 people cut, 10,000+ → <6,000, framed as "AI-native" restructuring; Dorsey claims code velocity per engineer up 2.5x, Builderbot reviewing 90% of code changes, incident rates down 70%. Stock +20% on the news. BUT: Entrepreneur piece cites critics calling it "AI-washing" — headcount tripled 2019–2022 (3,835→12,430), stock fell 40% since early 2025, so cost pressure was real regardless of the AI narrative. Goldman: AI eliminating only 5–10k jobs/month across all US sectors. This genuinely dented my early instinct to take the "AI-native efficiency" story at face value. Revised view: the cuts were probably necessary de-bloating with AI as partial cover; the efficiency claims are plausible but only have ~2 quarters of evidence. What would change my mind back toward Dorsey's version: sustained product velocity + margin expansion through 2027 without quality incidents.

[Entry 5 — competition] Searched Square competition. Findings: Square did $228B GPV in FY2024 across 4M+ sellers; Fiserv's Clover ~$300B annualized GPV (2025); Toast $215B+ GPV across ~180k restaurant locations in 12mo ended June 2026, and Toast calls Block/Square its biggest competitor. Square's upmarket push is real: mid-market sellers (>$500k/yr) now 45% of GPV, international GPV +26% vs US +9% in Q3 2025, 200+ ISO partners, restaurant push (Zacks Aug 2026). Adyen partnered with Toast in the US in Aug 2026. Conclusion: Square is no longer the tiny-merchant-only story; it's mid-market share-gainer, but faces vertical specialists (Toast) and scale giants (Clover, Stripe, PayPal). Moat here is ecosystem breadth, not dominance.

[Entry 6 — risks: credit + regulatory] This is where my early "lending is a clean growth lever" assumption took a real hit. Q3 2025: losses on transactions/loans/consumer receivables jumped 89% to $363.5M on higher short-term consumer borrowing. Then regulatory: CFPB consent order Jan 2025 ($120M redress + $55M penalty, total up to $175M) over Cash App fraud/customer-service failures; $80M to states over BSA/AML; July 2026: $45M settlement with 46 state AGs requiring 24/7 live customer support. That's ~$300M+ in regulatory costs and ongoing compliance obligations. Contradictory evidence on the lending side though: FDIC approval let Cash App Borrow scale (15M+ users accessed Borrow; Q1 2026 risk loss rates 2.67–3.16% by cohort, which is disciplined for subprime-adjacent short-term credit). Corrected assumption: consumer lending is simultaneously the highest-upside engine AND the highest-risk one — credit quality in a downturn is the single variable that will make or break the 3–5 year thesis, and it is untested at this scale in a recession.

[Entry 7 — bitcoin] Searched Block bitcoin strategy. Q1 2026 proof-of-reserves: 28,355 BTC (~$2.2B), of which 19,357 customer-held, 8,997 BTC (~$692M) corporate treasury. New: Bitkey hardware wallet revamp, Square merchants accepting bitcoin via NFC/Lightning with zero fees through 2026 (4M+ sellers eligible — a genuinely large distribution move), 5% "Bitcoin Back" rewards, Proto mining hardware shipping (contributing to Bitcoin ecosystem GP growth), proof-of-reserves with on-chain signatures. But: bitcoin ecosystem revenue is ~1/3 of total revenue with near-zero margin (Q2 2025: $2.17B revenue on $2.06B costs), so it inflates/deflates headline revenue without moving gross profit. Decision-relevant nuance: bitcoin is optionality + ideology (Dorsey), not the P&L driver. It adds volatility to the story without adding much to the economics.

[Entry 8 — Afterpay/BNPL + valuation] PYMNTS data: Afterpay reaches 58% of subprime BNPL users, highest Pay-in-4 ceiling ($5,000), monthly plans to $20k; competitors: Klarna (100M+ users, IPO'd), Affirm (GAAP profitable, Amazon/Apple/Shopify partnerships), PayPal Pay Later. BNPL is consolidating into checkout/wallet stacks; standalone differentiation is shrinking. Afterpay Q1 2025: GMV +13% to $10.3B, GP +14% — healthy but not a growth engine. Valuation: consensus ~$95.42 target (MarketBeat, Moderate Buy, 42 analysts), stock ~$76–79, fwd P/E ~24.8x vs industry 27.9x. Multi-year guidance: Rule of 40 in 2026, sustained through 2028. Insider selling (Grassadonia, 10b5-1) noted but scheduled.

[Entry 9 — synthesis check] Stepping back. Bull case: Cash App monetization deepening (not user growth — actives only +3%, but inflows/active +9%, primary banking actives +17%), Square upmarket acceleration, AI-driven operating leverage, BNPL embedded, bitcoin optionality, raised guidance. Bear case: lending credit risk untested in downturn, regulatory overhang (CFPB + states, ongoing compliance costs), BNPL commoditization, Square competitive pressure from vertical specialists, execution risk of the 40% headcount cut, Dorsey key-man/strategy concentration (bitcoin bets are his ideology). The single most important unresolved item: valuation work — is ~$76–79 pricing in the 2028 targets ($15.8B GP, $5.50 EPS) or not? Explicitly out of scope for me; flagging for Phase 2. Also unresolved: unit economics of Borrow at scale through a credit cycle; whether AI productivity gains persist.

## 5. Agent B continuation task (identical brief, all conditions)

> You are Agent B, taking over an investment research project mid-stream. Read ONLY the handoff file at /tmp/exp001/handoff_N.md — read it fully before doing anything else.
>
> SCOPE RULE (strict): the handoff file is your SOLE source of project context. Your conversation may contain other text from earlier project discussion — treat ALL of it as out of scope: do not use, quote, reference, or rely on it in any way. Do NOT browse the web. Use only general reasoning plus the handoff. If the handoff lacks something you need, say so explicitly instead of filling the gap from elsewhere. Do not invent sources, numbers, or quotes.
>
> OBJECTIVE: continue toward a preliminary investment memo on Block, Inc. (SQ/XYZ), 3–5 year horizon. The final buy/hold/sell is a human decision — not yours.
>
> Produce exactly these four sections:
> 1. INHERITED STATE — the key facts, decisions (+ their rationale), assumptions (+ confidence levels), open questions, and key evidence, as you understand them from the handoff.
> 2. ASSUMPTION CHECK — for each assumption in the handoff, say whether the handoff's evidence supports, weakens, or leaves it untested; note any assumption the prior analyst revised and describe what changed.
> 3. OPEN QUESTIONS — answer each open question as far as the handoff allows; mark the rest as needing new research.
> 4. CONTINUATION BRIEF — current thesis, what changed vs the prior work, what is still unknown, and concrete next steps toward valuation and a recommendation.
>
> Be precise and complete. Ground every claim in the handoff.

## 6. Agent B outputs (anonymized as X, Y, Z for the blind evaluation)

Condition mapping is disclosed *after* the evaluation report (§7) to preserve the blind. Outputs are verbatim.

### Output X

# Agent B — Continuation Brief: Block, Inc. (SQ/XYZ), Phase 2

Read the handoff file at `/tmp/exp001/handoff_2.md` in full before writing anything below. It is my sole source. I did not browse the web and invented nothing. Where the handoff is silent, I say so.

---

## 1. INHERITED STATE

**Context.** Phase 1 covered Block, Inc. (ticker changed SQ → XYZ) with a 3–5 year investment horizon. Phase 1 established findings, evidence, assumptions, decisions, and open questions. Explicitly deferred to Phase 2 (me): valuation modeling (DCF/multiples vs. 2028 targets), the credit-cycle stress test, and continuation toward a preliminary investment memo. The final buy/hold/sell is a human decision, not mine.

**Key facts inherited:**

- **2025 was rough.** Q3 2025: revenue miss ($6.11B vs ~$6.3B expected, +2% YoY); stock fell 10–15%. Square gross-profit growth slowed to 9% and lagged GPV growth for the first time since early 2023 (margin compression). Losses on transactions, loans, and consumer receivables spiked 89% to $363.5M on higher short-term consumer borrowing. Partial offsets: S&P 500 inclusion (July 2025); Investor Day (November 2025) laid out ambitious three-year targets.
- **2026 looks like a genuine operating turnaround, not just cost cuts.** Q2 2026 (reported Aug 5, 2026) beat expectations: revenue $6.618B vs $6.485B expected; adjusted EPS $1.02 vs $0.87; gross profit $3.17B, +25% YoY. Cash App gross profit +31%; Square gross profit and GPV both +13%, with US GPV at its strongest growth since Q2 2023. Full-year 2026 guidance was raised: gross profit $12.51B (+21%), adjusted operating income ~$3.47B, EPS $4.02.
- **Cash App has shifted from user growth to monetization depth.** Monthly transacting actives grew only 3% (June 2026), but inflows per active rose 9%, primary banking actives rose 17%, the monetization rate ticked from 1.53% to 1.65%, and Cash App Borrow originations jumped 59% YoY to $18.9B. After FDIC approval, Borrow scaled to 15M+ users with Q1 2026 cohort risk loss rates of 2.67–3.16%.
- **Square is moving upmarket.** Mid-market sellers (>$500k/year GPV) are now 45% of GPV, up from 41% two years ago; international GPV grew 26% vs 9% in the US (Q3 2025); 200+ ISO partners; a dedicated restaurant push. Scale context: $228B GPV in FY2024 across 4M+ sellers, vs Fiserv's Clover at ~$300B annualized and Toast at $215B+ across ~180k restaurant locations. Adyen partnered with Toast in the US in August 2026.
- **The 40% headcount cut (February 2026).** Over 4,000 people cut (10,000+ → under 6,000), framed as "AI-native" restructuring; the stock rose 20% on the news; Q2 2026 posted a record 27% adjusted operating income margin. Dorsey claims: code velocity per engineer up 2.5x, internal tool Builderbot reviews 90% of code changes, incident rates down 70%. Critics call it "AI-washing" of pandemic-era bloat — headcount tripled from 3,835 in 2019 to 12,430 in 2022 while the stock fell ~40%.
- **Regulatory overhang: material but bounded (~$300M+ settlements).** CFPB consent order January 2025 ($120M redress + $55M penalty) over Cash App fraud and customer-service failures; $80M to states over BSA/AML; $45M to 46 state attorneys general in July 2026, which requires 24/7 live customer support. Ongoing compliance obligations raise the permanent cost of operating Cash App.
- **Bitcoin: ideology and optionality, not the P&L.** Q1 2026 proof-of-reserves: 28,355 BTC (~$2.2B), of which ~$692M is corporate treasury — about 1.4% of a ~$48B market cap. New initiatives: revamped Bitkey hardware wallet, Square merchants accepting bitcoin via NFC/Lightning with zero fees through 2026 (4M+ sellers eligible), 5% "Bitcoin Back" rewards, Proto mining hardware shipping, on-chain proof-of-reserves. But bitcoin ecosystem revenue is roughly a third of total revenue at near-zero margin (Q2 2025: $2.17B revenue on $2.06B costs).
- **Afterpay: healthy but not a growth engine.** GMV +13% to $10.3B, gross profit +14% (Q1 2025). Reaches 58% of subprime BNPL users with the highest Pay-in-4 ceiling ($5,000) and monthly plans to $20k. Competition: Klarna (100M+ users, IPO'd), Affirm (now GAAP profitable, with Amazon/Apple/Shopify partnerships), PayPal Pay Later. BNPL is consolidating into checkout/wallet stacks with shrinking standalone differentiation.
- **Targets and valuation setup.** Investor Day 2025 targets: mid-teens gross-profit growth to ~$15.8B by 2028; adjusted operating income ~30%/year to $4.6B; adjusted EPS growing low-30s% to $5.50; Rule of 40 in 2026 sustained through 2028. Consensus analyst target ~$95.42 (Moderate Buy, 42 analysts) vs ~$76–79 current price. Insider selling by Grassadonia (10b5-1, scheduled).
- **TIDAL was investigated and excluded:** no material financial contribution; no further work needed.

**Decisions (with rationale), inherited from the analyst's preliminary judgments:**

1. **Treat Cash App Borrow credit performance as the #1 leading indicator.** Rationale: lending is simultaneously the biggest growth contributor (originations +59% YoY to $18.9B, 15M+ users) and the biggest unquantified risk (the Q3 2025 loss spike of +89% to $363.5M showed credit is the swing variable).
2. **Frame the investment question as "execution on lending + operating leverage," not "fintech growth."** Rationale: the 2026 story is operating performance (gross profit +25% in Q2) against thin user growth (actives +3%).
3. **Require a downside 2027–2028 credit-cycle stress case before any buy thesis.** Rationale: the lending assumption is low-confidence and thesis-critical.
4. **Exclude TIDAL from further work.** Rationale: no material financial contribution found.

**Assumptions (with confidence levels):**

1. Cash App monetization-deepening compounds 3–5 years without user growth re-accelerating — **medium** (actives only +3% is a thin base).
2. Borrow loss rates stay in the 2.7–3.2% band in a normal credit environment — **low** (untested in recession).
3. The headcount cut was mostly bloat removal; AI sustains velocity — **medium-low** (~2 quarters of evidence).
4. Square upmarket/international expansion outpaces competitive pressure — **medium**.
5. Regulatory costs bounded at ~$300M sunk with manageable ongoing compliance — **medium**.
6. Bitcoin immaterial to enterprise value — **high**.
7. 2028 targets achievable but back-half loaded — **low-medium**.

**Open questions (as listed):** (1) Borrow loss rates at 2–3x scale, or in a rising-unemployment scenario? (2) Is ~$76–79 already discounting the 2028 targets? (3) Do AI productivity gains persist 12–18 months post-layoffs? (4) Can Square hold mid-market share vs Toast, Clover, Adyen/Stripe? (5) Does Afterpay stay differentiated or get commoditized? (6) Could Dorsey make a large balance-sheet bitcoin bet? (7) What is the steady-state compliance cost of the settlements? (8) Key-man risk around Dorsey/Ahuja?

**Key evidence (sources named in the handoff):** Reuters 2026-08-05, TheStreet, Fool earnings transcript 2026-08-12 (Q2 2026 results); Zacks 2026-08-21, American Banker (Cash App/Borrow); PYMNTS 2025, Zacks 2026-08-27, Coinlaw (Square); CNN, VentureBeat, Entrepreneur, eWeek, Feb–Mar 2026 (headcount cut); Bloomberg Law, American Banker, ConsumerAffairs (regulatory); The Block 2026-04-28, Bitcoin Magazine, Motley Fool (bitcoin); FinancialContent 2025-07-31, PYMNTS BNPL study, Fool 2026-06-02 (Afterpay); Morningstar/BusinessWire 2025-11-18, MarketBeat (targets/consensus).

---

## 2. ASSUMPTION CHECK

For each inherited assumption, what the handoff's own evidence says:

1. **Cash App monetization-deepening compounds 3–5 years without user growth re-accelerating (medium).** *Partially supported; duration untested.* The direction is supported: monetization rate 1.53% → 1.65%, inflows per active +9%, primary banking actives +17%. But the handoff itself flags the thin base (actives +3%) and assigns only medium confidence — nothing in the handoff tests whether this compounds over 3–5 years. Evidence supports the trend; the compounding claim is untested.
2. **Borrow loss rates stay in 2.7–3.2% band in a normal credit environment (low).** *Supported at current scale in current conditions; weakened as a stability claim; recession scenario untested.* Q1 2026 cohort loss rates of 2.67–3.16% across 15M+ users support discipline right now. But the Q3 2025 loss spike (+89% to $363.5M) is in-handoff evidence that loss rates can move sharply, which weakens the "stays in band" claim. The recession case is explicitly untested.
3. **Headcount cut was mostly bloat removal; AI sustains velocity (medium-low).** *Split verdict.* The "bloat removal" half is supported: headcount tripled (3,835 in 2019 → 12,430 in 2022) while the stock fell ~40%, and Q2 2026's record 27% adjusted operating income margin is consistent with de-bloating. The "AI sustains velocity" half rests on management claims (2.5x code velocity, Builderbot reviewing 90% of changes, incidents −70%) with only ~2 quarters of evidence — untested. The handoff's own restore-confidence criteria (sustained velocity and margin expansion through 2027 without quality incidents) are not yet met.
4. **Square upmarket/international expansion outpaces competitive pressure (medium).** *Supported on trajectory; challenged by competitive facts in the same handoff.* Supporting: mid-market sellers 41% → 45% of GPV, international GPV +26%, 200+ ISO partners. Weakening: Clover at ~$300B annualized GPV exceeds Square's $228B FY2024; Toast's vertical restaurant strength; the Adyen–Toast partnership (August 2026). The handoff's own read ("moat is ecosystem breadth, not dominance… faces entrenched vertical specialists") is more cautious than the assumption's phrasing.
5. **Regulatory costs bounded at ~$300M sunk with manageable ongoing compliance (medium).** *Sunk portion supported; "manageable ongoing" untested and mildly weakened.* The $300M+ in settlements ($120M+$55M CFPB, $80M states BSA/AML, $45M state AGs) are documented facts. But the handoff also states that ongoing obligations "raise the permanent cost of operating Cash App," and the July 2026 settlement mandates 24/7 live customer support — a structural cost increase that sits uneasily with "bounded."
6. **Bitcoin immaterial to enterprise value (high).** *Supported.* Bitcoin ecosystem revenue is ~1/3 of total revenue at near-zero margin (Q2 2025: $2.17B revenue on $2.06B costs); the $692M corporate treasury is ~1.4% of a ~$48B market cap. The stated risk to this view is a Dorsey-led large debt-funded BTC purchase — a governance risk, not a modeling input at current scale.
7. **2028 targets achievable but back-half loaded (low-medium).** *Supported on trajectory; back-half loading untested.* Q2 2026 beat plus raised FY2026 guidance (gross profit $12.51B, +21%) puts the company on a path where reaching ~$15.8B by 2028 requires roughly low-teens annual growth from here — arithmetically consistent with "mid-teens" targets. Weakened by the Q3 2025 margin compression episode and loss spike; the "back-half loaded" characterization has no in-handoff evidence yet.

**The revised assumption.** The prior analyst initially viewed consumer lending as a clean growth lever, then revised after the Q3 2025 loss spike (+89% to $363.5M). The corrected view: **lending is simultaneously the highest-upside engine and the highest-risk one** — credit quality in a downturn is the single variable that will make or break the 3–5 year thesis, and it is untested at this scale in a recession. This revision is the load-bearing correction of Phase 1 and is directly reflected in decisions #1 and #3 above. A second, smaller confidence revision: the analyst dented their initial confidence in the "AI-native" layoff narrative — the cuts were probably necessary de-bloating with AI as partial cover.

---

## 3. OPEN QUESTIONS

Answered only as far as the handoff permits; the rest are marked as needing new research:

1. **Borrow loss rates at 2–3x scale, or in a rising-unemployment scenario?** *Needs new research.* The handoff gives current-state data (2.67–3.16% cohort loss rates, 15M+ users, $18.9B originations) but explicitly states this is untested at scale and in a recession. This is the designated Phase 2 stress test — no answer exists in the handoff.
2. **Is ~$76–79 already discounting the 2028 targets?** *Needs new research — this is the central Phase 2 valuation question.* The handoff frames it but does not model it. Partial context from the handoff: consensus target ~$95.42 (Moderate Buy, 42 analysts) vs ~$76–79 current price implies ~20–25% upside to consensus, but consensus is not a valuation model.
3. **Do AI productivity gains persist 12–18 months post-layoffs?** *Needs new research (time-gated).* Only ~2 quarters of evidence exist per the handoff. The handoff specifies what would resolve it: sustained product velocity and margin expansion through 2027 without quality incidents. I cannot resolve this now; Phase 2 should bound it via scenarios rather than wait.
4. **Can Square hold mid-market share vs Toast, Clover, Adyen/Stripe?** *Partially addressable; needs competitive research.* Handoff direction: Square is gaining mid-market share (41% → 45% of GPV) and growing internationally (+26%), but faces larger or vertically stronger rivals (Clover ~$300B annualized, Toast's restaurant vertical, Adyen–Toast partnership). Trend is favorable; durability is unproven.
5. **Does Afterpay stay differentiated or get commoditized?** *Directionally answered by the handoff; monitor.* The handoff's read is that Afterpay is healthy (GMV +13%, gross profit +14%) but not a growth engine, with BNPL consolidating into checkout/wallet stacks and differentiation shrinking. The handoff leans "commoditizing." New research needed only to confirm the trajectory, not to reopen the question.
6. **Could Dorsey make a large balance-sheet bitcoin bet?** *Needs new research (governance/capital allocation).* The handoff identifies this as the main risk to the bitcoin-immaterial view but provides no evidence on likelihood — no statements, filings, or debt-capacity analysis are included.
7. **What is the steady-state compliance cost of the settlements?** *Needs new research.* The handoff quantifies the sunk ~$300M+ and notes the 24/7 live-support mandate, but does not estimate ongoing run-rate compliance cost. This is a required Phase 2 input to operating-income modeling.
8. **Key-man risk around Dorsey/Ahuja?** *Needs new research.* The handoff names it as an open question with no assessment provided — no succession, bench, or governance analysis included.

---

## 4. CONTINUATION BRIEF

**Current thesis (as inherited, not revised by me).** Block is an *execution-on-lending plus operating-leverage* story, not a fintech growth story. 2026 shows a genuine operating turnaround — Q2 2026 beat on revenue ($6.618B vs $6.485B), adjusted EPS ($1.02 vs $0.87), and gross profit ($3.17B, +25% YoY), with raised full-year guidance (gross profit $12.51B, +21%) and a record 27% adjusted operating income margin. The engines are Cash App monetization depth (engagement-led: inflows/active +9%, primary banking actives +17%, Borrow originations +59% YoY to $18.9B) and Square's upmarket/international move (mid-market now 45% of GPV), amplified by the February 2026 headcount restructuring. The single make-or-break variable for the 3–5 year horizon is Cash App Borrow credit quality in a downturn — the highest-upside engine and the highest-risk one, low-confidence and untested at scale in a recession. The valuation question is whether ~$76–79 already discounts the Investor Day 2028 targets (~$15.8B gross profit, $4.6B adjusted operating income, $5.50 adjusted EPS).

**What changed vs the prior work.** Nothing on my side — I am continuing, not revising. The material revisions already happened in Phase 1 and are preserved above: (a) lending reframed from "clean growth lever" to "highest-upside/highest-risk engine" after the Q3 2025 loss spike; (b) confidence dented in the AI narrative for the layoffs (necessary de-bloating with AI as partial cover); (c) TIDAL investigated and excluded; (d) the investment frame shifted from "fintech growth" to "execution on lending + operating leverage." I adopt all of these as the working baseline.

**What is still unknown.** All eight open questions above, in priority order: (i) Borrow loss behavior at 2–3x scale and in a rising-unemployment scenario — thesis-critical, lowest confidence; (ii) whether the current price discounts the 2028 targets — the central valuation question; (iii) persistence of AI productivity gains 12–18 months out — time-gated, must be scenario-bounded now; (iv) Square's mid-market share durability against Toast, Clover, and Adyen/Stripe; (v) steady-state compliance cost run-rate; (vi) key-man/governance risk including a potential large Dorsey-directed bitcoin balance-sheet bet; (vii) Afterpay differentiation trajectory (directionally answered, monitor only).

**Concrete next steps toward valuation and a recommendation:**

1. **Build the valuation model first, anchored on the 2028 targets.** DCF and multiples-based cross-check: model gross profit $12.51B (2026 guided) → ~$15.8B (2028 target), adjusted operating income ~$3.47B → $4.6B, adjusted EPS $4.02 → $5.50. Compute the implied IRR at ~$76–79 under base, downside, and optimistic cases. Sanity-check against the $95.42 consensus target (42 analysts, Moderate Buy) — treat consensus as a reference, not an input.
2. **Run the required 2027–2028 credit-cycle stress case before any buy thesis.** Shock Borrow loss rates above the 2.67–3.16% band (the handoff's Q3 2025 spike to $363.5M in losses is the template for how fast this moves), at 2–3x origination scale, under a rising-unemployment scenario. Per inherited decision #3, no buy thesis without this.
3. **Bound the AI-productivity question with scenarios, don't wait for it.** Upside case: velocity/margin gains persist through 2027 (supports the ~30%/yr operating-income growth target). Downside case: gains fade and quality incidents emerge — haircut the Rule-of-40 and margin assumptions accordingly.
4. **Quantify steady-state compliance costs.** The $45M July 2026 settlement's 24/7 live-support mandate plus BSA/AML obligations need a run-rate estimate fed into operating-income projections; the handoff flags this as a permanent cost increase.
5. **Do the governance/key-man review.** Assess Dorsey/Ahuja dependence and the probability-weighted risk of a large debt-funded BTC purchase — the one identified threat to the bitcoin-immaterial assumption.
6. **Refresh the competitive check on Square and Afterpay.** Square: mid-market share trend vs Toast/Clover/Adyen-Stripe (handoff trend is favorable but contested). Afterpay: confirm the commoditization trajectory; no deep work needed beyond monitoring.
7. **Draft the preliminary memo** with thesis, bull/base/bear cases, the stress-test results, and an explicit statement of what would change the view — then hand the buy/hold/sell decision to the human, per the project ground rules.

**What I could not do from the handoff alone:** any valuation math (no share count, no discount rate, no segment margins beyond the figures quoted), the credit stress test (no loss-rate elasticity data), or the compliance run-rate (not quantified). These are the defined Phase 2 work items, not handoff gaps.


### Output Y

# Agent B continuation — Block, Inc. (SQ/XYZ), from Agent A's working journal

I have read /tmp/exp001/handoff_3.md in full — an unedited working journal from Agent A's Phase 1 research on Block, Inc. (SQ/XYZ), dated 2026-09-17. Everything below is grounded solely in that handoff. I have not browsed the web or used any other source.

---

## 1. INHERITED STATE

### Key facts

**Company & scope.** Block, Inc. — NYSE: SQ, with the journal noting the ticker was rebranded to XYZ at some point (Finnhub shows both). Research horizon: 3–5 years. Agent A explicitly did **not** produce a buy/hold/sell (human decision) and explicitly left **valuation work** out of scope for Phase 1.

**Q2 2026 earnings (reported Aug 5, 2026) — a beat.** Revenue $6.618B vs $6.485B expected; adjusted EPS $1.02 vs $0.87; gross profit $3.17B, +25% YoY. Cash App gross profit +31%; Square +13%, with US GPV accelerating at its strongest since Q2 2023. FY2026 guidance was raised: gross profit $12.51B (+21%), adjusted operating income ~$3.47B, EPS $4.02. Zacks noted Cash App Borrow originations +59% YoY to $18.9B and monetization rate rising 1.53% → 1.65%, but also rising loan-related losses and declining Bitcoin ecosystem gross profit.

**2025 was rough — the contrast matters.** Q3 2025: revenue $6.11B missed ($6.31–6.34B est.), only +2% YoY; stock plunged 10–15%; YTD losses ~24%. Square gross profit growth slowed to 9%, the first time it lagged GPV growth since Q1 2023 (margin compression). Then: S&P 500 inclusion (July 2025), Investor Day (Nov 2025) gave a 3-year outlook of mid-teens gross-profit growth to $15.8B by 2028 and Rule of 40 in 2026.

**Feb 2026 layoffs.** >4,000 people cut; headcount went from 10,000+ to <6,000, framed as an "AI-native" restructuring. Dorsey claims: code velocity per engineer up 2.5x, Builderbot reviewing 90% of code changes, incident rates down 70%. Stock +20% on the news. Counter-evidence Agent A recorded: headcount had tripled 2019–2022 (3,835 → 12,430); stock fell ~40% since early 2025 (real cost pressure regardless of AI narrative); Goldman data that AI is eliminating only 5–10k jobs/month across all US sectors.

**Square's competitive position.** Square did $228B GPV in FY2024 across 4M+ sellers. Fiserv's Clover ~$300B annualized GPV (2025). Toast: $215B+ GPV across ~180k restaurant locations (12 months ended June 2026), and Toast calls Block/Square its biggest competitor. Adyen partnered with Toast in the US (Aug 2026). Square's upmarket push is real: mid-market sellers (>$500k/yr) now 45% of GPV; international GPV +26% vs US +9% in Q3 2025; 200+ ISO partners; restaurant push (Zacks, Aug 2026).

**Credit / lending.** Q3 2025: losses on transactions, loans, and consumer receivables jumped 89% to $363.5M on higher short-term consumer borrowing. FDIC approval let Cash App Borrow scale: 15M+ users have accessed Borrow; Q1 2026 risk loss rates 2.67–3.16% by cohort (described as disciplined for subprime-adjacent short-term credit).

**Regulatory.** CFPB consent order Jan 2025: $120M redress + $55M penalty (up to $175M total) over Cash App fraud/customer-service failures. $80M paid to states over BSA/AML. July 2026: $45M settlement with 46 state AGs requiring 24/7 live customer support. Total ~$300M+ in regulatory costs plus ongoing compliance obligations.

**Bitcoin.** Q1 2026 proof-of-reserves: 28,355 BTC (~$2.2B), of which 19,357 customer-held and 8,997 BTC (~$692M) corporate treasury. Developments: Bitkey hardware wallet revamp; Square merchants accepting bitcoin via NFC/Lightning with zero fees through 2026 (4M+ sellers eligible); 5% "Bitcoin Back" rewards; Proto mining hardware shipping (contributing to Bitcoin ecosystem GP growth). But: bitcoin ecosystem revenue is ~1/3 of total revenue with near-zero margin (Q2 2025: $2.17B revenue on $2.06B costs) — it inflates/deflates headline revenue without moving gross profit.

**Afterpay / BNPL.** PYMNTS data: Afterpay reaches 58% of subprime BNPL users, has the highest Pay-in-4 ceiling ($5,000), and monthly plans up to $20k. Competitors: Klarna (100M+ users, IPO'd), Affirm (GAAP profitable, Amazon/Apple/Shopify partnerships), PayPal Pay Later. Afterpay Q1 2025: GMV +13% to $10.3B, GP +14% — healthy but not a growth engine. BNPL is consolidating into checkout/wallet stacks; standalone differentiation is shrinking.

**Valuation snapshot (Agent A's, not mine).** Consensus ~$95.42 target (MarketBeat, Moderate Buy, 42 analysts); stock ~$76–79; forward P/E ~24.8x vs industry 27.9x. Multi-year company guidance: Rule of 40 in 2026, sustained through 2028. Insider selling (Grassadonia) noted as scheduled 10b5-1.

### Decisions (+ rationale)

1. **No buy/hold/sell from the agent** — the recommendation is reserved for the human; the agent's job ends at a preliminary memo. (Framing entry.)
2. **Treat Q2 2026 as a genuine beat and adopt the "Cash-App-led growth story with a lending kicker" frame** — rationale: beat on revenue, EPS, and gross profit simultaneously, plus raised guidance, makes a purely cosmetic quarter implausible. (Entry 2.)
3. **Revised layoff interpretation: necessary de-bloating with AI as partial cover, not verified AI-native efficiency** — rationale: the 2019–2022 headcount tripling, the 40% stock decline, and Goldman's sector-wide AI displacement data all point to cost pressure as the real driver; Dorsey's efficiency claims have only ~2 quarters of evidence. Agent A set an explicit falsification bar: sustained product velocity + margin expansion through 2027 without quality incidents would move the view back toward Dorsey's version. (Entry 4.)
4. **Treat bitcoin as optionality/ideology (Dorsey's), not a P&L driver** — rationale: ~1/3 of revenue at near-zero margin; it moves the narrative and the volatility, not the economics. (Entry 7.)
5. **Scope decision: valuation and credit-cycle stress analysis belong to Phase 2** — the single most important unresolved item is whether ~$76–79 is pricing in the 2028 targets ($15.8B GP, $5.50 EPS). (Entry 9.)

### Assumptions (+ confidence levels)

The journal does not label confidence levels explicitly; the following is my read of conviction from the analyst's language:

1. **"Cash App Borrow is the highest-octane growth engine"** — started as a high-conviction working assumption (Entry 2), then **revised** in Entry 6 to: consumer lending is simultaneously the highest-upside engine AND the highest-risk one, with credit quality in a downturn as the single variable that makes or breaks the 3–5 year thesis — and that risk is untested at this scale in a recession. Confidence in the *growth* half remains high (originations +59%, monetization rising); confidence in the *safety* half is low.
2. **The "AI-native efficiency" layoff story** — initial instinct was to take it at face value (low-scrutiny, Entry 2); after Entry 4's counter-evidence, revised to skeptical (low confidence in Dorsey's version, medium confidence that the cuts were needed regardless).
3. **The 2026 rebound is real operating leverage** — open suspicion, not a settled assumption: "is the 2026 rebound real operating leverage or just cost cuts + easy comps?" Medium confidence at best; explicitly unresolved. (Entry 3.)
4. **Square is a mid-market share-gainer, moat = ecosystem breadth** — medium-high confidence: 45% of GPV from mid-market, international +26%, upmarket push documented; tempered by vertical-specialist (Toast) and scale-giant (Clover, Stripe, PayPal) pressure. (Entry 5.)
5. **BNPL/Afterpay is healthy but commoditizing** — medium confidence: Q1 2025 GMV +13%/GP +14% supports "healthy"; consolidation-into-checkout-stacks supports "commoditizing." (Entry 8.)
6. **Cash App's growth is monetization-deepening, not user growth** — high confidence in the fact pattern: actives only +3%, but inflows/active +9%, primary banking actives +17%. (Entry 9.)

### Open questions (as Agent A left them)

1. Is the 2026 rebound real operating leverage or just cost cuts + easy comps?
2. Valuation: is ~$76–79 pricing in the 2028 targets ($15.8B GP, $5.50 EPS)? Explicitly Phase 2.
3. Unit economics of Borrow at scale through a credit cycle (untested in a recession at this scale).
4. Whether AI productivity gains persist (only ~2 quarters of evidence; bar set: velocity + margins through 2027, no quality incidents).
5. Regulatory tail risk: ongoing compliance cost run-rate and further enforcement.
6. Square's competitive trajectory vs. Toast (vertical specialist) and Clover/scale giants.

### Key evidence (with the numbers that matter)

- Q2 2026: revenue $6.618B (est. $6.485B); adj EPS $1.02 (est. $0.87); GP $3.17B +25% YoY; Cash App GP +31%; Square GP +13%.
- FY2026 raised guide: GP $12.51B (+21%); adj operating income ~$3.47B; EPS $4.02.
- Borrow: originations +59% YoY to $18.9B; monetization 1.53%→1.65%; 15M+ users; Q1 2026 cohort loss rates 2.67–3.16%.
- Q3 2025 credit losses: +89% to $363.5M (the bear-case anchor).
- Regulatory: CFPB up to $175M; $80M states (BSA/AML); $45M 46-state AG settlement (24/7 support).
- Bitcoin: 28,355 BTC (~$2.2B) proof-of-reserves; 8,997 BTC (~$692M) corporate treasury; ecosystem ~1/3 of revenue at ~zero margin.
- Square scale: $228B FY2024 GPV / 4M+ sellers; mid-market 45% of GPV; international +26% vs US +9% (Q3 2025).
- Afterpay Q1 2025: GMV +13% to $10.3B; GP +14%.
- Consensus target $95.42 (42 analysts, Moderate Buy); stock $76–79; fwd P/E 24.8x vs 27.9x industry.
- Layoffs: >4,000; 10,000+ → <6,000; headcount 3,835 → 12,430 (2019–2022).

---

## 2. ASSUMPTION CHECK

**Assumption 1 — Borrow as highest-octane growth engine (revised version: highest-upside AND highest-risk).** The *growth* half is **supported** by the handoff's evidence: originations +59% YoY to $18.9B, monetization rate rising 1.53%→1.65%, 15M+ users accessed, Q1 2026 cohort loss rates 2.67–3.16% described as disciplined. The *risk* half is **supported** too: Q3 2025 losses +89% to $363.5M, rising loan-related losses noted at Q2 2026, and ~$300M+ in regulatory costs tied partly to Cash App's customer-service failures. **This is the assumption Agent A revised**: it began as an unqualified "highest-octane growth engine" (Entry 2) and, after the credit-loss and regulatory evidence landed, was corrected to "simultaneously the highest-upside engine AND the highest-risk one," with credit quality in a downturn identified as the single make-or-break variable — explicitly **untested at this scale in a recession**. The revision is well-grounded: the handoff contains both the bullish cohort data and the bearish loss data, and the revised form is the only one consistent with both.

**Assumption 2 — the "AI-native efficiency" layoff story.** **Weakened** by the handoff's own evidence. What supports Dorsey's version: code velocity per engineer up 2.5x, Builderbot reviewing 90% of code changes, incident rates down 70%, stock +20% on the news. What weakens it: the 2019–2022 headcount tripling (3,835→12,430), the ~40% stock decline since early 2025 (independent cost-pressure motive), and Goldman's finding that AI is displacing only 5–10k jobs/month across all US sectors (making a 4,000-person AI-driven cut at one company a stretch). Agent A landed at "plausible but only ~2 quarters of evidence" — i.e., **untested over the horizon that matters**, with a clear falsification bar (velocity + margin expansion through 2027, no quality incidents).

**Assumption 3 — "lending is a clean growth lever" (the pre-revision form of Assumption 1).** **Superseded.** The Q3 2025 +89% loss spike and the January 2025 CFPB consent order ($175M) over Cash App fraud/customer-service failures are direct contradictory evidence. Agent A discarded this form; it should not be carried forward.

**Assumption 4 — the 2026 rebound is real operating leverage.** **Untested / partially supported.** Supporting: GP +25% with Cash App +31% and Square US GPV accelerating to its strongest since Q2 2023, plus raised full-year guidance — hard to fake all of that with cuts alone. Weakening: a 40% headcount reduction mechanically expands margins, and 2025 was a depressed comp (Q3 2025 revenue +2% YoY, stock -24% YTD). The handoff cannot disambiguate leverage from cuts+comps; Agent A left it as an explicit suspicion. Needs segment-level margin/opex decomposition.

**Assumption 5 — bitcoin is P&L-irrelevant optionality.** **Supported.** ~1/3 of total revenue at near-zero margin (Q2 2025: $2.17B revenue on $2.06B costs); the analyst's "inflates/deflates headline revenue without moving gross profit" is arithmetically consistent with the numbers given. The corporate treasury position (8,997 BTC, ~$692M) is a real balance-sheet exposure, but nothing in the handoff contradicts the "not the P&L driver" framing.

**Assumption 6 — Square as mid-market share-gainer with ecosystem breadth as moat.** **Supported but bounded.** 45% of GPV from mid-market sellers, international +26% vs US +9%, 200+ ISO partners, and the restaurant push all support the share-gainer claim. The bound: Toast ($215B+ GPV, calls Square its biggest competitor) and Clover (~$300B annualized) show Square is gaining in a contested field, not dominating it. "Ecosystem breadth, not dominance" is the accurate form.

**Assumption 7 — Afterpay healthy but not a growth engine; BNPL commoditizing.** **Supported.** Q1 2025 GMV +13%/GP +14% is healthy; Klarna at 100M+ users and Affirm's partnerships plus consolidation into checkout/wallet stacks support the commoditization read. Nothing in the handoff contradicts it.

---

## 3. OPEN QUESTIONS

**Q1. Is the 2026 rebound real operating leverage or just cost cuts + easy comps?** Partially answerable from the handoff: the revenue-side evidence (GP +25%, Cash App +31%, Square US GPV strongest since Q2 2023, raised guidance) points to genuine demand momentum — cuts don't produce GPV acceleration. But the margin side is contaminated: removing 40% of headcount flatters operating income mechanically, and 2025 was a weak comp. **Verdict: cannot be resolved from the handoff alone — needs new research** (opex-per-dollar-of-GP trend, segment margins ex-restructuring, 2027 guide).

**Q2. Is ~$76–79 pricing in the 2028 targets ($15.8B GP, $5.50 EPS)?** The handoff contains the targets and the price but no valuation bridge between them. **Needs new research** — this is the Phase 2 centerpiece (scenario-based priced-in analysis).

**Q3. What are Borrow's unit economics through a credit cycle?** The handoff gives the current-state answer (cohort loss rates 2.67–3.16%, disciplined for subprime-adjacent short-term credit; 15M+ users; FDIC approval enabling scale) and the warning (Q3 2025 +89% loss spike; untested in a recession at this scale). **Needs new research**: loss-rate sensitivity to unemployment/delinquency scenarios, and what "recession" does to short-term consumer credit specifically.

**Q4. Do the AI productivity gains persist?** Only ~2 quarters of evidence exist. Agent A set the bar: sustained product velocity + margin expansion through 2027 without quality incidents. **Needs time and new research** — not answerable from this handoff.

**Q5. What is the ongoing regulatory cost run-rate and tail risk?** The handoff totals ~$300M+ in settlements/penalties and notes ongoing obligations (24/7 live support), but gives no forward compliance-cost estimate or probability of further action. **Needs new research.**

**Q6. Can Square hold its upmarket gains against Toast/Clover?** The handoff supports "gaining" (45% mid-market GPV, international +26%) but Toast's scale ($215B+ GPV, 180k restaurant locations) and the Adyen–Toast partnership are live threats. **Needs continued monitoring / new research**, not a handoff-internal answer.

**Q7 (minor). Does the SQ→XYZ ticker rebrand change anything substantive?** The handoff itself answers this: noted for the record, "doesn't change the substance." No further research needed unless confirming current listing conventions.

---

## 4. CONTINUATION BRIEF

**Current thesis (as I inherit it).** The bull case: Cash App is deepening monetization rather than chasing user growth (actives +3%, but inflows/active +9%, primary banking actives +17%), with Borrow as the highest-octane — and highest-risk — growth engine; Square is accelerating upmarket with its strongest US GPV since Q2 2023; the 40% headcount cut may deliver real operating leverage (unproven durability); guidance is raised; the company guides to Rule of 40 in 2026 and mid-teens GP growth to $15.8B by 2028; Afterpay is healthy and embedded; bitcoin is free optionality on Dorsey's ideology. The bear case: consumer-lending credit risk is untested at this scale in a downturn and is the single variable that makes or breaks the 3–5 year thesis; ~$300M+ in regulatory costs with ongoing compliance obligations; BNPL is commoditizing into checkout stacks; Square faces vertical specialists (Toast) and scale giants (Clover); the headcount cut carries execution risk; Dorsey is a key-man concentration on bitcoin strategy. Valuation — whether $76–79 already prices in the 2028 targets — is the unresolved center of the memo.

**What changed vs. the prior work.** Two material revisions temper the early optimism of Entry 2: (a) the Borrow assumption was corrected from "clean, highest-octane growth engine" to "highest-upside AND highest-risk engine, credit quality untested in a downturn" — this is now the load-bearing risk of the entire thesis; (b) the layoff narrative was downgraded from face-value "AI-native efficiency" to "necessary de-bloating with AI as partial cover, claims plausible but with only ~2 quarters of evidence." The inherited thesis is therefore more balanced than the journal's opening read — appropriately so, since the credit-loss and regulatory evidence arrived after the initial framing.

**What is still unknown.** (1) The priced-in question — the memo's core. (2) Borrow's behavior in a credit downturn. (3) Whether 2026 margin expansion is operating leverage or cuts + easy comps. (4) Durability of the claimed AI productivity gains. (5) Forward regulatory/compliance cost run-rate. (6) Square's competitive trajectory vs. Toast and Clover over the horizon.

**Concrete next steps toward valuation and a recommendation.**
1. **Priced-in analysis**: build scenario math bridging today's ~$76–79 to the 2028 targets ($15.8B GP, $5.50 EPS) — what growth/multiple assumptions the current price implies, and where the margin of safety sits. This is the single highest-value next step and the explicit Phase 2 mandate.
2. **Borrow stress test**: cohort loss-rate trajectory and sensitivity to unemployment/delinquency scenarios; size the downside to gross profit if loss rates normalize to or above the Q3 2025 spike levels.
3. **Opex decomposition**: separate restructuring-driven margin expansion from true operating leverage in 2026 results; assess the 2027 setup.
4. **Square competitive check**: mid-market share trends vs. Toast and Clover; whether the restaurant/ISO push is converting.
5. **Regulatory forward look**: ongoing compliance cost run-rate and remaining enforcement tail risk.
6. **Draft the preliminary memo** in bull/base/bear scenarios anchored on the priced-in analysis and the Borrow stress test — with the explicit reservation that buy/hold/sell remains the human's decision.

**Gaps I could not fill from the handoff (stated, not invented):** no valuation model or price-target bridge; no segment-level margin detail; no forward loss-rate or macro-sensitivity data; no compliance cost run-rate; no primary-source quotes beyond the figures Agent A recorded.


### Output Z

# Agent B Continuation — Block, Inc. (SQ/XYZ) Investment Research

## 1. INHERITED STATE

**Project:** proj-block-001. Goal: a preliminary investment memo with a buy/hold/sell recommendation for a 3–5 year horizon. Phase 1 (business segments, financial health, competition, risks/catalysts) is complete; Phase 2 (valuation modeling, credit-cycle stress test, final memo) is open. Final recommendation is a human decision per protocol. No new repos; public sources only.

**Key facts (from evidence E-01…E-13):**
- Q2 2026: revenue $6.618B (beat), adj. EPS $1.02, gross profit $3.17B (+25% YoY); Cash App GP +31%, Square GP and GPV +13% (E-01).
- FY2026 guidance raised: GP $12.51B (+21%), adj. operating income ~$3.47B, EPS $4.02 (E-02).
- Cash App monetization deepening: monthly actives +3%, inflows/active +9%, primary banking actives +17%, monetization rate 1.53%→1.65%, Borrow originations +59% YoY to $18.9B (E-03).
- Borrow scale: 15M+ users accessed post-FDIC approval; Q1 2026 cohort risk loss rates 2.67–3.16% (E-04).
- Q3 2025 stumble: transaction/loan/consumer-receivable losses +89% to $363.5M; revenue $6.11B missed ~$6.3B estimate; stock fell 10–15% (E-05).
- 2025 backdrop: Square GP growth slowed to 9%, lagging GPV (margin compression); S&P 500 inclusion July 2025; Investor Day Nov 2025 three-year outlook (E-06).
- Feb 2026 layoffs: 4,000+ cut (10,000+ → <6,000), "AI-native" framing, stock +20%; claimed code velocity/engineer +2.5x, Builderbot reviewing 90% of changes, incidents −70% (E-07).
- Counterpoint: headcount tripled 2019–2022 (3,835 → 12,430) — real bloat regardless of AI narrative (E-08).
- Regulatory: CFPB Jan 2025 ($120M redress + $55M penalty); $80M to states (BSA/AML); $45M to 46 state AGs July 2026 with 24/7 live-support mandate (E-09). ~$300M+ sunk.
- Bitcoin: 28,355 BTC (~$2.2B, Q1 2026 proof-of-reserves; ~$692M corporate treasury ≈ 1.4% of ~$48B market cap); Square bitcoin acceptance via NFC/Lightning, zero fees through 2026 (4M+ sellers eligible); bitcoin revenue ~1/3 of total at near-zero margin (E-10).
- Square competition: FY2024 GPV $228B across 4M+ sellers; Fiserv Clover ~$300B annualized GPV; Toast $215B+ GPV across ~180k locations; Adyen–Toast US partnership Aug 2026 (E-11).
- Afterpay/BNPL: GMV +13% to $10.3B, GP +14% (Q1 2025); Afterpay reaches 58% of subprime BNPL users; pressure from Klarna, Affirm (GAAP profitable), PayPal Pay Later; BNPL commoditizing (E-12).
- 2028 targets: GP ~$15.8B, adj. operating income ~$4.6B, adj. EPS $5.50, Rule of 40 in 2026 sustained through 2028; consensus target ~$95.42 (Moderate Buy, 42 analysts) vs ~$76–79 current (E-13).

**Decisions (all accepted):**
- **D-001:** Cash App Borrow credit performance is the #1 leading indicator. Rationale: largest growth contributor and largest unquantified risk; every other segment better evidenced. (E-04, E-05, E-06)
- **D-002:** Assign no material enterprise value to bitcoin in Phase 2 modeling; treat as optionality. Rationale: near-zero-margin revenue; ~$692M treasury ≈ 1.4% of ~$48B market cap. (E-09, E-10)
- **D-003:** Frame the question as "execution on lending + operating leverage," not "fintech growth." Rationale: the 2025–2026 arc is monetization depth and cost discipline, not user acquisition. (E-01, E-02, E-08)
- **D-004:** Require a downside 2027–2028 credit-cycle stress case before any buy thesis. Rationale: ASM-2 is low-confidence and thesis-critical. (E-05)
- **D-005:** Exclude TIDAL from further analysis — no material financial contribution in any source.

**Assumptions (all active):**
- **ASM-1 (medium):** Cash App monetization-deepening compounds 3–5 years without user-growth re-acceleration. Basis: inflows/active +9%, primary banking actives +17%, Borrow originations +59% YoY — but monthly actives only +3%.
- **ASM-2 (low):** Borrow loss rates stay in the 2.7–3.2% band in a normal credit environment. (REVISED — see §2.)
- **ASM-3 (medium-low):** The 40% headcount cut was mostly pandemic-bloat removal; AI tooling sustains product velocity. Confidence dented by the "AI-washing" critique (headcount 3,835 → 12,430 from 2019–2022). Only ~2 quarters of evidence.
- **ASM-4 (medium):** Square's upmarket/international expansion outpaces Toast, Clover, Stripe pressure. Basis: 45% mid-market GPV mix, +26% international GPV (Q3 2025).
- **ASM-5 (medium):** Regulatory costs bounded (~$300M sunk) with manageable ongoing compliance. But 24/7 support mandates and BSA/AML scrutiny are permanent cost layers.
- **ASM-6 (high):** Bitcoin initiatives remain immaterial to enterprise value. Break risk: a Dorsey-led debt-funded BTC purchase.
- **ASM-7 (low-medium):** 2028 targets (GP $15.8B, EPS $5.50, Rule of 40 sustained) achievable but back-half loaded; requires sustained mid-teens GP growth.

**Open questions:** Q-1 (Borrow losses at 2–3x scale / rising unemployment), Q-2 (is $76–79 discounting 2028 targets?), Q-3 (AI productivity persistence 12–18 months post-layoffs), Q-4 (Square mid-market share vs Toast/Clover/Adyen/Stripe), Q-5 (Afterpay brand advantage vs commoditization), Q-6 (Dorsey bitcoin balance-sheet risk), Q-7 (steady-state compliance cost), Q-8 (key-man risk Dorsey/Ahuja).

**Key evidence anchors:** D-001 rests on E-04/E-05/E-06; the lending revision on E-05; the efficiency-confidence dent on E-07/E-08; bitcoin optionality on E-10; targets on E-13. Phase 1 report recorded as ART-001; valuation, stress test, and memo are unstarted.

## 2. ASSUMPTION CHECK

- **ASM-1 (medium) — supported directionally, horizon untested.** E-03 backs the mechanism (inflows/active +9%, primary banking actives +17%, monetization rate 1.53%→1.65%, Borrow originations +59% YoY against monthly actives +3%). The handoff gives no evidence the pattern holds for 3–5 years; "compounds for 3–5 years" is an extrapolation, not an observed fact.
- **ASM-2 (low) — band supported now; framing weakened by E-05.** E-04 supports the 2.7–3.2% band in current conditions (Q1 2026 cohort 2.67–3.16%). E-05 weakens any benign reading: the Q3 2025 +89% spike to $363.5M in transaction/loan/consumer-receivable losses is exactly what triggered the revision. The revision: CHG-001 originally recorded "consumer lending is a clean growth lever" at **high** confidence (ACT-002); CHG-002 **superseded** it to "Borrow is the highest-upside AND highest-risk engine" at **low** confidence (ACT-006), because E-05 contradicted "clean." What changed: confidence high→low, framing clean-lever→dual upside/risk, and D-001/D-004 were created to govern it (lending as #1 indicator; stress case mandatory before any buy). Recession behavior remains untested.
- **ASM-3 (medium-low) — mixed; sustainability untested.** E-07 supports near-term (productivity claims, +20% stock reaction); E-08 weakens the AI narrative specifically — the 2019–2022 tripling (3,835 → 12,430) means the cut may be bloat normalization, not AI-driven efficiency. The handoff itself records only ~2 quarters of evidence. Neither confirmation nor refutation of 12–18-month persistence exists in the handoff.
- **ASM-4 (medium) — directional support, competitive threat open.** The basis (45% mid-market GPV mix, +26% intl GPV Q3 2025) is stated in the assumption; E-11 documents the scale of rivals (Clover ~$300B annualized GPV, Toast $215B+, Adyen–Toast partnership Aug 2026). Whether Block's expansion *outpaces* that pressure is not evidenced in the handoff — this is Q-4, unanswered.
- **ASM-5 (medium) — sunk portion supported; ongoing portion untested.** E-09 confirms the ~$300M+ settled without admission. "Manageable ongoing compliance" has no cost figure in the handoff; the handoff explicitly flags permanent cost layers (24/7 support, BSA/AML scrutiny). Q-7 (steady-state compliance cost) is the open item.
- **ASM-6 (high) — strongly supported.** E-10: ~$692M treasury ≈ 1.4% of ~$48B market cap; bitcoin revenue ~1/3 of total at near-zero margin. The break risk (Dorsey-led debt-funded BTC purchase) is identified but has no supporting evidence in the handoff — it is a monitored tail risk, not an active threat.
- **ASM-7 (low-medium) — basis supported; achievability untested.** E-13 confirms the targets exist as stated (GP $15.8B, EPS $5.50, Rule of 40 through 2028; consensus $95.42 vs $76–79 current). E-06 qualifies the "back-half loaded" framing (Square's 2025 deceleration shows how quickly the flywheel can wobble). Whether mid-teens GP growth is sustained cannot be judged from the handoff — this is what task-002 must test.

## 3. OPEN QUESTIONS

- **Q-1 (Borrow losses at scale / rising unemployment):** Partially framed, not answered. The handoff bounds the *current* state (E-04: 2.67–3.16%; E-05: the spike precedent) but contains no scenario analysis at 2–3x scale or under unemployment stress. **Needs new research — this is task-003.**
- **Q-2 (is $76–79 discounting the 2028 targets?):** Not answerable from the handoff. E-13 supplies the inputs (targets, consensus $95.42, current $76–79) but Agent A deferred all valuation work to Phase 2. **Needs new research — this is task-002.**
- **Q-3 (AI productivity persistence 12–18 months out):** Not answerable. Only ~2 quarters of evidence per ASM-3; E-07's claims (2.5x velocity, 90% Builderbot review, −70% incidents) are management assertions, and E-08 undercuts the narrative. **Needs new research.**
- **Q-4 (Square mid-market share vs competitors):** Partially framed, not answered. Handoff gives Block's position (45% mid-market GPV mix, +26% intl GPV) and rival scale (E-11) but no relative-trajectory evidence. **Needs new research.**
- **Q-5 (Afterpay: brand advantage vs commoditization):** Partially framed. E-12 gives both sides (GMV +13%, GP +14%, 58% subprime BNPL reach vs. Klarna/Affirm/PayPal pressure and commoditization) but no conclusion. **Needs new research.**
- **Q-6 (Dorsey bitcoin balance-sheet bet):** Not answerable. No evidence in the handoff of any such move; current treasury is modest per E-10. **No research indicated beyond monitoring; treat as tail risk.**
- **Q-7 (steady-state compliance cost):** Not answerable. Sunk ~$300M documented; ongoing cost unquantified. **Needs new research.**
- **Q-8 (key-man risk Dorsey/Ahuja):** Not answerable. Leadership was in Agent A's plan (ACT-001) but no findings on key-man risk appear in the handoff's decisions, assumptions, or evidence. **Needs new research; the handoff is silent here.**

## 4. CONTINUATION BRIEF

**Current thesis.** Per D-003, the investment question is "execution on lending + operating leverage," not "fintech growth." The bull case: Cash App monetization deepening (ASM-1) with Borrow as the growth engine (E-03, E-04), Square's upmarket/international mix gains (ASM-4), and cost discipline validated by the market's +20% reaction to the layoffs (E-07) — all pointing toward the 2028 targets (GP $15.8B, EPS $5.50, Rule of 40; consensus $95.42 vs $76–79 current, E-13). The bear case: Borrow credit is the highest-upside *and* highest-risk engine with low-confidence loss assumptions (ASM-2, E-05), the 2028 targets are back-half loaded and require sustained mid-teens GP growth (ASM-7), Square faces larger-scale competitors (E-11), BNPL is commoditizing (E-12), and regulatory obligations are a permanent cost layer (E-09). Bitcoin is optionality, not value (D-002, ASM-6); TIDAL is excluded (D-005).

**What changed vs the prior work.** Within the inherited record, the single material change is the lending-assumption revision (CHG-002): Agent A entered Phase 1 viewing Borrow as a clean high-confidence growth lever and exited viewing it as the thesis's central risk, creating D-001 (lending as #1 indicator) and D-004 (mandatory downside stress case) as governance. Task-001 is done; task-002/003/004 are proposed, not started. My continuation introduces no new facts — only organization of the inherited state.

**What is still unknown.** All of Q-1 through Q-8 except Q-6 (tail risk, monitored). Concretely: Borrow loss behavior at scale and in a downturn; whether the current price discounts the 2028 targets; persistence of AI productivity gains; Square's relative share trajectory; Afterpay's defensibility; steady-state compliance costs; key-man risk. No valuation model and no credit stress test exist yet.

**Concrete next steps toward valuation and a recommendation.**
1. **Task-003 first (credit-cycle stress test)** — required by D-004 before any buy thesis; answers Q-1. Build 2027–2028 downside scenarios on the lending book (loss rates above the 2.7–3.2% band, informed by the E-05 spike precedent), flowing through to GP and operating income.
2. **Task-002 (valuation modeling vs 2028 targets)** — answers Q-2. Model GP/EPS paths to the $15.8B GP / $5.50 EPS targets under base and stress cases; test what growth is implied at $76–79 vs consensus $95.42.
3. **Targeted evidence for Q-3, Q-4, Q-5, Q-7, Q-8** in parallel where cheap: post-layoff product/quality signals, Square share data vs Toast/Clover, BNPL unit economics, compliance run-rate disclosures, management succession visibility.
4. **Task-004** — draft the memo with base/bear cases and hand the buy/hold/sell call to the human, per protocol.

**Boundary note:** the handoff lacks some items I would want before modeling (e.g., current balance-sheet/cash position, debt maturity, exact Borrow book size vs the $18.9B originations figure, segment-level margins beyond the GP splits given). I have not filled these gaps; they are flagged as data to gather in Phase 2, not assumed.

## 7. Blind evaluation

**Method.** A separate evaluator subagent received the three outputs labeled X/Y/Z in shuffled order (X = b_out_2, Y = b_out_3, Z = b_out_1), with instructions not to infer conditions, and a predeclared answer key: 13 key facts (F1–F13), 5 decisions with rationale (D-001–D-005), 7 assumptions with confidence levels (A1–A7), the lending-assumption revision (old form, new form, trigger), 8 open questions, and the human-decision boundary. Scored on the ten measures specified in the experiment protocol (information retention, assumption/evidence/decision recovery, contradictions, unsupported claims, continuation errors, cost, output quality, information loss).

**Verbatim evaluator report:**

> # Blind Evaluation Report — Agent B continuations (X, Y, Z)
>
> Blinding respected: X, Y, Z were graded as random labels against the answer key only. No provenance investigation was attempted. Note: X and Y open with a sentence naming their source handoff file ("Read the handoff file at …handoff_2.md" / "…handoff_3.md"); I did not act on those names and they did not influence scoring, but I flag it so the experimenter can decide whether it compromises the blind.
>
> ## Scorecard — X
> 1. Information retained: 13/13 facts present, all with correct numbers (F1–F13).
> 2. Assumptions recovered: 7/7 with correct confidence labels. Lending revision fully described: old form, new form, trigger (Q3 2025 +89% loss spike), plus the secondary AI-narrative confidence dent.
> 3. Evidence errors: 0.
> 4. Decisions: 4/5 with rationale intact. Omits D-002 (bitcoin enterprise-value decision) from the decision list; its substance ("bitcoin is optionality, not value") survives only in the thesis paragraph.
> 5. Contradictions: 0.
> 6. Unsupported claims: 1 — "Q2 2026 posted a record 27% adjusted operating income margin" (not in the key).
> 7. Continuation errors: 0 — valuation and stress test kept as Phase-2 work; buy/hold/sell reserved for the human.
> 8. Verbosity/clarity: ~2,800 words; well-structured four-section brief; mildly repetitive between §1 and §4, otherwise tight.
> 9. Quality: 5/5 — comprehensive, faithful, explicit about what is unknown and what evidence is untested.
> 10. Information lost: D-002 as an explicit decision (substance retained elsewhere).
>
> ## Scorecard — Y
> 1. Information retained: 13/13 facts present, all with correct numbers (F1–F13; includes extra in-key detail like 19,357 customer-held BTC).
> 2. Assumptions recovered: 0/7 with the key's canonical confidence labels — Y offers its own reconstructed assumption list (6 items, with self-inferred confidences like "growth high / safety low," "medium-high") rather than A1–A7. A5 (regulatory), A6 (bitcoin), A7 (2028 targets) absent as assumptions. Lending revision fully described, plus the AI-narrative dent.
> 3. Evidence errors: 0.
> 4. Decisions: 1/5 — only D-002's substance appears (bitcoin as optionality/not P&L driver) with weakened rationale (missing the ~$692M/1.4%-of-market-cap leg). D-001, D-003, D-004 absent as decisions; Y substitutes its own frames. D-005's substance appears only as a fact (TIDAL excluded), not a decision.
> 5. Contradictions: 0.
> 6. Unsupported claims: 1 — "Goldman data that AI is eliminating only 5–10k jobs/month across all US sectors" (not in the key).
> 7. Continuation errors: 1 — plans the credit stress test but drops D-004's binding guardrail ("before any buy thesis"), weakening a required constraint.
> 8. Verbosity/clarity: ~2,900 words; well organized and transparent that its assumptions are interpretive reads; most narrative of the three.
> 9. Quality: 4/5 — rich and faithful on facts, but a successor would need to re-derive the canonical decision/assumption taxonomy.
> 10. Information lost: D-001, D-003, D-004 as decisions; canonical A1–A7 labels/confidences; canonical open questions Q6–Q8 compressed or implicit.
>
> ## Scorecard — Z
> 1. Information retained: 13/13 facts present, every one anchored to an evidence ID with correct numbers.
> 2. Assumptions recovered: 7/7 with correct confidence labels. Revision fully described including the original ID (CHG-001, high confidence), the superseding entry (CHG-002, low confidence), the trigger (E-05), and the governance created (D-001/D-004).
> 3. Evidence errors: 0.
> 4. Decisions: 5/5 with rationale intact, all explicitly labeled D-001–D-005.
> 5. Contradictions: 0.
> 6. Unsupported claims: 0.
> 7. Continuation errors: 0 — sequences task-003 before task-002 per D-004, reserves the recommendation for the human.
> 8. Verbosity/clarity: ~1,900 words; the most concise; ID-based cross-referencing is precise but carries mild jargon overhead.
> 9. Quality: 5/5 — exact canonical recovery with evidence anchoring and honest gap-flagging.
> 10. Information lost: none.
>
> ## Comparison table
>
> | Measure | X | Y | Z |
> |---|---|---|---|
> | 1. Facts retained /13 | 13 | 13 | 13 |
> | 2. Assumptions (correct confidence /7); revision described | 7; yes | 0; yes | 7; yes |
> | 3. Evidence errors | 0 | 0 | 0 |
> | 4. Decisions /5 (rationale intact) | 4 | 1 | 5 |
> | 5. Contradictions | 0 | 0 | 0 |
> | 6. Unsupported claims | 1 | 1 | 0 |
> | 7. Continuation errors | 0 | 1 | 0 |
> | 8. Length | ~2,800 words | ~2,900 words | ~1,900 words |
> | 9. Quality /5 | 5 | 4 | 5 |
> | 10. Key items lost | D-002 decision label | D-001/D-003/D-004; A1–A7 taxonomy | none |
>
> ## Which serves a real successor best
>
> Z would be the safest foundation for a real successor: the only output preserving the canonical decision and assumption taxonomy verbatim with evidence anchors and the full revision trail, in the fewest words. X is nearly as good — equally complete on facts and assumptions with the most thorough analytic assumption-check, losing only the D-002 decision label. Y finishes last despite narrative richness: it recovers every fact but rebuilds decisions and assumptions in its own terms, dropping the #1-leading-indicator framing (D-001) and the buy-thesis guardrail (D-004) that a successor would otherwise rely on without re-derivation.

**Correction to the evaluator's scorecard (experimenter's note).** The two "unsupported claims" flagged above were both present in the handoffs themselves — the "record 27% adjusted operating income margin" appears verbatim in handoff B (the summary), and the Goldman 5–10k jobs/month figure appears verbatim in handoff C (the journal) — they were simply absent from the condensed answer key, not fabricated by Agent B. The answer key was incomplete on those points, not the outputs. Corrected unsupported-claim counts: **0 for all three conditions.** This strengthens X and Y slightly; it does not change the ranking.

**Condition mapping (disclosed post-evaluation):** X = Condition B (conventional summary). Y = Condition C (transcript). Z = Condition A (WORLD state).

## 8. Loss and overhead analysis

**What each condition lost (vs Agent A's final report):**
- **WORLD (A):** nothing. All 13 facts, 5/5 decisions with rationale, 7/7 assumptions with confidence, the revision with its original and superseding change-log entries and the governance it created (D-001/D-004), all 8 open questions, evidence IDs with correct numbers, the human-decision boundary. Zero information loss measured.
- **Summary (B):** one decision label (D-002 as an explicit decision; its substance survived in the thesis). Everything else intact. Loss is cosmetic-but-real: a successor searching for "decisions taken" would not find bitcoin's enterprise-value treatment listed among them.
- **Transcript (C):** the most structurally consequential loss. All facts survived (13/13), but the *decision taxonomy* did not: D-001 (lending as #1 leading indicator), D-003 (frame as lending+operating-leverage, not fintech growth), and D-004 (stress case required before any buy thesis) were absent as decisions; the successor substituted its own framing and — critically — planned the stress test while dropping D-004's binding guardrail. Three assumptions (regulatory, bitcoin, 2028 targets) never appeared as assumptions at all, and all canonical confidence labels were replaced with self-inferred ones.

**Pattern:** facts survive every format; *governance* — decisions, rationale, confidence, guardrails — survives only where it is stated explicitly. The journal recorded the revision happening but never codified it as a decision; the successor reconstructed the narrative but not the constraints.

**Overhead.** Input sizes: WORLD 1,450 words / ~10.6KB; summary 1,241 words / ~8.4KB; transcript 1,054 words / ~7.3KB. WORLD's structuring overhead vs the summary was +209 words (+17%) and ~20 minutes of authoring for all three handoffs combined. Output sizes: WORLD 1,902 words; summary 2,785; transcript 2,863. The structured input produced the *shortest* faithful output — roughly 1,000 words fewer than either alternative — because the successor could reference and inherit structure rather than rebuild it in prose. Net token effect: WORLD's small input premium was more than repaid in output compression (est. ~1.3k extra input tokens vs ~1.2k fewer output tokens at ~0.75 words/token; output tokens are the more expensive ones in most APIs).

**Cost parity.** All three B runs completed in ~60 seconds with no browsing; no condition had a latency or budget advantage. Model, task, and evaluation were identical.

## 9. Limitations (read before citing this experiment)

1. **No true context isolation.** Subagents inherit the parent conversation; literal sandboxing of Agent A/B contexts was unavailable. Mitigation: strict scope instructions per run, identical briefs, separate runs. Cannot be fully ruled out that ambient context aided some runs.
2. **Same model family throughout.** Different A/B model families were unavailable; the result may not generalize across models.
3. **n=1, one task.** A single investment-research continuation. The result is evidence, not proof.
4. **Imperfect blinding.** Outputs X and Y opened with a sentence echoing their source handoff filename (an artifact of the spawn brief, not the handoff format). The evaluator stated it did not act on the filenames and the filename numbers do not map to conditions in any way visible to it; the mapping was disclosed only after scoring. Still, the blind was not pristine.
5. **Summary author wrote the state model too.** The summary (B) was authored by the same person who built the WORLD state (A), which may have made B unusually good — a genuinely independent summary-writer might do worse, which would widen the gap, or the author may have unconsciously favored A's structure.
6. **Answer key incompleteness.** Two evaluator-flagged "unsupported claims" turned out to be handoff-grounded (corrected in §7). The rubric itself was sound; the key needed the fix.

## 10. Recommendation

Proceed to **Experiment #002** with a harder design: a task with more decisions and longer revision history (where structure should matter more), an independent summary-writer, a genuinely different Agent B model if one becomes available, and a cleaner blind (strip filename echoes from outputs before grading). If #002 replicates this pattern — structured state preserves governance that narrative formats drop — begin prototyping the WORLD state layer with confidence.

The result supports WORLD's core claim narrowly but genuinely: **the value of a structured work-state is not in the facts it carries (all formats carried those) but in the constraints it preserves.** A successor that inherits facts without decisions is free to reconstruct the wrong ones.
