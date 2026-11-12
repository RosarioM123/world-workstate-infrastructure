# Engineering Status Report: S1 API Rate Limiting

Status at the end of the session, after the Part 2 update. This report distinguishes merged work from decided but not yet merged work.

## Summary

Rate limiting for the gateway service is built on Redis backed counters with a shared key per client. That storage fix is merged. Two design decisions changed during this session on new evidence: the algorithm moves from fixed window to token bucket, and the default limit moves from 100 to 600 requests per minute per client. Neither change is recorded as merged in the source materials. One test fails intermittently and its cause is unknown.

## Service context

- The gateway fronts a multi-instance API with 6 instances behind a load balancer.
- Rate limiting must be consistent across those instances.
- Redis is operated in all environments and is already a dependency of the service.
- Latency budget: rate limiting may add at most 5 ms at p99.

## Current design

- Middleware: rate limit middleware skeleton, merged behind a feature flag.
- Counter storage: Redis, with a shared key per client. This gives one counter view per client across instances and avoids counters resetting on deploy.
- Algorithm: token bucket. This is the current accepted decision, superseding the fixed window counter. Implementation exists on a prototype branch.
- Default limit: 600 requests per minute per client. This is the current accepted decision, superseding 100 requests per minute per client, and is effective with this release.

## What is merged

1. Rate limit middleware skeleton, behind a feature flag.
   Source: Part 1 work log extracts.

2. Fix for the early counter storage bug.
   The bug: counters kept in process memory reset on every deploy and differed per instance.
   The fix: counters moved to Redis with a shared key per client.
   Coverage: the fix is covered by a regression test. The regression test name is not given in the materials.
   Source: Part 1 work log extracts.

Nothing else in this report should be read as merged.

## What changed in this session, and why

### Algorithm: fixed window to token bucket

A load test of the fixed window implementation showed a boundary burst problem: clients can send 2x the limit around window edges, specifically 100 requests at the end of one window plus 100 requests at the start of the next. The load test report recommends token bucket, and notes that the prototype branch already implements token bucket and passed the same load test without boundary bursts.

Source: Part 2 load test report.

### Default limit: 100 to 600 requests per minute per client

Support reported that a legitimate batch client is being throttled at 100 requests per minute. The product review meeting decided that the default limit becomes 600 requests per minute per client, effective with this release.

Source: Part 2 product review meeting notes.

## What is failing

- Test `test_burst_allowance` fails intermittently, roughly one run in five.
- Root cause: unknown. It has not yet been identified, and this report does not speculate on it.
- Everything else in the test suite is green.

Source: Part 2 remaining test status note.

## What remains

- Merge the token bucket implementation from the prototype branch. Status in the materials: prototype branch only.
- Apply the default limit change to 600 requests per minute per client for this release. Status in the materials: product decision made, effective with this release, merge not stated.
- Identify the root cause of the intermittent `test_burst_allowance` failure and fix it, or establish with evidence that it is unrelated to the changes above. No cause is available yet.
- Confirm the token bucket implementation against the 5 ms p99 latency budget. No latency measurement for token bucket is given in the materials, so this is unverified, not passed and not failed.

## Constraints still in force

- No new external dependencies beyond what the service already uses. Redis is already a dependency, so the current storage design stays within this constraint.
- Rate limiting overhead must stay within 5 ms at p99.
- Counters must survive deploys and must not reset a client's usage on deploy.

## Risks and open questions

- The intermittent test failure is the main release risk in the current record, because its cause is unknown and its failure rate is roughly one run in five.
- The boundary burst behaviour is a property of the fixed window design, so shipping fixed window would keep a known 2x burst at window edges, per the load test report.
- The 600 limit is a product decision based on a support report about one legitimate batch client. The materials give no broader client usage data, so the wider effect of the higher default is not assessed here.
