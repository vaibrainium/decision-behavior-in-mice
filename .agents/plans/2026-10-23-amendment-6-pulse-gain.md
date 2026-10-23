# Plan: implement primacy plan amendment 6 (cross-validated pulse gain) and run it
Status: active
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
- [ ] 1. Step 5 final fits on Hyak: L0U0V1Z0G1 and L1U1V1Z0G1, fast_only, bias free, split control, 50 reps (20 jobs).
- [ ] 2. `scripts/ddm/fit_pulse_gain.py`: per (baseline, mouse, fold) fit w_p on the training pulse trials; out-of-fold
      predictions (≥ 200 reps) in the `primacy.py` format, saved with the commit hash; all-trial w_p with a profile
      interval. Unit checks: w_p = 1 reproduces the current predictions; the folds cover each pulse trial once.
- [ ] 3. Revised gate: `primacy.py --analyze --gate_only` on the out-of-fold predictions, plus descriptive calibration
      by coherence and mouse.
- [ ] 4. Calibration and power (amendment 6 item 6): extend `primacy_sensitivity.py` to run the revised pipeline
      (w_p CV fit → predictions → gate → timing GLMM) on synthetic data at decay 0/10/20/40% (≥ 20 datasets each).
      Report gate-pass rate, false positives at 0, detection conditional on the gate and overall. Hyak.
- [ ] 5. Timing test (only after step 4 is reported): `primacy.py --analyze --unblind` on the revised predictions.
- [ ] 6. Verify and report; update the paper outline's R5 accordingly (three outcome versions already drafted).

## Out of scope
Any further baseline revision for the primacy question (amendment 6 item 8); location-level analyses.

## Log
- 2026-10-23: plan written after amendment 6 was adopted with corrections.
