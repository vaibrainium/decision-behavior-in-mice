<!-- np-contract
stage: S2 ; section: literature ; agent: np-synthesizer ; version: v3
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021
numbers:
sources: stine2020differentiating, hyafil2023temporal, huk2005neural, stine2023termination, steinemann2024direct, parespujolras2026glimpses, zhou2009time, tsetsos2012timevarying, carland2016evidence, ratcliff2008diffusion, palmer2005effect, yates2017functional, okazawa2018psychophysical, adelson1985spatiotemporal, kiani2008bounded, kiani2013integration, hawkins2015discriminating, hawkins2015revisiting, evans2017computations, cisek2009decisions, thura2012urgency, kumano2024employment, chakravarty2025cross, luken2025parameter, wiecki2013hddm, douglas2006motion, stirman2016touchscreen, pinto2018visualpulses, marques2018mousev1, samonds2018motion, odoemene2018visual, koay2020amplitude, you2022dynamics, caballero2022rt
-->
# Gap and conflict analysis

## Defensible gap statement

The literature establishes that joint choice/RT measurements and time-varying perturbations can
separate some decision-model implementations, and recent macaque work provides strong neural and
behavioural evidence consistent with bounded accumulation. It also shows that pulse efficacy and
temporal weighting depend on sensory dynamics, commitment, strategy and response policy. The retained
Mouse continuous-RDK psychophysics, dynamic discrete visual accumulation tasks, and visual choice/RT
diffusion modelling are each established separately. In a bounded mouse-specific search, we found no
prior study combining continuous noisy RDK, randomized signed motion pulses, and a frozen control-only
model evaluated jointly against choice, response-probability and response-time outcomes. This paper
addresses that predictive-transfer question; it does not claim the first mouse dynamic-visual task,
pulse experiment, accumulation result, RDK task, joint choice/RT model, or a unique mechanism.

## Gap 1: Model-compatible behaviour does not uniquely identify the computation

- **Type:** conflict.
- **Statement:** Integration models outperform tested alternatives in several datasets, yet extrema,
  urgency and leaky/competitive accounts can reproduce common behavioural signatures or prevail under
  other task regimes. The conflict concerns task-specific implementation and identifiability, not a
  universal integration-versus-non-integration verdict.
- **Evidence:** `stine2020differentiating` shows that accuracy and flat kernels can be mimicked;
  `tsetsos2012timevarying` produces similar temporal signatures from bounded diffusion and leaky
  competition; `cisek2009decisions` and `carland2016evidence` favour urgency/leak accounts under
  changing evidence or policy; `hawkins2015discriminating` finds different winners across datasets.
- **Counter-evidence:** `hyafil2023temporal` favours integration over extrema/snapshot models across
  several datasets; `evans2017computations`, `hawkins2015revisiting` and `winkel2014early` favour
  diffusion/fixed-bound or retained-evidence accounts in their tested comparisons.
- **How this paper addresses it:** Figure 3 and C004 report a relative joint held-out comparison among
  specified control-trial implementations; C008 forbids unique mechanism identification.

## Gap 2: Within-task model selection has not guaranteed out-of-condition pulse prediction

- **Type:** untested assumption.
- **Statement:** Prior studies use pulses or time-varying evidence to compare models within designed
  perturbation tasks. The retained search did not find a quantitative test of whether joint predictive
  adequacy under ordinary continuous evidence transfers to separately randomized strong transient
  evidence in the specified pipeline, including response probability and response-time distributions.
- **Evidence:** `stine2020differentiating` establishes joint choice/RT identification without this
  control-to-pulse transfer; `stine2023termination` and `steinemann2024direct` combine bounded
  choice/RT fits with weak randomized pulses and macaque neural measurements, but do not report a
  no-pulse-only behavioural fit tested prospectively on the pulse trials; `parespujolras2026glimpses`
  fits all single- and two-pulse accuracy conditions rather than holding pulses out. In mice,
  `marques2018mousev1` supplies continuous RDK without pulse transfer, `pinto2018visualpulses` and
  `odoemene2018visual` supply discrete visual accumulation tasks, and `caballero2022rt` supplies visual
  choice/RT diffusion modelling; none contains the full bounded combination above.
- **Counter-evidence:** `huk2005neural`, `stine2023termination`, `steinemann2024direct`,
  `tsetsos2012timevarying` and `carland2016evidence` already show that pulse manipulations can constrain
  mechanisms and, in macaques, can agree with neural accumulation signals. `douglas2006motion`,
  `stirman2016touchscreen`, `pinto2018visualpulses`, `odoemene2018visual`, `koay2020amplitude`,
  `samonds2018motion`, `you2022dynamics` and `caballero2022rt` reject every broader mouse novelty claim.
  The bounded distinction is the failed quantitative transfer of a specified pipeline.
- **How this paper addresses it:** Figures 3-5 and C001, C005, C006 and C009 compare control-selected
  predictions with randomized pulse outcomes; Figure S6 and C007 retain the failed adequacy and
  sensitivity gates.

## Gap 3: Behavioural pulse timing does not localize the failed processing stage

- **Type:** missing measurement.
- **Statement:** A response-associated time course combines sensory encoding, evidence transformation,
  commitment, nondecision processes and response emission. Without physical display measurement or
  neural recordings in these mice, a pulse mismatch cannot be assigned uniquely to sensory,
  decisional or motor dynamics.
- **Evidence:** `yates2017functional` locates early weighting in sensory MT responses;
  `okazawa2018psychophysical` shows that sensory/motor delays and decision bounds distort temporal
  kernels; `kiani2008bounded` shows that prior commitment reduces late evidence efficacy;
  `thura2012urgency` provides a sensory-filter-plus-urgency alternative.
- **Counter-evidence:** `huk2005neural`, `stine2023termination` and `steinemann2024direct` link pulse
  consequences to persistent LIP dynamics in macaques, while `parespujolras2026glimpses` separates
  transient CPP responses from sustained motor-level evidence in human EEG. Those measurements are
  absent here; `kiani2013integration` also tests retention with an independently manipulated gap,
  which this experiment does not.
- **How this paper addresses it:** Figure 2 and C003 expose replay/input assumptions; Figures 4-5 and
  C005-C008 use response-associated and pipeline-level language rather than an integration-time claim.

## Gap 4: Perturbation-based discrimination requires dataset-specific sensitivity

- **Type:** missing causal test / identifiability check.
- **Statement:** A randomized perturbation can establish an effect of assignment, while its ability to
  distinguish mechanisms depends on how separable candidate predictions are under the actual
  schedules, noise, sample sizes and response mapping.
- **Evidence:** `zhou2009time` finds regime-dependent model separability; `hawkins2015discriminating`
  shows that suitable designs can distinguish accumulation and urgency but yield dataset-specific
  preferences; `tsetsos2012timevarying` shows condition- and observer-dependent weights;
  `luken2025parameter` documents parameter trade-offs under low error rates or limited trials.
- **Counter-evidence:** `hyafil2023temporal` demonstrates successful discrimination across several
  discrete-sample datasets, and `brunton2013rats` separates noise sources when pulse events are known
  precisely.
- **How this paper addresses it:** Figure S6 and C007 report failed predictive gates, low strategy
  sensitivity and the withheld confirmatory timing test rather than interpreting failure to
  discriminate as equivalence.

## Gap 5: Established component methods do not validate this specified likelihood and replay

- **Type:** missing measurement / methods precedent.
- **Statement:** Motion-energy computation, reaction-time psychophysics and diffusion fitting each have
  strong precedents, but none of the retained papers validates this specified replay, fixed-window
  no-response likelihood and strong-pulse transfer pipeline as a unit.
- **Evidence:** `adelson1985spatiotemporal` supports the filter computation but not display fidelity;
  `ratcliff2008diffusion` and `palmer2005effect` support joint choice/RT constraints but not this
  censoring implementation; `wiecki2013hddm` and `luken2025parameter` motivate recovery without
  validating the present estimator.
- **Counter-evidence:** `adelson1985spatiotemporal`, `ratcliff2008diffusion`,
  `palmer2005effect` and `huk2005neural` establish the component methods. The gap must therefore not
  be sold as invention of motion energy, DDM fitting or pulse experiments.
- **How this paper addresses it:** Figure 2 documents the reconstructed input and its uncertainty;
  Figure 3 reports recovery/fit limitations with the relative comparison; Methods will bind every
  likelihood and censoring statement to project code rather than to a borrowed precedent.

## Fit condition versus perturbation test in the closest work

| Key | Fit condition | Perturbation | Outcomes predicted or analysed | Perturbation prediction genuinely held out? |
|---|---|---|---|---|
| `stine2020differentiating` | Free-response choice/RT datasets used for integration versus non-integration fits. | No separate motion-pulse transfer test in the retained note. | Choice and RT model comparisons. | Not applicable; establishes identification logic rather than pulse transfer. |
| `huk2005neural` | Reaction-time motion behaviour interpreted with bounded integration; the retained note does not document a no-pulse-only training split. | Brief motion pulses in macaques. | Choice, RT and LIP pulse effects. | No separately held-out control-to-pulse test is documented in the retained note. |
| `stine2023termination` | Bounded accumulator fit to macaque choice and mean RT; no no-pulse-only training split reported. | Randomly signed/timed 100 ms weak pulses (3.2% or 4.0% coherence) on about half of trials. | Choice and mean RT fit; choice, RT, LIP and SC pulse effects analysed. | **No.** Pulses supplied convergent within-task evidence. |
| `steinemann2024direct` | Racing bounded DDM fit per session to macaque choice-RT data. | The same weak 100 ms, random-time macaque pulse manipulation. | Choice and full RT distributions; neural LIP signals and pulse effects. | **No.** Neural decoder cross-validation was not behavioural pulse hold-out. |
| `parespujolras2026glimpses` | Bounded and reweighting models fit to all grand-averaged single- and two-pulse accuracy conditions. | One or two 200 ms motion glimpses separated by variable gaps. | Accuracy; model-derived CPP and motor-beta patterns compared qualitatively with EEG. | **No.** Pulse conditions comprised the fitting data. |

## Mouse-specific precedent boundary

| Established component | Verified mouse precedents | Boundary relative to this paper |
|---|---|---|
| Continuous noisy RDK discrimination | `douglas2006motion`; `stirman2016touchscreen`; `marques2018mousev1`; `samonds2018motion` | No brief randomized signed motion pulse with frozen control-only joint prediction. |
| Dynamic discrete visual evidence accumulation | `pinto2018visualpulses`; `odoemene2018visual`; `koay2020amplitude`; `chakravarty2025cross` | Pulses or flashes are the evidence stream, not a held-out perturbation embedded in continuous RDK. |
| Visual response-time analysis and diffusion modelling | `you2022dynamics`; `caballero2022rt` | Both include DDM fits, but no continuous-RDK signed-pulse transfer test of joint choice, response-probability and RT outcomes. |

These precedents reject broad novelty claims. The negative exact-precedent result is only “not found in
this bounded search,” should be refreshed before submission, and is not a universal historical absence
claim.

## Closest prior work: scoop check

| Key | Overlap with the locked claim | What this paper adds |
|---|---|---|
| `douglas2006motion`; `stirman2016touchscreen`; `marques2018mousev1`; `samonds2018motion` | Establish mouse continuous-RDK psychophysics, decisions and latency effects. | Adds randomized signed pulses and a frozen control-only joint prediction test; it does not claim mouse RDK novelty. |
| `pinto2018visualpulses`; `odoemene2018visual`; `koay2020amplitude`; `you2022dynamics`; `caballero2022rt`; `chakravarty2025cross` | Establish mouse dynamic visual evidence, pulse-based accumulation, response-time analysis and diffusion modelling. | Combines those otherwise separate elements with continuous noisy RDK and an out-of-condition pulse test; it does not claim first mouse visual accumulation or modelling. |
| `stine2023termination` | Bounded choice/RT fits, randomized weak pulses and persistent LIP effects support accumulation in macaques. | Uses a stronger pulse as an out-of-condition test after control-only fitting and reports the failed transfer across joint behavioural outcomes. |
| `steinemann2024direct` | Direct macaque LIP evidence for drift-diffusion-like computation, with weak randomized pulses as convergent support. | Tests a different preparation and prediction pipeline; the result limits that pipeline rather than contradicting the macaque neural mechanism. |
| `parespujolras2026glimpses` | Transient and sustained processing of separated motion evidence, with bounded and reweighting models fit within the pulse task. | Quantitatively tests control-to-strong-pulse transfer in continuous-motion mouse behaviour rather than fitting accuracy across pulse conditions. |

**Scoop verdict:** the 44-source verified synthesis establishes each broad mouse component separately.
The bounded search found no prior mouse study combining continuous noisy RDK, randomized signed motion
pulses, and a frozen control-only model evaluated jointly against choice, response-probability and RT
outcomes. Stine 2023 and Steinemann 2024 materially narrow the claim through strong positive macaque
behavioural and neural evidence with weak randomized pulses; Parés-Pujolràs 2026 v3 adds human EEG and
within-pulse-task modelling. The contribution is a preparation- and pipeline-specific transfer failure,
not priority for any component, and the exact-precedent search requires a pre-submission refresh.

## Discussion comparators

| Key | Agreement or conflict | Proposed reconciliation |
|---|---|---|
| `stine2020differentiating` | Agrees that accuracy/kernels are model-degenerate and joint RT matters. | Present Figure 3 as an implementation-specific extension; emphasize that Figures 4-5 test transfer beyond the fitting condition. |
| `hyafil2023temporal` | Supports integration over tested extrema/snapshot candidates and narrows novelty. | Treat it as convergent support for relative integration preference while retaining its stated non-exhaustiveness and the present replay uncertainty. |
| `huk2005neural` | Pulse persistence and LIP dynamics support bounded integration. | Contrast its macaque neural localization with the present behavioural-only pipeline mismatch; do not import its neural mechanism. |
| `stine2023termination` | Weak randomized pulses had persistent choice/RT and LIP consequences in macaques, supporting bounded accumulation. | Treat this as strong positive evidence in another preparation; contrast within-task convergence with the present strong-pulse transfer failure. |
| `steinemann2024direct` | Single-trial LIP population signals exhibited drift and diffusion linked to choice and RT. | State explicitly that the mouse result tests a specified behavioural pipeline and is not evidence against this macaque neural result. |
| `parespujolras2026glimpses` | Transient CPP pulse processing coexisted with sustained motor-level evidence; bounded and reweighting models remained partly confounded. | Use it to motivate multiple processing stages and explain why the present behavioural mismatch cannot be uniquely localized. |
| `douglas2006motion`; `stirman2016touchscreen`; `marques2018mousev1`; `samonds2018motion` | Continuous noisy RDK discrimination and RDK-linked latency effects were already established in rodents and mice. | Introduce the task as building on mouse RDK psychophysics, not as the first dynamic visual mouse task. |
| `pinto2018visualpulses`; `odoemene2018visual`; `koay2020amplitude`; `chakravarty2025cross` | Mice already accumulate or use discrete visual pulses and flashes, including in neural and cross-species studies. | Distinguish primary pulsatile evidence streams from a signed perturbation of continuous RDK and avoid broad visual-accumulation novelty. |
| `you2022dynamics`; `caballero2022rt` | DDMs have been fit to mouse visual response-time distributions and to visual choices with response latencies. | Frame the present contribution as held-out transfer of a joint model, not first mouse visual RT or diffusion modelling. |
| `carland2016evidence` | Pulse timing changed with policy and was interpreted against perfect integration. | Use it to show context dependence; the present result does not establish the same urgency/leak mechanism. |
| `hawkins2015discriminating`; `evans2017computations` | Matched tests can favour diffusion or urgency depending on dataset, with diffusion favoured in some comparisons. | Argue for task-specific prediction and calibration rather than choosing a universal family. |
| `yates2017functional` | Sensory responses can generate temporal weighting inherited by a downstream integrator. | Keep the failed object as a model-and-input pipeline and identify sensory processing as one unresolved alternative. |
| `okazawa2018psychophysical` | Temporal kernels combine sensory, decision and response processes. | Describe Figure 4 as response-associated timing, not a direct integration kernel or memory constant. |
| `zhou2009time` | Perturbation discrimination depends on prediction separability in the tested regime. | Make the failed gates and low sensitivity a scientific result and the reason the primacy test was withheld. |
| `kiani2013integration` | Demonstrates retention across an explicitly manipulated blank gap. | Separate evidence-retention claims from the present post-onset response time course, which contains no independent gap manipulation. |
| `luken2025parameter` | Parameter trade-offs limit mechanistic interpretation when information is sparse. | Tie parameter claims to recovery and do not interpret bounded or weakly constrained values biologically. |

## Version status

- `parespujolras2026glimpses` is bound to eLife Reviewed Preprint v3 (DOI
  `10.7554/eLife.107980.3`). The obsolete 2025 bioRxiv ledger row is absent, and only the refreshed v3
  note supports the comparisons above.
