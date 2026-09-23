"""Model adapters: how the runner obtains continuations.

The benchmark never calls an LLM provider directly. Programmatic runs use
an adapter — any object with ``complete(system, user)`` returning an
``AdapterResult``::

    # my_adapter.py
    from runner.adapters import AdapterResult

    class MyAdapter:
        def complete(self, system: str, user: str) -> AdapterResult:
            text = call_your_model(system, user)  # your provider here
            return AdapterResult(text=text)

    python runner/run.py run --adapter my_adapter:MyAdapter --out results/run1

Manual runs (any model, any chat UI, no API keys) use the two-step flow::

    python runner/run.py build-prompts --out /tmp/prompts
    # ... paste each prompt into your model, save continuations to
    # /tmp/raw/<task>__<condition>.md ...
    python runner/run.py manifest --prompts /tmp/prompts --raw /tmp/raw \\
        --out /tmp/manifest.json
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class AdapterResult:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class ModelAdapter(Protocol):
    def complete(self, system: str, user: str) -> AdapterResult:
        """Return the model's continuation for the prompt."""
        ...


class EchoAdapter:
    """Dry-run adapter: returns canned text, for pipeline smoke tests."""

    def __init__(self, text: str = "echo continuation") -> None:
        self.text = text

    def complete(self, system: str, user: str) -> AdapterResult:
        return AdapterResult(text=self.text)
