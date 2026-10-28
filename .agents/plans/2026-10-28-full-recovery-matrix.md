# Plan: full model-recovery matrix (C, E, DDMx, ESx), responded-only
Status: active
Created: 2026-10-28 by Claude (Opus 5.5)
Related reports: reports/2026-10-27-f1a-strategy-recovery-responded.md, reports/2026-10-28-stine-exact-models.md

## Goal
Confusion and inversion matrices over four candidates (amendment 14), from 160 new cross-family fits plus the
existing pairwise recoveries.

## Assumptions
- Same seeds and generator labels reproduce the pairwise synthetic datasets (same code path, synthesize()).
- ES excluded (author: wrong assumptions).

## Steps
- [x] 1. Amendment 14 written before any cross-family fit.
- [x] 2. model_recovery --strategy --cross (160 jobs; candidate gets its own input); smoke test DBM13 C->DDMx and
      DDMx->C (2 iterations), generator folders checked for all four.
- [x] 3. Hyak: 160 jobs (command below).
- [ ] 4. rsync; combine three folders; confusion + inversion matrices; dashboard; report.

## Hyak command
sbatch --array=0-159 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.model_recovery,EXTRA_ARGS="--strategy --cross --responded_only --fits_dir ddm/fits_resp_final ddm/fits_resp_fast_only_leak20-200_cap ddm/fits_resp_nominal_ddm_g001 ddm/fits_resp_nominal_es --out_dir ddm/recovery_cross_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm

## Out of scope
New statistical tests; ES; pulse trials.

## Log
- 2026-10-28: plan written; code and smoke test.
- 2026-10-28: submitted 42503176 (160 jobs, lab A100s: -p gpu-a100 -A gpu-a100-walkerlab --qos=normal), code 63552c1.
- 2026-10-28: tasks 4-159 moved to ckpt-all (Account ckpt-walkerlab, QOS ckpt-gpu) by scontrol; 0-3 ran on gpu-a100.
- 2026-10-28: 160 fits received. Check failed: candidates saw different synthetic data (n_train/n_test differ in 63/80
  datasets across folders; GPU-dependent torch synthesis suspected). Matrix not valid; report
  reports/2026-10-28-recovery-synthetic-data-mismatch.md. Proposed: pre-generated CPU datasets + rerun 320 fits (awaiting OK).
