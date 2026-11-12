# Continuation Document: API Rate Limiting for Gateway Service

## 1. Where things stand

The service is a gateway fronting a multi-instance API, with six instances behind a load balancer. A limit counted separately on each instance would not amount to a single limit for a client, so the design must give a consistent view of a client's usage across all six instances.

Current design:
- Algorithm: token bucket. This is the current accepted design, but it is not merged. The code exists on a prototype branch.
- Storage: Redis, with a shared key per client. This gives one counter view per client across instances.
- Default limit: 600 requests per minute per client. This is decided and meant to be effective with this release, but the handoff material does not state that the change is merged.

Already merged:
- A rate limit middleware skeleton, behind a feature flag.
- A fix moving counters from in-process memory to Redis with a shared key per client. The fix is covered by a regression test. The name of that regression test is not given in the handoff material.

Current test status:
- All tests are green except one.
- test_burst_allowance fails intermittently, roughly one run in five. Its root cause has not been identified.

## 2. Decisions in force

Decisions currently governing the implementation:

- Use token bucket as the algorithm. Reason: a load test of the fixed window implementation showed a boundary burst problem, and the load test report recommended token bucket. A prototype branch implementing token bucket passed the same load test without boundary bursts.
- Use a default limit of 600 requests per minute per client, effective with this release. Reason: support reported that a legitimate batch client was being throttled at 100 requests per minute, and a product review meeting made the decision to raise the default to 600.
- Store counters in Redis with a shared key per client. Reason: this gives one counter view per client across all six instances and avoids counters resetting on deploy. Redis is already operated by the team in all environments and is already a dependency of the service.
- Keep the rate limit middleware behind a feature flag. Reason given in the material: the skeleton was merged behind a feature flag, so the rollout guard is in place.

Decisions no longer in force:

- Fixed window counter as the algorithm. It was the initial choice because it was the simplest approach to implement. It was superseded by token bucket.
- Default limit of 100 requests per minute per client. It was taken from the original API spec. It was superseded by the 600 requests per minute decision.
- Storing counters in process memory. This was the earlier buggy storage approach. It was superseded by Redis storage with a shared key per client, and that fix is merged.

## 3. Assumptions and facts

Established facts:

- The API runs as six instances behind a load balancer.
- Redis is already operated in all environments and is already a dependency of the service.
- The middleware skeleton is merged behind a feature flag.
- The Redis storage fix is merged and covered by a regression test.
- A load test of the fixed window implementation showed a client could send twice the limit around a window edge, by sending 100 requests at the end of one window and another 100 requests at the start of the next.
- A prototype branch implements token bucket and passed the same load test without boundary bursts.
- Support reported that a legitimate batch client was being throttled at 100 requests per minute.
- A product review meeting decided the default becomes 600 requests per minute per client, effective with this release.
- test_burst_allowance fails intermittently, roughly one run in five, and all other tests are green.
- No latency measurement for the token bucket implementation is given in the handoff material.

Assumptions, labeled as assumptions:

- Assumption: Raising the default to 600 requests per minute per client is appropriate more broadly. Confidence: low, based on the material given. The decision rests on a support report about one legitimate batch client, no broader client usage data is given, and the wider effect of raising the default is not assessed in the record.
- Assumption: The token bucket implementation will comply with the latency budget. Confidence: not established. Compliance is unverified, neither passed nor failed, because no latency measurement for token bucket is given.

## 4. Constraints

- Rate limiting may add at most 5 ms at p99.
- Counters must survive deploys. A deploy must not reset a client's usage.
- No new external dependencies should be added beyond what the service already uses.
- The implementation must give a consistent view of a client's usage across all six instances, so that the limit is a single limit for a client.
- Shipping the fixed window version would mean knowingly keeping the 2x burst at window edges found by the load test. Token bucket is the authoritative design instead.

## 5. What changed and why

Storage change:
- From: counters kept in process memory.
- To: counters in Redis with a shared key per client.
- Why: counters in process memory reset on every deploy and differed from instance to instance, which conflicted with the consistency and deploy survival requirements.
- Authoritative now: Redis with a shared key per client.
- Evidence and status: the bug was identified, the fix is merged, and the fix is covered by a regression test whose name is not given.

Algorithm change:
- From: fixed window counter, chosen because it was the simplest approach to implement.
- To: token bucket.
- Why: a load test of the fixed window implementation showed a boundary burst problem, where a client could send twice the limit around a window edge.
- Authoritative now: token bucket.
- Evidence: the load test report recommended token bucket, and a prototype branch implementing token bucket passed the same load test without boundary bursts. The material does not say that branch has been merged, so merging it is still outstanding.

Default limit change:
- From: 100 requests per minute per client, taken from the original API spec.
- To: 600 requests per minute per client, effective with this release.
- Why: support reported that a legitimate batch client was being throttled at 100 requests per minute, and a product review meeting decided to raise the default.
- Authoritative now: 600 requests per minute per client.
- Evidence: the support report and the product review decision. The material does not state that this change is merged.

## 6. Open questions and missing information

- The root cause of the intermittent test_burst_allowance failure is unknown. It fails roughly one run in five. No cause is stated, and no cause should be guessed from the material available. It is the main release risk in the current record because its cause is unknown.
- Whether the token bucket implementation complies with the 5 ms at p99 latency budget is unknown. No latency measurement for token bucket is given, so compliance is unverified, neither passed nor failed.
- Whether the token bucket prototype branch has been merged is not stated. Based on the material, merging it is still outstanding work.
- Whether the default limit change to 600 requests per minute per client has been merged is not stated. It is recorded as decided and planned for this release rather than landed.
- The name of the regression test covering the Redis storage fix is not given.
- The wider effect of raising the default limit to 600 is not assessed. No broader client usage data is given beyond the report about one legitimate batch client.

## 7. Next actions

In order:

1. Merge the token bucket implementation from the prototype branch. Do not ship the fixed window version.
2. Apply the default limit change to 600 requests per minute per client for this release.
3. Investigate the intermittent test_burst_allowance failure to identify its root cause and fix it, or establish with evidence that it is unrelated to the changes described above.
4. Confirm that the token bucket implementation stays within the 5 ms at p99 latency budget.

These steps do not redo the merged middleware skeleton or the merged Redis storage fix, and they do not revert earlier fixes.

## 8. Implementation plan

Remaining work is to land the decided design, resolve the test risk, and verify latency.

First, merge the token bucket implementation from the prototype branch, keeping the merged middleware skeleton, feature flag, and Redis storage with a shared key per client. Apply the default limit of 600 requests per minute per client as part of the same release work, and confirm the merged result uses token bucket and not fixed window.

Second, attack the outstanding test problem by reproducing the intermittent test_burst_allowance failure, which occurs roughly one run in five, and gathering evidence about when it fails. Do not assume a cause. Either identify and fix the root cause, or establish with evidence that the failure is unrelated to these changes.

Before release, verify that the full suite passes consistently, including test_burst_allowance and the regression test for the Redis fix, and measure the token bucket implementation against the 5 ms at p99 latency budget, since compliance is currently unverified.
