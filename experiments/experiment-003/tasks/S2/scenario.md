# S2 scenario materials

## Part 1: initial materials

### Incident report
The checkout service returns intermittent HTTP 500 errors, roughly 2% of
requests, clustered at busy times. The errors began appearing "recently"
according to the support team. A deploy of the separate pricing service
happened four days ago, and several people suspect it.

### Standing constraints
- Change freeze: during the incident, code changes are allowed only in
  the checkout service repository.
- No rollback of any service without evidence that the rollback target
  caused the problem.

### Initial state
Your first working hypothesis, based on timing gossip: the pricing
service deploy four days ago introduced the errors.

## Part 2: update (log analysis results, mid-session)

### Log analysis (evidence)
Timestamp analysis of the checkout error logs shows the 500 errors began
seven days ago, three days before the pricing service deploy. The deploy
is exonerated by the timeline. Error rate correlates with report
generation traffic, not with pricing calls.

### Code inspection (evidence)
The report-generation path in the checkout service opens database
connections without reliably closing them on error paths. Under load the
connection pool (50 connections) is exhausted, and subsequent checkout
requests fail with 500s. A fix was written and merged: connections are now
released via a context manager on all paths, with a regression test.

### Remaining symptom (given fact)
 Separately, a rare timeout in the payment webhook handler (about 1 in
 2,000 calls) is still occurring and is unexplained. It does not correlate
with the pool exhaustion pattern.
