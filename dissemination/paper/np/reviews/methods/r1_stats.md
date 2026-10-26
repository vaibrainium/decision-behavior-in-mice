VERDICT: REVISE
<!-- np-contract
stage: S4 ; section: methods ; agent: np-stats-reviewer ; version: r1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C016, C017, C018
numbers: N001, N004, N005, N006, N009, N010, N016, N018, N022, N023, N051, N052, N053, N054, N055, N056, N057, N058, N059, N060, N061, N062, N063, N064, N065, N066
sources: adelson1985spatiotemporal, bogacz2006physics, luken2025parameter, palmer2005effect, ratcliff2008diffusion, wiecki2013hddm
-->
# Statistical review: methods round 1

Criteria file: `np/reviews/methods/criteria_stats_r1.md`

P0: 0. P1: 5. P2: 0. No new analysis is required: the cited source reports/code already contain the missing rules and denominators.

## Criterion results

| Criterion | Result | Evidence |
|---|---|---|
| S1 | partly met | Mouse-level group inference and within-mouse weighting are explicit, but the supplementary hidden-coherence inferential analysis reported in Results has no Methods path. |
| S2 | met | Lines 78–90 define pre-outcome rig-specific assignment, supported mouse × session × signed-coherence × onset cells, smaller-arm weights and equal mouse weighting. |
| S3 | met | Lines 20–24 and 80–94 retain pre-onset/no-response outcomes, distinguish the cutoff from task termination, disclose the 15 outcome-dependent legacy exclusions and 48 historical mislabels, and define pseudo-onsets. |
| S4 | met | Lines 48–68 specify model equations, mixture/censor mapping, multinomial outcomes, conditional side-specific RT bins, sparse-cell omission and 0.5 smoothing, while calling the objective simulation-based rather than calibrated. |
| S5 | partly met | Lines 70–74 establish control-only five-fold held-out scoring and correct score meaning, but the fold assignment and Monte Carlo working-threshold algorithm are not specified reproducibly. |
| S6 | partly met | Recovery is reported and its limits are respected, but generators/candidates, replicate count and the threshold used to define hits/false positives are absent. |
| S7 | partly met | Frozen control parameters, common-row restriction and training/held-out folds are stated, but the amended joint-gain objective, exact candidate grid/fold construction and choice-optimal selection rule are incomplete. |
| S8 | met | Line 110 makes the common-row, common-cell/weight comparison explicitly descriptive and disclaims a new timing test. |
| S9 | met | Line 108 limits the diagnostic to PSUIM6/PSUIM7 under a predeclared rule and explicitly declines generalization to weakly informative mice. |
| S10 | partly met | Holm family, pointwise intervals, estimator simulation and stopping are covered, but some named-test/tailing and raw-versus-adjusted reporting rules are incomplete. |
| S11 | partly met | Missing release facts remain honest placeholders, but figure-level input/script/command/version/seed/output provenance is not supplied. |

## Issues

| # | Severity | Criteria | Location | Problem | Required change |
|---|---|---|---|---|---|
| 1 | P1 | S1, S10 | After line 42 or in a supplementary-analysis Methods subsection | Results reports a shared hidden-coherence ratio plus one-sided and paired mouse-level Wilcoxon tests, but Methods never defines the analysis population, coefficient estimation, pooled-ratio fit/profile interval or the two Wilcoxon estimands. This breaks the promised one-to-one Methods path and leaves the supplementary inference unreproducible. | Add the existing notebook-defined analysis: historical control-labelled set and coherence restriction, ten mouse coefficients, shared-ratio/profile procedure, one-sided Wilcoxon signed-rank test against zero and paired Wilcoxon signed-rank comparison. State that these are unadjusted supplementary tests and preserve the scheduled-label caveat. |
| 2 | P1 | S5 | Lines 70–74 | “Assigned trials to folds stratified by condition” and “multiple seeds” do not uniquely reproduce the control comparison. The within-mouse fold algorithm/seed, exact aggregation, rescoring seed count and numerical working-threshold rule are omitted. “Across most mice” is not an operational parsimony rule. | Name the implemented fold routine or fully state its deterministic/random rule and seed, confirm per-mouse fitting and fold aggregation, and give the exact Monte Carlo rescoring/threshold rule used for N016 and component selection. Keep the threshold explicitly non-inferential. |
| 3 | P1 | S6 | Line 74 | Recovery cannot be reconstructed from “five model variants” and {{N018}} files. The text omits the five generator/candidate identities, two replicates per mouse, the held-out score-difference threshold used for hits/false positives, and the denominator construction underlying Results N019–N020. | State the generator/candidate set, ten mice × two replicates, fitting/scoring procedure and exact decision threshold; define hit and false-positive denominators. Retain the pooled-correlation and near-zero generating-effect caveats. |
| 4 | P1 | S7, S9 | Lines 100–108 | The amended pulse-gain and choice-optimal workflows do not identify the joint training objective, exact initial grid, deterministic fold assignment, fold aggregation, or how the “choice-optimal” value differs operationally from the revised joint gain. The prose also says “every available seed” without stating that the dense-mouse held-out diagnostic had only one main Monte Carlo seed. | Define both training objectives and candidate/search rules, identify the stored folds and held-out aggregation, and state the seed count/CRN scheme for the reported PSUIM6/7 diagnostic. Explicitly note that one seed prevents a direct dense-mouse Monte Carlo uncertainty estimate. |
| 5 | P1 | S10, S11 | Lines 88, 120–128 and figure-specific sections | The primary pulse procedure gives a Student-t interval and Holm-adjusted probability but does not name the two-sided one-sample mouse-level t test or distinguish the available raw p from the adjusted p. More broadly, the section supplies generic libraries and an unresolved final lock, but not the versioned inputs, runnable commands/scripts, seeds, environments and output locations needed to regenerate Figures 1–5/S6. | Name the test/tailing and raw-to-Holm adjustment rule. Add a compact figure-level reproducibility map using the already documented report/manifest paths, commands, seeds, hashes/commits and output directories; retain `[MISSING: ...]` only for genuinely unresolved release and final-lock facts. |

## Ruling

No P0 was found. The draft correctly preserves mouse-level inference, random assignment, censoring/no-response outcomes, held-out model selection, descriptive model–data timing scope, the PSUIM6/7 restriction and the stopping rule. Revision is required because the five P1 omissions prevent a reader from fully reproducing or auditing several reported statistical results.

NEEDS_HUMAN_ANALYSIS: none.

