#!/bin/bash
# Motion energy for every trial in valid_data.csv with a comparison filter (scripts/compute_motion_energy_full.py
# --filter; plan .agents/plans/2026-10-29-motion-energy-filter-comparison.md). One shard per array task; outputs
# <CLUSTER_DATA_PATH>/processed/<OUT_DIR>/me_shard_<k>.pkl. Never point OUT_DIR at motion_energy_mouse (pipeline ME).
#
# Submit from the repo root on the cluster (same container and .env as fit_mouse_ddm.slurm):
#   mkdir -p slurm-logs
#   sbatch --array=0-7 --export=ALL,FILTER=okazawa_temporal,OUT_DIR=motion_energy_okazawa_temporal,NUM_SHARDS=8 scripts/slurm/motion_energy_filter.slurm
#   sbatch --array=0-15 --export=ALL,FILTER=okazawa,OUT_DIR=motion_energy_okazawa,NUM_SHARDS=16 scripts/slurm/motion_energy_filter.slurm
# A resubmitted shard resumes from its checkpoint.
#
# The container has no OpenCV; it is side-installed (author decision 2026-10-29), not added to the image:
#   singularity exec "$SIF_PATH" python3 -m pip install --no-deps --target "$CLUSTER_DATA_PATH/pylib" opencv-python-headless==4.11.0.86
# (4.11.0 = the version the pipeline ME was computed with); it is seen in the container as /mnt/data/pylib.

#SBATCH --job-name=me_filter
#SBATCH -p ckpt-all
#SBATCH -A walkerlab
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=9
#SBATCH --gpus=1
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --requeue
#SBATCH -o slurm-logs/%x_%A_%a.out
#SBATCH -e slurm-logs/%x_%A_%a.err

set -euo pipefail

PROJECT_ROOT="${SLURM_SUBMIT_DIR}"
source "${PROJECT_ROOT}/.env"
: "${CLUSTER_DATA_PATH:?set CLUSTER_DATA_PATH in .env}" "${SIF_PATH:?set SIF_PATH in .env}"
: "${FILTER:?set FILTER}" "${OUT_DIR:?set OUT_DIR}" "${NUM_SHARDS:?set NUM_SHARDS}"
[[ "${OUT_DIR}" != "motion_energy_mouse" ]] || { echo "refusing to write the pipeline ME directory"; exit 1; }

module load singularity

singularity exec --nv \
    --bind "${CLUSTER_DATA_PATH}":/mnt/data \
    --bind "${PROJECT_ROOT}":/src \
    "${SIF_PATH}" \
    bash -c "cd /src && export PYTHONPATH=/src:/mnt/data/pylib && python3 -m scripts.compute_motion_energy_full --gpu 0 --shard ${SLURM_ARRAY_TASK_ID} \
        --num-shards ${NUM_SHARDS} --num-workers 8 --queue-maxsize 8 --checkpoint-every 200 --filter ${FILTER} --out-dir ${OUT_DIR}"
