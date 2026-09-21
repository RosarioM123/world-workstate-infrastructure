#!/usr/bin/env python3
"""guardrail_audit.py - re-run a session's actions against the bundle's guardrails.

Idea 6: experiment #001 proved transcripts drop guardrails silently. This pass
takes the session's action log and the bundle's guardrail list and flags
violations mechanically. What it cannot check (honest reporting, G4) it marks
MANUAL so a human does the semantic review.

Action log format (JSON list), one entry per action:
    {"type": "write", "target": "tools/staleness.py", "path": "/tmp/x.py"}
    {"type": "commit", "target": "branch main", "detail": "..."}
    {"type": "read", "target": "docs/startup/mvp.md"}

`target` is the repo-relative path for writes. `path` is the local file to scan
for text checks (em dashes, secrets); it must contain the exact bytes committed.

Usage:
    python3 guardrail_audit.py --bundle world-state.json --actions session-02-actions.json

Exit code is 1 when any guardrail is flagged, 0 otherwise.
"""

import argparse
import json
import re
import sys

EM_DASH = "\u2014"
PROTECTED_PREFIXES = ("docs/experiment-002/",)
PROTECTED_FILES = ("docs/development-log.md",)
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)


def check_g1(actions):
    """No em dashes in polished or repo-facing text."""
    hits = []
    for a in actions:
        if a.get("type") == "write" and a.get("path"):
            try:
                text = open(a["path"], encoding="utf-8").read()
            except OSError:
                continue
            n = text.count(EM_DASH)
            if n:
                hits.append("%s (%d em dash%s)" % (a["target"], n, "es" if n > 1 else ""))
    if hits:
        return "FLAG", "; ".join(hits)
    return "PASS", "no em dashes in %d written files" % sum(1 for a in actions if a.get("path"))


def check_g2(actions):
    """Never touch experiment-002 or development-log.md outside the schedule."""
    hits = []
    for a in actions:
        t = (a.get("target") or "")
        if a.get("type") == "write" and (
            t in PROTECTED_FILES or t.startswith(PROTECTED_PREFIXES)
        ):
            hits.append(t)
    if hits:
        return "FLAG", "protected path written: " + ", ".join(hits)
    return "PASS", "no writes to protected paths"


def check_g3(actions):
    """No license changes, secrets, history rewrites, or new product features."""
    hits = []
    for a in actions:
        t = (a.get("target") or "").lower()
        if a.get("type") == "write" and t.startswith("license"):
            hits.append("license file written: " + a["target"])
        if a.get("type") in ("history-rewrite", "force-push", "rebase"):
            hits.append("history rewrite action: " + a["type"])
        if a.get("path"):
            try:
                text = open(a["path"], encoding="utf-8").read()
            except OSError:
                continue
            if SECRET_RE.search(text):
                hits.append("possible secret in " + a["target"])
    if hits:
        return "FLAG", "; ".join(hits)
    return "PASS", "no license/secret/history issues in %d actions" % len(actions)


CHECKS = [
    ("G1", "No em dashes in polished or repo-facing text", check_g1),
    ("G2", "Never touch docs/experiment-002/ or docs/development-log.md outside the experiment schedule", check_g2),
    ("G3", "No license changes, secrets, history rewrites, or new product features in the validation program", check_g3),
    ("G4", "Report evidence honestly, including evidence against WORLD", None),  # manual
]


def main():
    ap = argparse.ArgumentParser(description="Audit a session's actions against bundle guardrails.")
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--actions", required=True, help="JSON action log for the session")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    bundle = json.load(open(args.bundle))
    actions = json.load(open(args.actions))
    guardrails = {g["id"]: g for g in bundle.get("guardrails", [])}

    results = []
    for gid, rule, fn in CHECKS:
        if gid not in guardrails:
            results.append({"id": gid, "rule": rule, "verdict": "SKIP", "detail": "not in bundle"})
            continue
        if fn is None:
            results.append({"id": gid, "rule": rule, "verdict": "MANUAL",
                            "detail": "cannot be checked mechanically; needs human review"})
            continue
        verdict, detail = fn(actions)
        results.append({"id": gid, "rule": rule, "verdict": verdict, "detail": detail})

    if args.json:
        print(json.dumps(results, indent=1))
    else:
        for r in results:
            print("%-6s %s: %s" % (r["verdict"], r["id"], r["detail"]))

    sys.exit(1 if any(r["verdict"] == "FLAG" for r in results) else 0)


if __name__ == "__main__":
    main()
