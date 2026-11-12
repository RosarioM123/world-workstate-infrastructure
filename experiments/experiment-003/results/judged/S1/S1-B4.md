# Continuation Document: S1 API Rate Limiting

## 1. Where things stand

The governing design is: counters stored in Redis with a shared key per client, a token bucket algorithm, and a default limit of 600 requests per minute per client.

Storage is the merged part of that design. The rate limit middleware skeleton is written and merged behind a feature flag. Counters were moved from process memory to Redis with a shared key per client, that fix is merged, and it is covered by a regression test.

The algorithm and the default limit are decided but not recorded as merged. Token bucket was accepted in place of the fixed window counter, but its implementation exists on a prototype branch only. The default limit of 600 requests per minute per client was accepted and is effective with this release, but the handoff material does not state that the change is merged.

Current test status, as reported in the handoff material: the suite has one intermittently failing test, `test_burst_allowance`, which fails roughly one run in five. Its root cause is not yet identified. Everything else is reported as green. No run identifier or full test output is given.

## 2. Decisions in force

Decisions currently governing the implementation:

- D2: Store rate limit counters in Redis with a shared key per client. Reason: counters in process memory reset on every deploy and differed per instance. Redis gives a single shared counter per client across the 6 instances and persists usage across deploys. Redis is already a dependency and is operated in all environments, so this adds no new external dependency.
- D5: Use a token bucket algorithm instead of a fixed window counter. Reason: a load test of the fixed window implementation showed clients can send 2x the limit around window edges, and the load test report recommends token bucket. The prototype branch implementation passed the same load test without boundary bursts.
- D6: Set the default limit to 600 requests per minute per client, effective with this release. Reason: support reported that a legitimate batch client is being throttled at 100 requests per minute, and the product review meeting decided on 600 requests per minute per client in response.

Decisions no longer in force:

- D1: Keep rate limit counters in process memory. Superseded by D2.
- D3: Use a fixed window counter algorithm, chosen initially as the simplest to implement. Superseded by D5.
- D4: Set the default limit to 100 requests per minute per client, taken from the original API spec. Superseded by D6.

## 3. Assumptions and facts

Established facts, distinct from assumptions:

- The service runs 6 instances behind a load balancer, and Redis is operated in all environments and is already a service dependency.
- The middleware skeleton is merged behind a feature flag.
- The Redis counter fix is merged and covered by a regression test. No pass count, test output, or measurement from that test is given, and its test name and run identifier are not given.
- A load test of the fixed window implementation showed a boundary burst: 100 requests at the end of one window plus 100 at the start of the next, for 2x the limit around window edges. A prototype branch implementing token bucket passed the same load test without boundary bursts. No latency figures are given in that load test summary.
- Support reported a legitimate batch client throttled at 100 requests per minute, and a product decision set the default to 600 for this release.
- `test_burst_allowance` fails intermittently, roughly one run in five, with cause unknown, and everything else is reported green.

Assumptions, labeled with confidence:

- A1, confidence high, active: Redis is available in every environment this service runs in, so Redis backed counters can be used everywhere the gateway runs.
- A2, confidence high, validated: A shared Redis key per client gives one consistent count across instances and across deploys. Validated in the record only to the extent that the fix is merged and covered by a regression test.
- A3, confidence low, active and unverified: The token bucket implementation meets the 5 ms p99 latency budget. No latency measurement for token bucket is given in the material, so this must not be treated as a result.
- A4, confidence medium, active: A default of 600 requests per minute per client resolves the throttling of the legitimate batch client, without further changes for that client. No usage figures for that client beyond being throttled at 100 are given, and no data on other clients is given.
- A5, confidence medium, active: Everything in the test suite other than `test_burst_allowance` is currently passing. This is a reported status, not a test run reproduced in the material, with no run identifier or full output given.

## 4. Constraints

- C1: No new external dependencies beyond what the service already uses. Redis is already a dependency.
- C2: Rate limiting may add at most 5 ms at p99.
- C3: Counters must survive deploys. A deploy must not reset clients' usage.
- C4: Rate limiting must be consistent across instances. The service runs 6 instances behind a load balancer.

The definition of done in the material is a merged implementation that enforces one per client limit consistently across all instances, survives deploys, stays within the latency budget, and has a green test suite with no unexplained intermittent failures.

## 5. What changed and why

Storage change:

- From: D1, counters held in the memory of each gateway process.
- To: D2, counters stored in Redis with a shared key per client.
- Why: in process memory, counters reset on every deploy and differed per instance.
- Authoritative now: D2.
- Evidence: the work log extracts recording the early bug and the fix, and the regression test covering the Redis fix. The fix is merged.

Algorithm change:

- From: D3, fixed window counter, initially chosen as the simplest to implement.
- To: D5, token bucket algorithm.
- Why: the fixed window implementation allowed boundary bursts.
- Authoritative now: D5.
- Evidence: the load test report, which showed clients can send 2x the limit around window edges, recommended token bucket, and recorded that the prototype branch passed the same load test without boundary bursts. D5 is accepted but not merged; the implementation is on a prototype branch only.

Default limit change:

- From: D4, 100 requests per minute per client, from the original API spec.
- To: D6, 600 requests per minute per client, effective with this release.
- Why: a legitimate batch client was being throttled at the lower limit.
- Authoritative now: D6.
- Evidence: the product review meeting notes, recording the support report and the product decision. D6 is accepted, but the material does not state that it is merged.

## 6. Open questions and missing information

- Q1: What is the root cause of the intermittent `test_burst_allowance` failure? Unknown. The test fails roughly one run in five and blocks the task to find its root cause. No cause is given in the material, and no cause is guessed here.
- Q2: Does the token bucket implementation stay within the 5 ms p99 latency budget? Unknown. No latency measurement for token bucket is given. The load test evidence covers boundary bursts only.
- Q3: Have the token bucket branch and the 600 limit been merged and released? Unknown from the material. Both are recorded as not merged, and their real merge and release state must be verified in the repository rather than assumed.
- Q4: Is 600 requests per minute per client the right default for clients other than the reported batch client? Unassessed. No wider client usage data is given.
- Missing information: latency figures for token bucket, usage figures for the reported batch client beyond throttling at 100, data on other clients, the regression test name and run identifier, pass counts or output from that regression test, and a run identifier or full output for the current suite status.

## 7. Next actions

In order:

1. Verify in the repository the real merge state of the token bucket prototype branch and of the 600 requests per minute per client default, since the material records both as not merged.
2. Diagnose the intermittent `test_burst_allowance` failure to a root cause, without assuming a cause. Preserve the failure evidence needed to identify it.
3. Measure token bucket latency against the 5 ms p99 budget in C2. Do not claim the budget is met before that measurement exists.
4. Merge the token bucket implementation, once the steps above allow it, and apply the default limit of 600 requests per minute per client for this release.
5. Confirm the merged result against the standing constraints and the definition of done, including a green test suite with no unexplained intermittent failures.

These steps do not redo the merged middleware skeleton or the merged Redis counter fix, and they do not revert any earlier fix.

## 8. Implementation plan

Remaining work is to finish what is decided but not merged: the token bucket algorithm, currently on a prototype branch only, and the default limit of 600 requests per minute per client for this release. First verify the actual merge state of both in the repository.

For the outstanding test problem, run `test_burst_allowance` repeatedly to reproduce its roughly one in five failure, capture the failing output and conditions each time, and compare failing and passing runs to isolate what differs. Treat the cause as unknown until that evidence identifies it, then fix the identified cause and show repeated green runs.

Before release, verify: token bucket passes the load test without boundary bursts, measured latency is within the 5 ms p99 budget, counters in Redis with a shared key per client remain consistent across instances and survive deploys, the 600 limit is in effect, no new external dependency was added, and the full suite is green with no unexplained intermittent failures.
