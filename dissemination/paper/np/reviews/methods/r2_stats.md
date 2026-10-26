VERDICT: PASS
<!-- np-contract
stage: S4 ; section: methods ; agent: np-stats-reviewer ; version: r2
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C016, C017, C018
numbers: N001, N004, N005, N006, N009, N010, N016, N018, N022, N023, N051, N052, N053, N054, N055, N056, N057, N058, N059, N060, N061, N062, N063, N064, N065, N066, N067, N068, N069, N070, N071, N072, N073, N074, N075, N076, N077, N078, N079, N080, N081, N082, N083, N084, N085, N086, N087, N088, N089, N090, N091, N092, N093, N094, N095, N096, N097, N098, N099, N100, N101, N102, N103, N104
sources: adelson1985spatiotemporal, bogacz2006physics, luken2025parameter, palmer2005effect, ratcliff2008diffusion, wiecki2013hddm
-->
# Statistical review: methods round 2

Criteria file: `np/reviews/methods/criteria_stats_r2.md`

P0: 0. P1: 0. P2: 0. All five round-1 Methods issues are resolved from existing source-mapped evidence; no new analysis or scope expansion was introduced.

## Round-1 issue closure

| ID | Result | Evidence in v2 |
|---|---|---|
| R1-M1 | resolved | Lines 48–54 define the historical-label population, per-mouse logistic coefficients, the one-sided and paired Wilcoxon tests, unadjusted status, scheduled-label caveat, and conditional shared-ratio profile through N084–N087. The missing W values are result-reporting fields, not missing Methods definitions. |
| R1-M2 | resolved | Lines 88–92 and N081–N082 give within-mouse condition-stratified seed-0 folds, per-fold fitting, fold/mouse score aggregation, held-out seed, ten-seed rescoring, repetitions and the approximate greater-than-10-NLL non-inferential working rule. The text accurately disclaims a universal calibrated cutoff. |
| R1-M3 | resolved | Lines 94–100 and N083 identify all five generator/candidate variants, ten mice × two replicates, independent train/test simulations, the greater-than-10-NLL rule, 20-dataset mechanism-state denominators and the pooled/near-null identifiability limits. |
| R1-M4 | resolved | Lines 126–140 and N093–N094 distinguish original, joint-gain and choice-only objectives; specify grid/refinement, stored folds, seeds, CRN repetitions and held-out aggregation; and state the one-main-seed/no-direct-MC-precision limit for PSUIM6/7. |
| R1-M5 | resolved | Lines 108–124 and N088 name the two-sided one-sample mouse test, df, raw p, Holm p and family. Lines 152–167 give a figure-level provenance map with existing inputs, commands, seeds, hashes/commits and outputs while preserving exact `[MISSING: ...]` placeholders for unfinished figures and the final release lock. |

## Preserved criteria and regression check

| Criterion | Result | Evidence |
|---|---|---|
| S1–S3 | met | Mouse-level inference, supported-cell construction, equal mouse weighting, scheduled assignment, pre-onset responses, no-response outcomes, historical labels and the 15-row legacy exclusion remain explicit. |
| S4–S7 | met | The joint censored objective, model equations/bounds, held-out control comparison, recovery and pulse-gain selection/testing are operationally specified without leakage or p-value reinterpretation. |
| S8–S10 | met | Common-row model–data timing stays descriptive; C009 stays restricted to PSUIM6/7; Holm/pointwise/stopping distinctions and the unrun timing model remain intact. |
| S11 | met | Existing figure-level regeneration records are supplied honestly; final-artwork/source-table/release facts remain specific placeholders rather than inventions. |
| Contract/token provenance | met | `np.py check-contract` passes; N067–N104 are registered and source-mapped in `numbers.csv` and `wave1_number_audit.md`; no placeholder token N105–N109 was fabricated. |

## Issues

None.

NEEDS_HUMAN_ANALYSIS: none.

