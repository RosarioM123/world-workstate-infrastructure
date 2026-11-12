# Continuation Document: Checkout Incident Investigation

## 1. Where things stand

The checkout service had intermittent HTTP 500 errors at roughly 2% of requests, clustered at busy times.

The main cause is established: the report generation path in the checkout service opened database connections without reliably closing them on error paths. Under load, this leak exhausted the 50 connection pool, and subsequent checkout requests failed with 500s.

What has been fixed: a fix was written and merged. Database connections are now released via a context manager on all paths, including error paths, in the report generation path, with a regression test.

What remains open:

- A rare timeout in the payment webhook handler, about 1 in 2,000 calls, is still occurring and is unexplained. It does not correlate with the pool exhaustion pattern and is treated as a separate problem.
- The measured checkout 500 error rate after the fix was merged is not recorded in the handoff material. The merged fix must not be mistaken for a measured recovery.

## 2. Decisions in force

Decisions that currently govern the incident response:

- D1: Do not roll back the pricing service on suspicion alone, and investigate the timeline and correlations first. Reason: a standing constraint bars a rollback without evidence that the rollback target caused the problem. At intake, the only basis was timing gossip about a deploy four days earlier, which was a hypothesis, not evidence.
- D2: Treat the main cause as a database connection leak on error paths in the report generation path of the checkout service, exhausting the 50 connection pool under load, and no longer treat the pricing service deploy as the cause. Reason: log timestamp analysis shows the errors began seven days ago, three days before the pricing deploy, and the error rate correlates with report generation traffic rather than pricing calls. Code inspection then found the exact leak mechanism in that path.
- D3: Fix the connection leak in the checkout service with a context manager and a regression test. Reason: the leak was on paths where connections were not reliably closed, so release must hold on all paths. The change is in the checkout service repository, so it complies with the change freeze. The handoff material states the fix was written and merged.
- D4: Treat the payment webhook timeout as a separate open problem, not as part of the pool exhaustion cause. Reason: the timeout is still occurring, is unexplained, and does not correlate with the pool exhaustion pattern. No evidence in the material links it to the connection pool exhaustion or to the pricing service.

Decisions or hypotheses no longer in force:

- A1: The hypothesis that the pricing service deploy four days ago introduced the intermittent checkout HTTP 500 errors. This is invalidated, not deleted, and is retained for the record. It was based on timing gossip only. It was invalidated because the errors began seven days ago, three days before the deploy, and the error rate does not correlate with pricing calls. No separate decision record is listed in the handoff material as superseded; D2 supersedes the working position based on A1.

## 3. Assumptions and facts

Established findings, distinct from hypotheses:

- Incident report: the checkout service returned intermittent HTTP 500 errors, roughly 2% of requests, clustered at busy times. The support team reported that the errors began "recently." A deploy of the separate pricing service happened four days before intake, and several people suspected it. The word "recently" was a report from the support team, not a measured start date.
- Log analysis: timestamp analysis of the checkout error logs shows the 500 errors began seven days ago, three days before the pricing service deploy. The error rate correlates with report generation traffic, not with pricing calls.
- Code inspection: the report generation path in the checkout service opens database connections without reliably closing them on error paths. Under load, the 50 connection pool is exhausted, and subsequent checkout requests fail with 500s.
- Fix record: a fix was written and merged, with connections released via a context manager on all paths and a regression test. No commit identifier, pull request identifier, or post merge measurement is given in the handoff material.
- Remaining symptom: a rare timeout in the payment webhook handler, about 1 in 2,000 calls, is still occurring and is unexplained. It does not correlate with the pool exhaustion pattern.

Assumptions still in play, labeled as assumptions:

- A2, validated, confidence high: the report generation path leaking database connections on error paths, exhausting the 50 connection pool under load, is the cause of the main intermittent 500 pattern, including its clustering at busy times. It was validated by the code inspection evidence and supported by the correlation with report generation traffic. Validation rests on the timeline, correlation, and code inspection evidence, not on a measured post merge recovery, because no post merge error rate is given.
- A3, active, confidence low: no causal assumption is adopted for the payment webhook handler timeout. This entry makes the absence explicit. No hypothesis for its cause is recorded.

## 4. Constraints

Every standing constraint on the incident response:

- C-1: Change freeze. During the incident, code changes are allowed only in the checkout service repository.
- C-2: No rollback of any service without evidence that the rollback target caused the problem.
- C-3: Use only the scenario materials. A hypothesis is not a finding, and hypotheses are labeled as assumptions until evidence settles them. In this continuation, work only from the handoff material and flag missing information instead of filling gaps.
- C-4: When a hypothesis is replaced, keep the old one visible as superseded or invalidated, with the reason.

## 5. What changed and why

At intake, the understanding was based on the incident report and an initial hypothesis, A1: that the pricing service deploy four days earlier had introduced the errors. That hypothesis had low confidence and was based on timing gossip only: the deploy was recent, the support team said the errors began recently, and several people suspected the deploy. No log, code, or correlation evidence supported it at formation. Decision D1 therefore held that the pricing service would not be rolled back on suspicion alone.

Part 2 log analysis changed the understanding. Timestamp analysis showed the errors began seven days ago, three days before the pricing deploy, and the error rate correlated with report generation traffic rather than pricing calls. That evidence invalidated A1 and redirected the investigation from pricing calls to the report generation path. A new working hypothesis, A2, focused on that path.

Code inspection then supplied the mechanism: the report generation path did not reliably close database connections on error paths, the 50 connection pool was exhausted under load, and subsequent checkout requests failed with 500s. On that basis, A2 was validated with high confidence, D2 recorded the report generation connection leak as the main cause, and D3 recorded the merged context manager fix with a regression test.

The authoritative account now is D2 and A2: the main cause is the connection leak on error paths in the report generation path, not the pricing service deploy. The evidence that settled it was the log timeline and correlation, which exonerated the pricing deploy and pointed to report generation traffic, combined with the code inspection that found the exact leak mechanism.

Separately, the payment webhook timeout was recorded as still occurring and unexplained, with no correlation to the pool exhaustion pattern. D4 treats it as a separate open problem, not as part of the main cause.

## 6. Open questions and missing information

- Q1: What causes the rare timeout in the payment webhook handler, about 1 in 2,000 calls, which is still occurring and unexplained? Its cause is unknown. It does not correlate with the pool exhaustion pattern, so the connection leak fixed under D3 does not explain it. No cause is guessed here.
- Q2: What is the measured checkout 500 error rate after the context manager fix was merged? The handoff material states the fix was written and merged but gives no post merge measurement.
- Missing information flagged in the handoff material: no commit identifier, pull request identifier, or post merge measurement for the merged fix is given. No evidence links the webhook timeout to any other cause, and no causal assumption for it has been adopted.

## 7. Next actions

In order:

1. Investigate Q1 first: establish the cause of the payment webhook handler timeout, about 1 in 2,000 calls, from evidence. Treat it as a separate problem under D4, and do not attribute it to the pool exhaustion or to the pricing service without evidence.
2. Obtain the measured post merge checkout 500 error rate for the main pattern, Q2, before claiming recovery for that pattern.
3. Keep any further code changes within the checkout service repository, in line with the change freeze in C-1, and do not roll back any service without evidence that the rollback target caused the problem, in line with C-2.

Completed work is not to be redone: the context manager fix with its regression test is already written and merged, and the pricing service rollback question was already settled under D1 and D2 on the timeline and correlation evidence.

## 8. Incident follow-up note

Current status: the main cause of the intermittent checkout 500 errors is established and a fix is merged. What was fixed: the report generation path in the checkout service leaked database connections on error paths, exhausting the 50 connection pool under load. Connections are now released via a context manager on all paths, with a regression test. What was ruled out and why: the pricing service deploy was ruled out as the cause because log analysis shows the errors began seven days ago, three days before that deploy, and the error rate correlates with report generation traffic, not pricing calls. No post merge error rate is recorded yet, so recovery for the main pattern has not been measured. What is being investigated next: a rare payment webhook handler timeout, about 1 in 2,000 calls, still occurring and unexplained. It does not correlate with the pool exhaustion pattern and is being treated as a separate open problem. Its cause is unknown and is not guessed here.
