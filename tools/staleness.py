#!/usr/bin/env python3
"""staleness.py - flag WORLD bundle entities whose recorded state contradicts repo reality.

Reads a world-state.json bundle and checks every entity's `source` field:
  - path-like sources (docs/..., src/...) must still exist in the repo checkout
  - commit SHAs mentioned in sources must exist in the repo's object store
  - files recorded before their `created_at` date that changed afterwards are
    flagged as "changed since recorded" (warning, not stale)

Entities whose sources are prose ("two consecutive failures") are reported as
uncheckable; they are not counted as stale. Semantic staleness (a true statement
that stopped being true) still needs a human rot check. This tool catches
reference rot: the bundle pointing at things that no longer exist.

Usage:
    python3 staleness.py --bundle world-state.json --repo /path/to/repo
    python3 staleness.py --bundle world-state.json --repo /path/to/repo --json

Exit code is 1 when any entity is stale, 0 otherwise.
"""

import argparse
import json
import os
import re
import subprocess
import sys

PATH_RE = re.compile(r"^[A-Za-z0-9_.\-]+(/[A-Za-z0-9_.\-]+)+\.[a-zA-Z0-9]+$")
SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def is_path_like(source):
    return bool(PATH_RE.match(source.strip().split("#")[0]))


def path_exists(repo, source):
    return os.path.exists(os.path.join(repo, source.strip().split("#")[0]))


def sha_exists(repo, sha):
    r = subprocess.run(
        ["git", "cat-file", "-e", sha],
        cwd=repo,
        capture_output=True,
    )
    return r.returncode == 0


def changed_since(repo, source, created_at):
    """True if the file has commits after the entity's created_at date."""
    if not DATE_RE.match(created_at or ""):
        return None
    r = subprocess.run(
        ["git", "log", "--since=" + created_at, "--format=%h", "--", source],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    return bool(r.stdout.strip())


def check_entity(repo, kind, entity):
    eid = entity.get("id", "?")
    source = entity.get("source", "")
    created_at = entity.get("created_at", "")
    result = {"id": eid, "kind": kind, "source": source, "verdict": "uncheckable", "detail": ""}

    if not source:
        result["detail"] = "no source recorded"
        return result

    shas = SHA_RE.findall(source)
    if is_path_like(source):
        if not path_exists(repo, source):
            result["verdict"] = "stale"
            result["detail"] = "referenced path no longer exists in repo"
            return result
        changed = changed_since(repo, source.strip().split("#")[0], created_at)
        if changed:
            result["verdict"] = "changed"
            result["detail"] = "file changed in repo after entity was recorded"
        elif changed is None:
            result["verdict"] = "ok"
            result["detail"] = "path exists; change history unavailable"
        else:
            result["verdict"] = "ok"
            result["detail"] = "path exists and unchanged since recorded"
    elif shas:
        missing = [s for s in shas if not sha_exists(repo, s)]
        if missing:
            result["verdict"] = "stale"
            result["detail"] = "referenced commit(s) not in repo: " + ", ".join(missing)
        else:
            result["verdict"] = "ok"
            result["detail"] = "referenced commit(s) exist"
    else:
        result["detail"] = "source is prose, not a checkable reference"
    return result


def main():
    ap = argparse.ArgumentParser(description="Detect reference rot in a WORLD state bundle.")
    ap.add_argument("--bundle", required=True, help="path to world-state.json")
    ap.add_argument("--repo", required=True, help="path to a checkout of the repo the bundle describes")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    with open(args.bundle) as f:
        bundle = json.load(f)

    entities = []
    for kind in ("decisions", "assumptions", "questions"):
        for e in bundle.get(kind, []):
            entities.append((kind, e))

    results = [check_entity(args.repo, kind, e) for kind, e in entities]

    if args.json:
        print(json.dumps(results, indent=1))
    else:
        for r in results:
            print("%-4s %-12s %-40s %s" % (r["verdict"].upper(), r["id"], r["source"][:40], r["detail"]))

    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    if not args.json:
        print("\n%d entities: %s" % (len(results), ", ".join("%d %s" % (v, k) for k, v in sorted(counts.items()))))

    sys.exit(1 if counts.get("stale", 0) else 0)


if __name__ == "__main__":
    main()
