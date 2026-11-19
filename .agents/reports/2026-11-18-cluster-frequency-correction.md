# Report: Frequency-aggregation correction for clustered covariance
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Should CR1 count grouped coherence/time cells or the underlying frequency-weighted trials?

## Summary
The grouped-cell correction changed uncertainty under mathematically equivalent trial aggregation. Frequency-weighted objectives/scores require a consistent underlying-trial count here. Fixed CR1 to G/(G-1)*(N_trials-1)/(N_trials-K), checked against explicit individual Bernoulli expansion. No fits or point estimates changed; scientific conclusions unchanged.

## Findings
- VERIFIED: continuous model primary p.049464→.049262. Initial grouped-cell N6184 versus underlying19313; covariance/test/curve output versioned in inference_v2_trial_count/. Source: parent/final primary_slope_tests.csv.
- VERIFIED: earlier ordinal mouse-ID restricted alpha omnibus Holm p3.19679e-5→2.625942499746293e-05;beta.100328→0.09195426886830577. New source: observed_hessian_inference_v2_trial_count/regression_tests.csv. Earlier point estimates/jackknife retained.
- VERIFIED:7 continuous model and6 existing regression tests pass; explicit expansion of grouped counts yields matching Hessian and cluster covariance. Source: tests/test_pulse_time_continuous.py, test_cluster_covariance_is_invariant_to_frequency_aggregation.

## What didn't work
Using grouped-cell count in finite correction was not invariant to aggregation. Earlier statsmodels linearized verification replicated the grouped-row correction and did not test frequency expansion. New regression test addresses this gap. All initial source snapshots/results retained.

## How to reproduce
Tests: `.venv/bin/python -m unittest tests.test_pulse_time_continuous tests.test_pulse_time_mouse_fixed_effects -v`.
Refinement commands in current inference READMEs, using saved fits. Modified functions: covariance in pulse_time_continuous.py; observed_cluster_cov in refine_mouse_fixed_effects_inference.py; cluster_cov in pulse_time_mouse_fixed_effects.py. Source snapshots in original output directories.

## Caveats
This addresses a finite correction, not few-cluster calibration or shared-effect model assumptions.10 mice still imply approximate t/F inference. Older separate per-mouse sign-flip tests unaffected.

## Open questions and next steps
- [ ] Use version2 covariance outputs for future summaries; keep jackknife sensitivity visible.
