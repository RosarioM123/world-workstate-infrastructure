"""Shipped invariant helpers for the WORLD primitive.

An invariant is a callable ``(old_state, new_state) -> None`` that raises
:class:`~world.core.InvariantViolation` to reject a proposed transition.
These helpers build the common ones; anything else is a plain function.

Path patterns are dot-separated, with ``*`` matching every key (or list
item) at one level: ``"totals.*"``, ``"tasks.0.status"``. With no patterns,
helpers apply to every matching leaf in the document.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from typing import Any

from .core import Invariant, InvariantViolation

__all__ = [
    "finite_numbers",
    "no_negative",
    "require_keys",
    "respect_locks",
]


def _resolve(doc: Any, parts: list[str], prefix: str) -> Iterator[tuple[str, Any]]:
    """Yield (dotted_path, value) for a path pattern over ``doc``."""
    if not parts:
        yield prefix, doc
        return
    head, rest = parts[0], parts[1:]
    if head == "*":
        children: Any = ()
        if isinstance(doc, dict):
            children = doc.items()
        elif isinstance(doc, list):
            children = enumerate(doc)
        for key, value in children:
            child = f"{prefix}.{key}" if prefix else str(key)
            yield from _resolve(value, rest, child)
    elif isinstance(doc, dict) and head in doc:
        child = f"{prefix}.{head}" if prefix else head
        yield from _resolve(doc[head], rest, child)
    elif isinstance(doc, list) and head.isdigit() and int(head) < len(doc):
        child = f"{prefix}.{head}" if prefix else head
        yield from _resolve(doc[int(head)], rest, child)


def _walk_leaves(doc: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    if isinstance(doc, dict):
        for key, value in doc.items():
            yield from _walk_leaves(value, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(doc, list):
        for i, value in enumerate(doc):
            yield from _walk_leaves(value, f"{prefix}.{i}" if prefix else str(i))
    else:
        yield prefix, doc


def _targets(new: dict[str, Any], paths: tuple[str, ...]) -> Iterator[tuple[str, Any]]:
    if not paths:
        yield from _walk_leaves(new)
    else:
        for pattern in paths:
            yield from _resolve(new, pattern.split("."), "")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def no_negative(*paths: str) -> Invariant:
    """Reject a transition that would leave a numeric field negative."""

    def check(old: dict[str, Any], new: dict[str, Any]) -> None:
        for path, value in _targets(new, paths):
            if _is_number(value) and value < 0:
                raise InvariantViolation(f"no_negative: {path} = {value}")

    return check


def finite_numbers(*paths: str) -> Invariant:
    """Reject non-finite numbers (inf; NaN is already rejected at the gate)."""

    def check(old: dict[str, Any], new: dict[str, Any]) -> None:
        for path, value in _targets(new, paths):
            if _is_number(value) and not math.isfinite(value):
                raise InvariantViolation(f"finite_numbers: {path} = {value}")

    return check


def require_keys(*paths: str) -> Invariant:
    """Reject a transition missing any of the required paths."""

    def check(old: dict[str, Any], new: dict[str, Any]) -> None:
        for pattern in paths:
            if not any(True for _ in _resolve(new, pattern.split("."), "")):
                raise InvariantViolation(f"require_keys: missing {pattern}")

    return check


def respect_locks(lock_key: str = "_locks") -> Invariant:
    """Reject changes to locked paths.

    Convention: ``old[lock_key]`` is a list of path patterns. A locked path's
    value must be identical in the new state, and locked paths cannot be
    removed. Locking and unlocking are ordinary versioned updates (edit the
    list), so every lock change is itself audited. Missing paths and a
    missing/non-list lock key are ignored.
    """

    def check(old: dict[str, Any], new: dict[str, Any]) -> None:
        locked = old.get(lock_key, [])
        if not isinstance(locked, list):
            return
        for pattern in locked:
            if not isinstance(pattern, str):
                continue
            old_vals = dict(_resolve(old, pattern.split("."), ""))
            new_vals = dict(_resolve(new, pattern.split("."), ""))
            for path, old_value in old_vals.items():
                if path not in new_vals:
                    raise InvariantViolation(
                        f"respect_locks: {path} removed while locked"
                    )
                if new_vals[path] != old_value:
                    raise InvariantViolation(
                        f"respect_locks: {path} changed while locked"
                    )

    return check
