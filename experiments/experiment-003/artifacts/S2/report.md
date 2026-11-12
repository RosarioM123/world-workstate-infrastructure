# Incident Status Report: Checkout Service HTTP 500 Errors

Task: S2, Experiment 003
Status as of: End of Agent A session
Basis: Scenario materials in tasks/S2/scenario.md, Part 1 and Part 2 update only.

## Summary

The checkout service returned intermittent HTTP 500 errors at roughly 2% of requests, clustered at busy times. The main problem was caused by a database connection leak in the report generation path of the checkout service itself. A fix has been written and merged. A separate, rare payment webhook timeout remains unexplained.

## What caused the main problem

- The report generation path in the checkout service opens database connections without reliably closing them on error paths.
- Under load, leaked connections exhaust the connection pool, which has 50 connections.
- Once the pool is exhausted, subsequent checkout requests fail with HTTP 500 errors.

Provenance: code inspection evidence in the Part 2 update. The mechanism explains the clustering at busy times reported at intake.

Supporting evidence:
- Timestamp analysis of the checkout error logs shows the errors began seven days ago.
- The error rate correlates with report generation traffic, not with pricing calls.

Provenance: log analysis evidence in the Part 2 update.

## What was fixed and merged

- Fix merged in the checkout service repository, which is the only repository where code changes were allowed under the change freeze.
- Change: database connections are now released via a context manager on all paths, including error paths.
- A regression test was included with the fix.

No post merge error rate is stated in the source materials, so this report does not claim a measured post merge outcome.

## What was ruled out and why

### Pricing service deploy, ruled out

- Initial suspicion: a deploy of the separate pricing service four days ago was suspected by several people, and it was the first working hypothesis of this session, based on timing gossip.
- Why it was ruled out: timestamp analysis shows the 500 errors began seven days ago, three days before that deploy. The deploy is exonerated by the timeline.
- Additional support: the error rate does not correlate with pricing calls. It correlates with report generation traffic.
- Action consequence: no rollback of the pricing service was performed. That is also consistent with the standing constraint that no service is rolled back without evidence that the rollback target caused the problem, and here the evidence points away from it.

The original hypothesis is retained in the journal and in the state bundle as invalidated, with the timeline evidence as the reason, rather than being deleted.

## What remains unexplained

- A rare timeout in the payment webhook handler is still occurring.
- Frequency: about 1 in 2,000 calls.
- Cause: unknown.
- Relationship to the main problem: it does not correlate with the pool exhaustion pattern, so it is treated as a separate symptom and is not explained by the connection leak.
- No cause, fix, or owner for this timeout is given in the source materials.

## Constraints that governed the work

- Change freeze: during the incident, code changes were allowed only in the checkout service repository. The merged fix complies, because it was made in that repository.
- No rollback of any service without evidence that the rollback target caused the problem. No rollback was performed.

## Open next questions

- What causes the payment webhook handler timeout at about 1 in 2,000 calls?
- Does the timeout have its own traffic, timing, or dependency pattern, given that it does not follow the pool exhaustion pattern?

These questions are open and unanswered at the end of this session.
