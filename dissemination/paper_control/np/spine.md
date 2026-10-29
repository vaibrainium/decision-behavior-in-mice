<!-- np-contract
stage: S1 ; section: spine ; agent: np-architect ; version: v3
thesis: "On held-out control trials, a single bounded accumulator of net motion energy with fast guesses predicts the per-coherence distributions of mouse choices and response times better at group level than rapid-forgetting or extrema-detection models, mostly through response times, but model recovery shows that control-trial behavior alone cannot tell these strategies apart."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021, C022, C023, C024, C025, C026
numbers: N001, N002, N003, N004, N005, N006, N007, N008, N009, N010, N011, N012, N013, N014, N015, N016, N017, N018, N019, N020, N021, N022, N023, N024, N025, N026, N027, N028, N029, N030, N031, N032, N033, N034, N035, N036, N037, N038, N039, N040, N041, N042
sources: stine2020differentiating, gold2007neural, brunton2013rats, odoemene2018visual, pinto2018visualpulses, douglas2006motion, stirman2016touchscreen, marques2018mousev1, samonds2018motion, okazawa2018psychophysical, adelson1985spatiotemporal, usher2001leaky
-->

## Changes v2 -> v3 (applies D002 and D003; details in np/reviews/spine_v3_changes.md)
1. THESIS and all variants: "predicts the per-coherence distributions of mouse choices and response times ... mostly through response times". The likelihood pools trials per signed coherence (C024). The advantage is mostly in the RT terms against every alternative ({{N035}}, {{N037}}, {{N039}}, {{N041}}). Against ES the choice part is about 0 ({{N036}}). The THESIS line is still variant B, the conservative default, with INPUT unchanged pending the nominal refits.
2. NH1 resolved (D002-1, D003): ES is the 5th generator and candidate (5 x 5 grid: C, E, ES, DDMx, ESx). The X set is {E, ES}. Variant A_E and the NH1-b and NH1-c options are removed.
3. NH2 resolved (D002-2, D003): criterion G (cohort level, the same group test as Fig 3) sets the wording. Per-dataset counts with Clopper-Pearson CIs are reported as secondary results and are not decisive. Thresholds are fixed now. A section explains why DDMx and ESx do not enter the rule.
4. NH3 resolved (D003): the shuffled-motion-energy refits are dropped as a no-op by construction. The choice/RT split is done (N034–N041). The nominal-coherence refits of C, E and ES are pending and get a figure panel (Fig 3—figure supplement 1) and claim slots C025 and C026 with the rule "(NLL_nominal − NLL_ME) per 1,000 trials > 0, Holm over 3". The INPUT slot is now tied mechanically to C's row of that rule. H0b is rewritten, and H0c is new.
5. NH4 resolved (D003): one Methods sentence, without numbers, says that the sv model set was chosen after the no-sv comparison had been seen and that the ranking depends on sv (C020). The scope line is changed to match.
6. NH5: D009 is kept. NH6: leave-one-mouse-out is reported as robustness (N042, C023). NH7: there is no design guide, and the Discussion stays qualitative.
7. New claims C020–C026. C008–C012 and C019 are rewritten. The figure plan, glossary and promises are updated.

# Paper spine

The spine anchors the whole paper against drift. Every agent reads it first, and every agent output
copies the THESIS line verbatim into its np-contract header. Everything between LOCK-START and
LOCK-END is frozen at gate G1. Changing it needs an entry in decisions.md, human approval, and
`np.py lock-spine` again. The selection rule below must be logged in decisions.md before any output of
recovery job 42579825 or of the 180-fit ES job is opened.

<!-- LOCK-START -->
THESIS: On held-out control trials, a single bounded accumulator of net motion energy with fast guesses predicts the per-coherence distributions of mouse choices and response times better at group level than rapid-forgetting or extrema-detection models, mostly through response times, but model recovery shows that control-trial behavior alone cannot tell these strategies apart.

## THESIS selection rule (v3, fixed 2026-10-29 under D002/D003, before any paired-recovery count is read)
The THESIS line above is variant B, the conservative default. Only two things can change it. Applying the
recovery rule to the paired 5 x 5 recovery [PENDING: paired recovery] selects variant A, I_E, I_ES, B or B0.
Applying the INPUT rule to the nominal-coherence refits [PENDING: nominal refits] fills INPUT. Each swap is
logged in decisions.md together with the numbers that triggered it. Any other change to the wording needs
a new decision.

### Slots
- **INPUT**: "a single bounded accumulator of net motion energy" (current) or "a single bounded
  accumulator". This is set by the INPUT rule below.
- **EXT_LABEL** = "extrema detection" (ES, the matched-component extrema-sampling model, enters the rule).

### Pre-written variants (exact wording; only INPUT is filled)
Shared prefix P = "On held-out control trials, <INPUT> with fast guesses predicts the per-coherence
distributions of mouse choices and response times better at group level than rapid-forgetting or
extrema-detection models, mostly through response times"
- **Variant A (both separated):** P + ", and model recovery at the level of the group test shows that this comparison distinguishes integration from rapid forgetting and from extrema detection, so control-trial behavior favors integration over both."
- **Variant I_E (only E separated):** P + "; model recovery shows that this comparison distinguishes integration from rapid forgetting but not from extrema detection."
- **Variant I_ES (only ES separated):** P + "; model recovery shows that this comparison distinguishes integration from extrema detection but not from rapid forgetting."
- **Variant B (default; neither separated):** P + ", but model recovery shows that control-trial behavior alone cannot tell these strategies apart."
- **Variant B0 (recovery invalid or incomplete):** P + "; whether control-trial behavior alone can tell these strategies apart was not established."

The clause "mostly through response times" is fixed from existing numbers: for every alternative, the RT part is
most of the total held-out advantage (C021, C022). It does not depend on recovery.

### Recovery design
Generators x candidates over {C, E, ES, DDMx, ESx} (5 x 5). There are 20 synthetic datasets per generator
(the fitted control-split parameters of the 10 mice, 2 replicates each, at the mice's trial counts). All
datasets are CPU pre-generated in /mnt/data/processed/ddm/recovery_datasets_cpu_2026-10-29/ and listed in a
sha256 manifest of 100 datasets. For dataset d:
- NLL_c(d) = candidate c's summed held-out NLL on the synthetic test trials.
- Δ_X(d) = NLL_X(d) − NLL_C(d) (positive = C better).
- δ_X(d) = 1,000 · Δ_X(d) / n_test(d) (per 1,000 trials, the real-data scale).

**Criterion G (primary; sets the wording):** this is the Fig 3 group test applied to synthetic cohorts.
- A cohort is one replicate per mouse for all 10 mice. There are 2^10 = 1,024 cohorts per generator.
- A cohort *reproduces the real-data result for X* iff the mean of its 10 δ_X values is > 0 and the
  one-sample t-test on those 10 values has a Holm-adjusted p < 0.05. Holm runs over the 4 non-C candidates
  (E, ES, DDMx, ESx), the same family as Fig 3 (paper_accumulation D006, D008).
- FPg_X = fraction of X-generated cohorts that reproduce for X.
- SENSg_X = fraction of C-generated cohorts that reproduce for X.
- X is **separated** iff FPg_X ≤ 0.10 AND SENSg_X ≥ 0.50.
- Cohorts share replicates (2 per mouse), so FPg and SENSg are resampling summaries, not rates from
  independent draws. No binomial CI is attached to them, and Methods says so.

**Per-dataset counts (secondary; reported, not decisive):**
- FP_X = number of the 20 X-generated datasets with Δ_X(d) > 10.
- SENS_X = number of the 20 C-generated datasets with Δ_X(d) > 10.
- Both are reported with Clopper-Pearson 95% CIs for every cell of the 5 x 5 matrix. These counts calibrate
  the per-mouse > 10 rule (N030–N033), not the group test. If they point the other way from criterion G, the
  text reports both and the wording follows G.

**Selection:** E and ES both separated → A. Only E → I_E. Only ES → I_ES. Neither → B.

**Why only E and ES decide.** E and ES share the common model's input (net motion energy), drift
variability and fast guesses. E differs from C only in leak, and ES only in the sampling rule. A
separation from E or ES is therefore a separation of integration from a non-integration strategy, with the
components held fixed. DDMx and ESx differ from C in three ways at once: nominal-coherence input, no drift
variability and no fast guesses. Whether recovery separates them from C measures how detectable those
components and that input are, not whether integration can be told from non-integration. DDMx is itself an
integration model. ESx separating from C could follow from its missing components alone (the same
confound as Fig 3B). DDMx and ESx stay in the Holm family so that the cohort test is the Fig 3 test
exactly. Their rows and columns are reported in full.

**Validity precondition (checked before anything is counted):**
- All 500 planned fits finished: 320 from job 42579825, plus 180 ES-cell fits (the ES candidate on the 80
  existing datasets, and all 5 candidates on the 20 ES datasets).
- Within every dataset, all 5 candidates were scored on identical train and test trials: same manifest
  sha256 and equal n_train and n_test.
- The check reads fit counts and manifests only, never NLL values.
- If any fit is missing or mismatched, no partial counts are used and the THESIS becomes **B0**. The failure
  is reported. B0 also applies if the recovery is not complete by G3.

**Ordering:** this rule, including the G thresholds (0.10, 0.50), is logged in decisions.md before any
recovery output is opened. The 0.05/Holm test and the > 10 threshold are the rules already used on real
data.

### INPUT rule (nominal-coherence refits, D003) [PENDING: nominal refits]
- Refits: C, E and ES on the control split with nominal-coherence input and otherwise identical
  components (sv, fast guesses, guess bias; leak 20–200/s for E). Cross-validated on the same folds and
  scored with the same held-out rule.
- Per model m: Δnom_m = (NLL_nominal − NLL_ME) per 1,000 control trials, with mice as the unit.
  The t-test is decisive and the Wilcoxon is reported. Holm runs over the 3 models. A result > 0 means the
  motion-energy input predicts better.
- INPUT keeps "of net motion energy" iff Δnom_C has mean > 0 and t Holm p < 0.05. Otherwise
  INPUT = "a single bounded accumulator", and Methods states that the model input is net motion energy.
- If the refits are not complete and valid (all 150 fits, same folds) by G3, INPUT = "a single bounded
  accumulator".
- Rows E and ES, and the ranking of C_nom against E_nom and ES_nom, are reported as sensitivity results
  (C025, C026). They do not change the wording.
- Interpretation is fixed in advance. The likelihood pools trials per signed coherence (C024), so this
  comparison tests whether the measured within-coherence distribution of motion energy predicts better
  than nominal coherence plus drift variability. It does not test whether the mouse uses each trial's own
  motion.

## Story (OCAR)
- Opening (problem space, audience): Bounded accumulation of evidence is the standard account of perceptual decisions in primates and rats [@gold2007neural; @brunton2013rats]. Mice are now widely used for visual decision tasks, including random-dot motion [@douglas2006motion; @stirman2016touchscreen; @marques2018mousev1; @samonds2018motion], but the case that mice accumulate evidence rests mostly on tasks with discrete pulses of evidence [@odoemene2018visual; @pinto2018visualpulses]. Rodent random-dot reaction-time work reports flat chronometric functions and fast errors [for S2: Reinagel 2013; Shevinsky & Reinagel 2019; caballero2022rt]; our descriptives are framed as consistent with that pattern, not as new. Audience: systems and computational neuroscientists who use mice to study decisions.
- Challenge (the hinge): Stine et al. showed that non-integration strategies (rapid forgetting, extrema detection) can mimic the accuracy, chronometric and kernel signatures of integration, and that only joint choice and response-time constraints, checked by model recovery, can separate them [@stine2020differentiating]. Can ordinary (control) trials of a reaction-time random-dot motion task show whether mice integrate motion evidence over time?
- Action:
  1. 10 mice, reaction-time RDK direction discrimination; 14,014 responded control trials {{N001}} {{N002}}; choice, chronometric function and RT by outcome (Fig 1).
  2. Every stimulus was replayed and filtered for motion energy [@adelson1985spatiotemporal]; psychophysical kernels with model overlays (Fig 2).
  3. Fitted the common model (a single bounded accumulator of net motion energy with drift variability and fast guesses) and four alternatives: E and ES with matched components, and the paper-exact DDMx and ESx. Compared them on held-out control trials with mice as the unit, split the advantage into choice and RT parts, and checked leave-one-mouse-out robustness. Refit C, E and ES on nominal coherence [PENDING: nominal refits] (Fig 3).
  4. Paired 5 x 5 model recovery over C, E, ES, DDMx and ESx, scored with the same held-out rule and calibrated at the level of the group test with synthetic 10-mouse cohorts (Fig 4) [PENDING: paired recovery].
  5. Component tests: which ingredients of the common model matter for held-out prediction (Fig 5).
- Resolution: At group level, held-out prediction favors the accumulator over every tested alternative by t-test (Holm) {{N005}}–{{N012}}, and this survives dropping any one mouse {{N042}}. The Wilcoxon tests do not reach 0.05, and only 5–6 of 10 mice favor it individually by > 10 {{N030}}–{{N033}}. The advantage lies mostly in response-time distributions. Against the matched extrema model, choice proportions are predicted equally well {{N036}} and the whole advantage is in RT {{N037}}. Against rapid forgetting there is also a small, consistent choice advantage {{N034}}. Fast guesses are needed {{N014}}. Because the likelihood pools trials per coherence, none of this shows that mice use each trial's motion. Whether control trials can show integration depends on recovery at the group-test level:
  - A: yes, against both matched non-integration alternatives.
  - I_E or I_ES: only against the separated one.
  - B: no. Control-trial behavior favors the accumulator but cannot tell the strategies apart, so a decision needs designed perturbations of evidence (stated qualitatively; no design guide).
  - B0: not established.

  Kernels and chronometry do not decide the question. They are small or not significant after Holm {{N019}}–{{N024}}, the kernel test is underpowered {{N027}}, and the models over-predict the kernel {{N029}}, consistent with Stine et al.'s point that these signatures are not diagnostic. Architecture (single opponent accumulator vs race or competing accumulators) is outside what this design can constrain.

## Competing hypotheses and what each predicts
| Hypothesis | Prediction | Which figure decides it |
|---|---|---|
| H1: Integration over time by a single bounded accumulator (C; input net motion energy; DDMx as the paper-exact form) | C has lower held-out NLL than E and ES at group level. In recovery, C-generated cohorts reproduce the Fig 3 result (SENSg ≥ 0.50) and E- and ES-generated cohorts rarely do (FPg ≤ 0.10) | Fig 3 (real data), Fig 4 (whether the Fig 3 group result is diagnostic) |
| H2: Rapid forgetting (E: leak 20–200/s, time constant 5–50 ms, same input, sv and fast guesses as C) | E predicts held-out trials as well as C. In recovery, E-generated cohorts often reproduce "C better than E" (FPg_E high), so a C win is not evidence against H2 | Fig 3, Fig 4 |
| H3: Extrema detection (ES with matched components; ESx paper-exact) | ES predicts held-out trials as well as C. ES-generated cohorts often reproduce "C better than ES" (FPg_ES high). ESx rows are descriptive: their separation can follow from the missing sv and fast guesses | Fig 3, Fig 4 (ES decides; ESx reported) |
| H0a (flexibility): C wins only through sv and fast guesses | C's advantage vanishes against alternatives with the same components (E, ES) | Fig 3A: it does not vanish at group level {{N005}}–{{N008}}; Fig 5 |
| H0b (RT shape): C's advantage reflects RT-distribution shape (including how fast guesses are allocated) rather than better prediction of choice proportions | The advantage is in the RT part of the held-out NLL and the choice part is about 0 | Fig 3D (done). Supported against ES, ESx and DDMx: choice part not significant {{N036}} {{N038}} {{N040}}, RT part carries the advantage {{N037}} {{N039}} {{N041}}. Partly against E: small consistent choice advantage {{N034}} plus RT {{N035}}. This sets "mostly through response times" in the THESIS. Fast-guess allocation is not separately quantified [not in ledger] |
| H0c (input): the measured motion energy adds nothing beyond nominal coherence plus drift variability | C with nominal-coherence input predicts held-out trials as well as C with motion energy (Δnom_C not > 0) | Fig 3—figure supplement 1 [PENDING: nominal refits]; sets INPUT. Trial-level use of motion energy cannot be tested with this likelihood (C024). The only trial-level test is the kernel, which is null and underpowered (Fig 2) |
| H4 (architecture): race, LCA or other partially dependent accumulators | Not tested: all models are single opponent accumulators and the task has no equal-evidence condition | None; scope and Discussion limitation (C018) |

## Key control (rules out the boring explanation)
1. Flexibility control (real data): E and ES carry the same input, drift variability and fast guesses as C. They differ only in leak or in the sampling rule. So C vs E {{N005}} {{N006}} and C vs ES {{N007}} {{N008}} cannot be explained by C's extra components. DDMx/ESx comparisons are confounded by components and input and are shown separately.
2. Paired model recovery (Fig 4): every candidate is scored on the same synthetic held-out trials, generated at the mice's fitted parameters and trial counts. The primary criterion G gives the rate at which synthetic 10-mouse cohorts reproduce the Fig 3 group result when E or ES generated the data (FPg) and when C did (SENSg). The per-dataset counts with Clopper-Pearson CIs calibrate the per-mouse > 10 rule and do not set the wording.
3. Choice/RT split (done) and nominal-coherence refits [PENDING]: these show where the advantage lies and whether the measured motion energy contributes beyond nominal coherence. Neither is a test of trial-level use.

## Figure plan (one claim per figure)
| Fig | Claim it supports (claim IDs) | Data source (path) | Status |
|---|---|---|---|
| 1 | Task and behavior: on responded control trials, accuracy rises with coherence {{N028}}. Correct RT trends downward with coherence and errors tend to be faster than correct responses; neither trend survives Holm (C001–C004). Panels: task schematic, psychometric, chronometric, RT distributions by outcome, error minus correct RT per mouse. The legend defines fast guesses vs decision errors (errors at 100% coherence). | /src/dissemination/paper/figures/fig1_task_behaviour_2026-10-26_v2.*; /src/dissemination/paper_control/tables/control_chronometry_2026-10-29.csv, control_per_mouse_2026-10-29.csv | Partial: rebuild on responded control trials only, with the no-response panels removed or moved to Methods; RT-by-outcome and error-minus-correct panels [MISSING: panel script] |
| 2 | Motion energy and kernels: reconstructed motion energy tracks the stimulus, but control-trial kernels are too small and noisy to tell strategies apart, and both models predict a larger kernel than observed (C005–C007, C016, C017). Panels A–C: stimulus reconstruction. D: stimulus-aligned kernel and E: response-aligned kernel, with C and E overlays. | /src/dissemination/paper/figures/fig2_stimulus_reconstruction_2026-10-26_v6.* A–C; /src/dissemination/paper_control/tables/control_kernels_2026-10-29.csv, control_tests_2026-10-29.csv | A–C exist; D–E [MISSING: panel script]; C016 calibration number [MISSING] |
| 3 | Model comparison: at group level, the common model predicts the per-coherence choice and RT distributions of held-out control trials better than E, ES, DDMx and ESx, mostly through RT (t-test Holm; Wilcoxon not significant; 5–6/10 mice individually; robust to dropping any mouse) (C008, C009, C021–C023). Panel A: matched components (E, ES), per-mouse per-1,000 ΔNLL, group test. Panel B: "different components and input" (DDMx, ESx). Panel C: model overlays on psychometric/chronometric. Panel D: choice part vs RT part per alternative (N034–N041). Figure supplement 1: nominal-coherence refits, Δnom per model per mouse and the C_nom vs E_nom/ES_nom ranking (C025, C026) [PENDING: nominal refits]. Supplement table: leave-one-mouse-out (N042). | /src/dissemination/paper_control/tables/heldout_group_2026-10-29.csv, heldout_diff_per_mouse_2026-10-29.csv, heldout_lomo_2026-10-29.csv (reproduce /src/dissemination/paper_accumulation/tables/heldout_per_trial_2026-10-28.csv exactly); nominal fits /mnt/data/processed/ddm/fits_resp_nominal_matched_{C,E,ES} [PENDING] | Numbers for A, B, D and LOMO exist; panels [MISSING: panel script]; supplement 1 [PENDING: nominal refits; control_heldout.py _nom models not yet added] |
| 4 | Recovery: how often the group test reproduces the Fig 3 result when each model generated the data; this sets the THESIS variant (C010–C012). Panel A (primary): cohort-level reproduction rates, a 5 x 5 matrix of FPg/SENSg, with the E and ES cells (the decisive ones) marked. Panel B: per-dataset counts of Δ > 10 with Clopper-Pearson CIs, 5 x 5. Panel C: δ distributions for E-, ES- and C-generated datasets with the real-data per-mouse values marked. | /mnt/data/processed/ddm/recovery_full_cpu_resp/ (320 + 180 fits); datasets /mnt/data/processed/ddm/recovery_datasets_cpu_2026-10-29/ (manifest of 100) | [PENDING: paired recovery]; cohort post-processing script [MISSING]; [MISSING: panel script] |
| 5 | Components: fast guesses are needed for held-out prediction. Removing drift variability, adding leak or urgency, or fixing the guess bias does not change prediction at group level (C013–C015). Supplement panel: data minus model fast-error RT (exploratory, C015), linked to the architecture limitation (C018). | /src/dissemination/paper_accumulation/tables/components_group_2026-10-28.csv, components_per_trial_2026-10-28.csv; control_per_mouse_2026-10-29.csv | Numbers exist; panels [MISSING: panel script] |

## Scope: what this paper will NOT claim
- No pulse-trial results, primacy, pulse gain or temporal-weighting claims. Pulse trials appear in Methods only as excluded trials.
- No comparison or interpretation by site (UCLA vs UW); rig is a covariate only.
- No analysis of trials without a response by 5 s {{N004}}. All likelihoods are conditional on a response by 5 s.
- No claim that mice integrate rather than forget rapidly or detect extrema unless variant A is selected. Under I_E or I_ES, the claim is made only against the separated alternative.
- No claim that recovery against DDMx or ESx bears on integration vs non-integration. Those rows are descriptive.
- No claim that mice use each trial's own motion energy, or that within-trial motion fluctuations drive choices or the model advantage. The likelihood pools trials per signed coherence (C024), and the only trial-level test, the kernel, is null and underpowered {{N019}} {{N027}}. "Net motion energy" names the model input. Even the nominal-coherence comparison concerns the within-coherence stimulus distribution only.
- No claim that the common model predicts choices better than the matched extrema model: the choice part is about 0 {{N036}}. Against E, the choice advantage is reported as small {{N034}}.
- No claim that a flat or null kernel means mice ignore motion fluctuations: the kernel test is underpowered {{N027}} and the models over-predict the kernel {{N029}}.
- No architecture claim. All models are a single bounded accumulator of net (opponent) motion energy. Race and LCA models were not fitted, and the control task has no equal-evidence condition that could constrain architecture (Kirkpatrick et al. 2021, doi 10.1037/rev0000284, unverified until S2). The fast-error misfit {{N026}} is discussed as consistent with architecture or starting-point-variability alternatives, not as evidence for any of them.
- No claim that drift variability is needed at group level {{N013}}; only fast guesses are {{N014}}.
- The model without drift variability appears only in one Methods sentence, without numbers (C020, D003). No no-sv results, tables or Discussion.
- Rapid forgetting means leak 20–200/s (time constant 5–50 ms). Slower leak is not tested and no integration time constant is claimed. No free-leak fits (D009).
- No claim that the chronometric trend or fast errors are significant: both fail Holm {{N022}} {{N024}}. The fast-error misfit of the common model is exploratory {{N026}}.
- Recovery is at each mouse's fitted parameters only. No claim about recovery elsewhere in parameter space (for example, E at slower leak).
- No design guide or simulated designed perturbations (D003 NH7). Under B, the Discussion states qualitatively that designed evidence perturbations are needed.
- The earlier recovery run with unpaired synthetic data is reported in Methods only as superseded and invalid. Its counts are not reported [not in ledger].
- No neural mechanism and no optimality claim. No "mechanism" or "strategy used by mice" wording outside variant A.
<!-- LOCK-END -->

## Glossary (one term per concept; never use synonyms)
| Term | Definition | Do not use |
|---|---|---|
| control trial | A trial with no added motion pulse (sched_pulse_type 0) | no-pulse trial, baseline trial |
| responded trial | A trial with a choice and RT ≤ 5 s; the only trials analyzed | valid trial, completed trial |
| coherence | Nominal signed fraction of coherently moving dots | motion strength (except in Methods definition) |
| motion energy | Output of the spatiotemporal energy filter applied to the replayed stimulus, in % coherence units | ME (in text), motion signal |
| net motion energy | Rightward minus leftward motion energy; the model input of C, E and ES (DDMx/ESx and the nominal refits use nominal coherence) | opponent signal (except once, in Methods); "evidence the mouse uses" |
| psychophysical kernel | Mean motion-energy fluctuation, choice-conditioned, as a function of time (stimulus- or response-aligned) | reverse-correlation kernel, temporal weighting function |
| chronometric function | Median correct RT as a function of absolute coherence | RT curve |
| common model (C) | Single bounded accumulator of net motion energy with drift variability, fast guesses and free guess bias (L0U0V1Z0G1), responded-only | full model, DDM (alone), winning model |
| rapid-forgetting model (E) | Common model plus leak (20–200/s, time constant 5–50 ms) | leaky model, forgetting model |
| extrema-sampling model (ES) | Non-integration model that commits when a single sample exceeds a threshold, with the common model's components (sv, fast guesses) | extrema model |
| paper-exact models (DDMx, ESx) | Integration and extrema-detection models as specified by Stine et al. 2020 (nominal coherence input; without sv, fast guesses, leak or urgency) | Stine models |
| nominal-coherence refit (C_nom, E_nom, ES_nom) | C, E or ES refit with nominal coherence as input and otherwise identical components | ablation, shuffled model |
| non-integration strategy | Rapid forgetting or extrema detection | non-accumulation, snapshot |
| fast guess | Response drawn from the model's stimulus-independent fast RT component. Errors at 100% coherence can arise from fast guesses or from decision errors; the paper does not split them except through the fitted model | lapse, guess (alone), contaminant |
| drift variability (sv) | Across-trial SD of the drift rate | noise, trial-to-trial variability |
| held-out NLL | Negative log likelihood of per-coherence choice counts and per-choice RT quantiles on cross-validation test trials; group statistics per 1,000 trials | test loss, cross-validated likelihood, trial-wise likelihood |
| choice part / RT part | The two terms of the held-out NLL: choice counts per coherence, and RT quantiles per coherence and choice | choice likelihood (alone), RT likelihood (alone) |
| synthetic cohort | One synthetic dataset (replicate) per mouse for all 10 mice, from one generator | simulated experiment |
| reproduces | A synthetic cohort reproduces the result for X when mean δ_X > 0 and the Holm-adjusted one-sample t-test p < 0.05 (Holm over the 4 non-C candidates) | replicates, recovers |
| model recovery | Fitting all candidates to synthetic datasets generated by each model and scoring them with the held-out rule | parameter recovery (different concept) |
| separated | Criterion G for X in {E, ES}: FPg_X ≤ 0.10 and SENSg_X ≥ 0.50 | identifiable, distinguishable (in technical statements) |
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
| Results Fig 3 | The held-out group result is checked by recovery at the level of the group test (criterion G), with per-dataset counts and CIs beside it | Results Fig 4 | open [PENDING: paired recovery] |
| Results Fig 3 | Wilcoxon result, per-mouse counts and leave-one-mouse-out stated beside the t-test | Results Fig 3 text {{N006}} {{N008}} {{N010}} {{N012}} {{N030}}–{{N033}} {{N042}} | open |
| THESIS / Results Fig 3 | "Mostly through response times": choice vs RT split shown for every alternative | Results Fig 3D {{N034}}–{{N041}} | open |
| Methods | The likelihood pools per coherence, so no comparison tests trial-level use of motion energy (C024) | Methods model comparison; Discussion limitations | open |
| Results Fig 3 | Nominal-coherence refits reported with the pre-fixed rule; INPUT wording set by C's row | Fig 3—figure supplement 1; decisions.md entry | open [PENDING: nominal refits] |
| Methods | Recovery selection rule, ES addition, criterion and thresholds fixed before results; unpaired preview disclosed as superseded and invalid (C019) | Methods recovery subsection; decisions.md entry | open |
| Methods | One sentence: the sv model set was chosen after the no-sv comparison had been seen, and the ranking depends on sv (C020) | Methods model set | open |
| Results Fig 2 | Kernel power caveat and model over-prediction quantified | Results Fig 2 text {{N027}} {{N029}} | open |
| Results Fig 5 | Fast-error misfit flagged as exploratory, revisited as an architecture limitation | Discussion limitations (C018) | open |
| Scope | Architecture not constrained; net motion energy is the model input only | Discussion limitations | open |
| Scope | Leak range tested (20–200/s) and untested slower leak stated | Methods models; Discussion limitations | open |
| Discussion | What would decide integration under B or I: designed evidence perturbations (qualitative, no design guide) | Discussion D4/D5 | open |
