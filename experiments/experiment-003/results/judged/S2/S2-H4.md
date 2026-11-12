# Continuation Document: Checkout Incident Investigation

## 1. Where things stand

The checkout service has been returning intermittent HTTP 500 errors, at a rate of roughly 2% of requests, clustered at busy times.

The established cause of the main problem is a database connection leak in the report generation path of the checkout service. That path opened database connections without reliably closing them on error paths. Under load, the connection pool, which has 50 connections, is exhausted, and subsequent checkout requests then fail with 500s. This mechanism fits the reported pattern of errors clustered at busy times and a rate of roughly 2% rather than a total outage.

What has been fixed: a fix for the main cause was written and merged in the checkout service repository. Connections are now released via a context manager on all paths, including error paths, and a regression test was included with the fix.

What remains open: a rare timeout in the payment webhook handler is still occurring, at about 1 in 2,000 calls. It is unexplained, and it does not correlate with the pool exhaustion pattern. No fix is recorded for this symptom. No information is given in the handoff material about post merge error rates, so whether the merged fix has changed the observed error rate in operation is not recorded.

## 2. Decisions in force

Decisions that currently govern the incident response:

- Do not roll back the pricing service. Reason: there is no evidence that it caused the problem, the timeline evidence exonerates it, and the standing constraint requires evidence before any rollback.
- Focus the investigation of the main problem on the report generation path in the checkout service rather than on the pricing service. Reason: the error rate correlates with report generation traffic and does not correlate with pricing calls, and code inspection found the connection leak in that path.
- Use connection release via a context manager on all paths, including error paths, as the fix approach for the connection leak in the checkout service, with a regression test. Reason: this directly addresses the leak found on error paths. This fix has been written and merged.
- Treat the rare payment webhook handler timeout as a separate open issue, not attributed to the connection pool problem or to the pricing service. Reason: the handoff material states that it does not correlate with the pool exhaustion pattern, and no evidence links it to any other cause.

Decisions or hypotheses that are no longer in force:

- The initial working hypothesis that the pricing service deploy four days ago introduced the errors. This hypothesis was based on timing only, had low confidence at formation, and was invalidated by timeline evidence. It has been replaced, not retained.

## 3. Assumptions and facts

Established findings, distinct from hypotheses:

- The checkout service returns intermittent HTTP 500 errors, at roughly 2% of requests, clustered at busy times.
- The 500 errors began seven days ago.
- A deploy of the separate pricing service happened four days ago, which is three days after the errors began.
- The error rate correlates with report generation traffic.
- The error rate does not correlate with pricing calls.
- The report generation path in the checkout service opened database connections without reliably closing them on error paths.
- Under load, the 50 connection pool is exhausted, and subsequent checkout requests fail with 500s.
- A rare timeout in the payment webhook handler is still occurring, at about 1 in 2,000 calls, and it does not correlate with the pool exhaustion pattern.

Assumptions still in play:

- No assumptions are recorded as still in play in the handoff material. The only hypothesis recorded, the pricing service deploy hypothesis, is no longer in force, as noted in Section 2, and the cause of the main problem is recorded as established by code inspection and log analysis rather than as an assumption.
- No assumption about the cause of the payment webhook handler timeout is recorded, and none should be treated as in play. Its cause is unknown.

## 4. Constraints

Standing constraints on the incident response, recorded before any fix or rollback was considered:

- Change freeze: during the incident, code changes are allowed only in the checkout service repository.
- No rollback of any service without evidence that the rollback target caused the problem.

## 5. What changed and why

The understanding of the incident changed during the prior session in the following way.

At intake, several people suspected the deploy of the separate pricing service that happened four days ago, and the initial working hypothesis, held with low confidence, was that this deploy introduced the errors. Its basis was timing only, with no log, code, or correlation evidence.

That account is no longer authoritative. Log analysis in the Part 2 update showed that the 500 errors began seven days ago, three days before the pricing service deploy. A deploy cannot have introduced errors that were already occurring three days before it, so the pricing service deploy was exonerated and the initial hypothesis was invalidated.

The same log analysis showed that the error rate correlates with report generation traffic and does not correlate with pricing calls. Attention therefore shifted to the report generation path in the checkout service. Code inspection of that path then found the connection leak on error paths, leading to exhaustion of the 50 connection pool under load.

The authoritative account now is the later account: the main problem was caused by the database connection leak on error paths in the report generation path of the checkout service, leading to connection pool exhaustion under load. The evidence that settled the change was the timestamp analysis of the checkout error logs, the correlation analysis, and the code inspection findings.

## 6. Open questions and missing information

- The cause of the rare timeout in the payment webhook handler, at about 1 in 2,000 calls, remains unexplained. It does not correlate with the pool exhaustion pattern, and no cause is given in the handoff material. Do not guess a cause.
- The post merge outcome is missing: no information is given about post merge error rates, so it is not recorded whether the observed 500 error rate has fallen since the fix was merged.
- No precise calendar start date for the errors is given. The handoff material gives relative timing only: the errors began seven days ago and the pricing service deploy happened four days ago.
- No information is given linking the payment webhook handler timeout to the pricing service, the connection pool problem, or any other cause.

## 7. Next actions

In order, without redoing completed fixes and without proposing anything the constraints prohibit:

1. Check the observed checkout 500 error rate after the merged fix, using the log evidence approach already used in the investigation, to establish the post merge outcome that is not yet recorded.
2. Investigate the rare payment webhook handler timeout as a separate issue: gather evidence on when it occurs and what it does or does not correlate with, since its cause is currently unknown.
3. Keep the pricing service out of rollback consideration unless new evidence shows that a rollback target caused a problem, in line with the standing constraint.
4. Make any further code changes only in the checkout service repository, in line with the change freeze.

## 8. Incident follow-up note

Current status: the main cause of the intermittent checkout 500 errors has been identified and a fix has been merged. The errors, which occurred at roughly 2% of requests and clustered at busy times, were caused by a database connection leak on error paths in the report generation path. Under load, the 50 connection pool was exhausted and subsequent checkout requests failed.

What was fixed: connections in that path are now released via a context manager on all paths, including error paths, and a regression test was included.

What was ruled out and why: the pricing service deploy was ruled out because the errors began seven days ago, three days before that deploy, and the error rate did not correlate with pricing calls. It did correlate with report generation traffic.

What is being investigated next: the post merge error rate, which is not yet recorded, and a separate rare payment webhook handler timeout at about 1 in 2,000 calls. That timeout is unexplained, does not correlate with the pool exhaustion pattern, and has no attributed cause.
