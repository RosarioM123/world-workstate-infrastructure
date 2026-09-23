#!/usr/bin/env python3
"""Benchmark runner.

Programmatic (any provider via an adapter)::

    python runner/run.py run --adapter my_adapter:MyAdapter \\
        --tasks task_001_vendor_selection --out results/run1

Manual (any model, no API keys)::

    python runner/run.py build-prompts --out /tmp/prompts
    # paste each prompt into your model; save each continuation to
    # /tmp/raw/<task>__<condition>.md
    python runner/run.py manifest --prompts /tmp/prompts --raw /tmp/raw \\
        --out /tmp/manifest.json

All commands are stdlib-only.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from prompts import CONDITIONS, build_prompt

DATASET = HERE.parent / "dataset" / "tasks"


def _tasks(names: list[str] | None) -> list[Path]:
    all_tasks = sorted(p for p in DATASET.iterdir() if p.is_dir())
    if not names:
        return all_tasks
    wanted = set(names)
    found = [p for p in all_tasks if p.name in wanted]
    missing = wanted - {p.name for p in found}
    if missing:
        raise SystemExit(f"unknown tasks: {sorted(missing)}")
    return found


def _words(text: str) -> int:
    return len(text.split())


def cmd_build_prompts(args: argparse.Namespace) -> None:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for task_dir in _tasks(args.tasks):
        for condition in CONDITIONS:
            system, user = build_prompt(task_dir, condition)
            (out / f"{task_dir.name}__{condition}.md").write_text(
                f"{system}\n\n{user}"
            )
            print(f"wrote {task_dir.name}__{condition}.md")


def _load_adapter(dotted: str):
    mod_name, _, attr = dotted.partition(":")
    if not attr:
        raise SystemExit("--adapter must be module:Attribute")
    mod = importlib.import_module(mod_name)
    factory = getattr(mod, attr)
    return factory() if callable(factory) and not isinstance(factory, type) else factory


def cmd_run(args: argparse.Namespace) -> None:
    adapter = _load_adapter(args.adapter)
    out = Path(args.out)
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created": datetime.now(UTC).isoformat(),
        "adapter": args.adapter,
        "items": [],
    }
    for task_dir in _tasks(args.tasks):
        for condition in CONDITIONS:
            system, user = build_prompt(task_dir, condition)
            result = adapter.complete(system, user)
            name = f"{task_dir.name}__{condition}"
            (raw / f"{name}.md").write_text(result.text)
            manifest["items"].append(
                {
                    "task": task_dir.name,
                    "condition": condition,
                    "file": f"raw/{name}.md",
                    "prompt_words": _words(system + user),
                    "prompt_chars": len(system + user),
                    "output_words": _words(result.text),
                    "output_chars": len(result.text),
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                }
            )
            print(f"ran {name} ({_words(result.text)} words)")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"manifest: {out / 'manifest.json'}")


def cmd_manifest(args: argparse.Namespace) -> None:
    prompts = Path(args.prompts)
    raw = Path(args.raw)
    out = Path(args.out)
    manifest = {
        "created": datetime.now(UTC).isoformat(),
        "adapter": "manual",
        "items": [],
    }
    for task_dir in _tasks(args.tasks):
        for condition in CONDITIONS:
            name = f"{task_dir.name}__{condition}"
            prompt_file = prompts / f"{name}.md"
            raw_file = raw / f"{name}.md"
            if not prompt_file.exists():
                raise SystemExit(f"missing prompt: {prompt_file}")
            if not raw_file.exists():
                raise SystemExit(f"missing continuation: {raw_file}")
            prompt = prompt_file.read_text()
            text = raw_file.read_text()
            manifest["items"].append(
                {
                    "task": task_dir.name,
                    "condition": condition,
                    "file": str(raw_file),
                    "prompt_words": _words(prompt),
                    "prompt_chars": len(prompt),
                    "output_words": _words(text),
                    "output_chars": len(text),
                    "input_tokens": None,
                    "output_tokens": None,
                }
            )
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"manifest: {out} ({len(manifest['items'])} items)")


def main() -> None:
    parser = argparse.ArgumentParser(description="001-state-continuation runner")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("build-prompts", help="write prompt files for manual runs")
    p.add_argument("--out", required=True)
    p.add_argument("--tasks", nargs="*")
    p.set_defaults(func=cmd_build_prompts)

    p = sub.add_parser("run", help="run all task x condition via an adapter")
    p.add_argument("--adapter", required=True, help="module:Attribute")
    p.add_argument("--out", required=True)
    p.add_argument("--tasks", nargs="*")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("manifest", help="build manifest from manual raw files")
    p.add_argument("--prompts", required=True)
    p.add_argument("--raw", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--tasks", nargs="*")
    p.set_defaults(func=cmd_manifest)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
