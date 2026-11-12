# Work Journal: S1 API Rate Limiting (Gateway Service)

Actor: Agent A, Experiment 003, Task S1
Basis: scenario materials in Part 1, then the Part 2 update. No measurements beyond those materials are claimed here.

## 1. Session start: service context examined

I began with Part 1. The gateway fronts a multi-instance API with 6 instances behind a load balancer, so rate limiting has to be consistent across instances. A limit counted separately on each instance would not be a single limit for a client.

The team operates Redis in all environments, and Redis is already a dependency of the service. The standing latency budget is strict: rate limiting may add at most 5 ms at p99.

Standing constraints recorded at the start:

- No new external dependencies beyond what the service already uses.
- Rate limiting overhead must stay within 5 ms at p99.
- Counters must survive deploys. A deploy must not reset a client's usage.

## 2. Work already done before this design review

From the Part 1 work log extracts:

- A rate limit middleware skeleton is written and merged behind a feature flag.
- An early bug was found in how counters were stored. Counters kept in process memory reset on every deploy and differed per instance. That behaviour conflicts directly with two requirements above: consistency across instances and survival across deploys.
- The bug was fixed and merged. Counters moved to Redis with a shared key per client. The fix is covered by a regression test. The test name for that regression test is not given in the materials.

This part of the work is merged. It is not a proposal in this journal.

## 3. Initial design at the start of the session

My initial algorithm choice, as given at the start of the session, was a fixed window counter. The reason recorded for it was simplicity: it was the simplest approach to implement.

The default limit at the start of the session was 100 requests per minute per client, taken from the original API spec.

At this point the design was therefore:

- Storage: Redis, shared key per client, merged.
- Algorithm: fixed window counter.
- Default limit: 100 requests per minute per client.
- Rollout guard: middleware behind a feature flag.

## 4. Part 2 update arrives and changes the design

Part 2 arrived partway through the session and changed two decisions. I worked it in the order given.

### 4.1 Load test report: fixed window has a boundary burst problem

A load test of the fixed window implementation showed a boundary burst problem. Clients can send 2x the limit around window edges: 100 requests at the end of one window plus 100 requests at the start of the next window.

Provenance: Part 2 load test report on the fixed window implementation.

The report recommends a token bucket algorithm. The same report notes that a prototype branch already implements token bucket and passed the same load test without boundary bursts.

Effect on the design: the fixed window choice no longer stands. Token bucket supersedes it. The reason is evidence from the load test, not preference. The token bucket code exists on a prototype branch. The materials do not say that branch is merged, so I record it as planned for merge, not merged.

### 4.2 Product review meeting notes: default limit changes

Support reported that a legitimate batch client is being throttled at 100 requests per minute. In the product review meeting, the product decision was that the default limit becomes 600 requests per minute per client, effective with this release.

Provenance: Part 2 product review meeting notes, reporting a support report and a product decision.

Effect on the design: the 100 requests per minute default no longer stands. The 600 requests per minute default supersedes it. As with token bucket, the materials state the decision and its effective release, but do not state that the change is merged, so I record it as decided and planned for this release, not merged.

## 5. Test status at the end of the session

The remaining test status given in Part 2 is:

- One test, `test_burst_allowance`, fails intermittently, roughly one run in five.
- Its root cause is not yet identified. I record the cause as unknown and do not guess at it in this journal.
- Everything else in the suite is green.

Provenance: Part 2 remaining test status note.

## 6. End of session position

Merged:

- Rate limit middleware skeleton, behind a feature flag.
- Redis counter storage with a shared key per client, with a regression test covering the fix for the in process memory bug.

Decided but not recorded as merged:

- Token bucket algorithm, replacing fixed window, based on the load test report and the prototype branch result in that same report.
- Default limit of 600 requests per minute per client, replacing 100, effective with this release, based on the product review decision.

Open:

- The intermittent failure of `test_burst_allowance`, roughly one run in five, cause unknown.
- No latency measurement for the token bucket implementation is given in the materials, so compliance with the 5 ms p99 budget is not established here for that algorithm.
