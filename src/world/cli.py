"""Command-line interface for the WORLD primitive: the ``world`` command."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from .core import ConflictError, Invariant, InvariantViolation, World


def _world(
    args: argparse.Namespace, invariants: list[Invariant] | None = None
) -> World:
    return World(args.name, dir=args.dir, invariants=invariants)


def _load_json_file(path_str: str) -> dict[str, Any]:
    text = sys.stdin.read() if path_str == "-" else Path(path_str).read_text()
    data = json.loads(text)
    if not isinstance(data, dict):
        raise TypeError("top-level JSON must be an object")
    return data


def cmd_init(args: argparse.Namespace) -> int:
    w = _world(args)
    print(f"initialized world {w.name!r} at {w.path}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    w = _world(args)
    try:
        seq = w.update(
            _load_json_file(args.file),
            actor=args.actor,
            note=args.note or "",
            expected_version=args.expected_version,
            idempotency_key=args.idempotency_key,
        )
    except ConflictError as e:
        print(f"conflict: {e}", file=sys.stderr)
        return 1
    except InvariantViolation as e:
        print(f"rejected (seq {e.seq}): {e.reason}", file=sys.stderr)
        return 1
    print(seq)
    return 0


def cmd_update_many(args: argparse.Namespace) -> int:
    """Apply many updates from a JSONL file (one state per line)."""
    w = _world(args)
    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text()
    states = [json.loads(line) for line in text.splitlines() if line.strip()]
    try:
        seqs = w.update_many(
            states,
            actor=args.actor,
            note=args.note or "",
            expected_version=args.expected_version,
        )
    except ConflictError as e:
        print(f"conflict: {e}", file=sys.stderr)
        return 1
    except InvariantViolation as e:
        print(f"rejected (seq {e.seq}): {e.reason}", file=sys.stderr)
        return 1
    print(json.dumps(seqs))
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    w = _world(args)
    try:
        state = w.state(version=args.version, checkpoint=args.checkpoint)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    """Print {"version": v, "state": doc}: the OCC read half in one call."""
    w = _world(args)
    state, version = w.read()
    print(json.dumps({"version": version, "state": state}, indent=2, sort_keys=True))
    return 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    w = _world(args)
    try:
        seq = w.checkpoint(args.cp_name)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(seq)
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    w = _world(args)
    try:
        seq = w.resume(args.cp_name, actor=args.actor, note=args.note)
    except KeyError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except InvariantViolation as e:
        print(f"rejected (seq {e.seq}): {e.reason}", file=sys.stderr)
        return 1
    print(seq)
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    w = _world(args)
    print(json.dumps(w.history(limit=args.limit), indent=2))
    return 0


def cmd_proposal(args: argparse.Namespace) -> int:
    w = _world(args)
    try:
        proposal = w.proposal(args.seq)
    except KeyError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(proposal, indent=2, sort_keys=True))
    return 0


def cmd_checkpoints(args: argparse.Namespace) -> int:
    w = _world(args)
    print(json.dumps(w.checkpoints(), indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    w = _world(args)
    if w.verify():
        print("ok")
        return 0
    print("FAILED: hash chain broken", file=sys.stderr)
    return 1


def _diff_values(old: Any, new: Any, prefix: str, out: list[dict[str, Any]]) -> None:
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(set(old) | set(new)):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in old:
                out.append({"path": path, "change": "added", "old": None, "new": new[key]})
            elif key not in new:
                out.append({"path": path, "change": "removed", "old": old[key], "new": None})
            else:
                _diff_values(old[key], new[key], path, out)
    elif isinstance(old, list) and isinstance(new, list):
        for i in range(max(len(old), len(new))):
            path = f"{prefix}.{i}" if prefix else str(i)
            if i >= len(old):
                out.append({"path": path, "change": "added", "old": None, "new": new[i]})
            elif i >= len(new):
                out.append({"path": path, "change": "removed", "old": old[i], "new": None})
            else:
                _diff_values(old[i], new[i], path, out)
    elif old != new:
        out.append({"path": prefix, "change": "modified", "old": old, "new": new})


def cmd_blame(args: argparse.Namespace) -> int:
    w = _world(args)
    print(json.dumps(w.blame(args.path, version=args.version), indent=2, sort_keys=True))
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    w = _world(args)
    old = w.state(version=args.from_version)
    new = w.state(version=args.to_version) if args.to_version is not None else w.state()
    out: list[dict[str, Any]] = []
    _diff_values(old, new, "", out)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Dump every proposal row as JSONL (committed and rejected)."""
    w = _world(args)
    lines = [
        json.dumps(w.proposal(r["seq"]), sort_keys=True) for r in w.history()
    ]
    text = "\n".join(lines) + ("\n" if lines else "")
    if args.file and args.file != "-":
        Path(args.file).write_text(text)
    else:
        print(text, end="")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    """Replay an export file's COMMITTED rows as new updates.

    The import builds a fresh hash chain (new timestamps, new hashes);
    use ``export`` + ``verify`` on the source for audit fidelity. Rejected
    rows are skipped: they were never state, only evidence.
    """
    w = _world(args)
    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text()
    imported = skipped = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") != "COMMITTED":
            skipped += 1
            continue
        note = f"imported seq {row.get('seq')}"
        if row.get("note"):
            note += f": {row['note']}"
        w.update(row["state"], actor=row.get("actor"), note=note)
        imported += 1
    print(f"imported {imported} versions, skipped {skipped} rejected")
    return 0


def cmd_import_transcript(args: argparse.Namespace) -> int:
    from .producers import import_transcript

    w = _world(args)
    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text()
    seq = import_transcript(w, text, actor=args.actor)
    print(seq)
    return 0


def _load_invariants(spec: str) -> list[Invariant]:
    mod_name, _, attr = spec.partition(":")
    if not attr:
        raise ValueError("use --invariants module:attribute")
    mod = importlib.import_module(mod_name)
    invs = getattr(mod, attr)
    return list(invs)


def cmd_serve(args: argparse.Namespace) -> int:
    try:
        import uvicorn  # lazy: `world` works without server deps installed

        from .server import create_app
    except ImportError:
        print(
            'error: `world serve` needs the server extra: pip install -e ".[server]"',
            file=sys.stderr,
        )
        return 2

    invariants = _load_invariants(args.invariants) if args.invariants else []
    api_key = args.api_key or os.environ.get("WORLD_API_KEY")
    app = create_app(
        args.name,
        dir=args.dir,
        invariants=invariants,
        api_key=api_key,
        write_limit_per_min=args.rate_limit,
    )
    uvicorn.run(app, host=args.host, port=args.port)
    return 0  # pragma: no cover - blocks serving


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="world", description="WORLD work-state primitive")
    p.add_argument(
        "--dir", default=None, help="storage dir (default $WORLD_DIR or ~/.world)"
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="create (or open) a world")
    s.add_argument("name")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser(
        "update", help="replace the document (reads JSON file, '-' for stdin)"
    )
    s.add_argument("name")
    s.add_argument("--file", required=True)
    s.add_argument("--actor", default=None)
    s.add_argument("--note", default="")
    s.add_argument("--expected-version", type=int, default=None)
    s.add_argument("--idempotency-key", default=None)
    s.set_defaults(func=cmd_update)

    s = sub.add_parser(
        "update-many", help="apply many updates, one JSONL state per line"
    )
    s.add_argument("name")
    s.add_argument("--file", required=True, help="JSONL file, '-' for stdin")
    s.add_argument("--actor", default=None)
    s.add_argument("--note", default="")
    s.add_argument("--expected-version", type=int, default=None)
    s.set_defaults(func=cmd_update_many)

    s = sub.add_parser("state", help="print the document as JSON")
    s.add_argument("name")
    s.add_argument("--version", type=int, default=None)
    s.add_argument("--checkpoint", default=None)
    s.set_defaults(func=cmd_state)

    s = sub.add_parser(
        "read", help="print {version, state} atomically (OCC read half)"
    )
    s.add_argument("name")
    s.set_defaults(func=cmd_read)

    s = sub.add_parser("checkpoint", help="pin the current version under a name")
    s.add_argument("name")
    s.add_argument("cp_name")
    s.set_defaults(func=cmd_checkpoint)

    s = sub.add_parser("resume", help="restore a checkpoint as a new version")
    s.add_argument("name")
    s.add_argument("cp_name")
    s.add_argument("--actor", default=None)
    s.add_argument("--note", default=None)
    s.set_defaults(func=cmd_resume)

    s = sub.add_parser("history", help="print the verdict log as JSON")
    s.add_argument("name")
    s.add_argument("--limit", type=int, default=None)
    s.set_defaults(func=cmd_history)

    s = sub.add_parser("proposal", help="print one proposal row as JSON (any status)")
    s.add_argument("name")
    s.add_argument("seq", type=int)
    s.set_defaults(func=cmd_proposal)

    s = sub.add_parser("checkpoints", help="list checkpoints as JSON")
    s.add_argument("name")
    s.set_defaults(func=cmd_checkpoints)

    s = sub.add_parser("verify", help="check the hash chain")
    s.add_argument("name")
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("diff", help="diff two versions as JSON")
    s.add_argument("name")
    s.add_argument("--from", dest="from_version", type=int, required=True)
    s.add_argument("--to", dest="to_version", type=int, default=None)
    s.set_defaults(func=cmd_diff)

    s = sub.add_parser("blame", help="show who last changed a field as JSON")
    s.add_argument("name")
    s.add_argument("path", help="dot-separated field path, e.g. budget.total")
    s.add_argument("--version", dest="version", type=int, default=None,
                   help="blame as of this committed version (default: latest)")
    s.set_defaults(func=cmd_blame)

    s = sub.add_parser("export", help="dump every proposal row as JSONL")
    s.add_argument("name")
    s.add_argument("--file", default="-", help="output file ('-' for stdout)")
    s.set_defaults(func=cmd_export)

    s = sub.add_parser(
        "import",
        help="replay an export JSONL into a world (fresh hash chain; "
        "rejected rows are skipped)",
    )
    s.add_argument("name")
    s.add_argument("--file", required=True, help="export file ('-' for stdin)")
    s.set_defaults(func=cmd_import)

    s = sub.add_parser(
        "import-transcript", help="fold a chat transcript into the document"
    )
    s.add_argument("name")
    s.add_argument("--file", required=True, help="transcript file ('-' for stdin)")
    s.add_argument("--actor", default=None)
    s.set_defaults(func=cmd_import_transcript)

    s = sub.add_parser("serve", help="serve the world over HTTP")
    s.add_argument("name")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--api-key", default=None)
    s.add_argument(
        "--invariants", default=None, help="module:attribute with invariant list"
    )
    s.add_argument(
        "--rate-limit", type=int, default=60, help="writes/min/IP, 0 to disable"
    )
    s.set_defaults(func=cmd_serve)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, TypeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
