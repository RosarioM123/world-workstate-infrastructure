# Task S2 Work Journal: Checkout Incident Debugging

Project: Checkout service intermittent HTTP 500 errors
Session: Agent A, Experiment 003, Task S2
Basis: Scenario materials in tasks/S2/scenario.md only, worked in order, Part 1 first and then the Part 2 update.

## Entry 1: Incident intake (Part 1)

Received the incident report from the support team account in the scenario materials.

Facts as reported at intake:
- The checkout service returns intermittent HTTP 500 errors.
- The error rate is roughly 2% of requests.
- The errors are clustered at busy times.
- The errors began appearing "recently", according to the support team. No precise start date was given at this stage.
- A deploy of the separate pricing service happened four days ago.
- Several people suspect that pricing service deploy.

What was not yet known at intake:
- The actual start date of the errors.
- Whether the error rate tracked pricing service calls, any other traffic pattern, or load in general.
- Any code level cause in either service.

## Entry 2: Standing constraints recorded (Part 1)

Recorded before any fix or rollback was considered:
- Change freeze: during the incident, code changes are allowed only in the checkout service repository.
- No rollback of any service without evidence that the rollback target caused the problem.

These constraints ruled out an immediate rollback of the pricing service on suspicion alone.

## Entry 3: Initial working hypothesis formed (Part 1)

Formed an initial working hypothesis, labelled as a hypothesis and not a finding:
- Hypothesis: the pricing service deploy four days ago introduced the errors.

Basis given in the materials: timing gossip only. The deploy was recent and close in time to when the support team noticed the errors. No log evidence, code evidence, or correlation evidence supported it at this stage.

Confidence at formation: low. It was the leading hypothesis to test, not a conclusion.

Planned checks implied by the hypothesis:
- Establish when the 500 errors actually began, from timestamps.
- Check whether the error rate correlates with pricing calls.

## Entry 4: Log analysis results received (Part 2 update)

Received the Part 2 update mid session, containing log analysis results. This evidence changed the leading hypothesis.

Findings from timestamp analysis of the checkout error logs:
- The 500 errors began seven days ago.
- That start is three days before the pricing service deploy, which happened four days ago.
- The pricing service deploy is therefore exonerated by the timeline. A deploy cannot have introduced errors that were already occurring three days before it.
- The error rate correlates with report generation traffic.
- The error rate does not correlate with pricing calls.

Effect on the investigation:
- The initial hypothesis in Entry 3 was invalidated by this timeline evidence and was replaced, not edited away. It remains recorded here and in the state bundle as invalidated.
- Attention shifted from the pricing service to the report generation path in the checkout service, following the correlation with report generation traffic.
- No rollback of the pricing service was made, consistent with the standing constraint requiring evidence before a rollback.

## Entry 5: Code inspection of the report generation path (Part 2)

Received code inspection evidence for the report generation path in the checkout service.

Findings:
- The report generation path in the checkout service opens database connections without reliably closing them on error paths.
- Under load, the connection pool, which has 50 connections, is exhausted.
- Once the pool is exhausted, subsequent checkout requests fail with 500s.

This mechanism fits the intake pattern: errors clustered at busy times, when report generation traffic and load are highest, and a rate of roughly 2% rather than a total outage.

This became the established cause of the main problem: a database connection leak on error paths in the report generation path of the checkout service, leading to connection pool exhaustion under load.

## Entry 6: Fix written and merged (Part 2)

Action taken, within the change freeze because the change was in the checkout service repository:
- A fix was written and merged.
- Connections are now released via a context manager on all paths, including error paths.
- A regression test was included with the fix.

Status at the end of the session: the fix for the main cause is merged. No claim is made in the materials about post merge error rates, so no post merge outcome is recorded here.

## Entry 7: Separate remaining symptom noted (Part 2)

Noted a separate given fact in the Part 2 update:
- A rare timeout in the payment webhook handler is still occurring.
- Frequency: about 1 in 2,000 calls.
- It is still unexplained.
- It does not correlate with the pool exhaustion pattern.

Treatment in this session:
- Recorded as an open question, cause unknown.
- Not attributed to the connection pool problem, because the materials state it does not correlate with that pattern.
- Not attributed to the pricing service either. No evidence in the materials links it to any cause.
- No fix is recorded for this symptom.

## Session summary

- Started with: a suspected pricing service deploy, based on timing only.
- Settled by evidence: the errors began before that deploy, the deploy was exonerated, the error rate tracked report generation traffic, and code inspection found a connection leak on error paths in that path that exhausts the 50 connection pool under load.
- Fixed and merged: connection release via a context manager on all paths in the checkout service, with a regression test.
- Still open: the rare payment webhook handler timeout, about 1 in 2,000 calls, cause unknown.
