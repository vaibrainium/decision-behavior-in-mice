#!/bin/bash
# Fit the mouse DDM grid (scripts/ddm/fit_mouse_ddm.py), one fit per array task.
#
# Submit from the repo root on the cluster (the clone is bound to /src in the container):
#   mkdir -p slurm-logs
#   python3 -m scripts.ddm.fit_mouse_ddm --list        # job_id ranges per split (needs the inputs file)
#   sbatch --array=0-319 --export=ALL,JOB_OFFSET=0 scripts/slurm/fit_mouse_ddm.slurm      # split cv0
#   sbatch --array=0-319 --export=ALL,JOB_OFFSET=1600 scripts/slurm/fit_mouse_ddm.slurm   # split all
# job_id = JOB_OFFSET + SLURM_ARRAY_TASK_ID, so the 2240-job grid can be sent in chunks below the cluster's
# MaxArraySize. Jobs whose output already exists are skipped, so preempted or failed tasks can simply be resubmitted.
#
# Needs <repo>/.env (see scripts/slurm/cluster.env.example) with CLUSTER_DATA_PATH and SIF_PATH.

#SBATCH --job-name=mouse_ddm
#SBATCH -p ckpt-all
#SBATCH -A walkerlab
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gpus=1
#SBATCH --mem=24G
#SBATCH --time=08:00:00
#SBATCH --requeue
#SBATCH -o slurm-logs/%x_%A_%a.out
#SBATCH -e slurm-logs/%x_%A_%a.err

set -euo pipefail

PROJECT_ROOT="${SLURM_SUBMIT_DIR}"
source "${PROJECT_ROOT}/.env"
: "${CLUSTER_DATA_PATH:?set CLUSTER_DATA_PATH in .env}" "${SIF_PATH:?set SIF_PATH in .env}"
JOB_ID=$(( ${JOB_OFFSET:-0} + SLURM_ARRAY_TASK_ID ))

module load singularity

singularity exec --nv \
    --bind "${CLUSTER_DATA_PATH}":/mnt/data \
    --bind "${PROJECT_ROOT}":/src \
    "${SIF_PATH}" \
    bash -c "cd /src && export PYTHONPATH=/src && python3 -m scripts.ddm.fit_mouse_ddm --job_id ${JOB_ID}"
