# Plan: paper-exact Stine et al. (2020) extrema detection and integration models (ESx, DDMx)
Status: done (report: reports/2026-10-28-stine-exact-models.md)
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
- [x] 4. rsync; bound check; ESx vs DDMx and vs common model (held-out NLL, > 10 rule); C0 reported.
- [x] 5a. Code (smoke-tested on DBM13 with 3-iteration fits): build_pulse_timing.py -> ddm/pulse_timing_global.npz
      (13,509 pulse trials; pulse component zero before onset, peak at the response's peak lag in all); primacy.py
      extrema_exact / integration_exact, --strategy_baseline, --lead_shift; lead UCLA 54.3 ms, UW 60.1 ms. Early pulses
      whose shifted start falls before 0 are clipped at 0 (caveat for the report).
- [x] 5. Pulse timing file (onset/offset frames, pulse coherence by agg_code) and nominal pulse stimuli in primacy.py
      (`--baselines` entries for ESx/DDMx), with the Δ ± 50 ms sensitivity; frozen predictions; strategy test.
- [x] 6a. model_recovery --strategy --exact (DDMx, ESx; 80 jobs), smoke-tested both directions.
- [x] 6. model_recovery support for nominal input; recovery jobs (80).
- [x] 7. Verify: report with all numbers traced; STATUS update.

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
- 2026-10-27: lead sensitivity submitted: DDMx +50 42488536, DDMx -50 42488544, ESx +50 42488548 (after X2), ESx -50 42488550 (after X2). All amendment-13 jobs queued. Next: when X2 and all of these are done, rsync fits_resp_nominal_ddm, fits_resp_nominal_es, primacy_exact_resp*, recovery_exact_resp; then step 4 (bound check, comparisons), strategy test (--strategy_model extrema_exact --strategy_baseline integration_exact --out_dir ddm/primacy_exact_resp, and per lead dir), recovery verdict, report.
- 2026-10-27 RESULTS v1 (VERIFIED locally; SUPERSEDED for DDMx by the gain-bound refit; inline script, held-out sums in
  scratchpad exact_heldout.csv): all outputs complete (60+60 fits, 6x10 predictions, 80 recovery).
  * DDMx drift_gain at lower bound 0.5 in 31/60 fits; ndt at 0 in 13/60. ESx: no parameter at a bound (gain 3.7-13.1,
    b 3.25-3.60 in control fits). C0 (control fits) DDMx -0.26..0.18, ESx -0.27..0.14.
  * Held-out NLL (control-only CV, summed over folds), per mouse summed / better by > 10:
    ESx - DDMx 31.3 (DDMx 3/10, ESx 1/10); DDMx - C 686.8 (C 7/10, DDMx 0/10); ESx - C 718.0 (C 6/10, ESx 0/10).
    Reference: E - C 278.9 (C 5/10, E 0/10); ES - C 391.0 (C 6/10, ES 0/10; matches the earlier interim).
  * Recovery: DDMx-generated scored DDMx 7, ESx 3, within 10: 10 of 20; ESx-generated scored ESx 9, DDMx 3, within 8.
  * Pulse strategy test ESx (a) vs DDMx (b): lead as rule z 0.60 (pulse) / 0.63 (total); +50 ms -1.07 / -0.06;
    -50 ms 2.36 / 0.63: not distinguished at any lead.
  * Also (sv set, final): E vs primary strategy test (P2 42489706): pulse z 1.43, same sign 7/10, total z 0.00 -> not
    distinguished (ddm/primacy_resp/results_strategy.pkl).
- 2026-10-27: amendment 13 addendum: DDMx drift_gain lower bound 0.01 (NOMINAL_DDM_GAIN_MIN); rerun DDMx fits
  (fits_resp_nominal_ddm_g001), DDMx predictions (primacy_exact2_resp, _lead+50, _lead-50; ESx predictions to be copied
  in locally from primacy_exact_resp*), recovery (recovery_exact2_resp, all 80).
- 2026-10-27: DDMx g001 refit 42491645 (60/60 COMPLETED); predictions 42492100 (rule lead), 42493231 (+50), 42493235 (-50); recovery 42493255 (80, recovery_exact2_resp). Next: rsync; copy ESx predictions from primacy_exact_resp* into primacy_exact2_resp* locally; bound check; rerun comparison, strategy tests, recovery verdict; report.
- 2026-10-27: tried Partition=gpu-a100,ckpt-all Account=gpu-a100-walkerlab on pending recovery tasks 36-79 -> InvalidQOS (one QOS per job; ckpt-gpu not valid for the A100 account). Reverted with Partition=ckpt-all Account=ckpt-walkerlab QOS=ckpt-gpu. To use both pools, split the array by hand (A100 part: -p gpu-a100 -A gpu-a100-walkerlab --qos=normal).
- 2026-10-27: recovery tasks 38-79 were starting one at a time after the partition edit; cancelled and resubmitted as 42497999 (--array=38-79, JOB_OFFSET=0, same out_dir). F1a (42489714) left the queue.
- 2026-10-27 RESULTS v2 (VERIFIED locally; DDMx = fits_resp_nominal_ddm_g001): DDMx gain 0.25-1.13 (none near 0.01;
  12/60 below 0.52, i.e. the old bound did bind); ndt at 0 in 17/60. Refit improved DDMx held-out by 31.4 summed.
  * Held-out (control-only CV): ESx - DDMx 62.7 summed (DDMx better > 10 in 3/10, ESx in 0/10);
    DDMx - C 655.4 (C 6/10, DDMx 0/10); ESx - C 718.0 (C 6/10, ESx 0/10).
  * Pulse strategy test ESx vs DDMx (ESx predictions copied from primacy_exact_resp* into primacy_exact2_resp*;
    identical files): rule lead pulse z 1.20 / total z 1.86; +50 ms -0.58 / 0.13; -50 ms 3.39 (same sign 5/10) / 1.27;
    verdict "not distinguished" at all three.
  * Recovery v2 (recovery_exact2_resp): 38/80 so far; pending 42497999.
- 2026-10-27: 42497999 stalled again on ckpt-all (reason None, nothing running); cancelled; tasks 39-79 resubmitted on lab A100s: 42498684 (-p gpu-a100 -A gpu-a100-walkerlab --qos=normal).
- 2026-10-28: recovery v2 complete (80): DDMx-gen DDMx 5 / ESx 3 / within 12; ESx-gen ESx 7 / DDMx 1 / within 12. Plan done; report reports/2026-10-28-stine-exact-models.md.
