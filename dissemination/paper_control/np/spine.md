<!-- np-contract
stage: S1 ; section: spine ; agent: np-architect ; version: v2
thesis: "On held-out control trials, a single bounded accumulator of net motion energy with fast guesses predicts mouse choices and response times better at group level than rapid-forgetting or extrema-detection models, but model recovery shows that control-trial behavior alone cannot tell these strategies apart."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019
numbers: N001, N002, N003, N004, N005, N006, N007, N008, N009, N010, N011, N012, N013, N014, N015, N016, N017, N018, N019, N020, N021, N022, N023, N024, N025, N026, N027, N028, N029, N030, N031, N032, N033
sources: stine2020differentiating, gold2007neural, brunton2013rats, odoemene2018visual, pinto2018visualpulses, douglas2006motion, stirman2016touchscreen, marques2018mousev1, samonds2018motion, okazawa2018psychophysical, adelson1985spatiotemporal, usher2001leaky
-->

## Changes v1 -> v2 (response to np/reviews/spine_challenge.md; point-by-point in np/reviews/spine_v2_changes.md)
1. THESIS and all variants: "a single bounded accumulator of net motion energy" (no architecture implied); "better at group level than ... models" (P1-2, P1-3). Variant A no longer says "behave as bounded accumulators".
2. Selection rule rewritten with two slots that the author fills before any recovery count is read: X_ext (which extrema model the rule uses; NEEDS HUMAN 1) and the separation criterion (per-dataset vs cohort-level; NEEDS HUMAN 2). Each option has a mechanical rule. Clopper-Pearson CIs always reported. Partial runs never counted (P2-4). DDMx exclusion justified (P2-5).
3. Key control: no longer calls FP_X "the false-positive rate of the Fig 3 conclusion" (P0-1).
4. New hypothesis rows: H0b (RT shape / fast-guess allocation / robust front end, P0-3) and H4 (architecture, not tested).
5. Scope: architecture line (Kirkpatrick et al. 2021, unverified until S2), net motion energy as model input only, leak range not tested (D009 kept), recovery at fitted parameters only, unpaired preview disclosed as superseded and invalid without numbers, no "mechanism"/"strategy used by mice" outside A.
6. Figure plan: Fig 3 splits matched-component (E, ES) from paper-exact (DDMx, ESx) panels and shows per-mouse counts (N030–N033); Fig 2 shows the model-kernel misfit (N029); Fig 4 adds CIs and an optional cohort panel.
7. Claims: C002 now N028; C006 "comparable"; C008/C009 per-mouse counts added; C010–C012 rewritten for the slots; new C017 (kernel misfit), C018 (architecture limitation tied to N026), C019 (Methods disclosure of the rule's history).
8. Open items blocked on the author: NEEDS HUMAN 1–7 in np/reviews/spine_v2_changes.md. Markers [NH#] below show where each lands.

# Paper spine

The spine anchors the whole paper against drift. Every agent reads it first, and every agent output
copies the THESIS line verbatim into its np-contract header. Everything between LOCK-START and
LOCK-END is frozen at gate G1. Changing it needs an entry in decisions.md, human approval, and
`np.py lock-spine` again. G1 cannot pass while NH1, NH2, NH3 and NH4 are open.

<!-- LOCK-START -->
THESIS: On held-out control trials, a single bounded accumulator of net motion energy with fast guesses predicts mouse choices and response times better at group level than rapid-forgetting or extrema-detection models, but model recovery shows that control-trial behavior alone cannot tell these strategies apart.

## THESIS selection rule (v1 fixed 2026-10-29; v2 slots must be filled and logged in decisions.md before any paired-recovery count is read)
The THESIS line above is variant B, the conservative default. It is replaced by variant A, I or B0 only by
applying this rule to the paired recovery result [PENDING: paired recovery]. The swap is logged in
decisions.md with the counts; no other wording change is allowed without a new decision.

### Slots (filled by the author; see spine_v2_changes.md)
- **INPUT** [NH3]: default "a single bounded accumulator of net motion energy". If the author chooses to
  drop the input from the THESIS, or the pre-specified ablation criterion fails, INPUT = "a single
  bounded accumulator" in every variant.
- **X_ext** [NH1]: the extrema model used by the rule.
  - NH1-a: X_ext = ES (ES added as 5th generator and candidate). EXT_LABEL = "extrema detection".
  - NH1-b: X_ext = ESx. EXT_LABEL = "paper-exact extrema detection (nominal-coherence input, no drift variability or fast guesses)".
  - NH1-c: no extrema model in the rule (X set = {E}); ESx rows reported descriptively. Variant I cannot occur; variant A uses the A_E wording below.
- **CRITERION** [NH2]: per-dataset (P), cohort-level (G) or both (P+G); defined below.

### Pre-written variants (exact wording; fill INPUT and EXT_LABEL, nothing else)
- **Variant A (separated):** "On held-out control trials, <INPUT> with fast guesses predicts mouse choices and response times better at group level than rapid-forgetting or extrema-detection models, and model recovery shows that this comparison distinguishes integration from rapid forgetting and from <EXT_LABEL>, so control-trial behavior favors integration over both."
- **Variant A_E (only under NH1-c, E separated):** "On held-out control trials, <INPUT> with fast guesses predicts mouse choices and response times better at group level than rapid-forgetting or extrema-detection models, and model recovery shows that this comparison distinguishes integration from rapid forgetting; recovery did not test extrema detection."
- **Variant I (one separated):** "On held-out control trials, <INPUT> with fast guesses predicts mouse choices and response times better at group level than rapid-forgetting or extrema-detection models; model recovery shows that this comparison distinguishes integration from <SEPARATED> but not from <NOT SEPARATED>." (Fill from {"rapid forgetting", EXT_LABEL}.)
- **Variant B (default; none separated):** the THESIS line above, with INPUT filled.
- **Variant B0 (recovery invalid or incomplete):** "On held-out control trials, <INPUT> with fast guesses predicts mouse choices and response times better at group level than rapid-forgetting or extrema-detection models; whether control-trial behavior alone can tell these strategies apart was not established."

### Definitions
Recovery = generators x candidates over {C, E, DDMx, ESx} (4 x 4), plus ES as generator and candidate
under NH1-a (5 x 5). 20 synthetic datasets per generator (fitted control-split parameters of the 10
mice, 2 replicates each, the mice's trial counts), CPU pre-generated, sha256 manifest. For dataset d,
NLL_c(d) = candidate c's summed held-out NLL on the synthetic test trials; Δ_X(d) = NLL_X(d) − NLL_C(d)
(positive = C better); δ_X(d) = 1,000 · Δ_X(d) / n_test(d) (per 1,000 trials, the real-data scale).
X set = {E, X_ext}.

**Criterion P (per dataset; the >10 rule of paper_accumulation D006):**
- FP_X = number of the 20 X-generated datasets with Δ_X(d) > 10.
- SENS_X = number of the 20 C-generated datasets with Δ_X(d) > 10.
- P-separated iff FP_X ≤ 2/20 AND SENS_X ≥ 10/20 (the SENS threshold is the v1 value unless the author
  changes it under NH2 before counts are read).

**Criterion G (cohort level; mirrors the Fig 3 group test):**
- A cohort = one replicate per mouse for all 10 mice; all 2^10 = 1,024 cohorts per generator.
- A cohort "reproduces the real-data result for X" iff mean δ_X > 0 and the one-sample t-test on the
  10 δ_X values has Holm-adjusted p < 0.05, Holm over all non-C candidates in the recovery.
- FPg_X = fraction of X-generated cohorts that reproduce; SENSg_X = fraction of C-generated cohorts
  that reproduce.
- G-separated iff FPg_X ≤ 0.10 AND SENSg_X ≥ 0.50.
- Cohorts share replicates, so FPg/SENSg are resampling summaries, not rates from independent draws;
  this is stated in Methods.

**Separated:** under P, P-separated; under G, G-separated; under P+G, both. Always reported
whichever is chosen: FP_X and SENS_X with Clopper-Pearson 95% CIs, and the full matrix including
DDMx-generated rows and all off-diagonal cells.

**Selection:** every X in the X set separated → A (A_E under NH1-c). Exactly one of two separated → I.
None separated → B.

**Validity precondition (checked before anything is counted):** every planned fit finished (320 for
4 x 4; 500 for 5 x 5); within every dataset all candidates were scored on identical train and test
trials (same manifest sha256, equal n_train and n_test). The completion check reads fit counts and
manifests only, never NLL values. If any fit is missing or mismatched, no partial counts are used and
the THESIS becomes **B0**; the failure is reported. B0 also applies if the recovery is not complete by G3.

**Why DDMx rows do not enter the rule:** DDMx is an integration model, so whether it separates from C
is a question about components and input, not about integration versus non-integration.

**Ordering:** NH1 and NH2 are decided and logged in decisions.md before any output of the running
recovery job is opened. The threshold 10 and the 0.05/Holm test are the rules already used on real
data (paper_accumulation D006, D008).

## Story (OCAR)
- Opening (problem space, audience): Bounded accumulation of evidence is the standard account of perceptual decisions in primates and rats [@gold2007neural; @brunton2013rats]. Mice are now widely used for visual decision tasks, including random-dot motion [@douglas2006motion; @stirman2016touchscreen; @marques2018mousev1; @samonds2018motion], but the case that mice accumulate evidence rests mostly on tasks with discrete pulses of evidence [@odoemene2018visual; @pinto2018visualpulses]. Rodent random-dot reaction-time work reports flat chronometric functions and fast errors [for S2: Reinagel 2013; Shevinsky & Reinagel 2019; caballero2022rt]; our descriptives are framed as consistent with that pattern, not as new. Audience: systems and computational neuroscientists who use mice to study decisions.
- Challenge (the hinge): Stine et al. showed that non-integration strategies (rapid forgetting, extrema detection) can mimic the accuracy, chronometric and kernel signatures of integration, and that only joint choice and response-time constraints, checked by model recovery, can separate them [@stine2020differentiating]. Can ordinary (control) trials of a reaction-time random-dot motion task show whether mice integrate motion evidence over time?
- Action:
  1. 10 mice, reaction-time RDK direction discrimination; 14,014 responded control trials {{N001}} {{N002}}; choice, chronometric function and RT by outcome (Fig 1).
  2. Replayed every stimulus and filtered it for motion energy [@adelson1985spatiotemporal]; psychophysical kernels with model overlays (Fig 2).
  3. Fitted the common model (single bounded accumulator of net motion energy with drift variability and fast guesses) and four alternatives (E, ES with matched components; DDMx, ESx paper-exact); compared them on held-out control trials, mice as the unit (Fig 3). [NH3: input ablation and choice/RT split, if chosen.]
  4. Paired model recovery over C, E, DDMx, ESx [NH1-a: + ES], scored with the same held-out rule (Fig 4) [PENDING: paired recovery].
  5. Component tests: which ingredients of the common model matter for held-out prediction (Fig 5).
- Resolution: At group level, held-out prediction favors the accumulator over every tested alternative by t-test (Holm) {{N005}}–{{N012}}, although the Wilcoxon tests do not reach 0.05 and only 5–6 of 10 mice favor it individually by > 10 {{N030}}–{{N033}}; fast guesses are needed {{N014}}. Whether control trials can therefore show integration depends on recovery: A → yes against both non-integration alternatives tested; I → only against the separated one; B → no: control-trial behavior favors the accumulator but cannot tell the strategies apart, so deciding requires designed perturbations of evidence; B0 → not established. Kernels and chronometry do not decide it: they are small or not significant after Holm {{N019}}–{{N024}}, underpowered {{N027}}, and the models over-predict the kernel {{N029}}, consistent with Stine et al.'s point that these signatures are not diagnostic. Architecture (single opponent accumulator vs race or competing accumulators) is outside what this design can constrain.

## Competing hypotheses and what each predicts
| Hypothesis | Prediction | Which figure decides it |
|---|---|---|
| H1: Integration over time by a single bounded accumulator of net motion energy (C; DDMx as the paper-exact form) | C has lower held-out choice+RT NLL than E, ES, ESx at group level; in recovery, C-generated data are scored as C (SENS high) | Fig 3 (real data), Fig 4 (whether the Fig 3 win is diagnostic) |
| H2: Rapid forgetting (E: leak 20–200/s, time constant 5–50 ms, same sv and fast guesses as C) | E predicts held-out trials as well as C; in recovery, E-generated data are often scored as C (FP_E high), so a C win is not evidence against H2 | Fig 3, Fig 4 |
| H3: Extrema detection (ES matched components; ESx paper-exact) | ES/ESx predict held-out trials as well as C; X_ext-generated data scored as C (FP high). Under NH1-b, separation of ESx can follow from its missing sv and fast guesses rather than from the sampling rule | Fig 3, Fig 4 (extrema side as set by NH1) |
| H0a (flexibility): C wins only through sv and fast guesses | C's advantage vanishes against an alternative with the same components (E, ES) | Fig 3 panel A (matched components), Fig 5 |
| H0b (RT shape / input robustness): C wins through RT-distribution shape, fast-guess allocation, or robustness to input noise the mouse does not see, not through use of within-trial motion | C with nominal-coherence or time-shuffled input predicts as well as C with motion energy; advantage concentrated in the fastest RT quantile or in the choice-vs-RT split | [NH3] ablation and NLL split (Fig 3 supplement) if chosen; otherwise undecided and stated as a limitation |
| H4 (architecture): race, LCA or other partially dependent accumulators | Not tested: all models are single opponent accumulators and the task has no equal-evidence condition | None; scope and Discussion limitation (C018) |

## Key control (rules out the boring explanation)
1. Flexibility control (real data): E and ES carry the same drift variability and fast guesses as C and differ only in leak or in the sampling rule, so C vs E {{N005}} {{N006}} and C vs ES {{N007}} {{N008}} are not explained by C's extra components. DDMx/ESx comparisons are confounded by components and input and are shown separately.
2. Paired model recovery (Fig 4): each candidate is scored on the same synthetic held-out trials, generated at the mice's fitted parameters and trial counts. Under criterion P it gives the per-dataset false-positive rate of the > 10 rule (FP_X), which is not the error rate of the Fig 3 group test; under criterion G [NH2] it gives the rate at which synthetic 10-mouse cohorts reproduce the Fig 3 group result when X generated the data. The text names which one sets the wording.
3. [NH3] Input control: nominal-coherence and time-shuffled motion-energy refits, if chosen.

## Figure plan (one claim per figure)
| Fig | Claim it supports (claim IDs) | Data source (path) | Status |
|---|---|---|---|
| 1 | Task and behavior: on responded control trials accuracy rises with coherence {{N028}}; correct RT trends downward with coherence and errors tend to be faster than correct responses, neither surviving Holm (C001–C004). Panels: task schematic, psychometric, chronometric, RT distributions by outcome, error minus correct RT per mouse. Legend defines fast guesses vs decision errors (errors at 100% coherence). | /src/dissemination/paper/figures/fig1_task_behaviour_2026-10-26_v2.*; /src/dissemination/paper_control/tables/control_chronometry_2026-10-29.csv, control_per_mouse_2026-10-29.csv | Partial: rebuild on responded control trials only, no-response panels removed or moved to Methods; RT-by-outcome and error-minus-correct panels [MISSING: panel script] |
| 2 | Motion energy and kernels: reconstructed motion energy tracks the stimulus, but control-trial kernels are too small and noisy to tell strategies apart, and both models predict a larger kernel than observed (C005–C007, C016, C017). Panels A–C stimulus reconstruction; D stimulus-aligned and E response-aligned kernels with C and E overlays. | /src/dissemination/paper/figures/fig2_stimulus_reconstruction_2026-10-26_v6.* A–C; /src/dissemination/paper_control/tables/control_kernels_2026-10-29.csv, control_tests_2026-10-29.csv | A–C exist; D–E [MISSING: panel script]; C016 calibration number [MISSING] |
| 3 | Model comparison: at group level the common model predicts held-out control choices and RTs better than E, ES, DDMx and ESx (t-test Holm; Wilcoxon not significant; 5–6/10 mice individually) (C008, C009). Panel A: matched components (E, ES), per-mouse per-1,000 ΔNLL, group test. Panel B: "different components and input" (DDMx, ESx). Panel C: model overlays on psychometric/chronometric. Supplement: [NH3] input ablation and choice/RT NLL split; [NH6] leave-one-mouse-out; [NH4] no-sv sensitivity table; [NH5] free-leak table. | /src/dissemination/paper_accumulation/tables/heldout_group_2026-10-28.csv, heldout_per_trial_2026-10-28.csv | Numbers exist; panels [MISSING: panel script]; supplements depend on NH3–NH6 |
| 4 | Recovery: how often the held-out rule identifies the generating model; this sets the THESIS variant (C010–C012). Panel A: confusion matrix (counts of Δ > 10, with Clopper-Pearson CIs), 4 x 4 or 5 x 5 [NH1]. Panel B: Δ (and δ) distributions for X-generated and C-generated datasets with the real-data values marked. Panel C [NH2-G or P+G]: cohort-level reproduction rates. | /mnt/data/processed/ddm/recovery_full_cpu_resp/ (expected out_dir); datasets /mnt/data/processed/ddm/recovery_datasets_cpu_2026-10-29/; [NH1-a: ES datasets and fits, path MISSING] | [PENDING: paired recovery]; [MISSING: panel script] |
| 5 | Components: fast guesses are needed for held-out prediction; removing drift variability, adding leak or urgency, or fixing the guess bias do not change prediction at group level (C013–C015). Supplement panel: data minus model fast-error RT (exploratory, C015), linked to the architecture limitation (C018). | /src/dissemination/paper_accumulation/tables/components_group_2026-10-28.csv, components_per_trial_2026-10-28.csv; control_per_mouse_2026-10-29.csv | Numbers exist; panels [MISSING: panel script] |

## Scope: what this paper will NOT claim
- No pulse-trial results, primacy, pulse gain or temporal-weighting claims; pulse trials appear in Methods only as excluded trials.
- No comparison or interpretation by site (UCLA vs UW); rig is a covariate only.
- No analysis of trials without a response by 5 s {{N004}}; all likelihoods are conditional on a response by 5 s.
- No claim that mice integrate rather than forget rapidly or detect extrema unless variant A is selected (variant I: only against the separated alternative; A_E: only against rapid forgetting).
- No architecture claim: all models are a single bounded accumulator of net (opponent) motion energy; race and LCA models were not fitted, and the control task has no equal-evidence condition that could constrain architecture (Kirkpatrick et al. 2021, doi 10.1037/rev0000284, unverified until S2). The fast-error misfit {{N026}} is discussed as consistent with architecture or starting-point-variability alternatives, not as evidence for any of them.
- Net motion energy is the model input; no claim that within-trial motion fluctuations drive the model advantage unless the [NH3] ablation shows it.
- No claim that a flat or null kernel means mice ignore motion fluctuations: the kernel test is underpowered {{N027}} and the models over-predict the kernel {{N029}}.
- No claim that drift variability is needed at group level {{N013}}; only fast guesses are {{N014}}.
- Rapid forgetting means leak 20–200/s (time constant 5–50 ms); slower leak is not tested and no integration time constant is claimed. No free-leak fits (D009) [NH5].
- No discussion of the model without drift variability [NH4: pending author decision; D005 note conflicts].
- No claim that the chronometric trend or fast errors are significant: both fail Holm {{N022}} {{N024}}; the fast-error misfit of the common model is exploratory {{N026}}.
- Recovery is at each mouse's fitted parameters only; no claim about recovery elsewhere in parameter space (e.g., E at slower leak).
- Under NH1-b: no recovery-based claim about ES (matched-component extrema model); "extrema detection" in Fig 4 means paper-exact ESx, and its separation does not rule out extrema detection with matched components.
- The earlier recovery run with unpaired synthetic data is reported in Methods only as superseded and invalid; its counts are not reported [not in ledger].
- No neural mechanism, no optimality claim; no "mechanism" or "strategy used by mice" wording outside variant A.
<!-- LOCK-END -->

## Glossary (one term per concept; never use synonyms)
| Term | Definition | Do not use |
|---|---|---|
| control trial | A trial with no added motion pulse (sched_pulse_type 0) | no-pulse trial, baseline trial |
| responded trial | A trial with a choice and RT ≤ 5 s; the only trials analyzed | valid trial, completed trial |
| coherence | Nominal signed fraction of coherently moving dots | motion strength (except in Methods definition) |
| motion energy | Output of the spatiotemporal energy filter applied to the replayed stimulus, in % coherence units | ME (in text), motion signal |
| net motion energy | Rightward minus leftward motion energy; the single input to every model except DDMx/ESx | opponent signal (except once, in Methods) |
| psychophysical kernel | Mean motion-energy fluctuation, choice-conditioned, as a function of time (stimulus- or response-aligned) | reverse-correlation kernel, temporal weighting function |
| chronometric function | Median correct RT as a function of absolute coherence | RT curve |
| common model (C) | Single bounded accumulator of net motion energy with drift variability, fast guesses and free guess bias (L0U0V1Z0G1), responded-only | full model, DDM (alone), winning model |
| rapid-forgetting model (E) | Common model plus leak (20–200/s, time constant 5–50 ms) | leaky model, forgetting model |
| extrema-sampling model (ES) | Non-integration model that commits when a single sample exceeds a threshold, with the common model's components (sv, fast guesses) | extrema model |
| paper-exact models (DDMx, ESx) | Integration and extrema-detection models as specified by Stine et al. 2020 (nominal coherence input; without sv, fast guesses, leak or urgency) | Stine models |
| non-integration strategy | Rapid forgetting or extrema detection | non-accumulation, snapshot |
| fast guess | Response drawn from the model's stimulus-independent fast RT component; errors at 100% coherence can arise from fast guesses or from decision errors, and the paper does not split them except through the fitted model | lapse, guess (alone), contaminant |
| drift variability (sv) | Across-trial SD of the drift rate | noise, trial-to-trial variability |
| held-out NLL | Negative log likelihood of choice and RT quantiles on cross-validation test trials; group statistics per 1,000 trials | test loss, cross-validated likelihood |
| model recovery | Fitting all candidates to synthetic datasets generated by each model and scoring with the held-out rule | parameter recovery (different concept) |
| separated | Recovery criterion for alternative X as fixed in the selection rule (criterion P, G or P+G) | identifiable, distinguishable (in technical statements) |
| architecture | How evidence for the two directions is combined (single opponent accumulator, race, competing accumulators) | mechanism |

## For S2 (unverified; do not cite until verified)
- Kirkpatrick, Turner & Sederberg 2021, Psychol Rev 128(6):1051–1087, doi 10.1037/rev0000284 (architecture; author-supplied).
- Reinagel 2013 (rats, RDK speed and accuracy; PMC3695925).
- Shevinsky & Reinagel 2019 (rats, errors vs RT; bioRxiv 726703).
- Frontiers in Neuroscience 2019, rat vs human RDK (fnins.2019.01211).
- Treviño et al. 2022 (mouse RT distributions); check whether this is the existing key caballero2022rt.

## Promises ledger
What earlier sections set up that later sections must deliver. The editor checks every row.
| Promised in | Promise | Delivered in | Status |
|---|---|---|---|
| Introduction | Non-integration strategies can mimic integration; we test whether control trials can tell them apart | Results Fig 4; Discussion D1 | open |
| Introduction | Kernels and chronometry are reported but not used as strategy evidence | Results Fig 1–2; Discussion limitations | open |
| Introduction | Flat chronometry and fast errors framed as a known rodent pattern | Discussion (after S2 verification of Reinagel papers) | open |
| Results Fig 3 | The held-out win is checked for false positives by recovery, at the level (P/G) the selection rule names | Results Fig 4 | open [PENDING: paired recovery] |
| Results Fig 3 | Wilcoxon result and per-mouse counts stated beside the t-test | Results Fig 3 text {{N006}} {{N008}} {{N010}} {{N012}} {{N030}}–{{N033}} | open |
| Methods | Recovery selection rule, slot choices and threshold fixed before results; unpaired preview disclosed as superseded and invalid (C019) | Methods recovery subsection; decisions.md entry | open |
| Results Fig 2 | Kernel power caveat and model over-prediction quantified | Results Fig 2 text {{N027}} {{N029}} | open |
| Results Fig 5 | Fast-error misfit flagged as exploratory, revisited as an architecture limitation | Discussion limitations (C018) | open |
| Scope | Architecture not constrained; net motion energy is the input only | Discussion limitations | open |
| Scope | Leak range tested (20–200/s) and untested slower leak stated | Methods models; Discussion limitations | open |
| Discussion | What would decide integration if B/I: designed evidence perturbations | Discussion D4/D5 | open |
