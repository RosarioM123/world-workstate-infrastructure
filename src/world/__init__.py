"""WORLD v0.1 — a minimal, verifiable work-state primitive.

A :class:`~world.core.World` is a named, durable unit of work: an opaque JSON
document whose every change is judged by optional invariants, with every
verdict (COMMITTED or REJECTED) appended to a hash-chained log.
"""

from .core import ConflictError, InvariantViolation, World

__version__ = "0.1.0"

__all__ = ["ConflictError", "InvariantViolation", "World", "__version__"]
