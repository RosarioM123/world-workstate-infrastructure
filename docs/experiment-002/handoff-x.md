# Agent A — Research Journal (Experiment #002, Phase 1)
**Company:** Intel Corporation (NASDAQ: INTC) | **Horizon:** 3–5 years
**Agent:** Agent A (Muse Spark) | **Date:** 2026-09-17
**Status note:** This is a raw, chronological, unedited working journal. Early takes are recorded as they were formed and explicitly marked where later evidence revised them. Dead ends and failures are included.

---

## 13:30 — Kickoff and framing

Task received: research Intel for a 3–5 year horizon. No valuation modeling, no buy/hold/sell, no code. Deliverables: this journal, a report, and a world_state.md following /tmp/world/docs/state-model.md.

Read the state model. Key mechanics I'll respect: decisions are immutable and superseded (never edited); state projects from an append-only log; every entity needs created_by/created_at/source basis.

[EARLY TAKE — naive, pre-research] Going in, my priors: (1) 18A is the make-or-break story and if Panther Lake ships on 18A the foundry turnaround is basically validated; (2) NVIDIA is the competitor that buried Intel in AI; (3) US government money de-risks the balance sheet. I am writing these down NOW so I can check them honestly later rather than pretending I always knew the nuances.

Also decided early: source hierarchy = SEC filings > Intel press releases > reputable press (Reuters etc.) > analyst commentary > aggregator/blog content. [DECISION D3 — source hierarchy]

Plan: batch 1 = 18A/Panther Lake status + Q2 2026 results + government stake + NVIDIA. Batch 2 = AI accelerators, dividend, TSMC JV, leadership. Batch 3 = fill gaps, verify.

---

## 13:45 — Batch 1 searches

Ran 3 searches in parallel:
- "Intel 18A Panther Lake status Q2 2026 results"
- "Intel Q2 2026 earnings revenue EPS foundry segment results"
- "US government Intel stake CHIPS 2025 2026 details"

### 18A / Panther Lake findings
Reuters (Oct 9, 2025): Panther Lake = first PC processor on 18A. Intel claimed CPU+graphics >50% above Lunar Lake. Production ramping 2025, broad availability from Jan 2026. 18A brings new transistor design (RibbonFET) + backside power delivery (PowerVia). https://www.reuters.com/business/intel-outlines-details-first-pc-chip-made-its-new-manufacturing-tech-2025-10-09/

So the "5 nodes in 4 years" story actually landed. My early take D1 forming: "treat 18A Panther Lake ramp as the primary evidence of process turnaround." Recorded as DECISION D1 (accepted at the time).

But — cautionary counter-evidence in the same batch: a PCGamer piece citing Reuters sources: 18A yield allegedly ~10% (up from 5%), and CFO David Zinsner said Panther Lake would NOT initially be accretive even once yields support volume. Intel never confirmed the yield number. https://www.pcgamer.com/hardware/processors/intels-bad-news-year-rolls-on-as-new-18a-chip-manufacturing-node-is-reportedly-in-trouble-with-10-percent-yields-and-doubts-over-profitability-of-the-panther-lake-cpu/

So: 18A works technically (products exist) but economics are unproven. Noted the tension. 10% figure is anonymous-source only — do NOT treat as fact.

### Q2 2026 results (reported July 23, 2026)
Intel press release via Nasdaq: Revenue $16.1B (+25% YoY). GAAP EPS $(2.16). Non-GAAP EPS $0.42. Q3 guide: rev $15.8–16.8B, non-GAAP EPS $0.38. https://www.nasdaq.com/press-release/intel-reports-second-quarter-2026-financial-results-2026-07-23

Other figures from coverage: non-GAAP gross margin 41.8%; operating cash flow $7B; cash + short-term investments ~$30B; CCPG (client) $8.9B; DCAI $6.3B (+59% YoY); Foundry $5.8B (mostly internal). https://www.businesswire.com/news/home/20260723707213/en/Intel-Reports-Second-Quarter-2026-Financial-Results and https://news.alphastreet.com/intel-corporation-intc-q2-2026-earnings-call-transcript/

Big flag: GAAP net loss ~$11B in the same quarter non-GAAP prints +$0.42. The bridge needs investigation before I say anything about financial health. Marked as open item.

### Government stake
Reuters (Aug 29, 2025): Intel amended CHIPS agreement, got ~$5.7B early. Remaining guardrails: dividends/buybacks restricted, certain change-of-control deals restricted, expansion in specified countries restricted. Intel issued 274.6M shares to the government; option for up to 240.5M more under conditions. Total government investment described as $8.9B + $2.2B previously = $11.1B; ~9.9% stake. CFO framed it as incentive to retain foundry control. https://www.reuters.com/technology/intel-amends-chips-act-deal-with-us-commerce-department-gets-57-billion-early-2025-08-29/?ref=bytenewsdaily.com

Intel's own announcement: 433.3M primary shares at $20.47 = 9.9% passive stake, no board seats, 5-year warrant at $20/share for another 5% exercisable ONLY if Intel ceases to own ≥51% of foundry; clawback/profit-sharing on the earlier $2.2B grant eliminated. https://businesswire.com/news/home/20250822458848/en/Intel-and-Trump-Administration-Reach-Historic-Agreement-to-Accelerate-American-Technology-and-Manufacturing-Leadership

My early take was "government support de-risks Intel" [DECISION D4, recorded]. But the warrant structure + guardrails already make me uneasy: this is also a structural barrier to ever separating the foundry, plus dilution. Parking the revision until I've seen more.

Doubt noted: is the $11B GAAP loss connected to the escrowed government shares? The warrant/escrow language suggests mark-to-market somewhere. Must check the earnings reconciliation.

---

## 14:30 — Batch 2 searches

Ran 3 searches in parallel:
- "Intel NVIDIA partnership $5 billion investment custom x86"
- "Intel Falcon Shores Jaguar Shores Gaudi AI accelerator cancelled"
- "Intel dividend history suspended 2024 2025"

### NVIDIA partnership
TechCrunch (Sep 18, 2025): NVIDIA to invest $5B in Intel common stock at $23.28/share (pending approvals). Multi-generation NVLink-connected data-center + PC products. Intel builds custom x86 CPUs for NVIDIA AI infrastructure; Intel builds PC SoCs integrating NVIDIA RTX GPU chiplets. https://techcrunch.com/2025/09/18/nvidia-buys-5-billion-stake-in-intel-planning-ai-chip-collaboration/

Reuters analyst take: strategically significant for Intel, potentially threatening to AMD. https://www.reuters.com/world/asia-pacific/view-nvidias-5-billion-bet-intel-2025-09-18/

[EARLY TAKE — recorded as DECISION D2]: I had framed NVIDIA as purely the competitor that ate Intel's lunch in AI. That framing is now wrong or at least incomplete: NVIDIA is an investor and product partner. Need to revise: NVIDIA = dominant competitor AND strategic partner. The partnership does NOT prove Intel has a standalone accelerator story — it arguably confirms the opposite (Intel needs NVIDIA's GPU IP for the PC SoC). Recorded assumption A2 → flagged for revision.

### AI accelerators — worse than I expected
TechTarget: Falcon Shores cancelled as a commercial product, kept as internal test chip. https://www.techtarget.com/searchdatacenter/news/366618595/Intel-axes-Falcon-Shores-amid-market-challenges
Tom's Hardware: shift to Jaguar Shores + rack-scale systems. https://www.tomshardware.com/tech-industry/artificial-intelligence/intel-cancels-falcon-shores-gpu-for-ai-workloads-jaguar-shores-to-be-successor

So my early instinct to evaluate Intel as a would-be merchant GPU challenger [DECISION D7 — evaluate AI via Falcon/Jaguar Shores GPUs] is looking wrong. Gaudi sales/software described as disappointing. The honest frame: Intel's near-term AI exposure runs through Xeon CPUs, AI PCs, ASICs, packaging/foundry, and now NVIDIA-linked products. Recording D7 but expecting to supersede it.

### Dividend
TheStreet: dividend suspended starting Q4 2024 to preserve liquidity. https://www.thestreet.com/investing/stocks/intel-dividends
Barchart: still no dividend by 2026; long-term debt >$43B; stock up ~6x from 2025 lows (~$100); forward P/E cited at 66 (aggregator — treat with caution). https://www.barchart.com/story/news/2389397/intel-stock-has-risen-sixfold-from-its-2025-lows-but-dont-expect-a-dividend-yet

[DECISION D9]: assume dividend = 0 in any Phase 2 base case unless primary-source evidence of reinstatement. The CHIPS guardrails independently restrict dividends, so this is over-determined.

Note: stock ~$100 in Sept 2026, up ~400% from 2025 lows, near all-time highs, forward P/E ~66 — the market is already pricing a successful turnaround. That raises the bar for the thesis; worth flagging in the report even though valuation is out of scope. (The P/E figure is from a secondary aggregator; confidence medium-low.)

---

## 15:15 — Batch 3: foundry external customers, TSMC JV, leadership

Searches:
- "Intel foundry external customers 2026 Microsoft Amazon 14A"
- "TSMC Intel foundry joint venture 2025"
- "Intel CEO Lip-Bu Tan strategy 2025 2026 Gelsinger"

### Foundry external validation — the key finding of the day
EE Times (Aug 2026): "Intel Foundry improves execution but external customers remain the test." Internal product demand improves utilization/yield/cost but does NOT prove outside customers prefer Intel Foundry. https://www.eetimes.com/intel-foundry-improves-execution-but-external-customers-remain-the-test/

Fool (Aug 9, 2026): Fortinet = first named outside customer under Lip-Bu Tan — but on Intel 4 (a 2021-era node) for Security Processor 6. Not an 18A/14A leading-edge validation. https://www.fool.com/investing/2026/08/09/intel-foundry-lands-a-major-new-client-worth-watch/

Fool (Jan 2026): "make-or-break foundry moment" — essentially all foundry revenue internal. https://www.fool.com/investing/2026/01/26/intels-make-or-break-foundry-moment-arrives-this-y/

CRN: future of foundry "hinges on a significant external customer"; Intel warned it may pause/discontinue 14A and successor nodes without one. https://www.crn.com/news/components-peripherals/2025/intel-future-of-foundry-business-hinges-on-a-significant-external-customer

EE Times (Oct 2025): Clearwater Forest / Xeon 6+ on 18A, first-half 2026. https://www.eetimes.com/intels-confidence-shows-as-it-readies-new-processors-on-18a/

[REVISION — this is R1] My D1 ("18A ramp = foundry turnaround validated") is now under direct pressure. The right decomposition: 18A technical/product execution (Panther Lake shipping, Clearwater Forest) is real; merchant-foundry commercial validation is NOT — essentially all foundry revenue is internal, the only named external customer is on an old node. Recording ASSUMPTION REVISION R1: old "18A success validates the foundry turnaround" → new "18A may validate internal execution; the true commercial test is a significant external 14A customer commitment." D1 will need supersession by a joint-KPI decision.

[DECISION D5]: explicitly separate internal 18A execution from external foundry validation in all downstream analysis.

### TSMC JV
Reuters (Mar 12, 2025): TSMC pitched NVIDIA, AMD, Broadcom (and reportedly Qualcomm) on a JV to operate Intel's factories; TSMC would run operations but own ≤50%; talks early-stage, encouraged by the US administration; all parties declined comment. Intel 2024 net loss $18.8B (first since 1986); foundry PP&E book value $108B at 12/31/2024. https://www.reuters.com/technology/tsmc-pitched-intel-foundry-jv-nvidia-amd-broadcom-sources-say-2025-03-12/?ref=bigtechdigest.com

Note: the August 2025 government stake + warrant (5% more if Intel drops below 51% foundry ownership) materially complicates any such JV/breakup now. Treat JV as rumor, not base case. No later developments found in this session — open question.

### Leadership
Lip-Bu Tan became CEO March 18, 2025 (replacing Gelsinger). Reports: ~15% core workforce cut, target ~75,000 core employees end-2025 vs ~109,000 end-2024; opex targets ~$17B (2025) / $16B (2026); Germany and Poland projects cancelled/paused; Ohio slowed; $1.9B restructuring costs in one Q2 period. https://www.entrepreneur.com/business-news/intel-is-laying-off-thousands-of-staff-as-part-of-turnaround/495070 ; https://www.nbcpalmsprings.com/business-finance-and-tech/2025/07/24/intel-cuts-15-of-workforce-in-major-restructuring-under-new-ceo ; https://www.crn.com/news/components-peripherals/2025/intel-to-cut-operating-expenses-by-1-5-billion-through-next-year

Gelsinger exit details still needed — parked for next batch.

Doubt: layoffs of this scale cut costs but also risk hollowing out execution capability. The 18A ramp happening simultaneously is either evidence the cuts didn't break execution, or evidence the remaining team is stretched. Can't resolve from press; note as tension.

---

## 16:20 — Batch 4: Gaudi details, server share, equity raise

Searches:
- "Intel Gaudi AI accelerator sales 2025 2026 SynapseAI discontinued"
- "Intel stock price September 2026 $20 billion equity raise"
- (third slot used to re-check foundry external split)

### Gaudi / AI software
Confirmed: Falcon Shores cancelled as product (kept as test chip); Jaguar Shores = future rack-scale focus; Gaudi 3 missed its $500M revenue goal; SynapseAI software discontinued. Intel acknowledged silicon alone insufficient — needs full rack-scale solution.

[DECISION D6 — supersedes D7]: evaluate Intel's AI participation through Xeon CPUs, AI PCs, ASICs, packaging/foundry services, and NVIDIA-linked products — NOT as a near-term merchant GPU challenger to NVIDIA. Marking D7 SUPERSEDED (history retained).

### The $20B equity raise — did not see this coming
ainvest (Sept 2026, ~11 days old): Intel raised $20B selling ~210.5M new shares at $95 in August 2026 — "one of the largest equity raises in chip-industry history"; ~4–5% dilution; proceeds aimed at tooling fab shells for 14A (~$25B equipment per analyst estimates); 2026 capex raised above $20B; 2027 "significantly above." https://www.ainvest.com/news/intel-foundry-funding-absorption-test-dilution-funded-turnaround-2609/

Caveat: ainvest is a low-credibility aggregator. The specifics (210.5M shares × $95 = $20B) are suspiciously round and I could not corroborate with a primary source in this session. Treat as medium-low confidence; Phase 2 must verify against SEC filings. BUT the directional point — Intel is funding the foundry buildout with equity dilution, not debt — is consistent with the debt load and dividend suspension. [DECISION D14]: treat foundry funding as dilution-funded; Phase 2 share-count work must capture cumulative dilution (government 433.3M + NVIDIA 214.7M + this raise + SoftBank).

Also from the same piece: external foundry revenue was only $293M of $5.8B in Q2 2026 (~5%), up from $174M in Q1; part of even that is Altera (which Intel was selling — odd, flagged). Foundry op margin improved from -71.7% to -36.2% YoY — but on internal volume, not merchant traction.

Wait — I need to double-check the $293M figure against a better source before leaning on it. Adding to next batch.

---

## 17:10 — Batch 5: verify external foundry split + AMD share + NVIDIA close

Searches:
- "Intel Foundry external customer revenue breakdown separate from internal 2026"
- "AMD EPYC server CPU market share vs Intel Xeon 2026"

### External split — VERIFIED via multiple outlets
Motley Fool (Aug 11, 2026): external customers supplied just $293M of the foundry's $5.8B Q2 revenue; "internal revenue can only prove the factories work. It can't prove the business does." https://www.fool.com/investing/2026/08/11/intels-foundry-grew-31-last-quarter-and-lost-21-bi/
EE Times: same $293M figure, attributed to CFO David Zinsner. https://www.eetimes.com/intel-foundry-improves-execution-but-external-customers-remain-the-test/
industry-blog: full-year 2025 external revenue just $307M vs $17.8B total foundry revenue and a $10.3B operating loss; Q1 2026 external $174M. TSMC 72% foundry share. https://industry-blog.com/intel-foundry-revenue-external-customers/

This is now the single most important fact in the research: ~95% of "foundry revenue" is Intel selling wafers to itself. Any analysis that compares Intel Foundry revenue to TSMC's merchant revenue is apples-to-oranges. [GUARDRAIL G1 forming.]

Additional color from Fool: Intel says it is SUPPLY CONSTRAINED — data-center customers demanding more chips than Intel can produce; DCAI growth strongest on record; Xeon 6 one of fastest-ramping products; AI PC revenue +26% sequentially = 2/3 of client mix. Bullish demand signal, but supply constraint can also reflect underinvestment after years of capex discipline. Noted both readings.

### AMD server share (Mercury Research)
Q2 2026: AMD server unit share 34.5% (from 27.3% YoY); Xeon SP vs EPYC head-to-head AMD at 46.4%. https://www.webpronews.com/amd-crosses-30-client-cpu-share-as-soaring-memory-costs-crush-desktop-shipments/
Q1 2026: AMD server REVENUE share record 46.2% (units 33.2%) — AMD winning the high-value mix. https://www.techspot.com/news/112419-amd-keeps-gaining-intel-servers-but-desktop-pcs.html ; https://www.theregister.com/systems/2026/06/04/amd-takes-a-third-of-server-cpu-market-as-shipments-grow/5251283
Client: AMD 30.7% units Q2 2026 (Intel 70.4%); overall x86 revenue share 38.1%.

[DECISION D11]: use revenue share as the primary competitive metric (it captures mix/ASP where AMD is winning fastest), with unit share as context. Intel still leads but the trajectory is adverse.

### NVIDIA $5B — CLOSED
Reuters (Dec 29, 2025): NVIDIA completed purchase — 214.7M+ shares at $23.28 in a private placement, ~4% position. https://www.reuters.com/legal/transactional/nvidia-takes-5-billion-stake-intel-under-september-agreement-2025-12-29/
Reuters (Dec 19, 2025): US antitrust (FTC) cleared the investment. https://www.reuters.com/sustainability/boards-policy-regulation/nvidia-intel-deal-cleared-by-us-antitrust-agencies-2025-12-19/

So the NVIDIA leg is done and closed, not pending. [REVISION R2 confirmed]: A2 → A2' (competitor + partner/investor). BusinessQuarter notes early joint development under way, pilot hardware late 2026 — secondary source, medium-low confidence on timing.

---

## 18:00 — FAILED APPROACH #1: 18A yield verification

I attempted to verify the 18A yield figures against an official Intel disclosure — searching "Intel 18A yield rate disclosure official 2026". 

Result: FAILURE. Intel has never publicly disclosed node-level yield numbers for 18A. What I found instead:
- The original 10% claim: anonymous sources via Reuters, never confirmed by Intel (PCGamer piece).
- GF Securities analyst Jeff Pu (via wccftech, Sept 2026): 18A yields ~80% on Panther Lake; 14A risk production pulled to Q1 2027; 14A capacity 6K wpm 2027 → 24K wpm 2028. https://wccftech.com/intel-14a-production-capacity-tipped-to-sit-at-6000-wafers-per-month-by-2027-end-with-18a-yields-at-80-says-analyst/
- CEO Lip-Bu Tan via CNBC (TrendForce, May 2026): 18A yields improving 7–8% per month; expects multiple foundry customer commitments in 2H 2026; CFO Zinsner: external signals "more concrete" in 2H 2026–early 2027. https://www.trendforce.com/news/2026/05/19/news-intel-18a-yields-improve-7-8-monthly-with-2h26-customers-expected-reportedly-pushes-18a-cpus-amid-tight-supply/
- Syndicated low-quality content (financialcontent "tokenring"/"marketminute" articles): 65–75% yields, Fab 52 40K wpm, Apple/NVIDIA interest — these read as AI-generated sponsored content; I am NOT relying on them. Flagging as unreliable.

Why it failed: node yields are among the most closely guarded figures in semiconductors; Intel discloses yield *direction* (via cost/margin commentary) but not levels. The honest position: yield economics are unobservable from outside; triangulate via (a) management cost commentary (Panther Lake cost down ~50% YTD per Fool), (b) foundry margin trajectory (-71.7% → -36.2%), (c) whether external customers sign. This failure is itself a finding: any Phase 2 thesis that depends on a specific yield number is building on sand.

Related open question: the "multiple foundry customers in 2H 2026" — we're now past mid-September 2026; have any been named besides Fortinet (Intel 4)? Not found in this session. Watch item.

---

## 18:45 — Batch 6: Gelsinger exit, balance sheet, GAAP bridge, Altera/SoftBank

Searches:
- "Pat Gelsinger retired Intel December 2024 board ousted CEO details"
- "Intel debt cash balance sheet mid-2026 total debt long-term debt"
- "Intel Q2 2026 GAAP loss adjustments restructuring impairment charges explanation"
- "Intel Altera sale Silver Lake completed 2025 SoftBank $2 billion investment Intel"

### Gelsinger exit — confirmed details
Intel press release (Dec 2, 2024): Gelsinger "retired" effective Dec 1, 2024, stepped down from board; interim co-CEOs David Zinsner (CFO) + Michelle Johnston Holthaus (newly created CEO of Intel Products); Frank Yeary interim executive chair. https://www.businesswire.com/news/home/20241202016400/en/Intel-Announces-Retirement-of-CEO-Pat-Gelsinger
Bloomberg (via Engadget/TechCrunch): board gave Gelsinger the option to retire or be removed — i.e., pushed out after the Aug 2024 earnings disaster, dividend suspension, 15% layoffs, >50% stock decline under his tenure. https://www.engadget.com/big-tech/intels-ceo-pat-gelsinger-has-suddenly-retired-151410215.html?guccounter=1 ; https://techcrunch.com/2024/12/02/intel-ceo-pat-gelsinger-retires/

Assessment: the board explicitly re-centered the product group ("put our product group at the center of all we do" — Yeary). Gelsinger's IDM 2.0/foundry-first capital allocation is being re-underwritten by Tan with harder commercial gating (the 14A external-customer ultimatum). This is a genuine strategy discontinuity, not just a CEO swap. Key-person risk now concentrates on Tan.

### Balance sheet (6/30/2026, via Zacks/Barchart — secondary, needs 10-Q verification)
Long-term debt $48.549B; short-term debt $1.988B; cash & equivalents $12.874B; marketable securities $16.853B. https://www.zacks.com/stock/quote/INTC/balance-sheet ; https://www.barchart.com/stocks/quotes/INTC/balance-sheet/quarterly

So: gross debt ~$50.5B; cash + short-term investments ~$29.7B (≈ the "$30B liquidity" figure); NET debt ≈ $20.8B. [DECISION D10]: analyze leverage on net debt, not gross; treat the $30B liquidity as real but encumbered (capex, restructuring, CHIPS guardrails).

Notable: LT debt jumped $43.0B → $48.5B quarter-over-quarter (+$5.5B). Financing activity in Q2 2026 needs a look in Phase 2. FAILED APPROACH #2 (partial): I tried to get primary-source 10-Q MD&A text on debt maturities and the financing flow — search returned aggregator balance-sheet tables instead of filing narrative. Primary verification is unfinished Phase 2 work. The aggregators agree with each other (Zacks, Barchart, MarketBeat all show the same figures), so I'm treating the numbers as medium-high confidence but the maturity schedule as unknown.

### GAAP loss bridge — SOLVED
Q2 2026 earnings release reconciliation: GAAP net loss attributable to Intel $(11,033)M → non-GAAP net income $2,197M. The dominant adjustment: "(Gains) losses on mark-to-market of Escrowed Shares" = $12,529M ($2.45/share). Restructuring only $170M in-quarter; SBC $687M. https://www.businesswire.com/news/home/20260723707213/en/Intel-Reports-Second-Quarter-2026-Financial-Results

So the $11B GAAP loss is dominated by a NON-CASH mark-to-market on the escrowed government shares (the stock ran up, the escrowed-share liability got marked). This also explains why non-GAAP EPS is +$0.42. [DECISION D8]: treat GAAP net income as non-informative for operating health without the bridge; anchor on non-GAAP + cash flow — while noting that the MTM charge is a real economic cost of the government deal structure (dilution overhang is real even if non-cash this quarter).

Also from the release: Q2 operating cash flow $7.006B; gross capex $2.652B; "adjusted free cash flow" $(8.419)B (after partner contributions and other adjustments — the reconciliation has a large $(12.216)B "partner contributions, net" line I don't fully understand; flagged). Q3 2026 outlook: GAAP EPS $0.31, non-GAAP $0.38; FY2026 GAAP opex $23.0B vs non-GAAP $16.5B (SBC $2.1B, restructuring $4.3B).

Also useful: SEC 10-Q (intc-20260627) MD&A: gross profit drivers included absence of $797M Q2-2025 impairment/accelerated depreciation on manufacturing assets "with no remaining operational use," absence of Gaudi inventory charges, and $226M lower reserves from sell-through of 18A early-ramp inventory reserves. https://www.sec.gov/Archives/edgar/data/50863/000005086326000157/intc-20260627.htm — this is primary-source color that 18A cost/yield is genuinely improving.

### Altera + SoftBank — confirmed announced, completion unclear
Altera: Silver Lake 51% at $8.75B valuation (~$3.4–4.5B cash to Intel per various reports), Intel retains 49%, expected close H2 2025, deconsolidation planned; Raghib Hussain (ex-Marvell) CEO. https://techcrunch.com/2025/04/14/intel-agrees-to-sell-controlling-stake-in-altera-chip-business/?rand=7247/ ; https://www.eetimes.com/intel-sells-majority-stake-in-altera-to-silver-lake/

SoftBank: definitive $2B agreement at $23/share, announced Aug 18, 2025, "customary closing conditions." https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-25-000126/0000050863-25-000126.pdf

Neither completion was confirmed in this session's research → OPEN QUESTIONS Q1/Q2. The Altera one matters: one source claimed part of Q2 2026 external foundry revenue "is Altera, a chip business Intel itself owns" — if the sale closed, that framing is stale; if it didn't, the external revenue is even less third-party than it looks.

---

## 20:30 — Synthesis: the three revisions

Writing them out explicitly because the experiment demands it:

**R1 — Foundry validation.** OLD (A1, ~13:30): "18A technical success (Panther Lake shipping) validates the foundry turnaround." → NEW (A1'): "18A validates internal process/product execution; it does NOT validate the merchant foundry business. ~95% of foundry revenue is internal ($293M external of $5.8B, Q2 2026). The true commercial test is a significant external 14A customer commitment — the thing Intel itself says 14A's continuation depends on." Trigger evidence: EE Times/Fool/industry-blog external-split reporting.

**R2 — NVIDIA.** OLD (A2, ~13:30): "NVIDIA is purely the competitor that buried Intel in AI." → NEW (A2'): "NVIDIA is both the dominant AI-accelerator competitor AND a strategic partner/investor ($5B stake closed Dec 29, 2025; joint NVLink products; custom x86 for NVIDIA infra; RTX-integrated PC SoCs). The partnership improves Intel's CPU/PC relevance but underscores — not cures — the standalone accelerator gap." Trigger evidence: Reuters Dec 2025 closing reports.

**R3 — Government.** OLD (A3, ~13:30): "Government equity support de-risks the foundry." → NEW (A3'): "Support strengthens liquidity and strategic durability (too-important-to-fail dynamics, $5.7B early CHIPS cash) but adds ~9.9% dilution + warrant overhang, dividend/buyback/change-of-control guardrails, political dependence, and a structural barrier to foundry separation (warrant triggers if Intel drops below 51% foundry ownership). Net: asset AND constraint." Trigger evidence: Reuters CHIPS amendment + Intel announcement terms.

Decisions D1 and D7 are now SUPERSEDED (D1 by D12 joint-KPI; D7 by D6 AI-framing). History retained below.

**D12 (supersedes D1):** the foundry investment KPI is JOINT: (a) 18A internal yield/cost trajectory AND (b) 14A external customer commitment. Neither alone suffices.
**D13 (depends on D5):** Phase 2 guardrail — never credit internal foundry revenue as merchant validation. Rationale explicitly depends on D5's separation of internal execution from external validation.

Remaining gaps for Phase 2 (not failures, just unfinished): primary 10-Q verification of balance sheet/maturities; Altera/SoftBank completion; TSMC JV status post-Mar-2025; names of 2H-2026 foundry customers; Ohio fab timeline; Lip-Bu Tan background depth; Gaudi wind-down completion; client TAM detail.

---

## 21:00 — Journal closed; writing report + world_state

Complexity checklist before writing:
- Decisions ≥10: D1–D14 (14 total), each with evidence + rationale ✓
- Assumptions ≥10 with confidence: A1'–A13 (13) ✓
- Revisions ≥3: R1, R2, R3 ✓
- Superseded decisions ≥2: D1, D7 ✓
- Guardrails ≥2: G1–G4 ✓
- Supporting + contradicting evidence for ≥2 decisions: D5 (18A execution real vs yield-doubt reports), D12/A1' (foundry margin improvement vs 95% internal), R2/NVIDIA decision (partnership vs competition) ✓
- Open questions ≥3: Q1–Q6 ✓
- Failed approach: FA1 (18A yield official disclosure), FA2 (primary 10-Q debt narrative) ✓
- Decision depending on earlier decision: D13 depends on D5 ✓
- URLs for every important claim ✓

One more honesty note: several figures (forward P/E 66, $20B raise specifics, Ireland SCIP, TSMC 72% share, OFCF -$2.5B Q1 2026) come from secondary/weak sources and are marked as such in the report. I did not invent or smooth any numbers.
