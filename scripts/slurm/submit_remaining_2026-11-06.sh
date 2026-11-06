#!/bin/bash
# Submit the batches left over from submit_mapping_accumulator.sh (refused by QOSMaxSubmitJobPerUserLimit on 2026-11-06)
# and the nominal coherence joint fits (submit_joint_nominal.sh, not yet run), only as far as the queue limit allows.
# Plans: .agents/plans/2026-11-06-input-mapping-x-accumulator.md, .agents/plans/2026-11-06-nominal-coherence-joint-fits.md
# Run on Hyak from the repo root, as often as needed: bash scripts/slurm/submit_remaining_2026-11-06.sh
# Each batch is submitted at most once (recorded in slurm-logs/submitted_2026-11-06.txt); a batch that does not fit
# under LIMIT queued array tasks is skipped and tried again on the next run. Use this script instead of
# submit_joint_nominal.sh (same batches; running both would submit them twice).
set -euo pipefail
LIMIT=${LIMIT:-500}  # observed: 490 queued accepted, +50 refused
D=/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm
echo "f18e0e6be3b78311e1f5fcdcaa4d0249  $D/ddm_inputs_global_ucla_nofreeze.npz" | md5sum -c
echo "105f69fa7e4fcbfa395430ad875dae46  $D/pulse_timing_global.npz" | md5sum -c
mkdir -p slurm-logs
DONE=slurm-logs/submitted_2026-11-06.txt
touch "$DONE"
S=scripts/slurm/fit_mouse_ddm.slurm
J="--responded_only --guess_model fast_only --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15"
N="$J --nominal_input --nominal_matched"
P="--responded_only --guess_model fast_only --front_end power --variants L0U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 control --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --out_dir ddm/fits_resp_fast_only_fe-power_v2"
sub() {
  local name=$1 array=$2 size=$3 args=$4 queued id
  if grep -q "^$name " "$DONE"; then echo "$name already submitted ($(grep "^$name " "$DONE" | cut -d' ' -f2))"; return; fi
  queued=$(squeue -u "$USER" -h -r | wc -l)
  if (( queued + size > LIMIT )); then echo "$name SKIPPED for now ($queued queued + $size > $LIMIT); run again later"; return; fi
  if id=$(env EXTRA_ARGS="$args" sbatch --parsable --array="$array" --time=16:00:00 "$S"); then echo "$name $id" | tee -a "$DONE"; else echo "$name REFUSED; run again later"; fi
}
# priority order: completes the control-only power prediction first, then the bird-style nominal power fit
sub P1_power_ccv 0-49 50 "$P"
sub N4_nominal_power 0-59 60 "$N --front_end power --variants L0U0V1Z0G1 --out_dir ddm/fits_joint_nominal_power"
sub M_norm_integrators 0-239 240 "$J --front_end norm --variants L0U0V1Z0G1 L1U0V1Z0G1 L0U1V1Z0G1 L1U1V1Z0G1 --out_dir ddm/fits_joint_norm_integrators"
sub N1_nominal_integrators 0-299 300 "$N --variants L0U0V1Z0G1 L0U0V0Z0G1 L1U0V1Z0G1 L0U1V1Z0G1 L1U1V1Z0G1 --out_dir ddm/fits_joint_nominal_integrators"
sub N2_nominal_leak20-200 0-59 60 "$N --variants L1U0V1Z0G1 --leak_bounds 20 200 --out_dir ddm/fits_joint_nominal_leak20-200"
sub N3_nominal_es 0-59 60 "$N --variants L0U0V1Z0G1 --extrema_samples --out_dir ddm/fits_joint_nominal_es"
