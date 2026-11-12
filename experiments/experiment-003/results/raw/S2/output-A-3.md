# Continuation Document: Checkout Incident Investigation (S2)

## 1. Where things stand

The checkout service had intermittent HTTP 500 errors at roughly 2% of requests, clustered at busy times.

The main problem is settled. Its cause was a database connection leak on error paths in the report generation path of the checkout service. That path opened database connections without reliably closing them on error paths. Under load, the leak exhausted the 50 connection pool, and subsequent checkout requests failed with 500s.

What has been fixed: a fix was written and merged. Connections are now released via a context manager on all paths, including error paths, with a regression test.

What remains open:
- A rare timeout in the payment webhook handler, about 1 in 2,000 calls, is still occurring and is unexplained. It does not correlate with the pool exhaustion pattern and is treated as a separate problem.
- The measured post merge error rate for the main 500 pattern is not given in the handoff material, so a measured recovery has not been recorded.

## 2. Decisions in force

Decisions currently governing the incident response:

- D1: Do not roll back the pricing service on suspicion alone. Investigate the timeline and correlations first. Reason: constraint C-2 bars a rollback without evidence that the rollback target caused the problem. At intake the only basis was timing gossip about a deploy four days ago, which was a hypothesis, not evidence.
- D2: Treat the main cause as the database connection leak on error paths in the report generation path, exhausting the 50 connection pool under load, and no longer treat the pricing service deploy as the cause. Reason: log timestamp analysis shows the errors began seven days ago, three days before the pricing deploy, and the error rate correlates with report generation traffic rather than pricing calls. Code inspection then found the exact leak mechanism in that path. Evidence: E2 and E3.
- D3: Fix the connection leak in the checkout service with a context manager and a regression test, and merge that fix. Reason: the leak was on paths where connections were not reliably closed, so release must hold on all paths. The change is in the checkout service repository, so it complies with the change freeze in constraint C-1. The materials state the fix was written and merged. Evidence: E3 and E4.
- D4: Treat the payment webhook timeout as a separate open problem, not as part of the pool exhaustion cause, and do not attribute it to the connection pool exhaustion or to the pricing service. Reason: the materials state the timeout is still occurring, is unexplained, and does not correlate with the pool exhaustion pattern. No evidence in the materials links it to any other cause. Evidence: E5.

Decisions or hypotheses that are no longer in force:

- A1, the initial hypothesis that the pricing service deploy four days ago introduced the errors, is invalidated and is no longer in force. It is retained visibly for the record. Reason for invalidation: E2 shows the errors began seven days ago, three days before the deploy, and the error rate does not correlate with pricing calls. No decision record was superseded as a record; D2 superseded the working position based on A1.

## 3. Assumptions and facts

Established findings, distinct from hypotheses:

- E1, incident report: checkout service returns intermittent HTTP 500 errors, roughly 2% of requests, clustered at busy times. Errors were reported by the support team as having begun recently. That onset wording was a report, not a measured start date. A deploy of the separate pricing service happened four days ago and several people suspected it.
- E2, log analysis: timestamp analysis shows the 500 errors began seven days ago, three days before the pricing service deploy. The error rate correlates with report generation traffic, not with pricing calls.
- E3, code inspection: the report generation path in the checkout service opens database connections without reliably closing them on error paths. Under load the connection pool of 50 connections is exhausted, and subsequent checkout requests fail with 500s.
- E4, fix: a fix was written and merged. Connections are now released via a context manager on all paths, with a regression test. No commit identifier, pull request identifier, or post merge measurement is given in the handoff material.
- E5, remaining symptom: separately, a rare timeout in the payment webhook handler, about 1 in 2,000 calls, is still occurring and is unexplained. It does not correlate with the pool exhaustion pattern.

Assumptions, labeled as assumptions:

- A2, assumption, now recorded as validated, confidence high: the report generation path leaking database connections on error paths, exhausting the 50 connection pool under load, is the cause of the main intermittent 500 pattern, including its clustering at busy times. Validated by E3 and supported by the E2 correlation with report generation traffic. Note from the handoff material: validation rests on the timeline, correlation, and code inspection evidence, not on a measured recovery, because no post merge error rate is given.
- A3, assumption status active, confidence low: no causal assumption is adopted for the payment webhook handler timeout. This entry makes the absence explicit. No hypothesis for its cause is recorded.
- A1 is listed in Section 2 as invalidated and is not an assumption still in play.

## 4. Constraints

Every standing constraint on the incident response, as recorded in the handoff material:

- C-1: Change freeze. During the incident, code changes are allowed only in the checkout service repository.
- C-2: No rollback of any service without evidence that the rollback target caused the problem.
- C-3: Use only the scenario materials. A hypothesis is not a finding, and hypotheses are labelled as assumptions until evidence settles them.
- C-4: When a hypothesis is replaced, keep the old one visible as superseded or invalidated with the reason.

## 5. What changed and why

How the understanding changed during the prior session:

At intake, the working position was assumption A1: the pricing service deploy four days ago introduced the errors. Its basis at formation was timing gossip only. The support team said the errors began recently, the deploy was recent, and several people suspected the deploy. No log, code, or correlation evidence supported it at formation. Confidence was low.

That account was replaced. Log analysis in E2 showed the errors began seven days ago, three days before the pricing deploy, and that the error rate correlates with report generation traffic rather than pricing calls. On that evidence, A1 was invalidated at that point in the session and retained visibly rather than deleted.

The investigation then focused on the report generation path, following the E2 correlation. That became replacement assumption A2. Code inspection in E3 then supplied the mechanism: connections were not reliably closed on error paths in that path, exhausting the 50 connection pool under load.

Authoritative account now: the main cause is the report generation connection leak described in D2 and A2, not the pricing service deploy. Evidence that settled it: E2 settled the timeline and correlation question against the pricing deploy, and E3 settled the mechanism by finding the leak in the code. A2 was then recorded as validated, D2 was accepted, and the fix under D3 was merged.

Separately, E5 was recorded late in the session: the payment webhook timeout does not correlate with the pool exhaustion pattern. D4 was accepted to keep it as a separate open problem, not attributed to the leak or to the pricing service.

## 6. Open questions and missing information

- Q1, open: What causes the rare timeout in the payment webhook handler, about 1 in 2,000 calls, which is still occurring and unexplained? Cause unknown. It does not correlate with the pool exhaustion pattern, so the connection leak fixed under D3 does not explain it. No cause is guessed here.
- Q2, open: What is the measured checkout 500 error rate after the context manager fix was merged? The handoff material states the fix was written and merged but gives no post merge measurement. Missing information: the post merge error rate.
- Missing information noted in the handoff material: no commit identifier or pull request identifier for the merged fix is given, and no post merge measurement is given. None is invented here.
- No causal assumption for the webhook timeout is recorded in the handoff material. That information is missing and is flagged, not filled in.

## 7. Next actions

In order, based only on the open items in the handoff material:

1. Investigate Q1 first: establish the cause of the payment webhook handler timeout, about 1 in 2,000 calls, starting from the fact that it does not correlate with the pool exhaustion pattern. Do not attribute it to pool exhaustion or to the pricing service without new evidence.
2. Address Q2: obtain the measured post merge checkout 500 error rate for the main pattern before claiming recovery.
3. Carry forward decisions D1 to D4 in any further work. Do not reopen the pricing deploy account without new evidence that answers the timeline problem in E2, namely that the errors began three days before the deploy.

No step above proposes redoing the merged context manager fix, and no step proposes a rollback or a code change outside the checkout service repository, which the constraints prohibit.

## 8. Incident follow-up note

Current status: the main checkout 500 pattern has a settled cause and a merged fix. A separate rare payment webhook timeout remains open and unexplained.

What was fixed: the report generation path in the checkout service leaked database connections on error paths, exhausting the 50 connection pool under load. Connections are now released via a context manager on all paths, with a regression test. No post merge error rate is recorded yet, so recovery is not claimed as measured.

What was ruled out and why: the pricing service deploy was ruled out as the cause. Log analysis showed the errors began seven days ago, three days before that deploy, and the error rate correlates with report generation traffic, not pricing calls.

What is being investigated next: the payment webhook handler timeout, about 1 in 2,000 calls, which does not correlate with the pool exhaustion pattern, and obtaining the measured post merge error rate.
