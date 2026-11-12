# Continuation Document: S1 API Rate Limiting (Gateway Service)

## 1. Where things stand

Current design:

- Algorithm: token bucket. This is the authoritative algorithm, superseding fixed window. The token bucket code exists on a prototype branch and is planned for merge. The handoff material does not say that branch is merged.
- Storage: Redis, with a shared key per client.
- Default limit: 600 requests per minute per client. This is the authoritative default, superseding 100 requests per minute per client, and is effective with this release. The handoff material does not say this change is merged.

Context for the design: the gateway fronts a multi-instance API with 6 instances behind a load balancer, so rate limiting has to be consistent across instances. Redis is operated by the team in all environments and is already a dependency of the service.

What is already merged:

- A rate limit middleware skeleton, merged behind a feature flag.
- The fix for the counter storage bug: counters moved from process memory to Redis with a shared key per client. This fix is merged and is covered by a regression test. The name of that regression test is not given in the handoff material.

Current test status:

- One test, `test_burst_allowance`, fails intermittently, roughly one run in five. Its root cause is not yet identified.
- Everything else in the suite is green.

## 2. Decisions in force

Decisions that currently govern the implementation:

- Use token bucket as the rate limiting algorithm. Reason: a load test of the fixed window implementation showed a boundary burst problem, and a prototype token bucket implementation passed the same load test without boundary bursts.
- Use Redis storage with a shared key per client for counters. Reason: counters in process memory reset on every deploy and differed per instance, which conflicts with the requirements for consistency across instances and survival across deploys. Redis is already a dependency of the service and is operated in all environments.
- Set the default limit to 600 requests per minute per client, effective with this release. Reason: support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting decided to raise the default.
- Keep the rate limit middleware behind a feature flag. This is the state in which the middleware skeleton was merged.

Decisions that are no longer in force:

- Fixed window counter as the algorithm. It was initially chosen for simplicity. It is superseded by token bucket because of the load test evidence.
- Default limit of 100 requests per minute per client, taken from the original API spec. It is superseded by 600 requests per minute per client because of the product review decision.
- Storing counters in process memory. This was the early buggy behaviour and was replaced by the merged Redis fix.

## 3. Assumptions and facts

Established facts:

- The gateway has 6 instances behind a load balancer, so a limit counted separately on each instance would not be a single limit for a client.
- Redis is operated in all environments and is already a dependency of the service.
- The rate limit middleware skeleton is merged behind a feature flag.
- The Redis counter storage fix is merged, with a shared key per client, and is covered by a regression test.
- A load test of the fixed window implementation showed clients can send 2x the limit around window edges: 100 requests at the end of one window plus 100 requests at the start of the next window.
- The same load test report states that a prototype branch implements token bucket and passed the same load test without boundary bursts.
- Support reported a legitimate batch client being throttled at 100 requests per minute, and the product review meeting decided the default becomes 600 requests per minute per client effective with this release.
- `test_burst_allowance` fails intermittently, roughly one run in five, and everything else in the suite is green.

Assumptions:

- No statements are explicitly labeled as assumptions in the handoff material, and no confidence levels are given in the material. No assumption or confidence level is therefore recorded here, rather than inventing one.

## 4. Constraints

Every standing constraint recorded in the handoff material:

- No new external dependencies beyond what the service already uses.
- Rate limiting overhead must stay within 5 ms at p99. Rate limiting may add at most 5 ms at p99.
- Counters must survive deploys. A deploy must not reset a client's usage.
- Rate limiting has to be consistent across instances, as a consequence of the 6 instance deployment behind a load balancer recorded in the material.

## 5. What changed and why

Change 1: Counter storage

- From: counters kept in process memory.
- To: counters in Redis with a shared key per client.
- Why: counters in process memory reset on every deploy and differed per instance, conflicting with consistency across instances and survival across deploys.
- Authoritative now: Redis with a shared key per client.
- Evidence and status: the bug was found in the prior work, the fix was merged, and it is covered by a regression test.

Change 2: Algorithm

- From: fixed window counter, initially chosen for simplicity.
- To: token bucket.
- Why: the fixed window implementation allows a boundary burst of 2x the limit around window edges.
- Authoritative now: token bucket.
- Evidence and status: a Part 2 load test report on the fixed window implementation, which also reports that a prototype token bucket branch passed the same load test without boundary bursts. The material does not say the prototype branch is merged, so this change is recorded as decided and planned for merge, not merged.

Change 3: Default limit

- From: 100 requests per minute per client, from the original API spec.
- To: 600 requests per minute per client.
- Why: a legitimate batch client was being throttled at the lower limit.
- Authoritative now: 600 requests per minute per client, effective with this release.
- Evidence and status: a support report as reported in Part 2 product review meeting notes, and the product decision in that meeting. The material does not state that this change is merged, so it is recorded as decided and planned for this release, not merged.

## 6. Open questions and missing information

- The root cause of the intermittent failure of `test_burst_allowance`, roughly one run in five, is not yet identified. It is unknown. No cause is guessed here.
- No latency measurement for the token bucket implementation is given in the material, so compliance of that algorithm with the 5 ms at p99 budget is not established.
- The name of the regression test covering the Redis storage fix is not given in the material.
- The material does not state that the token bucket prototype branch is merged.
- The material does not state that the change to the 600 requests per minute per client default is merged.
- No other test problems are reported: everything else in the suite is green.

## 7. Next actions

In order:

1. Merge or integrate the token bucket prototype branch so the authoritative algorithm replaces fixed window in the main implementation. Do not redo the already merged middleware skeleton or Redis storage fix.
2. Apply the decided default limit of 600 requests per minute per client for this release.
3. Investigate the intermittent `test_burst_allowance` failure: reproduce it with repeated runs, collect evidence, and identify the root cause before changing code based on a guessed cause.
4. Measure the latency of the token bucket implementation and check it against the 5 ms at p99 budget, since no such measurement is in the material.
5. Run the full test suite repeatedly, including the existing regression test for Redis storage, to confirm everything is green across multiple runs given the intermittent failure rate.
6. Verify before release that counters remain consistent across instances and survive deploys, using the merged Redis design, and that the feature flag rollout is in place.

## 8. Implementation plan

Remaining work is to integrate the token bucket prototype branch as the authoritative algorithm, apply the 600 requests per minute per client default, and resolve the intermittent test failure. Neither the merged middleware skeleton nor the merged Redis storage fix should be redone.

For `test_burst_allowance`, I would run the suite and that test repeatedly to reproduce the roughly one in five failure, capture the failing output and conditions for each failure, and compare failing and passing runs. I would not propose a fix until that evidence identifies a root cause, since the cause is currently unknown.

Before release I would verify: the full suite passes consistently across multiple runs, the existing Redis regression test still passes, token bucket passes the boundary burst scenario described in the load test report, latency is measured and is within 5 ms at p99, and the default limit in the release configuration is 600 requests per minute per client.
