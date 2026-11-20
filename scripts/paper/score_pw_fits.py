"""Score the 2026-11-19 PW fits (gain decay, signed leak; plan 2026-11-19-choice-misfit-followup, criteria A)
with the committed machinery, unchanged:
  held-out  scripts/paper/audit_pulse_choice_rt_score.run (pcv folds, nbins 9) -> <output>/heldout/
  control   scripts/paper/choice_g2_control_training.run (full "pulse" fit on pulse + control trials) -> <output>/control/
Both new and constant-gain counterpart families are scored in the same run (same backend, same seeds).
The only addition is registering the new folders as pulse-only families. Simulation uses the stored parameters,
which include gain_decay / a possibly negative leak_rate; the held-out reproduction check (stored vs recomputed
test NLL) confirms they are applied.

Usage: python -m scripts.paper.score_pw_fits --output <new dir> [--which gain leak] [--seeds ...]
"""
import argparse
from pathlib import Path

from scripts.ddm import pulse_joint_signatures as pjs

NEW = {"pulse_linear_gain_decay": ("fits_pulse_linear_gain_decay", "L0U0V1Z0G1"),
       "pulse_linear_gain_decay_no_sv": ("fits_pulse_linear_gain_decay", "L0U0V0Z0G1"),
       "pulse_linear_signed_leak": ("fits_pulse_linear_signed_leak", "L1U0V1Z0G1"),
       "pulse_linear_signed_leak_no_sv": ("fits_pulse_linear_signed_leak", "L1U0V0Z0G1")}
# criteria A pairs: new -> constant-gain counterpart
PAIRS = {"pulse_linear_gain_decay": "pulse_linear_primary", "pulse_linear_gain_decay_no_sv": "pulse_linear_no_sv",
         "pulse_linear_signed_leak": "pulse_linear_leak", "pulse_linear_signed_leak_no_sv": "pulse_linear_leak_no_sv"}
pjs.PULSE_ONLY_FAMILIES.update(NEW)
pjs.OPTIONS.update({f: {} for f in NEW})

if __name__ == "__main__":
    from scripts.paper.audit_pulse_choice_rt_score import run as run_heldout
    from scripts.paper.choice_g2_control_training import run as run_control
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--which", nargs="+", choices=["gain", "leak"], default=["gain", "leak"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[12345, 23456, 34567, 45678, 56789])
    a = ap.parse_args()
    fams = [f for f in PAIRS if ("gain" in a.which and "gain" in f) or ("leak" in a.which and "leak" in f)]
    fams += [PAIRS[f] for f in fams]
    a.output.mkdir(parents=True, exist_ok=False)
    run_heldout(a.output / "heldout", fams, a.seeds)
    run_control(a.output / "control", fams, a.seeds)
