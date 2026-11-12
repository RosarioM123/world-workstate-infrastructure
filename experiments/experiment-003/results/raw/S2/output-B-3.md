# Continuation Document

## 1. Where things stand

The incident involves intermittent HTTP 500 errors in the checkout service. At intake the errors were reported at roughly 2% of requests and clustered at busy times, and the support team said they had begun appearing recently, with no precise start date known at that stage.

The cause of the main problem has been established. The report generation path in the checkout service opens database connections without reliably closing them on error paths. Under load, the leaked connections exhaust the connection pool, which has 50 connections. Once the pool is exhausted, subsequent checkout requests fail with 500s. This mechanism fits the intake pattern, since errors clustered at busy times when report generation traffic and load are highest, and it accounts for a rate of roughly 2% rather than a total outage.

A fix for that cause has been written and merged in the checkout service repository. Connections are now released via a context manager on all paths, including error paths, and a regression test was included with the fix. The handoff material makes no claim about post merge error rates, so no post merge outcome can be assumed.

No rollback was performed.

One separate symptom remains open and unexplained: a rare timeout in the payment webhook handler, still occurring at about 1 in 2,000 calls, which does not correlate with the pool exhaustion pattern.

## 2. Decisions in force

Decisions that currently govern the incident response:

- No rollback of the pricing service: the pricing service was not rolled back on suspicion alone, and no rollback was performed. Reason: a standing constraint required evidence that a rollback target caused the problem, and log analysis later exonerated the pricing service deploy.
- Focus on the report generation path in the checkout service: attention shifted to that path. Reason: log analysis showed the error rate correlates with report generation traffic and does not correlate with pricing calls.
- Fix approach for the connection leak: connections are now released via a context manager on all paths, including error paths, with a regression test included, and the fix was made in the checkout service repository. Reason: code inspection established that connections were not reliably closed on error paths, and the location of the fix complied with the change freeze.
- Retention of the invalidated pricing hypothesis in the record: the original hypothesis was retained as invalidated, with the timeline evidence as the reason, rather than being edited away or deleted.
- Treatment of the payment webhook timeout as a separate open question: it was not attributed to the connection pool problem and was not attributed to the pricing service. Reason: it does not correlate with the pool exhaustion pattern, and no evidence links it to any cause.

Decisions or hypotheses that are no longer in force:

- The hypothesis that a deploy of the separate pricing service four days earlier caused the errors. This was the first working hypothesis of the session, based only on timing, because the deploy was recent and close in time to when the errors were noticed. It has been invalidated by timestamp analysis of the checkout error logs, described in Section 5.

## 3. Assumptions and facts

Established findings:

- Timestamp analysis of the checkout error logs showed the 500 errors began seven days ago, which is three days before the pricing service deploy four days ago.
- The same log analysis showed the error rate correlates with report generation traffic and does not correlate with pricing calls.
- Code inspection of the report generation path in the checkout service established that it opens database connections without reliably closing them on error paths, that leaked connections under load exhaust the connection pool of 50 connections, and that once the pool is exhausted, subsequent checkout requests fail with 500s.
- A rare timeout in the payment webhook handler is occurring at about 1 in 2,000 calls and does not correlate with the pool exhaustion pattern.

Assumptions still in play:

- No assumptions are recorded as still in play in the handoff material. In particular, no cause for the payment webhook timeout is assumed, and no post merge error rate is assumed for the merged fix.

Hypotheses, distinct from established findings:

- The pricing service deploy hypothesis is no longer a hypothesis in play. It was only ever a hypothesis based on timing gossip, confidence in it was low from the start, and there was no log evidence, code evidence, or correlation evidence for it at that point. It has since been invalidated, as described in Sections 2 and 5.
- No hypothesis for the payment webhook timeout is recorded in the handoff material.

## 4. Constraints

- During the incident there is a change freeze under which code changes are allowed only in the checkout service repository.
- No service is to be rolled back without evidence that the rollback target caused the problem.

These constraints ruled out rolling back the pricing service on suspicion alone.

## 5. What changed and why

At intake, the precise start date of the errors was not known, and the first working hypothesis was that a deploy of the separate pricing service four days earlier had caused the errors. That hypothesis rested only on timing, with low confidence and no supporting log, code, or correlation evidence. What still needed to be established was when the errors had actually begun and whether the error rate tracked pricing service calls, another traffic pattern, or load in general.

Log analysis changed that understanding. Timestamp analysis of the checkout error logs showed the 500 errors began seven days ago, three days before the pricing service deploy, so that deploy cannot have introduced errors that were already occurring. The same analysis showed the error rate correlates with report generation traffic and does not correlate with pricing calls.

The pricing hypothesis was therefore invalidated and replaced. Attention shifted instead to the report generation path in the checkout service, following the correlation with report generation traffic. Code inspection of that path then established the connection leak mechanism described in Section 1.

The authoritative account now is: the pricing service deploy is exonerated by the timeline, and the main problem was caused by the report generation path in the checkout service leaking database connections on error paths, exhausting the 50 connection pool under load. The evidence that settled the pricing question was the timestamp analysis of the checkout error logs, together with the correlation findings. The evidence that settled the cause of the main problem was code inspection of the report generation path.

## 6. Open questions and missing information

- The rare timeout in the payment webhook handler remains unexplained. Its cause is unknown. It is occurring at about 1 in 2,000 calls and does not correlate with the pool exhaustion pattern. No evidence links it to any cause, and it was not attributed to the connection pool problem or to the pricing service for that reason. No fix or owner for it is recorded.
- The next questions on the timeout are what causes it, and whether it has its own traffic, timing, or dependency pattern, given that it does not follow the pool exhaustion pattern.
- Post merge error rates for the merged connection leak fix are missing from the handoff material. The material makes no claim about them, so whether the 500 error rate has changed after the merge is not established here.

## 7. Next actions

In order:

1. Establish the post merge error rate for the checkout 500 errors from the available evidence, without assuming an outcome from the fact that the fix was merged. Do not redo the completed fix.
2. Investigate the payment webhook timeout as a separate open question: determine whether it has its own traffic, timing, or dependency pattern, and what causes it. Do not attribute it to the connection pool problem or to the pricing service without evidence.
3. Apply the standing constraints to any further action: make any code changes only in the checkout service repository, and do not roll back any service without evidence that the rollback target caused the problem.

No other next actions are specified in the handoff material.

## 8. Incident follow-up note

Current status: the main cause of the intermittent checkout 500 errors has been identified and a fix has been merged. The errors were reported at roughly 2% of requests and clustered at busy times. Code inspection found that the report generation path in the checkout service opened database connections without reliably closing them on error paths. Under load the leaked connections exhausted the 50 connection pool, and later checkout requests then failed with 500s. Connections are now released via a context manager on all paths, including error paths, and a regression test was included. No post merge error rate is claimed here. The pricing service deploy was ruled out because timestamp analysis of the checkout error logs showed the errors began seven days ago, three days before that deploy, and the error rate correlates with report generation traffic, not pricing calls. No rollback was performed. Still being investigated next: a rare payment webhook timeout, at about 1 in 2,000 calls, which does not follow the pool exhaustion pattern and whose cause is unknown.
