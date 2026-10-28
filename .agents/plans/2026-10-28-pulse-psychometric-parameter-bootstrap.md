# Plan: bootstrap tests on psychometric-function parameters, per pulse stage
Status: done
Created: 2026-10-28 by Claude (Opus 5.5)
Related reports: reports/2026-10-28-pulse-congruency-tests.md
Related plans: plans/2026-10-28-pulse-psychometric-by-stage.md, plans/2026-10-28-pulse-congruency-tests.md

## Goal
Author request: the per-pulse-time bootstrap, done on the fitted psychometric parameters (bias mu, slope beta) instead of
the pp choice shift. Output: CI and p per stage x curve set x contrast x parameter.

## Specification (written before computing)
- Same trials, curves, panel mice and fits as pulse_psychometric_stage (responded, symmetric cells, a mouse enters a
  point with >= 5 trials; logistic with lapses on group-mean points weighted by sqrt(n mice); control fits 4 parameters,
  pulse curves fit mu and beta with the control's lapses). Lapses are not tested (only the control fits them).
- Hierarchical bootstrap per stage, as in the congruency bootstrap: resample the panel's mice with replacement, binomial
  redraw within each mouse x curve x coherence cell, rebuild group means, refit control then pulse curves (control
  lapses refitted each resample). 10,000 resamples, seed 0. 95% percentile CI; p = 2 x min(P(b <= 0), P(b >= 0)).
- Contrasts, each for mu and beta:
  congruency set: congruent - control, incongruent - control, congruent - incongruent;
  direction set:  right - control, left - control, right - left.
  Expected signature: congruency acts on beta (congruent steeper, incongruent flatter); direction acts on mu.
- Holm over the 18 tests (3 stages x 3 contrasts x 2 parameters) within each set. Report the fraction of resamples
  where a fit sits at a bound.

## Steps
- [x] 1. Factor curve-trial selection out of pulse_psychometric_stage.cells() so the bootstrap reuses it.
- [x] 2. scripts/ddm/pulse_psychometric_bootstrap.py; table dissemination/paper_accumulation/tables/pulse_psychometric_parameter_bootstrap_<date>.csv.
- [x] 3. Verify: observed parameters equal pulse_psychometric_stage_2026-10-28_fits.csv; cells.csv unchanged after refactor.
- [x] 4. Report section, dashboard table, STATUS.
- [x] 5. Figure (author request): scripts/ddm/pulse_psychometric_bootstrap_plot.py -> figures/qc/pulse_psychometric_parameter_bootstrap_2026-10-28.{png,pdf}; on dashboard.

## Out of scope
Per-mouse psychometric fits; lapse tests; model predictions.

## Log
- 2026-10-28: plan written.
- 2026-10-28: done; run took about a minute (joblib, 32 cores). Two tests survive Holm (early slope congruent -
  incongruent; early bias right - control). Dashboard version 13. Report: reports/2026-10-28-pulse-psychometric-parameter-bootstrap.md.
