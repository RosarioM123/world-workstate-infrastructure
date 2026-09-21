# Commit-email privacy rewrite (2026-09-21)

At the repo owner's request, the author/committer email on every commit was
replaced with the GitHub noreply address
(`208308619+RosarioM123@users.noreply.github.com`). Trees, messages, and dates
are unchanged; only identity metadata was rewritten. All future commits use the
noreply address.

Old tip -> new tip per repo (all other SHAs in each history changed likewise):

- `RosarioM123` (profile): `7131f3e9` -> `e6937e0b084c`
- `alphavoice`: `76473b69` -> `d6dc9a668d35`
- `odds-prediction-mispricing`: `494260e7` -> `93857b51d389`
- `reality-spatial-intelligence`: `d1ca0dc0` -> `ba09965a39be`
- `signal-research-lab`: `62fca9e1` -> `53ed1d78c770`
- `world-workstate-infrastructure`: `02fc199d` -> `8549f152366d`

Consequences, stated plainly:

- Commit SHAs cited in docs before this date now refer to superseded objects.
  The history is otherwise identical.
- The old objects are unreachable from any branch but may persist in GitHub's
  storage until garbage-collected; anyone who already cloned or forked keeps
  the old data. This rewrite removes the email from GitHub's live views, not
  from copies already outside GitHub.
- `BACKED` is an empty repo (no commits) and needed no rewrite.
