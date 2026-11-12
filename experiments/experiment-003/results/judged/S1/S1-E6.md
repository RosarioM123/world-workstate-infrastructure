# Continuation Document: S1 API Rate Limiting

## 1. Where things stand

The project is active. Its goal is to add rate limiting to the gateway service that is consistent across instances, stays within the latency budget, and does not reset client usage on deploys. The definition of done is a merged implementation that enforces one per client limit consistently across all instances, survives deploys, stays within the latency budget, and has a green test suite with no unexplained intermittent failures.

The current governing design is:

- Storage: counters in Redis, with a shared key per client.
- Algorithm: token bucket, by accepted decision. The token bucket implementation exists on a prototype branch only and is not recorded as merged.
- Default limit: 600 requests per minute per client, by accepted decision, effective with this release. Its merge is not stated in the handoff material.

Already merged:

- The rate limit middleware skeleton, merged behind a feature flag (task T1, done).
- The counter storage fix that moved counters from process memory to Redis with a shared key per client, merged and covered by a regression test (task T2, done).

Not recorded as merged:

- The token bucket replacement for the fixed window algorithm (task T3, in progress, prototype branch only).
- The change of the default limit to 600 requests per minute per client (task T4, proposed in the task list; the product decision is recorded as made and effective with this release, but merge is not stated).

Current test status: the test suite has one intermittently failing test, `test_burst_allowance`, which fails roughly one run in five. Its root cause is not yet identified. Everything else is reported as green. No run identifier or full test output is given in the handoff material. Finding the root cause of the intermittent failure is task T5, which is blocked on diagnosis.

## 2. Decisions in force

Decisions that currently govern the implementation:

- D2: Store rate limit counters in Redis with a shared key per client. Reason: counters in process memory reset on every deploy and differed per instance, while Redis gives a single shared counter per client across the 6 instances and persists usage across deploys. Redis is already a dependency and is operated in all environments, so this adds no new external dependency. Implementation status: merged, covered by a regression test.
- D5: Use a token bucket algorithm instead of a fixed window counter. Reason: a load test of the fixed window implementation showed clients can send 2x the limit around window edges, 100 requests at the end of one window plus 100 at the start of the next. The load test report recommends token bucket, and the prototype branch implementation passed the same load test without boundary bursts. Implementation status: accepted, planned, not merged; implementation exists on a prototype branch only.
- D6: Set the default limit to 600 requests per minute per client, effective with this release. Reason: support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting decided on 600 requests per minute per client in response. Implementation status: accepted, planned, not merged; the handoff material states the decision and that it is effective with this release, but does not state that the change is merged.

Decisions no longer in force:

- D1: Keep rate limit counters in process memory. Superseded by D2. This was the early implementation approach; the handoff material describes it as the early bug and gives no fuller rationale.
- D3: Use a fixed window counter algorithm. Superseded by D5. Its reason was that it was simplest to implement, as the initial algorithm choice at the start of the session.
- D4: Set the default limit to 100 requests per minute per client. Superseded by D6. Its value was taken from the original API spec and was the default at the start of the session.

## 3. Assumptions and facts

Established facts:

- The service runs 6 instances behind a load balancer, and the team operates Redis in all environments (E1).
- A rate limit middleware skeleton is written and merged behind a feature flag (E2).
- Counters were initially kept in process memory, so they reset on every deploy and differed per instance (E2).
- The fix moved counters to Redis with a shared key per client, was merged, and is covered by a regression test (E2, E3). No test name, run identifier, pass count, output, or measurement from that regression test is given.
- A load test of the fixed window implementation showed clients can send 2x the limit around window edges (E4). The prototype token bucket implementation passed the same load test without boundary bursts (E4). No latency figures are given in that report summary.
- Support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting decided the default becomes 600 requests per minute per client effective with this release (E5).
- The test suite currently has one intermittently failing test, `test_burst_allowance`, failing roughly one run in five, with root cause not yet identified, and everything else is green (E6). No run identifier is given.

Assumptions:

- A1: Redis is available in every environment this service runs in. The statement is that Redis is operated in all environments and is already a service dependency, so Redis backed counters can be used everywhere the gateway runs. Confidence: high. Status: active.
- A2: A shared Redis key per client gives one consistent count across instances and across deploys. Confidence: high. Status: validated, only to the extent that the fix is merged and covered by a regression test; no test output values are given.
- A3: The token bucket implementation meets the 5 ms p99 latency budget. Confidence: low. Status: active and unverified. No latency measurement for token bucket is given; the load test evidence covers boundary bursts only. This must not be treated as a result.
- A4: A default of 600 requests per minute per client resolves the throttling of the legitimate batch client, without further changes for that client. Confidence: medium. Status: active. The material gives no usage figures for that client beyond it being throttled at 100, and no data on other clients.
- A5: Everything in the test suite other than `test_burst_allowance` is currently passing. Confidence: medium. Status: active. This is a reported status, not a test run reproduced in the handoff material; no run identifier or full output is given.

## 4. Constraints

- C1: No new external dependencies beyond what the service already uses. Redis is already a dependency.
- C2: Rate limiting may add at most 5 ms at p99.
- C3: Counters must survive deploys. A deploy must not reset clients' usage.
- C4: Rate limiting must be consistent across instances. The service runs 6 instances behind a load balancer.

## 5. What changed and why

Storage change:

- From: D1, counters kept in the memory of each gateway process.
- To: D2, counters stored in Redis with a shared key per client.
- Why: in process memory, counters reset on every deploy and differed per instance. Redis gives a single shared counter per client across the 6 instances and persists usage across deploys, and Redis is already a dependency operated in all environments.
- Authoritative now: D2.
- Evidence: E1, E2, and E3. The fix is merged and covered by a regression test.

Algorithm change:

- From: D3, fixed window counter, chosen initially as simplest to implement.
- To: D5, token bucket algorithm.
- Why: a load test of the fixed window implementation showed clients can send 2x the limit around window edges, 100 requests at the end of one window plus 100 at the start of the next. The load test report recommends token bucket, and the prototype branch implementation passed the same load test without boundary bursts.
- Authoritative now: D5.
- Evidence: E4. Implementation status: prototype branch only, not merged.

Default limit change:

- From: D4, 100 requests per minute per client, taken from the original API spec.
- To: D6, 600 requests per minute per client, effective with this release.
- Why: support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting decided on 600 in response.
- Authoritative now: D6.
- Evidence: E5. Implementation status: decision recorded as made and effective with this release, but merge is not stated.

## 6. Open questions and missing information

- Q1: What is the root cause of the intermittent `test_burst_allowance` failure? The test fails roughly one run in five. Cause: unknown. It has not been identified in the handoff material, and no cause is asserted. Do not assume it is caused by the algorithm change, the limit change, or timing; the material gives no cause. This blocks task T5.
- Q2: Does the token bucket implementation stay within the 5 ms p99 latency budget? No latency measurement for token bucket is given. The load test evidence addresses boundary bursts only. This measurement is missing before the budget in C2 can be called met for the new algorithm.
- Q3: Have the token bucket branch and the 600 limit been merged and released? D5 is recorded as prototype branch only and D6 as effective with this release; neither is stated as merged. Merge and release state must be verified from the repository and is missing from the handoff material.
- Q4: Is 600 requests per minute per client the right default for clients other than the reported batch client? The material gives a support report about one legitimate batch client and the product decision that followed, but no wider client usage data, so the effect on other clients is unassessed.
- Missing information: no regression test name, run identifier, pass count, or output for the Redis fix; no latency figures for token bucket; no usage figures for the reported batch client beyond throttling at 100; no data on other clients; no run identifier or full output for the current test suite status.

## 7. Next actions

1. Address Q1 first: investigate the intermittent `test_burst_allowance` failure, which fails roughly one run in five with cause unknown, without assuming a cause.
2. Verify the real merge state of the token bucket prototype branch (D5, task T3) in the repository, since the handoff material records it as not merged.
3. Verify the real merge state of the 600 requests per minute per client default (D6, task T4) in the repository, since the handoff material does not state that it is merged.
4. Obtain a latency measurement for the token bucket implementation against the 5 ms p99 budget in C2 (Q2, assumption A3).
5. Complete and merge the token bucket implementation (task T3), honouring D5, once its merge state is known.
6. Apply and merge the 600 requests per minute per client default (task T4), honouring D6, once its merge state is known.
7. Assess, with wider client usage data if it can be obtained, whether the 600 default is right for clients other than the reported batch client (Q4) and whether it resolves that client's throttling (assumption A4).
8. Confirm the full test suite is green with no unexplained intermittent failures, as required by the definition of done.

## 8. Implementation plan

Remaining work is to finish task T3, apply task T4, and resolve task T5. First verify in the repository whether the token bucket prototype branch and the 600 requests per minute per client default are merged, because the handoff material records token bucket as prototype only and does not state that the limit change is merged. Then bring the prototype token bucket implementation to merge, keeping Redis counters with a shared key per client, and set the default limit to 600.

For the outstanding test problem, reproduce the intermittent `test_burst_allowance` failure by running it repeatedly, record how often it fails and under what observed conditions, and diagnose from those observations only; the cause is currently unknown and must not be assumed. Fix only what the evidence supports.

Before release, verify a latency measurement for token bucket against the 5 ms p99 budget, rerun the load test to confirm no boundary bursts, keep the Redis regression test passing, and require a green suite with no unexplained intermittent failures.
