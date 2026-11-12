# Revalidation provenance note (2026-11-04)

The 18 continuation outputs under `raw/` were re-filed once, and the
blinded grading was restarted, for the following reason.

The continuation results first reached the coordinating session as
individual deliveries. When the runtime later delivered the
consolidated completion batch for all 18 continuation agents, the
batch texts for tasks R2 and C1 described the actual task scenarios
(the R2 onboarding user study and the C1 Riverside Hall offsite,
matching `experiments/experiment-003/tasks/*/ground_truth.json` and
the prompt files under `prompts/`), while the individually filed
copies for R2 and C1 described scenarios that appear nowhere in this
repository. The R1 texts also differed in wording between the two
deliveries.

Resolution: the consolidated batch was treated as authoritative
(it is consistent with the on-disk prompt files, bundles, and ground
truths; the other set was not). All 18 files under `raw/` were
rewritten verbatim from the batch delivery, a scenario-keyword check
was run over every file (Team Notes / onboarding / Riverside Hall),
the previous `judged/` copies and label mapping were deleted, a
fresh blind mapping was generated, and grading was re-run from
scratch with new grader agents. The first set of grader agents was
stopped before producing scores used anywhere.

Scores under `scores/` and the numbers in `RESULTS.md` derive only
from the re-filed outputs.
