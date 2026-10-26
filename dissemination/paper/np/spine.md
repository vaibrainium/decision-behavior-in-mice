<!-- np-contract
stage: S1 ; section: spine ; agent: np-architect ; version: v2
thesis: "Joint held-out prediction on control trials favored the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009
numbers: N001, N004, N005, N006, N009, N010, N016, N024, N025, N026, N027, N030, N034, N035, N036, N039, N040, N041, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066
sources: E001, E019, E020, E021, E022, E024, E025, E026, E027, E028
-->
# Paper spine

The spine anchors the paper against drift. Everything between LOCK-START and LOCK-END is frozen after
human approval at G1. A change then requires a decision-log entry, renewed human approval and re-locking.

<!-- LOCK-START -->
THESIS: Joint held-out prediction on control trials favored the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence.

## Story (OCAR)

- **Opening (problem space, audience):** Decisions can look consistent with evidence accumulation even when they arise from rapid forgetting or extrema-like strategies, so behavioral fit alone does not identify the computation.
- **Challenge (the specific question; the hinge of the paper):** Does a model-and-input pipeline selected by joint prediction of choices, response probabilities and response times during ongoing noisy motion generalize to a brief, strong and randomly assigned motion perturbation?
- **Action (what was done):** Mice performed a reaction-time random-dot-motion task on two rigs; reconstructed motion energy drove accumulator and rapid-forgetting models fitted and compared on control trials; scheduled signed pulses provided a separate behavioral perturbation; pulse-aligned outcome curves, stimulus audits and joint choice/response-time diagnostics tested model generalization.
- **Resolution (the answer):** Joint held-out control prediction favored the tested accumulator among the tested implementations, and pulse assignment redirected responses, but neither the original nor gain-revised model-and-input pipeline reproduced the pulse response distribution; good control prediction therefore did not validate processing of transient strong evidence, and the missing sensory, decision or response mechanism remains unresolved.

## Competing hypotheses and what each predicts

| Hypothesis | Prediction | Which figure decides it |
|---|---|---|
| H1: Evidence is retained by the tested accumulator | The accumulator gives better joint held-out prediction of control-trial choices, response probabilities and response times than the 20–200 s⁻¹ rapid-forgetting approximation. | Figure 3 decides this relative control-model comparison; Figures 4–5 separately test out-of-condition generalization. |
| H2: Decisions rely on rapid forgetting or extrema-like sampling | The rapid-forgetting approximation matches or exceeds accumulator joint prediction on held-out control trials. | Figure 3. The insensitive pulse-strategy comparison in Supplementary Figure S6 cannot decide H1 versus H2. |
| H3: The fitted model-and-input pipelines omit a process engaged by transient strong evidence | Control behavior may favor one candidate, but both pipelines fail pulse prediction; at the group level they predict the wrong temporal profile, and in the two informative mice choice-optimal gains worsen the remaining response objective. | Figure 5, with predictive-gate and calibration details in Supplementary Figure S6. |

## Key control (rules out the boring explanation)

Pulse direction was assigned before behavior within coherence-defined schedules, and the primary comparison contrasts positive and negative assignments within mouse × session × signed-coherence × onset cells while retaining pre-onset responses and no-response trials. This prevents post-response pulse labeling or response-conditioned inclusion from manufacturing the directional effect. Paired software replays test the implemented stimulus representation for sign-aligned artifacts; they do not validate every displayed frame or acquisition timestamp. These controls do not distinguish sensory persistence, decision dynamics and response generation, and they do not rule out state-dependent effects such as attention or arousal.

## Figure plan (one claim per figure)

| Fig | Claim it supports (claim IDs) | Data source (path) | Status |
|---|---|---|---|
| 1 | The experiment provides choice, response-time and no-response constraints during motion discrimination with scheduled directional perturbations (C002). | `figures/fig1_behaviour_2026-10-20.*`; regeneration sources in `figure_captions.md` | Draft exists; labels, masks and uncertainty require reconciliation. |
| 2 | Stimulus reconstruction defines the model input and exposes assumptions and replay uncertainty beyond nominal coherence (C003). | `figures/fig2_motion_energy_2026-10-20.*`; stimulus-audit outputs | Draft requires revision; the unresolved hidden-coherence association moves to the supplement. |
| 3 | Joint held-out prediction on control trials favors the tested accumulator among the tested implementations (C004). | E019 outputs; `scripts/ddm/compare_strategy.py`; final fit-quality figure | Not assembled; source results available; score components are not claimed to favor the accumulator separately. |
| 4 | Randomized signed pulse assignment shifts response direction, and the cumulative response-associated contrast emerges mainly 0.5–2 s after logged onset (C005). | `figures/pulse_followup/20261023T191030Z_fa8de8b/behaviour_*`; `response_time_*` | Source panels available; composite not assembled; timing describes emitted responses. |
| 5 | The tested pipelines predict a different group temporal profile from the observed pulse-associated response contrast (C006), while a held-out choice-versus-remaining-objective gain tradeoff is demonstrated in two informative mice (C009). | `figures/pulse_followup/20261023T191030Z_fa8de8b/diagnostics_*` | Source panels available; C006 remains descriptive unless a paired model-minus-observed analysis is added; C009 is limited to PSUIM6/7. |

The failed original/revised gates, inconclusive pulse strategy comparison, strategy sensitivity and primacy calibration are mandatory Supplementary Figure S6 content (C007), not omitted outcomes.

## Scope: what this paper will NOT claim

- It will not claim that behavior uniquely proves accumulation or rules out every non-integrating strategy.
- It will not claim primacy, recency or flat temporal weighting: the confirmatory timing test was not run after gate failure, and calibration showed inadequate sensitivity.
- It will not identify the pulse mismatch as uniquely sensory, decisional or motor/response-related.
- It will not generalize the choice-versus-response-time gain conflict from PSUIM6/7 to all mice.
- It will not attribute failed pulse generalization to decision dynamics alone; the tested object includes reconstructed input and response-generation assumptions.
- It will not treat cumulative response time as a neural integration time or memory-duration measurement.
- It will not interpret the hidden-coherence shared ratio as a demonstrated population-wide discount without its scheduled-control sensitivity.
- It will not treat the stimulus replay as a frame-perfect record of the display or its 1.28–1.40 UCLA alternative as a universal error bound.
- It will not infer biological differences between sites, rigs or cohorts, which are confounded.
- It will not present the unreviewed `tau_p` pilot as a formal claim.
- It will not include the separate SC wide-field-voltage-fluorescence inactivation study.
<!-- LOCK-END -->

## Glossary (one term per concept; never use synonyms)

| Term | Definition | Do not use |
|---|---|---|
| tested accumulator | The fitted bounded evidence-accumulation model with drift variability and a fast-response mixture | accumulator mechanism proved; true DDM |
| rapid-forgetting approximation | The 20–200 s⁻¹ leak implementation used as an operational extrema-like candidate | exact extrema detector |
| control trial | A trial without a scheduled signed pulse under the analysis-specific scheduled classification | no-pulse trial when the historical label differs |
| scheduled pulse assignment | Positive or negative pulse category assigned before the behavioral outcome | delivered pulse when response preceded onset |
| directional contrast | Within-supported-cell `(ΔP(right) − ΔP(left))/2` for positive versus negative assignment | accuracy effect; psychometric shift |
| no response by 5 s | No registered response within the fixed motion-onset analysis window | timeout; late response unless directly observed |
| pulse-aligned cumulative contrast | Difference in cumulative directional response probabilities as a function of time from scheduled onset | integration kernel; neural latency |
| predictive gate | Prespecified adequacy screen required before the model-adjusted timing test | equivalence test |
| pulse gain | Mouse-specific scalar applied to the pulse component while control parameters remain fixed | sensory gain; behavioral sensitivity |
| model mismatch | Demonstrated disagreement between observed and predicted pulse-associated choice/response-time summaries | absence of accumulation |
| model-and-input pipeline | The fitted decision model together with reconstructed motion-energy input, likelihood and response mapping used to generate predictions | decision mechanism alone |

## Promises ledger

| Promised in | Promise | Delivered in | Status |
|---|---|---|---|
| Introduction | Distinguish accumulation from tested rapid forgetting using joint held-out control prediction among specified implementations. | Results / Figure 3 | planned |
| Introduction | Use randomized pulses as a generalization test rather than assuming they prove primacy. | Results / Figures 4–5 | planned |
| Introduction | Treat choice accuracy and temporal weighting as non-unique signatures and use joint choice/response-time prediction for the specified comparison. | Results / Figure 3; Discussion D2 | planned |
| Introduction | State only that the exact mouse predictive-transfer conjunction was not found in a bounded search; acknowledge established mouse RDK, discrete-evidence and visual DDM work. | Introduction P3; Discussion D2 | planned |
| Introduction | Report the randomized behavioral pulse effect separately from model interpretation. | Results / Figure 4; Discussion D1 | planned |
| Introduction | Test whether the frozen control-selected pipelines transfer to transient strong evidence. | Results / Figure 5 | planned |
| Results | Report gate failures, low sensitivity and the withheld timing test alongside exploratory diagnostics. | Results / Supplementary Figure S6; Discussion | planned |
| Results | Keep the group model–data timing comparison descriptive and the gain tradeoff limited to PSUIM6/7. | Results / Figure 5; Discussion D3–D4 | planned |
| Results | Explain why the replay and model form are one tested prediction pipeline rather than a direct assay of decision dynamics. | Discussion D1 and D3 | planned |
| Discussion | Separate the behavioral pulse effect from the unresolved processing mechanism. | Discussion opening and limitations | planned |
| Discussion | Give a concrete experiment that can separate display/input, sensory, decision and response explanations. | Discussion D5 | planned |
