# Plan: right vs left pulse psychometric parameters at each pulse time
Status: done
Created: 2026-10-28 by Claude (Opus 5.5)
Related reports: reports/2026-10-28-pulse-psychometric-parameter-bootstrap.md
Related plans: plans/2026-10-28-pulse-psychometric-parameter-bootstrap.md

## Goal
Author request: the effect of the pulse at each pulse time, as right pulse vs left pulse only (no control comparisons;
congruency set deferred). Bias and slope differences with CIs, a figure, and a dashboard panel.

## Specification
- Same bootstrap as the parameter bootstrap (same resamples, seed 0, 10,000): contrast right - left per stage for mu and
  beta. Bootstrap p unchanged; Holm over these 6 tests (3 stages x 2 parameters) instead of the earlier 18.
- Note: this family was chosen after the 18-test results were seen (author's refocus); flag as such in the report.

## Steps
- [x] 1. scripts/ddm/pulse_direction_by_time.py: table + figure from the bootstrap CSVs.
- [x] 2. Verify: estimates and CIs equal the right - left rows of the 18-test table.
- [x] 3. Report, dashboard, STATUS, commit.

## Out of scope
Congruency set (revisit later); control comparisons; tests between pulse times.

## Log
- 2026-10-28: plan written.
- 2026-10-28: done. Early bias right - left -17.1 (Holm 0.047); rest n.s. Dashboard version 16. Report:
  reports/2026-10-28-pulse-direction-by-time.md.
- 2026-10-28: the same 6-test analysis was run for congruent - incongruent (early slope +0.040 [0.016, 0.085], Holm
  0.007; middle slope +0.027, Holm 0.29; no bias differences). Author: not used; congruency dropped for now. Outputs
  and the --set option removed; the numbers come from the 36-test table
  (tables/pulse_psychometric_parameter_bootstrap_2026-10-28.csv) if needed.
- 2026-10-28: author chose right vs left for the paper (D010); congruency panels, the pp congruency bootstrap table and
  the 36-test parameter table removed from the dashboard (version 17); their CSVs and reports stay in the repo.
