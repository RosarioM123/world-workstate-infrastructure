# Continuation Document

## 1. Where things stand

The work is adding rate limiting to a gateway service that fronts a multi-instance API, with six instances behind a load balancer. The limit therefore has to give a consistent view of a client's usage across all six instances, not a separate count on each instance.

Current design:
- Algorithm: token bucket. This is the current accepted design, but it is not merged. It exists on a prototype branch that passed the load test described in Section 5.
- Storage: Redis, with a shared key per client. Counters were moved from process memory to Redis, and that fix is merged.
- Default limit: 600 requests per minute per client. This was decided in a product review and is meant to be effective with this release, but the handoff material does not state that the change is merged.

Already merged:
- A rate limit middleware skeleton, behind a feature flag.
- The storage fix moving counters to Redis with a shared key per client, covered by a regression test. The name of that regression test is not given in the handoff material.

Current test status:
- Everything in the suite is green except one test.
- test_burst_allowance fails intermittently, roughly one run in five. Its root cause has not been identified.

## 2. Decisions in force

Decisions currently governing the implementation:
- Use a token bucket algorithm. Reason: a load test of the fixed window implementation showed a boundary burst problem, and a prototype branch implementing token bucket passed the same load test without boundary bursts.
- Use a default limit of 600 requests per minute per client, effective with this release. Reason: support reported that a legitimate batch client was being throttled at the previous default, and the change was made as a product decision in a product review meeting.
- Store counters in Redis with a shared key per client. Reason: this gives one counter view per client across instances and avoids counters resetting on deploy. Redis is already operated by the team in all environments and is already a dependency of the service.
- Keep the merged middleware behind a feature flag. Reason given in the material: the feature flag is the rollout guard, in place even though the final design is not yet fully landed.

Decisions no longer in force:
- Fixed window counter as the algorithm. Superseded by token bucket.
- A default limit of 100 requests per minute per client. Superseded by 600 requests per minute per client.
- Counters kept in process memory. Superseded by Redis storage, as described in Section 5.

## 3. Assumptions and facts

Established facts:
- The service has six instances behind a load balancer.
- The team already operates Redis in all environments, and Redis is already a dependency of the service.
- The middleware skeleton is merged behind a feature flag.
- The Redis storage fix is merged and covered by a regression test.
- A load test found that, around a fixed window edge, a client could send twice the limit: 100 requests at the end of one window and another 100 requests at the start of the next.
- A prototype branch implements token bucket and passed the same load test without boundary bursts.
- Support reported that a legitimate batch client was being throttled at 100 requests per minute.
- test_burst_allowance fails intermittently, roughly one run in five, and everything else in the suite is green.

Assumptions, labeled as assumptions:
- Assumption: Redis storage will provide the consistent per client counter view required across all six instances and across deploys. Confidence: high, based on the merged fix and its stated purpose, though the handoff material gives no separate measurement of this.
- Assumption: a default of 600 requests per minute per client is an appropriate general default. Confidence: low. It rests on a support report about one legitimate batch client, no broader client usage data is given, and the wider effect of raising the default is not assessed in the material.
- Assumption: the token bucket implementation will comply with the latency budget in Section 4. Confidence: not established. No latency measurement for the token bucket implementation is given, so this is unverified rather than supported.

## 4. Constraints

- No new external dependencies beyond what the service already uses.
- Rate limiting may add at most 5 ms at p99.
- Counters must survive deploys. A deploy must not reset a client's usage.
- The limit must give a consistent view of a client's usage across all six instances behind the load balancer.

## 5. What changed and why

Change 1, counter storage:
- From: counters kept in process memory.
- To: counters in Redis with a shared key per client.
- Why: counters in process memory reset on every deploy and differed from instance to instance, which conflicted with the deploy survival and consistency requirements.
- Authoritative now: Redis with a shared key per client.
- Evidence and status: the problem was identified as a bug, the fix is merged, and it is covered by a regression test whose name is not given.

Change 2, algorithm:
- From: fixed window counter, chosen because it was the simplest approach to implement.
- To: token bucket.
- Why: a load test of the fixed window implementation showed a boundary burst problem, where a client could send twice the limit around a window edge.
- Authoritative now: token bucket.
- Evidence and status: the load test report recommended token bucket, and a prototype branch implementing it passed the same load test without boundary bursts. The material does not say that branch has been merged, so merging it is still outstanding. Shipping the fixed window version would knowingly keep the 2x burst at window edges.

Change 3, default limit:
- From: 100 requests per minute per client, taken from the original API spec.
- To: 600 requests per minute per client, effective with this release.
- Why: support reported that a legitimate batch client was being throttled at 100 requests per minute, and the new default was decided in a product review meeting.
- Authoritative now: 600 requests per minute per client.
- Evidence and status: the decision is made and planned for this release, but the material does not state that the change is merged. The supporting evidence given is the report about one legitimate batch client. No broader client usage data is given.

## 6. Open questions and missing information

- The root cause of the intermittent test_burst_allowance failure is unknown. It fails roughly one run in five. No cause is stated in the material, and none should be guessed.
- No latency measurement for the token bucket implementation is given. Compliance with the 5 ms at p99 budget is therefore unverified, neither passed nor failed.
- The name of the regression test covering the Redis storage fix is not given.
- The material does not state that the token bucket prototype branch has been merged, so its merge status is outstanding work rather than landed work.
- The material does not state that the default limit change to 600 requests per minute per client is merged.
- No broader client usage data is given, so the wider effect of raising the default limit is not assessed.
- It is not yet established whether the intermittent test failure is related to the changes described here. That would need evidence.

## 7. Next actions

In order:
1. Merge the token bucket implementation from the prototype branch. Do not redo the already merged middleware skeleton or the already merged Redis storage fix.
2. Apply the default limit change to 600 requests per minute per client for this release.
3. Investigate the intermittent test_burst_allowance failure to identify its root cause and fix it, or establish with evidence that it is unrelated to the changes described here.
4. Measure the token bucket implementation against the latency budget and confirm whether it stays within 5 ms at p99.
5. Before release, confirm the test status and the latency result with evidence, since both are currently unresolved.

## 8. Implementation plan

Remaining work is to land the decided design, not to revisit merged work. First, merge the token bucket implementation from the prototype branch, keeping the merged Redis storage with a shared key per client and the feature flag in place. Second, apply the default limit of 600 requests per minute per client for this release.

For the outstanding test problem, reproduce the intermittent test_burst_allowance failure by running it repeatedly, preserve the failing output when it occurs, and compare failing and passing runs using only that evidence. Do not assume a cause in advance. Either fix an identified root cause or establish with evidence that the failure is unrelated to these changes.

Before release, verify that the full suite passes reliably across repeated runs, that the token bucket version shows no boundary bursts under the load test already used, and that measured latency stays within 5 ms at p99. If latency or repeated test results cannot be shown, report that as unverified rather than as passed.
