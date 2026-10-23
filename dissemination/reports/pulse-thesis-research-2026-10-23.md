# Pulse experiments as a concrete thesis contribution: existing-data research review

Date: 2026-10-23. Agent: Codex. Repository snapshot: `fa8de8b2d33421c7dd18fc990b19984c4df4bac0`.
Status: research synthesis and proposed follow-up, not a newly adopted analysis protocol.
Constraint: **existing data only**, explicitly confirmed by the user. No new behavioural experiment is recommended as a dependency.
Related plan: `.agents/plans/2026-10-20-paper-writeup.md`, K–L.

The best near-term route is to make pulses a quantitative test of how a transient stimulus changes the joint distribution of choice and response time. Primacy is one possible question within that programme. The completed primacy procedure failed its adequacy checks and had low simulated sensitivity; that result remains closed. It does not establish that every pulse analysis is powerless. A broader claim about a unique neural implementation may remain unidentified even after the proposed work.

This is a targeted critical review, not an exhaustive systematic review. Public primary articles, publisher pages, author manuscripts, PMC/Europe PMC and preprints were searched on the date above; representative search strings and access limitations are recorded below. No unpublished data were sent to external research services. No new choice-by-timing contrast, behavioural model fit, or cluster job was run.

## What the existing project actually provides

**Verified by reading saved outputs:** the revised primary gate departure is 0.241769 logit, with a 95% posterior interval of 0.090580–0.365729; its predicted pulse effect is 0.056748. The secondary departure is 0.308882 (0.197824–0.405981), with predicted effect 0.028899. Both gates fail. These are departures from specified predictions, not direct causal pulse-effect estimates. Sources: `processed/ddm/primacy_revised/results_{primary,secondary}_gate.pkl`; reproduction and hashes are in the accompanying agent report.

**Verified by saved calibration summaries:** there are 20 datasets at each generating decay of 0%, 10%, 20% and 40% over 0.5 s. Gate passes are 19, 14, 7 and 1; negative primary timing intervals occur in 0, 0, 1 and 0 datasets. The one detection occurs outside a passing gate. The simulation holds real control fits fixed, generates only pulse-trial outcomes with an added global gain decay, then refits pulse gains. It evaluates that particular analysis under those generators. It is not a power calculation for the descriptive effect of assigning a pulse, a joint choice–RT model comparison, or every possible temporal effect. Sources: `scripts/ddm/primacy_calibration.py::run_job/summarize` and `processed/ddm/primacy_calibration/calibration_summary_levels*.csv`.

Zero false positives among 20 null datasets does not certify a nominal 5% false-positive rate: the upper endpoint of a two-sided exact 95% binomial interval is 0.1684 (`scipy.stats.beta.ppf(.975, 1, 20)`). Future calibration should report simulation uncertainty. This qualification changes interpretation, not the stored result or the decision to withhold the original timing test.

**Verified metadata inventory:** joining responded `valid_data.csv` to the retained DDM input rows by `agg_code`, using scheduled labels, gives:

| Inventory item | UCLA | UW |
|---|---:|---:|
| Mice | 4 | 6 |
| Responded pulse trials | 6,030 | 5,449 |
| Responded scheduled controls | 9,257 | 4,757 |
| Pulse onset range, seconds | 0.009995–0.301963 | 0.05001–0.41675 |
| Distinct recorded onset values | 5,727 | 3 |
| Responses before scheduled pulse onset | 0 | 224 |
| Responses at least 0.5 s after pulse onset | 4,830 | 3,883 |
| Mouse × seed × base-coherence cells with both pulse signs | 456 | 0 |
| Such cells also containing a scheduled control | 220 | 0 |

These are feasibility counts, not evidence of an effect or adequate power. They exclude censored trials, which must be included in an analysis of all scheduled trials. The large number of recorded UCLA onset values does not imply that many physically distinct display times: render timing is frame-quantized and the recordings include timestamp variation. Repeated seeds allow a limited matched-stimulus sensitivity analysis in one dataset; they do not justify a site-level biological comparison.

Pulses replace nominal coherence with +100% or −100%. Their signed increment is `pulse_coherence − base_coherence`, not uniformly ±100 percentage points. Retained recorded pulse durations have medians about 50.7 ms and 66.68 ms for UCLA and UW. Therefore pulse sign, baseline coherence, actual frame duration and rig must be handled explicitly.

## A newly verified stimulus issue to resolve before interpreting persistence

In both replay implementations, returning from a pulse to baseline coherence redraws some noise-dot directions. It does not restore the original directions. A deterministic check with seed 1, base coherences 0, +18 and −18, and a +100 pulse followed by return to baseline found changed direction arrays in both rigs. This agrees with the code branches in `scripts/ucla_rdk.py::updateBurst` and `scripts/uw_rdk.py::update_coherence`.

Meanwhile `scripts/ddm/primacy.py::no_pulse_frames` computes baseline-coherence onset response plus the **noise residual from the pulsed replay**. It removes the average pulse component; it does not generate the same-seed physical stimulus with pulse events omitted.

This is a verified difference in counterfactual definition, **not evidence that the observed behavioural effects are artefacts**. The full pulsed ME remains in the original model's actual-stimulus predictions. The issue matters for interpreting the removed component, fitted pulse gain and any apparent long-lasting pulse effect. A direction reset can change the realised background without causing a systematic pulse-direction-aligned bias. The size and sign of any such bias are unmeasured.

Priority check: paired replays with the same initial seed, baseline and duration, once with the scheduled pulse and once without pulse events. Verify equality before onset; measure the complete difference in ME after onset and after nominal offset. Separate the deterministic average response from trial-specific changes. Where branch-dependent random draws occur, define the coupling explicitly; do not describe this as holding every future random draw fixed. Compare signed and unsigned differences over seeds. Validate a subset before paying for complete ME recomputation.

The already documented UCLA one-frame freeze mismatch also needs assessment against available rig provenance. Its claimed 25–35% magnitude is an upstream estimate, not independently verified here. Correcting either issue might change quantitative predictions, but no rescue of the behavioural model is promised.

## What the primary literature supports

| Source and reading scope | Relevant finding | Consequence for this thesis |
|---|---|---|
| [Huk & Shadlen, 2005](https://doi.org/10.1523/JNEUROSCI.4684-04.2005), full author PDF | Brief motion perturbations affected choices, RTs and neural activity beyond pulse duration; bounded integration explains part of the apparent temporal decline. | Analyse directional choice and RT effects together. A delayed response alone does not reveal when commitment occurred; their neural evidence is stronger than behaviour alone. |
| [Wong et al., 2007](https://doi.org/10.3389/neuro.10.006.2007), full-text pulse sections | A recurrent attractor model reproduces aspects of pulse responses and predicts nonlinear interactions. | Pulse sensitivity or early weighting does not uniquely select a simple DDM. Their paired-pulse proposal is background, not feasible retrospectively here. |
| [Zhou, Wong-Lin & Holmes, 2009](https://doi.org/10.1162/neco.2009.07-08-817), full manuscript | Perturbation effects on RT moments distinguish some model classes under suitable conditions; noise and decision delays can destroy separation. | Joint RT structure is worth investigating, but discriminate models by simulations at this dataset's actual noise and trial counts. |
| [Cisek, Puskas & El-Murr, 2009](https://doi.org/10.1523/JNEUROSCI.1844-09.2009), full author PDF | Changing evidence provided support for an urgency-gating account in their task. | Urgency is a substantive competing hypothesis, not a generic fit-improvement parameter. Its predictions depend on the task and sensory representation. |
| [Tsetsos et al., 2012](https://doi.org/10.3389/fnins.2012.00079), full-text methods/discussion | Temporal weighting varied with experimental conditions; competing accumulation mechanisms could produce primacy. Some distinctive findings occurred in only a subset of observers. | Do not equate a temporal weighting curve with one mechanism or pool away individual differences. |
| [Kiani, Churchland & Shadlen, 2013](https://doi.org/10.1523/JNEUROSCI.2094-13.2013), full author PDF | Human observers combined two motion cues across variable gaps, constraining retention dynamics. | Retention is distinct from pulse-onset weighting. This dataset lacks independently manipulated gaps, so its free-response latency cannot substitute for that manipulation. |
| [Yates et al., 2017](https://doi.org/10.1038/nn.4611), full-text sensory-model sections | Time-dependent sensory responses in MT could produce early behavioural weighting even with linear downstream integration. | Validate the stimulus-to-evidence mapping before attributing timing effects to leak, urgency or an attractor. Mouse sensory dynamics are not established by macaque MT results. |
| [Evans et al., 2017](https://doi.org/10.1038/s41598-017-16694-7), full institutional PDF | Quantitative and qualitative comparisons favoured diffusion over urgency gating in their human experiments. | The existence of urgency models does not imply they will fix this dataset. Give competing models comparable sensory flexibility and test held-out joint behaviour. |
| [Okazawa et al., 2018](https://doi.org/10.1038/s41467-018-05797-y), full author PDF | Sensory/motor delays, decision dynamics and bounds can distort psychophysical kernels. | Treat RT-conditioned kernels as descriptions of selected trials; use explicit models for mechanistic interpretation. |
| [Stine et al., 2020](https://doi.org/10.7554/eLife.55365), full publisher article | Non-integration strategies can mimic accuracy and kernels; choice and response-time constraints improve discrimination. | Pulse-induced choice shifts establish sensitivity to perturbations, not accumulation by themselves. Retain the existing qualified control-strategy result. |
| [Kumano & Uka, 2024](https://doi.org/10.1097/WNR.0000000000001980), full Europe PMC text | Relevant and irrelevant pulse effects had different temporal profiles in a task-switching experiment. | Mechanistic value comes from contrasts between specified predictions. Their task manipulation, pooled analyses and neural context cannot be imported into this mouse experiment. |
| [Chakravarty et al., 2025](https://doi.org/10.7554/eLife.105116.1), reviewed preprint, publisher full text | A cross-species pulse task motivated models of time pressure and changing behavioural strategies in mice. | Consider response policy or state heterogeneity if diagnostics require it. This remains a reviewed preprint and uses a different stimulus/task; it is not evidence for urgency or switching in these mice. |

These studies motivate the proposed analyses; none guarantees a positive or identifiable result in the present data. A published reference list contained an incorrect DOI for Zhou et al.; the DOI above was checked against its own PubMed record, PMID 19416080.

## Recommended existing-data programme

### 1. Establish the behavioural effect independently of DDM adequacy

Define the primary descriptive target before fitting: the change in probability of right and left responses, and of no response by the analytical deadline, under the scheduled positive pulse, negative pulse and control conditions. Estimate adjusted probability differences in percentage points with per-mouse effects and group uncertainty. A simple descriptive logistic model among responders can be useful, but must be accompanied by the response probability; it conditions on an outcome affected by the intervention.

Use scheduled labels, both pulse directions, flexible baseline-coherence adjustment, mouse/session structure and stimulus-history information available before pulse onset. Zero nominal coherence is an informative subset, but is not stimulus-free: seed-specific hidden coherence remains. Check pulse assignment and balance within sessions from task records before using causal language. Do not adjust for realised RT as if it were a baseline covariate.

For the primary assignment analysis, retain trials that respond before a scheduled pulse: they contribute to the effect of the scheduling policy. In a separate onset-eligible analysis, define eligibility immediately before the pulse. Under randomized, unannounced pulse assignment and identical pre-onset exposure, this avoids selecting on a post-pulse response. It still compares particular populations at particular onset times, not an invariant neural integration window.

Use mouse as the independent unit for group claims. Prefer one declared primary directional contrast; if several confirmatory-style contrasts are added to the exploratory follow-up, declare their family and apply Holm correction, or specify simultaneous interval coverage. Show individual animals and leave-one-mouse-out sensitivity. Session and repeated-seed analyses test robustness, not additional independent replication.

**Deliverable:** a defensible statement of the pulse's directional behavioural influence with uncertainty. This step does not need a passing DDM gate. Success is a precise, robust estimate; a scientifically meaningful negative or heterogeneous estimate must also be reported.

### 2. Estimate the pulse-aligned joint response distribution

For a given onset stratum, estimate the cumulative probabilities of a left response, right response and remaining without a response as a function of elapsed time after the scheduled pulse. Compare pulse directions and appropriately matched controls, standardizing baseline coherence and mouse contributions. Controls need an actual sham schedule or a prespecified matched pseudo-onset assignment independent of their future response.

A useful estimand is `P(T <= onset + u, choice = right | T >= onset, assigned condition, baseline covariates)`, alongside its left-response counterpart. Keep an analysis of all scheduled trials as well. A multinomial event-history model can estimate both response types jointly; one response type must not be treated as independent censoring for the other. Raw cumulative-incidence curves and per-mouse contrasts should make model assumptions visible.

Ask whether the pulse mainly redirects responses, advances or delays them, changes omission probability, or combines these. Compare both pulse signs to test for a common response-time effect as well as a directional one. Hazard contrasts are themselves conditional on remaining unresponded after treatment, so do not interpret their late-time shape as an unselected causal memory curve.

The previous `RT >= onset + 0.5 s` check can be a labelled sensitivity description. It should not be the main proof of retention: conditioning on future RT can select different trials after the pulse, and the decision may precede the movement. Likewise, a late divergence of cumulative response curves can contain an earlier effect carried forward. Any persistence claim must be tested against full simulations including sensory filtering, changed stimulus background and motor delay.

**Deliverable:** a pulse-aligned behavioural fingerprint and an explicit statement of whether the current model fails on direction, latency, response probability, or their relationship.

### 3. Diagnose the existing model failure before choosing a new model

Use the paired-replay audit described above. On representative seeds, check pulse duration, timing, spatial pooling and filter-response shape. Verify that the average pulse template adequately describes actual pulse durations; the current builder fits the modal frame length per rig and applies its response to other lengths.

Then plot held-out choice, correct/error RT and censoring contributions across the pulse-gain profile. Compare a choice-only optimum with the existing joint optimum strictly as a diagnostic. This tests the suspicion that gains needed for choices force incorrect response times. Do not select a likelihood simply because it gives a preferred conclusion.

Check whether fixed control parameters prevent the revised model from fitting pulse trials because of already documented psychometric errors. A follow-up may estimate shared parameters jointly on training control and pulse trials, or propagate control-fit uncertainty, then predict held-out data. That is a new exploratory model, not a repair that changes the original frozen comparison. Any shared revision must still explain control behaviour.

**Deliverable:** an identified mismatch with a concrete, falsifiable proposed correction. If stimulus validation is unresolved, make sensory-mechanism conclusions conditional on it.

### 4. Compare a small, matched set of explanations

Choose candidates from the diagnostic result, with a limited parameter budget:

| Diagnostic finding | First candidate to test | Required discrimination |
|---|---|---|
| Pulse amplitude or response shape is misrepresented | Corrected input with pulse gain; if needed, one additional pulse-response time constant | Must explain both response direction and timing; avoid counting the existing ME filter delay twice |
| Both directions cause a common latency effect beyond the directional effect | A tightly specified pulse-triggered response/engagement component | Must predict the unsigned latency effect and the signed choice effect; additive nondecision delay cannot by itself explain directional choice shifts |
| Adequate input/response model leaves a robust temporal discrepancy | One memory/leak or evidence-weighting extension at a time | Must improve held-out prediction and be distinguishable from sensory-duration and response-delay changes |
| Brief-sample strategy remains a viable alternative | Matched extrema/short-memory candidate with the same input-calibration options | Model preference must not result solely from giving the accumulator a better sensory front end |

Do not add a flexible pulse kernel, leak, urgency, variable delay and latent states simultaneously. Sensory persistence and accumulator retention can trade off; a good joint fit need not identify their separate time constants. Leak/urgency were already included in the secondary baseline that failed, so repeating those additions without a new prediction is low priority.

Use held-out sessions where sample sizes allow, plus a repeated-seed holdout sensitivity. Ordinary random trial CV addresses prediction in the same sampled conditions; it does not automatically establish generalization to new sessions or unseen stimulus sequences. Existing data have already informed model selection, so retrospective CV does not restore an untouched confirmatory test.

### 5. Validate what the proposed comparison can resolve

Before interpreting a mechanism coefficient, simulate the observed schedules and sample sizes under every candidate. Refit all parameters that the proposed analysis estimates, including control parameters if it re-estimates them. Reproduce censoring, eligibility, summary construction and selection. Include no-effect/null cases, realistic parameter uncertainty and deliberately competing sensory versus decision explanations.

Measure model-confusion rates, parameter recovery, null false positives and interval coverage. A pilot simulation can cheaply reject an uninformative comparison; increase simulation replication for a final decision and report Monte Carlo intervals. The existing twenty-dataset calibration is useful evidence about the original procedure, but not enough to declare every new procedure calibrated. Specify sensitivity requirements and a stopping rule before the new comparison is evaluated.

**Stop if candidates remain indistinguishable.** The appropriate thesis endpoint is then a quantified behavioural perturbation and a demonstrated predictive limitation. Do not infer a unique neural mechanism, absence of accumulation, or absence of primacy from that endpoint.

## Feasible outputs and effort

These are engineering planning estimates, not measured completion promises. They assume existing dependencies, accessible processed data and prompt review of scientific decisions.

| Package | Additional hands-on effort | Dependencies / limit |
|---|---|---|
| Assignment/label audit, adjusted pulse-effect estimates and first pulse-aligned plots | 0.5–1 working day | No new full DDM fitting; no guarantee of a robust group effect |
| Paired-replay subset, pulse-component validation and choice–RT misfit diagnosis | 0.5–1.5 working days | Complete ME recomputation, if needed, adds processing time |
| One targeted candidate and fair comparison implementation | 1–2 working days | Follows diagnostic evidence; cluster fitting requires separate authorization |
| Recovery, discrimination simulations and final robustness | 1–3 working days plus queue time | Can be the largest compute cost; stop early if discrimination fails |

A first useful pulse analysis is plausible within one working day. A well-validated mechanistic follow-up is a roughly **4–7-working-day planning target**, potentially longer if stimulus reconstruction or joint fitting needs substantial revision. Existing data may still support only a restricted mechanism claim.

Compute anchors from saved metadata: the 20 final control fits report `fit_seconds` of 363.1–11,800.9 s, median 1,638.7 s, approximately 6 minutes–3.3 hours per fit. Ten level-zero/dataset-zero calibration jobs report 35.9–150.8 s, median 60.7 s, for their pulse-gain fitting/prediction stage. The latter excludes group GLMM summarization, initial control fitting and queue time. Neither runtime can be assumed for a more complex candidate.

For the thesis, prioritise three empirical panels: adjusted directional pulse effects per mouse; pulse-aligned left/right/no-response curves; and observed-versus-predicted behaviour with the original and revised failures retained. Add a mechanism-comparison panel only if the validation succeeds. A suitable organising question is **how transient evidence perturbs ongoing decisions and constrains accumulation models**. A pulse-derived neural time constant or primacy mechanism is conditional on additional evidence, not a prerequisite for a useful thesis contribution.

## Search and access record

The review used targeted web discovery and citation chaining, including the following exact search families; it did not export a complete bibliographic database or conduct duplicate independent screening. Public-only queries are archived in `pulse-thesis-searches-2026-10-23.json`. Full-text assessment focused on the twelve sources in the table. Odoemene et al. (2018), Pinto et al. (2018), Brunton et al. (2013), Scott et al. (2015), and related papers were considered as contextual leads rather than used to establish model identification in this experiment.

PMC HTML intermittently returned a browser challenge. Author/institutional PDFs supplied Huk, Okazawa, Kiani, Cisek and Evans; Europe PMC XML supplied Yates, Wong, Tsetsos and Kumano. Europe PMC retrieval attempts for PMC3797371 and PMC6246883 failed; the Kiani article was read through its author PDF. The literature review is limited by targeted retrieval and single-agent appraisal. Recent searches included 2024–2026 terms; no claim of exhaustive current coverage is made.

The local literature-review, scientific-critical-thinking, statistical-analysis and statistical-power skills informed the procedure. Workflow reference (metadata checked): Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065). This is a workflow attribution, not scientific evidence for the pulse conclusions.
