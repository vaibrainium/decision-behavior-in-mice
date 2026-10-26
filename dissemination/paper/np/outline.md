<!-- np-contract
stage: S3 ; section: outline ; agent: np-architect ; version: v3
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021
numbers: N001, N004, N005, N006, N009, N010, N011, N012, N013, N016, N018, N019, N020, N021, N024, N025, N026, N027, N030, N034, N035, N036, N039, N040, N041, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066
sources: adelson1985spatiotemporal, bogacz2006physics, caballero2022rt, carland2016evidence, cisek2009decisions, douglas2006motion, hawkins2015discriminating, huk2005neural, hyafil2023temporal, kiani2008bounded, koay2020amplitude, luken2025parameter, marques2018mousev1, odoemene2018visual, okazawa2018psychophysical, palmer2005effect, pinto2018visualpulses, ratcliff2008diffusion, samonds2018motion, steinemann2024direct, stine2020differentiating, stine2023termination, stirman2016touchscreen, tsetsos2012timevarying, wiecki2013hddm, winkel2014early, yates2017functional, you2022dynamics, zhou2009time
-->
# Detailed paper outline

## Narrative contract

The paper asks whether a model-and-input pipeline selected by joint held-out prediction during ongoing noisy motion transfers to a separately randomized, strong transient perturbation. Control trials provide a relative comparison between the tested accumulator and rapid-forgetting implementations; pulse trials first establish a model-free directional behavioural effect and then reveal that neither tested pipeline reproduces its temporal response profile. The paper ends at that pipeline-level failure and does not assign it uniquely to sensory encoding, decision dynamics or response generation.

The mouse-specific literature gap is intentionally bounded: the retained search found established mouse continuous-RDK psychophysics, discrete visual-evidence accumulation, and visual choice/response-time diffusion modelling, but did not find their exact conjunction with randomized signed pulses and a frozen control-only model tested jointly against choice, response probability and response time. This is not a universal first-in-mice claim and must be refreshed before submission.

## Word budgets

| Section | Budget | Included in suggested 5,000-word main text? |
|---|---:|---|
| Introduction | 700 | yes |
| Results | 2,850 | yes |
| Discussion | 1,200 | yes |
| Title, abstract and impact statement | 230 | yes |
| **Main-text total** | **4,980** | **yes** |
| Materials and Methods | 3,400 | no; separately budgeted |
| Figure legends (Figures 1–5 and S6) | 1,650 | no; separately budgeted |

## Title and front-of-paper package

- Preferred indicative title: **Brief motion pulses expose limits of an evidence-accumulation model in mice**.
- Acceptable alternative: **Control behaviour and motion pulses place distinct constraints on decision models in mice**.
- Avoid verbs implying that pulses prove accumulation, reveal primacy, or locate a neural mechanism.
- Abstract: 175–190 words, no citations, with the central claim by sentence 3; include `{{N001}}`, `{{N016}}`, and the directional effect `{{N051}}` [95% CI `{{N052}}`–`{{N053}}`; Holm-adjusted `{{N054}}`], then state the temporal mismatch and withheld confirmatory timing test without overloading the abstract with diagnostic scores.
- Impact statement: 15–30 words, third person, emphasizing that held-out perturbations exposed a failure not visible from control-trial model selection.
- Retain explicit front-matter placeholders: `[MISSING: author list, order, affiliations and corresponding author]`, `[MISSING: funding and funder role]`, `[MISSING: author contributions]`, `[MISSING: competing interests]`.
- Retain `[MISSING: final AI-use disclosure wording after eLife policy recheck]` for the submission-stage disclosure rather than drafting venue language from memory.

## Introduction (700 words; four paragraphs)

1. **Framework and identification problem (160 words).** Introduce evidence accumulation as a useful account, then explain that accuracy and temporal weighting alone do not uniquely identify it (`C010`). Establish why joint choice/response-time prediction adds constraints (`C011`) and note that integration has outperformed tested extrema/snapshot models in several discrete-sample datasets without exhausting non-integration policies (`C015`). Sources: `stine2020differentiating`, `tsetsos2012timevarying`, `cisek2009decisions`, `okazawa2018psychophysical`, `ratcliff2008diffusion`, `palmer2005effect`, `winkel2014early`, `hyafil2023temporal`.
2. **Why perturbations help, and why timing is not self-interpreting (180 words).** Explain that brief motion perturbations can alter choice and response time, but efficacy depends on timing, commitment and policy (`C012`). Frame a pulse as a transfer test, not a direct readout of memory duration or primacy. Sources: `huk2005neural`, `kiani2008bounded`, `tsetsos2012timevarying`, `carland2016evidence`; mention the positive macaque context from `stine2023termination` and `steinemann2024direct` without implying equivalence to this mouse preparation.
3. **Mouse preparation and bounded gap (180 words).** Establish the three prior components separately: continuous noisy RDK discrimination (`C019`), visual accumulation with discrete flashes/towers (`C020`), and visual choice/RT diffusion modelling (`C021`). State only that the bounded search did not find the exact combination tested here. Sources: `douglas2006motion`, `stirman2016touchscreen`, `marques2018mousev1`, `samonds2018motion`, `pinto2018visualpulses`, `odoemene2018visual`, `koay2020amplitude`, `you2022dynamics`, `caballero2022rt`.
4. **Competing hypotheses, approach and preview (180 words).** State H1–H3 in compact form, identify randomized assignment and held-out control fitting as the key controls, and preview the answer: relative support for the tested accumulator on controls, a directional pulse effect, and failure of both tested pipelines to reproduce the pulse response distribution. Promise the failed gates and sensitivity limits explicitly.

## Results (2,850 words)

### Figure 1. The task provides joint choice, response-time and no-response constraints during scheduled motion perturbations (400 words)

- Full claim: `C002`.
- Establish the 10-mouse, 50-mouse-session reaction-time RDK task and rig-specific pulse schedules (`{{N001}}`, `{{N004}}`, `{{N009}}`).
- Separate the fixed `{{N010}}`-s analysis cutoff from task termination and report `{{N005}}` within-window responses and `{{N006}}` censored trials.
- Describe psychometric, response-time and no-response summaries without treating accuracy–RT relations as proof of accumulation or comparing rigs biologically.
- End by motivating explicit stimulus reconstruction and joint modelling.

### Figure 2. Stimulus reconstruction defines the model input while exposing replay assumptions beyond nominal coherence (420 words)

- Full claim: `C003`.
- Walk from recorded seed/task parameters to rig-specific replay, direction-opponent motion energy and calibrated model input.
- Show nominal-coherence tracking, persistent trial-specific variation and the reconstructed pulse transient; make stimulus-trial/seed denominators distinct from animal-level inference.
- State that the replay is not a frame-perfect display measurement, that UCLA frozen-frame and offset-redraw choices remain assumptions, and that filter delay is not neural latency.
- Keep the hidden-coherence association and its `{{N011}}`–`{{N013}}` values in Supplementary Figure S2 unless its scheduled-control sensitivity is resolved.

### Figure 3. Joint held-out control prediction favours the tested accumulator among the tested implementations (600 words)

- Full claim: `C004`.
- Define the tested accumulator and 20–200 s⁻¹ rapid-forgetting approximation, and state the held-out, control-only comparison before presenting fit-quality diagnostics.
- Report extrema-minus-accumulator `ΔNLL={{N016}}`; define the positive sign and the working score threshold as a Monte Carlo reference, not a population p value.
- Show component-selection context, final control fit quality, and systematic high-coherence error-RT/no-response misfits.
- Summarize recovery (`{{N018}}`–`{{N021}}`) and move full matrices/parameters to S3; poorly recovered or near-bound parameters receive no mechanistic interpretation.
- Interpret only as relative support within the tested pair, then bridge to the stronger out-of-condition pulse test.

### Figure 4. Randomized signed pulses redirect responses, with the cumulative contrast emerging mainly 0.5–2 s after logged onset (620 words)

- Full claim: `C005`.
- Begin with assignment and the common-support estimand; retain pre-onset responses and no-response trials to avoid outcome-conditioned labelling.
- Report the mouse-level directional effect `{{N051}}` percentage points [95% CI `{{N052}}`–`{{N053}}`; Holm-adjusted `p={{N054}}`], with `{{N055}}` trials in `{{N056}}` supported cells, including `{{N057}}` pre-onset responses and `{{N058}}` no-response trials.
- Decompose right, left and no-response components, and explain why pulse-vs-control arms use different supported cells.
- Report the pulse-aligned endpoint `{{N059}}` and the qualitative 0.5–2 s emergence; identify pointwise intervals and cumulative carry-forward.
- Interpret the result as a randomized directional behavioural effect, not persistence, a neural latency, or a timing-weight test.

### Figure 5. The tested model-and-input pipelines predict a different temporal profile from the observed pulse-associated response contrast (600 words)

- Sole figure headline: `C006`.
- Compare observed and predicted cumulative directional curves and window increments on identical rows/weights; label the group comparison descriptive because no paired model-minus-observed inferential test was run.
- Show that original, joint-gain and choice-best predictions place too much effect early and partly reduce it later; describe this as a temporal-profile mismatch, not overall reversal of pulse direction.
- Present `C009` only as a subordinate PSUIM6/PSUIM7 diagnostic supporting the `C006` pipeline-mismatch story; it does not share the figure headline. Held-out choice improvements `{{N063}}`, `{{N064}}` accompany remaining-objective costs `{{N065}}`, `{{N066}}` relative to the joint-gain solution.
- State that gain is weakly constrained in most other mice, the dense-mouse simulation uses limited Monte Carlo seeds, and legacy input-label issues remain visible.
- Conclude at the model-and-input-pipeline level; do not choose among sensory, decision and response explanations.

### Supplementary Figure S6. Failed predictive gates and inadequate sensitivity precluded the confirmatory timing test (210 words)

- Full claim: `C007`; this negative/inconclusive subsection is mandatory in the main Results even though its detailed panels are supplementary.
- Report original departures `{{N026}}`, `{{N027}}`, revised departures `{{N030}}`, `{{N034}}`, and RT-cell coverage `{{N035}}`, `{{N036}}` only with definitions.
- State strategy recovery as `{{N024}}`/20 extrema and `{{N025}}`/20 accumulator datasets correctly selected; this is inadequate discrimination, not evidence of equivalence.
- Report primacy-calibration detections `{{N039}}`, `{{N040}}`, `{{N041}}` at 10%, 20%, 40% decline and state that the confirmatory timing test was not run.
- Transition directly to the Discussion's scope boundary.

## Discussion (1,200 words; six paragraphs)

1. **D1—plain answer (200 words).** Answer the Introduction: controls favoured the tested accumulator, randomized pulses redirected responses, and the tested pipelines failed to transfer. State `C008` as the scope boundary: the result does not identify a unique sensory, decision or response process.
2. **D2—relation to the model-identification literature (220 words).** Reconcile relative control support with studies favouring integration and studies showing urgency/leak/policy dependence. Use `stine2020differentiating`, `hyafil2023temporal`, `hawkins2015discriminating`, `carland2016evidence`, `stine2023termination`, `steinemann2024direct`. Establish `C013`: perturbation discrimination depends on separability in the tested regime.
3. **D3—specific alternatives and technical limits (300 words).** Establish `C014`: sensory dynamics can create time-dependent weighting inherited downstream. Then address replay fidelity, frozen-frame/offset redraw, motion-energy geometry/filter choices, control misfit, legacy pulse labels, sparse RT likelihood in some mice, limited Monte Carlo seeds, near-bound/poorly recovered parameters, and rig/cohort confounding. For each, state what remains valid and the measurement or analysis that would resolve it.
4. **D4—what these data cannot decide (140 words).** No unique accumulation proof, no primacy/recency conclusion, no integration or memory time constant, no sensory/decision/motor localization, no biological site comparison, and no generalization of the two-mouse gain tradeoff.
5. **D5—implication and next experiment (190 words).** Make out-of-condition predictive transfer the broader lesson. Specify a next experiment combining photodiode-verified pulse delivery, synchronized display/response timing, multiple pulse amplitudes/timings, and an independent retention or gap manipulation; include neural measurement only as a localization route, not a requirement for the current behavioural conclusion.
6. **Conclusion (150 words).** Return to the thesis without p values: held-out control selection and perturbation transfer answer different questions, and the strong pulse revealed a concrete predictive limitation that control performance did not expose.

## Materials and Methods (3,400 words; mirror of Results)

1. **Animals, ethics and oversight (250 words).** `[MISSING: strain, sex, age, provenance, housing, water restriction/welfare monitoring, sample-size rationale, ethics bodies and protocol identifiers for both sites]`; `[MISSING: whether blinding was performed and at which stages]`.
2. **M1—Task, apparatus, schedules and analysis outcomes (450 words; mirrors Figure 1).** Task/rig hardware, training, randomization, pulse schedules, response timing, 5-s analysis cutoff, exclusions and analysis-set denominators. `[MISSING: training stages/criteria, allocation details, session inclusion/stopping rules, complete display/hardware records]`.
3. **M2—Stimulus replay and motion-energy input (450 words; mirrors Figure 2).** Replay provenance, causal filtering, calibration, hidden-coherence calculation, pulse/no-pulse counterfactual and documented acquisition/replay uncertainty. Include `C017`, supported by `adelson1985spatiotemporal`; do not let this precedent imply replay fidelity.
4. **M3—Decision models, likelihood, fitting, comparison and recovery (700 words; mirrors Figure 3).** Equations/parameters, fast-response mixture, censoring, quantile likelihood, optimization, five-fold cross-validation, control restriction, Monte Carlo threshold and recovery. Include `C016` (`ratcliff2008diffusion`, `palmer2005effect`, `bogacz2006physics`) and `C018` (`wiecki2013hddm`, `luken2025parameter`).
5. **M4—Randomized assignment-based pulse estimands (550 words; mirrors Figure 4).** Source-code assignment audit, trial identity, support cells/weights, directional contrast, pulse-vs-control construction, competing cumulative outcomes, subject-level intervals, Holm family and estimator simulation.
6. **M5—Frozen pulse predictions and exploratory diagnostics (500 words; mirrors Figure 5).** Frozen control parameters, original and cross-validated pulse gains, decomposition into response/choice/RT terms, common-row overlays, gain profiles and choice-versus-remaining-objective held-out scoring; label post-gate diagnostics exploratory.
7. **M6—Predictive gates, sensitivity and timing decision (300 words; mirrors S6).** Define the strict primary baseline and supplementary `L1U1V1Z0G1` leak-plus-urgency baseline used for the registered C007 gate outcomes; report original/revised gate rules, pulse-strategy sensitivity, decay calibration and the prespecified stopping decision that withheld the timing model.
8. **Statistics, reproducibility and availability (200 words).** Units of analysis, interval/test definitions, software/environment/commit records, data and code statements. `[MISSING: final environment lock and run commits; data/code repository, identifiers, access conditions and release timing]`; `[MISSING: whether blinding was performed and at which stages]`.

## Figure legends (1,650 words total)

- Figure 1, 220 words: task/schedule, panel denominators, individual mice, summary/error bars, analysis cutoff.
- Figure 2, 270 words: replay pipeline, stimulus-vs-mouse units, calibration and replay uncertainty.
- Figure 3, 280 words: model definitions, score sign, working threshold, held-out versus in-sample panels, recovery pointer.
- Figure 4, 330 words: estimand, `n` at animal/trial/cell levels, CI and Holm definitions, cumulative-curve scope.
- Figure 5, 330 words: title states `C006` alone; common-row overlays and descriptive group comparison; `C009` appears only as a subordinate two-mouse diagnostic with gain settings and objective decomposition.
- Figure S6, 220 words: gate rules, strategy sensitivity, decay calibration and explicit statement that the timing test was not run.

## End-matter plan (outside the main-text budget)

- **Acknowledgements:** retain `[MISSING: acknowledgements and contributor permissions]` until supplied by the authors.
- **References:** generate the bibliography only from verified keys in `np/ledger/sources.csv`; unresolved or unverified records do not enter the manuscript.
- **Data and software availability:** retain `[MISSING: final data/software availability statement, repository identifiers, access conditions and release timing]`.
- **AI disclosure:** retain `[MISSING: final AI-use disclosure wording after eLife policy recheck]`; authors review and approve the final wording.

## Primary claim placement audit

| Primary location | Claim IDs |
|---|---|
| Title/Abstract | C001 |
| Introduction | C010, C011, C012, C015, C019, C020, C021 |
| Results | C002, C003, C004, C005, C006, C007, C009 |
| Discussion | C008, C013, C014 |
| Methods | C016, C017, C018 |
| Figure legends | none; legends restate figure claims only |

All 21 approved claims have exactly one primary location. Repetition elsewhere is synthesis or cross-reference and must not be presented as a new claim.

## Mandatory omissions and explicit unresolved facts

- Do not claim a first dynamic visual decision task, first visual pulse experiment, first mouse accumulation result, first mouse RDK task, or first mouse visual choice/RT model.
- Do not report the tau-p pilot as a formal result unless a later approved claim and independent validation are added.
- Do not turn the failed/inconclusive S6 record into a null result for primacy or strategy equivalence.
- Keep authorship, animal/training/ethics details, funding/declarations, final execution environments, and data/code release information visibly `[MISSING: ...]` until supplied.
