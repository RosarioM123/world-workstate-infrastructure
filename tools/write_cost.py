#!/usr/bin/env python3
"""write_cost.py - measure the WORLD record transition.

The record transition is the end-of-session work: updating WORLD.md,
world-state.json, the rot log, and writing the session file. Idea 5's bar is
60 seconds of agent time; the write-side trial's bar is 5 minutes.

Usage:
    python3 write_cost.py record --session 2026-09-21-02 --seconds 94 --entities 4
    python3 write_cost.py report

The log is a JSONL file (one record per session). Use --log to point at a
different file; the default is ./write-cost.jsonl next to the script.
"""

import argparse
import json
import os
import statistics
import sys

DEFAULT_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "write-cost.jsonl")
TRIAL_TARGET = 300   # write-side trial pass/fail: under 5 minutes
PRODUCT_TARGET = 60  # idea 5 aspiration: under 60 seconds of agent time


def cmd_record(args):
    entry = {
        "session": args.session,
        "seconds": args.seconds,
        "entities_changed": args.entities,
        "note": args.note or "",
    }
    with open(args.log, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print("recorded: session %s, %ds, %d entities -> %s" % (args.session, args.seconds, args.entities, args.log))


def cmd_report(args):
    if not os.path.exists(args.log):
        print("no data yet at %s" % args.log)
        return
    rows = [json.loads(line) for line in open(args.log) if line.strip()]
    if not rows:
        print("no data yet at %s" % args.log)
        return
    secs = [r["seconds"] for r in rows]
    under_product = sum(1 for s in secs if s <= PRODUCT_TARGET)
    under_trial = sum(1 for s in secs if s <= TRIAL_TARGET)
    print("sessions: %d" % len(rows))
    print("mean: %.0fs  median: %.0fs  min: %ds  max: %ds" % (
        statistics.mean(secs), statistics.median(secs), min(secs), max(secs)))
    print("under %ds (product bar): %d/%d" % (PRODUCT_TARGET, under_product, len(rows)))
    print("under %ds (trial bar):   %d/%d" % (TRIAL_TARGET, under_trial, len(rows)))
    for r in rows:
        flag = ""
        if r["seconds"] > TRIAL_TARGET:
            flag = "  OVER TRIAL BAR"
        elif r["seconds"] > PRODUCT_TARGET:
            flag = "  over product bar"
        print("  %s: %ds (%d entities)%s%s" % (
            r["session"], r["seconds"], r["entities_changed"], " " + r["note"] if r["note"] else "", flag))


def main():
    ap = argparse.ArgumentParser(description="Measure the WORLD record transition.")
    ap.add_argument("--log", default=DEFAULT_LOG)
    sub = ap.add_subparsers(dest="cmd", required=True)

    rec = sub.add_parser("record", help="log one session's record-transition time")
    rec.add_argument("--session", required=True)
    rec.add_argument("--seconds", required=True, type=int)
    rec.add_argument("--entities", required=True, type=int, help="entities added/changed/retired")
    rec.add_argument("--note", default="")
    rec.set_defaults(fn=cmd_record)

    rep = sub.add_parser("report", help="summarize recorded sessions")
    rep.set_defaults(fn=cmd_report)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
