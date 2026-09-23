"""Shared text utilities for the benchmark evaluation.

Matching is deliberately dumb (methodology §8.7): normalized substring
matching, plus two heuristics that keep the deterministic metrics honest:

- Negation filtering: sentences containing negation cues are excluded
  when checking must_not_state phrases, so "not a database outage" is
  not scored as claiming a database outage.
- Proposal filtering: already_done phrases only count when the sentence
  also carries proposal language ("should", "will", "next step", ...),
  so "we already rolled back" is not scored as re-proposing the rollback.
"""

from __future__ import annotations

import re

_NEGATION = re.compile(
    r"\b(not|never|n't|no\b|without|instead of|rather than|isn't|wasn't|aren't|"
    r"weren't|don't|doesn't|didn't|can't|cannot|won't|shouldn't|against)\b",
    re.IGNORECASE,
)

_PROPOSAL = re.compile(
    r"\b(should|need to|needs to|must|will|shall|plan to|propose|proposes|"
    r"recommend|recommends|action items?|next steps?|todo|let's)\b",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sentences(text: str) -> list[str]:
    # Split on sentence-ending punctuation followed by a capital letter or
    # markdown block marker, so version numbers ("v2.13") and decimals
    # don't fracture sentences.
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z*#\-])", text) if s.strip()]


def phrase_match(phrase: str, haystack: str) -> bool:
    """Normalized substring match, tolerating orthographic variants.

    "roll back" matches "rollback": compare spaceless as a fallback so
    hyphen/space spelling differences don't fail a semantically present
    phrase. Minimum length guards against tiny-phrase false positives.
    """
    p, h = normalize(phrase), normalize(haystack)
    if p in h:
        return True
    ps, hs = p.replace(" ", ""), h.replace(" ", "")
    return len(ps) >= 6 and ps in hs


def non_negated(text: str) -> str:
    """Text with negated sentences removed (for contradiction checks)."""
    return " ".join(s for s in sentences(text) if not _NEGATION.search(s))


def proposal_sentences(text: str) -> str:
    """Sentences carrying proposal language (for repeated-work checks)."""
    return " ".join(s for s in sentences(text) if _PROPOSAL.search(s))


def contradiction_hit(phrase: str, text: str) -> bool:
    """Is a forbidden phrase *asserted* (not merely denied)?

    A phrase counts when it appears in the full text AND either the
    phrase itself carries the negation ("soc2 is not required" asserts
    exactly that) or it survives negation filtering ("not a database
    outage" is a denial, not an assertion).
    """
    norm_phrase, norm_full = normalize(phrase), normalize(text)
    if norm_phrase not in norm_full and not phrase_match(phrase, text):
        return False
    if _NEGATION.search(norm_phrase):
        return True
    return phrase_match(phrase, non_negated(text))
