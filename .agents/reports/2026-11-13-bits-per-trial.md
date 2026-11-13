# Report: per-trial log likelihood in bits (normalized, additive score)
Date: 2026-11-13   Agent: Claude (Opus 5.5)   Commit: 4226404 (+ uncommitted scripts/ddm/bits_per_trial.py)
Plan: plans/2026-11-12-bits-per-trial.md (done)

## Question
Author 2026-11-12: score each trial in bits (choice + RT bin, relative to a null) so scores are normalized and can be
summed and compared across mice and trial subsets. Does it rank models as the likelihood / BIC / held-out NLL do, and
what does it say about early-pulse trials? EXPLORATORY.

## Summary
Full-data bits (fits scored on their training trials, independent seed) rank all-trial models like rescored BIC
(Spearman 0.94) and are useful descriptively. Held-out bits (CV test folds scored by their fold's fit) are dominated by
Monte Carlo noise at 150 reps: a second seed moves family means by 5-26 mbits, as much as the model gaps. They do not
rank models reliably and should not replace held-out NLL. Confidence: high on the noise finding (two seeds), moderate on
the full-data ranking (single seed, 30 reps; bias check at more reps not done).

## Findings
- VERIFIED. Definition: choice bits = log2 P(choice|cell) + 1; RT bits = log2 P(100 ms bin | choice, cell) - log2
  P_null, null = the mouse's pooled RT histogram per choice, leave-one-out; bins 0.3-5 s (47), add-0.5 smoothing.
  Source: scripts/ddm/bits_per_trial.py.
- VERIFIED. Full-data, all-trial fits (mean over 10 mice): best power_primary 126.8, power_urgency 124.4,
  power_leak_urgency 124.3 mbits/trial; choice 130-134 for all models, so model differences come from RT; RT bits of
  the best models -6 to -10 (the pooled null is hard to beat at 100 ms); a per-cell empirical LOO histogram scores
  -281. Spearman(total bits, -rescored BIC) 0.94 all-trial, 0.75 pulse-only. Source:
  dissemination/figures/qc/bits_summary_2026-11-12.csv.
- VERIFIED. Early-pulse trials, PSUIM6/7 (full-data): highest choice bits from no-sv per-pulse-time weights (153 / 145)
  and normalized UGM no sv (142 / 146), vs ~136 / 126 for power_leak_urgency. Same file, type == "early".
- VERIFIED. Held-out (150 reps, seed 34567): all-trial top = norm_primary 112.6, urgency 111.6; power_leak_urgency
  (held-out NLL and BIC best) 12th at 100.4. Spearman vs held-out NLL 0.68 all-trial, 0.01 pulse-only; pulse-only RT
  bits -120 to -230. Source: bits_summary_2026-11-13_heldout.csv; ranks vs
  model_ic_summary_2026-11-12_rescored.csv (d_heldout).
- VERIFIED. Seed check (seed 45678, 4 families; per family x mouse x seed table
  dissemination/figures/qc/bits_seedcheck_2026-11-13_heldout.csv): per-mouse totals change up
  to 65 mbits (all-trial) and 89 (pulse-only); norm_primary minus power_leak_urgency 12.2 -> 1.5 mbits;
  pulse_linear_leak mean -61.5 -> -87.4. Held-out bits differences of ~10-25 mbits between models are within noise.
- VERIFIED. PSUIM10 (425 trials): full-data power_leak_urgency beats norm_primary by +157 mbits, almost all on 0.6-1.0
  s RTs (+0.7 bits/trial on 102 trials); on held-out folds -39. Pulse-only fits for PSUIM10 score about -800 mbits
  held-out. Source: bits_per_trial_2026-11-12.csv.gz, bits_per_trial_2026-11-13_heldout.csv.gz.
- SUSPECTED. The PSUIM10 pattern is fit instability with few trials (the full-data fit captures a fast-RT mode the fold
  fits miss), not a scoring artifact; fold parameters not compared.

## What didn't work
- Held-out at 30 reps: 5x fewer simulated trials per cell than full-data; invalid (moved to scratchpad).
- Held-out at 150 reps: still noise-limited (above). The quantile likelihood is less noisy because it uses 9 coarse
  data-quantile bins and drops the RT term in cells with < 9 trials; fine fixed bins on small test folds need far more
  simulation.
- Fitting-time multiprocessing with CUDA (forked workers fail); used one sequential shard per GPU.

## How to reproduce
```
S=<cache dir>
CUDA_VISIBLE_DEVICES=0 .venv/bin/python -m scripts.ddm.bits_per_trial --cache $S/bits --n_reps 30 --shard 0/2  # and 1/2
.venv/bin/python -m scripts.ddm.bits_per_trial --cache $S/bits --n_reps 30          # collect, full-data
# held-out: add --heldout --n_reps 150 (about 4 h on 2 RTX 4090); seed check: --seed 45678 --families ...
```
Inputs: ddm_inputs_global_ucla_nofreeze.npz, pulse_timing_global.npz (responded trials, RT <= 5 s).

## Caveats
- Evaluation score only; fits optimized the quantile likelihood.
- Full-data bits scored on training trials (in-sample for the parameters) at one seed and 30 reps; their seed
  noise is not measured.
- Mouse is the unit (means over 10 mice); no inferential tests.

## Open questions and next steps
- [ ] Measure full-data bits seed noise (2 seeds, a few families) before using them in the browser or text.
- [ ] If held-out bits are wanted: coarser bins (200 ms) and/or many more reps, or compute bits from an analytic /
      KDE density instead of histograms.
- [ ] Compare PSUIM10 fold parameters with its full-data fit (instability check).
