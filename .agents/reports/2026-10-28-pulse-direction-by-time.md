# Report: right vs left pulse psychometric parameters at each pulse time
Date: 2026-10-28   Agent: Claude (Opus 5.5)   Commit: (this commit; parent 4dfa100)
Plan: plans/2026-10-28-pulse-direction-by-time.md

## Question
Author refocus: the effect of the pulse at each pulse time, as right vs left pulse only (no control comparisons;
congruency deferred). Do right and left pulses differ in fitted psychometric bias or slope at early, middle, late?

## Summary
Pulses act on bias, not slope. Right minus left bias: early -17.1% coherence (Holm 0.047), middle -12.4 (p 0.021,
Holm 0.10), late -16.8 with a CI spanning zero (6 mice). No slope difference at any time. Only the early bias
difference survives correction, narrowly; the 6-test family was set after the 36-test results were seen, so treat the
corrected p values as post hoc.

## Findings (VERIFIED; scripts/ddm/pulse_direction_by_time.py; tables/pulse_direction_by_time_2026-10-28.csv;
figure figures/qc/pulse_direction_by_time_2026-10-28.png)
| Pulse time (mice) | Bias, right - left | Slope, right - left |
|---|---|---|
| early (10) | -17.1 [-32.1, -4.4], p 0.008, Holm 0.047 | +0.002 [-0.021, 0.026], p 0.84, Holm 1 |
| middle (10) | -12.4 [-23.3, -2.2], p 0.021, Holm 0.10 | +0.017 [-0.007, 0.047], p 0.19, Holm 0.75 |
| late (6) | -16.8 [-49.3, 12.7], p 0.25, Holm 0.75 | +0.001 [-0.037, 0.013], p 0.96, Holm 1 |

- Estimates, CIs and bootstrap p are the right - left rows of
  tables/pulse_psychometric_parameter_bootstrap_2026-10-28.csv (same resamples, seed 0); only the Holm family changed
  (6 tests instead of 18). VERIFIED by construction (script reads those rows).
- Late bias fits hit the +-50 bound in 2.2% of resamples.
- SUSPECTED: the early effect is carried mostly by right pulses (right - control -15.1, left - control +2.0, from the
  parameter bootstrap report); this report does not test that asymmetry.

## What didn't work
Nothing new.

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_psychometric_bootstrap` (once), then
`.venv/bin/python -m scripts.ddm.pulse_direction_by_time --date 2026-10-28`.

## Caveats
- Post hoc family (see Summary). Under the earlier 18-test family the early bias difference had Holm 0.13.
- The bias difference is the same quantity as positive-vs-negative pulses, expressed as a horizontal curve shift.
- Group-mean fits with shared control lapses; late stage 6 mice.

## Open questions and next steps
- [ ] Whether the effect differs between pulse times (not tested; the three CIs overlap heavily).
- [ ] Congruency analysis to be revisited (author).
- [ ] Which pulse analysis the paper reports; then D010.
