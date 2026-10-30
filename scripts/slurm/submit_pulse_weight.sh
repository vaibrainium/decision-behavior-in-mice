#!/bin/bash
# Submit the joint pulse-weight fits (plan .agents/plans/2026-10-29-pulse-weight-joint.md, steps 2-3b): primary model with
# and without sv, free weight on the pulse component, all 10 mice, cv0-cv4 + all (120 jobs), warm start from the joint fits.
# Run on Hyak from the repo root: bash scripts/slurm/submit_pulse_weight.sh
# Rerun of the cv splits only (tasks 0-99; job 42579333 lost them to a held-out NLL crash, fixed in heldout_nll):
#   bash scripts/slurm/submit_pulse_weight.sh --cv
# Stops before submitting if an input or the warm-start folder is missing or the output folder already exists.
set -euo pipefail
D=/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm
echo "f18e0e6be3b78311e1f5fcdcaa4d0249  $D/ddm_inputs_global_ucla_nofreeze.npz" | md5sum -c
n=$(ls "$D"/fits_joint_unfreeze_integrators/*_L0U0V[01]Z0G1_*.pkl | wc -l)
[[ "$n" -ge 120 ]] || { echo "STOP: fits_joint_unfreeze_integrators has $n primary/no-sv fits, expected 120"; exit 1; }
ARRAY=0-119
if [[ "${1:-}" == "--cv" ]]; then
  ARRAY=0-99
  n_cv=$(find "$D"/fits_joint_unfreeze_pulse_weight -name "*_cv?.pkl" | wc -l)
  [[ "$n_cv" -eq 0 ]] || { echo "STOP: $n_cv cv fits already exist; not submitting"; exit 1; }
elif [[ -e "$D/fits_joint_unfreeze_pulse_weight" ]]; then echo "STOP: fits_joint_unfreeze_pulse_weight already exists; not submitting"; exit 1; fi
mkdir -p slurm-logs
A="--responded_only --guess_model fast_only --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15 --variants L0U0V1Z0G1 L0U0V0Z0G1 --pulse_weight --warm_start_from ddm/fits_joint_unfreeze_integrators --out_dir ddm/fits_joint_unfreeze_pulse_weight"
id=$(env EXTRA_ARGS="$A" sbatch --parsable --array=$ARRAY --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm)
echo "PW_pulse_weight $id"
