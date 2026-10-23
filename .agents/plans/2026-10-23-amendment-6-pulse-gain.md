# Plan: implement primacy plan amendment 6 (cross-validated pulse gain) and run it
Status: done
Created: 2026-10-23 by Claude (Opus 5.5)
Related reports: dissemination/reports/primacy-analysis-plan.md (amendment 6, adopted 6ec9b52); analysis log 5.10

## Goal
The amendment 6 pipeline (revised baselines with a per-mouse pulse gain, cross-validated), its calibration and power
reported, and then (only then) the timing test. Paper stays writable if the revised gate or calibration fails.

## Context
- Gate 1 failed on the 15-rep control fits (analysis log 5.10); strategy test not distinguished.
- Existing code: `primacy.py` (predictions, gates, GLMM, strategy test), `primacy_sensitivity.py` (section 9, needs
  the revised pipeline), `fit_mouse_ddm.py` (control-only fits).

## Assumptions
- Step 5 "final settings" = control-only fits of both baselines at 50 repetitions, warm-started from the 15-rep fits.
- w_p enters as no_pulse_frames + w_p × (signal − coherence × onset response); the noise N is unchanged.
- The w_p fits are 1-D and cheap enough for Hyak (CRN at 50 reps; ~20 likelihood evaluations each).

## Steps
- [x] 1. (done: job 42183146) Step 5 final fits on Hyak: L0U0V1Z0G1 and L1U1V1Z0G1, fast_only, bias free, split control, 50 reps (20 jobs).
- [x] 2. (code; run after step 1) `scripts/ddm/fit_pulse_gain.py`: per (baseline, mouse, fold) fit w_p on the training pulse trials; out-of-fold
      predictions (≥ 200 reps) in the `primacy.py` format, saved with the commit hash; all-trial w_p with a profile
      interval. Unit checks: w_p = 1 reproduces the current predictions; the folds cover each pulse trial once.
- [x] 3. (done: FAILS for both baselines, analysis log 5.11) Revised gate: `primacy.py --analyze --gate_only` on the out-of-fold predictions, plus descriptive calibration
      by coherence and mouse.
- [x] 4. (done; analysis log 5.11: calibrated under the null, no power at 10-40% decay) (code ready: `scripts/ddm/primacy_calibration.py`, a new script rather than an extension of `primacy_sensitivity.py`; run after step 3) Calibration and power (amendment 6 item 6): extend `primacy_sensitivity.py` to run the revised pipeline
      (w_p CV fit → predictions → gate → timing GLMM) on synthetic data at decay 0/10/20/40% (≥ 20 datasets each).
      Report gate-pass rate, false positives at 0, detection conditional on the gate and overall. Hyak.
- [ ] 5. NOT RUN: revised gate failed (amendment 6 item 8). Timing test (only after step 4 is reported): `primacy.py --analyze --unblind` on the revised predictions.
- [x] 6. (report reports/2026-10-23-amendment-6-result.md; paper outline update left to the paper session) Verify and report; update the paper outline's R5 accordingly (three outcome versions already drafted).

## Out of scope
Any further baseline revision for the primacy question (amendment 6 item 8); location-level analyses.

## Log
- 2026-10-23: plan written after amendment 6 was adopted with corrections.
- 2026-10-23: step 1 submitted (42183146). fit_pulse_gain.py written: the gain enters as the simulator's two-channel
  noise_weight (arrays fixed, so the GPU input cache stays valid). Checks: w = 1 reproduces the original predictions
  exactly; w = 0 removes the pulse exactly; each pulse trial predicted once. Gain likelihood profile at 50 reps (15-rep
  control fits, PSUIM10 and DBM14): flat within ~3 NLL for w = 0-7, steep above 10; minimum 3-7 depending on the seed,
  so the gain is only loosely constrained in small mice. primacy_calibration.py written (800 jobs; control fits held
  fixed, a stated caveat); smoke-tested end to end at reduced repetitions.
- 2026-10-23: chained on Hyak: 42183146 (step 1) -> 42183755 (step 2) -> 42183756/57 (step 4). Next: when synced,
  run step 3 (revised gate) and summarize step 4; the timing test (step 5) only after both are reported.
- 2026-10-23: all Hyak results in. Revised gate fails (primary +0.24, secondary +0.31 logit). Timing test not run
  (item 8). Calibration summary running locally (4 parallel processes, one per level).
- 2026-10-23: calibration summarized (4 parallel local runs). Null calibrated (gate 95%, 0/20 false positives); detection
  0-5% at 10-40% decay. Plan done; primacy result final under amendment 6 item 8.
