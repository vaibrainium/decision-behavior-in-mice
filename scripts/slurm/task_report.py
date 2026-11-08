"""Read-only report on your queued and running fit tasks: restarts (preempted and requeued on ckpt-all), hours lost to
those restarts, time in the current attempt, and the expected runtime from the task table; lists candidates to move to
the lab partition (scripts/slurm/autosubmit.py --to_lab). Standard library only, Python 3.6 (Hyak login node).

Sources: squeue (state, partition, run time, limit), scontrol show job -o (Restarts per array task), sacct --duplicates
(earlier attempts of requeued tasks and their run time), slurm-logs/autosubmit_state.json + scripts/slurm/tasks_2026-11-06.csv
(which fit a task is, expected hours). Changes nothing.

Run from the repo root on Hyak:
    python3 scripts/slurm/task_report.py                         # summary + restarted tasks
    python3 scripts/slurm/task_report.py --min_est 6 --write slurm-logs/to_lab.txt
        # also write candidates: restarted at least once, or expected >= 6 h; PENDING only unless --running
    python3 scripts/slurm/autosubmit.py --to_lab slurm-logs/to_lab.txt --dry_run    # then without --dry_run
"""

import argparse
import csv
import json
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

TASKS = Path("scripts/slurm/tasks_2026-11-06.csv")
STATE = Path("slurm-logs/autosubmit_state.json")
LOST_STATES = ("PREEMPTED", "REQUEUED", "NODE_FAIL", "BOOT_FAIL")


def run(cmd):
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).stdout


def hours(t):
    """Slurm duration [D-]HH:MM:SS, MM:SS or UNLIMITED -> hours."""
    if not t or t in ("UNLIMITED", "INVALID", "N/A"):
        return float("nan")
    days, _, rest = t.rpartition("-")
    parts = [float(x) for x in rest.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return (float(days) if days else 0.0) * 24 + parts[0] + parts[1] / 60 + parts[2] / 3600


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min_est", type=float, default=6.0, help="candidate if expected runtime >= this many hours (default 6)")
    ap.add_argument("--min_restarts", type=int, default=1, help="candidate if restarted at least this often (default 1)")
    ap.add_argument("--running", action="store_true", help="also list RUNNING tasks as candidates (moving them loses their progress)")
    ap.add_argument("--write", type=Path, help="write candidate task keys (batch:index) to this file for autosubmit --to_lab")
    args = ap.parse_args()

    # queue
    q = {}
    for line in run(["squeue", "-u", os.environ["USER"], "-h", "-r", "-o", "%i|%T|%P|%M|%l"]).splitlines():
        jid, st, part, elapsed, limit = line.split("|")
        q[jid] = {"state": st, "partition": part, "elapsed_h": hours(elapsed), "limit_h": hours(limit), "restarts": 0, "lost_h": 0.0, "lost_n": 0}
    arrays = sorted({j.split("_")[0] for j in q})
    # restarts per task
    for a in arrays:
        try:
            out = run(["scontrol", "show", "job", "-o", a])
        except subprocess.CalledProcessError:
            continue
        for line in out.splitlines():
            f = dict(re.findall(r"(\w+)=(\S*)", line))
            jid = f"{f.get('ArrayJobId', a)}_{f.get('ArrayTaskId', '')}"
            if jid in q:
                q[jid]["restarts"] = int(f.get("Restarts", 0) or 0)
    # earlier attempts and their run time
    for i in range(0, len(arrays), 50):
        try:
            out = run(["sacct", "-n", "-X", "-P", "--duplicates", "-o", "JobID,State,Elapsed", "-j", ",".join(arrays[i:i + 50])])
        except subprocess.CalledProcessError:
            continue
        for line in out.splitlines():
            jid, st, elapsed = line.split("|")[:3]
            if jid in q and st.split()[0] in LOST_STATES:
                q[jid]["lost_h"] += hours(elapsed)
                q[jid]["lost_n"] += 1

    # which fit each task is
    tasks = {}
    if TASKS.exists():
        with open(TASKS) as f:
            tasks = {f"{r['batch']}:{r['index']}": r for r in csv.DictReader(f)}
    by_jid = {}
    if STATE.exists():
        for k, s in json.loads(STATE.read_text()).items():
            if s.get("status") == "submitted" and s.get("job"):
                by_jid[f"{s['job']}_{tasks[k]['index'] if k in tasks else k.split(':')[1]}"] = k
    rows = []
    for jid, r in q.items():
        k = by_jid.get(jid)
        t = tasks.get(k, {})
        rows.append(dict(r, jid=jid, key=k or "", batch=t.get("batch", "(untracked)"),
                         fit=f"{t['mouse']} {t['variant']} {t['split']}" if t else "", est_h=float(t["est_hours"]) if t else float("nan")))

    # summary by batch
    summ = defaultdict(lambda: defaultdict(float))
    for r in rows:
        b = summ[r["batch"]]
        b[r["state"].lower()] += 1
        b["restarted"] += r["restarts"] >= 1
        b["restarts"] += r["restarts"]
        b["lost_h"] += r["lost_h"]
    print(f"{len(rows)} queued/running tasks; restarted at least once: {sum(r['restarts'] >= 1 for r in rows)}; "
          f"hours lost to earlier attempts: {sum(r['lost_h'] for r in rows):.1f}")
    print(f"\n{'batch':26s} {'running':>8s} {'pending':>8s} {'restarted':>10s} {'restarts':>9s} {'lost h':>8s}")
    for b in sorted(summ):
        s = summ[b]
        print(f"{b:26s} {int(s['running']):8d} {int(s['pending']):8d} {int(s['restarted']):10d} {int(s['restarts']):9d} {s['lost_h']:8.1f}")

    restarted = sorted((r for r in rows if r["restarts"] >= 1), key=lambda r: (-r["est_h"] if r["est_h"] == r["est_h"] else 0, -r["restarts"]))
    if restarted:
        print(f"\nrestarted tasks (longest expected first):\n{'job':16s} {'state':9s} {'partition':10s} {'restarts':>8s} {'lost h':>7s} "
              f"{'now h':>6s} {'limit h':>7s} {'est h':>6s}  task / fit")
        for r in restarted:
            print(f"{r['jid']:16s} {r['state']:9s} {r['partition']:10s} {r['restarts']:8d} {r['lost_h']:7.1f} {r['elapsed_h']:6.1f} "
                  f"{r['limit_h']:7.1f} {r['est_h']:6.1f}  {r['key']} {r['fit']}")

    cand = [r for r in rows if r["key"] and (r["restarts"] >= args.min_restarts or r["est_h"] >= args.min_est)
            and (r["state"] == "PENDING" or (args.running and r["state"] == "RUNNING"))]
    running_long = [r for r in rows if r["key"] and r["state"] == "RUNNING" and r["est_h"] >= args.min_est]
    print(f"\ncandidates for the lab partition (restarts >= {args.min_restarts} or expected >= {args.min_est} h; "
          f"{'PENDING and RUNNING' if args.running else 'PENDING only'}): {len(cand)}")
    print(f"  by batch: {dict(sorted(defaultdict(int, {b: sum(r['batch'] == b for r in cand) for b in {r['batch'] for r in cand}}).items()))}")
    if running_long and not args.running:
        print(f"  RUNNING with expected >= {args.min_est} h (not listed; --running to include, progress would be lost): {len(running_long)}")
    if args.write:
        args.write.write_text("".join(f"{r['key']}  # {r['jid']} {r['state']} restarts {r['restarts']} est {r['est_h']:.1f} h {r['fit']}\n" for r in cand))
        print(f"  written to {args.write} (review it, then: python3 scripts/slurm/autosubmit.py --to_lab {args.write} --dry_run)")


if __name__ == "__main__":
    main()
