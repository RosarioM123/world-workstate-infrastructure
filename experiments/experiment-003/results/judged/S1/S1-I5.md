# Continuation Document: S1 API Rate Limiting (Gateway Service)

## 1. Where things stand

The gateway fronts a multi-instance API with 6 instances behind a load balancer, so rate limiting has to be consistent across instances. A limit counted separately on each instance would not be a single limit for a client.

Current design:

- Algorithm: token bucket. This supersedes the earlier fixed window counter. See Section 5.
- Storage: Redis, with a shared key per client. Redis is operated in all environments and is already a dependency of the service.
- Default limit: 600 requests per minute per client. This supersedes the earlier default of 100 requests per minute per client, and is effective with this release. See Section 5.

Already merged:

- A rate limit middleware skeleton, behind a feature flag.
- Redis counter storage with a shared key per client. This was a fix for an earlier bug in which counters kept in process memory reset on every deploy and differed per instance. The fix is covered by a regression test. The name of that regression test is not given in the handoff material.

Decided but not recorded as merged:

- The token bucket algorithm. The code exists on a prototype branch. The handoff material does not say that branch is merged, so it is recorded as planned for merge, not merged.
- The default limit of 600 requests per minute per client. The handoff material states the decision and its effective release, but does not state that the change is merged, so it is recorded as decided and planned for this release, not merged.

Current test status:

- One test, `test_burst_allowance`, fails intermittently, roughly one run in five. Its root cause is not yet identified.
- Everything else in the suite is green.

## 2. Decisions in force

Decisions that currently govern the implementation:

- Use token bucket as the rate limiting algorithm. Reason: a load test of the fixed window implementation showed a boundary burst problem, and a prototype branch implementing token bucket passed the same load test without boundary bursts.
- Use Redis for counter storage, with a shared key per client. Reason: counters kept in process memory reset on every deploy and differed per instance, which conflicts with consistency across instances and survival across deploys.
- Set the default limit to 600 requests per minute per client, effective with this release. Reason: support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting made this product decision.
- Keep the rate limit middleware behind a feature flag. This was the rollout guard recorded for the merged middleware skeleton. No later change to it is recorded in the handoff material.

Decisions that are no longer in force:

- Fixed window counter as the algorithm. It was the initial choice, for simplicity. It was superseded by token bucket.
- Default limit of 100 requests per minute per client, taken from the original API spec. It was superseded by 600 requests per minute per client.
- Counter storage in process memory. This was the earlier buggy behaviour and was fixed and merged by moving counters to Redis. It is not recorded as an adopted design decision, and it is listed here only to make clear it does not govern the implementation.

## 3. Assumptions and facts

Established facts:

- The service has 6 instances behind a load balancer.
- Redis is operated in all environments and is already a dependency of the service.
- The middleware skeleton is merged behind a feature flag.
- The Redis storage fix is merged and covered by a regression test.
- A load test of the fixed window implementation showed clients can send 2x the limit around window edges: 100 requests at the end of one window plus 100 requests at the start of the next window.
- The same load test report states that a prototype branch implements token bucket and passed the same load test without boundary bursts.
- Support reported that a legitimate batch client is being throttled at 100 requests per minute.
- `test_burst_allowance` fails intermittently, roughly one run in five, and everything else in the suite is green.

Assumptions, labeled as assumptions:

- Assumption: the prototype token bucket branch can be merged into the merged middleware and Redis storage without further design changes. Confidence: low, because the handoff material does not describe its integration status, only that it exists and passed the load test.
- Assumption: the token bucket implementation will comply with the 5 ms at p99 latency budget. Confidence: low, because no latency measurement for the token bucket implementation is given in the handoff material, so compliance is not established.
- Assumption: a default of 600 requests per minute per client resolves the throttling reported for the legitimate batch client. Confidence: medium, because this rests on the product review decision and the support report, and no measurement confirming the outcome is given in the handoff material.

No other assumptions are explicitly recorded in the handoff material.

## 4. Constraints

Standing constraints on the implementation:

- No new external dependencies beyond what the service already uses.
- Rate limiting overhead must stay within 5 ms at p99.
- Counters must survive deploys. A deploy must not reset a client's usage.
- Rate limiting has to be consistent across the 6 instances behind the load balancer.

## 5. What changed and why

Change 1: counter storage.

- From: counters kept in process memory.
- To: counters in Redis with a shared key per client.
- Why: counters in process memory reset on every deploy and differed per instance, conflicting with consistency across instances and survival across deploys.
- Authoritative version now: Redis with a shared key per client.
- Evidence and status: the bug was found in the prior work, the fix was merged, and it is covered by a regression test.

Change 2: algorithm.

- From: fixed window counter, chosen initially because it was the simplest approach to implement.
- To: token bucket.
- Why: a load test of the fixed window implementation showed a boundary burst problem, with clients able to send 2x the limit around window edges, specifically 100 requests at the end of one window plus 100 requests at the start of the next window.
- Authoritative version now: token bucket.
- Evidence: the load test report on the fixed window implementation. The same report notes that a prototype branch already implements token bucket and passed the same load test without boundary bursts. This change is decided but not recorded as merged.

Change 3: default limit.

- From: 100 requests per minute per client, taken from the original API spec.
- To: 600 requests per minute per client, effective with this release.
- Why: support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting decided the new default.
- Authoritative version now: 600 requests per minute per client.
- Evidence: the product review meeting notes, reporting the support report and the product decision. This change is decided but not recorded as merged.

## 6. Open questions and missing information

- The root cause of the intermittent failure of `test_burst_allowance` is unknown. It fails roughly one run in five. No cause is stated in the handoff material, and none is guessed here.
- No latency measurement for the token bucket implementation is given, so whether it complies with the 5 ms at p99 budget is unknown.
- Whether the prototype token bucket branch is merged is not stated. The handoff material records it only as a prototype branch, planned for merge.
- Whether the change to the 600 requests per minute default is merged is not stated. The handoff material records the decision and that it is effective with this release, but not that it is merged.
- The name of the regression test covering the Redis storage fix is not given in the handoff material.
- No information is given in the handoff material about the integration status of the prototype token bucket branch with the merged middleware skeleton and Redis storage.

## 7. Next actions

In order:

1. Merge the token bucket implementation from the prototype branch into the merged middleware and Redis storage. Do not redo the merged middleware skeleton or the merged Redis storage fix.
2. Apply the decided default limit change to 600 requests per minute per client for this release.
3. Investigate the intermittent failure of `test_burst_allowance` by reproducing it over repeated runs and collecting the available evidence, without assuming a cause in advance.
4. Measure the latency of the token bucket implementation and check it against the 5 ms at p99 budget, since no such measurement is given in the handoff material.
5. Re-run the load test scenario that exposed the boundary burst problem and confirm the merged token bucket implementation passes it without boundary bursts.
6. Run the full test suite repeatedly, given the intermittent failure rate of roughly one run in five, and confirm the status of `test_burst_allowance` and that everything else remains green, before release.

## 8. Implementation plan

Remaining work is to merge the token bucket implementation from the prototype branch, apply the default limit of 600 requests per minute per client, and resolve or fully characterize the outstanding test problem. The merged middleware skeleton and Redis storage fix are not to be redone, and earlier fixes are not to be reverted.

For `test_burst_allowance`, I would run the suite, and that test in particular, repeatedly to reproduce the roughly one in five failure, preserve the failing output and run conditions for each failure, and compare failing and passing runs before forming any hypothesis about the cause, since the handoff material records the cause as unknown.

Before release I would verify: the boundary burst load test passes on the merged implementation without the 2x burst seen with fixed window; measured rate limiting latency stays within 5 ms at p99; counters remain shared across instances and survive deploys, as covered by the existing regression test; the default limit in effect is 600 requests per minute per client; and repeated full suite runs show the status of `test_burst_allowance` resolved or explicitly accounted for, with everything else green.
