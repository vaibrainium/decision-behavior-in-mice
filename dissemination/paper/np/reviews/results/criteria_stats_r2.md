<!-- np-contract
stage: S4 ; section: results ; agent: np-stats-reviewer ; version: r2
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C002, C003, C004, C005, C006, C007, C009
numbers: N001, N004, N005, N006, N009, N010, N011, N012, N013, N016, N018, N019, N020, N021, N024, N025, N026, N027, N030, N034, N035, N036, N039, N040, N041, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066
sources:
-->
# Statistics criteria commitment: results round 2

Sources used: `np/spine.md`, `np/briefs/results.md`, `np/reviews/results/criteria_stats_r1.md`, `np/reviews/results/r1_stats.md`, `np/reviews/methods/r1_stats.md`, and `review-rubrics.md` (no v2 draft seen).

Round 2 is unchanged in scope. Every round-1 criterion S1–S12 remains binding with its original P0/P1 thresholds; the table below freezes both regression protection and the five issue-closure tests. Existing evidence may be reported more completely, but no new analysis, claim, comparison or unregistered hard value may be introduced.

## Preserved round-1 criteria

| Original criterion | Round-2 preservation test | Regression severity |
|---|---|---|
| S1: complete traceable statistics | Every inference uses approved tokens and gives effect, labelled uncertainty, `n` with unit, named test/statistic, p/correction where applicable; descriptive values remain labelled. | P0 for fabrication/central missing inference/pseudoreplication; P1 for incomplete test, unit or interval reporting. |
| S2: mouse-level inference | Ten mice remain the group sampling unit; trials, cells and sessions explain support/precision only; per-mouse replication and equal-mouse aggregation remain clear. | P0 for inflated lower-level replication; P1 for unclear aggregation or `n`. |
| S3: randomized assignment estimand | C005 remains the direct positive-versus-negative scheduled-assignment contrast on common support with equal mice; pulse-control comparisons remain separately qualified. | P0 for delivered/outcome-conditioned labels or indirect comparison; P1 for missing assignment/support/control qualifications. |
| S4: pre-onset/no-response outcomes | Pre-onset responses and `no response by 5 s` remain visible in effects/denominators; exclusions and legacy restrictions remain adjacent. | P0 for post-onset/complete-case conditioning; P1 for buried denominators/exclusions/label limits. |
| S5: effect and multiplicity | Figure 4 leads with mouse-level magnitude/CI, then the named test and declared Holm family; robustness is not analysis shopping. | P0 for uncorrected/altered central family; P1 for unclear test, raw/adjusted p, interval or assumptions. |
| S6: response-associated timing | The 0.5–2-s curve remains cumulative, pointwise and descriptive of emitted responses, not a weighting kernel, persistence, latency or corrected time-bin test. | P0 for timing-mechanism or uncorrected confirmatory bin claims; P1 for unclear endpoint/pointwise/carry-forward limits. |
| S7: relative held-out model selection | N016 remains a control-only joint cross-validated score, non-p-value working threshold and comparison of the tested pair; components/in-sample adequacy are contextual. | P0 for leakage, p-value interpretation or unique-mechanism proof; P1 for incomplete aggregation/scope/MC limits. |
| S8: recovery beside model claim | Hit/false-positive recovery, pooled parameter recovery, boundaries and outcome misfits remain adjacent and do not imply individual-mouse precision. | P0 for concealed failed recovery/mechanistic use; P1 for missing denominators, rules or consequences. |
| S9: descriptive Figure 5 mismatch | C006 uses common rows/weights and no invented paired test, reversal language or stage localization. | P0 for invented inference or unique localization; P1 for unclear alignment/uncertainty/legacy limit. |
| S10: C009 two-mouse diagnostic | PSUIM6/7 have per-mouse held-out score changes and explicit selection/seed/uncertainty limits; no cohort test or representative language. | P0 for cohort generalization/circular confirmation; P1 for incomplete selection/objective/MC precision. |
| S11: failed gates and null language | Original/revised gate failures, RT coverage, strategy recovery, calibration and non-performance of the timing test remain visible; low sensitivity is not equivalence or biological absence. | P0 for omission/null conversion/unrun-test claim; P1 for incomplete denominator, level, chronology or stopping details. |
| S12: selection, provenance and adjacency | Prespecified, amended and exploratory analyses; multiplicity families; legacy/MC limitations; and figure/method/output provenance remain adjacent to affected claims. | P0 for circular/undisclosed flexibility or invented provenance; P1 for deferred or incomplete labels/provenance. |

## Required closure of round-1 issues

| ID | Round-1 issue | What must be present in v2 | REVISE if | BLOCK / P0 if |
|---|---|---|---|---|
| R1-R1 | Incomplete inferential reporting | Hidden coherence: one-sided Wilcoxon signed-rank and paired Wilcoxon signed-rank, `n = 10 mice`, unadjusted p status. C005: named two-sided one-sample t test, statistic/df, raw and Holm-adjusted p, three-test family. N059: `n = 10 mice`. Every new hard statistic must be an approved ledger token. | Any test, statistic, df, p status, correction or mouse `n` remains missing. | A hard value is inserted without an approved token/source or a different test is introduced. |
| R1-R2 | Recovery denominators absent | N019 and N020 stated with 20-dataset denominators; N021 identified as pooled across ten mice × two replicates for the common-model generator/fit, not individual-mouse precision; exact decision rule available in Methods. | A rate/correlation denominator or scope remains ambiguous. | Recovery is reframed as independent validation or mechanism proof. |
| R1-R3 | Assignment/exclusion qualifications not adjacent | C005 identifies assignment verification from available task-code snapshots plus balance audit and notes lack of per-session code pinning; primary behavioural estimand retained assigned outcomes; legacy model overlay notes the 15 outcome-dependent invalid-duration exclusions and common-row intersection. | One qualification is absent or so remote that causal/generalization scope is misleading. | The primary effect becomes delivered-exposure/complete-case inference or exclusions are concealed. |
| R1-R4 | C009 Monte Carlo precision vague | Explicit one main seed for PSUIM6 and PSUIM7; uncalibrated QMLE score units; no direct repeated-seed precision estimate for the dense pair; multi-seed small-mouse checks are not transferred to them. | “Limited seeds” or equivalent remains nonspecific, or precision scope is unclear. | The two-mouse diagnostic becomes a cohort/significance claim or receives invented uncertainty. |
| R1-R5 | Sensitivity denominators/mappings absent | N024/20 extrema-generated and N025/20 accumulator-generated full cohorts; N039/20, N040/20 and N041/20 mapped to 10%, 20% and 40% decay; coarse resolution and conditioning on fixed fitted parameters; distinct strategy-recovery versus timing-calibration questions. | Any denominator, decay mapping or fixed-parameter/precision limit remains missing. | Low recovery/detection becomes equivalence, no primacy or support for a strategy. |

## Token provenance and regression checks

- Every added or changed hard value must already exist in `np/ledger/numbers.csv` and be used with its registered unit, denominator and analysis set. Prose-only denominators may be added only when directly documented by the existing ledger/source records; they must not create a new result.
- Claims remain C002–C007 and C009 in their approved locations. C006 alone heads Figure 5; C009 stays subordinate and limited to PSUIM6/7.
- No new paired model-minus-observed test, pulse-sign asymmetry test, recovery run, gain fit, timing test or mechanism claim is permitted.
- Fixes must not remove retained pre-onset/no-response outcomes, Holm correction, pointwise wording, held-out distinctions, recovery limits, failed gates, low sensitivity or the explicit statement that the timing test was not run.

## Round-2 decision rule

- PASS requires all five R1-R issues resolved, all S1–S12 protections preserved, valid contract/tokens, and no new P0/P1/P2 regression.
- REVISE if an existing P1 is only partly resolved or any new P1/P2 statistical/reporting issue appears.
- BLOCK if resolution genuinely requires a new human analysis or conflicts with approved evidence; label it `NEEDS_HUMAN_ANALYSIS`. No such analysis is pre-authorized by this review.

