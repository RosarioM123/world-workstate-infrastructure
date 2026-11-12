"""Single prompt code path for Experiment #003 continuations.

Every Agent B prompt in every condition is composed here: one system
prompt, the task's continuation assignment verbatim, and one handoff
artifact. Conditions cannot receive different instructions because there
is exactly one composition function.
"""

import hashlib

SYSTEM_PROMPT = """You are an AI agent resuming a task started by another agent in a previous session. You have no memory of that session. The only record of the prior work available to you is the handoff material included in this prompt. Work only from that material: do not invent facts, figures, names, dates, or commitments that are not in it. Where information you need is missing from the material, say so explicitly instead of filling the gap. Where the material records that something was later changed or superseded, treat the latest version as authoritative and say what changed. Complete the continuation assignment exactly as specified."""

CONDITION_ARTIFACTS = {
    "A": "state.md",
    "B": "summary.md",
    "C": "journal.md",
}


def compose(continuation_assignment: str, artifact_text: str) -> str:
    """Compose the full user prompt for one continuation trial."""
    return (
        continuation_assignment.rstrip()
        + "\n\n----- HANDOFF MATERIAL FROM THE PREVIOUS SESSION -----\n\n"
        + artifact_text.rstrip()
        + "\n"
    )


def system_prompt_hash() -> str:
    return hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()
