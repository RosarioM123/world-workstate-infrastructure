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


def cmd_state(args: argparse.Namespace) -> int:
    w = _world(args)
    try:
        state = w.state(version=args.version, checkpoint=args.checkpoint)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(state, indent=2, sort_keys=True))
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

    s = sub.add_parser("state", help="print the document as JSON")
    s.add_argument("name")
    s.add_argument("--version", type=int, default=None)
    s.add_argument("--checkpoint", default=None)
    s.set_defaults(func=cmd_state)

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

    s = sub.add_parser("checkpoints", help="list checkpoints as JSON")
    s.add_argument("name")
    s.set_defaults(func=cmd_checkpoints)

    s = sub.add_parser("verify", help="check the hash chain")
    s.add_argument("name")
    s.set_defaults(func=cmd_verify)

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
