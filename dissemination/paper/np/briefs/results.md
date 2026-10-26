<!-- np-contract
stage: S3 ; section: results ; agent: np-architect ; version: v2
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C002, C003, C004, C005, C006, C007, C009
numbers: N001, N004, N005, N006, N009, N010, N011, N012, N013, N016, N018, N019, N020, N021, N024, N025, N026, N027, N030, N034, N035, N036, N039, N040, N041, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066
sources:
-->
# Brief: results

Purpose (one sentence): Present the experiment, reconstructed input, control-only model comparison, randomized pulse effect, failed predictive transfer and mandatory negative calibration record in the order of Figures 1–5 and S6.

Venue constraints: words 2,850; past tense for findings and present tense for figure descriptions; exactly one full-claim subsection for each main figure in figure order, followed by the mandatory S6 subsection; every hard number uses a ledger token; interpretation limited to one sentence per results paragraph.

Reader question this section answers: What did the mice do, which tested model predicted controls better, what did randomized pulses do, and where did the fitted pipelines fail?

Paragraph plan:

| # | Move (from section-specs) | Content | Claims | Numbers | Sources | Figure |
|---|---|---|---|---|---|---|
| 1 | Figure 1 claim and design | State the task, cohort/session scale, rig-specific scheduled perturbations and three outcome constraints. | C002 | N001, N004, N005, N006, N009, N010 | own data: E003, E006, E008 | 1A–B |
| 2 | Figure 1 descriptive behaviour/confounds | Psychometric, correct/error RT and no-response summaries; distinguish analysis censoring from task termination and avoid rig biology. | C002 continuation | N005, N006, N010 | own data: E003, E008 | 1C–E |
| 3 | Figure 2 reconstruction | Seed/task replay, causal motion energy, rig calibration and persistent trial-specific evidence. | C003 | — | own data: E009, E027 | 2A–C |
| 4 | Figure 2 assumptions/confounds | Pulse response and labelled replay alternatives; frame-perfect display, offset redraw, screen geometry and neural-latency limits. Hidden-coherence results remain supplementary. | C003 continuation | N011, N012, N013 (supplement only) | own data: E004, E009, E027 | 2D–E; S2 |
| 5 | Figure 3 comparison | Define the two tested implementations and report the held-out control score with sign and working-threshold meaning. | C004 | N016 | own data: E019 | 3A–B |
| 6 | Figure 3 adequacy/recovery | Component context, final fit quality, remaining errors and recovery boundaries. | C004 continuation | N018, N019, N020, N021 | own data: E019, E023 | 3C–D; S3 |
| 7 | Figure 4 estimand and assignment | Define randomized assignment, common-support cells, equal-mouse weighting, retained pre-onset/no-response trials and directional contrast. | C005 | N055, N056, N057, N058 | own data: E024, E025 | 4A–B |
| 8 | Figure 4 effect | Report the subject-level effect, CI and Holm-adjusted test; decompose outcomes and qualify control comparisons. | C005 continuation | N051, N052, N053, N054 | own data: E025 | 4A–C |
| 9 | Figure 4 time course | Report endpoint and 0.5–2 s emergence; distinguish emitted-response timing, cumulative carry-forward and pointwise intervals from evidence persistence. | C005 continuation | N059 | own data: E026 | 4D |
| 10 | Figure 5 sole headline: pipeline temporal-profile mismatch | Compare observed and predicted curves/window increments on common rows and weights; label as descriptive and pipeline-level. C006 alone supplies the subsection and figure headline. | C006 | — | own data: E028 | 5A–B |
| 11 | Figure 5 subordinate diagnostic | Explain gain profiles and held-out choice-versus-remaining-objective tradeoff in PSUIM6/7; show weak gain identification elsewhere. C009 supports the C006 mismatch story but does not share its headline. | C009 | N063, N064, N065, N066 | own data: E028 | 5C–D; S5 |
| 12 | S6 failed gates | Report original/revised predictive failures and inadequate RT-cell coverage with their operational definitions. | C007 | N026, N027, N030, N034, N035, N036 | own data: E020, E021, E022 | S6A–C |
| 13 | S6 sensitivity and stopping rule | Report strategy recovery and primacy-calibration detections; state explicitly that the confirmatory timing test was not run. | C007 continuation | N024, N025, N039, N040, N041 | own data: E020, E022 | S6D–F |

Promises this section creates: The Discussion must separate relative control-model support from unique mechanism identification, explain why perturbation sensitivity is regime-specific, localize no processing stage without new measurements, and propose a resolving experiment.

Promises it must deliver: Every main figure has one claim-heading; S6 is visible in main text; model comparison and pulse effect use their correct units of inference; limitations that alter interpretation appear beside the result rather than only in Discussion.

Must include: Headings exactly parallel to the five main-figure claims; C006 as the sole Figure 5 heading and C009 only as a subordinate two-mouse diagnostic; `n` identified as mice, trials or cells; selection/testing distinction; pointwise-not-simultaneous interval wording; legacy-input and Monte Carlo limitations; explicit non-performance of the timing test.

Must not include: Hard-coded statistics; a population p value for N016; independent interpretations of score components; a paired significance claim for observed-minus-model profiles; “model reversal” when only the cumulative contrast partially declines; a null primacy result; strategy equivalence; unique sensory/decision/motor localization.

Known risks / reviewer bait: Figure 2 may overstate replay fidelity; Figure 3 mixes held-out model selection with in-sample fit quality; Figure 4's cumulative curve can be misread as an integration kernel; Figure 5's selected mice can be mistaken for a cohort claim; S6 can disappear editorially unless retained as a named main-text subsection.

Acceptance criteria (the reviewer instantiates these at commit time):

- Six subsections appear in the required Figure 1–5, S6 order and every heading is a full claim; Figure 5 is headed by C006 alone.
- C002–C007 and C009 each have one primary location and no unapproved result claim is introduced.
- Every statistic uses an existing N token and states its unit of analysis.
- Every null/inconclusive result is reported with its sensitivity limit.
- The final paragraph leads naturally to C008 without claiming where the pipeline fails.
