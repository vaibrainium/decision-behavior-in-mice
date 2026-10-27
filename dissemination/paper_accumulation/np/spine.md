<!-- np-contract
stage: S1 ; section: spine ; agent: np-architect ; version: v2
thesis: "In mice performing a reaction-time random-dot motion task, a bounded accumulator with drift variability and fast guesses predicted held-out control-trial choices and response times better than a tested rapid-forgetting model, in a comparison not yet shown to identify rapid forgetting, whereas brief motion pulses moved choices far more than either control-fitted model predicted, which left the temporal weighting of evidence unresolved."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014
numbers: N001, N004, N005, N006, N014, N015, N016, N017, N018, N019, N020, N021, N022, N024, N025, N026, N027, N029, N030, N031, N032, N033, N034, N035, N036, N037, N038, N039, N040, N041, N042, N043, N044, N047, N051, N052, N053, N054, N055, N063, N064, N065, N066, N071, N072, N073, N078, N079, N082, N083, N088, N092, N095, N096, N097, N098, N105, N107, N108, N109, N110, N111, N112, N113, N114, N115, N116, N117, N118
sources: stine2020differentiating, hyafil2023temporal, okazawa2018psychophysical, levi2018strategic, zhou2009time, brunton2013rats
-->
# Paper spine

The spine anchors the whole paper against drift. Every agent reads it first, and every agent output
copies the THESIS line verbatim into its np-contract header. Everything between LOCK-START and
LOCK-END is frozen at gate G1. Changing it needs an entry in decisions.md, human approval, and
`np.py lock-spine` again.

v2 (2026-10-26) answers `np/reviews/spine_challenge.md`; point-by-point response in `np/reviews/spine_response.md`.
No new analysis was run or assumed. Wording that depends on pending analyses is given in the conditional-thesis
table below the lock, not inside it.

<!-- LOCK-START -->
THESIS: In mice performing a reaction-time random-dot motion task, a bounded accumulator with drift variability and fast guesses predicted held-out control-trial choices and response times better than a tested rapid-forgetting model, in a comparison not yet shown to identify rapid forgetting, whereas brief motion pulses moved choices far more than either control-fitted model predicted, which left the temporal weighting of evidence unresolved.

## Story (OCAR)
- **Opening (problem space, audience):** Evidence accumulation is the standard account of random-dot motion decisions, but psychometric and chronometric curves alone can also be produced by non-integrating strategies such as rapid forgetting or extrema detection (stine2020differentiating), and accumulators differ in how they weight evidence over time (primacy, recency or flat; levi2018strategic, okazawa2018psychophysical). Integration has been favored over extrema or snapshot models in rats (brunton2013rats, hyafil2023temporal), and separating them with response times is the approach stine2020differentiating proposed. The contribution here is narrow: mice, continuous random-dot motion, free response times, and a joint held-out fit of choices and response times, plus a prespecified attempt to measure temporal weighting with brief pulses. Audience: decision-making and mouse-vision researchers who model choices and response times.
- **Challenge (the specific question; the hinge of the paper):** When mice discriminate continuous noisy motion, does joint held-out prediction of control-trial choices and response times favor a bounded accumulator over a tested rapid-forgetting model, which accumulator components does that prediction need, how far can this comparison identify the strategy, and can brief motion pulses resolve temporal weighting?
- **Action (what was done, in one line per experiment):**
  1. Ten head-fixed mice on two rigs performed a reaction-time random-dot direction task with control trials and scheduled ±100% coherence pulses (Fig 1).
  2. Each trial's stimulus was replayed and filtered into motion energy, which entered every model through a linear front end (Fig 2).
  3. A bounded accumulator and a rapid-forgetting model (leak 20–200/s, applied to the filtered motion-energy signal) sharing the same input, bounds and fast-guess mixture were compared by five-fold cross-validation on control trials; a free-leak fit to all control trials described the fitted leak (Fig 3).
  4. Two prespecified within-trial checks were set beside that comparison: a response-aligned fluctuation-kernel test on control trials and a pulse-based strategy statistic (Fig 3—figure supplements).
  5. Nested variants (drift variability, fast guesses, guess bias, leak, urgency) were compared on held-out control trials and checked by model recovery of the accumulator variants; an exploratory compressive front end was compared on control trials and stopped before propagation (Fig 4 and supplement).
  6. The behavioral effect of scheduled pulse direction was estimated within matched cells with mice as the unit (Fig 5).
  7. The prespecified primacy pipeline was applied: observed versus predicted pulse effects, predictive gates, a gain revision, timing calibration under 10–40% simulated decay, and a synthetic control-trial fluctuation-kernel check (Fig 6).
- **Resolution (the answer, which must answer the Challenge):** With the linear motion-energy input, held-out control prediction favored the tested accumulator over the tested rapid-forgetting model in six of ten mice at a working 10-unit threshold, none favored rapid forgetting, and four did not distinguish them. This ranks two models that both misfit parts of the data. Model recovery covered only accumulator variants, so whether the comparison would select rapid forgetting when rapid forgetting generated the data is untested. A descriptive free-leak fit placed leak at 0–1.1/s, but leak recovery was too weak to exclude leak of a few per second. Under the parsimony rule the accumulator needed drift variability and fast guesses with a free guess bias; adding leak, or leak with urgency, improved the summed held-out score only within Monte Carlo noise, and an exploratory compressive front end that improved held-out prediction in two mice was not carried into these comparisons. The two prespecified within-trial checks did not favor the accumulator: the response-aligned kernel test found that neither model fit, and the pulse strategy statistic did not distinguish the models with a design whose sensitivity was 1/20 and 0/20. Scheduled pulse direction shifted response direction by about 6 percentage points, and the pulse effect on choice was about ten times the accumulator's prediction (about 0.3 against 0.03 logit; the rapid-forgetting prediction was similarly small), including at 0% coherence. The control-fitted model therefore failed its original and gain-revised predictive gates, the timing test was not run, and calibration and synthetic kernel checks showed no sensitivity to 10–40% primacy, a limit identified before pulse outcomes were inspected. Temporal weighting remains undetermined, not shown to be flat.

## Competing hypotheses and what each predicts
| Hypothesis | Prediction | Which figure decides it |
|---|---|---|
| H1: Control-trial decisions reflect bounded accumulation with a long time constant | The accumulator gives a lower held-out control score than the rapid-forgetting model in most mice, and the comparison selects rapid forgetting when rapid forgetting generated the data. | Figure 3, conditional on rapid-forgetting-generated recovery of the control comparison (not yet run). Without it, Figure 3 ranks the two implementations only. |
| H2: Control-trial decisions reflect rapid forgetting (extrema-like; leak 20–200/s on filtered motion energy) | The rapid-forgetting model matches or beats the accumulator on held-out control trials. A free-leak fit settling at high leak would support H2, but a low fitted leak weakly opposes it because leak recovery is poor. | Figure 3, under the same condition as H1. The pulse strategy statistic cannot decide H1 vs H2 (sensitivity 1/20 and 0/20). |
| H5: The control comparison reflects which first-passage-time family fits the response-time distribution, censoring and fast-guess allocation, not how momentary evidence is used | Rapid-forgetting-generated data are also scored as favoring the accumulator; the advantage sits mainly in the censoring or empty-prediction terms; it survives replacing motion energy by nominal coherence; it changes when fast guesses are removed. | Undecided. Requires the analyses listed in `np/reviews/spine_response.md` (F1a–c, M5b). Stated in Results and Discussion as an open alternative. |
| H3: The accumulator needs components beyond drift and bound (drift variability, fast guesses, leak, urgency) | Removing a needed component worsens held-out control prediction beyond the working threshold in most mice; adding an unneeded one improves it by less than Monte Carlo noise or in few mice. | Figure 4, read with its recovery limits and with the linear front end. |
| H4: The accumulator weights early evidence more (primacy) vs late or equal evidence (recency/flat) | Under primacy, middle pulses shift choices less than early pulses once the model predicts pulse trials adequately. | Undecided. Figure 6 shows the pulse effect far exceeded prediction, the deciding test was not reached (gates failed), and the design would not have detected 10–40% decay. |

## Key control (rules out the boring explanation)
The boring explanation for H1 is that the accumulator wins through extra flexibility, through structure leaking in from pulse trials, or through optimizer failure in the rapid-forgetting fits. The comparison addresses these only in part: (i) both models share the same linear motion-energy input, bound structure, fast-guess mixture and response mapping and differ only in leak; (ii) selection used five-fold cross-validation on control trials as labeled in the analysis input, so pulse-trial choices and response times did not enter selection, except that 38 genuine pulse trials, all without a response by 5 s and mislabeled as controls, remain in these fits (Methods); (iii) a free-leak fit (0–200/s) to all control trials, which could reach the rapid-forgetting range, settled at low leak in every mouse; this is an in-sample optimizer check, not a cross-validated test; (iv) model recovery shows which accumulator components the procedure can and cannot identify. **Missing control, stated as such:** recovery of the control comparison with rapid-forgetting-generated data. Until it exists, the comparison is reported as a ranking whose ability to identify rapid forgetting is untested (H5 open). For the pulse effect, pulse direction was scheduled before the outcome and the primary contrast compares positive and negative assignments within mouse × session × signed-coherence × onset cells, retaining pre-onset responses and no-response trials. Assignment is described as scheduled, not randomized, until session-pinned task-code provenance is supplied (first-version RM2). None of these controls separates sensory, decision and response contributions to the pulse response.

## Figure plan (one claim per figure)
| Fig | Claim it supports (claim IDs) | Data source (path) | Status |
|---|---|---|---|
| 1 | Task and behavior: trained mice performed the reaction-time random-dot task; choices, response times and no response by 5 s depended on motion coherence (C002). | Reuse `/src/dissemination/paper/figures/fig1_task_behaviour_2026-10-26_v2.*` and its `_source_*.csv`. | Exists; reuse as is. No learning panel. |
| 2 | Reconstructed motion energy defines the per-trial model input (C003). | Reuse `/src/dissemination/paper/figures/fig2_stimulus_reconstruction_2026-10-26_v6.*` and sources. | Exists. Main-text status conditional: stays main only if motion energy is shown to beat nominal coherence on held-out control trials (pending analysis F1c); otherwise A–C move to a Methods figure or Figure 3—figure supplement and D–E to a supplement. |
| 3 | Held-out control prediction ranked the tested accumulator above the tested rapid-forgetting model, in a comparison whose ability to identify rapid forgetting is untested (C004, C005, C011). | Panels A–B from `/src/dissemination/paper/figures/fig3_control_models_2026-10-26_v5.*` (`_source_strategy.csv`); panel C free-leak fit from `/mnt/data/processed/ddm/fits_guess_fast_only_leak0-200` (N112), labeled descriptive with the leak-recovery limit; panel D rapid-forgetting-generated recovery confusion matrix [MISSING: analysis F1a not run]. Figure supplement 1: response-aligned kernel verdict (C013) from `/mnt/data/processed/ddm/fluctuation_kernel_observed_2026-10-26.csv` [MISSING: panel script]. Figure supplement 2: pulse strategy statistic and its sensitivity (C011; S6 v2 panel D). | Partly exists; panel D pending analysis. |
| 4 | Needed accumulator variant with the linear front end: drift variability and fast guesses with free guess bias; leak and urgency not needed under the parsimony rule; recovery limits (C006, C007). | fig3 v5 C (`_source_components.csv`) and D (`_source_fit_quality.csv`); guess-bias panel (analysis log 5.8, `compare_guess_forms`); recovery panel from `/mnt/data/processed/ddm/recovery/summary_parameters.csv` and `summarize_recovery`. Figure supplement 1: amendment 7 front-end comparison (C014) from `ddm/mc_noise_front_end/` (analysis log 5.13). | Partly exists; new panels from existing outputs. |
| 5 | Scheduled pulse direction shifted response direction (C008). | Reuse panels A–C of `/src/dissemination/paper/figures/fig4_pulse_behaviour_2026-10-26_v2.*`; panel D (cumulative contrast) to Figure 5—figure supplement 1. | Exists; rebuild without D or reuse with D captioned as emitted-response timing only. |
| 6 | Temporal weighting could not be resolved: pulse effects exceeded the control-fitted predictions about tenfold, the original and gain-revised gates failed, the timing test was not run, and calibration and synthetic kernel checks showed no sensitivity to 10–40% primacy (C009, supported by C010). | New panel A: observed versus predicted pulse effect for both control-fitted models, including 0% coherence (log 5.10–5.11; `dissemination/reports/primacy_predicted_pulse_effects_17511ca.csv`, `primacy_revised_calibration_by_{coherence,mouse}.csv`) [MISSING: panel script]; panels from `/src/dissemination/paper/figures/figS6_gates_sensitivity_2026-10-26_v2.*` A–C, E–F; synthetic kernel panel from `/mnt/data/processed/ddm/fluctuation_kernel_power_v2.csv`. Figure supplement: `/src/dissemination/paper/figures/fig5_model_mismatch_2026-10-26_v3.*` panels C–D (gain tradeoff; C010). | Partly exists; two new panels. |

Failed original and gain-revised gates, the unrun timing test, timing calibration, the insensitive pulse strategy comparison, the response-aligned kernel verdict and the stopped front-end comparison are mandatory reported content (C009, C011, C013, C014), not omitted outcomes.

## Scope: what this paper will NOT claim
- It will not claim that mice learned the task or describe training; Figure 1 shows performance only.
- It will not claim that the data show accumulation, identify the mouse's algorithm, or rule out extrema detection or any other non-integrating strategy. The comparison ranks two tested implementations, has not been recovery-checked with rapid-forgetting data, and four of ten mice did not distinguish them.
- It will not describe the control comparison as testing how momentary evidence is used over time; control-trial motion energy varies little around nominal coherence.
- It will not call the rapid-forgetting model an exact extrema detector; it is an operational approximation with leak 20–200/s applied to temporally filtered motion energy.
- It will not claim the rankings are robust to the input front end; they used the linear front end, and the compressive front end selected in the exploratory amendment 7 was not propagated.
- It will not claim leak or urgency are absent, or that adding them "did not improve" the score; they improved the summed held-out score within Monte Carlo noise and were not needed under the parsimony rule.
- It will not use the free-leak fit to exclude time constants of a few hundred milliseconds.
- It will not interpret the guess delay (not recovered), per-mouse drift-variability presence (high false-positive rate in recovery), or drift variability as a specific mechanism (it is across-trial variability not explained by the stimulus).
- It will not claim starting-point variability is unneeded in the current model; it was tested only in an earlier model generation.
- It will not claim primacy, recency or flat temporal weighting; the timing test was not run and would not have detected 10–40% decay.
- It will not present the pulse excess as a discovery about mouse sensory processing, describe the pulse–model mismatch as a "wrong temporal profile", or attribute it to sensory, decision or response stages; the tested object is the model-and-input pipeline.
- It will not call pulses "evidence" for the decision; they are scheduled motion pulses that also form a salient visual transient.
- It will not describe the response-aligned kernel result as near-support for accumulation; its prespecified verdict is that neither model fits.
- It will not use the hidden-coherence analysis (N011–N013, N084–N087).
- It will not interpret differences between rigs, sites or cohorts; rig is a covariate only.
- It will not describe pulse assignment as randomized without session-pinned provenance.
<!-- LOCK-END -->

## Conditional thesis (outside the lock; chosen at G1 or after the analyses)
Decision rules are PROPOSED here and must be fixed by the authors before the analyses run.
| Outcome of F1a (rapid-forgetting-generated control-comparison recovery), with F1b/F1c | THESIS |
|---|---|
| Not run (current) | The THESIS above (identifiability gap stated in the sentence). |
| Rapid-forgetting-generated datasets rarely scored as favoring the accumulator (proposed: at most 2 of 20 mouse-replicates by > 10), accumulator-generated datasets rarely scored as favoring rapid forgetting, and F1b shows the advantage spread over choice and response-time terms | "In mice performing a reaction-time random-dot motion task, a bounded accumulator with drift variability and fast guesses predicted held-out control-trial choices and response times better than a tested rapid-forgetting model, in a comparison that recovered both generating models in simulation, whereas brief motion pulses moved choices far more than either control-fitted model predicted, which left the temporal weighting of evidence unresolved." |
| Recovery adequate, but F1b puts the advantage mainly in the censoring term, or F1c finds the difference unchanged with nominal-coherence input | "In mice performing a reaction-time random-dot motion task, control-trial response-time distributions were better described by a bounded accumulator with drift variability and fast guesses than by a tested rapid-forgetting model, whereas brief motion pulses moved choices far more than either control-fitted model predicted, which left the temporal weighting of evidence unresolved." |
| **Fallback.** Rapid-forgetting-generated datasets often scored as favoring the accumulator (proposed: at least 5 of 20), or F1b puts the advantage mainly in the empty-prediction penalty | "In mice performing a reaction-time random-dot motion task, a bounded accumulator with drift variability and fast guesses described control-trial choices and response times better than a tested rapid-forgetting model, but neither this comparison, which could not identify rapid forgetting in simulation, nor brief motion pulses, which moved choices far more than either model predicted, determined how mice use evidence over time." |
Between the proposed bounds (3–4 of 20), keep the current THESIS and report the confusion matrix.

## Glossary (one term per concept; never use synonyms)
| Term | Definition | Do not use |
|---|---|---|
| tested accumulator | The common model L0U0V1Z0G1: bounded drift-diffusion on motion energy (linear front end) with across-trial drift variability, no leak, no urgency, no starting-point variability, plus a fast-guess component | true DDM; accumulation proved; perfect integrator |
| rapid-forgetting model | The same pipeline with leak constrained to 20–200/s, applied to filtered motion energy, used as an operational extrema-like candidate | extrema detector (unqualified); snapshot model |
| linear front end | Motion energy entering drift in proportion to its value (F0); used in every reported model comparison | the input (unqualified) |
| compressive front end | Power-law transform of motion energy (F1, amendment 7), selected on control trials in a stopped exploratory comparison | the selected model (unqualified) |
| control trial | A trial without a scheduled signed pulse under the scheduled classification; model fits used the historical labels, which include 38 genuine pulse trials | no-pulse trial where the historical label differs |
| held-out control score | Simulation-based censored negative log likelihood summed over five control-only cross-validation folds (negative change = better); differences are reported per mouse against a working 10-unit threshold of roughly one per-mouse Monte Carlo SD | likelihood ratio; p value; significance |
| comparison recovery | Fitting both strategy models with the control-only cross-validation and score to data generated by each; not yet run for the rapid-forgetting generator | identifiability proof |
| drift variability (sv) | Across-trial standard deviation of drift not explained by the stimulus | noise; drift noise; engagement (as a mechanism) |
| fast-guess component | Mixture of responses independent of the stimulus by construction, with fitted probability, guess bias and exponential delay | lapse; contaminant (in Results) |
| guess bias | Probability that a fast guess is rightward | side bias (unqualified) |
| leak | Exponential decay rate of the accumulated evidence (per second) | forgetting (outside the rapid-forgetting model name) |
| urgency | Time-dependent term in the common model's urgency extension | collapsing bound unless that is the implementation |
| model recovery | Fitting the nested accumulator variants to data simulated from each with fitted parameters | identifiability proof |
| scheduled pulse direction | Positive or negative pulse category assigned by the task schedule before the outcome | randomized pulse; delivered pulse when the response preceded onset |
| motion pulse | Brief ±100% coherence replacement within a trial; a stimulus manipulation, not assumed to act only as decision evidence | evidence pulse |
| directional contrast | Within-supported-cell `(ΔP(right) − ΔP(left))/2` for positive versus negative scheduled pulse direction | accuracy effect; psychometric shift |
| pulse excess | Observed minus control-model-predicted pulse effect on choice (gate departure, logit) | pulse amplification (as a mechanism) |
| no response by 5 s | No registered response within the 5-s analysis window (most are later responses) | timeout; miss; lapse |
| temporal weighting | How strongly evidence at different times within a trial affects the choice | integration kernel (for model-free summaries) |
| primacy | Greater weight on early than later evidence, implemented in calibration as drift-gain decay over 0.5 s | early bias |
| predictive gate | Prespecified adequacy screen of the control-fitted model on pulse trials, required before the timing test | equivalence test; model validation |
| pulse gain | Mouse-specific scalar on the pulse component, cross-validated, with control parameters fixed | sensory gain |
| timing calibration | Simulation of full-cohort datasets with 0–40% drift-gain decay passed through the gate and timing pipeline | power analysis (unqualified) |
| fluctuation kernel | Reverse correlation of choices with within-trial motion-energy fluctuations on control trials | psychophysical kernel (as a different object) |
| response-aligned kernel test | Amendment 8 late-weight index on recorded control-trial choices, scored against both models' simulated references with a rule fixed before the run | kernel evidence for accumulation |
| model-and-input pipeline | The fitted model with reconstructed motion-energy input, likelihood and response mapping | decision mechanism alone |

## Promises ledger
What earlier sections set up that later sections must deliver. The editor checks every row.
| Promised in | Promise | Delivered in | Status |
|---|---|---|---|
| Introduction | Show that mice perform the task (performance only, no learning claim). | Results / Figure 1 | planned |
| Introduction | Compare accumulation with a tested rapid-forgetting model by joint held-out control prediction, stated as relative, operational and not yet recovery-checked for rapid forgetting. | Results / Figure 3; Discussion D2 | planned |
| Introduction | State the narrow novelty (mouse, continuous RDK, free RT, joint held-out fit) against rat and primate precedent. | Discussion D2 | planned |
| Introduction | Identify which accumulator components the control data require, with recovery limits and the linear front end. | Results / Figure 4; Methods | planned |
| Introduction | Ask whether brief pulses can resolve temporal weighting (primacy vs recency). | Results / Figures 5–6; Discussion D3 | planned |
| Results (Fig 3) | Report the four non-distinguishing mice and the per-mouse threshold as a working Monte Carlo resolution, not a test. | Results / Figure 3 legend; Methods | planned |
| Results (Fig 3) | State that recovery did not include a rapid-forgetting generator, and name H5 as an open alternative. | Results / Figure 3; Discussion D2 and limitations | planned |
| Results (Fig 3) | Report the response-aligned kernel verdict ("neither model fits") and the pulse strategy statistic beside the control comparison. | Results / Figure 3—figure supplements; Methods | planned (C013 subject to D001 item 4 revision) |
| Results (Fig 3) | Label the free-leak fit descriptive and give the leak-recovery limit. | Results / Figure 3C legend; Methods | planned |
| Results (Fig 4) | Report the amendment 7 compressive front end and that it was not propagated. | Results / Figure 4—figure supplement 1; Methods | planned |
| Methods | Disclose the 38 mislabeled pulse trials retained in control fits, and the motion-energy filter settings and how they were chosen. | Methods | planned ([MISSING: filter-choice provenance]) |
| Results (Fig 6) | Show observed versus predicted pulse effects for both control-fitted models, including 0% coherence, as the reason the gates failed. | Results / Figure 6A | planned |
| Results (Fig 6) | Report failed original and revised gates, the unrun timing test and the calibration as primary outcomes of the primacy plan, and that the power limit was found before pulse outcomes were read. | Results / Figure 6; Methods | planned |
| Results (Fig 6) | Explain the gate failure descriptively (pulse excess; mouse-varying gains; choice vs response-time gain conflict in two mice). | Results / Figure 6 and supplement; Discussion D3 | planned |
| Methods | Give units and operational definition of the rapid-forgetting leak range (first-version RM12). | Methods | planned |
| Discussion | State what design could resolve temporal weighting, qualitatively unless a forward design simulation is run. | Discussion D5 | planned |
| Discussion | Place the result against precedent showing integration beats extrema/snapshot models (hyafil2023temporal) and in rats (brunton2013rats). | Discussion D2 | planned |
| Discussion | Present the misspecification of both models (error RTs, late responses at 100%, pulse excess) as limiting what the ranking says about mechanism. | Discussion D4 | planned |

## Open items for G1 (outside the lock)
- D001 item 4 said to include the amendment 8 kernel "if it pans out". It did not; v2 reports it as a prespecified negative (C013) to avoid selective reporting. Needs author approval and a decisions.md entry.
- Working title in config ("Mice accumulate continuous motion evidence…") asserts more than the THESIS; replace at G1.
- Which pending analyses to run (`np/reviews/spine_response.md`), and the F1a decision bounds, fixed before running.
- Pulse wording: "scheduled" unless authors supply session-pinned provenance (RM2 option a).
- Figure 2 main versus Methods/supplement (conditional on F1c).
