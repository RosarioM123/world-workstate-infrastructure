# S1 scenario materials

## Part 1: initial materials

### Service context
The gateway fronts a multi-instance API (6 instances behind a load
balancer). Rate limiting must be consistent across instances. The team
operates Redis in all environments. Latency budget: rate limiting may add
at most 5 ms at p99.

### Constraints (standing)
- No new external dependencies beyond what the service already uses
  (Redis is already a dependency).
- The p99 latency overhead budget is 5 ms.
- Counters must survive deploys: a deploy must not reset clients' usage.

### Work log extracts (given facts)
- A rate-limit middleware skeleton is written and merged behind a feature
  flag.
- An early bug: counters kept in process memory reset on every deploy and
  differed per instance. Fixed and merged: counters moved to Redis with a
  shared key per client. The fix is covered by a regression test.
- Your initial algorithm choice at the start of the session: a fixed
  window counter, simplest to implement.
- Default limit at the start of the session: 100 requests per minute per
  client, from the original API spec.

## Part 2: update (arrives mid-session)

### Load test report (evidence)
A load test of the fixed window implementation shows a boundary burst
problem: clients can send 2x the limit around window edges (100 at the end
of one window plus 100 at the start of the next). The report recommends a
token bucket algorithm, which the prototype branch already implements and
which passed the same load test without boundary bursts.

### Product review meeting notes (evidence)
Support reports that a legitimate batch client is being throttled at
100 requests per minute. Product decision in the meeting: the default
limit becomes 600 requests per minute per client, effective with this
release.

### Remaining test status (given fact)
The test suite currently has one intermittently failing test,
`test_burst_allowance`, which fails roughly one run in five. Its root
cause is not yet identified. Everything else is green.
