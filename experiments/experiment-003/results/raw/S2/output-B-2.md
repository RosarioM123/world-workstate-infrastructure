# Continuation Document

## 1. Where things stand

The incident involves intermittent HTTP 500 errors in the checkout service. At intake, the errors were reported at roughly 2% of requests and clustered at busy times.

The cause of the main problem has been established. The report generation path in the checkout service opens database connections without reliably closing them on error paths. Under load, the leaked connections exhaust the connection pool, which has 50 connections, and once the pool is exhausted, subsequent checkout requests fail with 500s. This fits the intake pattern because errors clustered at busy times, when report generation traffic and load are highest, and it accounts for a rate of roughly 2% rather than a total outage.

A fix for that cause has been written and merged in the checkout service repository. Connections are now released via a context manager on all paths, including error paths, and a regression test was included with the fix. The handoff material makes no claim about post-merge error rates, so whether the 500 error rate has changed after the merge is not established in the material.

One separate symptom remains open and unexplained: a rare timeout in the payment webhook handler, still occurring at about 1 in 2,000 calls. It does not correlate with the pool exhaustion pattern. Its cause is unknown, and no fix or owner is recorded for it in the material.

No rollback was performed.

## 2. Decisions in force

Decisions that currently govern the incident response:

- Attention is focused on the report generation path in the checkout service. Reason: log analysis showed that the error rate correlates with report generation traffic and does not correlate with pricing calls, and code inspection of that path found the connection leak.
- The fix for the main problem is the merged change that releases connections via a context manager on all paths, including error paths, with a regression test included. Reason: the leak on error paths was exhausting the connection pool under load.
- No rollback is performed. Reason: there is no evidence that a rollback target caused the problem, and the pricing service deploy suspected at first was exonerated by the timeline.
- The original pricing service hypothesis is retained in the record as invalidated, with the timeline evidence as the reason, rather than being edited away or deleted.
- The payment webhook timeout is treated as a separate open question with cause unknown. It is not attributed to the connection pool problem because it does not correlate with the pool exhaustion pattern, and it is not attributed to the pricing service because no evidence links it to any cause.

Decisions or hypotheses that are no longer in force:

- The hypothesis that a deploy of the separate pricing service four days earlier caused the 500 errors. This was the first working hypothesis of the session, based only on timing, because the deploy was recent and close in time to when the errors were noticed. Confidence in it was low from the start, and there was no log evidence, code evidence, or correlation evidence for it at that point. It is now invalidated and replaced.

## 3. Assumptions and facts

Established findings, distinct from hypotheses:

- Timestamp analysis of the checkout error logs showed that the 500 errors began seven days ago.
- The pricing service deploy happened four days ago, three days after the errors began.
- The error rate correlates with report generation traffic.
- The error rate does not correlate with pricing calls.
- The report generation path in the checkout service opens database connections without reliably closing them on error paths.
- The connection pool has 50 connections, and leaked connections exhaust it under load, after which subsequent checkout requests fail with 500s.
- The fix described in Section 2 was written and merged in the checkout service repository, with a regression test included.
- The payment webhook timeout occurs at about 1 in 2,000 calls and does not correlate with the pool exhaustion pattern.

Assumptions still in play:

- Assumption: none is recorded in the handoff material as still in play. The only hypothesis recorded at intake, the pricing service hypothesis, had low confidence from the start and is now invalidated, so it is not still in play. No confidence level is given in the material for the established findings listed above, so none is assigned here.

## 4. Constraints

- Change freeze during the incident: code changes are allowed only in the checkout service repository.
- No service is to be rolled back without evidence that the rollback target caused the problem.

These constraints ruled out rolling back the pricing service on suspicion alone. The merged fix complied with the change freeze because it was made in the checkout service repository.

## 5. What changed and why

At the start of the prior session, the understanding was incomplete and the leading account was a hypothesis. The support team said the errors had begun appearing recently, but no precise start date was known at that stage. Several people suspected the pricing service deploy from four days earlier, and that suspicion became the first working hypothesis, based on timing alone and held with low confidence. What still needed to be established was when the errors had actually begun and whether the error rate tracked pricing service calls, another traffic pattern, or load in general.

That account changed because of log analysis and code inspection. Timestamp analysis of the checkout error logs showed that the errors began seven days ago, three days before the pricing service deploy, so that deploy cannot have introduced errors that were already occurring. The same analysis showed that the error rate correlates with report generation traffic and does not correlate with pricing calls. Code inspection of the report generation path then established the connection leak on error paths and the pool exhaustion mechanism.

The authoritative account now is the report generation account: leaked database connections on error paths in the checkout service report generation path exhaust the 50 connection pool under load, and subsequent checkout requests then fail with 500s. The pricing service deploy account is superseded and invalidated. The evidence that settled it was the timestamp analysis of the checkout error logs, the correlation findings for report generation traffic and pricing calls, and the code inspection of the report generation path.

## 6. Open questions and missing information

- What causes the rare timeout in the payment webhook handler, which occurs at about 1 in 2,000 calls? The cause is unknown. It is flagged here without guessing a cause.
- Whether the webhook timeout has its own traffic, timing, or dependency pattern. This remains to be established, given that it does not follow the pool exhaustion pattern.
- No fix for the webhook timeout is recorded in the material, and no owner for it is recorded.
- Post-merge error rates are not given in the material, so the effect of the merged fix on the observed 500 error rate is missing information and is not assumed here.

## 7. Next actions

In order:

1. Establish the post-merge checkout 500 error rate from the error logs, since the material records no post-merge outcome for the merged fix. Do not redo the completed fix.
2. Investigate the payment webhook timeout as a separate open question: determine what causes it.
3. As part of that investigation, establish whether the webhook timeout has its own traffic, timing, or dependency pattern, since it does not correlate with the pool exhaustion pattern.
4. Keep all code changes within the checkout service repository under the change freeze, and do not roll back any service without evidence that the rollback target caused the problem.

## 8. Incident follow-up note

Current status: the main cause of the intermittent checkout 500 errors has been found and a fix has been merged. The report generation path in the checkout service was leaking database connections on error paths. Under load the leaks exhausted the 50 connection pool, and later checkout requests then failed with 500s.

What was fixed: connections are now released via a context manager on all paths, including error paths, and a regression test was included. The fix was made in the checkout service repository, in line with the change freeze. No post-merge error rate is available in the handoff material, so no outcome is claimed here yet.

What was ruled out and why: the pricing service deploy from four days ago was ruled out because timestamp analysis showed the errors began seven days ago, before that deploy, and the error rate does not correlate with pricing calls. It does correlate with report generation traffic.

What is being investigated next: a separate rare timeout in the payment webhook handler, at about 1 in 2,000 calls, with cause unknown. It does not follow the pool exhaustion pattern, and the next questions are what causes it and whether it has its own traffic, timing, or dependency pattern.
