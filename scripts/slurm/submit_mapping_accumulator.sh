#!/bin/bash
# Submit the input mapping x accumulator fits (plan .agents/plans/2026-11-06-input-mapping-x-accumulator.md, M1, M2, P1,
# N4). Run on Hyak from the repo root: bash scripts/slurm/submit_mapping_accumulator.sh
# Stops before submitting if an input is missing or corrupt or any target folder already exists.
# Never writes to existing fit folders (new folders only; no --force).
set -euo pipefail
D=/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm
echo "f18e0e6be3b78311e1f5fcdcaa4d0249  $D/ddm_inputs_global_ucla_nofreeze.npz" | md5sum -c
echo "105f69fa7e4fcbfa395430ad875dae46  $D/pulse_timing_global.npz" | md5sum -c
for f in fits_joint_power_ fits_joint_norm_ fits_resp_fast_only_fe-power_v2 fits_joint_nominal_power; do
  if ls -d "$D"/$f* >/dev/null 2>&1; then echo "STOP: $D/$f* already exists; not submitting"; exit 1; fi
done
mkdir -p slurm-logs
S=scripts/slurm/fit_mouse_ddm.slurm
J="--responded_only --guess_model fast_only --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15"
I="--variants L0U0V1Z0G1 L1U0V1Z0G1 L0U1V1Z0G1 L1U1V1Z0G1"
sub() { local name=$1 array=$2 args=$3; local id; id=$(env EXTRA_ARGS="$args" sbatch --parsable --array="$array" --time=16:00:00 "$S") && echo "$name $id" || echo "$name REFUSED (resubmit later; finished fits are skipped)"; }
for fe in power norm; do
  sub M_${fe}_integrators 0-239 "$J --front_end $fe $I --out_dir ddm/fits_joint_${fe}_integrators"
  sub M_${fe}_leak20-200 0-59 "$J --front_end $fe --variants L1U0V1Z0G1 --leak_bounds 20 200 --out_dir ddm/fits_joint_${fe}_leak20-200"
  sub M_${fe}_es 0-59 "$J --front_end $fe --variants L0U0V1Z0G1 --extrema_samples --out_dir ddm/fits_joint_${fe}_es"
done
P="--responded_only --guess_model fast_only --front_end power --variants L0U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 control --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --out_dir ddm/fits_resp_fast_only_fe-power_v2"
sub P1_power_ccv 0-49 "$P"
sub P1_power_control 50-59 "$P --n_reps 50"
sub N4_nominal_power 0-59 "$J --nominal_input --nominal_matched --front_end power --variants L0U0V1Z0G1 --out_dir ddm/fits_joint_nominal_power"
