# Continuation Document: S1 API Rate Limiting

## 1. Where things stand

Current design, as decided:

- Algorithm: token bucket (Decision D5). This is the authoritative decision, but its implementation exists only on a prototype branch and is not recorded as merged.
- Storage: rate limit counters in Redis, with a shared key per client (Decision D2).
- Default limit: 600 requests per minute per client (Decision D6), effective with this release. The materials do not state that this change is merged.

Already merged:

- T1: The rate limit middleware skeleton is written and merged behind a feature flag.
- T2: The counter storage fix, moving counters to Redis with a shared key per client, is merged and covered by a regression test.

Not merged, based only on the handoff material:

- T3: The token bucket replacement is in progress, with implementation on a prototype branch only.
- T4: The change of the default limit to 600 requests per minute per client is proposed in task terms, with the product decision made. Merge is not stated in the materials.

Current test status:

- The test suite has one intermittently failing test, `test_burst_allowance`, which fails roughly one run in five. Its root cause is not yet identified.
- Everything else is reported as green. No run identifier or full output is given in the materials, so this is a reported status, not a reproduced run.
- The Redis counter fix is covered by a regression test, but the test name, run identifier, pass count, and output values are not given in the materials.

## 2. Decisions in force

Decisions that currently govern the implementation:

- D2: Store rate limit counters in Redis with a shared key per client. Reason: in process memory counters reset on every deploy and differed per instance. Redis gives a single shared counter per client across the 6 instances and persists usage across deploys. Redis is already a dependency and is operated in all environments, so this adds no new external dependency. Implementation status: merged, covered by a regression test.
- D5: Use a token bucket algorithm instead of a fixed window counter. Reason: a load test of the fixed window implementation showed clients can send 2x the limit around window edges, and the load test report recommends token bucket. The prototype branch implementation passed the same load test without boundary bursts. Implementation status: accepted, planned, not merged. Implementation exists on a prototype branch only.
- D6: Set the default limit to 600 requests per minute per client, effective with this release. Reason: support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting decided on 600 requests per minute per client in response. Implementation status: accepted, planned, not merged in the materials.

Decisions no longer in force:

- D1: Keep rate limit counters in process memory. Superseded by D2.
- D3: Use a fixed window counter algorithm. Superseded by D5.
- D4: Set the default limit to 100 requests per minute per client. Superseded by D6.

## 3. Assumptions and facts

Established facts, from measurements and merged work recorded in the material:

- The service runs 6 instances behind a load balancer.
- Redis is already a dependency of the service.
- The rate limit middleware skeleton is merged behind a feature flag.
- The fix moving counters to Redis with a shared key per client is merged and covered by a regression test.
- A load test of the fixed window implementation showed clients can send 2x the limit around window edges: 100 requests at the end of one window plus 100 at the start of the next.
- The prototype token bucket implementation passed the same load test without boundary bursts.
- Support reported that a legitimate batch client is being throttled at 100 requests per minute.

Assumptions, labeled as assumptions:

- A1, assumption, confidence high, active: Redis is available in every environment this service runs in. Redis is operated in all environments and is already a service dependency, so Redis backed counters can be used everywhere the gateway runs.
- A2, assumption, confidence high, validated: A shared Redis key per client gives one consistent count across instances and across deploys. Validated in the record only to the extent that the fix is merged and covered by a regression test. No test output values are given.
- A3, assumption, confidence low, active and unverified: The token bucket implementation, as implemented on the prototype branch, meets the 5 ms p99 latency budget, adding no more than 5 ms at p99. No latency measurement for token bucket is given in the materials. The load test evidence covers boundary bursts only. This must not be treated as a result.
- A4, assumption, confidence medium, active: A default of 600 requests per minute per client resolves the throttling of the legitimate batch client, without further changes for that client. The materials give no usage figures for that client beyond the fact that it is throttled at 100, and no data on other clients.
- A5, assumption, confidence medium, active: Everything in the test suite other than `test_burst_allowance` is currently passing. This is a reported status, not a test run reproduced in the material. No run identifier or full output is given.

## 4. Constraints

- C1: No new external dependencies beyond what the service already uses. Redis is already a dependency.
- C2: Rate limiting may add at most 5 ms at p99.
- C3: Counters must survive deploys. A deploy must not reset clients' usage.
- C4: Rate limiting must be consistent across instances. The service runs 6 instances behind a load balancer.

The definition of done in the material also requires: one per client limit enforced consistently across all instances, survival across deploys, staying within the latency budget, and a green test suite with no unexplained intermittent failures.

## 5. What changed and why

Change 1: Counter storage.

- From: D1, counters held in the memory of each gateway process.
- To: D2, counters stored in Redis with a shared key per client.
- Why: In process memory counters reset on every deploy and differed per instance.
- Authoritative now: D2.
- Evidence: E1, E2, and E3. The fix is merged and covered by a regression test.

Change 2: Counting algorithm.

- From: D3, fixed window counter, chosen initially as the simplest to implement.
- To: D5, token bucket algorithm.
- Why: A load test of the fixed window implementation showed clients can send 2x the limit around window edges, 100 requests at the end of one window plus 100 at the start of the next. The load test report recommends token bucket, and the prototype branch implementation passed the same load test without boundary bursts.
- Authoritative now: D5, as the accepted decision. Its implementation is on a prototype branch only and is not recorded as merged.
- Evidence: E4, the load test report.

Change 3: Default limit.

- From: D4, 100 requests per minute per client, taken from the original API spec.
- To: D6, 600 requests per minute per client, effective with this release.
- Why: Support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting decided on 600 requests per minute per client in response.
- Authoritative now: D6, as the accepted decision. The materials do not state that the change is merged.
- Evidence: E5, the product review meeting notes.

## 6. Open questions and missing information

- Q1: What is the root cause of the intermittent `test_burst_allowance` failure? The test fails roughly one run in five. Cause: unknown. It has not been identified in the materials, and no cause is asserted here. In particular, the material gives no basis to assume it is caused by the algorithm change, the limit change, or timing.
- Q2: Does the token bucket implementation stay within the 5 ms p99 latency budget? Missing information: no latency measurement for token bucket is given. The load test evidence addresses boundary bursts only.
- Q3: Have the token bucket branch and the 600 limit been merged and released? Missing information: D5 is recorded as prototype branch only and D6 as effective with this release, and neither is stated as merged. Merge and release state must be verified from the repository, not assumed from the handoff material.
- Q4: Is 600 requests per minute per client the right default for clients other than the reported batch client? Missing information: no wider client usage data is given, so the effect on other clients is unassessed. No usage figures for the reported batch client are given beyond throttling at 100.
- Other missing information: the regression test for the Redis counter fix has no test name, run identifier, pass count, or output values in the materials. The reported green status of the rest of the suite has no run identifier or full output.

## 7. Next actions

In order:

1. Verify the real merge and release state of the token bucket prototype branch (D5, T3) and of the 600 requests per minute per client limit (D6, T4) in the repository, since the handoff material records both as not merged.
2. Investigate the root cause of the intermittent `test_burst_allowance` failure (T5, Q1), without assuming a cause. Preserve the failure evidence needed for diagnosis.
3. Measure the latency of the token bucket implementation against the 5 ms p99 budget in C2 (Q2, A3), since no such measurement exists in the materials.
4. Merge the token bucket implementation, once its latency and test status are established, so the merged implementation matches D5.
5. Apply and merge the default limit of 600 requests per minute per client for this release, so the merged implementation matches D6.
6. Assess, using client usage data not present in the handoff material, whether the 600 default is appropriate for clients other than the reported batch client (Q4, A4).
7. Before release, verify the full criteria in section 8, including a green test suite with no unexplained intermittent failures.

These steps do not redo the merged middleware skeleton or the merged Redis counter fix, and they do not revert any earlier fix.

## 8. Implementation plan

Remaining work is to land the two accepted but unmerged decisions, D5 token bucket and D6 default limit of 600 requests per minute per client, on top of the merged middleware skeleton and Redis counter storage.

First, confirm the actual merge state of both changes in the repository. Next, attack the outstanding test problem by reproducing the intermittent `test_burst_allowance` failure, which occurs roughly one run in five, and collecting evidence about when it fails, without assuming a cause in advance. In parallel where possible, measure token bucket latency against the 5 ms p99 budget, since that is currently unverified.

Before release, verify: the load test no longer shows boundary bursts, counters remain shared across all 6 instances and survive a deploy, latency stays within budget, the 600 limit is in effect, and the full test suite is green with no unexplained intermittent failures.
