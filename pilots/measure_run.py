#!/usr/bin/env python3
"""Real timing/event evidence for one pilot migration run (not an agent launcher).

Appends events to <run-dir>/events.jsonl and, on finish, writes <run-dir>/metrics.json.
Each event records UTC wall-clock time, CLOCK_MONOTONIC (ns) and the kernel boot id.
Monotonic deltas are only used between events on the same boot; intervals spanning a
reboot (or with no boot id available) fall back to clearly labelled wall-clock values.
Metrics that are not directly observable (tokens, cost, memory, model) stay null.

Usage:
  measure_run.py start      --run-dir D --run-id ID [--branch B] [--base-revision R] [--harness-revision R]
  measure_run.py checkpoint --run-dir D --phase NAME [--note TEXT]
  measure_run.py pause      --run-dir D [--note TEXT]
  measure_run.py resume     --run-dir D [--note TEXT]
  measure_run.py error      --run-dir D --message TEXT [--exit-code N]
  measure_run.py validate   --run-dir D --label NAME -- <command> [args...]
  measure_run.py finish     --run-dir D --outcome complete|partial|blocked|failed [--note TEXT]
  measure_run.py status     --run-dir D
"""
import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EVENTS = "events.jsonl"
METRICS = "metrics.json"
OUTCOMES = ("complete", "partial", "blocked", "failed")
DIVERGENCE_ABS_S = 5.0
DIVERGENCE_REL = 0.01


class StateError(Exception):
    pass


def system_clock():
    boot = None
    try:
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip() or None
    except OSError:
        pass
    return {"utc_epoch": time.time(), "monotonic_ns": time.monotonic_ns(), "boot_id": boot}


def _iso(epoch):
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def read_events(run_dir):
    path = Path(run_dir) / EVENTS
    if not path.exists():
        return []
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for i, e in enumerate(events, 1):
        if e.get("seq") != i:
            raise StateError(f"{path}: event sequence broken at line {i}")
    return events


def _state(events):
    for e in reversed(events):
        if e["type"] in ("start", "pause", "resume", "finish"):
            return {"start": "running", "resume": "running", "pause": "paused", "finish": "finished"}[e["type"]]
    return "new"


ALLOWED = {
    "start": {"new"},
    "checkpoint": {"running"},
    "pause": {"running"},
    "resume": {"paused"},
    "error": {"running", "paused"},
    "validation": {"running", "paused"},
    "finish": {"running", "paused"},
}


def _git(run_dir, *args):
    try:
        r = subprocess.run(["git", "-C", str(run_dir), *args], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _inputs(run_dir):
    out = {}
    for name in ("source-manifest.json", "preflight.json"):
        p = Path(run_dir) / name
        if p.exists():
            d = json.loads(p.read_text())
            s = d.get("summary", {})
            out.update({"tier": d.get("tier"), "seed": d.get("seed"), "manifest_sha256": d.get("manifest_sha256"),
                        "business": s.get("business"), "support": s.get("support"),
                        "total_files": s.get("total_files"), "total_bytes": s.get("total_bytes"),
                        "process_nodes": s.get("process_nodes"), "dependency_edges": s.get("dependency_edges"),
                        "exceptions": s.get("exceptions")})
            if name == "preflight.json":
                out["preflight_status"] = d.get("status")
    return out or None


def record(run_dir, kind, clock=None, **fields):
    run_dir = Path(run_dir)
    if kind not in ALLOWED:
        raise StateError(f"unknown event type {kind}")
    events = read_events(run_dir)
    state = _state(events)
    if state not in ALLOWED[kind]:
        raise StateError(f"cannot record '{kind}' while run is '{state}'")
    if kind == "start" and not fields.get("run_id"):
        raise StateError("start requires run_id")
    if kind == "checkpoint" and not fields.get("phase"):
        raise StateError("checkpoint requires phase")
    if kind == "finish" and fields.get("outcome") not in OUTCOMES:
        raise StateError(f"finish requires outcome in {OUTCOMES}")
    c = (clock or system_clock)()
    e = {"seq": len(events) + 1, "type": kind, "utc": _iso(c["utc_epoch"]), "utc_epoch": c["utc_epoch"],
         "monotonic_ns": c["monotonic_ns"], "boot_id": c["boot_id"]}
    if kind == "start":
        e["run_id"] = fields["run_id"]
        e["branch"] = fields.get("branch") or _git(run_dir, "rev-parse", "--abbrev-ref", "HEAD")
        e["base_revision"] = fields.get("base_revision")
        e["harness_revision"] = fields.get("harness_revision") or _git(run_dir, "rev-parse", "HEAD")
        e["environment"] = {"python": platform.python_version(), "os": platform.system(),
                            "os_release": platform.release(), "machine": platform.machine(),
                            "cpu_count": os.cpu_count()}
        e["inputs"] = _inputs(run_dir)
    for k in ("phase", "note", "outcome", "message", "exit_code", "label", "command", "stdout_path",
              "stderr_path", "duration_seconds"):
        if fields.get(k) is not None:
            e[k] = fields[k]
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / EVENTS, "a") as fh:
        fh.write(json.dumps(e, sort_keys=True) + "\n")
    return e


def run_validation(run_dir, label, command, clock=None):
    """Run a validation command, keeping every attempt's raw output (never overwritten)."""
    run_dir = Path(run_dir)
    state = _state(read_events(run_dir))
    if state not in ALLOWED["validation"]:
        raise StateError(f"cannot record 'validation' while run is '{state}'")
    vdir = run_dir / "validation"
    vdir.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in label) or "check"
    n = 1
    while list(vdir.glob(f"attempt-{n:03d}-*")):
        n += 1
    out_p, err_p = vdir / f"attempt-{n:03d}-{safe}.stdout.log", vdir / f"attempt-{n:03d}-{safe}.stderr.log"
    t0 = time.monotonic()
    try:
        r = subprocess.run(command, capture_output=True)
        code, so, se = r.returncode, r.stdout, r.stderr
    except OSError as exc:
        code, so, se = 127, b"", str(exc).encode()
    out_p.write_bytes(so)
    err_p.write_bytes(se)
    return record(run_dir, "validation", clock=clock, label=label, command=list(map(str, command)),
                  exit_code=code, stdout_path=out_p.relative_to(run_dir).as_posix(),
                  stderr_path=err_p.relative_to(run_dir).as_posix(),
                  duration_seconds=round(time.monotonic() - t0, 3))


def _interval(a, b, notes, label):
    wall = b["utc_epoch"] - a["utc_epoch"]
    if a["boot_id"] is None or b["boot_id"] is None:
        return None, wall, "unsupported"
    if a["boot_id"] != b["boot_id"]:
        notes.append(f"{label} (events {a['seq']}->{b['seq']}) spans a reboot; monotonic value not used")
        return None, wall, "discontinuous"
    mono = (b["monotonic_ns"] - a["monotonic_ns"]) / 1e9
    if abs(mono - wall) > max(DIVERGENCE_ABS_S, DIVERGENCE_REL * max(abs(wall), abs(mono))):
        notes.append(f"{label} (events {a['seq']}->{b['seq']}): monotonic {mono:.1f}s vs wall-clock {wall:.1f}s "
                     "diverge (suspend/clock change?); both reported")
        return mono, wall, "divergent"
    return mono, wall, "continuous"


def compute_metrics(run_dir):
    events = read_events(run_dir)
    if not events or events[0]["type"] != "start":
        raise StateError("no start event")
    start = events[0]
    notes = []
    kinds = set()
    totals = {"running": [0.0, 0.0, True], "paused": [0.0, 0.0, True]}  # mono, wall, mono_valid
    seg_state, seg_start = "running", start
    active_mono_so_far, active_wall_so_far, active_valid = 0.0, 0.0, True
    checkpoints, errors, validations = [], [], []
    for e in events[1:]:
        if e["type"] in ("pause", "resume", "finish", "checkpoint"):
            mono, wall, k = _interval(seg_start, e, notes, f"{seg_state} interval")
            kinds.add(k)
            if e["type"] == "checkpoint":
                cm = active_mono_so_far + mono if (active_valid and mono is not None) else None
                checkpoints.append({"phase": e["phase"], "utc": e["utc"], "note": e.get("note"),
                                    "active_elapsed_seconds": cm,
                                    "active_elapsed_seconds_wallclock": active_wall_so_far + wall})
                continue
            t = totals[seg_state]
            t[1] += wall
            if mono is None:
                t[2] = False
            else:
                t[0] += mono
            if seg_state == "running":
                active_wall_so_far += wall
                if mono is None:
                    active_valid = False
                else:
                    active_mono_so_far += mono
            seg_state = "paused" if e["type"] == "pause" else "running"
            seg_start = e
        elif e["type"] == "error":
            errors.append({"utc": e["utc"], "message": e.get("message"), "exit_code": e.get("exit_code")})
        elif e["type"] == "validation":
            validations.append({k: e.get(k) for k in ("utc", "label", "command", "exit_code", "stdout_path",
                                                      "stderr_path", "duration_seconds")})
    finish = events[-1] if events[-1]["type"] == "finish" else None
    if "unsupported" in kinds:
        continuity = "unsupported"
    elif "discontinuous" in kinds:
        continuity = "discontinuous"
    elif "divergent" in kinds:
        continuity = "divergent"
    else:
        continuity = "continuous"
    if continuity == "unsupported":
        notes.append("boot id unavailable: monotonic clock continuity cannot be established; wall-clock only")
    run, pause = totals["running"], totals["paused"]
    return {
        "run_id": start["run_id"],
        "branch": start.get("branch"),
        "base_revision": start.get("base_revision"),
        "harness_revision": start.get("harness_revision"),
        "environment": start.get("environment"),
        "inputs": start.get("inputs"),
        "started_utc": start["utc"],
        "finished_utc": finish["utc"] if finish else None,
        "outcome": finish.get("outcome") if finish else None,
        "finished": finish is not None,
        "clock_continuity": continuity,
        "clock_notes": notes,
        "active_seconds": run[0] if run[2] and continuity != "unsupported" else None,
        "active_seconds_wallclock": run[1],
        "paused_seconds": pause[0] if pause[2] and continuity != "unsupported" else None,
        "paused_seconds_wallclock": pause[1],
        "wall_seconds": (finish["utc_epoch"] - start["utc_epoch"]) if finish else None,
        "pauses": sum(1 for e in events if e["type"] == "pause"),
        "checkpoints": checkpoints,
        "errors": errors,
        "validation_attempts": validations,
        "event_count": len(events),
        "unavailable": {"tokens": None, "cost": None, "peak_memory": None, "model": None},
        "notes": "Timing starts at the migration session's start event, not at worktree preparation.",
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    command = []
    if "--" in argv:
        i = argv.index("--")
        argv, command = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["start", "checkpoint", "pause", "resume", "error", "validate", "finish",
                                       "status"])
    ap.add_argument("--run-dir", required=True)
    for opt in ("--run-id", "--branch", "--base-revision", "--harness-revision", "--phase", "--note",
                "--message", "--label", "--outcome"):
        ap.add_argument(opt)
    ap.add_argument("--exit-code", type=int)
    a = ap.parse_args(argv)
    run_dir = Path(a.run_dir)
    try:
        if a.action == "status":
            events = read_events(run_dir)
            print(json.dumps({"state": _state(events), "events": len(events),
                              "metrics": compute_metrics(run_dir) if events else None}, indent=2))
            return 0
        if a.action == "validate":
            if not command or not a.label:
                ap.error("validate requires --label and a command after --")
            e = run_validation(run_dir, a.label, command)
            print(f"validation attempt recorded: exit={e['exit_code']} stdout={e['stdout_path']}")
            return 0
        if a.action == "finish" and (run_dir / METRICS).exists():
            raise StateError(f"{run_dir / METRICS} already exists; refusing to overwrite")
        e = record(run_dir, a.action, run_id=a.run_id, branch=a.branch, base_revision=a.base_revision,
                   harness_revision=a.harness_revision, phase=a.phase, note=a.note, message=a.message,
                   exit_code=a.exit_code, outcome=a.outcome)
        if a.action == "finish":
            m = compute_metrics(run_dir)
            (run_dir / METRICS).write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
            print(json.dumps({k: m[k] for k in ("run_id", "outcome", "clock_continuity", "active_seconds",
                                                 "paused_seconds", "wall_seconds")}, indent=2))
        else:
            print(f"recorded {e['type']} #{e['seq']} at {e['utc']}")
        return 0
    except StateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
