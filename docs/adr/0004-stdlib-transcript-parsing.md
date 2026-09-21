# ADR 0004: Stdlib-only transcript parsing

Date: 2026-09-21
Status: Accepted

## Context

The transcript importer turns chat exports into ledger intents
(decisions, assumptions, questions, constraints, notes). The obvious
implementation is an LLM call per transcript. The alternative is a
deterministic, rule-based parser using only the standard library.

## Decision

Parse with deterministic rules and stdlib only (`re`, `hashlib`, no
network, no model). Classification is keyword-based; idempotency comes
from a content hash of kind, speaker, and text, so re-imports never
double-commit.

## Consequences

- Good: the importer is free, offline, fast, and perfectly
  reproducible. Same transcript in, same intents out, on any machine,
  which is exactly the determinism guarantee the ledger is built on.
  An LLM in this path would make imports non-reproducible and turn a
  free local tool into a metered API dependency.
- Good: no prompt-injection surface. Transcript text is untrusted
  third-party content; a rule-based parser cannot be talked into
  emitting intents the rules do not produce.
- Bad: classification is crude. Keyword matching misses nuance an LLM
  would catch, and new phrasings need new keywords.
- Revisit when: extraction quality, measured against a labeled
  transcript set, becomes the bottleneck. The sane upgrade is an
  LLM *suggester* whose output still passes through the deterministic
  validator and the engine's constraint checks, never a direct
  LLM-to-ledger path.
