# Report: does divisive normalization, fitted to control trials, predict the pulse effect?
Date: 2026-11-06   Agent: Claude (Opus 5.5)   Commit: 3b24367
Plan: plans/2026-10-30-normalization-pulse-prediction.md

## Question
Mice respond to the 50 ms pulse more than the motion-energy model predicts. Does a divisive-normalization front end
(F2: x' = x / (1 + fe_beta * lowpass_fe_tau(|x|))), fitted to responded control trials only, predict the pulse effect?

## Summary
It gets the average closer but not the mice. Mean predicted pulse effect (0.3-1.2 s) rises from 3.25 to 4.71 pp
(data 5.48), but the per-mouse error does not fall (mean |error| change -0.17 pp, Wilcoxon p 0.92). The predictions
stay about 2.5-8 pp in every mouse, while the data run from -4.2 to 15.5 pp. Under the rule fixed on 2026-10-30:
NOT "captures the pulse better". High confidence (VERIFIED, 10 mice, pre-registered rule).

## Findings
- VERIFIED, audit: 60/60 fits (PSUIM6 control synced 2026-11-06; Hyak 42621773_58 had completed on 10-31). All
  converged, none at the iteration cap, front_end norm, responded only, n_train = responded control count.
  fe_beta > 0.05 in 9/10 control-split fits (DBM5 0.03); fe_tau 0.06-0.56 s. PSUIM6: fe_beta 1.43, fe_tau 0.30.
- VERIFIED, parameters (control split, median ratio normalization / linear, 9 mice): drift gain 1.55, sv 0.86, bound
  0.93; sv ~0 and bound halved in DBM6 and DBM15.
- VERIFIED, pulse effect 0.3-1.2 s, mean over 10 mice: data 5.48, linear 3.25 (reproduces the 2026-10-29 value),
  normalization 4.71. Per mouse (data / linear / norm): DBM12 -0.5/2.1/2.9, DBM13 1.1/2.4/4.0, DBM14 -4.2/2.4/4.6,
  DBM15 4.4/2.3/5.7, DBM5 3.9/4.5/4.6, DBM6 10.2/5.3/8.2, PSUIM10 0.7/2.1/2.5, PSUIM5 10.4/4.5/4.8,
  PSUIM6 15.5/3.8/5.3, PSUIM7 13.5/3.2/4.6.
- VERIFIED, rule test: |error| normalization - linear: mean -0.17 pp, dz -0.11, paired Wilcoxon p 0.92. Spearman
  predicted vs observed 0.67 vs 0.65. RMSE 5.67 vs 6.00. 1.2-5 s window mean |error| 4.28 vs 4.12 (no better).
  RT shift toward the pulse: data -60, linear -29, normalization -45 ms.
- VERIFIED, mechanism (fitted parameters on real stimuli, DBM6, PSUIM7, DBM12): the pulse is NOT spared; it passes
  0.67-0.91 of its size, less than steady 9% at the same time (0.94-0.98). The higher prediction comes from the refit:
  a higher gain on low-coherence trials (compression handles the high-coherence end), early pulses arriving before the
  pool fills, and, in DBM6/DBM15, sv near 0 and a lower bound.
- SUSPECTED: the steady-input decline (share passed 1.0 at onset to 0.82-0.92 at 1-2 s at 9%) is a sensory
  early-weighting that any primacy claim would have to rule out.

## What didn't work
- The pre-fit idea that normalization spares brief pulses: false for these parameters (above).

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_joint_signatures --cache <dir> --fe_norm --families --tag _fe-norm_9mice --mice <9 mice>`
and `--tag _fe-norm_PSUIM6 --mice PSUIM6` (30 reps, seed 0); tables dissemination/figures/qc/pulse_joint_signatures_2026-11-06_fe-norm_*
(committed 204834a, 3b24367 before comparing). Comparison: inline Python over the two _windows.csv files (this session).
Fits: ddm/fits_resp_fast_only_fe-norm (Hyak 42621772, 42621773).

## Caveats
- One front end form (F2); the static power law is running (plans/2026-11-06-input-mapping-x-accumulator.md, P1),
  expected to predict a smaller effect.
- 10 mice; the rule's power to detect a modest per-mouse improvement is low.

## Open questions and next steps
- [ ] P1 (power law, control-only) frozen prediction under the same rule when its fits land.
- [ ] Mapping x accumulator joint fits (M1, M2) and nominal fits (N1-N4): the plans' rules.
- [ ] What drives the between-mouse spread (PSUIM5/6/7, DBM6 at 10-16 pp vs ~0 elsewhere) is open; no front end tried explains it.
