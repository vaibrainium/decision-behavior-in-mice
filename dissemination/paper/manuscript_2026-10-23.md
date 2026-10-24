# Brief motion pulses constrain models of evidence accumulation in mice

**Working draft — not for submission.** Version 2026-10-23, story-integration pass: adds the assignment-based pulse effect, its response time course and the existing-model diagnosis. Evidence markers identify sources requiring author verification. The exploratory pulse-filter pilot remains outside the manuscript claims pending its independent check.

Draft records: [sources](sources_2026-10-23.json), [claim registry](claims_2026-10-23-v2.csv), and [numerical consistency registry](consistency_2026-10-23-v2.json). Human source verification remains pending.

## Abstract

Models that integrate sensory evidence and models that respond to individual strong samples can produce similar choices and response times. We asked whether candidate models fitted to unperturbed behaviour also predicted the effect of brief motion pulses in a reaction-time random-dot task. [claim:C079] [evidence:E001,E002]

Ten mice performed the task across two rigs. On held-out control trials, an accumulator outperformed a rapid-forgetting approximation to extrema detection by 345.7 summed negative-log-likelihood units; six mice exceeded the working 10-unit criterion in favour of the accumulator and none did so in favour of rapid forgetting. Randomized pulse direction shifted responses toward the pulse by 5.84 percentage points (95% confidence interval, 1.80–9.89; Holm-adjusted p = 0.019; n = 10 mice), with most of the response-associated difference emerging 0.5–2 s after pulse onset. [claim:C080] [evidence:E019,E024,E025,E026]

The fitted models predicted an earlier pulse effect followed by partial reversal. In the two informative mice, gains improving choices substantially worsened response-time prediction. Original and gain-revised predictive gates failed; the pulse comparison had low strategy sensitivity; and the planned temporal-weighting test was not run. Control behaviour therefore favours accumulation within the tested pair, whereas pulses expose a shared predictive limitation without identifying primacy or a unique mechanism. [claim:C081] [evidence:E020,E021,E022,E028]

## Introduction

Perceptual decision tasks ask how an observer uses uncertain sensory information to select an action. A central distinction is whether the observer combines successive samples of evidence or responds when an individual sample is sufficiently strong. These strategies can produce similar choices and reaction times: Stine and colleagues showed that several familiar behavioural signatures, and even successful fits of integration models, can arise from non-integration strategies. Establishing integration therefore requires an explicit comparison with alternatives (Stine et al., 2020). [claim:C003] [evidence:E001]

Brief stimulus perturbations provide a way to test predictions outside the conditions used for fitting. In our task, a pulse temporarily replaces the ongoing motion coherence with strong motion in one direction. We fit candidate strategies to trials without scheduled coherence changes and ask how well their predictions transfer to pulse trials. The comparison concerns the effect of the perturbation as well as overall choice prediction. [claim:C004] [evidence:E002,E006]

Temporal weighting presents a related problem. In a reaction-time task, the influence of a pulse depends on whether the decision is still sensitive to incoming evidence when the pulse arrives. An apparent preference for early evidence therefore needs a model-based interpretation. More generally, psychophysical reverse correlation reflects decision processes as well as sensory weights (Okazawa et al., 2018). [claim:C005] [evidence:E007,E002]

Here we characterize the motion signal presented on each trial, evaluate models of unperturbed behaviour, and test their predictions for brief motion pulses. We compare an accumulator without leak with a model that rapidly forgets previous evidence, used as an operational approximation to extrema detection. Temporal weighting is a secondary question: a primacy claim requires departures from an adequate baseline prediction and sufficient sensitivity to detect those departures. [claim:C006] [evidence:E002,E006]

## Results

### Mice performed a reaction-time motion discrimination task on two rigs

Ten mice performed a task in which they reported the direction of random-dot motion by licking the left or right port. Four mice were tested on the UCLA rig and six on the UW rig, contributing fifty mouse-sessions. A response could register after a minimum viewing time of 0.3 s. The descriptive dataset contained 25,508 responses within the analysis window and 4,537 trials with a later or missing response (Fig. 1). [claim:C007] [evidence:E003]

Motion strength varied across trials. On pulse trials, a brief period of either +100% or −100% coherence replaced the baseline motion. Both rigs included early and middle pulses; only UW included late pulses. UW pulse onsets were 50, 233 and 417 ms, with a duration of approximately 67 ms. UCLA onsets averaged 61 and 241 ms, with a standard deviation of 15 ms and a duration of approximately 51 ms. These differences require within-mouse timing contrasts and a separate analysis of the UW late pulses. [claim:C008] [evidence:E003,E002]

Behaviour included both fast errors and a substantial tail of late responses. On control trials, responses faster than 0.6 s accounted for 12% of responses on UCLA and 21% on UW, averaged across mice within each rig. At 100% coherence, these fast responses were 58% correct compared with 88% for slower responses, averaged across mice. The mean fraction of control trials with a later or missing response at the 5 s cutoff was 0.165 on UCLA and 0.133 on UW. These features motivated explicit treatment of fast responses and censoring in the models. [claim:C009] [evidence:E003]

The 5 s cutoff was an analysis choice rather than a common task deadline. Examination of the original response records showed that most censored trials in each mouse were responses occurring after this cutoff, and their accuracy varied with coherence. We therefore retain their contribution to the probability of responding by the cutoff without treating them as stimulus-independent lapses. [claim:C010] [evidence:E008]

### Stimulus reconstruction quantified the evidence associated with motion pulses

We regenerated stimuli from their trial seeds and rig-specific implementations, and computed direction-opponent motion energy using causal spatiotemporal filters. Replays extended to 5 s, allowing simulated decisions to continue beyond the observed response time without ending the evidence stream at the animal's response. Motion energy was calibrated separately for each rig into equivalent coherence units (Fig. 2). [claim:C011] [evidence:E009,E006]

After calibration, mean motion energy tracked programmed coherence approximately linearly. The descriptive fits had slopes of 1.013 for UCLA and 1.012 for UW, with correlations of 0.998 and 0.997, respectively. At zero programmed coherence, the standard deviation across trials of the time-averaged motion energy was 3.7% equivalent coherence for UCLA and 6.3% for UW. The measured pulse response peaked approximately 117 ms after pulse onset on both rigs. These are properties of the replay and filter output, not estimates of neural latency. [claim:C012] [evidence:E003]

### Persistent stimulus bias was associated with choices

In both stimulus implementations, non-coherent dots retained their assigned motion direction during a trial. Finite sampling of these directions produced a seed-dependent net horizontal bias, termed hidden coherence. At zero programmed coherence, its standard deviation was approximately 3.3% on UCLA and 5.9% on UW. Hidden coherence correlated with time-averaged motion-energy noise at zero coherence, with correlations of 0.87 and 0.97, respectively. Thus an important component of stimulus noise persisted within a trial rather than supplying independent fluctuations at successive times. [claim:C013] [evidence:E004,E009]

On the notebook's control-trial set, the estimated hidden-coherence coefficient was positive in eight of ten mice. A one-sided Wilcoxon signed-rank test across mice gave an unadjusted p value of 0.0186. This result supports an association between choices and the trial's persistent bias; its group-level sampling unit is the mouse. [claim:C014] [evidence:E004]

A model with mouse-specific intercepts and nominal-coherence slopes, but a shared hidden-to-nominal weight ratio, estimated that ratio as 0.50, with a 95% profile-likelihood interval of 0.15–0.90. This interval is conditional on the shared-ratio model. A separate paired comparison of the hidden and nominal coefficients across mice gave an unadjusted p value of 0.492. We therefore distinguish the reduced shared weight estimated by the pooled model from evidence for a consistent discount across the mouse population (Fig. 3, pending). [claim:C015] [evidence:E004]

The persistence of stimulus bias limits the interpretation of noise-based temporal kernels in this dataset. When evidence fluctuations remain correlated over time, an association between choice and motion energy at a particular time does not isolate the weight assigned at that time. We consequently use the externally scheduled pulses and explicit model predictions to address strategy and temporal weighting. [claim:C016] [evidence:E004,E009,E002]

### Control trials supported drift variability and a fast-response component

We compared models driven by each trial's reconstructed motion energy. Candidate mechanisms included leak, urgency, across-trial drift variability, starting-point variability and a stimulus-independent response component. The selected common model retained drift variability and fast guesses, with leak and urgency reserved for a secondary baseline. This selection specifies a predictive model; interpretation of the fitted components also depends on recovery and fit quality. [claim:C017] [evidence:E005,E010,E011]

Cross-validation restricted to control trials supported the two retained components. Removing drift variability increased summed held-out negative log likelihood by 1,017.8, and removing guesses increased it by 858.1. The deterioration exceeded 10 negative-log-likelihood units in eight of ten mice for drift variability and seven of ten for guesses. Relative to the common model, adding leak changed the summed score by −21.3, adding urgency by +25.8, and adding both by −33.3; negative values favour the extension. Improvements were concentrated rather than shared by most mice. [claim:C018] [evidence:E005]

These score differences require an assessment of simulation noise. Repeated evaluation of the earlier all-trial model comparisons, using fifty simulation repetitions and ten evaluation seeds, yielded median per-mouse standard deviations of approximately 4.1–5.9 negative-log-likelihood units across the comparisons. This quantifies Monte Carlo uncertainty in model scoring, separately from uncertainty across trials or mice. The control-only comparison used an approximate threshold of 10 units and had several remaining optimization discrepancies between nested models. [claim:C019] [evidence:E010,E005]

Allowing the fast-guess component to have a directional bias improved summed held-out negative log likelihood by 65.5 compared with fixing guess direction at chance. Improvements exceeded 10 units in three mice, with no deterioration above that threshold in any mouse. We retained the free-bias form. Stimulus independence of these responses therefore does not imply that left and right guesses are equally likely. [claim:C053] [evidence:E019]

The common model captured the broad psychometric and correct-response-time patterns but retained systematic misfit. At some high coherences, error responses were faster in the observations than in the predictions; the late-response fraction was also underpredicted at high coherence in several mice. These checks use all-trial fits evaluated on control trials and describe fit quality, rather than independent predictive performance on pulse trials. [claim:C054] [evidence:E019]

Final all-trial fits of the common model, with fifty simulation repetitions per evaluation, gave a median drift gain of 2.91 (range across mice 0.73–5.70), drift variability of 2.37 (0.40–2.99), fast-guess probability of 0.21 (0.12–0.35) and fast-guess bias toward rightward responses of 0.55 (0.37–0.76). Median bound separation was 7.9 (3.6–9.5), and median non-decision time was 0.12 s (0.00–0.49 s); drift gain and bound separation are in units of the motion-energy input with unit diffusion variance. Several estimates lay at a parameter bound: bound separation at its upper limit in two mice, drift variability in one, and non-decision time near zero in two, which is possible because the motion-energy filters already introduce a delay of about 116 ms. Guess-delay estimates reached their upper limit in three mice and are not interpreted, because that parameter was not recovered. [claim:C078] [evidence:E023,E019]

### Recovery supported the fast-response component with limits on mechanism interpretation

The recovery set contained 500 fits: five generating models, five candidate models, ten mice and two simulated replicates per generating model and mouse. At the working 10-unit held-out threshold, the guess component was detected in all twenty datasets generated from the common model and was falsely selected in three of twenty datasets generated without guesses. Corresponding rates for drift variability were seventeen of twenty detections and seven of twenty false selections. These are pooled descriptive simulation rates with only two replicates per mouse, not precise population detection probabilities. [claim:C055] [evidence:E019]

Leak and urgency were detected in seven and nine of twenty corresponding generating datasets, respectively, with three of twenty false selections for each. In several mice the fitted generating parameters were close to their off values, limiting the interpretation of these exercises as tests of distinguishable mechanisms. The fitted training score was no worse than the score at the generating parameters in all matched-model fits. This checks the optimizer against one available solution and does not prove global optimality. [claim:C056] [evidence:E019]

Within the common-model recovery set, correlations between generating and recovered parameters were 0.92 for drift gain, 0.93 for guess probability and 0.85 for drift variability. The exponential guess-delay parameter was poorly recovered (r = 0.18), so its fitted values are not given a mechanistic interpretation. These correlations pool mice and simulated replicates and do not establish parameter precision within an individual mouse. [claim:C057] [evidence:E019]

### Testing integration against rapid forgetting

The control-trial comparison favoured the integrator over the rapid-forgetting model. Summed across control-only cross-validation folds and mice, extrema minus integrator negative log likelihood was +345.7. Per-mouse differences ranged from +0.9 to +134.2, exceeding the working threshold of 10 units in six mice and in none in the opposite direction. The four remaining mice had differences below four units and did not clearly distinguish the candidates. These comparisons favour the integrator within the tested model pair; the working threshold concerns approximate Monte Carlo scoring variability and is not a population significance test. [claim:C058] [evidence:E019]

The extrema fits did not hit the drift-gain upper bound, so the prespecified gain-bound refit criterion was not triggered. Drift variability reached its upper-bound neighbourhood in two of sixty extrema fits and ten of fifty control-CV integrator fits. Bound effects therefore remain a caveat for both candidates, even though the specific gain restriction anticipated for extrema detection did not bind. [claim:C059] [evidence:E019]

A descriptive model allowing leak anywhere from zero to 200 s⁻¹ fitted all control trials with leak below 1 s⁻¹ in every mouse, far from the 20–200 s⁻¹ extrema range. These fits scored at least as well as both restricted candidates in sample. The result is consistent with slower forgetting within this model family, but without uncertainty intervals the fitted reciprocal leak values should not be read as precise biological integration times. [claim:C060] [evidence:E019]

### Randomized motion pulses shifted response direction

Pulse assignment was randomized within coherence and was not announced to the mouse in either task implementation. The exploratory assignment-based analysis retained trials with no response by 5 s and trials on which the response preceded the scheduled pulse. Positive and negative pulses were compared within mouse × session × signed coherence × onset cells at absolute baseline coherence no greater than 36%. Cells lacking both pulse signs were excluded, and mice contributed equally to the group estimate. [claim:C082] [evidence:E024]

Across mice, assignment to a rightward rather than a leftward pulse shifted responses toward the pulse direction by 5.84 percentage points (95% Student-t confidence interval, 1.80–9.89; n = 10 mice; standardized within-mouse effect d_z = 1.03; Holm-adjusted p = 0.019). Nine mice had positive estimates. The primary common-support analysis contained 10,281 pulse trials in 717 matched cells, including 118 responses before onset and 1,709 trials with no response by the deadline (Fig. 4A). [claim:C083] [evidence:E024,E025]

The contrast was expressed mainly through redirection rather than a common change in response probability. Right responses increased by 4.81 percentage points (95% confidence interval, 0.47–9.16), left responses decreased by 6.88 points (−10.97 to −2.78), and no response by 5 s increased by 2.07 points (−0.36 to 4.49). These three components sum to zero within mouse. [claim:C084] [evidence:E025]

Relative to matched controls, rightward pulses shifted the directional response by 4.86 percentage points (95% confidence interval, 2.43–7.29; Holm-adjusted p = 0.0043), whereas the control-versus-leftward contrast was 1.40 points (−2.13 to 4.92; p = 0.393). The two estimates use different supported cells, and their magnitudes do not establish an asymmetry between pulse directions. Alternative pseudo-onset seeds for UCLA controls changed either estimate by no more than 0.2 points (Fig. 4B–C). [claim:C085] [evidence:E025]

### The pulse-associated response difference emerged after the physical pulse

Pulse-aligned cumulative response curves reproduced the directional effect. Across all scheduled trials, the contrast reached 5.80 percentage points (pointwise 95% confidence interval, 1.82–9.78) by 4.58 s after pulse onset. It was small during the first 0.5 s and grew mainly from 0.5 to 2 s: the increments were 3.21 points from 0.5–1 s and 2.12 points from 1–2 s, with little additional change later (Fig. 4D). [claim:C086] [evidence:E026]

This time course locates emitted responses associated with pulse assignment, not the time at which pulse evidence entered or persisted in the decision process. A cumulative difference at a late time carries forward earlier divergence, and the pointwise intervals do not test an early-versus-late weighting contrast. Averaging across pulse signs also revealed no clear common effect on whether or when mice responded by the shared endpoint. [claim:C087] [evidence:E026]

Simulation checks kept the observed schedules, trial counts and censoring while generating known directional effects. Across 200 datasets per scenario, the primary estimator had absolute bias no larger than 0.17 percentage points and its t interval covered the generating value in 93–97.5% of datasets. The Holm-corrected test had estimated power 0.64 for a 6-point effect and 0.21 for a 3-point effect. These simulations support the primary estimator under the tested generators but show that smaller secondary effects remain weakly constrained. [claim:C088] [evidence:E029]

### The stimulus audit did not reveal a comparable directional artefact

In paired same-seed replays, pulse-present and physically omitted stimuli were identical before pulse onset. Returning from the pulse redrew background-dot directions and added trial-specific motion noise, but its mean was not detectably aligned with pulse direction. A deterministic rounding asymmetry left a 0.2–0.66% coherence shift in specified cells, approximately 0.1% when averaged over pulses. The motion-energy pulse template matched the paired replay mean within 10% over the first 333 ms; an unresolved UCLA acquisition alternative could increase pulse energy by a factor of 1.28–1.40. These checks make a large sustained directional stimulus artefact unlikely while leaving uncertainty in the absolute pulse-energy scale. [claim:C089] [evidence:E027]

### The fitted model misplaced the pulse effect in time

Using the same cells and weights as the behavioural curves, the gain-revised accumulator placed most of its directional effect in the first second and then partly reversed it. At the choice-optimal gain, observed versus predicted increments were 0.39 versus 3.0 percentage points at 0–0.5 s, 3.21 versus 4.72 at 0.5–1 s, 2.12 versus 0.25 at 1–2 s, and 0.12 versus −2.98 at 2–4.58 s. The secondary baseline with leak and urgency showed the same late reversal (Fig. 5A–B). [claim:C090] [evidence:E026,E028]

Choices and response times constrained pulse gain differently in the two mice with the densest response-time data. Their choice-only optima were gains of 7 and 4, compared with joint optima of 2.45 and 1.40. Moving to the choice-optimal gain improved held-out choice score by approximately 10 negative-log-likelihood units in each mouse but cost approximately 96 and 107 units in the remaining response and response-time objective. Choice data weakly constrained gain in most other mice, so a cohort-wide gain conflict is not established. [claim:C091] [evidence:E028]

The mismatch therefore concerns the joint temporal prediction, not pulse amplitude alone. The behavioural response difference emerged later and remained positive, whereas increasing pulse gain amplified an early model effect and its subsequent reversal. This identifies a predictive limitation of the fitted model family; it does not determine whether the missing process is sensory, decisional or response-related, and it does not establish the absence of accumulation. [claim:C092] [evidence:E027,E028]

[[AUTHOR NOTE: the bounded tau-p pulse-filter pilot has a recorded negative outcome but is awaiting its planned independent implementation/criteria check. Keep it out of the formal claims and place it in a Figure 5 supplement only after that review.]]

### The tested strategies made similar pulse predictions

All thirty prediction files, covering ten mice and three candidate baselines, were frozen with the prediction-code commit and SHA-256 checksums before comparison with recorded pulse outcomes. Each used 200 repetitions per trial. At absolute coherence at most 36%, mean within-mouse predicted pulse effects under the integrator were 0.028, 0.029 and 0.027 logit for early, middle and late pulses, respectively; late estimates include only UW mice. Corresponding extrema predictions were 0.040, 0.039 and 0.035 logit. Thus the candidates fitted to control trials predicted similar pulse effects, differing by approximately 0.01 logit. [claim:C062] [evidence:E020]

Synthetic sensitivity analysis used twenty full-cohort datasets generated from each candidate and scored using the frozen predictions. The prespecified pulse-specific rule selected the extrema generator in one of twenty extrema-generated datasets and the integrator in none of twenty integrator-generated datasets; all other pulse-specific verdicts were not distinguished. The secondary total-choice-likelihood rule selected the generating model in five of twenty extrema datasets and seven of twenty integrator datasets. These limited simulations show low discrimination under the fitted candidates and frozen-prediction procedure, rather than establishing a precise detection probability or lack of a behavioural difference. [claim:C063] [evidence:E020]

### Both baselines failed the first pulse predictive check

The first observed comparison used frozen predictions from control-only fits evaluated with fifteen simulation repetitions during fitting. For the primary integrator, the pooled choice departure toward the pulse was +0.296 logit, with a 95% posterior interval of 0.175–0.405, against a mean predicted pulse effect of 0.030 logit. For the secondary baseline with leak and urgency, the departure was +0.317 logit (0.209–0.408), against a predicted effect of 0.026. Both failed the choice component of the prespecified predictive gate. This departure describes calibration on pulse-trial choices and is not itself a direct causal estimate of pulse magnitude. [claim:C065] [evidence:E021]

Observed reaction-time quantiles fell within the simulated ranges in 34 of 50 mouse-by-quantile cells for each baseline, below the required fraction of 0.80. Censored fractions were within range in nine of ten mice for the primary model and five of ten for the secondary model. Thus choice and reaction-time failures both contributed to overall inadequacy. Each gate fit had one sampling divergence, despite reported maximum R-hat of 1.00; exact interval values remain subject to diagnostic review. [claim:C066] [evidence:E021]

Timing-agnostic exploratory diagnostics also found underprediction on zero-coherence trials, where the scheduled pulse was the programmed directional signal: pooled choice probability toward the pulse was 0.574 observed and 0.508 predicted across 1,388 responded trials. This is a descriptive pooled comparison, not a mouse-level effect estimate or randomized pulse-versus-control contrast. Departures varied between mice, and site, cohort, rig and training cannot be separated in this dataset. [claim:C067] [evidence:E021]

### Pulse outcomes did not distinguish the tested strategies

The prespecified pulse-associated likelihood-gain difference was +5.414 in favour of the extrema approximation, with estimated sampling standard deviation 1.825, giving z = 2.966. Eight of ten mouse-level sums had the same sign. The result did not meet the threshold of three standard deviations and was classified as not distinguished. The secondary total-choice-likelihood difference was −8.576, with standard deviation 11.613 and z = −0.738, also not distinguished. The near-threshold primary result is reported without rounding it into a positive decision. [claim:C068] [evidence:E021]

Given the failed gate and low synthetic discrimination, this comparison does not independently corroborate the control-trial preference for integration. The extrema model's somewhat larger predicted pulse effect can improve pulse-associated likelihood gain without adequately predicting the observed pulse sensitivity; this interpretation remains exploratory. [claim:C069] [evidence:E021,E020]

### Temporal weighting conditional on predictive adequacy

The confirmatory early-versus-middle timing test and UW late-pulse timing tests were not run on the prespecified baselines because both failed the predictive gate. [claim:C070] [evidence:E021]

### A pulse-gain revision also failed the predictive check

After the gate failed, and before any timing contrast was computed, the plan was amended to add one pulse gain per mouse, a weight on the pulse component of the motion-energy input that is the same at every pulse timing. The gain was fitted by five-fold cross-validation over each mouse's pulse trials, so each trial's prediction used a gain estimated without that trial. This is a model revision prompted by the observed failure, not part of the original confirmatory design. [claim:C072] [evidence:E002,E022]

Fitted gains for the primary integrator ranged from 0.06 to 7.0 across mice, against 1 for the unrevised model, and were poorly constrained in mice with few pulse trials. With the revised baselines, the pooled choice departure toward the pulse was +0.24 logit (95% interval 0.09–0.37) for the primary integrator, against a mean predicted pulse effect of 0.057, and +0.31 (0.20–0.41) for the secondary baseline. Reaction-time quantiles fell within the simulated ranges in 62% and 70% of mouse-by-quantile cells. Both revised baselines failed the gate. [claim:C073] [evidence:E022]

Descriptively, the revised integrator still underpredicted choices toward the pulse on zero-coherence trials (0.574 observed, 0.512 predicted). It overpredicted pulse influence when a 36%-coherence stimulus opposed the pulse. A single gain that also changes response times did not reproduce the observed pulse sensitivity; this interpretation is exploratory. [claim:C074] [evidence:E022]

### Calibration of the revised procedure and the stopping decision

Synthetic datasets generated from each mouse's revised model, with and without a declining drift gain, were passed through the whole revised procedure: gain fitting, out-of-fold prediction, gate and timing test. Without a decline, the gate passed in 19 of 20 datasets and the timing test made no false detections. With drift gain declining by 10%, 20% or 40% over the first 0.5 s, the timing test detected the decline in 0, 1 and 0 of 20 datasets. Control-trial parameters were held at their fitted values in these simulations. [claim:C075] [evidence:E022]

Under the prespecified stopping rule, the temporal-weighting analysis ends here: the timing test is not run, the planned mechanism extensions with declining drift gain or signed leak are not run, and no further baseline revision is made. These data therefore do not support a model-adjusted claim of primacy, recency or flat temporal weighting, and the calibration indicates that the design could not have resolved moderate primacy. [claim:C076] [evidence:E022,E002]

## Discussion

This study separates three questions that can otherwise be conflated. On control trials, held-out prediction favoured the tested accumulator over a rapid-forgetting approximation. Randomized pulse direction produced a reproducible directional response shift. Yet the fitted models did not reproduce when that shift appeared in the response distribution, and the pulse data could not distinguish the candidate strategies with adequate sensitivity. The resulting claim is a relative preference among specified control-trial models together with a demonstrated failure to generalize to brief strong perturbations. [claim:C093] [evidence:E019,E020,E024,E025,E026,E028]

The pulse manipulation supplies evidence that is useful even without a resolved mechanism. Because assignment preceded behaviour and the primary analysis retained early responses and no-response trials, the directional contrast estimates the effect of assignment within the supported trial population without conditioning on post-pulse response time. Its expression through opposite changes in left and right responses, together with the absence of a clear common response burst, is consistent with redirection of decisions. The analysis was nevertheless developed after the original predictive procedure failed and remains exploratory. [claim:C094] [evidence:E024,E025,E026]

The model diagnosis narrows the problem more than an overall goodness-of-fit statement. Increasing pulse gain can improve choices, but in the informative mice it worsens response-time prediction and preserves a late partial reversal that is absent from the data. Leak and urgency in the secondary baseline do not resolve that temporal pattern. Sensory persistence, a decision-process mismatch and response-generation mechanisms remain viable explanations; the current data do not identify one of them uniquely. [claim:C095] [evidence:E027,E028]

The stimulus analysis identifies a limitation of interpreting temporal kernels in these particular random-dot implementations. A trial's random seed introduces a persistent motion bias, and choices are associated with this bias. Such associations establish sensitivity to stimulus variation, but their temporal extent need not measure the duration of integration. The conclusion concerns the measured correlation structure of these stimuli and should not be generalized to random-dot displays whose noise is independently refreshed. [claim:C020] [evidence:E004,E009]

The shared hidden-coherence weight provides a compact description of behaviour, but its interpretation remains conditional. Spatial pooling over only part of the screen could make the whole-screen bias an imperfect predictor, and the motion-energy representation need not match the animal's representation. Moreover, the paired coefficient comparison across mice did not establish a systematic reduction. These alternatives limit an interpretation in terms of a uniform discount applied by mice. [claim:C021] [evidence:E004]

The behavioural models address fast responses and late trials, but successful prediction does not identify a unique decision algorithm. An extrema strategy can mimic signatures commonly attributed to integration (Stine et al., 2020). Our comparison therefore asks whether predictions made from control trials generalize to perturbations. Even if one candidate predicts better, that result distinguishes the tested implementations rather than excluding every alternative strategy. [claim:C022] [evidence:E001,E002]

Several limitations bound the interpretation. Rig and cohort are confounded, and late pulses occur only on UW. The minimum-response-time rule is approximated on UW, whose response window registers a new lick onset rather than an existing contact. UCLA replay does not reproduce the display-loop timing exactly. Motion-energy analysis uses a fixed spatial scale without correcting the screen's visual-angle geometry, and non-decision time is estimated without a separate speeded-response measurement. Each can affect the mapping between stimulus time, decision time and response time. [claim:C023] [evidence:E008,E009,E002]

Sensitivity differs between strategy discrimination and temporal weighting. Under the fitted candidates, the completed strategy simulation rarely selected the generating model using the pulse-specific statistic. The similar frozen pulse predictions therefore limit the perturbation comparison's ability to corroborate the control-trial preference. This strategy simulation does not establish sensitivity to gain decay or primacy. The separate calibration of the revised temporal-weighting procedure showed low sensitivity to a declining evidence weight. An inconclusive or unreached comparison does not establish equivalence or absence of primacy. [claim:C024] [evidence:E020,E022,E002]

## Methods

### Animals and experimental oversight

[[MISSING:strain, sex, age at testing, animal provenance, housing, water restriction and welfare monitoring; ethics bodies and protocol identifiers for each site. Supply actual records.]]

### Task and experimental design

Head-fixed mice reported leftward or rightward random-dot motion by licking the corresponding port. Correct responses were rewarded and errors were followed by a timeout. Responses were eligible after 0.3 s of viewing. Reaction times were expressed relative to motion onset; UW recorded response time relative to opening of the response window, and preprocessing added the minimum viewing interval. [claim:C025] [evidence:E003,E008]

The absolute coherence levels represented in the behavioural figures were 0%, 9%, 18%, 36% and 100%, with signed coherence indicating direction. Scheduled pulses replaced baseline coherence with ±100% motion. Pulse timing differed by rig as described in Results. The UCLA stimulus could continue up to 60 s; UW stimulus durations varied, whereas the modelled window ended at 5 s. This cutoff defines censoring and is not used as a description of the task's response deadline. [claim:C026] [evidence:E003,E008,E006]

[[MISSING:training stages and performance criteria, allocation and randomization of trial conditions, session selection and exclusion rules, stopping criteria, and rig hardware/display dimensions. Reconcile these with preprocessing before finalizing sample selection.]]

### Analysis sets and pulse labels

Descriptive figures combine the processed valid-response and censored-trial tables. DDM inputs exclude fifteen trials with invalid pulse durations, leaving 25,493 responses within the modelled window and 4,537 censored trials. The different descriptive and modelled denominators are retained explicitly. Censored model outcomes have infinite response time and an unspecified choice; actual responses after the cutoff are not treated as choices within the window. [claim:C027] [evidence:E003,E006,E010]

Behavioural figures and model analyses use scheduled pulse labels recovered from the pulse flag, coherence change and onset. They retain trials on which a response occurred before or during the scheduled pulse. The earlier preprocessing label can reclassify such trials as controls, making pulse grouping depend on response time. The hidden-coherence notebook uses that earlier control definition; it is therefore a distinct analysis set and is not described as the control-only model-fitting set. [claim:C028] [evidence:E006,E004]

[[TODO:assess whether a scheduled-control sensitivity check materially changes the hidden-coherence estimates before treating that analysis as final. The existing notebook includes responses during partially delivered pulses among its earlier-label controls.]]

### Stimulus reconstruction and motion energy

Trial stimuli were regenerated using the recorded random seed and rig-specific replay implementations. Replays sampled a 5 s sequence at 60 Hz. Frames were rendered at native resolution and downsampled by area averaging to a common grid of 0.5° per sample. The motion-energy calculation uses quadrature filter pairs followed by a directional opponent stage, following the general energy-model construction of Adelson and Bergen (1985). [claim:C029] [evidence:E009,E013]

The spatial filter constants were σc = 6° and σg = 3°, and the temporal constant was 34 s⁻¹. Temporal support extended to 0.55 s. Filtering was causal, with initial zero padding and no contribution from future frames. Spatial padding was zero. We calibrated the output independently for each rig by its slope against nominal signed coherence. These parameter choices define the analysis representation; sensitivity to alternative filters remains to be established. [claim:C030] [evidence:E009]

For DDM inputs, the full motion-energy trace was decomposed into an expected signal S and a residual N. The expected signal combines a rig-specific response to the onset coherence and a measured response to the pulse's coherence change. The pulse response is estimated from stimulus replays after subtracting the onset response, without using choices. The model input S + N equals the reconstructed motion energy. The no-pulse counterfactual removes the expected pulse response while retaining the residual from the same trial. Input values were converted from percent coherence to coherence fractions and held constant over the corresponding intervals on a 1 ms simulation grid. [claim:C031] [evidence:E006,E011]

### Hidden coherence and choice

Hidden coherence was calculated from the seed-dependent net horizontal motion of non-coherent dots. The notebook's per-mouse logistic regressions predicted choice from nominal and hidden coherence on its control set restricted to absolute coherence at most 36%. Across-mouse tests used the hidden coefficient against zero and the paired difference between hidden and nominal coefficients. Reported p values are unadjusted; these exploratory tests should not be represented as a multiplicity-corrected family. [claim:C032] [evidence:E004]

The shared-ratio analysis fitted each mouse's own intercept and coherence slope, using nominal coherence plus k times hidden coherence as the predictor. A grid search profiled over k and used a likelihood-ratio cutoff to construct the reported interval. This interval conditions on a common ratio across mice and the fitted trial-level likelihood; it is not a bootstrap interval across subjects. [claim:C033] [evidence:E004]

### Decision models

The simulator evolves evidence between bounds at zero and a, starting at z times a. At each time step, the drift is the trial's motion energy multiplied by a fitted gain, plus a fitted offset and a normally distributed across-trial drift offset where that mechanism is enabled. Diffusion variance is fixed at one and the time step is 0.001 s. A bound crossing determines choice, and fitted non-decision time is added to the crossing time. The causal sensory filtering delay is already present in the stimulus input. [claim:C034] [evidence:E011]

Leak subtracts a term proportional to displacement from the starting point. Urgency multiplies that displacement by a linear function of elapsed time before comparison with the bounds. Starting-point variability, when enabled, introduces a uniform offset across trials. The common model sets leak, urgency and starting-point variability to zero and retains across-trial drift variability. [claim:C035] [evidence:E011,E010]

The fast-guess mixture assigns a fitted fraction of trials to stimulus-independent responses. Guess times begin at 0.3 s with an exponential delay whose mean is constrained to 0.01–0.3 s. Guess direction was compared between a free probability and a probability fixed at 0.5 for a rightward response; the free-bias form was retained for both baselines and the extrema model. Simulated response times are floored at 0.3 s, and responses later than 5 s or unresolved simulations are mapped to the censored outcome. [claim:C036] [evidence:E011,E019]

### Fitting and model comparison

Fits minimize a quantile-based negative log likelihood separately for each mouse. Within each coherence-by-condition cell, the score includes a multinomial term for left, right and censored outcomes, and separate conditional response-time histograms for each response direction. There are nine response-time bins when enough observed responses are available; simulated counts are smoothed by adding 0.5 per category. Response-time terms are omitted when fewer than nine observed responses are available for that direction, using a rule determined by the observed data. [claim:C037] [evidence:E014]

Optimization uses differential evolution followed by Nelder–Mead refinement. The fitting code sets relative differential-evolution tolerance to zero and absolute tolerance to one negative-log-likelihood unit, with a default maximum of 1,000 iterations and fifteen simulation repetitions. Warm starts were used for targeted refits where a nested larger model fitted worse than a smaller model. Cross-validation assigns trials to five folds stratified by condition; a separate comparison restricts this procedure to control trials. These folds assess prediction of held-out trials within the sampled data, not generalization to new animals or sessions. [claim:C038] [evidence:E011,E010]

Monte Carlo variability was evaluated by rescoring saved comparisons with multiple simulation seeds and more repetitions. Parsimony favoured components that improved held-out scores beyond simulation noise across most mice, with interpretability and recovery as additional requirements. Final parameter interpretation remains conditional on the recovery checks. [claim:C039] [evidence:E010,E015]

### Integration and extrema comparison

The fitted extrema approximation adds rapid forgetting to the common model, with a leak-rate range of 20–200 s⁻¹, corresponding to nominal time constants of 5–50 ms. This acts after sensory filtering and is a rapid-forgetting approximation rather than an exact discrete-sample extrema rule. Both candidates were fitted to control trials and compared using held-out control folds. The prespecified rule required repeating relevant extrema fits with the upper gain bound increased from 20 to 200 if drift gain met the upper-bound criterion; this criterion was not triggered. The implemented Euler update has a discretization effect at the largest leak values, which must accompany interpretation of time constants. [claim:C040] [evidence:E002,E011,E019]

Pulse predictions were frozen before comparison with recorded pulse outcomes, using 200 repetitions per trial and matched predictions with and without the expected pulse component. The primary strategy statistic is the difference between models in pulse-associated choice log-likelihood gain: for each model, the observed choice log likelihood with the pulse minus that without the pulse, paired across the same trials. Total choice log likelihood is secondary. The prespecified operational rule favours a candidate when the summed difference exceeds three estimated sampling standard deviations and has the same sign in at least six of ten mice. The standard deviation is constructed from within-mouse per-trial differences; this rule is not a calibrated random-effects population test. [claim:C041] [evidence:E002,E016,E020]

Strategy sensitivity was assessed with twenty synthetic full-cohort datasets from each candidate, with each dataset containing a simulation of every mouse's pulse trials. The outcomes were generated from the corresponding control-fit parameters and scored against both models' frozen predictions using the same decision rule. The analysis plan and amendments preceded model-based inspection of pulse residuals, but the raw pulse effects from the earlier poster were already known. This is not a prospectively registered experiment or a fully untouched dataset. [claim:C042] [evidence:E002,E020]

### Predictive gate and secondary temporal weighting

Primary choice analyses use responded scheduled-pulse trials with absolute coherence at most 36%. The predictive gate pools timings and assesses an overall offset from predicted choice probabilities, response-time quantiles, and the censored fraction. Its choice component passes if the 95% interval includes zero departure or the absolute mean departure is less than 25% of the mean predicted pulse effect on the logit scale. This is a screening rule, not an equivalence test. Response-time and censoring checks require at least 80% of their respective cells to fall within the simulated 95% ranges. [claim:C043] [evidence:E002,E016]

For an adequate baseline, timing effects are estimated with a Bayesian logistic mixed model whose offset is the logit of the predicted choice probability. Fixed effects include timing and rig; mice have random intercepts and timing slopes. Normal priors with standard deviation one are assigned to logit-scale fixed effects, and half-normal priors of the same scale to random-effect standard deviations. The main timing contrast is middle versus early across all mice; late-versus-early and timing trends are secondary analyses restricted to UW. Posterior intervals, directional probabilities and sampling diagnostics are to be reported. [claim:C044] [evidence:E002,E016]

The amended plan also specified separate extensions with declining drift gain or signed leak, a supplementary regression conditioned on sufficient time after the pulse, and simulations of known temporal-weight decay. The extensions were not run because the baselines failed predictive adequacy and the revised procedure had low sensitivity. The supplementary regression was deferred: its conditioning on response time selects different trial subsets at different pulse timings, and its sensitivity cannot be inferred from the model-based calibration. The decay simulations were completed for the revised procedure. [claim:C045] [evidence:E002,E022]

The pulse-gain revision scaled the pulse component of each pulse trial's motion-energy input by a mouse-specific gain between 0 and 50, with all other parameters fixed at the mouse's control-only fit at 50 simulation repetitions. The gain was fitted to the censored quantile likelihood of training-fold pulse trials by a grid followed by golden-section search, using common random numbers. Out-of-fold predictions used 200 simulation repetitions. The calibration used 20 synthetic full-cohort datasets at each of four levels of drift-gain decline (0%, 10%, 20% and 40% over 0.5 s). Generating gains were the fitted gains, and gate passing, false detections under no decline, and detections overall and conditional on the gate were reported. [claim:C077] [evidence:E002,E022]

### Exploratory assignment-based pulse analyses

The pulse follow-up used a read-only trial table joining the valid-response, censored-trial, aggregate and retained DDM-input tables by unique trial identity. Scheduled pulse direction was recovered from task fields rather than the earlier response-dependent preprocessing label. Source-code inspection showed that UW drew a pulse or sham category before each trial conditional on coherence, whereas UCLA shuffled fixed pulse categories within coherence blocks. Analyses retained assignment regardless of whether the pulse occurred before the response. [claim:C096] [evidence:E024]

The primary analysis included absolute baseline coherence no greater than 36% and compared scheduled positive and negative pulses within mouse × session × signed coherence × onset cells. A cell contributed only when both signs were represented, with weight equal to the smaller arm count and weights normalized within mouse; mice were then weighted equally. For each mouse, changes in right, left and no-response probabilities were standardized over these cells, and the directional contrast was defined as (ΔR − ΔL)/2. Group means used two-sided 95% Student-t intervals across mice. The primary contrast and two pulse-versus-control contrasts formed one Holm correction family. [claim:C097] [evidence:E024,E025]

UW controls used scheduled sham onsets. UCLA controls were assigned outcome-independent pseudo-onsets drawn from observed pulse onsets in the same session and absolute-coherence stratum with a fixed seed; five further seeds assessed sensitivity. Pulse-aligned cumulative incidence curves treated left and right responses as competing outcomes and retained no response as the third state. The shared endpoint of 4.58 s after onset fell within the available follow-up for every onset category. “Onset eligible” summaries were restricted to trials still unresponded immediately before onset; the all-scheduled curves retained every assigned trial. [claim:C098] [evidence:E024,E026]

The behavioural estimator check retained the observed design and censoring and replaced outcomes with simulations from declared null and directional-effect generators. Two hundred datasets were generated per scenario. Bias, t-interval coverage, Holm-adjusted rejection probability and mouse-bootstrap coverage were recorded; these checks assess the behavioural estimands under the specified generators and do not validate a decision mechanism. [claim:C099] [evidence:E029]

### Pulse stimulus and model diagnostics

The stimulus audit rendered paired trials from the same initial seed with the pulse either present or physically omitted. Motion-energy traces were compared before, during and after the pulse, and deterministic dot-count differences were evaluated by coherence and pulse sign. For model diagnosis, the existing censored-quantile objective was decomposed into response, choice and conditional response-time terms and checked to reproduce the original objective. Pulse gain was profiled while control parameters remained fixed; observed and simulated directional curves used the behavioural analysis's cells and weights. These analyses were developed after inspection of the failed predictive checks and are exploratory. [claim:C100] [evidence:E027,E028]

### Software and availability

The analysis implementation uses Python with NumPy, SciPy, pandas, statsmodels, PyTorch and Numba; the timing model is implemented in PyMC. Exact execution environments and final run commits must accompany the completed analyses. [claim:C046] [evidence:E017,E016]

[[MISSING:data and code release location, access conditions, final environment lock and execution records; author contributions, affiliations, funding, competing interests and acknowledgments.]]

### Drafting assistance

This working draft was prepared with Codex using the repository's scientific-writing and evidence-appraisal instructions. The authors must review the text and decide the final disclosure required by the target journal. The procedural skill library is described by Kassis and colleagues (2026). [claim:C047] [evidence:E018]

## References

Adelson, E. H., and Bergen, J. R. Spatiotemporal energy models for the perception of motion. *Journal of the Optical Society of America A* **2**, 284–299 (1985). https://doi.org/10.1364/JOSAA.2.000284. [claim:C048] [evidence:E013]

Okazawa, G., Sha, L., Purcell, B. A., and Kiani, R. Psychophysical reverse correlation reflects both sensory and decision-making processes. *Nature Communications* **9**, 3479 (2018). https://doi.org/10.1038/s41467-018-05797-y. [claim:C049] [evidence:E007]

Stine, G. M., Zylberberg, A., Ditterich, J., and Shadlen, M. N. Differentiating between integration and non-integration strategies in perceptual decision making. *eLife* **9**, e55365 (2020). https://doi.org/10.7554/eLife.55365. [claim:C050] [evidence:E001]

Kassis, T., Agarwal, V., He, Y., Patel, D., and Brueckner, A. M. Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. *arXiv* (2026). https://doi.org/10.48550/arXiv.2609.00065. [claim:C051] [evidence:E018]
