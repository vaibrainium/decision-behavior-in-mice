#!/bin/bash
# Submit the joint control + pulse refits (plan .agents/plans/2026-10-29-joint-control-pulse-refits.md, J1-J7).
# Run on Hyak from the repo root: bash scripts/slurm/submit_joint_unfreeze.sh
# Stops before submitting if an input is missing or corrupt or any fits_joint_unfreeze_* folder already exists.
# Never writes to existing fit folders (new folders only; no --force).
set -euo pipefail
D=/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm
echo "f18e0e6be3b78311e1f5fcdcaa4d0249  $D/ddm_inputs_global_ucla_nofreeze.npz" | md5sum -c
echo "105f69fa7e4fcbfa395430ad875dae46  $D/pulse_timing_global.npz" | md5sum -c
if ls -d "$D"/fits_joint_unfreeze_* >/dev/null 2>&1; then echo "STOP: fits_joint_unfreeze_* already exists; not submitting"; exit 1; fi
mkdir -p slurm-logs
S=scripts/slurm/fit_mouse_ddm.slurm
C="--responded_only --guess_model fast_only --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15"
N="--responded_only --nominal_input --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15 --variants L0U0V0Z0G0"
sub() { local name=$1 array=$2 args=$3; local id; id=$(env EXTRA_ARGS="$args" sbatch --parsable --array="$array" --time=16:00:00 "$S") && echo "$name $id" || echo "$name REFUSED (resubmit later; finished fits are skipped)"; }
sub J1_integrators 0-359 "$C --variants L0U0V1Z0G1 L0U0V0Z0G1 L0U0V1Z0G0 L1U0V1Z0G1 L0U1V1Z0G1 L1U1V1Z0G1 --out_dir ddm/fits_joint_unfreeze_integrators"
sub J2_FB 0-59 "$C --variants L0U0V1Z0G1 --fixed_guess_bias --out_dir ddm/fits_joint_unfreeze_FB"
sub J3_leak20-200 0-59 "$C --variants L1U0V1Z0G1 --leak_bounds 20 200 --out_dir ddm/fits_joint_unfreeze_leak20-200"
sub J4_leak0-200 0-59 "$C --variants L1U0V1Z0G1 --leak_bounds 0 200 --out_dir ddm/fits_joint_unfreeze_leak0-200"
sub J5_es 0-59 "$C --variants L0U0V1Z0G1 --extrema_samples --out_dir ddm/fits_joint_unfreeze_es"
sub J6_nominal_ddm 0-59 "$N --out_dir ddm/fits_joint_unfreeze_nominal_ddm"
sub J7_nominal_es 0-59 "$N --extrema_samples --out_dir ddm/fits_joint_unfreeze_nominal_es"
