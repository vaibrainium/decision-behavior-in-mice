#!/bin/bash
# Keep processed/ddm consistent between the lab NAS copy and Hyak.
#
# Ownership (sync only in this direction):
#   inputs  (ddm_inputs_global*.npz, pulse_timing_global.npz, recovery_datasets_*/)  created on the NAS side  ->  pushed to Hyak
#   fits    (every other folder under processed/ddm, incl. archive/ and recovery/)  created on Hyak  ->  pulled here
# Inputs are never pulled, so a stale Hyak copy (e.g. an older recovery manifest.json) cannot overwrite the local one,
# and `pull --mirror` never deletes them. Moves and deletions of fit folders are done on Hyak only, then mirrored here.
#
# Usage (run where both the NAS copy and `ssh hyak` are available; bash, so from fish call `bash scripts/...`):
#   bash scripts/sync_ddm_data.sh status            # dry run, both directions: what differs, nothing changed
#   bash scripts/sync_ddm_data.sh pull              # Hyak -> here: new/updated fit files (no deletions)
#   bash scripts/sync_ddm_data.sh pull --mirror     # same, and delete fit files/folders here that no longer exist on Hyak
#   bash scripts/sync_ddm_data.sh push-inputs       # here -> Hyak: input files and recovery dataset folders
# Settings: LOCAL_DDM (default /mnt/data/processed/ddm), REMOTE (default hyak:/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm).
set -euo pipefail

LOCAL_DDM="${LOCAL_DDM:-/mnt/data/processed/ddm}"
REMOTE="${REMOTE:-vthakur@klone.hyak.uw.edu:/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm}"
INPUTS=(ddm_inputs_global.npz ddm_inputs_global_ucla_nofreeze.npz pulse_timing_global.npz)
INPUT_DIRS=(recovery_datasets_*)  # synthetic recovery datasets (CPU, sha256 manifest); glob relative to LOCAL_DDM
# fit outputs = everything except the inputs
FIT_FILTER=(--exclude='*.tmp')  # .tmp: fits being written (renamed when complete)
for f in "${INPUTS[@]}"; do FIT_FILTER+=(--exclude="/$f"); done
FIT_FILTER+=(--exclude='/recovery_datasets_*/')

input_dirs() { (cd "$LOCAL_DDM" && shopt -s nullglob && for d in ${INPUT_DIRS[@]}; do [[ -d "$d" ]] && echo "$d"; done); }

case "${1:-}" in
  status)
    echo "== Hyak -> here (fit files that would be added/updated here; 'deleting' = only here, would go with --mirror)"
    rsync -ani --delete "${FIT_FILTER[@]}" "$REMOTE/" "$LOCAL_DDM/" | grep -v '^\.d' || true
    echo
    echo "== here -> Hyak (inputs that would be pushed)"
    for f in "${INPUTS[@]}"; do [[ -e "$LOCAL_DDM/$f" ]] && { rsync -ani "$LOCAL_DDM/$f" "$REMOTE/$f" || true; }; done
    for d in $(input_dirs); do rsync -ani "$LOCAL_DDM/$d/" "$REMOTE/$d/" | grep -v '^\.d' || true; done
    ;;
  pull)
    if [[ "${2:-}" == "--mirror" ]]; then
      echo "Mirroring fits from Hyak (deletes fit files here that are not on Hyak). Dry run first:"
      rsync -ani --delete "${FIT_FILTER[@]}" "$REMOTE/" "$LOCAL_DDM/" | grep -v '^\.d' || true
      read -r -p "Apply these changes? [y/N] " answer
      [[ "$answer" == "y" ]] || { echo "Aborted."; exit 1; }
      rsync -a --delete "${FIT_FILTER[@]}" "$REMOTE/" "$LOCAL_DDM/"
    else
      rsync -a --info=stats1 "${FIT_FILTER[@]}" "$REMOTE/" "$LOCAL_DDM/"
    fi
    ;;
  push-inputs)
    for f in "${INPUTS[@]}"; do [[ -e "$LOCAL_DDM/$f" ]] && rsync -a --info=stats1 "$LOCAL_DDM/$f" "$REMOTE/$f"; done
    for d in $(input_dirs); do rsync -a --info=stats1 "$LOCAL_DDM/$d/" "$REMOTE/$d/"; done
    ;;
  *)
    sed -n '2,15p' "$0"
    exit 1
    ;;
esac
