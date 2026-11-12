# External validation protocol (independent reproduction challenge)

Status: **PENDING.** No external reviewer has completed this
protocol. Nothing in the repository may claim external validation
until a completed record exists in the results section at the end
of this file. This protocol was written in Prompt 6 (2026-11-05);
it has not been run by anyone outside the project.

## Purpose

Test whether a researcher or developer who has never seen WORLD
can, from the public repository alone, install it, run its checks,
execute the handoff demonstration, inspect a revision history, and
reproduce at least one reported result, and can afterwards state
accurately what WORLD does not prove.

## Reviewer profile

- A developer or researcher comfortable with Python and the
  command line.
- No prior exposure to this repository, its author, or its
  internal working notes.
- They receive exactly two things: the repository URL and the task
  list below. They do not receive `REPRODUCE.md` in advance; part
  of the test is whether the repository's own documentation leads
  them to it. (The maintainer may point them at it only after
  recording that they failed to find a needed instruction, and
  that intervention is logged as a documentation gap.)

## Tasks

1. **Install.** Follow the README's install instructions in a
   clean environment (fresh virtualenv; ideally a machine or
   container without the maintainer's setup). Success: the
   `world` package imports and the quickstart example runs.
2. **Test suite.** Run the full test suite by the documented
   command. Success: the run completes; record the pass count and
   any failure verbatim.
3. **Model checker.** Run the model checker by the documented
   command. Success: it reports the three configuration totals
   (165,579; 935,111; 119,565 states) and that P1 to P6 hold, and
   the mutation test reports the injected bug found.
4. **Demonstration.** Run the two-process demo (`demo/agent_a.py`,
   then `demo/agent_b.py`). Then answer, from the output alone:
   (a) Which decision is authoritative at the end of Agent A's
   work, and which one is superseded? (b) Why did the superseded
   decision change, and on what evidence? (c) What confidence level
   does assumption A2 carry? Success: all three answers correct
   without maintainer help.
5. **Revision inspection.** Using the demo world (or any world
   they create), retrieve one decision's revision chain through
   the documented API or CLI and explain what each entry means.
   Success: a correct explanation covering original value, change,
   actor, reason, and current authoritative version.
6. **Benchmark reproduction.** Run the documented benchmark script
   (`experiments/prompt3/bench.py`). Success: it completes, and
   the `verify()` peak-memory delta on the 20,000-version chain is
   in the low single-digit MB (the F5 streaming property), not the
   tens of MB a materializing verifier would show. Rates are
   host-dependent and are not compared exactly.
7. **Analysis reproduction.** Follow the documented procedure for
   re-running the Experiment #003 analysis from preserved outputs
   in a scratch copy. Success: the regenerated `results.json` and
   `tables.md` are identical to the preserved files (empty diff).

## What to record (per reviewer)

- Reviewer background (role, years of experience, OS, Python
  version) with consent to record it.
- Setup time: from first opening the repository to the first
  successful task, in wall-clock minutes, excluding download waits
  they attribute to their own network.
- Every error encountered, verbatim, with the step it occurred in
  and how it was resolved (self, documentation, maintainer).
- Every documentation gap: any place they had to guess, search
  outside the repository, or ask the maintainer.
- Per-task outcome: success, success with help, or failure.
- Comprehension check: after the tasks, the reviewer states in
  their own words (a) what WORLD guarantees, (b) what it does not
  guarantee (expected content: the hash chain is tamper-evident,
  not immutable; actor is self-asserted; no external validation
  exists yet), and (c) the strongest experimental result and its
  status (expected: assumption-metadata preservation in
  Experiment #003, PRELIMINARY, single model family).
- Free-form feedback: what was confusing, what was convincing,
  what they would challenge first as a reviewer of the research.

## Success criteria for the protocol itself

The reproduction challenge is considered passed for a reviewer
when tasks 1 to 7 complete without maintainer intervention beyond
logging gaps, the three comprehension questions in task 4 are
answered correctly from output, and the reviewer's own-words
summary does not overclaim beyond the repository's stated
limitations. One completed record is a start, not a validation
program; the project should report the number of completed records
and their outcomes, including failures, rather than a pass badge.

## Results

| # | Reviewer | Date | Environment | Setup time | Tasks passed | Errors and doc gaps | Outcome |
|---|---|---|---|---|---|---|---|
| (none yet) |  |  |  |  |  |  |  |

No rows exist. The status of external validation is: not started.
