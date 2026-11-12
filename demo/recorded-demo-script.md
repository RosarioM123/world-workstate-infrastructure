# Recorded demo script: the two-process handoff

A narration script for recording a walkthrough of `demo/agent_a.py`
and `demo/agent_b.py`. Target length: about 3 minutes. Run the pair
once before recording so the terminal state is familiar; reset by
re-running Agent A.

## Before you press record

- Terminal in the repository root, font large enough to read seq
  numbers.
- Say at the top: "Everything in this recording is live output from
  two scripts in this repository. Nothing is precomputed."

## Script

**[0:00, show demo/README.md briefly, then the terminal]**
"When an AI agent's work outlives its session, what crosses to the
successor is usually a summary or a transcript. This is WORLD: the
work state itself is a durable, verifiable record. Two processes,
no shared memory. The first one works and leaves. The second one
has to pick the work up from a file."

**[0:25, run `.venv/bin/python demo/agent_a.py`]**
"Agent A is researching solid-state battery suppliers. It records
spend against a declared cap of five thousand dollars. Watch seq 2:
it tries to commit nine thousand, the invariant judges the
proposal, rejects it, and the rejection itself is written to the
record. The state does not move."

**[0:55, Agent A output, seq 3 and 4]**
"Now the handoff state: decisions, evidence, and assumptions with
confidence levels as fields, not prose. Then new evidence arrives,
and decision D1 is superseded by D3, with the reason and the
evidence link stored. Agent A checkpoints, signs the chain tip, and
exits. The process is gone. What survives is one SQLite file and
the signed tip."

**[1:35, run `.venv/bin/python demo/agent_b.py`]**
"Agent B is a new process. It knows only the world's name. First,
verification: the hash chain checks out, and the signed tip still
matches the chain, which is what detects a rollback or a rewrite
of the file."

**[2:00, Agent B reconstruction output]**
"Here is the reconstruction. D3 is authoritative; D1 is present but
marked superseded, so a successor will not act on it. The revision
chain shows the original decision, when its status changed, who
changed it, why, and on what evidence. The assumptions carry their
confidence levels, medium and low. In Experiment 003, summaries
kept the substance of assumptions and lost exactly those levels;
that is the narrow, measured contrast this design targets."

**[2:35, Agent B continuation and verdict log]**
"Agent B continues the work, one new decision, and the chain still
verifies. The verdict log is the whole story of the task, including
the blocked attempt at seq 2. Rejected work is evidence here, not
silence."

**[2:55, close]**
"What this demo does not show: it is one machine, one file, two
scripts. The experiments behind the design are preliminary, single
model family, and the limitations file in this repository is
deliberately blunt about what is not yet proven. The record is the
point: decisions, revisions, and rejections you can inspect and
verify after the fact."

## Recording notes

- If a run differs from the README's expected output in sequence
  numbers or verdicts, stop and investigate; do not edit the
  recording to match. The outputs are deterministic in everything
  but timestamps and file paths.
- Do not describe the demo as evidence that WORLD improves agent
  reliability. It demonstrates the mechanism; the evidence section
  of the README states what the experiments did and did not show.
