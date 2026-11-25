"""Score the informed-guess fits (plan 2026-11-24-informed-guess-family, step 6) with the committed machinery:
  held-out  scripts/paper/audit_pulse_choice_rt_score.run (pcv folds, nbins 9) -> <output>/heldout/
  control   scripts/paper/choice_g2_control_training.run (full "pulse" fit on pulse + control trials) -> <output>/control/
New family and its counterpart (pulse_norm_ugm_no_sv) are scored in the same run (same backend, same seeds). The stored
parameters carry guess_w and read_lag, which the simulation applies; the held-out reproduction check (stored vs
recomputed test NLL) confirms it.
Usage: OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore -m scripts.paper.score_informed_fits --output <new dir>
"""
import argparse
from pathlib import Path

from scripts.ddm import pulse_joint_signatures as pjs

NEW = {"pulse_norm_ugm_informed_no_sv": ("fits_pulse_norm_ugm_informed", "L1U1V0Z0G1")}
PAIRS = {"pulse_norm_ugm_informed_no_sv": "pulse_norm_ugm_no_sv"}
pjs.PULSE_ONLY_FAMILIES.update(NEW)
pjs.OPTIONS.update({f: dict(ugm=True, front_end="norm") for f in NEW})

if __name__ == "__main__":
    from scripts.paper.audit_pulse_choice_rt_score import run as run_heldout
    from scripts.paper.choice_g2_control_training import run as run_control
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--seeds", type=int, nargs="+", default=[12345, 23456, 34567, 45678, 56789])
    a = ap.parse_args()
    fams = list(NEW) + [PAIRS[f] for f in NEW]
    a.output.mkdir(parents=True, exist_ok=False)
    run_heldout(a.output / "heldout", fams, a.seeds)
    run_control(a.output / "control", fams, a.seeds)
