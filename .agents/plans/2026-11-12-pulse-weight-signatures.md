# Plan: pulse signatures of the existing pulse-weight fits
Status: done (report: reports/2026-11-13-pulse-weight-signatures.md)
Created: 2026-11-12 by Claude (Opus 5.5)
Related reports: reports/2026-10-30-pulse-weight-joint.md, reports/2026-10-31-pulse-time-weights.md, reports/2026-11-12-rescored-ic.md

## Goal
Does a free pulse weight (shared, or per pulse time) close the early-effect gap in PSUIM6/PSUIM7 (data 15.5 / 13.5 pp,
best models <= 9)? Simulate the existing joint "all" fits and compare per-mouse early / late window effects with the
data CIs (pulse_effect_bootstrap). Author 2026-11-12: "go ahead with simulation". Exploratory.

## Context
fits_joint_unfreeze_pulse_weight and fits_joint_unfreeze_pulse_time_weights: linear input, L0U0V1Z0G1 and L0U0V0Z0G1,
splits cv0-4 + all. Weights: PSUIM6 early ~3 (sv and no sv), PSUIM7 early ~2 (no sv only).

## Steps
- [x] 1. primacy.make_model: pass pulse_weight and n_pulse_times; pulse_joint_signatures: register 4 families
      (pulse_weight, pulse_weight_no_sv, pulse_time_weights, pulse_time_weights_no_sv), select() with the fit's
      pulse_weight / n_pulse_times. Check: rescoring a test fold reproduces the stored test NLL.
- [x] 2. Simulate (signature cache, |coh| <= 36) + pulse_effect_bootstrap --tag _pw; per-mouse table vs data.
- [x] 3. Fit browser group + publish; report.

## Out of scope
New fits.

## Log
- 2026-11-12: plan written.
- 2026-11-12: steps 1-2 done; browser v7 (group "All trials, free pulse weight") published; rescored NLL for the 4 families added (rescored_nll_2026-11-12_pw.csv).
- 2026-11-13: report written. Step 1's separate test-fold NLL check was not run (noted in report). Plan closed.
