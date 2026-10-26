VERDICT: REVISE
<!-- np-contract
stage: S4 ; section: results ; agent: np-stats-reviewer ; version: r1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C002, C003, C004, C005, C006, C007, C009
numbers: N001, N004, N005, N006, N009, N010, N011, N012, N013, N016, N018, N019, N020, N021, N024, N025, N026, N027, N030, N034, N035, N036, N039, N040, N041, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066
sources:
-->
# Statistical review: results round 1

Criteria file: `np/reviews/results/criteria_stats_r1.md`

P0: 0. P1: 5. P2: 0. No new analysis is required: the missing tests, denominators, sensitivity levels and seed counts are present in the cited source records.

## Criterion results

| Criterion | Result | Evidence |
|---|---|---|
| S1 | partly met | Approved tokens are used and units are usually clear, but several inferential statements omit test names/statistics, mouse `n` or simulation denominators. |
| S2 | met | Individual-mouse/equal-mouse summaries are distinguished from trials, cells and sessions; no lower-level unit is used as independent group replication. |
| S3 | partly met | The common-support randomized signed-assignment estimand is correct, but its source-version and outcome-dependent-exclusion qualifications are not adjacent to the causal interpretation. |
| S4 | met | Lines 42–52 retain and quantify pre-onset and no-response outcomes and avoid responder-only conditioning. |
| S5 | partly met | The effect, t interval and Holm-adjusted p lead the claim, but named-test/statistic/raw-p reporting and the validated ten-mouse interval limitation are incomplete. |
| S6 | met | Lines 50–52 call the curves response-associated, cumulative and pointwise/descriptive, with no timing-mechanism claim. |
| S7 | met | Lines 32–38 correctly limit N016 to a relative held-out joint comparison, separate in-sample adequacy and reject a population-p interpretation. |
| S8 | partly met | Recovery limitations are prominent, but hit/false-positive denominators and the pooled correlation denominator are absent. |
| S9 | met | Lines 56–58 use common rows/weights, explicitly disclaim a paired test and retain pipeline-level rather than stage-specific interpretation. |
| S10 | partly met | C009 is restricted to PSUIM6/7 with held-out per-mouse changes, but “limited Monte Carlo seeds” does not disclose the one-seed basis or resulting lack of a direct precision estimate. |
| S11 | partly met | Gate failure/null language is correct, but strategy/calibration denominators and decay-level mappings are omitted. |
| S12 | partly met | Confirmatory, amended and exploratory stages are distinguished, but key assignment, simulation and Monte Carlo limitations are not consistently adjacent and exact figure/output provenance depends on an incomplete Methods section. |

## Issues

| # | Severity | Criteria | Location | Problem | Required change |
|---|---|---|---|---|---|
| 1 | P1 | S1, S5 | Lines 26, 46 and 50 | Statistical reports are incomplete. N012/N013 are presented as unnamed “mouse-level” tests without `n = 10`, test statistic/type or explicit unadjusted status; the primary pulse result gives a t interval and Holm p but not the named two-sided one-sample t test, statistic/df or raw p; the N059 endpoint likewise omits `n = 10 mice`. | Name the Wilcoxon signed-rank and paired Wilcoxon tests and their mouse `n`; identify their p values as unadjusted. For C005, add the mouse-level test/statistic/df and distinguish the raw from Holm-adjusted p, and attach `n = 10 mice` to N059. Use ledger tokens for any added hard values. |
| 2 | P1 | S8 | Line 36 | Recovery rates/correlation lack their analysis denominators: N019 and N020 are not stated as 20 generated datasets each, and N021 is not identified as a pooled across-mouse-and-replicate correlation rather than within-mouse precision. The decision threshold behind hit/false-positive classification is also absent from the paired Methods prose. | Add the `/20` denominators and explicitly label N021 as pooled over the common-model generating/fitted set; cross-reference the exact Methods recovery rule and retain the warning that this does not establish individual-mouse identifiability. |
| 3 | P1 | S3, S4, S12 | Lines 42–48 | The randomized-assignment conclusion omits two qualifications that affect its strength: task code was a current snapshot rather than version-pinned to each collection session, and 15 legacy model-input exclusions were outcome-dependent responses during a pulse. The second issue is disclosed in Methods but not beside the behavioural/generalization claims it limits. | Add a concise adjacent qualification: assignment was verified from the available task-code snapshots and balance audit; the primary behavioural estimand retained assigned outcomes, while the legacy model overlay excluded the disclosed 15 invalid-duration rows and used its historical common-row intersection. Do not weaken the verified primary signed-assignment contrast beyond those limits. |
| 4 | P1 | S10 | Line 60 | “Limited Monte Carlo seeds” is too vague for the selected two-mouse diagnostic. The cited source states one main Monte Carlo seed for each dense mouse, so N063–N066 have no direct repeated-seed uncertainty estimate; the source's multi-seed stability check was performed only in selected smaller mice. | State explicitly that PSUIM6/7 diagnostic scoring used one main seed, that the score changes are uncalibrated QMLE units, and that Monte Carlo precision was not directly estimated for these two mice. Keep C009 descriptive and per-mouse. |
| 5 | P1 | S11, S12 | Lines 66–72 | The mandatory sensitivity record omits crucial denominators and mappings. “Only {{N024}} ... and {{N025}} ... datasets” does not say out of 20 per generator; {{N039}}–{{N041}} are not mapped to 10%, 20% and 40% decay or stated as counts out of 20. The coarse Monte Carlo resolution is therefore invisible. | Report N024/20 and N025/20 full-cohort datasets. Map N039–N041 explicitly to 10%, 20% and 40% decay, each out of 20 datasets, and state that these coarse empirical rates condition on fixed fitted parameters. Preserve the distinct strategy-recovery versus timing-calibration questions. |

## Ruling

No P0 was found. The draft respects nesting, multiplicity, censoring, selection/testing separation, descriptive model–data scope, the two-mouse limit and the failed-gate stopping record. Revision is required because five P1 reporting gaps obscure the exact inferential evidence and its simulation precision.

NEEDS_HUMAN_ANALYSIS: none.

