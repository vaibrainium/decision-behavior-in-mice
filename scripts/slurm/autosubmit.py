"""Queue-aware submission of the 2026-11-06 fit batches (plans/2026-11-06-input-mapping-x-accumulator.md,
plans/2026-11-06-nominal-coherence-joint-fits.md). Standard library only, so it runs on the Hyak login node.

Each pass:
  1. a tracked task whose output file exists is done;
  2. a submitted task that left the queue without its output failed: it is put back with twice its time limit after a
     TIMEOUT (at most MAX_HOURS), with the same limit after any other failure, at most MAX_ATTEMPTS submissions;
  3. free slots = LIMIT - (your queued array tasks, all jobs); that many pending tasks are submitted, in priority order,
     as arrays grouped by batch and time limit (--array=<index list>, --time from the task table).
Tasks and time limits: scripts/slurm/tasks_2026-11-06.csv (make_task_table.py). State: slurm-logs/autosubmit_state.json.
The jobs submitted before this script (QOS-limited runs of submit_mapping_accumulator.sh and
submit_remaining_2026-11-06.sh) are imported on the first run, so they are tracked and retried too.

Run from the repo root on Hyak (bash):
    python3 scripts/slurm/autosubmit.py --dry_run           # what one pass would do; changes nothing
    python3 scripts/slurm/autosubmit.py                     # one pass
    tmux new -s autosubmit 'python3 scripts/slurm/autosubmit.py --watch 10'   # every 10 min until all are done
    python3 scripts/slurm/autosubmit.py --shrink_pending    # also lower the 16 h limit of imported tasks still pending
Settings (environment): LIMIT (500), MAX_HOURS (48), MAX_ATTEMPTS (3), DDM_DIR (Hyak processed/ddm).
Use only this script for these batches from now on (not submit_remaining_2026-11-06.sh).
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

TASKS = Path("scripts/slurm/tasks_2026-11-06.csv")
STATE = Path("slurm-logs/autosubmit_state.json")
OLD_DONE = Path("slurm-logs/submitted_2026-11-06.txt")  # written by submit_remaining_2026-11-06.sh
SLURM_SCRIPT = "scripts/slurm/fit_mouse_ddm.slurm"
LIMIT = int(os.environ.get("LIMIT", 500))
MAX_HOURS = float(os.environ.get("MAX_HOURS", 48))
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", 3))
DDM_DIR = Path(os.environ.get("DDM_DIR", "/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm"))
BUCKETS = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48]  # time limits are rounded up to these, so a batch becomes a few arrays
GRACE_SECONDS = 300  # a just-submitted task may not be visible in squeue yet
# submitted 2026-11-06 before this script (all with --time=16:00:00): batch -> [(job id, first index, last index)]
IMPORTED = {
    "M_power_integrators": [("43010287", 0, 239)], "M_power_leak20-200": [("43010288", 0, 59)], "M_power_es": [("43010289", 0, 59)],
    "M_norm_leak20-200": [("43010290", 0, 59)], "M_norm_es": [("43010291", 0, 59)],
    "P1_power": [("43010292", 50, 59), ("43013411", 0, 49)],
}
# batch names used by submit_remaining_2026-11-06.sh -> (batch, first, last)
OLD_NAMES = {"P1_power_ccv": ("P1_power", 0, 49), "N4_nominal_power": ("N4_nominal_power", 0, 59),
             "M_norm_integrators": ("M_norm_integrators", 0, 239), "N1_nominal_integrators": ("N1_nominal_integrators", 0, 299),
             "N2_nominal_leak20-200": ("N2_nominal_leak20-200", 0, 59), "N3_nominal_es": ("N3_nominal_es", 0, 59)}


def run(cmd: list[str], env: dict | None = None) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, env=env).stdout


def load_tasks() -> dict:
    with open(TASKS) as f:
        return {f"{r['batch']}:{r['index']}": r for r in csv.DictReader(f)}


def old_done_entries() -> list[tuple[str, int, int, str]]:
    """(batch, first, last, job id) from submit_remaining_2026-11-06.sh's record, including its 60-task chunks."""
    out = []
    if OLD_DONE.exists():
        for line in OLD_DONE.read_text().splitlines():
            name, job = line.split()[:2]
            if name in OLD_NAMES:
                out.append((*OLD_NAMES[name], job))
            else:  # chunk: <batch>_<first>-<last>
                base, rng = name.rsplit("_", 1)
                lo, hi = map(int, rng.split("-"))
                out.append((OLD_NAMES[base][0] if base in OLD_NAMES else base, lo, hi, job))
    return out


def initial_state(tasks: dict) -> dict:
    state = {k: {"status": "pending", "job": None, "time_hours": float(t["time_hours"]), "attempts": 0, "submitted_at": 0, "history": []}
             for k, t in tasks.items()}
    entries = [(b, lo, hi, job) for b, spans in IMPORTED.items() for job, lo, hi in spans] + old_done_entries()
    for batch, lo, hi, job in entries:
        for i in range(lo, hi + 1):
            s = state[f"{batch}:{i}"]
            s.update(status="submitted", job=job, time_hours=16.0, attempts=1, submitted_at=0)
            s["history"].append(f"imported job {job}")
    return state


def save(state: dict) -> None:
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=0))
    tmp.replace(STATE)


def queue() -> dict[str, str]:
    """Your queued and running array tasks: '<job>_<index>' -> state (PENDING, RUNNING, ...)."""
    lines = run(["squeue", "-u", os.environ["USER"], "-h", "-r", "-o", "%i %T"]).split("\n")
    return dict(line.split()[:2] for line in lines if line.strip())


def sacct_states(ids: list[str]) -> dict[str, str]:
    states = {}
    for i in range(0, len(ids), 200):
        out = run(["sacct", "-n", "-X", "-P", "-o", "JobID,State", "-j", ",".join(ids[i:i + 200])])
        for line in out.splitlines():
            jid, st = line.split("|")[:2]
            states[jid] = st.split()[0]
    return states


def bucket(hours: float) -> float:
    return next((b for b in BUCKETS if b >= hours), BUCKETS[-1])


def ranges(idx: list[int]) -> str:
    idx, parts, start = sorted(idx), [], None
    for a, b in zip(idx, idx[1:] + [None]):
        start = a if start is None else start
        if b != a + 1:
            parts.append(f"{start}-{a}" if a > start else f"{a}")
            start = None
    return ",".join(parts)


def one_pass(tasks: dict, state: dict, dry_run: bool, shrink_pending: bool) -> bool:
    q = queue()
    now = time.time()
    # 1-2: done / failed
    gone = []
    for k, s in state.items():
        if s["status"] in ("done", "gave_up"):
            continue
        if (DDM_DIR / tasks[k]["out"]).exists():
            s["status"] = "done"
        elif s["status"] == "submitted" and f"{s['job']}_{tasks[k]['index']}" not in q and now - s["submitted_at"] > GRACE_SECONDS:
            gone.append(k)
    if gone:
        st = sacct_states(sorted({f"{state[k]['job']}_{tasks[k]['index']}" for k in gone}))
        for k in gone:
            s = state[k]
            reason = st.get(f"{s['job']}_{tasks[k]['index']}", "UNKNOWN")
            if reason == "COMPLETED" and not (DDM_DIR / tasks[k]["out"]).exists():
                reason = "COMPLETED_NO_OUTPUT"
            new_time = min(MAX_HOURS, s["time_hours"] * 2) if reason == "TIMEOUT" else s["time_hours"]
            s["history"].append(f"job {s['job']}: {reason} at {s['time_hours']} h")
            if s["attempts"] >= MAX_ATTEMPTS or (reason == "TIMEOUT" and s["time_hours"] >= MAX_HOURS):
                s["status"] = "gave_up"
            else:
                s.update(status="pending", job=None, time_hours=new_time)
    # optional: lower the limit of imported tasks still pending to the table estimate (helps backfill; can only decrease)
    if shrink_pending:
        for k, s in state.items():
            jid = f"{s['job']}_{tasks[k]['index']}" if s["status"] == "submitted" else None
            want = float(tasks[k]["time_hours"])
            if jid and q.get(jid) == "PENDING" and s["time_hours"] > want and s["attempts"] == 1:
                cmd = ["scontrol", "update", f"JobId={jid}", f"TimeLimit={int(want * 60)}"]
                if dry_run:
                    print("would run:", " ".join(cmd))
                else:
                    try:
                        run(cmd)
                        s["time_hours"] = want
                        s["history"].append(f"time limit lowered to {want} h")
                    except subprocess.CalledProcessError as e:
                        print(f"scontrol failed for {jid}: {e.stderr.strip()}")
    # 3: submit into free slots; tasks submitted within GRACE_SECONDS that squeue does not show yet still take a slot
    unseen = sum(1 for k, s in state.items() if s["status"] == "submitted" and now - s["submitted_at"] <= GRACE_SECONDS
                 and f"{s['job']}_{tasks[k]['index']}" not in q)
    free = LIMIT - len(q) - unseen
    pending = sorted((k for k, s in state.items() if s["status"] == "pending"),
                     key=lambda k: (int(tasks[k]["priority"]), tasks[k]["batch"], int(tasks[k]["index"])))
    take = pending[:max(0, free)]
    groups = defaultdict(list)
    for k in take:
        t = tasks[k]
        state[k]["time_hours"] = min(MAX_HOURS, bucket(state[k]["time_hours"]))
        groups[(t["batch"], state[k]["time_hours"], t["args"])].append(int(t["index"]))
    refused = False
    for (batch, hours, args), idx in groups.items():
        cmd = ["sbatch", "--parsable", f"--array={ranges(idx)}", f"--time={int(round(hours * 60))}", SLURM_SCRIPT]
        if dry_run:
            print(f"would submit {batch}: {len(idx)} tasks, {hours} h: {' '.join(cmd)}  EXTRA_ARGS='{args}'")
            continue
        try:
            job = run(cmd, env={**os.environ, "EXTRA_ARGS": args, "JOB_OFFSET": "0"}).strip().split(";")[0]
        except subprocess.CalledProcessError as e:
            print(f"{batch}: sbatch refused ({e.stderr.strip()}); trying again next pass")
            refused = True
            break
        for i in idx:
            s = state[f"{batch}:{i}"]
            s.update(status="submitted", job=job, attempts=s["attempts"] + 1, submitted_at=time.time())
            s["history"].append(f"submitted job {job} at {hours} h")
        print(f"submitted {batch}: {len(idx)} tasks, {hours} h, job {job}")
    # summary
    counts = defaultdict(lambda: defaultdict(int))
    for k, s in state.items():
        counts[tasks[k]["batch"]][s["status"]] += 1
    print(f"{time.strftime('%Y-%m-%d %H:%M')}  queued {len(q)} (+{unseen} just submitted)/{LIMIT}, free {free}, submitted this pass {0 if dry_run else sum(len(v) for v in groups.values())}{' (refused)' if refused else ''}")
    for b in sorted(counts, key=lambda b: min(int(tasks[k]['priority']) for k in tasks if tasks[k]['batch'] == b)):
        print(f"  {b:24s} " + "  ".join(f"{st} {n}" for st, n in sorted(counts[b].items())))
    for k, s in state.items():
        if s["status"] == "gave_up":
            print(f"  GAVE UP {k}: {'; '.join(s['history'])}")
    return any(s["status"] in ("pending", "submitted") for s in state.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--watch", type=float, metavar="MINUTES", help="repeat every MINUTES until every task is done or given up")
    ap.add_argument("--dry_run", action="store_true", help="print what one pass would do; change nothing")
    ap.add_argument("--shrink_pending", action="store_true", help="lower the 16 h limit of imported tasks still pending to the table estimate")
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)  # readable live in tmux / a log file
    if not TASKS.exists():
        sys.exit(f"{TASKS} not found; run from the repo root after git pull")
    tasks = load_tasks()
    STATE.parent.mkdir(exist_ok=True)
    state = json.loads(STATE.read_text()) if STATE.exists() else initial_state(tasks)
    while True:
        try:
            busy = one_pass(tasks, state, args.dry_run, args.shrink_pending)
        except (subprocess.CalledProcessError, OSError) as e:  # e.g. slurmctld busy: keep the state, try next pass
            if not args.watch:
                raise
            print(f"{time.strftime('%Y-%m-%d %H:%M')} pass failed ({e}); retrying in {args.watch} min")
            busy = True
        if not args.dry_run:
            save(state)
        if not args.watch or args.dry_run or not busy:
            break
        time.sleep(args.watch * 60)
    if not busy:
        print("all tasks done or given up")


if __name__ == "__main__":
    main()
