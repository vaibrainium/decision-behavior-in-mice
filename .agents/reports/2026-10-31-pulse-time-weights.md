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

## Addendum: simulated pulse effects with the fitted weights (PSUIM6, PSUIM7; author OK 2026-10-31)
Joint fit (weights 1) vs per-time fit, each simulated on the mouse's responded trials, 30 reps, seed 0; statistics as
pulse_joint_signatures (pulse_descriptive_package definitions; |coh| <= 36, symmetric cells), per pulse time and pooled.
Source: scripts/ddm/pulse_time_weight_signatures.py, dissemination/figures/qc/pulse_time_weight_signatures_2026-10-31_{pooled,per_pulse_time}.csv.
VERIFIED numbers.

| mouse | model | weights (early, middle) | early 0.3-1.2 s | middle 0.3-1.2 s | RT shift toward pulse |
|---|---|---|---|---|---|
| PSUIM6 | data | | 18.3 pp | 12.6 pp | -350 ms |
| PSUIM6 | sv joint | 1, 1 | 4.0 | 3.0 | -59 |
| PSUIM6 | sv per-time | 3.16, 1.05 | 11.5 | 3.6 | -129 |
| PSUIM6 | no-sv joint | 1, 1 | 4.7 | 4.2 | -38 |
| PSUIM6 | no-sv per-time | 2.65, 1.19 | 10.6 | 4.8 | -91 |
| PSUIM7 | data | | 15.4 | 11.1 | -96 |
| PSUIM7 | sv (per-time = joint) | 1, 1 | 3.2 | 4.1 | -62 |
| PSUIM7 | no-sv joint | 1, 1 | 4.1 | 5.2 | -22 |
| PSUIM7 | no-sv per-time | 2.11, 0.96 | 8.2 | 4.9 | -44 |

- Where the early weight moves, it closes about half of the early-pulse gap (PSUIM6 sv 4.0 -> 11.5 vs 18.3) and doubles the
  RT shift, with control accuracy and median RT unchanged (acc 36%: 0.757 -> 0.767, data 0.813; median RT 1.69 -> 1.71 s,
  data 1.69). The middle pulse stays at 3.6-4.9 pp vs 11-13 pp in the data in every model: the fit does not raise it.
- Late-window (1.2-5 s) effects stay near the joint fits (sv PSUIM7 still -4.4/-4.8 pp vs data -1.0/-0.9).
- Note: the data effects here (PSUIM6 pooled 15.5 pp) use this script's selection (|coh| <= 36, symmetric cells, pooled
  stages); the LCA illustration's per-time numbers used a different selection and are not comparable.
- Reading: even in the mouse with the most data, a per-time weight takes the early pulse halfway and leaves the middle
  pulse at ~1/3 of the data, at the likelihood optimum. Pulse weighting alone cannot reproduce the pulse effect under the
  joint choice + RT fit. SUSPECTED as a general statement (2 mice).

## Open questions and next steps
- [x] PSUIM6/PSUIM7 simulation with fitted weights (addendum).
- [ ] The pulse-weight line ends here: no shared or per-time weight reproduces the effect across mice, or fully in PSUIM6.
- [ ] What else limits it? In the fits the RT distributions hold the weight down: the pulse-trial RT distributions would
      have to shift by -350 ms (PSUIM6) for the observed choice effect, which no weight produces. Candidate: a pulse
      effect on timing (e.g. the pulse also triggers commitment), not only on evidence.
