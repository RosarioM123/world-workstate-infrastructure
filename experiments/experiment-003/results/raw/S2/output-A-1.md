# Continuation Document: Checkout Incident Investigation

## 1. Where things stand

The checkout service returned intermittent HTTP 500 errors at roughly 2% of requests, clustered at busy times.

The main problem has been established: a database connection leak on error paths in the report generation path of the checkout service. That path opened database connections without reliably closing them on error paths. Under load, the leak exhausted the 50 connection pool, and subsequent checkout requests failed with 500s.

What has been fixed: a fix was written and merged. Database connections are now released via a context manager on all paths, including error paths, in the report generation path, and a regression test was included.

What remains open:

- A rare timeout in the payment webhook handler, about 1 in 2,000 calls, is still occurring and is unexplained. It is treated as a separate problem. It does not correlate with the pool exhaustion pattern.
- The measured post merge error rate for the main 500 pattern is not given in the handoff material. The merged fix must not be mistaken for a measured recovery.

## 2. Decisions in force

**D1: Do not roll back the pricing service on suspicion alone.**
Do not roll back the pricing service at intake, and investigate the timeline and correlations first. Reason: Constraint C-2 bars a rollback without evidence that the rollback target caused the problem. At intake, the only basis was timing gossip about a deploy four days ago, which was a hypothesis, not evidence.

**D2: Treat the report generation connection leak as the established main cause.**
Treat the main cause as a database connection leak on error paths in the report generation path of the checkout service, exhausting the 50 connection pool under load, and no longer treat the pricing service deploy as the cause. Reason: log timestamp analysis shows the errors began seven days ago, three days before the pricing deploy, and the error rate correlates with report generation traffic rather than pricing calls. Code inspection then found the exact leak mechanism in that path. Evidence: E2 and E3.

**D3: Fix the connection leak in the checkout service with a context manager and a regression test.**
Release database connections via a context manager on all paths, including error paths, in the report generation path, with a regression test, and merge that fix. Reason: the leak was on paths where connections were not reliably closed, so release must hold on all paths. The change is in the checkout service repository, so it complies with the change freeze in Constraint C-1. The handoff material states the fix was written and merged. Evidence: E3 and E4.

**D4: Treat the payment webhook timeout as a separate open problem.**
Record the rare payment webhook handler timeout as a separate unexplained symptom, and do not attribute it to the connection pool exhaustion or to the pricing service. Reason: the handoff material states the timeout is still occurring, is unexplained, and does not correlate with the pool exhaustion pattern. No evidence in the material links it to any other cause. Evidence: E5.

### Decisions or hypotheses that are no longer in force

- **A1: Pricing service deploy introduced the errors (initial hypothesis).** No longer in force. It is invalidated, not deleted. Reason: E2 shows the errors began seven days ago, three days before the deploy, and the error rate does not correlate with pricing calls. No decision record is listed in the handoff material as superseded. D2 supersedes the working position based on A1.

## 3. Assumptions and facts

### Established findings

- **E1, incident report:** Checkout service returned intermittent HTTP 500 errors, roughly 2% of requests, clustered at busy times. The support team reported that the errors began appearing "recently." That onset wording was a report, not a measured start date. A deploy of the separate pricing service happened four days ago and several people suspected it.
- **E2, log analysis:** Timestamp analysis of the checkout error logs shows the 500 errors began seven days ago, three days before the pricing service deploy. The error rate correlates with report generation traffic, not with pricing calls.
- **E3, code inspection:** The report generation path in the checkout service opens database connections without reliably closing them on error paths. Under load the connection pool, 50 connections, is exhausted, and subsequent checkout requests fail with 500s.
- **E4, fix:** A fix was written and merged. Connections are now released via a context manager on all paths, with a regression test. No commit identifier, pull request identifier, or post merge measurement is given in the handoff material.
- **E5, remaining symptom:** Separately, a rare timeout in the payment webhook handler, about 1 in 2,000 calls, is still occurring and is unexplained. It does not correlate with the pool exhaustion pattern.

### Assumptions still in play

- **A2, labeled as an assumption in the handoff material, status validated, confidence high:** The report generation path leaking database connections on error paths, exhausting the 50 connection pool under load, is the cause of the main intermittent 500 pattern, including its clustering at busy times. Validated by E3 and supported by E2 correlation with report generation traffic. The handoff material notes that no post merge error rate is given, so this validation rests on the timeline, correlation, and code inspection evidence, not on a measured recovery.
- **A3, labeled as an assumption in the handoff material, status active, confidence low:** No causal assumption is adopted for the payment webhook handler timeout. This entry makes the absence explicit. The timeout is open question Q1, with cause unknown.

### Hypothesis that is not an established finding and is no longer in play

- **A1, confidence was low, status invalidated:** The pricing service deploy four days ago introduced the intermittent checkout HTTP 500 errors. At formation its basis was timing gossip only, with no log, code, or correlation evidence. It was invalidated by E2.

## 4. Constraints

- **C-1, change freeze:** During the incident, code changes are allowed only in the checkout service repository.
- **C-2, no rollback without evidence:** No rollback of any service without evidence that the rollback target caused the problem.
- **C-3, use only the scenario materials:** A hypothesis is not a finding, and hypotheses are labelled as assumptions until evidence settles them.
- **C-4, keep replaced hypotheses visible:** When a hypothesis is replaced, keep the old one visible as superseded or invalidated with the reason.

## 5. What changed and why

At intake, the working position was hypothesis A1: the pricing service deploy four days ago introduced the errors. Its basis was timing gossip only. The support team had said the errors began "recently," the deploy was recent, and several people suspected the deploy. It was labelled a hypothesis, not a finding, and held at low confidence.

That understanding changed when log analysis, E2, arrived. It showed the errors began seven days ago, three days before the pricing deploy, and that the error rate correlates with report generation traffic rather than pricing calls. For that reason A1 was invalidated and retained visibly in the record.

The investigation was redirected to the report generation path, and assumption A2 was created as the replacement working hypothesis. Code inspection, E3, then supplied the mechanism: the report generation path did not reliably close database connections on error paths, the 50 connection pool was exhausted under load, and subsequent checkout requests failed with 500s. A2 was then recorded as validated, with high confidence, validated by E3 and supported by E2. Decisions D2 and D3 followed, recording the leak as the main cause and the merged context manager fix with a regression test.

The authoritative account now is D2: the main cause is the database connection leak on error paths in the report generation path of the checkout service, not the pricing service deploy. The evidence that settled it is E2, the timeline and correlation, together with E3, the code inspection that found the leak mechanism.

Separately, E5 recorded the rare payment webhook handler timeout as still occurring and unexplained, and D4 recorded it as a separate open problem.

## 6. Open questions and missing information

- **Q1, open:** What causes the rare timeout in the payment webhook handler, about 1 in 2,000 calls, which is still occurring and unexplained? Its cause is unknown. It does not correlate with the pool exhaustion pattern, so the connection leak fixed under D3 does not explain it. No cause is guessed here.
- **Q2, open:** What is the measured checkout 500 error rate after the context manager fix was merged? The handoff material states the fix was written and merged but gives no post merge measurement.
- **Missing information:** No commit identifier or pull request identifier for the merged fix is given in the handoff material. No post merge error rate is given. No evidence linking the webhook timeout to any cause is given, and no causal assumption for the timeout has been adopted.

## 7. Next actions

1. Obtain the measured post merge checkout 500 error rate for the main pattern, Q2, before claiming recovery.
2. Investigate Q1, the payment webhook handler timeout, as a separate open problem, starting from E5: about 1 in 2,000 calls, still occurring, unexplained, and not correlated with the pool exhaustion pattern. Do not attribute it to the pool exhaustion or to the pricing service without evidence.
3. Keep the pricing service deploy ruled out unless new evidence answers the timeline problem in E2, namely that the errors began three days before the deploy. Do not roll back any service without evidence that the rollback target caused the problem, per C-2.
4. In any further incident work, keep code changes only in the checkout service repository, per C-1, and keep hypotheses labelled as assumptions until evidence settles them, per C-3. Keep A1 visible as invalidated with its reason, per C-4.
5. Do not redo the completed fix under D3 and E4: the context manager release on all paths, with a regression test, is already written and merged.

## 8. Incident follow-up note

Current status: the main cause of the intermittent checkout 500 errors is established and a fix is merged. A separate rare payment webhook handler timeout, about 1 in 2,000 calls, is still occurring and remains unexplained.

What was fixed: the report generation path in the checkout service leaked database connections on error paths, exhausting the 50 connection pool under load. Connections are now released via a context manager on all paths, with a regression test.

What was ruled out and why: the pricing service deploy was ruled out because log analysis shows the errors began seven days ago, three days before that deploy, and the error rate correlates with report generation traffic, not pricing calls.

What is being investigated next: the cause of the webhook timeout, as a separate problem, and the measured post merge 500 error rate, which is not yet recorded. No recovery claim is made until that rate is obtained.
