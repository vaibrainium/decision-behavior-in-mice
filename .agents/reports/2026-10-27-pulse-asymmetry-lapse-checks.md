# Report: pulse congruency asymmetry and ±100% lapse check
Date: 2026-10-27   Agent: Claude Opus 5.5   Commit: 85d4f8d (+ uncommitted scripts/ddm/pulse_asymmetry_lapse.py)
Plan: plans/2026-10-27-pulse-asymmetry-lapse-checks.md

## Question
Before a nonlinear (sinh) leak model: is incongruent > congruent real beyond the models' own prediction, and is the
±100% pulse effect fast-guess/lapse capture?

## Summary
No asymmetry: excluding asymmetric UW cells, observed incongruent - congruent = 0.54 ± 3.22 pp (p 0.87); every model
predicts 0.36-0.84 pp; observed minus model ≈ 0 for all 7 (Holm p 1.0). The 2.0 vs 4.0 pp split in the earlier figure
came with the asymmetric cells. The test is weak (95% CI of the difference about ±7 pp). At ±100% the excess pulse-direction
errors (3.77 ± 1.15 pp per trial) are spread over RTs, largest at 1-2 s; not concentrated in the fast-guess range.

## Findings (VERIFIED; responded trials, symmetric cells, 21,841 trials; 10 mice; source dissemination/figures/qc/pulse_asymmetry_lapse_2026-10-27_{asymmetry,lapse}.csv)
- Asymmetry A (pp): observed 0.54 ± 3.22; models: primary 0.44, secondary 0.36, primary+gain 0.84, secondary+gain 0.58,
  E 0.76, ES 0.39, free leak 0.38. Obs - model: -0.31 to 0.18, CI about [-7, 7], p > 0.92. Logit scale: same conclusion
  (observed 0.030 ± 0.149).
- ±100% excess errors per trial, incongruent pulse - control (pp, mean ± SEM over mice): 0.3-0.5 s 0.56 ± 0.88,
  0.5-1 s 0.71 ± 0.75, 1-2 s 1.74 ± 0.97, 2-5 s 0.76 ± 0.62; total 3.77 ± 1.15.
- Median error RT, incongruent pulse vs control at ±100%: longer in 7/10 mice (e.g. DBM6 0.75 vs 0.59 s).

## Caveats
Weak asymmetry test (between-mouse SD ~10 pp). RT bins condition on an outcome the pulse may change. Descriptive except the Holm-corrected asymmetry tests.

## Next
- The sinh-leak motivation (asymmetry) is not supported. The slow-trial pattern at ±100% fits the "readout bias on slow
  trials" proposal; its descriptive checks are next (author paste, 2026-10-27).
