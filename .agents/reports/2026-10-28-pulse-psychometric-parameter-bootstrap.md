# Report: bootstrap tests on psychometric parameters, per pulse stage
Date: 2026-10-28   Agent: Claude (Opus 5.5)   Commit: (this commit; parent ed3bc7d)
Plan: plans/2026-10-28-pulse-psychometric-parameter-bootstrap.md

## Question
Author request: the per-pulse-time hierarchical bootstrap, applied to the fitted psychometric parameters (bias mu, slope
beta) instead of the pp choice shift. Do pulses change bias or slope relative to control, per stage?

## Summary
Two of 36 tests survive Holm, both early pulses: congruent curves are steeper than incongruent ones (slope +0.040 per %
coherence, Holm 0.022), and right pulses shift the bias leftward (-15.1% coherence, Holm 0.011) while left pulses do not
shift it (+2.0, Holm 1.0). Middle pulses point the same way but nothing survives; late pulses (6 mice) show nothing.
The slope contrast congruent - incongruent asks the same question as positive-vs-negative (do choices follow the pulse),
not the pp "congruent - incongruent" asymmetry, which was ~1 pp and n.s.

## Findings (VERIFIED; scripts/ddm/pulse_psychometric_bootstrap.py; tables
dissemination/paper_accumulation/tables/pulse_psychometric_parameter_bootstrap_2026-10-28.csv and _parameters_2026-10-28.csv)
Difference [95% percentile CI], bootstrap p, Holm p (18 tests per curve set). Bias in % coherence, slope per % coherence.

| Stage (mice) | Contrast | Bias | Slope |
|---|---|---|---|
| early (10) | congruent - control | -6.3 [-14.5, 1.4] p .099, Holm 1 | +0.027 [0.003, 0.073] p .025, Holm .43 |
| early | incongruent - control | -10.7 [-23.1, 0.6] p .063, Holm .94 | -0.013 [-0.028, 0.007] p .16, Holm 1 |
| early | congruent - incongruent | +4.4 [-8.2, 17.6] p .48, Holm 1 | **+0.040 [0.016, 0.085] p .001, Holm .022** |
| early | right - control | **-15.1 [-25.0, -6.8] p .001, Holm .011** | +0.003 [-0.015, 0.029] Holm 1 |
| early | left - control | +2.0 [-8.3, 13.2] p .67, Holm 1 | +0.001 Holm 1 |
| early | right - left | -17.1 [-32.1, -4.4] p .008, Holm .13 | +0.002 Holm 1 |
| middle (10) | congruent - incongruent | -4.7 [-17.8, 4.8] Holm 1 | +0.027 [-0.001, 0.070] p .057, Holm .92 |
| middle | right - left | -12.4 [-23.3, -2.2] p .021, Holm .33 | +0.017 Holm 1 |
| late (6) | congruent - incongruent | +4.5 [-28.2, 53.0] Holm 1 | +0.007 Holm 1 |
| late | right - left | -16.8 [-49.3, 12.7] Holm 1 | +0.000 Holm 1 |

Figure: dissemination/paper_accumulation/figures/qc/pulse_psychometric_parameter_bootstrap_2026-10-28.png (scripts/ddm/pulse_psychometric_bootstrap_plot.py --date 2026-10-28).
Full 36 rows in the CSV. Observed parameters equal pulse_psychometric_stage_2026-10-28_fits.csv (max difference 5e-5,
rounding); cells.csv unchanged after factoring out stage_curves(). Bias fits at their +-50 bound: 0 in early/middle,
up to 7% of resamples for late.

- VERIFIED: the expected signatures appear in early pulses: congruency acts on slope, direction acts on bias.
- SUSPECTED: the right/left asymmetry of the early bias shift (right -15.1, left +2.0) is a real direction asymmetry
  rather than noise; not tested directly here (right - control vs left - control has no test of its own). Compare with
  reports/2026-10-27-pulse-asymmetry-lapse-checks.md before interpreting.

## What didn't work
Nothing new; pulse curves keep the control's lapses (free lapses were unconstrained, see the by-stage plan).

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_psychometric_bootstrap` (from /src; about a minute on 32 cores). 10,000
resamples, seed 0 (SeedSequence spawned per stage).

## Caveats
- Fits are to group-mean points (descriptive curves), not per mouse; the bootstrap carries mouse and trial variability.
- Pulse curves lack the +-100% (congruent) or 0% points; their slopes depend on the shared control lapses.
- Slope differences are absolute (per % coherence), not ratios.
- 36 tests in two Holm families of 18; the pp bootstrap was a separate family of 9. The paper should report one family.

## Open questions and next steps
- [ ] Author: which pulse analysis the paper reports (pp effects, parameters, or positive-vs-negative); then record D010.
- [ ] If the right/left asymmetry matters, test (right - control) + (left - control) directly per stage.
