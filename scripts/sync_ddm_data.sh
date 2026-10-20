#!/bin/bash
# Keep processed/ddm consistent between the lab NAS copy and Hyak.
#
# Ownership (sync only in this direction):
#   inputs  (ddm_inputs_global.npz)          created on the NAS side  ->  pushed to Hyak
#   fits    (every folder under processed/ddm, incl. archive/ and recovery/)  created on Hyak  ->  pulled here
# Moves and deletions of fit folders (e.g. archiving) are done on Hyak only, then mirrored here with `pull --mirror`.
#
# Usage (run where both the NAS copy and `ssh hyak` are available; bash, so from fish call `bash scripts/...`):
#   bash scripts/sync_ddm_data.sh status            # dry run, both directions: what differs, nothing changed
#   bash scripts/sync_ddm_data.sh pull              # Hyak -> here: new/updated fit files (no deletions)
#   bash scripts/sync_ddm_data.sh pull --mirror     # same, and delete fit files/folders here that no longer exist on Hyak
#   bash scripts/sync_ddm_data.sh push-inputs       # here -> Hyak: ddm_inputs_global.npz
# Settings: LOCAL_DDM (default /mnt/data/processed/ddm), REMOTE (default hyak:/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm).
set -euo pipefail

LOCAL_DDM="${LOCAL_DDM:-/mnt/data/processed/ddm}"
REMOTE="${REMOTE:-hyak:/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm}"
INPUTS=(ddm_inputs_global.npz)
# fit outputs = everything except the input files
FIT_FILTER=(--exclude=/ddm_inputs_global.npz)

case "${1:-}" in
  status)
    echo "== Hyak -> here (fit files that would be added/updated here; 'deleting' = only here, would go with --mirror)"
    rsync -ani --delete "${FIT_FILTER[@]}" "$REMOTE/" "$LOCAL_DDM/" | grep -v '^\.d' || true
    echo
    echo "== here -> Hyak (inputs that would be pushed)"
    for f in "${INPUTS[@]}"; do rsync -ani "$LOCAL_DDM/$f" "$REMOTE/$f" || true; done
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
    for f in "${INPUTS[@]}"; do rsync -a --info=stats1 "$LOCAL_DDM/$f" "$REMOTE/$f"; done
    ;;
  *)
    sed -n '2,16p' "$0"
    exit 1
    ;;
esac
