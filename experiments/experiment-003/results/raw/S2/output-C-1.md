# Continuation Document: Checkout Incident Investigation

## 1. Where things stand

The checkout service has been returning intermittent HTTP 500 errors at a rate of roughly 2% of requests, clustered at busy times.

The established cause of the main problem is a database connection leak in the report generation path of the checkout service. That path opens database connections without reliably closing them on error paths. Under load, the connection pool, which has 50 connections, is exhausted, and subsequent checkout requests then fail with 500s. This mechanism fits the intake pattern of errors clustered at busy times and a rate of roughly 2% rather than a total outage.

What has been fixed:
- A fix for the main cause was written and merged in the checkout service repository.
- Connections are now released via a context manager on all paths, including error paths.
- A regression test was included with the fix.

What remains open:
- A rare timeout in the payment webhook handler is still occurring, at about 1 in 2,000 calls. It is unexplained and no fix is recorded for it.
- No information is given in the handoff material about post merge error rates, so whether the merged fix has changed the observed 500 rate in production is not recorded.

## 2. Decisions in force

Decisions that currently govern the incident response:
- No rollback of the pricing service. Reason: the timeline evidence exonerated that service, and the standing constraint requires evidence that a rollback target caused the problem before any rollback.
- No rollback of any service on suspicion alone. Reason: a rollback requires evidence that the rollback target caused the problem.
- The fix was made in the checkout service repository. Reason: the established cause was in that repository, and the change freeze allows code changes only there during the incident.
- Attention is directed to the report generation path in the checkout service rather than to the pricing service. Reason: the error rate correlates with report generation traffic and does not correlate with pricing calls.
- The rare payment webhook handler timeout is treated as a separate open symptom, not as part of the connection pool problem. Reason: the handoff material states it does not correlate with the pool exhaustion pattern, and no evidence links it to any cause.

Decisions or hypotheses that are no longer in force:
- The initial hypothesis that the pricing service deploy four days ago introduced the errors. This was a hypothesis only, based on timing gossip, with low confidence and no log, code, or correlation evidence. It was invalidated by the timestamp evidence described in section 5 and is no longer in force.
- The implied plan to check the pricing service deploy as the leading explanation. That line of investigation was replaced once the timeline and correlation evidence arrived.

## 3. Assumptions and facts

Assumptions still in play:
- None are recorded as still in play in the handoff material. The only hypothesis formed in the prior session, the pricing service deploy hypothesis, was invalidated and is listed in section 2 as no longer in force. No assumption is recorded about the cause of the payment webhook handler timeout, and none should be treated as in play.

Established findings, distinct from hypotheses:
- The checkout service returns intermittent HTTP 500 errors at roughly 2% of requests, clustered at busy times.
- The 500 errors began seven days ago.
- A deploy of the separate pricing service happened four days ago, which is three days after the errors began.
- The error rate correlates with report generation traffic.
- The error rate does not correlate with pricing calls.
- The report generation path in the checkout service opens database connections without reliably closing them on error paths.
- The connection pool has 50 connections, and under load the pool is exhausted, after which subsequent checkout requests fail with 500s.
- A fix releasing connections via a context manager on all paths, including error paths, was written and merged, with a regression test.
- A rare timeout in the payment webhook handler is still occurring at about 1 in 2,000 calls, and it does not correlate with the pool exhaustion pattern.

## 4. Constraints

Standing constraints on the incident response:
- Change freeze: during the incident, code changes are allowed only in the checkout service repository.
- No rollback of any service without evidence that the rollback target caused the problem.

## 5. What changed and why

At intake, the leading account was suspicion of the pricing service. Several people suspected its deploy four days ago, and the prior agent formed that as an initial working hypothesis with low confidence, based on timing only and on the support team report that the errors began appearing "recently", with no precise start date given at that stage.

That understanding changed when the Part 2 log analysis results arrived:
- Timestamp analysis showed the 500 errors began seven days ago, three days before the pricing service deploy.
- The error rate was found to correlate with report generation traffic and not with pricing calls.

Why it changed: a deploy cannot have introduced errors that were already occurring three days before it, so the pricing service deploy was exonerated by the timeline, and the correlation results pointed to the report generation path instead.

Code inspection of the report generation path then supplied the mechanism: connections opened without reliable closing on error paths, exhausting the 50 connection pool under load and causing subsequent checkout requests to fail with 500s.

The authoritative account now is the later account: the main problem was caused by the database connection leak on error paths in the report generation path of the checkout service, not by the pricing service deploy. The evidence that settled it was the timestamp analysis of the checkout error logs, the correlation findings, and the code inspection of the report generation path. The earlier pricing hypothesis was replaced, not removed from the record; it remains documented as invalidated.

## 6. Open questions and missing information

- The cause of the rare timeout in the payment webhook handler, occurring at about 1 in 2,000 calls, is unexplained. No cause is stated in the handoff material, it does not correlate with the pool exhaustion pattern, and no evidence links it to the pricing service or to any other cause. This is flagged as unknown; no cause is guessed here.
- Post merge error rates are not recorded in the handoff material, so the effect of the merged fix on the observed 500 rate is missing information.
- No other missing information needed for the main cause is recorded: the start date, the correlations, and the code level mechanism for the main problem were all established in the prior session.

## 7. Next actions

In order:
1. Monitor the checkout 500 error rate after the merged fix and record the observed rate, since no post merge outcome is recorded yet. Do not redo the merged fix.
2. Investigate the rare payment webhook handler timeout as a separate symptom: gather its timing and frequency evidence and check what it does and does not correlate with, following the same evidence based approach used for the main problem.
3. Keep the standing constraints in force throughout: make any code changes only in the checkout service repository, and do not roll back any service unless evidence shows the rollback target caused the problem.
4. Do not pursue a pricing service rollback or pricing service code changes, since that service was exonerated by the timeline and such actions would breach the constraints in section 4.

## 8. Incident follow-up note

Incident update: the main cause of the intermittent checkout HTTP 500 errors has been found and fixed. The report generation path in the checkout service was leaking database connections on error paths. Under load this exhausted the 50 connection pool, and later checkout requests failed with 500s.

The fix, releasing connections via a context manager on all paths including error paths, has been merged with a regression test. No post merge error rate is available yet, so the observed effect of the fix still needs to be recorded.

Ruled out: the pricing service deploy. Timestamp analysis showed the errors began seven days ago, three days before that deploy, and the error rate did not correlate with pricing calls. It correlated with report generation traffic instead.

Still being investigated next: a rare timeout in the payment webhook handler, about 1 in 2,000 calls. It is unexplained, does not correlate with the pool exhaustion pattern, and has not been attributed to any cause.
