# Report: response-aligned fluctuation kernel on recorded choices (amendment 8): neither model fits
Date: 2026-10-26   Agent: Claude (Opus 5.5)   Commit: b92fa6f + uncommitted observed mode in scripts/ddm/fluctuation_kernel.py
Plan: plans/2026-10-25-fluctuation-kernel-power.md (step 4); plans/2026-10-26-paper-accumulation-variant.md

## Question
Does the response-aligned late-weight index of recorded control-trial choices favor the integrator over the
rapid-forgetting (extrema-like) model? Criteria fixed in amendment 8 (primacy-analysis-plan.md; plan SHA-256 bcec2ce9...
at 22:14:30Z) before the recorded-choice run (22:15:40Z).

## Summary
Pre-specified verdict: **neither model fits**. S_I = 11.44 just exceeds its 95th-percentile reference (11.22) and S_E =
14.74 exceeds its reference (13.21). The data lie nominally closer to the integrator, but by the frozen rule this is
inconclusive and does not qualify as supporting evidence for the accumulation-first paper (author condition: "add it if
it pans out"). Confidence in the verdict itself: high (deterministic, rule fixed in advance).

## Findings
- VERIFIED: S_I 11.44 (q95 | I 11.22); S_E 14.74 (q95 | E 13.21); verdict "neither model fits".
- VERIFIED: group mean late-weight index -0.032 % coh, 95% t interval [-0.562, 0.497], n = 10 mice (descriptive).
  Predicted group means: I about +0.25, E about -0.85 (means of the per-mouse predictions).
- VERIFIED (descriptive, no per-mouse verdicts per item 5): per-mouse index vs pred_I / pred_E:
  DBM12 0.06 (0.27/-0.43), DBM13 1.38 (0.46/-0.89), DBM14 0.24 (0.27/-0.11), DBM15 -1.30 (0.61/-0.13),
  DBM5 0.04 (-0.31/-0.51), DBM6 -0.43 (0.27/-0.37), PSUIM10 0.77 (-0.99/-1.55), PSUIM5 -0.61 (0.74/-1.15),
  PSUIM6 -0.19 (0.76/-1.00), PSUIM7 -0.30 (0.40/-1.41). The two reliably classifiable mice split (PSUIM6 nearer E, PSUIM7 nearer I).
- VERIFIED: rule's synthetic operating characteristics (recorded before the run): I 14/20 accumulation, 5/20 not
  distinguished, 1/20 neither; E 19/20 extrema, 1/20 neither.
- Source: /mnt/data/processed/ddm/fluctuation_kernel_observed_2026-10-26.csv; reference
  /mnt/data/processed/ddm/fluctuation_kernel_resp_power_v2.csv.

## What didn't work
- The kernel route does not add independent support for accumulation over the extrema-like model with these trials.

## How to reproduce
`.venv/bin/python -m scripts.ddm.fluctuation_kernel --observed --unblind` (local CPU, seconds; no simulation).

## Caveats
- Predictions are in-sample (fits to the same trials); q95 thresholds come from 20 datasets each, so they are coarse;
  S_I misses its threshold by 0.22. Do not describe this as "nearly supports accumulation" in the paper.
- "Neither" may reflect misfit of both models' fluctuation sensitivity (stimulus-aligned kernel was only 0.1-0.4 % coh).

## Open questions and next steps
- [ ] Authors decide at G1 whether the paper mentions this as an inconclusive exploratory analysis (recommended, to
      avoid selective reporting, e.g. one Methods/supplement sentence) or omits it.
