# Plan: paper-exact Stine et al. (2020) extrema detection and integration models (ESx, DDMx)
Status: active
Created: 2026-10-27 by Claude (Opus 5.5)
Related reports: amendment 13 in dissemination/reports/primacy-analysis-plan.md; ES results in
.agents/plans/2026-10-26-v2-refits-and-strategy-recovery.md (Log)

## Goal
Fit, compare and recover the free-response extrema-detection and integration models exactly as specified by Stine et
al. 2020 (nominal coherence input, κ, B, C0, tND; no sv/guesses), responded-only, and predict pulse trials from them.

## Context
ES (amendment 10) uses motion energy, sv and fast guesses, so it is not the paper's model. Author asked for the exact one.

## Assumptions
- Δt = 1 ms is close enough to their 0.5 ms (they report unchanged results at 1 ms; amendment 10 text).
- The 0.3 s response floor and 50% no-response cap (amendment 11) apply as for all models.
- Pulse timing: logged pulse frames, shifted by Δ (UCLA 54.3 ms, UW 60.1 ms; amendment 13 item 4).

## Steps
- [x] 1. Amendment 13 written before any fit.
- [x] 2. `--nominal_input` in fit_mouse_ddm (variant L0U0V0Z0G0; z = 0.5 for DDMx; wide drift_offset); smoke test
      (DBM13 ccv0, 3 iterations, both models ran and saved; 4 free parameters each).
- [x] 3. Hyak X1 (DDMx, 60 jobs) and X2 (ESx, 60 jobs); commands below.
- [ ] 4. rsync; bound check; ESx vs DDMx and vs common model (held-out NLL, > 10 rule); C0 reported.
- [x] 5a. Code (smoke-tested on DBM13 with 3-iteration fits): build_pulse_timing.py -> ddm/pulse_timing_global.npz
      (13,509 pulse trials; pulse component zero before onset, peak at the response's peak lag in all); primacy.py
      extrema_exact / integration_exact, --strategy_baseline, --lead_shift; lead UCLA 54.3 ms, UW 60.1 ms. Early pulses
      whose shifted start falls before 0 are clipped at 0 (caveat for the report).
- [ ] 5. Pulse timing file (onset/offset frames, pulse coherence by agg_code) and nominal pulse stimuli in primacy.py
      (`--baselines` entries for ESx/DDMx), with the Δ ± 50 ms sensitivity; frozen predictions; strategy test.
- [x] 6a. model_recovery --strategy --exact (DDMx, ESx; 80 jobs), smoke-tested both directions.
- [ ] 6. model_recovery support for nominal input; recovery jobs (80).
- [ ] 7. Verify: report with all numbers traced; STATUS update.

## Hyak commands
X1: env EXTRA_ARGS="--responded_only --nominal_input --variants L0U0V0Z0G0 --splits ccv0 ccv1 ccv2 ccv3 ccv4 control --out_dir ddm/fits_resp_nominal_ddm" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
X2: env EXTRA_ARGS="--responded_only --nominal_input --extrema_samples --variants L0U0V0Z0G0 --splits ccv0 ccv1 ccv2 ccv3 ccv4 control --out_dir ddm/fits_resp_nominal_es" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm

Pulse predictions (10 jobs each; fits_dir per model; lead sensitivity in separate out_dirs):
XP1: sbatch --dependency=afterok:42487747 --array=0-9 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.primacy,EXTRA_ARGS="--predict --responded_only --baselines extrema_exact --fits_dir ddm/fits_resp_nominal_es --out_dir ddm/primacy_exact_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
XP2: same with --baselines integration_exact --fits_dir ddm/fits_resp_nominal_ddm (no dependency)
Sensitivity: XP1/XP2 with --lead_shift -0.05 / 0.05 and --out_dir ddm/primacy_exact_resp_lead-50 / _lead+50
Recovery XR: sbatch --dependency=afterok:42487747 --array=0-79 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.model_recovery,EXTRA_ARGS="--strategy --exact --responded_only --fits_dir ddm/fits_resp_nominal_ddm ddm/fits_resp_nominal_es --out_dir ddm/recovery_exact_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
Needs ddm/pulse_timing_global.npz on Hyak (built locally, sha256 below in Log).

## Out of scope
Collapsing-bound ("elaborated") version; their mean-RT fitting objective; gates for these models.

## Log
- 2026-10-27: plan written; amendment 13; code and smoke test.
- 2026-10-27: X1 DDMx 42474716 done (60/60 saved, 2-5 min per fit; train_nll e.g. PSUIM7 control 11796.0). X2 ESx submitted 42487747.
- 2026-10-27: pulse timing file built locally: /mnt/data/processed/ddm/pulse_timing_global.npz sha256 01d4d378e9cdf731cbcf5a427e8a4ad869416838473ab4d4af83a7d3eaae55f4.
- 2026-10-27: Hyak at 40dc38e, pulse timing sha256 verified. XP2 (DDMx predictions) 42488464; XP1 (ESx predictions) 42488498 after X2; XR (recovery, 80) 42488502 after X2. Pending: lead-shift sensitivity (4 submissions).
