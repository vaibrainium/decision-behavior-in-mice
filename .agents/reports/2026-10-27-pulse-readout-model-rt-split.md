# Report: RT-split pulse checks, data vs primary model
Date: 2026-10-27   Agent: Claude Opus 5.5   Commit: eafc83b (+ this packet)
Plan: plans/2026-10-27-pulse-readout-model-rt-split.md

## Question
Where in RT does the primary model (L0U0V1Z0G1, fits_resp_final control fits) fall short of the observed pulse effect?

## Summary
The model gets the shape right: pulse effect in fast-to-middle RTs, none in slow ones, pulse-direction choices faster,
control accuracy rising with RT. It falls short in magnitude in Q1-Q3 (median RT ~0.45-1.3 s), and it predicts a small
late reversal (Q5, -1.6 to -1.8 pp) that the data do not show. Only one bin survives correction (±100% Q2, +8.2 pp).
So the gap is a too-weak pulse on trials deciding within ~1 s of the pulse, not a different mechanism visible in RT.

## Findings (VERIFIED; 10 mice, mean ± SEM; responded trials, symmetric cells; observed control quintile edges;
source dissemination/figures/qc/pulse_readout_model_2026-10-27_{by_bin,rt_given_choice,shortfall}.csv)
| set | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|
| \|c\| <= 36 data (pp) | 4.9 | 4.3 | 6.2 | -0.2 | -0.4 |
| \|c\| <= 36 model | 1.7 | 3.2 | 1.8 | -0.4 | -1.6 |
| data - model, Holm p | 3.2 ± 1.1, 0.077 | 1.2 ± 2.4, 1.0 | 4.4 ± 2.5, 0.44 | 0.2 ± 1.8, 1.0 | 1.2 ± 2.3, 1.0 |
| ±100% data | 2.3 | 11.8 | 2.3 | 0.5 | 3.7 |
| ±100% model | 2.5 | 3.6 | 1.6 | -0.1 | -1.8 |
| data - model, Holm p | -0.2, 1.0 | 8.2 ± 2.5, 0.043 | 0.7, 1.0 | 0.6, 1.0 | 5.5 ± 5.9, 1.0 |
- Control accuracy ±100%: model 0.63, 0.85, 0.90, 0.91, 0.86 vs data 0.66, 0.85, 0.88, 0.90, 0.91 (model dips in Q5).
- RT pulse - control given choice (ms, q 0.1-0.9): toward pulse model 0, -18, -42, -64, -64 vs data 16, -23, -71, -109, -152
  (SEM 23-84); against pulse model 2, 18, 44, 60, 62 vs data -11, -4, 39, 42, -48 (SEM 18-79). Same direction for
  toward-pulse choices; within noise.
- Model's own RT quintiles give the same picture (by_bin.csv, "model (own bins)").
- Simulated response fraction 0.884 (200 reps x 23,229 trials).

## Caveats
Per-bin tests were added after the first run (post hoc), Holm within set over 5 bins. RT bins condition on an outcome
the pulse changes, in model and data alike (same statistic both sides, so the comparison is fair). Primary model only.

## Open questions and next steps
- [ ] The missing late reversal matches the pulse-diagnostics finding (model reverses, data sustained). Together with the
      Q1-Q3 shortfall this suggests the pulse's influence is both larger and longer-lasting than a 300 ms evidence
      transient through the fitted gain; tau_p (300 ms) did not fix the reversal. Author decision on any further model.
