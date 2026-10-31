# Report: separate pulse weight per pulse time (joint fit, 10 mice)
Date: 2026-10-31   Agent: Claude (Opus 5.5)   Commit: see git log for this file
Plan: plans/2026-10-30-pulse-time-weights.md

## Question
Does a free pulse weight per pulse time (early / middle / late) improve held-out prediction over the shared weight and the
joint model, and are early pulses weighted more than later ones across mice (primacy)?

## Summary
No at the group level. Held-out NLL does not improve (sum -2.0 sv, -8.4 no-sv vs the joint fits; all Holm p = 1.0) and the
weights are ~1 in most mice, so no early > middle > late ordering across mice. One mouse carries the only clear signal:
PSUIM6 fits an early weight ~3 (sv 3.16, no-sv 2.65) with middle ~1, and predicts held-out trials better (-17.3 sv vs joint).
PSUIM7 shows the same in the no-sv model only (early 2.11, held-out -9.0). This matches the pre-fit likelihood profile. Confident
for the group null (VERIFIED); the PSUIM6 primacy-like weight is one mouse (SUSPECTED as a general property).

## Findings
- All 120 fits succeeded, none at the iteration cap. VERIFIED.
- Held-out NLL, per-time weights minus joint, summed over cv0-cv4 per mouse (Wilcoxon over 10 mice, Holm over the 10 tests
  in the summary file): sv sum -2.0, median +0.46, better by >10 in 1 mouse (PSUIM6 -17.3), worse by >10 in 1 (DBM15 +11.8);
  no-sv sum -8.4, median +0.29, 0 better / 0 worse by >10. Vs the shared weight: sv -16.8, no-sv -17.2 (sums), Holm p 1.0.
  VERIFIED. Source: dissemination/figures/qc/pulse_time_weights_{per_mouse,summary}_2026-10-31.csv,
  `.venv/bin/python -m scripts.ddm.compare_pulse_time_weights`.
- Weights, all-trial fits (early / middle / late): 1.00-1.06 for every weight in 6/10 mice (sv) and 5/10 (no-sv).
  Exceptions: sv PSUIM6 3.16 / 1.05; sv DBM6 1.83 / 1.00 / 1.66; sv DBM13 1.33 / 1.39 / 1.33; no-sv PSUIM6 2.65 / 1.19;
  no-sv PSUIM7 2.11 / 0.96; no-sv PSUIM5 1.66 / 1.67; no-sv PSUIM10 4.55 / 4.71 (425 trials; unstable, as with the shared
  weight); no-sv DBM14 1.18 / 0.67 / 1.01. Fold medians agree for PSUIM6 (early 2.56 sv, 2.81 no-sv; middle ~0.95). VERIFIED.
- Ordering across mice (paired, all-trial fits): early - middle, sv median +0.003 (6/10 positive), no-sv +0.011 (5/10);
  middle - late (6 UW mice) and early - late: medians ~0; all Holm p = 1.0. VERIFIED.
- Pooled pre-fit profile (reports/2026-10-30-pulse-time-weight-profile.md) suggested early ~1.5 / middle ~1 / late ~0.5 for
  the sv model; the fits do not reproduce this at the group level: the pooled gain came mostly from PSUIM6/PSUIM7.

## What didn't work
- First comparison run hit the parameter `sv` overwriting the model label column (same bug as compare_pulse_weight); fixed.

## How to reproduce
Fits: Hyak job 42623428 (scripts/slurm/submit_pulse_time_weights.sh at 89f14d2), out ddm/fits_joint_unfreeze_pulse_time_weights.
Comparison: `.venv/bin/python -m scripts.ddm.compare_pulse_time_weights`.

## Caveats
- 10 mice; per-mouse likelihoods are nearly flat in the weights for all but the densest mice, so weights mostly stay at their
  warm start (1). The group null is partly "not identifiable", not only "equal to 1".
- Pulse-time bins are only ~0.2 s apart (early vs middle); late exists in 6 UW mice.
- Simulated pulse effects with the fitted weights were not run (step 5: weights differ only in PSUIM6, PSUIM7 no-sv).

## Open questions and next steps
- [ ] Optional: simulate PSUIM6 with its fitted weights to see if an early weight ~3 brings the predicted 0.3-1.2 s
      effect up to its data (9.3 pp early in that mouse) and keeps the RT fit.
- [ ] The pulse-weight line ends here unless the author wants the PSUIM6 check: no shared or per-time weight helps across mice.
