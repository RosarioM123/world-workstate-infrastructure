# Continuation Document: S1 API Rate Limiting (Gateway Service)

## 1. Where things stand

The gateway fronts a multi-instance API with 6 instances behind a load balancer, so rate limiting must be consistent across instances. A limit counted separately on each instance would not be a single limit for a client.

Current design:
- Algorithm: token bucket. This is the authoritative design, superseding fixed window. The token bucket code exists on a prototype branch and is recorded as planned for merge, not merged.
- Storage: Redis, with a shared key per client. Redis is already a dependency of the service and is operated in all environments.
- Default limit: 600 requests per minute per client. This is the authoritative limit, superseding 100 requests per minute per client, effective with this release. The materials do not state that this change is merged, so it is recorded as decided and planned for this release, not merged.

Already merged:
- A rate limit middleware skeleton, behind a feature flag.
- The fix moving counters from process memory to Redis with a shared key per client. That fix is covered by a regression test. The name of that regression test is not given in the handoff material.

Current test status:
- One test, `test_burst_allowance`, fails intermittently, roughly one run in five. Its root cause is not yet identified.
- Everything else in the suite is green.

## 2. Decisions in force

Decisions that currently govern the implementation:

- Storage in Redis with a shared key per client. Reason: counters kept in process memory reset on every deploy and differed per instance, which conflicted with consistency across instances and survival across deploys. Redis was already a dependency and is operated in all environments.
- Rollout behind a feature flag, for the rate limit middleware skeleton that is already merged. Reason: recorded as the rollout guard in the design at the start of the session. No other reason is given in the material.
- Algorithm is token bucket. Reason: evidence from a load test report. The fixed window implementation allowed a boundary burst, and a prototype branch implementing token bucket passed the same load test without boundary bursts.
- Default limit is 600 requests per minute per client, effective with this release. Reason: a product review decision following a support report that a legitimate batch client was being throttled at 100 requests per minute.

Decisions that are no longer in force:

- Fixed window counter as the algorithm. Superseded by token bucket. It was originally chosen for simplicity as the simplest approach to implement.
- Default limit of 100 requests per minute per client, taken from the original API spec. Superseded by 600 requests per minute per client.
- Counters kept in process memory. Superseded by Redis storage with a shared key per client, after the bug described above was found and fixed.

## 3. Assumptions and facts

Established facts, from the handoff material:

- The gateway has 6 instances behind a load balancer.
- Redis is operated in all environments and is already a dependency of the service.
- The middleware skeleton is merged behind a feature flag.
- The move to Redis with a shared key per client is merged and covered by a regression test.
- A load test of the fixed window implementation showed clients can send 2x the limit around window edges: 100 requests at the end of one window plus 100 requests at the start of the next window.
- A prototype branch already implements token bucket and passed the same load test without boundary bursts.
- Support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review decision set the default to 600 requests per minute per client effective with this release.
- `test_burst_allowance` fails intermittently, roughly one run in five, cause unknown. Everything else in the suite is green.
- No latency measurement for the token bucket implementation is given in the material.

Assumptions, labeled as assumptions:

- Assumption: a shared Redis key per client provides consistent counting across all 6 instances and counters that survive deploys. Confidence: high, based on the merged fix and its regression test recorded in the material.
- Assumption: the token bucket prototype will show the same lack of boundary bursts after it is merged as it did in the load test on the prototype branch. Confidence: moderate, based on the load test result for the prototype branch only. It is not yet merged and no latency measurement for it is given.
- Assumption: the new default of 600 requests per minute per client will stop the legitimate batch client reported by support from being throttled. Confidence: moderate, based on the support report and product decision recorded in the material. No measurement confirming the new limit for that client is given.

## 4. Constraints

Standing constraints on the implementation:

- No new external dependencies beyond what the service already uses.
- Rate limiting overhead must stay within 5 ms at p99. The material states this as the standing latency budget and, restated in the constraints, rate limiting may add at most 5 ms at p99.
- Counters must survive deploys. A deploy must not reset a client's usage.
- Counting must be consistent across instances. A limit counted separately on each of the 6 instances would not be a single limit for a client.

## 5. What changed and why

Change 1: Counter storage.
- From: counters kept in process memory.
- To: Redis with a shared key per client.
- Why: process memory counters reset on every deploy and differed per instance, conflicting with consistency across instances and survival across deploys.
- Authoritative now: Redis with a shared key per client.
- Evidence: an early bug found in how counters were stored, recorded in the Part 1 work log extracts. The fix is merged and covered by a regression test.

Change 2: Algorithm.
- From: fixed window counter, chosen at the start of the session for simplicity.
- To: token bucket.
- Why: a load test showed a boundary burst problem with fixed window, where clients can send 2x the limit around window edges.
- Authoritative now: token bucket.
- Evidence: the Part 2 load test report on the fixed window implementation, which recommends token bucket and notes that a prototype branch already implements token bucket and passed the same load test without boundary bursts. The material does not say that branch is merged.

Change 3: Default limit.
- From: 100 requests per minute per client, taken from the original API spec.
- To: 600 requests per minute per client, effective with this release.
- Why: support reported that a legitimate batch client was being throttled at 100 requests per minute.
- Authoritative now: 600 requests per minute per client.
- Evidence: the Part 2 product review meeting notes, reporting the support report and recording the product decision. The material does not state that this change is merged.

## 6. Open questions and missing information

- The root cause of the intermittent failure of `test_burst_allowance`, roughly one run in five, is not yet identified. The cause is unknown. It is flagged here and not guessed.
- No latency measurement for the token bucket implementation is given, so compliance with the 5 ms at p99 budget is not established for that algorithm.
- The name of the regression test covering the Redis storage fix is not given in the material.
- The material does not state that the token bucket prototype branch is merged, and does not state that the change to the 600 requests per minute default is merged. Both are recorded as decided and planned, not merged.
- Token bucket configuration details beyond the algorithm choice, such as bucket capacity and refill parameters, are not given in the material.
- Whether the 600 requests per minute limit resolves the throttling of the legitimate batch client is not confirmed by any measurement in the material.

## 7. Next actions

In order, without redoing work already merged and without reverting earlier fixes:

1. Review the token bucket prototype branch against the merged Redis storage and feature flag setup, and merge it as the implementation of the authoritative algorithm.
2. Apply the decided default limit change to 600 requests per minute per client for this release.
3. Investigate the intermittent `test_burst_allowance` failure by reproducing it across repeated runs and gathering evidence from failing runs, without assuming a cause in advance.
4. Measure latency for the token bucket implementation and check it against the 5 ms at p99 budget, since no such measurement is in the handoff material.
5. Run the full test suite, including the existing regression test for Redis storage, repeatedly enough to assess the intermittent failure and confirm everything else remains green.
6. Verify before release that counting remains consistent across instances and that counters survive deploys, as required by the standing constraints.

## 8. Implementation plan

Remaining work is to merge the token bucket prototype, apply the default limit of 600 requests per minute per client, and resolve the outstanding test problem. I would first review the prototype branch against the merged middleware skeleton, the feature flag, and the merged Redis storage with a shared key per client, and merge it without changing that storage fix. I would then apply the limit change for this release.

For `test_burst_allowance`, I would run the suite repeatedly to reproduce the roughly one in five failure, capture output and state from failing and passing runs, and compare them to identify the cause from evidence rather than assuming one.

Before release, I would verify that p99 latency for the token bucket path is within the 5 ms budget, that the full suite passes on repeated runs, that the Redis regression test still passes, that boundary burst behaviour matches the load test result, and that counters stay consistent across instances and survive deploys.
