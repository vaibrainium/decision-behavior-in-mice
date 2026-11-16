# What attention and decision research imply for the pulse/RT mismatch

Date searched: 2026-11-14. Repository baseline: `b63c9d9`; new review files are uncommitted. Focused critical narrative review, not a systematic review or meta-analysis.

## Recommendation

**Investigate predictable choice-history effects and persistent behavioral states before treating independent gain variability as an attention explanation.** Keep positive evidence-gain variability as a compact candidate, but first ask whether the variability requiring explanation is independent across trials, predictable from recent choices/rewards, or persistent within sessions. Then test its consequences for the *joint* choice/RT distribution and the signed pulse response.

This revises the order proposed after the response-delay pilot. The literature supports gain as a plausible computational component; it does not establish that gain alone will fix the data, that attention is its source, or that another gain fit would constitute a novel result.

The recommended next work is an existing-data analysis and a short simulation feasibility study, followed by one targeted model comparison. No further experiments are required to take these steps. Detailed implementation decisions are in [NEXT_ANALYSES.md](NEXT_ANALYSES.md), and study-by-study assessments are in [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md).

## The problem the literature must explain

The recent pilot leaves two constraints unresolved. In PSUIM7, replacing additive drift variability with an independent lognormal postdecision delay still costs about 256 held-out NLL units relative to the matched drift-variability model. The new model predicts early directional pulse effects of about 7.15 and 4.84 percentage points in PSUIM6 and PSUIM7, versus observed effects of 15.50 and 13.48. These are selected diagnostic mice, not a population estimate. [Pilot results and source tables](../response_delay_2026-11-14/RESULTS.md).

The repository already contains more relevant evidence than a generic proposal to fit another DDM:

- Choice history affects behavior after controlling for coherence and pulse direction. The earlier subject-level analysis found a tendency to repeat after an unrewarded choice, with history coefficients comparable to pulse coefficients in the informative UCLA mice. That descriptive result exists; its implications for the generative choice/RT fit remain untested. [Existing report](../../.agents/reports/2026-10-29-behavior-exploration.md).
- Response timing changes across sessions; late recorded choices are not automatically disengaged guesses. These observations motivate structured variability but do not establish its origin. [Timing diagnostic](../pulse_rt_tradeoff_2026-11-13/RESULTS_AND_NEXT_MODEL.md), [behavior report](../../.agents/reports/2026-10-29-behavior-exploration.md).
- Static power mappings, temporal normalization, pulse weights, leak/urgency, pulse-only fits and race/LCA illustrations have already been examined. The next proposal must add a different prediction, not repeat these under another label. [Completed-results inventory](../reviewer_2026-11-13/COMPLETED_RESULTS.md).

Three time scales should remain distinct: the encoding of a brief stimulus event; integration and decision termination during a trial; and changes in sensitivity, bias or engagement across trials. A parameter called “drift variability” can absorb effects from several of them.

## 1. Structured strategies are a serious alternative to independent noise

Mouse choices can reflect persistent stimulus-guided and biased strategies. Ashwood and colleagues compared a GLM-HMM with static and continuous alternatives, and examined response-time and violation patterns that were not used to fit the choice model. Their response-time measure in the IBL data included time until feedback, rather than being the exact same movement-onset latency used in some RT tasks. This distinction limits direct numerical transfer. [Ashwood et al., 2022](https://doi.org/10.1038/s41593-021-01007-z).

Hulsey and colleagues related mouse performance states to prestimulus pupil and movement measures, including omissions in the behavioral model. Those independent observations strengthen the interpretation that behavior varies with physiological state, while not proving that a particular state is attention. A choice-only HMM without such measures would support a more limited behavioral claim. [Hulsey et al., 2024](https://doi.org/10.1016/j.celrep.2024.113709).

Continuous strategy variation must remain a competitor. PsyTrack estimates changes in bias, sensitivity and history weights, including changes across session boundaries. Its smoothed trajectories can use future choices; they are not automatically prestimulus predictors. [Roy et al., 2021](https://doi.org/10.1016/j.neuron.2020.12.004).

**Inference for this repository:** first establish whether serial dependence remains after the already documented history effects. Compare a static history model, a continuous strategy model and a small state model with a common held-out target. A visually convincing state raster is not sufficient. A choice model must also predict RT or pulse features that did not determine its state labels.

An important limitation is that state mixing cannot, by itself, create an unconditional signed effect of a properly randomized pulse. It could alter which states contribute to response-conditioned time bins and explain why an aggregate RT fit assigns variability incorrectly. The randomized perturbation effect and its response-conditioned time profile are different estimands.

## 2. Choice history may bias the accumulation itself

Urai and colleagues found that history-dependent accumulation bias explains choice repetition across several human perceptual tasks, challenging the assumption that history operates only by shifting the starting point. The time course of repetition bias across RTs helped distinguish these accounts. This is a direct reason to compare both mechanisms here. [Urai et al., 2019](https://doi.org/10.7554/eLife.46331).

A separate EEG-constrained study illustrates why independent observations can change the inferred allocation of prior bias between starting point and drift. It does not supply those missing observations for the present mice. [Prior-probability study, 2024](https://doi.org/10.1162/imag_a_00338).

**Inference:** a trial-constant signed offset in the current model could partially represent predictable history or persistent bias, rather than independent neural noise. Replacing it wholesale with gain before testing this possibility skips an explanation already suggested by the data. The relevant comparison is history-dependent drift bias versus history-dependent starting point, with residual variability allowed and all common parameters refitted.

This is not a prediction that history will necessarily restore the pulse effect. It predicts a specific conditional choice/RT signature that the current independent-offset model should reproduce if it is an adequate approximation.

## 3. Attention supports several mechanisms, not one parameter

Human neural studies associate attentional fluctuations with accumulation rate, preprocessing, and decision onset. Controlled cueing experiments support effects on both sensitivity and the initiation of decision-related activity. These are relevant precedents for separating encoding from accumulation, but spatial cueing and EEG constraints differ from an uncued single-stream mouse task. [Kelly and O’Connell, 2013](https://doi.org/10.1523/JNEUROSCI.3355-13.2013), [Nunez et al., 2017](https://doi.org/10.1016/j.jmp.2016.03.003), [Ueno et al., 2024](https://doi.org/10.1007/s00221-024-06862-3).

Other experiments find that target selection influences the onset and rate of accumulation, and that divided attention can impair downstream integration even when decision information is encoded. Those tasks introduce selection demands that this task does not explicitly manipulate. [Loughnane et al., 2016](https://doi.org/10.1016/j.cub.2015.12.049), [Wyart et al., 2015](https://doi.org/10.1523/JNEUROSCI.3276-14.2015).

The literature also supplies counterevidence to a simple gain replacement: pupil-linked arousal can relate to drift-rate variability, and attention can change sensory population noise correlations. These findings do not select one scalar noise model for the mice. [Murphy et al., 2014](https://doi.org/10.1371/journal.pcbi.1003854), [Cohen and Maunsell, 2009](https://doi.org/10.1038/nn.2439).

**Inference:** the failed postdecision-delay pilot did not test variable sensory encoding, delayed accumulation onset, within-trial selection or correlated sensitivity states. Conversely, the failure is not a reason to add all these mechanisms. Each needs a separate behavioral prediction and a demonstration that this dataset can distinguish it.

The aligned trial table reviewed here has history, session, position and schedule variables, but no pupil or movement columns. Unless an already acquired independent measure is found elsewhere, use terms such as “sensitivity variation,” “bias state” or “behavioral regime.” A parameter estimate alone does not justify “attention,” “arousal” or “locus coeruleus mechanism.”

## 4. Gain is plausible, but iid positive gain is only a candidate

A multiplicative drift-rate scaling model for fluctuating stimuli already appears in the computational literature. Thus replacing an additive offset with stimulus scaling is a defensible model comparison, not a new general principle. The published framework is a confidence model and does not establish that the proposed positive distribution explains these pulse/RT data. [Calder-Travis et al., 2023](https://doi.org/10.1016/j.jmp.2023.102815).

Neuronal gain fluctuations can be correlated over relatively slow time scales and are affected by anesthesia. That supports testing temporal structure; it does not make neural gain synonymous with attention or with behavioral sensitivity. [Goris et al., 2014](https://doi.org/10.1038/nn.3711).

“Gain” also has several meanings. Global gain related to urgency is not the same mathematical operation as multiplying only the signed sensory input. A neural normalization model can generate different forms of attentional modulation depending on stimulus configuration. Neither result is a warrant to rename an already fitted normalization or urgency model. [Murphy et al., 2016](https://doi.org/10.1038/ncomms13526), [Reynolds and Heeger, 2009, theoretical review](https://doi.org/10.1016/j.neuron.2009.01.002).

**Inference:** simulate positive sensory gain as a minimal feasibility comparison, and ask whether independence across trials is adequate. If correlated gain is considered, serial likelihood or genuinely predictive state tests must constrain its persistence. The current condition-pooled choice/RT likelihood cannot establish that the actual temporal ordering of a latent gain process is correct.

## 5. Sensory encoding can masquerade as changed integration

A recent macaque RDK study is especially relevant: temporal context affected sensory adaptation in MT and decision behavior, while pupil-related effects provided partly separate explanatory information. The authors explicitly leave the exact accumulation algorithm unresolved. This is a current reviewed eLife report; its canonical DOI links the updated version. [McGaughey and Gold, 2026](https://doi.org/10.7554/eLife.110685).

Context-dependent gain has also been demonstrated in sequential human decisions. Importantly, Cheadle and colleagues found greater influence for evidence consistent with recent samples. That result should not be cited as a generic prediction that a surprising, strong pulse is amplified. [Cheadle et al., 2014](https://doi.org/10.1016/j.neuron.2014.01.020).

**Inference:** if state/history analyses fail to explain the mismatch, look for a specific encoding signature: dependence on baseline coherence, signed local context, pulse magnitude relative to baseline, or onset timing. A new encoder must explain sustained evidence as well as pulses. Static power laws and the previous normalization family have already failed to resolve the problem; their negative results should remain visible.

Pulse-evoked alerting is a lower-priority possibility. It predicts consequences of pulse presence beyond a signed choice shift. Use the existing all-scheduled response analyses and directional/shared decomposition rather than treating a nonsignificant shared component as proof that alerting is absent. There is currently no established attention-capture result in these data.

## 6. Persistent perturbation effects constrain a model without uniquely identifying memory

Temporal weights can reflect stimulus strategy, bounds, integration and variable delays. Recurrent circuit models can also reproduce persistent pulse effects and timing dependence. These observations motivate forward prediction, rather than reading an integration time constant directly from a response-conditioned curve. [Levi et al., 2018](https://doi.org/10.1523/ENEURO.0169-18.2018), [Okazawa et al., 2018](https://doi.org/10.1038/s41467-018-05797-y), [Wong et al., 2007](https://doi.org/10.3389/neuro.10.006.2007).

Similarly, high-coherence errors need not be attentional lapses: reward-sensitive exploration is an experimentally supported alternative in another rodent task. A guess parameter is a statistical component, not a cognitive diagnosis. [Pisupati et al., 2021](https://doi.org/10.7554/eLife.55490).

The paper should retain the distinction between evidence for accumulation relative to specified nonintegration alternatives and identification of the dynamics or source of variability. The former is not a license for the latter. [Stine et al., 2020](https://doi.org/10.7554/eLife.55365), [Hyafil et al., 2023](https://doi.org/10.7554/eLife.84045).

## What I would do next

1. **Use the existing history result to test a dynamic prediction.** Estimate repetition bias versus RT, separately after reward and error, while accounting for current evidence, pulse schedule and session. Compare it with predictions from history-dependent drift bias and starting point. Preserve actual trial chronology and assess effects per mouse.
2. **Test residual persistence.** Determine whether choice bias and RT remain serially structured beyond simple history and session trends. Only then compare a small HMM with continuous changes; validate states through held-out RT/pulse predictions, not in-sample choice accuracy.
3. **Run a bounded gain feasibility simulation.** Use the current schedules and forward estimators. Check whether plausible sensitivity variation can jointly broaden the relevant RT distributions and preserve the sustained pulse effect before launching new fits.
4. **Fit the one alternative supported by those diagnostics.** Require joint choice/RT adequacy, both pulse signs and coherence sensitivity, followed by recoverability and parameter uncertainty. A candidate improving one constraint while preserving the original failure has not resolved point 3.

These steps are specified more concretely in [NEXT_ANALYSES.md](NEXT_ANALYSES.md). They are recommendations; no new model fits or behavioral statistics were produced during this review.

## Publication story and its limits

A defensible current statement is: **mice use evidence over time, while transient perturbations expose limitations in models that explain ordinary choice/RT variability.** A stronger conditional statement, if validated, would be that the perturbations distinguish predictable bias or sensitivity variation from independent directional drift fluctuations. That is a hypothesis to demonstrate, not the present result.

“Mice accumulate” and “mice change behavioral strategies” are already established. A recent cross-species accumulation framework is also a close comparator. Novelty would need to lie in what the perturbation reveals about otherwise confounded sources of variability, with predictions beyond the residual that prompted the model. [Odoemene et al., 2018](https://doi.org/10.1523/JNEUROSCI.3478-17.2018), [Chakravarty et al., 2025, reviewed preprint](https://elifesciences.org/reviewed-preprints/105116).

For a Neuron submission, my assessment is that a better fit in two diagnostic mice would be insufficient. A stronger route using existing data is a compact validated account across the cohort, an explanation of the informative failures, and a general demonstration through recovery/theory or a compatible public dataset. Circuit-specific attention claims would require independent observations that a behavioral fit cannot provide. The specificity available from neural recordings and intervention in decision-termination work is a useful benchmark, not a requirement this study can satisfy by changing terminology. [Stine et al., 2023](https://doi.org/10.1016/j.neuron.2023.05.028).

## Search, verification and limitations

The review builds on the earlier accumulation/pulse review and adds targeted searches across decision variability, attention, arousal, history, strategy states and sensory adaptation. Sources include PubMed records via Europe PMC, publisher/author reports, independent OpenAlex discovery and Crossref identity checks. Search strings and bounded result sets are saved. Large OpenAlex result totals are not screening counts; some broad hits concern machine-learning attention and were not used.

The bibliography contains 32 selected reference records, including background/theoretical reviews and earlier accumulation comparators. Twenty-six DOI identities were freshly checked against Crossref. Ten XML bodies were retrieved and parsed with a metadata-only safeguard; additional author PDFs/PMC text supported selected full-text assessment. The matrix distinguishes these from abstract-only and earlier-review assessments. Reports using related datasets are not counted as independent replications. No meta-analysis or exhaustive screening claim is made.

Several XML requests returned HTTP 500 and some publisher pages presented bot challenges. Those failures are access limitations, not evidence against the papers. Bibliography authors come from Crossref/Europe PMC: the JATS contributor parser can include editors/reviewers in some eLife documents. The gain/confidence paper is bibliographically 2023 despite an earlier local retrieval key containing 2024; Nunez’s attention paper has an online 2016 date and a 2017 issue date.

The repository virtual environment lacked `requests`, needed by the bundled citation scripts. The existing system Python already supplied it, so citation generation/validation used that environment without installing or upgrading anything. Citation identity and claim support were checked separately; a valid DOI is not proof of a scientific claim. Checks for correction/retraction metadata are limited to the records accessed and do not certify the absence of all notices.

The [verified bibliography](references_verified.bib) preserves the raw API-derived export separately. It corrects electronic-page range formatting, obtains the Wong article locator from its XML, and represents the Chakravarty report as reviewed preprint content rather than a conventional journal article. Validation finds no structural errors or duplicates; two remaining warnings concern hyphens within article identifiers, which must not be changed into page ranges.

Workflow guidance used the pinned literature-review, paper-lookup and citation-management skills. Their procedural source is acknowledged as [Kassis et al., 2026, Scientific Agent Skills](https://arxiv.org/abs/2609.00065); it is not evidence about decision-making. No unpublished data were sent to external AI services.
