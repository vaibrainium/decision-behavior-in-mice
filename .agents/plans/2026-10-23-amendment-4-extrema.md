# Plan: primacy plan amendment 4, integration vs extrema detection
Status: active
Created: 2026-10-23 by Claude (Opus 5.5)
Related reports: dissemination/reports/primacy-analysis-plan.md (amendment 4); reports/2026-10-22-primacy-power.md;
dissemination/paper/outline.md (core question 5)

## Goal
Before gate 1: control-trial comparison of the extrema-detection model (E) with the common model, and E's pulse-trial
predictions frozen. After gate 1: the strategy test (amendment 4, item 5).

## Context
- E = L1U0V1Z0G1, fast-only guesses, leak_rate in [20, 200] /s (`fit_mouse_ddm.py --leak_bounds 20 200`).
- Guess bias (free vs 0.5) is still undecided (amendment 3), so E and the common model's ccv fits are run both ways.
- `compare_models --fits_dir A B` merges folders by variant name and keeps the better fit; E and the ordinary-leak
  L1U0V1Z0G1 ccv fits (step 3.3, `fits_guess_fast_only`) share the variant name, so the E comparison needs its own
  script.

## Assumptions
- The continuous-time short-leak model is an acceptable stand-in for extrema detection (stated in the paper).
- The common model's bounds (a ≥ 0.3) don't prevent E from fitting; check fitted leak and a at their limits.

## Steps
- [x] 1. `--leak_bounds` in `fit_mouse_ddm.py` (default grids unchanged: 2,240 fit jobs; 20 prediction jobs);
      `--baselines extrema` in `primacy.py` (`STRATEGY_MODELS`, leak bounds checked on load).
- [x] 2. Checks: one-iteration smoke fit (PSUIM10 ccv0, saved leak bounds, warm seeds clipped into range); Numba and
      torch backends agree exactly at leak 0/20/60/200 (400 trials, shared noise).
- [x] 3. Amendment 4 appended to the primacy plan and committed before any pulse outcome was read.
- [ ] 4. User submits the Hyak batches (analysis log 8.4d): E (free and fixed bias, 60 + 60), common model fixed-bias
      ccv (50), descriptive leak 0–200 (10 + 10).
- [ ] 5. `scripts/ddm/compare_strategy.py`: held-out NLL, E vs common model, per mouse and summed, on ccv0–ccv4,
      against the Monte Carlo noise; fitted leak, a **and drift_gain** at their bounds (amendment 5 rule: refit E with
      `--drift_gain_max 200` if drift_gain binds); descriptive time constants.
- [x] 6. Strategy test (item 5, as changed by amendment 5) in `primacy.py` (`strategy_test`, `--strategy_test
      --unblind`): pulse-specific log-likelihood gain (primary) and total (secondary), paired per-trial SD, 3 SD and
      6/10 mice. Null calibration done (`check_strategy_test.py`, 150 datasets: z SD 1.01 / 0.97, 0 beyond 3).
- [ ] 6b. Power of item 5 (amendment 5, item 4): synthetic datasets from the E and common-model fits, once E is fitted.
- [ ] 7. After the guess-bias decision: E predictions (`primacy.py --predict --baselines extrema`), saved with the
      commit hash; record in the analysis log.
- [ ] 8. Verify: E fits converged (nested checks not applicable; compare against warm-seed NLLs), predictions
      reproducible; then report and hand over to gate 1.

## Out of scope
Gate 1 itself; any comparison with recorded pulse outcomes.

## Log
- 2026-10-23: adopted with the proposed defaults (V. Thakur). Draft file removed; text lives in the primacy plan.
- 2026-10-23: review of amendment 4 (V. Thakur asked): item 5 used simulation-only SD and a whole-trial statistic; E's
  drift_gain may bind. Amendment 5 drafted at V. Thakur's request (adoption to be confirmed), code updated, null calibration done.
