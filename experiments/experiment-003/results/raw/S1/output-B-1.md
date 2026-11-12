# Continuation Document: API Rate Limiting for Gateway Service

## 1. Where things stand

Current design:
- Algorithm: token bucket. This is the current accepted design, but it is not merged. The code exists on a prototype branch.
- Storage: Redis, with a shared key per client. This gives one counter view per client across instances.
- Default limit: 600 requests per minute per client. This was decided in a product review and is effective with this release, but the handoff material does not state that the change is merged.

Already merged:
- A rate limit middleware skeleton, behind a feature flag.
- A fix moving counters from in-process memory to Redis with a shared key per client. The fix is covered by a regression test, although the name of that regression test is not given in the handoff material.

Current test status:
- Everything in the suite is green except one test.
- test_burst_allowance fails intermittently, roughly one run in five. Its root cause has not been identified.

Context: the gateway fronts a multi-instance API with six instances behind a load balancer.

## 2. Decisions in force

Decisions that currently govern the implementation:
- Use token bucket as the algorithm. Reason: a load test of the fixed window implementation showed a boundary burst problem, and a prototype token bucket implementation passed the same load test without boundary bursts.
- Use Redis for counters, with a shared key per client. Reason: a limit counted separately on each instance would not amount to a single limit for a client, and in-process counters reset on deploy and differed from instance to instance. Redis is already operated by the team in all environments and is already a dependency of the service.
- Set the default limit to 600 requests per minute per client, effective with this release. Reason: support reported that a legitimate batch client was being throttled at 100 requests per minute, and the product decision was made in a product review meeting.
- Keep the rate limit middleware behind a feature flag. Reason: the skeleton was merged behind a feature flag as a rollout guard, as recorded in the handoff material.

Decisions no longer in force:
- Fixed window counter as the algorithm. It was chosen because it was the simplest approach to implement. It was superseded by token bucket.
- 100 requests per minute per client as the default limit. It was taken from the original API spec. It was superseded by 600 requests per minute per client.
- Storing counters in process memory. This was the earlier buggy storage approach. It was superseded by Redis storage.

## 3. Assumptions and facts

Established facts:
- The service has six instances behind a load balancer.
- The team already operates Redis in all environments, and Redis is already a dependency of the service.
- A load test of the fixed window implementation showed that around a window edge a client could send twice the limit, by sending 100 requests at the end of one window and another 100 requests at the start of the next.
- The load test report recommended token bucket, and noted that a prototype branch already implements token bucket and passed the same load test without boundary bursts.
- Support reported that a legitimate batch client was being throttled at 100 requests per minute.
- The middleware skeleton and the Redis storage fix are merged, as stated in Section 1.
- test_burst_allowance fails intermittently, roughly one run in five, and everything else in the suite is green.

Assumptions:
- Assumption, low confidence: raising the default to 600 requests per minute per client is appropriate more broadly. The handoff material says this rests on a support report about one legitimate batch client, that no broader client usage data is given, and that the wider effect of raising the default is not assessed in the record.
- Assumption, unverified: the token bucket implementation complies with the latency budget. No latency measurement for the token bucket implementation is given, so compliance is neither passed nor failed in the handoff material. No confidence can be assigned from the material.

## 4. Constraints

- No new external dependencies should be added beyond what the service already uses.
- Rate limiting may add at most 5 ms at p99.
- Counters must survive deploys. A deploy must not reset a client usage count.
- The implementation must give a consistent view of a client usage across all six instances, so a limit counted separately on each instance is not acceptable.

## 5. What changed and why

Change 1, storage:
- From: counters kept in process memory.
- To: counters in Redis with a shared key per client.
- Why: in-process counters reset on every deploy and differed from instance to instance, which conflicted with the consistency and deploy survival requirements.
- Evidence: the bug described in the handoff material, in how counters were stored.
- Authoritative now: Redis with a shared key per client.
- Status: the fix is merged and covered by a regression test.

Change 2, algorithm:
- From: fixed window counter, chosen because it was the simplest approach to implement.
- To: token bucket.
- Why: the fixed window version allowed a boundary burst of twice the limit around a window edge.
- Evidence: a load test of the fixed window implementation, and the load test report recommendation. The report noted that the prototype token bucket branch passed the same load test without boundary bursts.
- Authoritative now: token bucket.
- Status: decided and accepted as the current design, but not treated as merged. The code exists on the prototype branch.

Change 3, default limit:
- From: 100 requests per minute per client, taken from the original API spec.
- To: 600 requests per minute per client.
- Why: a legitimate batch client was being throttled at the lower limit.
- Evidence: a support report about that client, followed by a decision in a product review meeting.
- Authoritative now: 600 requests per minute per client, effective with this release.
- Status: decided and planned for this release, but the handoff material does not state that the change is merged.

## 6. Open questions and missing information

- The root cause of the intermittent test_burst_allowance failure is unknown. It fails roughly one run in five. No cause is stated in the handoff material, and no cause is guessed here.
- Whether test_burst_allowance is related to the changes described above is unknown. The handoff material says the next person needs either to identify the root cause and fix it, or to establish with evidence that it is unrelated to those changes.
- No latency measurement for the token bucket implementation is given. Compliance with the 5 ms at p99 budget is unverified for that algorithm.
- The name of the regression test covering the Redis storage fix is not given.
- Whether the token bucket implementation from the prototype branch has been merged is not stated. The material treats merging it as outstanding work.
- Whether the default limit change to 600 requests per minute per client has been merged is not stated.
- No broader client usage data is given, so the wider effect of raising the default limit is not assessed.

## 7. Next actions

In order:
1. Merge the token bucket implementation from the prototype branch.
2. Apply the default limit change to 600 requests per minute per client for this release.
3. Investigate the intermittent test_burst_allowance failure to identify its root cause and fix it, or establish with evidence that it is unrelated to the changes above.
4. Confirm that the token bucket implementation stays within the latency budget of at most 5 ms at p99.

These steps do not redo the merged middleware skeleton or the merged Redis storage fix, and they do not revert earlier fixes.

## 8. Implementation plan

Remaining work is to land the decided design and resolve the release risk. First, merge the token bucket code from the prototype branch and apply the default of 600 requests per minute per client, keeping the merged Redis storage with a shared key per client and the feature flag in place.

For the outstanding test problem, run test_burst_allowance repeatedly to reproduce the intermittent failure, preserve the failing output, and investigate from that evidence until the root cause is identified and fixed, or until evidence shows it is unrelated to these changes. Do not assume a cause in advance.

Before release, verify that the full suite is green across repeated runs, that the token bucket version passes the load test scenario that exposed the fixed window boundary burst without allowing twice the limit at a window edge, that counters give one view per client across instances and survive a deploy, and that measured latency stays within 5 ms at p99. Also verify that the merged default is 600 and that no new external dependency was added.
