"""Multi-seed held-out pulse-only rescore of selected families, reusing the committed 2026-11-19 score audit
(scripts/paper/audit_pulse_choice_rt_score.run) unchanged; adds only the family selection.
Usage: python -m scripts.paper.rescore_top_models_multiseed --output <new dir> [--families ...] [--seeds ...]"""
import argparse
from pathlib import Path

from scripts.paper.audit_pulse_choice_rt_score import run

TOP = ["pulse_power_ugm", "pulse_norm_ugm_no_sv", "pulse_linear_leak", "pulse_linear_leak_urgency"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--families", nargs="+", default=TOP)
    ap.add_argument("--seeds", type=int, nargs="+", default=[12345, 23456, 34567, 45678, 56789])
    a = ap.parse_args()
    run(a.output, a.families, a.seeds)
