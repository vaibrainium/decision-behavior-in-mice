# Plan: bootstrap uncertainty of the data pulse effect; model predictions vs data noise
Status: done
Created: 2026-11-09 by Claude (Opus 5.5)
Related reports: reports/2026-11-09-mapping-accumulator-exploratory.md

## Goal
Author request 2026-11-09 ("perform the bootstraps"): is the late-window misfit (integrators predict a reversal, data
+1.22 pp at 1.2-5 s) and the per-mouse spread (-4.2 to 15.5 pp at 0.3-1.2 s) larger than the sampling noise of the data?
Exploratory, descriptive (no decision rules).

## Context
- Statistic: pulse_joint_signatures.stats_of -> per-mouse window effect (pp), stages pooled by pulse count.
- Model predictions: pulse_joint_signatures_{2026-11-08_explore_partial, 2026-11-09_explore_norm, 2026-11-09_explore_norm_lu}_windows.csv.

## Assumptions
- Sessions are the independent units within a mouse (primary: session bootstrap); trial bootstrap as a lower bound.
- Model simulation noise (30 reps) is small relative to data noise; added as se^2/30.

## Steps
- [x] 1. scripts/ddm/pulse_effect_bootstrap.py: fast weighted-count version of the window statistic; check it reproduces
      stats_of on the data exactly; session and trial bootstrap within mouse (2,000 reps, seed 0); hierarchical
      (mice + sessions) for the mean.
- [x] 2. Per mouse and mean: data effect with 95% CI per window; heterogeneity across mice (Cochran's Q, I^2).
- [x] 3. Every family: model - data per window (mean, with bootstrap CI), mice outside the data CI, sum of squared
      z = (data - model)/se over mice vs chi-square(10).
- [x] 4. Log + report section; commit.

## Out of scope
The sv = 0 counterfactual simulation (check 2, offered separately).

## Log
- 2026-11-09: plan written.
- 2026-11-09: session bootstrap impossible (5 mice with 1-3 sessions); 50-trial blocks within sessions used as the
  sensitivity scheme instead. Done; report reports/2026-11-09-pulse-effect-bootstrap.md.
