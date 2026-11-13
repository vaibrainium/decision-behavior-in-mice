# Plan: per-trial log likelihood in bits (normalized, additive score)
Status: done (report: reports/2026-11-13-bits-per-trial.md)
Created: 2026-11-12 by Claude (Opus 5.5)
Related reports: reports/2026-11-12-likelihood-check.md, reports/2026-11-12-rescored-ic.md

## Goal
Author 2026-11-12: score each trial in bits so scores are normalized and can be summed / compared across mice and
trial subsets. Per trial: log2 P(choice | cell) + log2 P(RT bin | choice, cell), fixed RT bins, probabilities from the
fit's simulation of the trial's cell; reported as information gain over a null (choice 0.5, the mouse's pooled RT
histogram of that choice), in bits per trial; split by mouse and trial type (control / early / middle / late pulse).

## Assumptions
- Fixed bins (primary 100 ms on 0.3-5 s, i.e. 47 bins; check 50 ms); add-0.5 smoothing per bin as the QMLE.
- Cell = the fit's condition cell (coherence x scheduled pulse), per mouse. Evaluation score only (fits optimized QMLE).
- Null RT histogram from the scored trials themselves (in-sample for the null; same for every model, cancels in model
  differences).

## Steps
- [x] 1. scripts/ddm/bits_per_trial.py: per (family, mouse, split) simulate on the scored trials (seed independent of
      the fit), per-trial bits (choice, RT, total), null, per-trial table cached; full-data fits first.
- [x] 2. Run all families, full-data fits (2 GPUs).
- [x] 3. Summaries: bits/trial by family x mouse x trial type; mean over mice (mouse = unit); ranks vs rescored BIC.
- [x] 4. Held-out: CV folds (cv0-4 / pcv0-4), test trials scored by their fold's fit.
- [x] 5. Report (browser view dropped: held-out scores not usable, see log).

## Out of scope
Refitting with this score as objective.

## Log
- 2026-11-12: plan written; author approved ("okay, try it").
- 2026-11-12: steps 1-3 done (full-data, 67 families incl. pulse-weight ones, 30 reps). Null made leave-one-out after the smoke test (in-sample null overfit small mice). Ceiling check: per-cell empirical LOO histogram scores RT -281 mbits (overfits), models -6 to -100, so the pooled null is a strong reference. First held-out run (30 reps on test folds) INVALID: 5x fewer simulated trials per cell -> noisy 47-bin histograms, log p biased down (held-out RT -125 to -260 mbits; pulse-only ranking anti-correlated with held-out NLL). Rerun held-out with 150 reps (= full-data simulated count per cell).
- 2026-11-13: held-out run at 150 reps done (640 tasks, 2 GPUs, ~4 h). Ranking vs held-out NLL: Spearman 0.68 (all-trial), 0.01 (pulse-only). Second seed (45678) for 4 families: per-mouse totals move up to 65 (all-trial) / 89 (pulse-only) mbits, family means 5-26 mbits, as large as the model gaps (norm_primary - power_leak_urgency 12.2 -> 1.5 mbits). Held-out bits are Monte Carlo-noise limited at this simulation size; not used for ranking. Browser view dropped. Plan closed.
