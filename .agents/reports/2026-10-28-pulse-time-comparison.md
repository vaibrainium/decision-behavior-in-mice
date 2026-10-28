# Report: does the pulse effect change with pulse time?
Date: 2026-10-28   Agent: Claude (Opus 5.5)   Commit: (this commit; parent ffe4a39)
Plan: plans/2026-10-28-pulse-time-comparison.md

## Question
Author: is the right vs left pulse effect larger for earlier pulses (early > middle > late)?

## Summary
No within-mouse evidence that the pulse effect changes with pulse time. Every within-mouse contrast (early - middle on
10 mice; early - late, middle - late on the 6 mice with late pulses) has an interval spanning zero, in the per-mouse
tests, the hierarchical model, and the RT-conditioned sensitivity. The apparent decline in per-stage group means
(early > middle > late) is mostly a mouse-set effect: late pulses exist only in 6 mice, and those mice have small
pulse effects at every pulse time. Underpowered: a modest decline cannot be excluded.

## Findings (VERIFIED; scripts/ddm/pulse_time_comparison.py; tables/pulse_time_comparison_{per_mouse,tests,bayes}_2026-10-28.csv;
figure figures/qc/pulse_time_comparison_2026-10-28.png)
Pulse effect = right - left pulse, per mouse and pulse time.

Hierarchical Bayesian logistic model (PyMC; 4 x 1,000 draws; 0 divergences, max r_hat 1.005, min ESS 1,329).
Right - left log-odds, averaged over the sample mice:
| | Mice | Mean | 95% HDI | P(> 0) |
|---|---|---|---|---|
| early effect | 10 | 0.47 | [0.31, 0.63] | 1.00 |
| middle effect | 10 | 0.33 | [0.18, 0.49] | 1.00 |
| late effect | 6 | 0.17 | [-0.07, 0.40] | 0.92 |
| early - middle | 10 | 0.14 | [-0.08, 0.37] | 0.89 |
| early - late | 6 | 0.05 | [-0.28, 0.37] | 0.61 |
| middle - late | 6 | 0.04 | [-0.31, 0.37] | 0.58 |

Per-mouse estimates, paired tests (Holm over 3; mice as unit):
| Measure | early - middle (10) | early - late (6) | middle - late (6) | Page trend (6 mice) |
|---|---|---|---|---|
| pp, all trials | -0.8 [-9.8, 8.2], Holm 1.0 | +1.5 [-8.7, 11.8], Holm 1.0 | +5.3 [-1.2, 11.9], t Holm 0.27, Wilcoxon Holm 0.094 (6/6 positive) | p 0.10; 3/6 monotone |
| logit, all trials | +0.08 [-0.13, 0.28], Holm 0.84 | +0.07 [-0.23, 0.37], Holm 0.84 | +0.06 [-0.06, 0.18], Holm 0.83 | p 0.24; 2/6 monotone |
| logit, RT > onset + 100 ms | +0.00 [-0.28, 0.29], Holm 1.0 | +0.07 [-0.40, 0.54], Holm 1.0 | +0.09 [-0.13, 0.31], Holm 0.98 | p 0.24; 3/6 monotone |

- VERIFIED: in the 6 mice with late pulses, mean logit effect is 0.20 / 0.19 / 0.13 (early / middle / late); the 10-mouse
  means are 0.44 / 0.36 at early / middle. The group-level decline to late reflects which mice are in the late panel.
- VERIFIED: the early - middle hint (Bayes P(> 0) 0.89) comes mainly from the two mice with the most trials (logit early
  vs middle 1.06 vs 0.51 and 0.91 vs 0.51, SE ~0.12-0.14); the model weights trials, the per-mouse tests weight mice
  equally (early - middle 0.08, 5/10 mice positive).
- VERIFIED: RT > onset + 100 ms keeps 100% / 97.1% / 84.1% of early / middle / late pulse trials (10.1% of late-pulse
  trials responded before the pulse began). Conditioning does not change the conclusions.
- pp middle - late (6/6 mice positive, uncorrected Wilcoxon 0.031) is driven by one mouse's middle value (DBM15, 29 pp)
  and does not hold in the logit measure (4/6 positive).
- Rig covariate on the early and middle effects (g, centred): early -0.32 [-0.51, -0.13], middle -0.15 [-0.33, 0.01];
  included as a covariate only, not interpreted by site.

## What didn't work
- First full run was killed (out of memory) by `az.rhat(idata).to_array()`, which broadcasts all variables together;
  replaced by a per-variable maximum.
- No frequentist logistic GLMM available (plan deviation logged); Bayesian model + per-mouse paired tests instead.

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_time_comparison` from /src (about 5 min; PyMC seed 0).

## Caveats
- 10 mice (6 for late). The early - middle CI on logit (-0.13 to 0.28) still admits a decline of about half the middle
  effect; "no evidence of change", not "equal effects".
- Bayesian contrasts are not p values; report HDIs and P(> 0).
- pp measure averages over 5-7 coherences per mouse (those present in all of the mouse's stages, both directions).
- Late-pulse trials include 10% that responded before the pulse began; handled by the RT sensitivity.

## Open questions and next steps
- [ ] Paper text: pulses shift choices at each pulse time (early and middle clearly, late in 6 mice weakly); no
      detectable change across pulse times within mice. Author to confirm wording.
- [ ] If a decline matters for the thesis, a power estimate for the early - middle contrast (statistical-power skill).
