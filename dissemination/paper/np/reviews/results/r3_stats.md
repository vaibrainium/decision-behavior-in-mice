VERDICT: REVISE
<!-- np-contract
stage: S4 ; section: results ; agent: np-stats-reviewer ; version: r3
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C002, C003, C004, C005, C006, C007, C009
numbers: N001, N004, N005, N006, N009, N010, N011, N016, N018, N019, N020, N021, N026, N027, N030, N034, N035, N036, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066, N070, N071, N083, N088, N090, N093, N095, N096, N097, N098
sources:
-->
# Final statistical review: Results round 3

Criteria file: `np/reviews/results/criteria_stats_r3.md`

P0: 0. P1: 1. P2: 0. The complete secondary-pipeline failure record is restored and the incomplete Wilcoxon inference is removed, but one frozen qualification on the retained descriptive N011 result is absent.

## Frozen-criterion findings

| Criterion | Result | Evidence |
|---|---|---|
| F-R1 | met | Lines 66–70 restore secondary N027/N034/N036 beside primary N026/N030/N035, state departure and coverage units, identify the shared adequacy gate, distinguish frozen original predictions from failure-prompted cross-validated mouse gains with control parameters fixed, and state that both revised pipelines failed. The record is confined to Supplementary Figure S6/C007 and is neither confirmation, equivalence nor a replacement baseline. |
| F-R2 | partly met | Line 28 removes N012/N013, Wilcoxon language and the missing-W placeholder; the contract also drops N012/N013. It correctly calls N011 descriptive, conditional on the shared model and historical labels, and not population-wide. It does not state that scheduled-control-label sensitivity was unavailable/unresolved, which the frozen criterion requires whenever N011 is retained. |
| F-R3 | met | Ten-mouse group inference and nesting, randomized signed assignment/common support/equal mouse weights, pre-onset/no-response retention, N088/Holm reporting, pointwise cumulative timing, relative held-out N016 scope, N083 recovery denominators, descriptive C006 overlays, one-seed two-mouse C009 scope, N096–N098 denominators, failed-gate stopping and the no-timing-test/no-null interpretation all remain intact. |
| F-R4 | met | All hard values are registered tokens with their recorded populations/units; restored tokens are limited to C007, claims remain C002–C007/C009, and no new analysis or claim appears. Canonical `np.py lint` reports Results at 2756/2850 words with no error; `np.py check-contract` passes. |

## Issue

| # | Severity | Criterion | Location | Problem | Required change |
|---|---|---|---|---|---|
| 1 | P1 | F-R2 | Line 28 | The retained N011 description gives the shared-model and historical-label limitations but omits the frozen qualification that no scheduled-control-label sensitivity analysis was available. Historical labels identify the population difference but do not disclose that unresolved sensitivity check. | Add the existing-evidence qualification that scheduled-control-label sensitivity was unavailable/not assessed. Do not add a test, statistic or population inference. |

No P0, new claim, new analysis, pseudoreplication, leakage, central multiplicity failure, cohort generalization, false null/equivalence claim or mechanism localization was found.

NEEDS_HUMAN_ANALYSIS: none.
