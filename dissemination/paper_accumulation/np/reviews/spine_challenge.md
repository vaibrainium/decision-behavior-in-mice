<!-- np-contract
stage: S1 ; section: spine_challenge ; agent: np-devils-advocate ; version: v1
thesis: "In mice performing a reaction-time random-dot motion task, held-out control-trial choices and response times were better explained by a bounded accumulator with drift variability and fast guesses than by a tested rapid-forgetting model, but brief motion pulses could not resolve whether the accumulator weights early or late evidence more heavily."
claims: C001, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012
numbers: N016, N020, N021, N026, N029, N030, N033, N042, N043, N047, N063, N065, N071, N078, N079, N082, N083, N097, N098, N110, N112, N113, N114, N115, N117, N118
sources: stine2020differentiating, hyafil2023temporal, brunton2013rats
-->
# Spine challenge (S1, accumulation-first variant)

Scope: the locked spine at `np/spine.md` v1, read against `np/ledger/claims.csv`, `np/ledger/numbers.csv`, the analysis
log (sections 5.6, 5.8–5.13), and the reports on control-only selection, amendment 6 and the observed fluctuation
kernel. The spine is not edited. Rig is treated as a covariate only. No challenge below asks for site-level
interpretation.

Summary verdict on the thesis as worded: the sentence is mostly defensible *as a relative statement*, but the spine
builds an "accumulation-first" paper on it (working title "Mice accumulate continuous motion evidence"). That framing
rests on one family of evidence: the shape of control-trial RT distributions under a model whose input mapping and
pulse predictions fail elsewhere. Every analysis that looks directly at within-trial temporal use of evidence either
rejects both models, leans toward the rapid-forgetting model below threshold, or had no power. Point 3 reports that a
question went unanswered. Its most informative content (pulse sensitivity about 10 times higher than predicted) is
pushed to a supplement.

---

## FATAL (sinks the accumulation-first framing unless answered)

### F1. No one has shown that the control-trial comparison can tell the two models apart. All within-trial tests fail to support it.
**Argument.** C004 says held-out control prediction favored the accumulator in 6/10 mice (N110) with a summed
difference of +345.7 (N016). Three things are missing:
1. **No recovery for this comparison.** Model recovery (N083) used five nested accumulator generators. None was the
   rapid-forgetting model (E). The only E-generated recovery in the record is pulse-based (N097: 1/20 and 0/20). So
   nobody has checked whether control-only five-fold CV picks E when the data come from E. A hostile reviewer will
   ask first whether the scoring rule favors the integrator by construction. Three features make this a live
   concern:
   - E's fitted bounds are tiny (separation 0.52–1.02 against a median of 7.9 for the integrator; analysis log 5.8).
   - The score has an empty-prediction penalty of 20 per data trial and minimum-count rules for RT cells (N079).
   - 4/60 E fits sit at the leak lower bound of 20/s.
2. **The input on control trials is close to constant.** On control trials the stimulus-aligned fluctuation
   sensitivity is tiny (0.1–0.4 % coh; fluctuation-kernel report caveat). The hidden-coherence analysis is excluded
   from the paper. So the control comparison may mostly compare two first-passage-time distribution families given
   nominal coherence: a Wiener process with large sv against an Ornstein–Uhlenbeck hazard process. Extrema detection
   is defined by *how momentary evidence is used over time*. Choice and RT shape at fixed coherence cannot test that
   alone, and the spine's own Opening says as much (stine2020differentiating).
3. **Every direct within-trial test fails to support the claim.**
   - The prespecified response-aligned kernel (amendment 8) returned "neither model fits", and it was not
     underpowered: the rule identified E-generated data 19/20 and I-generated data 14/20. So the integrator's
     prediction of how mice use fluctuations was rejected by a test that could detect a mismatch.
   - The pulse strategy statistic leaned toward E: z = 2.97, same sign in 8/10 mice (N029). That is just under the
     3-SD rule and was declared underpowered.
   - The spine records neither of these in the Resolution.

**What would answer it.**
- (a) Control-only CV model recovery with E as a generator, using E's fitted control parameters for all 10 mice and
  at least 2 replicates, scored exactly as N016/N110. The E-generated synthetic datasets from the fluctuation-kernel
  power work may be reusable. Report the confusion matrix: E→E, E→I, I→I.
- (b) Split the E–I difference into its choice, RT, censoring (P(RT > 5 s)) and empty-cell-penalty terms, per mouse.
  If the advantage comes mainly from the penalty or the censoring term, it is not evidence about integration.
- (c) Refit both models with nominal coherence as a constant-drift input. If the E–I difference is unchanged,
  rewrite the claim as "control RT distributions are better described by…" and drop "accumulate continuous motion
  evidence" from the title.
- (d) Put the amendment 8 verdict and the pulse strategy z in the main text next to Figure 3, as prespecified results
  that do not support the integrator. At present they are an optional G1 sentence, which is selective reporting.

If (a) shows good E→E recovery and (b) shows the advantage spread over choice and RT terms, F1 drops to MAJOR.

---

## P0 / MAJOR

### M1. The control-fitted model fails out of sample in exactly the regime that tests integration, and point 2 depends on that model.
**Argument.**
- The integrator predicts a pulse effect of about 0.03 logit (0.7 pp). Observed: about 0.3 logit, about 10 times
  more, still present at 0% coherence (0.574 vs 0.508). See N026 and analysis log 5.10.
- A per-mouse pulse gain (0.06–7, N042/N043) only reduces the departure to +0.24 (N030).
- In PSUIM6/7, the gain that best fits choices costs 96–107 units on the remaining (RT) objective (N063–N066).
- A model that cannot jointly fit the choices and RTs of a known evidence perturbation is weak support for the claim
  that it is the mechanism generating control choices and RTs. Joint choice/RT prediction is the basis of point 2.
- The model also misfits control trials: error RTs are faster than predicted at 36–100%, and P(RT > 5 s) at 100% is
  underpredicted in three mice (log 5.8, 5.12).
- E failed the pulse predictions as badly. So point 2 is "the less-bad of two misspecified models", which the spine
  should say explicitly.

**Alternative account.** Both models get the mapping from stimulus to decision variable wrong for transients, so the
control comparison tells us which RT family fits better, not which algorithm the mouse runs.

**What would answer it.**
- Main-text sentence plus panel: put the predicted against observed pulse effect next to Figure 3, not in a
  supplement.
- Repeat (F1b) for the pulse misfit: which objective terms fail.
- Rewrite C001/C012 so that "the control data constrain the form of the accumulator" is qualified by "within a model
  that does not predict responses to brief transients".

### M2. The selected front end (amendment 7) is missing. The input assumption that the whole comparison rests on was rejected on control trials.
**Argument.**
- Analysis log 5.13: a compressive power-law front end (F1) beat the linear front end (F0) on control-only CV by
  −62.7 summed (2 SD = 28.9) and passed the prespecified rule, so it is the *selected* front end. γ was 0.62–0.77 in
  five mice.
- The spine never mentions it. C006 ("needed accumulator variant") and Figure 4 describe the F0 model as though it
  were the selected model.
- Every E vs I comparison (N016, N110, N112) used the linear front end the selection rejected.
- This is the "motion-energy input assumption" boring explanation in its most concrete form. With compressive input,
  a ±100% pulse is compressed, so the integrator's pulse prediction gets smaller and M1 gets worse.

**What would answer it.**
- Report amendment 7 in Figure 4 / C006.
- Repeat the E vs I comparison and the free-leak fit with F1 (control-only CV, same scoring).
- If the ranking holds, C004 becomes robust to the front end. If it does not, the thesis changes.

### M3. The free-leak time constant (C005) lacks an identifiability check. The 2–20/s range was never compared under cross-validation.
**Argument.**
- The free-leak fit (0–200/s) is in-sample on all control trials and was never cross-validated (N112).
- In model recovery, leak was detected in only 35% of datasets that contained it. Where the generators had sizeable
  leak, hits were 0.5 (DBM15, 4.1/s), 0 (DBM5, 0.8/s), 0.5 (PSUIM6) and 1.0 (PSUIM7) (log 5.8).
- So the procedure often misses leak of about 1–4/s, which means a fitted leak below 2/s cannot rule out time
  constants of about 0.25 s.
- The all-trial L1 generator fit for DBM15 has leak 4.1/s (τ ≈ 0.24 s). That conflicts with "below 2/s in every
  mouse" and suggests the leak estimate shifts with the trial set.
- The CV comparison only covers 0 against 20–200/s (τ 5–50 ms). Moderate leaky integration (τ 50–500 ms) is the
  realistic rodent alternative (hyafil2023temporal, brunton2013rats discuss leak), and it was never compared under
  cross-validation.

**What would answer it.**
- (a) Held-out profile over a fixed leak grid (0, 1, 2, 5, 10, 20, 50/s) per mouse.
- (b) Parameter recovery for leak in the free-range model at generating values of 1, 2, 5, 10 and 20/s.
- (c) Explain the DBM15 all-trial 4.1/s against below 2/s on control trials.
- Until then, C005 should say "point estimates below 2/s; resolution limited (see recovery)".

### M4. C006 contradicts the ledger: adding leak did improve the summed held-out score.
**Argument.**
- N113 is −21.3. The sign convention in the control-only report and in log 5.6/5.13 is "negative = better", so adding
  leak *improved* the summed held-out NLL by 21.3, and leak plus urgency improved it by 33.3.
- C006 says adding leak or urgency "did not improve the summed held-out score". That is wrong for leak and for the
  combination. Both gains are inside summed Monte Carlo noise (SD 22–54 at 15 reps), and the CV splits had no warm
  starts, which biases against larger models (report caveat).
- For an accumulation paper this matters. The direction of the leak evidence on held-out data is toward *some*
  leak, not away from it.

**What would answer it.** Reword C006 to: "leak and urgency did not improve the held-out score beyond Monte Carlo
noise (summed −21 and +26; beyond 10 units only in one mouse)". Better still, rescore with 10 seeds × 50 reps and
warm-started CV fits, as was done for F1.

### M5. Fast guesses (median 21% of trials) may decide both the E vs I comparison and the pulse effect. This is the lapse explanation.
**Argument.**
- The stimulus-independent fast-guess component has median p = 0.21 (range 0.12–0.35; N047).
- Its delay is not recovered (r = 0.18, N021), and fast (< 0.6 s) responses make up 14–34% of trials in some mice.
- If fast responses are partly stimulus-dependent, the "guess" component is soaking up exactly the early, accurate
  commitments that an extrema-like or short-τ strategy would produce. That pre-empts H2.
- E's tiny bounds compete with the guess component for fast responses. The comparison may therefore turn on how each
  model shares out fast trials, not on integration.
- Separately, the pulse-gain tradeoff fits a different reading: pulses shift *direction* without speeding responses,
  which looks like a choice or guess bias rather than added drift.

**What would answer it.**
- (a) Conditional accuracy functions: accuracy against RT bin per coherence, observed against both models. If
  < 0.6 s responses are above chance and rise with coherence, the guess component is misspecified.
- (b) Rerun E vs I with p_guess fixed at 0, and with the guess component restricted to responses before stimulus
  onset or below a fixed latency.
- (c) For pulses: the directional contrast restricted to responses more than 300 ms after pulse onset (excluding
  reflexive responses), plus the effect of pulses on RT. A pulse that shifts choice without shifting RT is
  bias-like, not evidence-like, under these models.

### M6. Point 3 is an absence of a finding from a design that could not have succeeded. Its positive content is buried.
**Argument.**
- The power finding (log 5.7) was derived *after* data collection: a 50–67 ms pulse carries 0.05–0.08 coh·s,
  predicting about 0.6 pp; the GLMM SE on β_middle is about 0.05–0.07 against an expected change of 0.02–0.04.
- Calibration confirms 0–1/20 detection (N098), and the synthetic kernel detects 0/20 (N117).
- An eLife reviewer will read this as "the pulse arm was underpowered by design", which is a lab-notebook outcome and
  not a result.
- The spine promises design guidance (D5) but no simulation identifies a design that *would* work.
- Meanwhile the one positive pulse result is moved to a figure supplement (C010): pulse sensitivity about 10 times
  the motion-energy prediction, persisting at 0% coherence, varying across mice, with a choice/RT gain conflict.
  For an accumulation-first paper this is the result that most challenges point 2, and it is the most interesting
  thing in the pulse data.

**Is it publishable at eLife?** As written, point 3 adds little significance. With an accumulation-first framing, a
"couldn't tell" third result plus a demoted misfit looks like hiding a problem. Two honest routes:
- (i) Make point 3 "brief pulses drive choices about 10 times more than an accumulator fitted to continuous motion
  predicts, so pulse-based temporal-weighting designs in mice need models of transient sensitivity". Then add a
  forward simulation that gives the pulse strength, duration and trial count needed for 80% detection of 20% decay
  under the gain-revised model.
- (ii) Drop the temporal-weighting question from the title and abstract, and report the primacy pipeline as a
  prespecified negative in Methods/supplement.

The current hybrid (thesis clause plus main Figure 6 of null calibrations) is the weakest option.

### M7. "Control trials only" is not strictly true for the baseline inputs (key control ii).
**Argument.**
- The legacy DDM input labels 48 UCLA no-response pulse trials as control. Of these, 38 are genuine non-null pulses
  (N071), and they enter the censoring term of every control-only fit and of the E vs I comparison.
- The spine's key control says "pulse-trial misfit cannot enter the baseline".
- The fluctuation-kernel v2 rerun already excluded these trials (N117 note). The model comparisons did not.

**What would answer it.** Rerun N016/N110 and the component CV on corrected labels, or bound the effect (38 trials out
of about 16.5k, censoring term only) and reword key control (ii) to "control trials as labeled in the analysis input;
38 mislabeled pulse trials retained (see Methods)".

---

## P1 / MINOR

- **P1-1. Per-mouse counts sit at the edge of Monte Carlo noise.**
  - The 10-unit threshold is uncalibrated for N016 (N082 note).
  - Per-mouse MC SD at 15 reps is 6.5–12.8, so "> 10" is about 1 SD.
  - The 6/10 count (N110) and the sv 8/10 and guesses 7/10 counts (N115/N116) need the 10-seed × 50-rep rescoring
    used for F1.
  - Also report the per-trial-normalized difference, so the summed +345.7 is not just a measure of which mice ran
    the most trials. The 4 non-distinguishing mice are the smallest ones.
- **P1-2. "Needed drift variability" may be engagement or history in disguise.**
  - Median sv (2.37) is close to median drift gain (2.91), and 10/50 integrator CV fits reach the sv upper bound.
  - Across-trial drift variability will absorb arousal/engagement drift, slow drift across 50 sessions, and
    choice-history effects. Neither model includes these, and recovery has a 35% sv false-positive rate (N020).
  - Add previous choice/outcome to drift offset or starting point and check whether the need for sv shrinks.
    Otherwise phrase sv as "across-trial variability not explained by the stimulus".
- **P1-3. sz (starting-point variability) was not tested on the selected model.**
  - The classic explanation for fast errors (observed at 36–100%) is sz.
  - N118 comes from an earlier, different model generation (all-trial CV, L1U1 base, before fast-only guesses) and
    was split 2 for and 2 against per mouse.
  - Test sz on L0U0V1Z0G1 with control CV, or state that it was not tested in the current generation.
- **P1-4. Figure 2 is a methods figure built on a claim (C003) with no behavioral consequence in the paper.**
  - "Fluctuations beyond nominal coherence" is a stimulus fact. The analyses that show behavior uses them are
    excluded (hidden coherence) or inconclusive (kernel).
  - Either show that motion-energy input beats nominal-coherence input on held-out control trials (links F1c), or
    move Figure 2 to Methods/supplement.
- **P1-5. Motion-energy filter parameters are a hidden degree of freedom in the leak contrast.**
  - The temporal filter (temporal support 0.55 s, about 116 ms delay; N073, log 5.12) already integrates the input
    over a window comparable to E's forgetting time.
  - "Rapid forgetting at 20–200/s" therefore applies to a smoothed signal, and the result depends on the filter.
  - Report how the filter parameters were chosen (whether behavior was used) and run one sensitivity check with a
    shorter temporal filter.
  - The rig-specific replay approximation of pulse energy (log 5.10) belongs here as an input caveat with rig as a
    covariate. No site-level reading.
- **P1-6. Novelty against precedent.**
  - Integration beating extrema/snapshot models has been shown in rats (hyafil2023temporal; brunton2013rats). The RT
    approach to separating integration from extrema detection is stine2020differentiating's own proposal.
  - Mouse evidence-accumulation tasks with temporal kernels exist (for example Odoemene et al. 2018, flashes; Pinto
    et al. 2018, towers; both need S2 verification before citing).
  - What is new is narrow: continuous RDK, RT, mouse, held-out joint fit. Say so plainly in the Opening. S2 should
    check for mouse RDK reaction-time DDM work.
- **P1-7. Wording of the H1/H2 table.**
  - H2 predicts a free-leak fit "settles at high leak", but given M3 the free-leak fit has low power to show that.
  - H1's figure decision depends on F1 being resolved. Mark both rows "conditional on recovery (F1a, M3b)".
- **P1-8. The pulse effect (C008) and transient/salience explanations.**
  - A ±100% coherence burst is also a salient visual transient. Spine scope already declines to attribute it to a
    stage, which is right.
  - With no eye or body tracking, Figure 5's "shifted response direction" should not be paired with "evidence"
    wording anywhere in the accumulation framing. The thesis currently calls pulses "motion pulses" inside a sentence
    about weighting evidence, which implies they are evidence.

---

## What a hostile reviewer writes first
"The authors claim mice accumulate motion evidence because a Wiener-diffusion model with large across-trial drift
variability and a 21% guess mixture fits control RT distributions better than a strongly leaky one. The comparison was
never recovery-validated, uses an input front end their own selection rejected, and both models miss the pulse effect
by about 10 times. The authors' own prespecified, adequately powered fluctuation-kernel test rejected the accumulator.
The temporal-weighting question was unanswerable by design. What remains is a descriptive model fit."

## Single experiment or analysis most likely to sink point 2
Control-only CV recovery with E as the generator (F1a). If E-generated data are also scored as favoring the
integrator, then N016/N110 carry no information about strategy.
