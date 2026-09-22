# WORLD State Bundle - Disney (DIS) replication, Agent A Phase 1

Schema: docs/state-model.md (Draft v0.1). Project: Experiment #002 Day 6 Disney replication, Agent A research.
created_by: agent::disney-agent-a | created_at: 2026-09-22

## Project

- id: P-DIS-001
- name: Disney (DIS) replication, Agent A Phase 1 research
- goal: Produce research findings, assumptions, decisions, and evidence on The Walt Disney Company (3-5 year horizon) sufficient for a Phase 2 successor to complete valuation and recommendation.
- scope: Public sources only. In scope: streaming economics, parks and experiences, linear networks and sports rights, studio slate, financial health, competitive position, leadership succession, recent M&A/partnerships. Out of scope: valuation modeling, buy/hold/sell recommendation, application code.
- constraints: [G1, G2, G3] (see Guardrails)
- definition_of_done: Journal, final report, and this state bundle written; complexity targets met; no invented numbers; conflicts disclosed.
- status: completed (Phase 1)

## Decisions

- id: D1 | statement: Phase 1 is research only; no valuation modeling and no buy/hold/sell recommendation. | rationale: Protocol scope boundary; prevents premature conclusions before Phase 2 modeling. | status: accepted | evidence_ids: [] | dependencies: []
- id: D2 | statement: Treat the streaming-margin inflection as the core 3-5 year profit thesis. | rationale: It is the largest single P&L change vs the 2022-23 base case: from ~$4B annual streaming losses (FY2022) to 10%+ operating margins (FY2026). | status: accepted | evidence_ids: [E1, E2, E3] | dependencies: []
- id: D3a | statement: Model domestic parks as attendance-led volume growth. | rationale: Historical pattern at time of writing. | status: superseded (supersedes nothing; superseded by D3b) | evidence_ids: [] | dependencies: []
- id: D3b | statement: Treat domestic parks growth as pricing/per-cap-spend led, attendance flat to modest. | rationale: Three quarters of data show operating income growing on flat-to-down attendance (Q2 FY2026 attendance -1% with OI +5%; Q3 FY2026 per-cap spend +4-5%). | status: accepted | evidence_ids: [E2, E4, E5] | supersedes_id: D3a | dependencies: []
- id: D4 | statement: Treat ESPN DTC as a strategic option with unproven net economics; do not assume it offsets linear decline one-for-one. | rationale: Launch bundle pricing ($29.99/month) and pay-TV affiliate-fee cannibalization are undisclosed; linear networks OI fell 21% YoY in fiscal Q4 2025. | status: accepted | evidence_ids: [E6, E7] | dependencies: []
- id: D5 | statement: Exclude Abu Dhabi from capex modeling; model only royalty revenue. | rationale: Disney's own disclosure: zero-capex license structure, Miral funds/builds/operates, Disney provides creative design and oversight. | status: accepted | evidence_ids: [E8] | dependencies: []
- id: D6 | statement: Carry the WBD acquisition as an unresolved competitive overhang; no point forecast. | rationale: Source conflict between the Dec 2025 Netflix deal and the Feb 2026 Paramount Skydance board recommendation; honesty over precision. | status: accepted | evidence_ids: [E9, E10] | dependencies: []
- id: D7 | statement: Carry the Epic Games stake as option value, not as a thesis pillar. | rationale: No launch date and no metrics since the Feb 2024 announcement; extends the D2 framing of engagement-driven growth but cannot anchor it. | status: accepted | evidence_ids: [E11] | dependencies: [D2]
- id: D8 | statement: Treat dividend ($1.50/share) plus raised buyback (to at least $9B FY2026) as shareholder-return discipline that supports downside, not as a growth driver. | rationale: Capital-return programs reflect maturity, not expansion; buyback funded by ~$10B FY2026 FCF guidance. | status: accepted | evidence_ids: [E12, E13] | dependencies: []
- id: D9 | statement: Score the succession as reducing execution risk vs an external hire, but flag Iger's continued presence through Dec 31, 2026 as residual transition risk. | rationale: Unanimous board vote and continuity team (Walden, Bergman, Pitaro); Iger remains senior advisor. | status: accepted | evidence_ids: [E14, E15] | dependencies: []
- id: D10 | statement: Constrain franchise reliability: do not assume Star Wars or live-action remakes are automatic theatrical hits in any Phase 2 model. | rationale: The Mandalorian and Grogu ($345.2M, lowest-grossing live-action Star Wars) and live-action Moana (~$263M gross vs ~$250M budget); mirrors D3b's pattern of evidence overriding a prior on franchise strength. | status: accepted | evidence_ids: [E16, E17] | dependencies: [D3b]
- id: D11 | statement: Use FY2026 management guidance (double-digit adjusted EPS growth FY26/FY27, $19B operating cash flow) as the public-anchor baseline, not as fact. | rationale: It is the market's reference point; testing it is Phase 2's job. | status: accepted | evidence_ids: [E4] | dependencies: []

## Assumptions

- id: A1 | statement: Streaming margin trajectory continues upward (FY2026 target 10%, from ~5% in FY2025). | confidence: high | status: active
- id: A2 | statement: Parks growth is driven by per-cap spend and pricing, not attendance volume, over the 3-5 year horizon. | confidence: high | status: active
- id: A3 | statement: Domestic linear networks decline continues at a similar pace (double-digit annual OI decline). | confidence: medium | status: active
- id: A4 | statement: ESPN DTC is net positive to segment economics once past launch investment. | confidence: medium | status: active
- id: A5 | statement: Star Wars and live-action remakes cannot be assumed automatic theatrical hits. | confidence: high | status: active
- id: A6 | statement: D'Amaro-led Disney continues Iger's four strategic priorities with no sharp pivot. | confidence: medium | status: active
- id: A7 | statement: The Abu Dhabi resort requires no Disney capex (pure royalty model). | confidence: high | status: active
- id: A8 | statement: The Epic Games universe ships within the 3-5 year horizon and becomes a material engagement channel. | confidence: low | status: active
- id: A9 | statement: Debt remains investment-grade and declining; no refinancing stress. | confidence: medium | status: active (stale risk: single third-party source; verify from 10-K)
- id: A10 | statement: The buyback program ($7B raised to at least $9B for FY2026) is executed as announced. | confidence: medium | status: active

## Revisions

- id: R1 | old: Streaming is a drag on earnings. | new: Streaming is a sustained profit engine with 10%+ margins. | trigger: Q2 and Q3 FY2026 streaming OI ($582M +88%, then $712M at 13% margin) vs FY2022 ~$4B annual losses. | evidence_ids: [E1, E2, E3]
- id: R2 | old: Iger remains CEO with unresolved succession. | new: D'Amaro named CEO effective March 18, 2026; succession resolved with a continuity team. | trigger: Feb 3, 2026 Disney board announcement; D'Amaro's May 2026 earnings debut (+7-8% stock pop). | evidence_ids: [E14, E15]
- id: R3 | old: Epic Universe will take meaningful share from Disney World. | new: Epic Universe is real but Disney's attendance is holding; growth is pricing-led. | trigger: Fiscal Q3 2026 global attendance +3%; MoffettNathanson ~1M-visitor impact estimate; Disney CFO's minimal-impact comments. | evidence_ids: [E5, E18, E19]

## Guardrails

- id: G1 | statement: Do not build a buy/hold/sell recommendation on third-party research notes alone; verify debt, segment OI, and cash flow from Disney's own 10-K/10-Q before modeling.
- id: G2 | statement: Do not impute per-service subscriber counts; Disney stopped disclosing them. Work from revenue, OI, and ARPU lines only.
- id: G3 | statement: Conflicting claims (notably the WBD acquisition status) must be disclosed as conflicts, never averaged or silently picked.

## Open Questions

- id: Q1 | question: What is the actual current status and eventual owner of WBD's studio/streaming assets, and what does the combined entity mean for Disney's streaming competition? | status: open
- id: Q2 | question: What are D'Amaro's own strategic priorities, if any differ from Iger's four? | status: open
- id: Q3 | question: What is the net cannibalization of ESPN DTC on pay-TV affiliate fees over 3-5 years? | status: open
- id: Q4 | question: Will the raised $9B FY2026 buyback be fully executed, and at what average price? | status: open
- id: Q5 | question: When does the Disney-Epic universe launch, and on what commercial terms does it monetize? | status: open

## Failed Approaches

- id: FA1 | approach: Searched for D'Amaro-era strategic pillars distinct from Iger's four priorities. | result: Not found; sources through September 2026 still quote Iger's framework (studio quality, streaming profitability, ESPN digital, Experiences growth). Left as Q2.
- id: FA2 | approach: Attempted to verify current per-service subscriber counts for Disney+ and Hulu. | result: Not possible; Disney stopped disclosing them. Last verifiable combined figure: 195.7-196M (fiscal Q4 2025). Adopted G2.

## Evidence

- id: E1 | kind: source | reference: https://www.ainvest.com/news/disney-streaming-longer-problem-valuation-gap-2607/ | summary: Streaming OI +88% to $582M in Q2 FY2026, first quarter above 10% margin; full-year target at least 10%. | captured_by: agent::disney-agent-a
- id: E2 | kind: data | reference: https://momoview.com/blog/en/posts/disney-dis-q2-fy2026-earnings-25-17b-revenue-up-7-adj-eps-1-57-streaming-oi-582m-up-88-experiences-2-62b-record-buyback-raised-to-8b/ | summary: Q2 FY2026 recap: streaming OI $582M (+88%), Experiences OI $2.62B (Q2 record), domestic attendance -1%, growth from per-cap spend, sports OI guided down. | captured_by: agent::disney-agent-a
- id: E3 | kind: source | reference: https://thedesk.net/2026/08/disney-fiscal-q3-calendar-q2-2026-earnings-report/ | summary: Q3 FY2026: revenue $25.25B (+7%), segment OI $5.56B (+21%); subscription streaming revenue $5.53B (+11%), ad revenue $851M (+3%). | captured_by: agent::disney-agent-a
- id: E4 | kind: data | reference: https://www.businesswire.com/news/home/20260202165935/en/The-Walt-Disney-Company-Reports-First-Quarter-Earnings-for-Fiscal-2026 | summary: Q1 FY2026: Experiences revenue $10.0B, OI $3.3B; FY2026 guidance: double-digit adjusted EPS growth, $19B operating cash flow, $9B capex, $7B buyback (later raised). | captured_by: agent::disney-agent-a
- id: E5 | kind: source | reference: https://www.wdwinfo.com/news-stories/disney/disney-reports-strong-q3-earnings-fueled-by-parks-streaming-and-toy-story-5/ | summary: Q3 FY2026: Experiences revenue ~$10B, OI up 20% to $3.02B; global attendance +4%, domestic +3%, ticket revenue per guest +5%; cruise capacity +50% from new ships. | captured_by: agent::disney-agent-a
- id: E6 | kind: source | reference: https://espnpressroom.com/feature/espn-dtc-launch-nfl-wwe-deals/ | summary: ESPN DTC launched Aug 21, 2025 ($29.99/month, all ESPN networks); ESPN acquiring NFL Network and RedZone; NFL taking 10% equity stake in ESPN; WWE PLEs exclusive to ESPN from 2026. | captured_by: agent::disney-agent-a
- id: E7 | kind: source | reference: https://www.sportsbusinessjournal.com/Articles/2025/11/13/disneys-sports-segment-anchored-by-espn-reports-2-revenue-gain-in-fiscal-q4/ | summary: Fiscal Q4 2025: sports revenue +2% to $4B, OI -2% to $911M; DTC OI $352M (+39%) nearly matched linear networks $391M (-21%); FY2025 sports OI $2.88B (+20%). | captured_by: agent::disney-agent-a
- id: E8 | kind: source | reference: https://thewaltdisneycompany.com/press-releases/the-walt-disney-company-and-miral-announce-plans-for-disney-theme-park-and-resort-on-yas-island-abu-dhabi/ | summary: May 7, 2025: seventh Disney resort with Miral on Yas Island, Abu Dhabi; fully funded/built/operated by Miral; Disney creative design and oversight, earns royalties; no Disney capital. | captured_by: agent::disney-agent-a
- id: E9 | kind: source | reference: https://www.reuters.com/legal/transactional/view-netflix-buy-warner-bros-discoverys-studios-streaming-unit-72-billion-2025-12-05/?share=linkedin | summary: Dec 5, 2025: Netflix agreed to buy WBD's studio/streaming unit for $82.7B ($27.75/share). SUPPORTS the Netflix-acquires-WBD version. | captured_by: agent::disney-agent-a
- id: E10 | kind: source | reference: https://www.sharewise.com/us/news_articles/Netflix_Drops_Its_Deal_to_Acquire_Warner_Bros_What_Lies_Ahead_Zacks_20260302_1729 | summary: Feb 26, 2026: Netflix declined to raise its bid; WBD board found Paramount Skydance's $31/share a superior proposal. CONTRADICTS E9. Status unresolved; carried as conflict. | captured_by: agent::disney-agent-a
- id: E11 | kind: source | reference: https://www.gamesindustry.biz/disney-invests-15bn-in-epic-games-and-announces-major-fortnite-partnership | summary: Feb 2024: $1.5B Epic Games equity stake; multiyear persistent Disney universe interoperating with Fortnite; Unreal Engine powered; no launch date. | captured_by: agent::disney-agent-a
- id: E12 | kind: source | reference: https://www.fool.com/investing/2026/02/08/7-billion-reasons-to-buy-walt-disney-stock-now/ | summary: FY2026 $7B buyback (second-highest ever) funded by FCF; $19B operating cash flow guidance minus $9B capex = ~$10B FCF; dividend ~$2.6B expense. | captured_by: agent::disney-agent-a
- id: E13 | kind: source | reference: https://markets.financialcontent.com/wral/article/finterra-2026-2-16-disneys-2026-resurgence-inside-the-7-billion-buyback-and-the-damaro-era | summary: FY2025: revenue $94.4B, net income $12.0B, adjusted EPS $5.93 (+19%); 2026 dividend $1.50/share (+50%); D'Amaro named CEO effective March 18, 2026. | captured_by: agent::disney-agent-a
- id: E14 | kind: source | reference: https://www.screendaily.com/news/disney-appoints-new-ceo-replacing-bob-iger-from-march-2026/5213350.article | summary: Feb 3, 2026: Josh D'Amaro (28-year veteran, ex-chair of Disney Experiences) named CEO effective March 18, 2026; Iger senior advisor and board member through Dec 31, 2026; Dana Walden named President and Chief Creative Officer. | captured_by: agent::disney-agent-a
- id: E15 | kind: source | reference: https://thewaltdisneycompany.com/press-releases/josh-damaro-named-next-chief-executive-officer-of-the-walt-disney-company/ | summary: Disney's own press release confirming D'Amaro appointment, Iger's four priorities legacy, continuity leadership team. | captured_by: agent::disney-agent-a
- id: E16 | kind: source | reference: https://wdwnt.com/2026/08/disney-admits-the-mandalorian-grogu-live-action-moana-underperformed-at-box-office/ | summary: Disney acknowledged Mandalorian & Grogu ($345.2M) and live-action Moana (~$263M vs ~$250M budget) underperformed expectations; strong audience scores; value beyond theaters cited. | captured_by: agent::disney-agent-a
- id: E17 | kind: source | reference: https://wdwnt.com/2026/07/toy-story-5-crosses-1-billion-at-global-box-office/ | summary: Toy Story 5 crossed $1B worldwide (third Toy Story film to do so); third 2026 film to $1B; Disney first studio to $3B global in 2026. | captured_by: agent::disney-agent-a
- id: E18 | kind: source | reference: https://cordcuttersnews.com/disney-finalizes-hulu-buyout-from-comcast-for-9-05-billion-ending-two-year-valuation-dispute/ | summary: June 9, 2025: Disney finalized 100% Hulu ownership; $438.7M additional payment after appraisal; ~$9.05B total for Comcast's 33%; enables full Hulu/Disney+/ESPN integration. | captured_by: agent::disney-agent-a
- id: E19 | kind: source | reference: https://insidethemagic.net/2026/09/disney-world-and-universal-see-2-different-realities-in-orlando-2026-update-ab1/ | summary: Sept 2026: Universal seeing softer attendance post-Epic Universe debut but ahead of pre-Epic levels; Disney attendance "exceeded expectations." Supports R3. | captured_by: agent::disney-agent-a

## StateChange log (summary)

- seq 1-11: Decisions D1-D11 created (D3a created then superseded by D3b).
- seq 12: Assumption set A1-A10 created with confidence levels.
- seq 13: Revisions R1-R3 recorded (priors P1 revised, P2 revised, P3 reversed).
- seq 14: Guardrails G1-G3, questions Q1-Q5, failed approaches FA1-FA2 recorded.
- seq 15: Evidence E1-E19 recorded, including the E9/E10 conflict (Netflix vs Paramount Skydance for WBD).

## Priors disposition (from journal)

- P1 (streaming is a drag): REVISED to R1.
- P2 (Orlando dominance unassailable): REVISED to R3.
- P3 (Iger CEO, succession unresolved): REVERSED to R2.
