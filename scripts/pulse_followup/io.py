"""Run directories, hashing, manifests and completion markers shared by every pulse follow-up stage.

Conventions (plan, "File boundaries and handoff contract"):
  run ID     YYYYMMDDTHHMMSSZ_<commit>, created once by the coordinator (package A)
  outputs    /mnt/data/processed/pulse_followup/<run_id>/<stage>/
  figures    dissemination/paper/figures/pulse_followup/<run_id>/<stage>_*.png
  markers    <stage>/COMPLETE (written last, only after outputs and checks); never overwritten

Stages refuse to write into a stage directory that already has a COMPLETE marker, and `write_*` refuse to replace an
existing file, so completed outputs cannot be overwritten silently.
"""

import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROCESSED = Path("/mnt/data/processed")
OUTPUT_ROOT = PROCESSED / "pulse_followup"
FIGURE_ROOT = REPO / "dissemination" / "paper" / "figures" / "pulse_followup"
STAGES = ("data", "stimulus", "behaviour", "response_time", "diagnostics", "models", "validation")


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout


def git_snapshot() -> dict:
    """Commit, dirty tracked diff hash and untracked pulse_followup files (hashed by content)."""
    diff = _git("diff", "HEAD", "--binary").encode()
    code = {str(p.relative_to(REPO)): sha256_file(p) for p in sorted((REPO / "scripts" / "pulse_followup").glob("*.py"))}
    return {
        "commit": _git("rev-parse", "HEAD").strip(),
        "short_commit": _git("rev-parse", "--short", "HEAD").strip(),
        "dirty_tracked_diff_sha256": sha256_bytes(diff),
        "dirty_tracked_files": [line[3:] for line in _git("status", "--porcelain").splitlines() if not line.startswith("??")],
        "pulse_followup_code_sha256": code,
    }


def environment() -> dict:
    versions = {}
    for name in ("numpy", "pandas", "scipy", "statsmodels", "matplotlib"):
        try:
            versions[name] = __import__(name).__version__
        except ImportError:
            versions[name] = None
    return {"python": sys.version.split()[0], "platform": platform.platform(), "executable": sys.executable, **versions}


def new_run_id() -> str:
    return f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{git_snapshot()['short_commit']}"


def run_dir(run_id: str) -> Path:
    path = OUTPUT_ROOT / run_id
    if not path.is_dir():
        raise FileNotFoundError(f"run directory {path} does not exist; package A creates it")
    return path


def stage_dir(run_dir_path, stage: str, create: bool = True) -> Path:
    """The stage's output directory. Refuses a stage that already has a COMPLETE marker."""
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}; expected one of {STAGES}")
    path = Path(run_dir_path) / stage
    if (path / "COMPLETE").exists():
        raise FileExistsError(f"{path} is complete; start a new run or a new suffixed sub-directory instead")
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def figure_dir(run_id: str) -> Path:
    path = FIGURE_ROOT / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _refuse_existing(path: Path):
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")


def write_json(path, obj):
    path = Path(path)
    _refuse_existing(path)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False, default=_json_default) + "\n")
    return path


def write_csv(path, frame, **kwargs):
    path = Path(path)
    _refuse_existing(path)
    frame.to_csv(path, index=False, **kwargs)
    return path


def savefig(fig, path, **kwargs):
    path = Path(path)
    _refuse_existing(path)
    fig.savefig(path, **kwargs)
    return path


def _json_default(o):
    import numpy as np

    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serializable: {type(o)}")


def load_config(run_dir_path) -> dict:
    """The frozen analysis contract. Raises unless package A published its ready marker."""
    data = Path(run_dir_path) / "data"
    if not (data / "COMPLETE").exists():
        raise RuntimeError(f"{data} has no COMPLETE marker: the shared contract is not frozen")
    config = json.loads((data / "analysis_config.json").read_text())
    if not config.get("ready_for_behaviour"):
        raise RuntimeError("analysis_config.json does not set ready_for_behaviour")
    return config


def load_trials(run_dir_path):
    """The frozen trial table, checked against the hash recorded in the config."""
    import pandas as pd

    config = load_config(run_dir_path)
    path = Path(run_dir_path) / "data" / config["files"]["trial_table"]
    if sha256_file(path) != config["hashes"]["trial_table"]:
        raise RuntimeError(f"{path} does not match the hash frozen in analysis_config.json")
    return pd.read_csv(path, dtype={"session_id": str}, keep_default_na=True, low_memory=False), config


class Timer:
    def __init__(self):
        self.start = time.time()

    @property
    def seconds(self) -> float:
        return round(time.time() - self.start, 2)


def stage_manifest(stage: str, command: str, inputs: dict, outputs: list, checks: dict, seconds: float, extra=None) -> dict:
    """Handoff record: code snapshot, input hashes, command, environment, outputs, checks, runtime."""
    return {
        "stage": stage,
        "created_utc": f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
        "command": command,
        "code": git_snapshot(),
        "environment": environment(),
        "inputs_sha256": inputs,
        "outputs": [str(o) for o in outputs],
        "checks": checks,
        "runtime_seconds": seconds,
        **(extra or {}),
    }


def mark_complete(stage_path, manifest: dict, checks_passed: bool):
    """Write the manifest, then the COMPLETE marker only if every check passed."""
    stage_path = Path(stage_path)
    write_json(stage_path / "manifest.json", manifest)
    if not checks_passed:
        print(f"checks failed: {stage_path} left without a COMPLETE marker")
        return False
    write_json(stage_path / "COMPLETE", {"created_utc": manifest["created_utc"], "manifest_sha256": sha256_file(stage_path / "manifest.json")})
    return True
