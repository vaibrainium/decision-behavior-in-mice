# Paper story and figure arrangement — discussion draft

Date: 2026-10-23. Source snapshot: `84fedd7` plus the existing manuscript/review files. This document proposes a narrative and panel arrangement; it does not adopt a new scientific analysis or replace the historical protocol. eLife is the provisional journal target, with an expanded thesis version outlined below. Five main figures are an editorial proposal, not a journal requirement. Numerical captions retain the recorded A–E/G1 results; subsequent corrected-input comparisons and pulse-filter pilot results are not incorporated. Input-correction and pilot-specification commits `6b4cf2b` and `a5583fc` arrived during drafting and remain with the analysis coordinator.

Companion: [draft captions](figure_captions_story_2026-10-23.md). Provenance: [source records](story_sources_2026-10-23.json), [caption/paragraph claim records](story_claims_2026-10-23.csv). Evidence IDs below belong to this drafting package. Human verification is pending.

## The story I recommend

**Working title: Brief motion pulses constrain models of evidence accumulation in mice.**

Control-trial choices and response times favoured an accumulator over the tested rapid-forgetting strategy. Brief, randomly assigned motion pulses also shifted response direction, providing a separate behavioural perturbation result. The fitted accumulation models did not reproduce the time course of that effect: increasing pulse gain improved choices at the expense of response-time prediction in the two most informative mice. Together, these results support accumulation relative to a specified alternative during unperturbed behaviour, while exposing a limitation in the tested models' account of transient evidence. The pulse effect itself does not identify a unique mechanism or establish primacy. [claim:C101] [evidence:E101,E103,E104,E105,E106,E108,E110]

The organizing question is **whether a model that explains decisions during ongoing noisy motion also predicts the consequences of a brief, strong perturbation**. This preserves the earlier strategy-comparison objective and makes pulses central to the experimental argument. The two bodies of evidence have different roles: controls compare candidate strategies; pulses constrain their generalization and quantify the perturbation's behavioural influence.

The conceptual motivation is that familiar choice/RT signatures can be shared by integration and non-integration strategies. The Introduction should make that distinction briefly, then explain why this experiment combines explicit model comparisons with stimulus perturbations. [Stine et al., 2020](https://elifesciences.org/articles/55365) provides the relevant primary evidence; this is motivation, not a claim that the present experiment reproduces that study's full identification result.

**Poster-inspired opening:** start with the comparative motivation for studying visual decisions in mice using a task with a familiar random-dot-motion structure. Then ask whether similar-looking behaviour is explained by the same candidate computations and whether those models predict brief perturbations. The present study contains no direct primate comparison: cross-species mechanism equivalence is a motivation to investigate, not an established result. This restores the accessible biological opening of the SfN poster before introducing the model-validation question.

**Candidate closing sentence:** “Brief sensory perturbations revealed constraints on the temporal predictions of the fitted decision models that were not resolved by their control-trial performance.” This states the scientific contribution without assigning the failure to a particular sensory, decision or motor process.

Alternative title if the authors want the perturbation finding first: **Motion pulses redirect perceptual decisions and constrain accumulation models in mice.** Avoid titles claiming primacy, a measured integration time constant, or definitive independent pulse confirmation of accumulation.

## Key results and order of presentation

| Result section | What we can say now | Evidence and limitation | Main figure |
|---|---|---|---|
| 1. Mice discriminate motion under a brief-pulse perturbation design | Ten mice performed a left/right reaction-time task across 50 mouse-sessions. Both pulse directions and an explicit analytical response deadline define the subsequent comparisons. | E101. Rig/cohort differences are descriptive; 5 s is an analysis cutoff, not a shared task termination time. | 1 |
| 2. Trial reconstruction characterizes the input beyond nominal coherence | Replayed motion energy follows nominal coherence and contains persistent seed-dependent variation. Earlier analyses associate reconstructed bias with choices. | E102/E107. Acquisition/replay uncertainties remain; the hidden-coherence analysis still needs its scheduled-control sensitivity. A shared fitted weight near 0.5 is not a demonstrated population-wide discount. | 2 |
| 3. Control trials favour the tested accumulator over rapid forgetting | The integrator improves summed held-out control score by 345.7 NLL units; six mice exceed the working 10-unit difference and none favour extrema by that amount. Drift variability and a fast-response component improve prediction. | E103. Scores compare these implementations, not every strategy, and the summed difference is not a population p-value. All-trial fit quality retains systematic errors. | 3 |
| 4. Scheduled motion pulses redirect responses | The primary directional probability contrast is +5.84 percentage points, 95% t CI 1.80–9.89, ten mice, Holm-adjusted p = 0.019. Nine mice have positive estimates. The response-associated contrast grows mainly 0.5–2 s after onset. | E104/E105. Exploratory, common-support estimand. The time course concerns emitted responses; persistent cumulative differences do not locate neural integration or retention. | 4 |
| 5. A pulse gain does not reconcile choice and response-time predictions | The tested models produce an earlier directional contrast and a later partial decline. Choice-only and joint gain optima disagree in PSUIM6/7; held-out choice improvement comes with a larger RT/response-score cost. | E106/E110. The diagnostic curves are partly in-sample and use legacy inputs; effects are well constrained in only a subset of mice. The other tested leak/urgency baseline also shows the temporal mismatch. | 5 |

The main Results must also state that both original/revised predictive gates failed, the pulse-specific strategy comparison was inconclusive, and the confirmatory primacy test was withheld. These outcomes cannot disappear when the exploratory pulse result becomes clearer. Put the complete gate/calibration panels in the supplement and summarize their consequence in the main text immediately before the new diagnostic analysis (E108).

### Suggested Results headings

1. **Mice discriminate motion in a task with brief directional perturbations.**
2. **Stimulus reconstruction reveals persistent variation beyond nominal coherence.**
3. **Control-trial prediction favours accumulation over the tested rapid-forgetting strategy.**
4. **Brief motion pulses shift response direction.**
5. **Pulse responses reveal a mismatch in the models' temporal predictions.**

Keep the stimulus Methods compact in the Results. The causal evidence for a pulse effect comes from assignment and the matched behavioural comparison, not from the fidelity of any one ME reconstruction. The model interpretation does depend on that reconstruction. This distinction gives the paper a stable behavioural result even if the model input is subsequently refined.

## Main figures: one question per figure

### Figure 1 — What task and behaviour are being explained?

**Take-home:** the experiment supplies choice, response-time and brief-perturbation constraints.

| Panel | Proposed content | Construction/source |
|---|---|---|
| A | Compact head-fixed task/left–right lick schematic, joined to trial timeline | Borrow the poster Figure 1 pairing of left/right dot motion with the corresponding lick report, using an original schematic of the actual apparatus. Mark the 0.3 s minimum viewing and separate 5 s analysis cutoff. Do not copy the poster's 60 s stimulus bar as the analysis window. |
| B | Baseline coherence and positive/negative pulse schedules; separate small strips for UCLA and UW | Existing Fig. 1C plus A/B task audit. Show approximate scheduled durations and acquisition caveats; a pulse replaces coherence rather than adding a fixed 100 percentage points. |
| C | Control psychometric functions, individual mouse traces and equal-mouse summary | Existing Fig. 1D source; regenerate after control-mask reconciliation. Avoid fitting a new inferential model for illustration. |
| D | Correct/error RT summaries over absolute coherence, with mouse values visible | Existing behaviour code and final fit-quality data extraction; descriptive data only. |
| E | Fraction with no response by 5 s versus signed coherence | Existing Fig. 1F; use the explicit no-response label. |

Layout: task and pulse schedule across the top; three behavioural panels below. Move accuracy-versus-RT and full RT histograms to S1. Those curves describe behaviour but do not independently prove accumulation. Rig-specific schedules should be labelled; a prominent UCLA-versus-UW biological comparison is not supported.

### Figure 2 — What evidence does the reconstructed stimulus contain?

**Take-home:** nominal coherence is an incomplete description of the replayed evidence; explicit pulses are therefore useful controlled perturbations.

| Panel | Proposed content | Construction/source |
|---|---|---|
| A | Seed and task parameters → replay → direction-opponent ME | Original compact schematic; the filter image can be an inset or go to S2. |
| B | Mean calibrated ME versus programmed coherence, with per-trial spread | Existing Fig. 2D; preserve per-rig calibration and identify stimulus trials as the sampling unit. |
| C | Persistent trial-specific component on nominally identical control stimuli | Notebook 2.14 control-only quantities. Show deterministic example-selection rule and overall distribution; no response-conditioned pulse kernel. |
| D | Nominal and reconstructed hidden-coherence choice coefficients for every mouse | Notebook 2.14 existing analysis, explicitly labelled historical control subset until scheduled-control check is complete. Do not headline the pooled 0.5 weight or claim all mice discount noise. |
| E | Pulse-aligned ME response, showing the transient and labelled reconstruction alternatives | Existing Fig. 2E and B audit. Show original representation alongside tested UCLA alternatives; full replay validation in S2. |

Layout: three compact evidence-characterization panels above, coefficient and pulse-response panels below. This combines the old standalone ME and hidden-coherence figures and frees space for two pulse figures. If the hidden-coherence sensitivity changes the interpretation, retain A/B/C/E and move D to S2; the central paper story remains intact.

### Figure 3 — Which candidate explains control behaviour better?

**Take-home:** controls favour the tested accumulator, with explicit limits to fit quality and identifiability.

| Panel | Proposed content | Construction/source |
|---|---|---|
| A | Shared model diagram and difference between accumulation and rapid forgetting | ME input, bound crossing, fast-response mixture; show which component differs in the extrema approximation. |
| B | Per-mouse held-out control score difference: extrema minus accumulator | Saved control-CV fits and `scripts/ddm/compare_strategy.py`. Zero reference; 10-unit line labelled a working threshold, not a confidence interval. |
| C | Per-mouse changes when removing sv/fast guesses or adding leak/urgency | Control-only selection report and saved scores. Consistent sign: positive means the reference accumulator predicts better. |
| D | Compact observed/model control summary: choices, correct/error RTs and no response by 5 s | Final all-trial fits evaluated on controls. Label this as in-sample fit quality, separate from B/C. Show equal-mouse summaries with individual values; complete ten-mouse grid in S3. |

Layout: model schematic plus large strategy comparison on top, component comparison and fit-quality strip below. Parameter values belong in a supplementary table, not a row of main-figure bars. Avoid two hand-picked “representative” mice as the only demonstration of adequate control fits.

### Figure 4 — What do pulses do to behaviour?

**Take-home:** pulse assignment changes response direction, and its behavioural expression can be quantified over time without assuming a DDM.

| Panel | Proposed content | Construction/source |
|---|---|---|
| A | Directional effect in each mouse and group mean/95% CI | C `per_mouse.csv`, `group.csv`, `coverage.csv`; adapt `behaviour_primary_components.png`. |
| B | Separate changes in right, left and no-response probabilities | Same C tables; make clear that these sum to zero and that the directional statistic is (ΔR−ΔL)/2. |
| C | Positive versus control and control versus negative directional contrasts | `behaviour_pulse_vs_control.png`; retain both estimates/intervals and their distinct matched populations. |
| D | All-scheduled cumulative directional contrast versus time since pulse | D `contrast_curves_group.csv.gz`; individual curves faint, mean and pointwise 95% t interval emphasized. Pool onset strata for the main panel. |

Layout: A/B on top; C compact lower left; D large lower right. Keep pulse-onset comparisons, onset eligibility, full left/right/no-response curves and common-latency summaries in S4. They must not turn into an implied early-versus-late primacy test. Make this figure readable without the model section.

Poster-inspired production option: add a small, explicitly illustrative pulse-direction inset beside A to explain the sign of the directional contrast before presenting individual mice. If a psychometric display is preferred, construct it from audited scheduled assignments with its conditioning and denominators stated; the old pooled early/middle/late curves cannot be copied into this figure. A new empirical inset needs a checked source table and revised caption; it is not part of the current numerical caption.

### Figure 5 — What does the model fail to predict about pulses?

**Take-home:** pulse amplitude alone does not reproduce the observed combination of direction and response timing in the tested baselines.

| Panel | Proposed content | Construction/source |
|---|---|---|
| A | Observed cumulative directional contrast versus original, stored joint-gain and choice-best-gain predictions | E curves on identical rows and weights. Keep gain 10/20 demonstrations in S5 so they do not compress the scientifically relevant curves. |
| B | Directional increments over 0–0.5, 0.5–1, 1–2 and 2–4.58 s | `e4_model_vs_D_summary.csv`; label increments rather than rates. Show uncertainty and the model gain setting. No significance inferred from separate model/data intervals. |
| C | Choice and joint objective profiles in PSUIM6/7 | E `e2_e3_profiles.csv.gz`/`e3_optima.csv`. Separate subaxes if needed to prevent the larger RT score flattening the choice curve; no misleading dual axis. Label these two mice as selected diagnostics, not representative population examples. |
| D | Held-out choice benefit and remaining objective cost when using choice-optimal gain | E `e3_optima.csv`, summed across held-out folds. Show all mice with PSUIM6/7 identified, so the restriction of strong evidence to those mice is visible. |

Layout: A/B across the top; gain profiles and held-out costs below. Explain the original/revised failed predictive gates in the main Results and point to S6. The curves in A/B are exploratory diagnostics, not a new confirmatory timing test. A negative late increment is a partial reduction of the earlier positive cumulative contrast; it does not imply an overall negative pulse effect.

## Supplementary allocation

| Display | Content | Why it belongs here |
|---|---|---|
| S1 | Trial inclusion/assignment audit; scheduled-label corrections; design asymmetry; RT distributions and descriptive accuracy–RT curves | Establishes design and exclusions without overloading the experimental introduction. |
| S2 | Filters/calibration, full replay audit, acquisition uncertainties, rounding shift, hidden-coherence model and sensitivity | Makes the stimulus assumptions inspectable; includes unresolved issues rather than treating reconstruction as ground truth. |
| S3 | Complete ten-mouse final-fit grid, Monte Carlo scoring checks, model/parameter recovery, parameter table | Supports the strategy comparison and documents misfits/near-bound estimates. |
| S4 | Pulse robustness, all outcome curves, onset eligibility, sham alignment, matched-seed limits and G1 estimator calibration | Supports the behavioural effect and defines the scope of null findings. |
| S5 | Full gain profiles and RT-term coverage in all mice; leak/urgency baseline diagnostics | Shows where the model diagnosis is strong or poorly constrained. |
| S6 | Original/revised gate results; pulse strategy comparison; strategy sensitivity and primacy calibration as separate panels | Preserves the original scientific record and why primacy was not tested. |
| Conditional S7 | Pulse-filter pilot, if authorized and completed | A diagnostic pilot is supplementary unless full validation makes a stronger main-text result warranted. No placeholder positive result. |

These are content groups, not a promise that every group fits on one supplementary page. A complete recovery figure may need its own number under the eventual journal format.

## Display conventions and production decisions

- Keep colours consistent by meaning: data black/grey; rightward and leftward assignment distinguished by both colour and symbols; model identity distinguished by line style. Do not reuse a colour for rig in one panel and pulse direction in the next.
- For behavioural group inference show individual mice and name 95% Student-t intervals. Pointwise curve intervals are not simultaneous bands. If a descriptive panel uses SEM instead, state that locally; do not imply a universal error-bar convention across every panel.
- Stimulus-only spread is across reconstructed trials/seeds; it is not biological replication. State this in Figure 2.
- Use `P(no response by 5 s)`, not an axis suggesting every censored trial has an observed late response. Distinguish the fixed motion-onset deadline from a common pulse-aligned horizon.
- Keep the original input version identifiable in model figures. Corrected behavioural labels and legacy fitted inputs are different analysis sets; do not overlay them without an explicit common-row comparison.
- Final figures should be redrawn from saved tables, with editable/vector lines and a source-data table. The current PNGs are source figures for the arrangement, not ready-made panels to crop without checking labels and uncertainty.
- No journal-specific dimensions, maximum figure count or export compliance are claimed here. Final sizing follows the selected venue's current instructions.

## What to retain and update from the SfN 2025 poster

Source: [supplied poster](<../poster/SfN Poster - 2025.pdf>), one page, checked 2026-10-23 (E114). The PDF's text and embedded figure images were inspected locally. The poster is a record of earlier presentation, not a replacement for the current evidence sources.

**Retain the communicative strengths:** a concrete task illustration, a simple psychometric introduction, visible pulse-coherence traces, and a progression from behaviour to the computation being tested. Keep the comparative motivation in the Introduction and thesis background. Main figure headings should state a finding or question in plain language. The paper's new motion-energy and model-validation material should explain the behavioural experiment rather than bury it.

| Poster element | Paper/thesis treatment now |
|---|---|
| Title and highlights claim accumulation strategies similar to primates | Retain comparative task motivation; report the preference between the tested mouse models. This dataset does not establish cross-species mechanism equivalence. |
| Figure 1: motion direction, lick report and trial sequence | Reuse the conceptual arrangement in the new Figure 1. Redraw the apparatus and distinguish task events from the analytical deadline. |
| Figure 2A: pooled psychometric curve | Preserve its visual simplicity while showing mouse-level variation in the paper. Replace the printed session count with the audited mouse-session count and compute each panel's trial denominator from its actual mask. The notebook hard-codes the total responded-trial count inside a control-only plot. |
| Figure 2B: accuracy plateaus with response time, titled as bounded accumulation | Retain as a descriptive supplementary display if useful. The paper's strategy evidence is the held-out candidate comparison, not this curve alone. |
| Figure 3: early/middle/late psychometric shifts interpreted as primacy | Preserve the intuition that pulse direction can shift behaviour; use the corrected assignment-based analysis for the quantitative result. Old timing bins and response-conditioned labels cannot supply a new primacy claim. Main Figure 4 now emphasizes directional effects and their response time course. |
| Figure 4: alpha changes, nonsignificant beta differences | Do not transfer its numerical significance or infer unchanged sensitivity from a nonsignificant slope test. Re-establish the fit's parameter definitions and analysis population before any reuse. The paper can express the behavioural result directly in response probabilities. |
| Figure 5: WFV inactivation | Remains outside this paper under the earlier scope decision. In a thesis it could provide a transition to a separately documented circuit chapter; the poster alone is insufficient evidence for that chapter's conclusions. |

**Specific production corrections:** the poster Figure 3 legend maps blue to rightward pulses and red to leftward; Figure 4 reverses those labels. This verifies inconsistent visual encoding, not which underlying analysis is wrong. Regenerate from named conditions with one direction palette across figures. Poster Figure 2's caption also says “negative: positive”; the intended signed-coherence convention is negative = leftward. Verify all sign labels against the current trial contract.

**Thesis opportunity:** use a short account of how the original early-pulse observation motivated stricter tests. Explain the move from a suggestive timing pattern to assignment audits, predictive checks and sensitivity calibration. Identify the poster interpretation as historical and the follow-up as exploratory; readers should not have to infer which conclusion is current. A small “original question / completed test / current conclusion” table is more useful than repeating every historical plot.

The poster's reference list is a set of literature leads. Its claims about the cited papers require checking the primary sources before they enter the Introduction; no citation has been newly validated in this poster-review pass.

## Paper and thesis versions

**Author preference, 2026-10-23:** eLife is the provisional journal target; the thesis should extend the account to explain what worked, what failed and what remained unresolved. Maintain the same evidence and conclusions in both versions. Expand the rationale and diagnostic evidence in the thesis, while retaining every limitation that materially affects the paper's claims.

### Provisional eLife format

Use the Research Article format. eLife suggests a main text of about 5,000 words or less, excluding Methods, references and legends, with no limit on display items. Its normal abstract length is 150–200 words. Figure supplements attach to individual main figures; legends should specify sample sizes, uncertainty, tests and relevant processing, with detailed information in source data where necessary. These instructions were checked on 2026-10-23 in the [official author guide](https://elife-rp.msubmit.net/html/elife-rp_author_instructions.html).

The five-figure arrangement above is an editorial recommendation. Map S1 to Figure 1 supplements, S2 to Figure 2, S3 to Figure 3, S4 to Figure 4, and S5/S6 plus any completed S7 to Figure 5. Split these content groups into readable individual supplements when needed; a single numbered group need not become a crowded composite.

My editorial assessment is that the strongest submission argument is the value of controlled sensory perturbations for evaluating models that describe unperturbed behaviour. Selection for review remains uncertain: the paper needs to explain what this particular experiment establishes beyond a model's imperfect fit. Foreground the randomized behavioural effect, the joint choice/response-time constraint, and the restricted scope of the mechanistic inference. Do not frame model inadequacy by itself as a general discovery about all accumulation models.

eLife selects submissions for review and publishes reviewed papers with an assessment and public reviews as Reviewed Preprints. A later Version of Record is an author decision. This is a venue choice for later discussion, not authorization to submit or post the work. See [eLife's publishing process](https://elifesciences.org/about/submit-your-research).

### Thesis chapter structure

Organize the chapter around scientific questions and the decisions they motivated. A short development timeline can orient the reader; detailed optimizer histories and implementation logs belong in an appendix or the repository.

| Chapter section | Purpose and expansion beyond the paper |
|---|---|
| 1. Why perturb sensory evidence during a decision? | Explain the distinction between showing that evidence influences behaviour, comparing candidate strategies, and identifying the temporal weighting mechanism. State the original aims and distinguish later exploratory questions. |
| 2. Task design and behavioural performance | Develop Figure 1 into a fuller account of pulse assignment, timing, response deadlines, cohort differences and inclusion rules. Explain the intended logic of the perturbation. |
| 3. Reconstructing the evidence available to the animal | Give stimulus reconstruction and hidden-coherence analyses separate space if useful. Present replay assumptions and acquisition uncertainties alongside their validation, including any sensitivity analyses that are actually completed. |
| 4. Building and checking the candidate models | Explain the common model, component comparisons, control-strategy comparison, recovery and parameter limitations. Promote the full fit-quality and recovery displays from supplements when they help the reader assess the inference. |
| 5. What the pulses establish behaviourally | Present the randomized directional effect and all-scheduled response time course. Explain the estimator and its calibration; distinguish this evidence from a measurement of a neural integration time constant. |
| 6. Model development, predictive failures, and limits of inference | Develop the failed gates, pulse-gain diagnostics, choice/response-time tension and sensitivity of the planned primacy procedure. Explain why each result changed the next defensible question. |
| 7. Targeted follow-up and synthesis | Include a completed pulse-filter pilot only with its actual validation status and input version. Bring together the supported claims, unresolved alternatives and lessons for interpreting pulse experiments. The chapter does not depend on a successful extension or additional data collection. |

The thesis can reuse the paper's main results and captions while showing supporting analyses in more space. Final caption facts, sample definitions and uncertainty must agree across versions. Put longer explanations of modelling choices in the surrounding chapter text. Check institutional chapter/reuse requirements when preparing the thesis; none have been supplied here.

### How to report unsuccessful approaches

For each substantial attempt, give the **question, test, result, warranted conclusion and remaining uncertainty**. Include it when it changes the scientific interpretation, validates a method, or explains a consequential decision. Routine troubleshooting need not receive equal space.

| Type of outcome | Existing example | Appropriate interpretation |
|---|---|---|
| Predictive failure | Original and gain-calibrated gates; the gain tradeoff in the informative mice | The specified model and input pipeline do not meet the relevant predictive requirement. Keep the failure's domain explicit; it does not reject every accumulation mechanism. |
| Inconclusive or insufficiently sensitive test | Pulse strategy comparison and calibration of the planned primacy procedure | The procedure cannot resolve the intended distinction under the tested conditions. Do not convert this into evidence that primacy is absent, or that every analysis of these pulse data lacks power. |
| Weakly identified quantity | Poor recovery of the guess delay; weak pulse-gain constraints in several mice | Explain which quantities can support interpretation and which are nuisance parameters or uncertain estimates. Cross-simulation recovery is not a within-mouse confidence interval. |
| Technical correction or unresolved measurement issue | Scheduled-label corrections, censored pulse directions and replay timing assumptions | Document the cause, input version and demonstrated impact. A correction is a provenance issue; its effect on biological conclusions must be checked rather than presumed. |
| Unfinished exploratory extension | The pulse-filter pilot while evaluation is pending | State the hypothesis and current status. Report its outcome only after the coordinator's checks; any mechanistic interpretation remains conditional on validation. |

All examples refer to evidence already indexed in this document and its source manifest; this addition introduces no new numerical result. The failed predictive gates and reason the confirmatory primacy test was not run remain visible in the paper's main Results. The thesis supplies the fuller reasoning and supporting displays.

## What remains before these captions become final

**Required for the selected figures:** reconcile the Figure 1 control mask with the new assignment audit; complete or explicitly limit the Figure 2 scheduled-control sensitivity; regenerate the main layouts with their intended uncertainty; carry over the legacy-input caveat or update the model comparisons when corrected-input results arrive; inspect every final plot against its caption. Corrected-input comparisons and the model pilot remain with the analysis coordinator.

**Required for the manuscript:** animal/ethics/training details, actual exclusion decisions and author declarations remain missing in the draft. Use the [ARRIVE 2.0 guidance](https://arriveguidelines.org/arrive-guidelines) to track these facts; no compliance claim is made by this outline.

**Optional for the central story:** a new mechanism extension, a unique neural time constant, or a resolved primacy test. The current paper can report a behavioural perturbation and a quantitative limitation of specified models without these outcomes.

## Points to settle with the authors

The main editorial decision is whether the title foregrounds **testing accumulation with pulses** (recommended) or **the behavioural pulse response itself**. The scientific claim stays the same. The second is whether the hidden-coherence coefficient panel earns main-figure space after its sensitivity check; its methodological relevance should not turn a tentative population-discount claim into a headline. eLife is now the provisional target; final journal selection and institutional thesis requirements remain to be settled.

Workflow note: the repository's scientific-writing and scientific-visualization skills informed this drafting package. Procedural reference, metadata checked 2026-10-23: Kassis T, Agarwal V, He Y, Patel D, Brueckner AM (2026), [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065). This is workflow attribution, not evidence for the experimental conclusions.
