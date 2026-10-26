<!-- np-contract
stage: S4 ; section: methods ; agent: np-stats-reviewer ; version: r2
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C016, C017, C018
numbers: N001, N004, N005, N006, N009, N010, N016, N018, N022, N023, N051, N052, N053, N054, N055, N056, N057, N058, N059, N060, N061, N062, N063, N064, N065, N066
sources: adelson1985spatiotemporal, bogacz2006physics, luken2025parameter, palmer2005effect, ratcliff2008diffusion, wiecki2013hddm
-->
# Statistics criteria commitment: methods round 2

Sources used: `np/spine.md`, `np/briefs/methods.md`, `np/reviews/methods/criteria_stats_r1.md`, `np/reviews/methods/r1_stats.md`, `np/reviews/results/r1_stats.md`, and `review-rubrics.md` (no v2 draft seen).

Round 2 is unchanged in scope. Every round-1 criterion S1–S11 remains binding with its original P0/P1 thresholds; the table below makes the required preservation and the five issue-closure tests explicit. Corrections must use existing approved evidence. A new analysis, new claim, invented method detail or unregistered hard value is not an acceptable fix.

## Preserved round-1 criteria

| Original criterion | Round-2 preservation test | Regression severity |
|---|---|---|
| S1: estimands, populations and nesting | Every analysis declares its population/estimand; mice remain the independent group unit and trials/cells/sessions remain nested or descriptive. | P0 for pseudoreplication; P1 for unclear aggregation or `n` unit. |
| S2: assignment and pulse estimand | Pre-outcome scheduled assignment, supported mouse × session × signed-coherence × onset cells, smaller-arm cell weights and equal mouse weighting remain intact. | P0 for outcome-conditioned assignment/inclusion or unsupported pooling; P1 for incomplete audit/support/weight rules. |
| S3: pre-onset, no-response and censoring | Pre-onset responses and `no response by 5 s` remain assigned outcomes; cutoff/task termination, exclusions, historical labels and pseudo-onsets remain distinct. | P0 if conditioning/missingness changes the estimand; P1 for incomplete counts, reasons or sensitivity restrictions. |
| S4: joint observation model | Choice/response/censor mass, side-conditional RT bins, mixture, smoothing, sparse-cell rule and objective-versus-likelihood distinction remain operational. | P0 if an omitted term changes the fitted object; P1 for incomplete bin/mixture/objective specification. |
| S5: held-out control comparison | Control-only five-fold fitting/scoring, score sign, aggregation, Monte Carlo working threshold and selection-versus-adequacy distinction remain explicit and non-inferential. | P0 for leakage or a false p-value interpretation; P1 for incomplete split/threshold/aggregation rules. |
| S6: recovery and identifiability | Generator/candidate recovery, parameter limits, bounds and residual misfits qualify mechanism claims. | P0 if unrecovered parameters support mechanism or selection recovery disappears; P1 for missing generators, metrics, denominators or consequences. |
| S7: pulse-gain selection/testing | Frozen controls, common rows, training/held-out pulse-gain selection, separate objectives and exploratory status remain distinct. | P0 for data reuse/leakage; P1 for unclear split, objective, search or Monte Carlo precision. |
| S8: descriptive model–data timing | Observed/predicted curves use common rows/cells/weights and remain descriptive, cumulative and pointwise without an invented paired test. | P0 for invented inference or timing/localization claims; P1 for unclear alignment or descriptive status. |
| S9: C009 two-mouse scope | PSUIM6/7 remain selected informative mice, never representative of the cohort; weak identification elsewhere and Monte Carlo limits remain explicit. | P0 for cohort generalization; P1 for unclear selection, per-mouse evidence or precision. |
| S10: multiplicity, uncertainty and stopping | Holm family, raw/adjusted distinction, pointwise time-course intervals, mouse-level intervals, robustness, gate chronology and withheld timing test remain auditable. | P0 for uncorrected central multiplicity/hidden stopping or claiming the timing test ran; P1 for incomplete test/family/interval/amendment details. |
| S11: reproducibility and honest availability | Every Results analysis has figure-level input/code/command/environment/seed/output provenance; missing release, sample-size and blinding facts remain explicit. | P0 for invented provenance/availability or irreproducible central analysis; P1 for vague regeneration details/placeholders. |

## Required closure of round-1 issues

| ID | Round-1 issue | What must be present in v2 | REVISE if | BLOCK / P0 if |
|---|---|---|---|---|
| R1-M1 | Missing hidden-coherence Methods path | Existing historical control-labelled population/coherence restriction; ten mouse coefficients; coefficient estimation; shared-ratio/profile-interval procedure; one-sided signed-rank test against zero; paired signed-rank comparison; unadjusted status and scheduled-label caveat. | Any listed detail, test estimand or nesting fact remains ambiguous. | A new inferential method/result is substituted or the historical-label limitation is erased. |
| R1-M2 | Control CV and working threshold underspecified | Implemented within-mouse fold routine or complete deterministic/random algorithm and seed; per-mouse refitting; fold/mouse aggregation; rescoring seed count; exact numerical working-threshold/parsimony rule; explicit non-p-value meaning. | A knowledgeable reader still cannot reconstruct folds, aggregation or threshold. | Pulse outcomes enter baseline selection, folds leak, or threshold becomes population inference. |
| R1-M3 | Recovery design underspecified | Five generator and five candidate identities; ten mice × two replicates; synthetic generation/fitting/scoring procedure; exact held-out score-difference decision rule; hit/false-positive denominators; pooled-correlation and near-zero-generator caveats. | Any design dimension, rule, denominator or scope caveat remains missing. | Recovery is newly rerun/redefined, or unsupported recovery validates mechanism. |
| R1-M4 | Pulse-gain/choice-optimal workflow underspecified | Joint and choice-only training objectives; exact candidate/search rules; stored folds and held-out aggregation; CRN/seed scheme; distinction among original, joint-gain and choice-optimal objects; one-main-seed limitation for PSUIM6/7 and no direct dense-mouse MC precision estimate. | Selection/testing or seed precision remains vague. | Same outcomes/objective are reused as held-out validation, or a new gain analysis replaces the documented workflow. |
| R1-M5 | Test reporting and figure-level reproducibility incomplete | Named two-sided one-sample mouse-level t test; raw p versus Holm-adjusted p and three-test family; compact map from Figures 1–5/S6 to existing versioned inputs, scripts/commands, seeds, environments, commits/hashes and outputs; unresolved release/final-lock facts remain `[MISSING: ...]`. | Test/tailing/correction or regeneration map remains incomplete. | New hard values lack approved tokens/evidence, or commits, versions, repositories or availability are invented. |

## Round-2 decision rule

- PASS requires all five R1-M issues resolved, all S1–S11 protections preserved, valid contract/tokens, and no new P0/P1/P2 regression.
- REVISE if an existing P1 is only partly resolved or any new P1/P2 statistical/reproducibility issue appears.
- BLOCK if resolution genuinely requires a new human analysis or conflicts with approved evidence; label it `NEEDS_HUMAN_ANALYSIS`. No such analysis is pre-authorized by this review.

