VERDICT: REVISE
<!-- np-contract
stage: S4 ; section: results ; agent: np-stats-reviewer ; version: r2
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C002, C003, C004, C005, C006, C007, C009
numbers: N001, N004, N005, N006, N009, N010, N011, N012, N013, N016, N018, N019, N020, N021, N026, N030, N035, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066, N070, N071, N083, N088, N090, N093, N095, N096, N097, N098
sources:
-->
# Statistical review: results round 2

Criteria file: `np/reviews/results/criteria_stats_r2.md`

P0: 1. P1: 1. P2: 0. Four of five round-1 Results issues are resolved; one reporting item remains incomplete and one mandatory negative-result regression was introduced.

## Round-1 issue closure

| ID | Result | Evidence in v2 |
|---|---|---|
| R1-R1 | partly resolved | Lines 28, 46 and 52 now name the tests, mouse denominator, unadjusted/Holm distinction, df/CI convention and endpoint mouse unit through N088/N090. However, both hidden-coherence Wilcoxon W statistics remain explicit `[MISSING: ...]` values, so the precommitted complete-statistic criterion is not met. |
| R1-R2 | resolved | Lines 36–38 use N083's 20-dataset state denominators and identify N021 as pooled across mice/replicates rather than within-mouse precision; the exact decision rule is in Methods. |
| R1-R3 | resolved | Lines 44–50 place the task-snapshot/non-session-pinned audit, retained assigned outcomes, N070 exclusions, N071 historical labels and common-row legacy qualification beside C005/C006. |
| R1-R4 | resolved | Lines 62–64 state the one-main-seed PSUIM6/7 basis, uncalibrated QMLE units and absence of direct repeated-seed precision, without transferring small-mouse checks or making a cohort claim. |
| R1-R5 | resolved | Lines 72–74 use N096–N098 to give 20-per-condition denominators, 10/20/40% mappings, 1/20 resolution, fixed fitted-parameter limits and distinct strategy-versus-timing questions. |

## Preserved criteria and regression check

| Criterion | Result | Evidence |
|---|---|---|
| S1 | partly met | All added hard details are registered tokens and most statistical reports are complete; the two missing W statistics remain an explicit completeness gap. |
| S2–S6 | met | Mouse-level inference, supported randomized assignment, retained pre-onset/no-response outcomes, Holm family and pointwise cumulative response-associated timing remain intact. |
| S7–S10 | met | Control selection remains relative/held out, recovery limits remain adjacent, Figure 5 remains descriptive/common-row, and C009 stays a one-seed two-mouse diagnostic. |
| S11 | not met | The v2 S6 subsection retains only the primary pipeline's original/revised gate results (N026, N030, N035). The secondary pipeline outcomes present in v1 and required by the brief/spine—N027, N034 and N036—were removed. |
| S12 | met otherwise | Adaptation/exploration, finite-simulation, fixed-parameter and legacy-row limits are adjacent; no new analysis or unregistered result was added. |

## Issues

| # | Severity | Criteria | Location | Problem | Required change |
|---|---|---|---|---|---|
| 1 | P0 | S11; locked-spine regression | Lines 66–76 and contract line 5 | The mandatory negative record no longer reports the secondary pipeline's original choice departure (N027), gain-revised departure (N034) or revised RT-cell coverage (N036). This regresses from v1, conflicts with the brief's requirement to report both original/revised predictive failures, and leaves the plural spine claim that both pipelines failed without its registered secondary numerical support. | Restore N027, N034 and N036 with their pipeline labels and the same gate-definition/stopping qualifications. Add the tokens to the Results contract. No new computation is needed. |
| 2 | P1 | S1; R1-R1 | Line 28 and writer note | The one-sided and paired hidden-coherence tests now have names, `n` and p values, but their Wilcoxon W statistics remain missing. The number audit identifies this as N108 and warns not to infer W from rounded coefficients or p values. | Export/source-lock the already computed `w_stat` and `d_stat` from notebook cell 25, register token(s), and report them. This is an existing-test output export, not a new scientific analysis. If the workflow elects not to require W, that would need an explicit criteria-level waiver rather than silently passing this frozen check. |

## Ruling

The statistical core remains sound—no pseudoreplication, leakage, censoring regression, invented model–data test, two-mouse generalization or null overinterpretation was found. Results cannot pass round 2 because a mandatory secondary-pipeline negative result was dropped and the precommitted test-statistic field remains unresolved.

NEEDS_HUMAN_ANALYSIS: none. The P0 uses existing registered outcomes; the P1 requires export of an already implemented test's stored variables, not a new analysis design.

