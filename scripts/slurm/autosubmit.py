"""Queue-aware submission of the 2026-11-06 fit batches (plans/2026-11-06-input-mapping-x-accumulator.md,
plans/2026-11-06-nominal-coherence-joint-fits.md). Standard library only and Python 3.6 compatible (the Hyak login node python3).

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
    python3 scripts/slurm/autosubmit.py --to_lab slurm-logs/to_lab.txt [--include_running]   # see task_report.py
    python3 scripts/slurm/autosubmit.py --now FILE      # submit these tasks now on the shared partition (cancels PENDING lab copies)
    python3 scripts/slurm/autosubmit.py --cap_pending 6 # lower PENDING tasks' limit to 6 h (e.g. before maintenance); state follows
    python3 scripts/slurm/autosubmit.py --tasks scripts/slurm/tasks_2026-11-10_pulse.csv --state slurm-logs/autosubmit_state_pulse.json --watch 10
        # another task table: its own state and lock file, so two loops can run side by side
Failover (--failover_to_lab, e.g. with --watch): a task requeued after preemption on the shared partition (PENDING,
reason BeginTime), or one that has restarted there and has been running less than FAILOVER_MAX_RUN_MIN (60) minutes
(requeuehold first; those minutes are lost), is moved in place with scontrol update (Partition LAB_PARTITION, Account LAB_UPDATE_ACCOUNT, QOS
LAB_QOS; same job ID); a task that failed there (timeout, node failure, ...) is resubmitted on the lab partition (doubled
limit after a timeout). Running tasks are left alone. Tasks moved by hand are recognised from squeue.
Moving to the lab partition (--to_lab FILE, one batch:index per line): each listed task still queued is cancelled and
put back as pending with partition LAB_PARTITION / account LAB_ACCOUNT; later passes submit it there, at most LAB_LIMIT
of your tasks in that partition at a time. RUNNING tasks are skipped unless --include_running (their progress is lost:
fits do not checkpoint). Safe while a --watch loop runs: every pass re-reads the state under a lock.
Settings (environment): LIMIT (500), MAX_HOURS (48), MAX_ATTEMPTS (3), PROCESSED_DIR (Hyak processed; task outputs are
relative to it, e.g. ddm/fits_...), LAB_PARTITION (gpu-a100), LAB_ACCOUNT (walkerlab), LAB_LIMIT (8).
Use only this script for these batches from now on (not submit_remaining_2026-11-06.sh).
"""

import argparse
import contextlib
import csv
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

TASKS = Path("scripts/slurm/tasks_2026-11-06.csv")
STATE = Path("slurm-logs/autosubmit_state.json")
LOCK = Path("slurm-logs/autosubmit.lock")
OLD_DONE = Path("slurm-logs/submitted_2026-11-06.txt")  # written by submit_remaining_2026-11-06.sh
SLURM_SCRIPT = "scripts/slurm/fit_mouse_ddm.slurm"
LIMIT = int(os.environ.get("LIMIT", 500))
MAX_HOURS = float(os.environ.get("MAX_HOURS", 48))
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", 3))
LAB_PARTITION = os.environ.get("LAB_PARTITION", "gpu-a100")
LAB_ACCOUNT = os.environ.get("LAB_ACCOUNT", "walkerlab")
LAB_LIMIT = int(os.environ.get("LAB_LIMIT", 8))
LAB_UPDATE_ACCOUNT = os.environ.get("LAB_UPDATE_ACCOUNT", "gpu-a100-walkerlab")  # scontrol update needs the full association
LAB_QOS = os.environ.get("LAB_QOS", "normal")
FAILOVER_MAX_RUN_MIN = float(os.environ.get("FAILOVER_MAX_RUN_MIN", 60))  # restarted tasks running shorter than this move too
PROCESSED_DIR = Path(os.environ.get("PROCESSED_DIR", "/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed"))
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


def run(cmd, env=None):
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env).stdout


def load_tasks():
    with open(TASKS) as f:
        return {f"{r['batch']}:{r['index']}": r for r in csv.DictReader(f)}


def old_done_entries():
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


def initial_state(tasks):
    state = {k: {"status": "pending", "job": None, "time_hours": float(t["time_hours"]), "attempts": 0, "submitted_at": 0, "history": []}
             for k, t in tasks.items()}
    entries = [(b, lo, hi, job) for b, spans in IMPORTED.items() for job, lo, hi in spans] + old_done_entries()
    for batch, lo, hi, job in entries:
        for i in range(lo, hi + 1):
            if f"{batch}:{i}" not in state:  # another task table (--tasks): nothing to import
                continue
            s = state[f"{batch}:{i}"]
            s.update(status="submitted", job=job, time_hours=16.0, attempts=1, submitted_at=0)
            s["history"].append(f"imported job {job}")
    return state


def save(state):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=0))
    tmp.replace(STATE)


def minutes(t):
    """squeue run time [D-]HH:MM:SS or MM:SS -> minutes."""
    days, _, rest = t.rpartition("-")
    parts = [float(x) for x in rest.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return (float(days) if days else 0.0) * 1440 + parts[0] * 60 + parts[1] + parts[2] / 60


def queue():
    """Your queued and running array tasks: '<job>_<index>' -> (state, partition, reason, run minutes)."""
    lines = run(["squeue", "-u", os.environ["USER"], "-h", "-r", "-o", "%i %T %P %M %r"]).split("\n")
    return {f[0]: (f[1], f[2], f[4] if len(f) > 4 else "", minutes(f[3])) for f in (line.split() for line in lines if line.strip())}


def restarts(array_ids):
    """'<job>_<index>' -> Restarts, from scontrol (one call per array job)."""
    out = {}
    for a in array_ids:
        try:
            text = run(["scontrol", "show", "job", "-o", a])
        except subprocess.CalledProcessError:
            continue
        for line in text.splitlines():
            m_job, m_task, m_r = (re.search(p, line) for p in (r"ArrayJobId=(\d+)", r"ArrayTaskId=(\d+)\b", r"Restarts=(\d+)"))
            if m_job and m_task and m_r:
                out[f"{m_job.group(1)}_{m_task.group(1)}"] = int(m_r.group(1))
    return out


@contextlib.contextmanager
def locked():
    """Exclusive lock around a read-modify-write of the state file (watch loop vs --to_lab)."""
    LOCK.parent.mkdir(exist_ok=True)
    with open(LOCK, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def load_state(tasks):
    return json.loads(STATE.read_text()) if STATE.exists() else initial_state(tasks)


def to_lab(tasks, state, keys, include_running, dry_run):
    q = queue()
    for k in keys:
        if k not in state:
            print(f"{k}: unknown task, skipped")
            continue
        s = state[k]
        jid = f"{s['job']}_{tasks[k]['index']}" if s["status"] == "submitted" else None
        qstate = q.get(jid, (None, None))[0] if jid else None
        if s["status"] in ("done", "gave_up") or s.get("partition") == LAB_PARTITION:
            print(f"{k}: {s['status']}{' (already lab)' if s.get('partition') == LAB_PARTITION else ''}, skipped")
            continue
        if qstate == "RUNNING" and not include_running:
            print(f"{k}: RUNNING as {jid}, skipped (--include_running to cancel it and lose its progress)")
            continue
        print(f"{k}: {'cancel ' + jid + ' (' + str(qstate) + ') and ' if qstate else ''}move to {LAB_PARTITION}")
        if dry_run:
            continue
        if qstate:
            run(["scancel", jid])
        s["history"].append(f"moved to {LAB_PARTITION}" + (f" (cancelled {jid}, {qstate})" if qstate else ""))
        timed_out = any("TIMEOUT" in h for h in s["history"])  # keep a doubled limit; otherwise back to the table's
        s.update(status="pending", job=None, partition=LAB_PARTITION, account=LAB_ACCOUNT,
                 time_hours=s["time_hours"] if timed_out else float(tasks[k]["time_hours"]),
                 attempts=max(0, s["attempts"] - (1 if qstate else 0)))  # our cancel is not a failed attempt


def submit_now(tasks, state, keys, dry_run):
    """Submit the listed tasks now on the default (shared) partition, ahead of the table order: a still-PENDING
    submission is cancelled first (nothing has run, and fits checkpoint anyway); RUNNING / done tasks are left alone.
    The lab flag is cleared, so later retries go to the shared partition too."""
    q = queue()
    groups = defaultdict(list)
    for k in keys:
        if k not in state:
            print(f"{k}: unknown task, skipped")
            continue
        s = state[k]
        jid = f"{s['job']}_{tasks[k]['index']}" if s["status"] == "submitted" else None
        qstate = q.get(jid, (None,))[0] if jid else None
        if s["status"] in ("done", "gave_up") or (s["status"] == "submitted" and qstate != "PENDING"):
            print(f"{k}: {s['status']}{' ' + str(qstate) if qstate else ''}, skipped")
            continue
        print(f"{k}: {'cancel ' + jid + ' (PENDING) and ' if qstate else ''}submit now on the shared partition")
        if dry_run:
            continue
        if qstate:
            run(["scancel", jid])
            s["history"].append(f"cancelled {jid} (PENDING) to submit now on the shared partition")
            s["attempts"] = max(0, s["attempts"] - 1)
        s.pop("partition", None)
        s.pop("account", None)
        s.update(status="pending", job=None, time_hours=min(MAX_HOURS, bucket(float(tasks[k]["time_hours"]))))
        groups[(tasks[k]["batch"], s["time_hours"], tasks[k]["args"])].append(k)
    for (batch, hours, args), ks in groups.items():
        idx = sorted(int(tasks[k]["index"]) for k in ks)
        cmd = ["sbatch", "--parsable", f"--array={ranges(idx)}", f"--time={int(round(hours * 60))}", SLURM_SCRIPT]
        try:
            job = run(cmd, env={**os.environ, "EXTRA_ARGS": args, "JOB_OFFSET": "0"}).strip().split(";")[0]
        except subprocess.CalledProcessError as e:
            print(f"{batch}: sbatch refused ({e.stderr.strip()}); the tasks stay pending for the watch loop")
            continue
        for k in ks:
            s = state[k]
            s.update(status="submitted", job=job, attempts=s["attempts"] + 1, submitted_at=time.time())
            s["history"].append(f"submitted job {job} at {hours} h (--now)")
        print(f"submitted {batch}: {len(idx)} tasks, {hours} h, job {job}")


def cap_pending(tasks, state, hours, dry_run):
    """Lower the time limit of this table's PENDING tasks to `hours` (e.g. so they fit before a maintenance
    reservation; fits checkpoint, so a task cut short times out, is resubmitted with twice the limit and resumes).
    Slurm and the state are changed together, so the doubling starts from the new limit. The cut is not a failed
    attempt (attempts - 1). RUNNING tasks are left alone; limits can only be lowered by users."""
    q = queue()
    n = 0
    for k, s in state.items():
        jid = "{}_{}".format(s["job"], tasks[k]["index"]) if s["status"] == "submitted" else None
        if not jid or q.get(jid, (None,))[0] != "PENDING" or s["time_hours"] <= hours:
            continue
        cmd = ["scontrol", "update", "JobId=" + jid, "TimeLimit={}".format(int(round(hours * 60)))]
        if dry_run:
            print("would run:", " ".join(cmd), "  ({}, was {} h)".format(k, s["time_hours"]))
            n += 1
            continue
        try:
            run(cmd)
        except subprocess.CalledProcessError as e:
            print("scontrol failed for {} ({}): {}".format(jid, k, e.stderr.strip()))
            continue
        s["history"].append("time limit lowered {} -> {} h while pending (--cap_pending)".format(s["time_hours"], hours))
        s.update(time_hours=float(hours), attempts=max(0, s["attempts"] - 1))
        n += 1
    print("{} pending tasks {}capped at {} h".format(n, "would be " if dry_run else "", hours))


def sacct_states(ids):
    states = {}
    for i in range(0, len(ids), 200):
        out = run(["sacct", "-n", "-X", "-P", "-o", "JobID,State", "-j", ",".join(ids[i:i + 200])])
        for line in out.splitlines():
            jid, st = line.split("|")[:2]
            states[jid] = st.split()[0]
    return states


def bucket(hours):
    return next((b for b in BUCKETS if b >= hours), BUCKETS[-1])


def ranges(idx):
    idx, parts, start = sorted(idx), [], None
    for a, b in zip(idx, idx[1:] + [None]):
        start = a if start is None else start
        if b != a + 1:
            parts.append(f"{start}-{a}" if a > start else f"{a}")
            start = None
    return ",".join(parts)


def one_pass(tasks, state, dry_run, shrink_pending, failover=False):
    q = queue()
    now = time.time()
    # record the partition tasks are actually on (e.g. moved by hand with scontrol update)
    for k, s in state.items():
        if s["status"] == "submitted":
            part = q.get(f"{s['job']}_{tasks[k]['index']}", (None, None))[1]
            if part == LAB_PARTITION and s.get("partition") != LAB_PARTITION:
                s.update(partition=LAB_PARTITION, account=LAB_ACCOUNT)
                s["history"].append(f"found on {LAB_PARTITION}")
    # failover: a task requeued after preemption on the shared partition (pending, reason BeginTime) moves in place to
    # the lab partition; it keeps its job ID, and nothing more is lost (the preemption already discarded its progress)
    # a requeued task usually restarts on the shared partition within minutes, so also move tasks that have restarted
    # and have been running less than FAILOVER_MAX_RUN_MIN (requeuehold -> update -> release; only those minutes lost)
    if failover:
        on_shared = {}
        for k, s in state.items():
            jid = f"{s['job']}_{tasks[k]['index']}" if s["status"] == "submitted" else None
            if jid and jid in q and q[jid][1] != LAB_PARTITION:
                on_shared[jid] = k
        rs = restarts(sorted({j.split("_")[0] for j, k in on_shared.items() if q[j][0] == "RUNNING"}))
        for jid, k in on_shared.items():
            s = state[k]
            st, part, reason, run_min = q[jid]
            requeued = st == "PENDING" and reason == "BeginTime"
            restarted = st == "RUNNING" and rs.get(jid, 0) >= 1 and run_min < FAILOVER_MAX_RUN_MIN
            if not (requeued or restarted):
                continue
            update = ["scontrol", "update", f"JobId={jid}", f"Partition={LAB_PARTITION}", f"Account={LAB_UPDATE_ACCOUNT}", f"QOS={LAB_QOS}"]
            cmds = [update] if requeued else [["scontrol", "requeuehold", jid], update, ["scontrol", "release", jid]]
            what = "requeued" if requeued else f"restarted ({rs.get(jid)}x), running {run_min:.0f} min"
            if dry_run:
                print(f"would move {k} ({jid}, {what}):", " ; ".join(" ".join(c) for c in cmds))
                continue
            try:
                for c in cmds:
                    run(c)
                s.update(partition=LAB_PARTITION, account=LAB_ACCOUNT)
                s["history"].append(f"{what} on {part}; moved to {LAB_PARTITION} in place")
                print(f"failover: {k} ({jid}) {what} on {part}, moved to {LAB_PARTITION}")
            except subprocess.CalledProcessError as e:
                print(f"failover: {' '.join(c)} failed for {jid}: {e.stderr.strip()}; if it is held, run: scontrol release {jid}")
    # 1-2: done / failed
    gone = []
    for k, s in state.items():
        if s["status"] in ("done", "gave_up"):
            continue
        if (PROCESSED_DIR / tasks[k]["out"]).exists():
            s["status"] = "done"
        elif s["status"] == "submitted" and f"{s['job']}_{tasks[k]['index']}" not in q and now - s["submitted_at"] > GRACE_SECONDS:
            gone.append(k)
    if gone:
        st = sacct_states(sorted({f"{state[k]['job']}_{tasks[k]['index']}" for k in gone}))
        for k in gone:
            s = state[k]
            reason = st.get(f"{s['job']}_{tasks[k]['index']}", "UNKNOWN")
            if reason == "COMPLETED" and not (PROCESSED_DIR / tasks[k]["out"]).exists():
                reason = "COMPLETED_NO_OUTPUT"
            new_time = min(MAX_HOURS, s["time_hours"] * 2) if reason == "TIMEOUT" else s["time_hours"]
            s["history"].append(f"job {s['job']}: {reason} at {s['time_hours']} h")
            if s["attempts"] >= MAX_ATTEMPTS or (reason == "TIMEOUT" and s["time_hours"] >= MAX_HOURS):
                s["status"] = "gave_up"
            else:
                s.update(status="pending", job=None, time_hours=new_time)
                if failover and s.get("partition") != LAB_PARTITION:  # failed on the shared partition: retry on the lab's
                    s.update(partition=LAB_PARTITION, account=LAB_ACCOUNT)
                    s["history"].append(f"retry on {LAB_PARTITION} (failover)")
    # optional: lower the limit of imported tasks still pending to the table estimate (helps backfill; can only decrease)
    if shrink_pending:
        for k, s in state.items():
            jid = f"{s['job']}_{tasks[k]['index']}" if s["status"] == "submitted" else None
            want = float(tasks[k]["time_hours"])
            if jid and q.get(jid, (None,))[0] == "PENDING" and s["time_hours"] > want and s["attempts"] == 1:
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
    lab_unseen = sum(1 for k, s in state.items() if s["status"] == "submitted" and s.get("partition") == LAB_PARTITION
                     and now - s["submitted_at"] <= GRACE_SECONDS and f"{s['job']}_{tasks[k]['index']}" not in q)
    lab_free = LAB_LIMIT - sum(1 for v in q.values() if v[1] == LAB_PARTITION) - lab_unseen
    pending = sorted((k for k, s in state.items() if s["status"] == "pending"),
                     key=lambda k: (int(tasks[k]["priority"]), tasks[k]["batch"], int(tasks[k]["index"])))
    # lab tasks: longest expected first (they gain most from a partition without preemption), into the lab slots;
    # then the rest in priority order; every task also takes a slot of the overall limit
    lab = sorted((k for k in pending if state[k].get("partition") == LAB_PARTITION), key=lambda k: -float(tasks[k]["est_hours"]))
    take = lab[:max(0, min(lab_free, free))]
    take += [k for k in pending if state[k].get("partition") != LAB_PARTITION][:max(0, free - len(take))]
    groups = defaultdict(list)
    for k in take:
        t = tasks[k]
        state[k]["time_hours"] = min(MAX_HOURS, bucket(state[k]["time_hours"]))
        groups[(t["batch"], state[k]["time_hours"], t["args"], state[k].get("partition"), state[k].get("account"))].append(int(t["index"]))
    refused = False
    for (batch, hours, args, part, account), idx in groups.items():
        where = ["-p", part, "-A", account] if part else []
        cmd = ["sbatch", "--parsable", *where, f"--array={ranges(idx)}", f"--time={int(round(hours * 60))}", SLURM_SCRIPT]
        if dry_run:
            print(f"would submit {batch}: {len(idx)} tasks, {hours} h{', ' + part if part else ''}: {' '.join(cmd)}  EXTRA_ARGS='{args}'")
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
        print(f"submitted {batch}: {len(idx)} tasks, {hours} h{', ' + part if part else ''}, job {job}")
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
    global TASKS, STATE, LOCK
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--watch", type=float, metavar="MINUTES", help="repeat every MINUTES until every task is done or given up")
    ap.add_argument("--dry_run", action="store_true", help="print what one pass would do; change nothing")
    ap.add_argument("--shrink_pending", action="store_true", help="lower the 16 h limit of imported tasks still pending to the table estimate")
    ap.add_argument("--to_lab", type=Path, metavar="FILE", help="move the tasks listed in FILE (batch:index per line) to the lab partition")
    ap.add_argument("--now", type=Path, metavar="FILE", help="submit the tasks listed in FILE (batch:index per line) now on the shared partition, ahead of the order")
    ap.add_argument("--include_running", action="store_true", help="with --to_lab: also cancel RUNNING tasks (their progress is lost)")
    ap.add_argument("--tasks", type=Path, default=TASKS, help="task table (default %(default)s)")
    ap.add_argument("--state", type=Path, default=STATE, help="state file; use one per task table (default %(default)s)")
    ap.add_argument("--failover_to_lab", action="store_true", help="tasks preempted (requeued) or failed on the shared partition continue on the lab partition")
    ap.add_argument("--cap_pending", type=float, metavar="HOURS", help="lower the time limit of this table's PENDING tasks to HOURS (e.g. before a maintenance reservation); the state follows")
    args = ap.parse_args()
    if args.tasks != TASKS and args.state == STATE:
        sys.exit("--tasks other than the default needs its own --state file")
    if args.state != STATE:  # the default keeps slurm-logs/autosubmit.lock (a running loop holds it)
        LOCK = args.state.with_suffix(".lock")
    TASKS, STATE = args.tasks, args.state
    sys.stdout = os.fdopen(sys.stdout.fileno(), "w", 1)  # line-buffered: readable live in tmux / a log file (Python 3.6)
    if not TASKS.exists():
        sys.exit(f"{TASKS} not found; run from the repo root after git pull")
    tasks = load_tasks()
    folders = {(PROCESSED_DIR / t["out"]).parent for t in tasks.values()}
    if not any(f.is_dir() or f.parent.is_dir() for f in folders):  # wrong base path would make every finished fit look failed
        sys.exit("none of the output folders exists under {}; check PROCESSED_DIR".format(PROCESSED_DIR))
    STATE.parent.mkdir(exist_ok=True)
    if args.cap_pending:
        with locked():
            state = load_state(tasks)
            cap_pending(tasks, state, args.cap_pending, args.dry_run)
            if not args.dry_run:
                save(state)
        return
    if args.to_lab or args.now:
        keys = [line.split("#")[0].strip() for line in (args.to_lab or args.now).read_text().splitlines()]
        with locked():
            state = load_state(tasks)
            if args.now:
                submit_now(tasks, state, [k for k in keys if k], args.dry_run)
            else:
                to_lab(tasks, state, [k for k in keys if k], args.include_running, args.dry_run)
            if not args.dry_run:
                save(state)
        return
    while True:
        with locked():  # re-read every pass: --to_lab may have changed the state since
            state = load_state(tasks)
            try:
                busy = one_pass(tasks, state, args.dry_run, args.shrink_pending, args.failover_to_lab)
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
