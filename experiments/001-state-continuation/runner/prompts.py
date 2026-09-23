"""Prompt composition: one code path for all conditions.

Every continuation prompt is: SYSTEM (fixed) + handoff artifact (the only
thing that varies) + brief (fixed, from dataset/tasks/<id>/brief.md).
Conditions cannot receive different instructions.
"""

from __future__ import annotations

from pathlib import Path

SYSTEM = """You are a senior engineer continuing a colleague's work. You \
have received a handoff describing what they did and decided. Read it \
carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.
"""

FORMAT_TAGS = {
    "transcript": "[Format: chronological transcript]",
    "summary": "[Format: written summary]",
    "world": "[Format: structured JSON state]",
}

CONDITIONS = ("transcript", "summary", "world")


def load_artifact(task_dir: Path, condition: str) -> str:
    if condition == "world":
        return (task_dir / "artifacts" / "world.json").read_text()
    return (task_dir / "artifacts" / f"{condition}.md").read_text()


def load_brief(task_dir: Path) -> str:
    return (task_dir / "brief.md").read_text()


def build_prompt(task_dir: Path, condition: str) -> tuple[str, str]:
    """Return (system, user) for one task x condition."""
    artifact = load_artifact(task_dir, condition)
    brief = load_brief(task_dir)
    user = (
        f"{FORMAT_TAGS[condition]}\n\n"
        f"--- HANDOFF FROM PREVIOUS AGENT ---\n{artifact}\n"
        f"--- END HANDOFF ---\n\n"
        f"--- YOUR TASK ---\n{brief}\n--- END TASK ---"
    )
    return SYSTEM, user
