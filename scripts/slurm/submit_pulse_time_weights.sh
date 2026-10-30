#!/bin/bash
# Submit the per-pulse-time weight fits (plan .agents/plans/2026-10-30-pulse-time-weights.md): primary model with and without
# sv, one free pulse weight per pulse time (UCLA 2, UW 3), all 10 mice, cv0-cv4 + all (120 jobs), warm start from the
# shared pulse-weight fits (copied into every per-time weight) and the joint fits (all weights 1).
# Run on Hyak from the repo root: bash scripts/slurm/submit_pulse_time_weights.sh
# Stops before submitting if an input or a warm-start folder is missing or the output folder already exists.
set -euo pipefail
D=/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm
echo "f18e0e6be3b78311e1f5fcdcaa4d0249  $D/ddm_inputs_global_ucla_nofreeze.npz" | md5sum -c
for W in fits_joint_unfreeze_integrators fits_joint_unfreeze_pulse_weight; do
  n=$(find "$D/$W" -name "*_L0U0V[01]Z0G1_*.pkl" | wc -l)
  [[ "$n" -ge 120 ]] || { echo "STOP: $W has $n primary/no-sv fits, expected 120"; exit 1; }
done
if [[ -e "$D/fits_joint_unfreeze_pulse_time_weights" ]]; then echo "STOP: fits_joint_unfreeze_pulse_time_weights already exists; not submitting"; exit 1; fi
mkdir -p slurm-logs
A="--responded_only --guess_model fast_only --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15 --variants L0U0V1Z0G1 L0U0V0Z0G1 --pulse_time_weights --warm_start_from ddm/fits_joint_unfreeze_pulse_weight ddm/fits_joint_unfreeze_integrators --out_dir ddm/fits_joint_unfreeze_pulse_time_weights"
id=$(env EXTRA_ARGS="$A" sbatch --parsable --array=0-119 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm)
echo "PTW_pulse_time_weights $id"
