# Continuation Document: Checkout Incident Investigation

## 1. Where things stand

The checkout service returns intermittent HTTP 500 errors at a rate of roughly 2% of requests, clustered at busy times.

The established cause of the main problem is a database connection leak in the report generation path of the checkout service. That path opens database connections without reliably closing them on error paths. Under load, the connection pool, which has 50 connections, is exhausted, and once the pool is exhausted, subsequent checkout requests fail with 500s.

What has been fixed:
- A fix for the connection leak was written and merged in the checkout service repository.
- Connections are now released via a context manager on all paths, including error paths.
- A regression test was included with the fix.

What remains open:
- No post merge error rate is recorded in the handoff material, so whether the merged fix has changed the observed error rate in operation is not stated.
- A separate symptom remains: a rare timeout in the payment webhook handler, occurring about 1 in 2,000 calls. It is still unexplained, it does not correlate with the pool exhaustion pattern, and no fix is recorded for it.

## 2. Decisions in force

Decisions that currently govern the incident response:

- No rollback of the pricing service was made. Reason: the standing constraint requires evidence that a rollback target caused the problem, and the timeline evidence exonerated the pricing service deploy.
- Attention shifted from the pricing service to the report generation path in the checkout service. Reason: the error rate correlates with report generation traffic and does not correlate with pricing calls, and code inspection of that path found the connection leak.
- The main cause was fixed in the checkout service by releasing connections via a context manager on all paths, including error paths, with a regression test included. Reason: code inspection showed connections were not reliably closed on error paths, leading to pool exhaustion under load. This change was within the change freeze because it was in the checkout service repository.
- The payment webhook handler timeout is treated as a separate open question, not attributed to the connection pool problem or to the pricing service. Reason: the handoff material states it does not correlate with the pool exhaustion pattern, and no evidence in the material links it to any cause.

Decisions or hypotheses no longer in force:

- Initial working hypothesis: the pricing service deploy four days ago introduced the errors. This hypothesis is no longer in force. It was invalidated by timestamp evidence showing the errors began seven days ago, three days before that deploy. It was based on timing only, with no log, code, or correlation evidence, and its confidence at formation was low.

## 3. Assumptions and facts

Established findings, distinct from hypotheses:

- The 500 errors began seven days ago, based on timestamp analysis of the checkout error logs.
- The pricing service deploy happened four days ago, three days after the errors began.
- The error rate correlates with report generation traffic.
- The error rate does not correlate with pricing calls.
- The report generation path in the checkout service opens database connections without reliably closing them on error paths.
- The connection pool has 50 connections and is exhausted under load, after which subsequent checkout requests fail with 500s.
- A fix releasing connections via a context manager on all paths, including error paths, was written and merged, with a regression test.
- A rare timeout in the payment webhook handler is still occurring at about 1 in 2,000 calls, is unexplained, and does not correlate with the pool exhaustion pattern.

Assumptions still in play:

- None are recorded as still in play in the handoff material. The only hypothesis recorded, the pricing service deploy hypothesis, was invalidated and is listed in Section 2 as no longer in force. No hypothesis for the payment webhook handler timeout is recorded, and no confidence level for any remaining assumption is given in the material.

## 4. Constraints

Standing constraints on the incident response, recorded before any fix or rollback was considered:

- Change freeze: during the incident, code changes are allowed only in the checkout service repository.
- No rollback of any service without evidence that the rollback target caused the problem.

## 5. What changed and why

At intake, several people suspected the pricing service deploy that happened four days ago, and the initial working hypothesis was that that deploy introduced the errors. That hypothesis rested on timing only and was held with low confidence.

The understanding changed when log analysis results were received in the Part 2 update:

- What changed: the leading explanation moved from the pricing service deploy to a connection leak in the report generation path of the checkout service.
- Why it changed: timestamp analysis showed the 500 errors began seven days ago, three days before the pricing service deploy. A deploy cannot have introduced errors that were already occurring three days before it. The error rate also correlated with report generation traffic and did not correlate with pricing calls. Code inspection of the report generation path then found database connections opened without reliable closing on error paths, exhausting the 50 connection pool under load.
- Which account is authoritative now: the later, evidence based account is authoritative. The established cause of the main problem is the database connection leak on error paths in the report generation path of the checkout service, leading to connection pool exhaustion under load. The pricing service deploy is exonerated.
- What evidence settled it: the error log timestamps establishing the start seven days ago, the correlation with report generation traffic and lack of correlation with pricing calls, and the code inspection finding on connection handling in the report generation path.

The initial hypothesis was replaced, not edited away, and remains recorded as invalidated.

## 6. Open questions and missing information

- The cause of the rare timeout in the payment webhook handler, about 1 in 2,000 calls, remains unexplained. It is flagged here with no cause guessed. The material states only that it does not correlate with the pool exhaustion pattern and links it to no other cause.
- No post merge error rate is recorded, so the effect of the merged fix on the observed 500 error rate is missing information.
- No precise calendar start date for the errors is given in the material. The start is recorded only in relative terms, as seven days ago, with the pricing service deploy four days ago.
- No other missing information is specified in the handoff material.

## 7. Next actions

In order:

1. Check the post merge error rate and connection pool behaviour for the checkout service to establish whether the merged fix has removed the pool exhaustion pattern observed before the fix. Do not redo the completed fix.
2. Investigate the payment webhook handler timeout as a separate issue, gathering evidence on when it occurs and what it does or does not correlate with, without attributing it to the pool problem or the pricing service in advance.
3. Keep the pricing service deploy treated as exonerated unless new evidence emerges. Do not roll back any service without evidence that the rollback target caused the problem, and keep any code changes within the checkout service repository under the change freeze.

## 8. Incident follow-up note

Current status: the main cause of the intermittent checkout 500 errors, about 2% of requests and clustered at busy times, has been identified and a fix has been merged.

What was fixed: the report generation path in the checkout service did not reliably close database connections on error paths, exhausting the 50 connection pool under load. Connections are now released via a context manager on all paths, including error paths, and a regression test was included.

What was ruled out and why: the pricing service deploy was ruled out because timestamp analysis showed the errors began seven days ago, three days before that deploy, and the error rate did not correlate with pricing calls. It correlated with report generation traffic instead.

What is being investigated next: the post merge error rate, which is not yet recorded, and a separate rare timeout in the payment webhook handler, about 1 in 2,000 calls, whose cause is still unknown.
