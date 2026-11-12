# Continuation Document: Checkout Service HTTP 500 Incident (S2)

## 1. Where things stand

The main problem is intermittent HTTP 500 errors in the checkout service, reported at intake at roughly 2% of requests and clustered at busy times.

The cause of the main problem has been established. The report generation path in the checkout service opens database connections without reliably closing them on error paths. Under load, the leaked connections exhaust the connection pool, which has 50 connections. Once the pool is exhausted, subsequent checkout requests fail with 500s. This mechanism fits the intake pattern, since errors clustered at busy times when report generation traffic and load are highest, and it accounts for a rate of roughly 2% rather than a total outage.

A fix for that cause has been written and merged in the checkout service repository. Connections are now released via a context manager on all paths, including error paths, and a regression test was included with the fix. The handoff material makes no claim about post-merge error rates, so no post-merge outcome is assumed here.

One separate symptom remains open and unexplained: a rare timeout in the payment webhook handler, still occurring at about 1 in 2,000 calls. It does not correlate with the pool exhaustion pattern, and its cause is unknown.

## 2. Decisions in force

Decisions and positions that currently govern the incident response:

- No rollback was performed, and no service is to be rolled back without evidence that the rollback target caused the problem. Reason: suspicion alone was not evidence, and the timeline later exonerated the pricing service.
- The fix was made in the checkout service repository only. Reason: this complied with the change freeze in force during the incident.
- The fix approach in force is to release connections via a context manager on all paths, including error paths, with a regression test included. Reason: this addresses the established cause, connections not being reliably closed on error paths.
- Attention is directed to the report generation path in the checkout service rather than to the pricing service. Reason: the error rate correlates with report generation traffic and does not correlate with pricing calls.
- The payment webhook timeout is recorded as an open question with cause unknown, and is not attributed to the connection pool problem or to the pricing service. Reason: it does not correlate with the pool exhaustion pattern, and no evidence links it to any cause.
- The original pricing service hypothesis is retained in the record as invalidated, with the timeline evidence as the reason, rather than being edited away or deleted.

Decisions or hypotheses that are no longer in force:

- The hypothesis that a deploy of the separate pricing service four days ago caused the errors. This was the first working hypothesis of the session, based only on timing gossip because the deploy was recent and close in time to when the errors were noticed. Confidence in it was low from the start, and there was no log evidence, code evidence, or correlation evidence for it. It is now invalidated and replaced.
- Any consideration of rolling back the pricing service on suspicion alone. This is ruled out by the standing constraint on rollbacks and by the timeline evidence.

## 3. Assumptions and facts

Established findings, distinct from hypotheses:

- The 500 errors began seven days ago, established by timestamp analysis of the checkout error logs.
- The pricing service deploy happened four days ago, which is three days after the errors began.
- The error rate correlates with report generation traffic.
- The error rate does not correlate with pricing calls.
- Code inspection established that the report generation path in the checkout service opens database connections without reliably closing them on error paths, that the connection pool has 50 connections, and that leaked connections exhaust the pool under load, after which subsequent checkout requests fail with 500s.
- The payment webhook timeout occurs at about 1 in 2,000 calls and does not correlate with the pool exhaustion pattern.

Assumptions and hypotheses still in play:

- None for the main problem. The cause of the main problem is treated as established by code inspection and by the correlation and timeline findings above, not as an assumption.
- For the payment webhook timeout, no hypothesis is in play. Its cause is explicitly unknown, and no assumption about its cause is recorded.
- Missing information, not an assumption: post-merge error rates are not stated in the handoff material, so whether the merged fix has changed the observed error rate in production is not established here.

## 4. Constraints

Every standing constraint recorded in the handoff material:

- During the incident there is a change freeze under which code changes are allowed only in the checkout service repository.
- No service is to be rolled back without evidence that the rollback target caused the problem.

These constraints ruled out rolling back the pricing service on suspicion alone.

No other standing constraints are recorded in the handoff material.

## 5. What changed and why

At intake, the errors were said to have begun appearing recently, although no precise start date was known. Several people suspected a deploy of the separate pricing service that had happened four days earlier, and that suspicion became the first working hypothesis, based on timing gossip and with low confidence from the start.

What changed: that hypothesis was invalidated and replaced, and attention shifted to the report generation path in the checkout service.

Why it changed: log analysis settled the question. Timestamp analysis of the checkout error logs showed that the 500 errors began seven days ago, three days before the pricing service deploy four days ago, so that deploy cannot have introduced errors that were already occurring. The same analysis showed that the error rate correlates with report generation traffic and does not correlate with pricing calls.

Which account is authoritative now: the current authoritative account is that the pricing service deploy is exonerated by the timeline, and that the main problem was caused by the report generation path in the checkout service leaking database connections on error paths until the 50 connection pool was exhausted under load. The earlier pricing service account is retained only as an invalidated hypothesis.

What evidence settled it: the timestamp analysis establishing the seven day start date, the correlation with report generation traffic and lack of correlation with pricing calls, and code inspection of the report generation path establishing the connection leak mechanism.

## 6. Open questions and missing information

- What causes the rare timeout in the payment webhook handler, occurring at about 1 in 2,000 calls? Cause unknown. It is not attributed to the connection pool problem and not attributed to the pricing service. No cause is guessed here.
- Whether the payment webhook timeout has its own traffic, timing, or dependency pattern, given that it does not follow the pool exhaustion pattern.
- No fix and no owner are recorded for the payment webhook timeout.
- Post-merge error rates are not stated in the handoff material, so the observed effect of the merged fix is missing information.

No other open questions are recorded in the handoff material.

## 7. Next actions

In order, and without redoing completed fixes or proposing anything the constraints prohibit:

1. Investigate the payment webhook timeout as a separate symptom: establish what causes it, at about 1 in 2,000 calls.
2. As part of that investigation, check whether the timeout has its own traffic, timing, or dependency pattern, rather than assuming the pool exhaustion pattern.
3. Obtain the post-merge error rate information that is missing from the handoff material, to establish the observed status of the main problem after the merged fix, without assuming an outcome.
4. Keep any further code changes within the checkout service repository under the change freeze, and do not roll back any service without evidence that the rollback target caused the problem.

## 8. Incident follow-up note

Current status: the main cause of the intermittent checkout 500 errors, at roughly 2% of requests, has been identified and a fix has been merged. The report generation path leaked database connections on error paths until the 50 connection pool was exhausted under load. Connections are now released via a context manager on all paths, including error paths, with a regression test included. Post-merge error rates are not stated in the handoff material.

Ruled out: the pricing service deploy from four days ago. The errors began seven days ago, before that deploy, and the error rate correlates with report generation traffic, not pricing calls. No rollback was performed.

Still open: a rare payment webhook timeout at about 1 in 2,000 calls, with cause unknown and no correlation to the pool exhaustion pattern. Next, that timeout is being investigated as a separate symptom, including whether it has its own traffic, timing, or dependency pattern.
