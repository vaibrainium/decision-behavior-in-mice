VERDICT: REVISE
<!-- np-contract
stage: S4 ; section: methods ; agent: np-stats-reviewer ; version: r3
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C016, C017, C018
numbers: N001, N004, N005, N006, N009, N010, N016, N018, N022, N023, N027, N034, N036, N051, N052, N053, N054, N055, N056, N057, N058, N059, N060, N061, N062, N063, N064, N065, N066
sources: adelson1985spatiotemporal, bogacz2006physics, luken2025parameter, palmer2005effect, ratcliff2008diffusion, wiecki2013hddm
-->
# Final statistical review: Methods round 3

Criteria file: `np/reviews/methods/criteria_stats_r3.md`

P0: 0. P1: 1. P2: 0. The secondary-baseline correction is reproducible and bounded, and all prior statistical passes remain intact, but the D005-authorized removal of the incomplete hidden-coherence inference was not made.

## Frozen-criterion findings

| Criterion | Result | Evidence |
|---|---|---|
| F-M1 | met | Lines 144–146 identify `L1U1V1Z0G1` as the supplementary leak-plus-urgency baseline with drift variability, no starting-point variability and fast-only guesses; specify per-mouse control fitting under the primary settings; freeze control parameters during cross-validated pulse-gain revision; give the saved implementation/commit; and restrict its role to C007 and N027/N034/N036 without mechanistic interpretation. |
| F-M2 | not met | Lines 50–54 retain descriptive input characterization with the required historical-label, absent scheduled-label-sensitivity, shared-model and non-population qualifications. However, line 52 still reports both Wilcoxon results N085/N086 and retains the explicit missing-W placeholder. |
| F-M3 | met | The round-2 pass is preserved: mouse-level inference and nesting, randomized assignment, supported-cell/equal-mouse construction, retained pre-onset/no-response outcomes, censoring definitions, held-out model comparison and recovery, pulse-gain split/seed limits, descriptive common-row timing, two-mouse C009 scope, multiplicity/pointwise language, stopping, and honest reproducibility gaps remain explicit. |
| F-M4 | met except for stale inferential tokens | Hard results use registered tokens with their recorded units/populations; N027/N034/N036 are confined to the secondary C007 record. Canonical `np.py lint` reports Methods at 3400/3400 words with no budget error. The draft contract passes `np.py check-contract`, but N085/N086 remain stale because their inference should have been removed. |

## Issue

| # | Severity | Criterion | Location | Problem | Required change |
|---|---|---|---|---|---|
| 1 | P1 | F-M2; D005 | Lines 52 and contract line 5 | The two incomplete Wilcoxon results and missing-W placeholder remain in the reported Methods path; N085/N086 therefore also remain in the contract. This is exactly the inference D005 authorized removing, not a request for a rerun. | Delete the Wilcoxon sentence and missing-W placeholder and remove N085/N086 from the Methods contract. Retain only descriptive hidden-coherence characterization if desired, with the qualifications already present. Do not compute or export W. |

No P0, new claim, new analysis, pseudoreplication, leakage, multiplicity regression, false null/equivalence statement or fabricated provenance was found.

NEEDS_HUMAN_ANALYSIS: none.

