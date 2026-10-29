# Plan: refit all DDM variants on all responded trials (control + pulse together)
Status: active
Created: 2026-10-29 by Claude (Opus 5.5)
Related: reports/2026-10-29-pulse-leak-vs-urgency.md, reports/2026-10-29-pulse-descriptive-package.md,
reports/2026-10-29-ucla-pulse-me-nofreeze.md, plans/2026-10-26-v2-refits-and-strategy-recovery.md (the control-only set)

## Goal
Author: "refit the ddm models and its variations (including all extrema models) on all responded trials (RT < 5),
control and pulse together, and then see what happens." Done = every model family below fitted per mouse on all
responded trials with 5-fold CV over all trials plus an all-trial fit, and a comparison against the control-only
results: model ranking, parameter shifts, and how well each fitted model reproduces the pulse signatures.

## Context
- Current model selection used control trials only (ccv splits); pulse trials entered only fits_resp_final "all"
  (primary and secondary). Adding pulse trials shifted UCLA parameters (STATUS known issue).
- Inputs: ddm/ddm_inputs_global_ucla_nofreeze.npz (UCLA pulse corrected x1.13; control rows identical to v1).
- Responded-only likelihood with the 50% non-response cap (amendment 11) is in the code; fast_only guesses.
- Fit times on control CV (15 reps): median 1-29 min per fit by family, max 77 min; all-trial data are ~1.7x larger.

## Models (12 families; mouse x split grid each)
| # | Family | Variant / options | Previous control-only folder |
|---|---|---|---|
| 1 | primary integrator | L0U0V1Z0G1 | fits_resp_fast_only |
| 2 | no drift variability | L0U0V0Z0G1 | fits_resp_fast_only |
| 3 | no guesses | L0U0V1Z0G0 | fits_resp_fast_only |
| 4 | + leak | L1U0V1Z0G1 | fits_resp_fast_only_cap |
| 5 | + urgency | L0U1V1Z0G1 | fits_resp_fast_only |
| 6 | + leak + urgency | L1U1V1Z0G1 | fits_resp_fast_only |
| 7 | guess bias fixed | L0U0V1Z0G1 --fixed_guess_bias | fits_resp_fast_only_FB |
| 8 | rapid forgetting E | L1U0V1Z0G1 --leak_bounds 20 200 | fits_resp_fast_only_leak20-200_cap |
| 9 | free leak 0-200 | L1U0V1Z0G1 --leak_bounds 0 200 | fits_resp_fast_only_leak0-200_cap |
| 10 | extrema sampling ES | L0U0V1Z0G1 --extrema_samples | fits_resp_fast_only_es_cap |
| 11 | Stine nominal DDM | --nominal_input (gain min 0.01) | fits_resp_nominal_ddm_g001 |
| 12 | Stine nominal ES | --nominal_input --extrema_samples | fits_resp_nominal_es |
Families 11-12 need a code change: nominal input is defined for control trials only. Proposed: nominal pulse =
pulse coherence held for the recorded pulse frames (as primacy.nominal_stimuli, lead 0). Needs author OK.

## Steps
- [x] 0. Author approval of model list, inputs, reps and cost; decision on families 11-12.
- [x] 1. (if 11-12 approved) add nominal pulse input to fit_mouse_ddm.select; unit check on a few trials; commit, push.
- [ ] 2. Hyak: per family, splits cv0-cv4 + all, 15 reps, cold start (warm starts match split names; the control-only
      folders have ccv/control splits only), NEW folders ddm/fits_joint_unfreeze_* (nothing old is written); 720 fits. Commands below.
- [ ] 3. Pull fits; audit (non-response cap, parameters at bounds, failed fits).
- [ ] 4. Model comparison on held-out NLL over all trials (summed over folds, per mouse, mice as unit; same rules as
      the control-only selection), next to the control-only ranking.
- [ ] 5. Parameter shifts: all-trial vs control fits, per family and mouse (rig as covariate only).
- [ ] 6. Pulse signatures: simulate each all-trial fit on the real schedules; S1 profile, window effects, RT shifts
      vs data (scripts/ddm/pulse_descriptive_package.py statistics).
- [ ] 7. Report; STATUS.

## Out of scope
Free pulse gain (separate option, see log), recovery runs, manuscript changes.

## Log
- 2026-10-29: plan proposed; not started.
- 2026-10-29: approved by the author (AskUserQuestion): no-freeze inputs, include Stine nominal models with a nominal
  pulse, 15 reps everywhere. Author: "store them separately. Don't override any old models". Step 1 done: nominal
  pulse = scheduled pulse coherence over the logged pulse frames (UCLA 50 ms, UW 67 ms; checked); --pulse_timing
  option. Smoke tests (DBM14 cv0, 2 reps, 3 iterations): nominal DDM, nominal ES, primary all ran.

## Hyak commands (from the repo root; needs ddm_inputs_global_ucla_nofreeze.npz and pulse_timing_global.npz in
## processed/ddm on Hyak)
```
C="--responded_only --guess_model fast_only --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15"
# J1 integrator families 1-6 (360)
env EXTRA_ARGS="$C --variants L0U0V1Z0G1 L0U0V0Z0G1 L0U0V1Z0G0 L1U0V1Z0G1 L0U1V1Z0G1 L1U1V1Z0G1 --out_dir ddm/fits_joint_unfreeze_integrators" sbatch --array=0-359 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# J2 guess bias fixed (60)
env EXTRA_ARGS="$C --variants L0U0V1Z0G1 --fixed_guess_bias --out_dir ddm/fits_joint_unfreeze_FB" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# J3 rapid forgetting E (60)
env EXTRA_ARGS="$C --variants L1U0V1Z0G1 --leak_bounds 20 200 --out_dir ddm/fits_joint_unfreeze_leak20-200" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# J4 free leak 0-200 (60)
env EXTRA_ARGS="$C --variants L1U0V1Z0G1 --leak_bounds 0 200 --out_dir ddm/fits_joint_unfreeze_leak0-200" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# J5 extrema sampling ES (60)
env EXTRA_ARGS="$C --variants L0U0V1Z0G1 --extrema_samples --out_dir ddm/fits_joint_unfreeze_es" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# J6, J7 Stine nominal DDM and ES (60 each; guess form unused in L0U0V0Z0G0)
N="--responded_only --nominal_input --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15 --variants L0U0V0Z0G0"
env EXTRA_ARGS="$N --out_dir ddm/fits_joint_unfreeze_nominal_ddm" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
env EXTRA_ARGS="$N --extrema_samples --out_dir ddm/fits_joint_unfreeze_nominal_es" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
```
- 2026-10-29: author renamed outputs to fits_joint_unfreeze_* (J1 -> fits_joint_unfreeze_integrators).
