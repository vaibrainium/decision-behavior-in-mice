# Paper plan: evidence integration over time in mice (RT motion task with pulses)

**Author decision, 2026-10-22 (client date):** strategy discrimination (integration versus the extrema approximation)
is the primary paper question; primacy is secondary and conditional on predictive adequacy and sensitivity.
The historical confirmatory analysis endpoints and testing order are unchanged. A first prose draft is in
[`manuscript_2026-10-22.md`](manuscript_2026-10-22.md); its qualifications supersede stronger wording below:
the shared hidden-coherence ratio is a conditional model estimate, not an established population-wide discount;
final strategy discrimination and temporal-weighting results remain pending queued Hyak jobs.

**Status:** living outline, not prose. Started 2026-10-20; **revised 2026-10-22** after the common-model choice, the
leak/urgency diagnosis and the primacy power result (changes listed at the end).
**Sources:** [`mouse-ddm-analysis-log.md`](../reports/mouse-ddm-analysis-log.md) (log),
[`mouse-ddm-next-steps.md`](../reports/mouse-ddm-next-steps.md) (next steps),
[`primacy-analysis-plan.md`](../reports/primacy-analysis-plan.md) (primacy plan, amendments 1–3),
[`motion-energy-methods.md`](../reports/motion-energy-methods.md) (ME methods), agent reports in `.agents/reports/`,
figure captions in [`figure_captions.md`](figure_captions.md).

Status tags used below:
- **FINAL**: result done and documented; can be written up now.
- **PROVISIONAL**: result exists but depends on a plan step still running; write the methods, leave numbers as `[TBD]`.
- **PENDING**: not run yet.
- **MISSING**: information the authors must supply (nothing in the repo says it).
- **SUSPECTED**: an inference not yet checked; never goes into prose as a result.

No number goes into prose unless it is tagged FINAL here, with its source.

---

## 1. Core story

**Question.** Do mice weight early motion evidence more than late evidence (primacy), once you account for the
reasons a reaction-time task makes late evidence matter less anyway?

**What changed (2026-10-22).** The timing question may not be answerable with these pulses. Under the fitted model a
±100%, 50–67 ms pulse moves choices by only ~0.025 logit (~0.6 percentage points), so even complete primacy changes the
expected timing contrast by ~0.02–0.04 logit, against an expected SE of ~0.05–0.07 (report
`2026-10-22-primacy-power.md`; SE is SUSPECTED, scaled from trial counts). The test becomes informative only if mice
react to pulses much more than the model predicts, which gate 1 checks first (decision 2026-10-22, option 2).
So the paper now rests on three finished or nearly finished results (R1–R4) plus a pulse result whose form depends
on gate 1.

**The argument, in order:**
1. Mice do a reaction-time random-dot motion task on two rigs (UCLA, 4 mice; UW, 6 mice; 50 sessions), with brief
   ±100% coherence pulses at early, middle and (UW only) late times. *(FINAL; Fig 1)*
2. To know what evidence the mice saw, we replay every trial's stimulus and compute motion energy with filters tuned
   to mouse vision, calibrated per rig. *(FINAL; Fig 2)*
3. In standard RDKs the stimulus noise is a **fixed bias per trial** ("hidden coherence"), not fresh noise over time.
   Mice use it but discount it to about 0.35–0.50 of programmed coherence. Consequence: noise-based psychophysical
   kernels cannot show when evidence is weighted in these tasks. *(FINAL; Fig 3)*
4. A motion-energy-driven DDM with drift variability (sv) and fast guesses at chance (guess delay ≤ 0.3 s), censored
   at 5 s with a 0.3 s response floor, explains choices and RTs; leak and urgency are not needed in most mice. Where they
   help (PSUIM5/6/7), they mainly fit the coherence-independent share of responses after 5 s, which looks like a
   delayed, variable start of integration. *(PROVISIONAL: model chosen, final fits / step 3.3 / recovery pending; Fig 4)*
5. **Do mice integrate at all?** (added 2026-10-23, after Stine et al. 2020.) Good DDM fits, sigmoid psychometric
   functions and accuracy that rises with RT are also produced by strategies that don't integrate, notably extrema
   detection. We test it two ways: (i) on control trials, the strict integrator vs an extrema-detection model (same
   model with a 5–50 ms time constant); (ii) on pulse trials, out of sample: which model's frozen predictions explain
   the observed pulse effects. The pulses are what make (ii) possible: the two strategies are expected to predict
   different effects of a brief strong pulse (SUSPECTED until E's predictions are computed, amendment 4 item 4). *(PENDING; primacy plan amendment 4, adopted 2026-10-23)*
6. Pulses: does a brief strong pulse move choices as much as its motion energy predicts, and does its effect depend on
   timing beyond what the model predicts? *(PENDING; Fig 5)*

**What this does to the paper.** With point 5, the paper goes from *assuming* integration to *testing* it in mice,
with a stimulus manipulation the human study didn't have. That holds whichever way gate 1 goes, so point 5 is now the
most likely centre of the paper, with temporal weighting as the second question.

**R5 outcome (2026-10-23): branch (a2), final.** Gate 1 failed (+0.30 logit vs predicted 0.03); the strategy test did
not distinguish E from the integrator (underpowered); the amendment 6 pulse-gain revision also failed (+0.24); its
calibration was valid under the null but detected 0–5% of 10–40% primacy. The primacy analysis is stopped (primacy plan,
closing note; analysis log 5.10–5.11). Write R5 as: mice respond to brief pulses more than a motion-energy model fitted
to control trials predicts, by an amount that varies between mice; temporal weighting is not resolvable with these
pulses. Manuscript version `manuscript_2026-10-23.md`.

**Three ways R5 can come out** (draft all three now, so the outcome doesn't shape the framing):
- **(a) Gate 1 fails: pulses matter far more than predicted.** Mice react to a 50–67 ms full-coherence pulse much more
  than a motion-energy integrator fitted to control trials predicts. With amendment 4, the frozen extrema-detection
  predictions say whether a non-integration strategy explains it: (a1) E predicts the pulse effects → evidence that mice
  (at least some) do not integrate, and any "primacy" in raw pulse effects is a by-product of detection; (a2) neither
  model does → the integrator is revised (documented, before any timing test), and the finding is a disproportionate
  sensitivity to brief strong transients (salience, nonlinear weighting of coherence). Without amendment 4, only (a2)
  is available and any strategy explanation is post hoc.
  *Prior hint, not a result:* the SfN 2025 poster's early-pulse psychometric shift was ~10% coherence, which would be
  several tenths of a logit, an order of magnitude above 0.025, if it survives the scheduled-label correction (the
  poster grouped trials by preprocessing's RT-dependent `pulse_type`). SUSPECTED until gate 1 runs.
- **(b) Gate 1 passes: pulses act as predicted, timing test underpowered.** Report the timing test as planned with the
  sensitivity result, worded as "pulses of this strength cannot resolve primacy", plus a design result: what pulse
  strength/duration or trial count would. Headline moves to R3/R4.
- **(c) Gate 1 passes and the timing contrast is still clearly non-zero.** Unlikely under the power estimate; report
  as planned (primacy or recency), with the mechanism tests (gain decay, signed leak).

**Framing (from the SfN 2025 poster).** Comparative: mice learn the primate random-dot task and use bounded evidence
accumulation like primates. Still fits all three outcomes. What the paper adds over the poster:
- *Poster:* early pulses shift the psychometric function most, read as primacy. *Paper:* in an RT task that pattern
  is expected even with flat weighting (Okazawa et al. 2018), and under our model the pulses should barely matter at
  all, so the raw shifts become the observation that the model has to explain (gate 1, Fig 5A). The paper must not
  repeat the poster's primacy claim.
- *Poster:* accuracy plateaus with RT, read as bounded accumulation. *Paper:* the DDM fits are the evidence; the curve
  is descriptive (Fig 1G).
- *Poster:* pulse windows 0–160 / 160–320 / 320–480 ms; 26 sessions. *Paper:* scheduled onsets per rig; 50 sessions
  (the 26 was a counting bug, see `figure_captions.md`).

**Possible titles** (placeholders, by outcome):
- (a1) "Brief motion pulses reveal [extrema detection / a non-integration strategy] in mice".
- (a2) "Mice weigh brief motion pulses far more than an evidence accumulator predicts".
- If the integrator wins both tests: "Motion pulses confirm evidence integration in mice", the strongest version of
  the poster's comparative claim.
- (b) "Hidden stimulus noise and the limits of measuring evidence timing in mice", or, in the poster's style, "Mice
  accumulate visual evidence like primates".
- (c) "Mice integrate motion evidence [with primacy / recency] in a reaction-time task".

---

## 2. Figure plan

| Fig | Content | Status | Source |
|---|---|---|---|
| 1 | Task (illustration, trial timeline, pulse traces), psychometric (all mice), chronometric and late-response rate per rig, accuracy vs RT, RT distributions | **Drafted** (panel A illustration to draw; panel F relabel, see §5) | `scripts/paper/fig1_behaviour.py` |
| 2 | Motion energy: filter, ME time courses by coherence, linearity, pulse response (peak 117 ms) | **Drafted** | `scripts/paper/fig2_motion_energy.py` |
| 3 | Hidden coherence: per-trial noise bias, it explains ME noise, per-mouse weight (k ≈ 0.50) with robustness, why noise kernels can't resolve timing | Results FINAL; figure to make | log §3.3; notebook 2.14 §1–5 |
| 4 | DDM: schematic (ME input, bound, sv, fast guesses, censoring at 5 s, 0.3 s floor); per-mechanism held-out change per mouse against the Monte Carlo noise (sv, guesses pass; leak, urgency in 3–4 mice; sz fails); fit quality of the common model (psychometric, chronometric incl. error RTs, P(response after 5 s)) | Comparison FINAL (log 5.6); fit quality PENDING (final fast-only fits) | `mc_noise_per_mouse.csv`; notebook 3.0 |
| 5 | Pulses: (A) raw pulse effects by timing, scheduled labels (descriptive); (B) gate 1: observed vs predicted pooled pulse effect per mouse, **with both the integrator's and extrema detection's frozen predictions**; (C) pulse-trial log-likelihood, E minus integrator, per mouse (amendment 4); (D) predicted vs observed effect by timing under each model; then by outcome: β_middle posterior, per-mouse estimates, UW late, sensitivity curve | Results FINAL (branch a2): panels A–D plus revised gate and calibration; no β_middle panel (timing test not run) | primacy plan §5–9, amendments 4–6, closing note; `scripts/ddm/primacy.py`, `fit_pulse_gain.py`, `primacy_calibration.py` |
| 4D | Integration vs extrema detection on control trials: held-out NLL per mouse against the Monte Carlo noise; per-mouse integration time constant (descriptive) | PENDING (amendment 4) | primacy plan amendment 4 |
| S1 | Rig behaviour check (response floor, pulse frames) | FINAL | log §6b |
| S2 | Monte Carlo noise of the comparison; warm starts; where leak/urgency help (late-response rate, PSUIM5/6/7) and UCLA vs UW behaviour | Results FINAL; figure exists in draft | log 5.5–5.6; `figures/leak_urgency_diagnosis_20261022.png` |
| S3 | Model and parameter recovery | PENDING (step 4, submitted) | `scripts/ddm/model_recovery.py` |
| S4 | Guess forms (fast_only best, 9/10 mice); fitted lapse vs psychometric lapse (16–53% implied vs ≤ 1.5% fitted) | Results FINAL; figure to make | `compare_guess_forms.py`; report 2026-10-21 |
| S5 | Control-only CV check of the model choice | PENDING (step 3.3) | next steps step 3 |
| S6 | Late responses (> 5 s): share by coherence, accuracy by coherence and lateness | FINAL (data only) | log 5.6; `censored_trials.csv` |
| S7 | Primacy power: predicted pulse effect by timing and decay level; sensitivity curve | Partly FINAL (predicted effects); sensitivity PENDING | report 2026-10-22-primacy-power |
| S8 | Model-free pulse-timing regression; all-coherence robustness; secondary baseline (leak + urgency) | PENDING | primacy plan amendments 2–3 |
| S9 | Robustness: centre-of-screen ME, filter sensitivity | PENDING (step 7) | ME methods §5 |

Poster Figs 3B/4 used preprocessing's `pulse_type` (RT-dependent labels); Fig 5A must be redone with scheduled
labels. Fig 5A is descriptive; drawing it does not compare against model predictions, so it does not unblind the test,
but make it after gate 1's predictions are frozen to keep the order clean.

Poster Fig 5 (SC wide-field vertical cell inactivation) is out of scope (separate study).

---

## 3. Section-by-section outline

### Introduction (write after gate 1; draft background now)
Order follows the poster: primate RDK integration (Shadlen & Newsome 1996) → bounded accumulation (Kiani et al. 2008)
→ temporal weighting in primates (Kiani et al. 2008; Yates et al. 2017) → rodents (Odoemene et al. 2018) → the RT-task
caveat (Okazawa et al. 2018) → the strategy caveat (Stine et al. 2020): the usual signs of integration don't
establish it, and animals, which learn without instructions, are where this matters most. Then:
1. Why pulses: noise kernels need noise that varies over time; in standard RDKs it doesn't (R3), so timing and strategy
   have to come from injected pulses compared with model predictions made in advance.
2. Two rodent-specific obstacles this paper handles: fixed-per-trial stimulus noise, and many fast near-chance
   responses a plain DDM can't fit.
3. What we found (last paragraph; depends on outcome a/b/c).
Each claim to be checked against the cited paper.

### Results
- **R1 Task and behaviour** (Fig 1). 10 mice, 50 sessions, 25,508 responses within 5 s + 4,537 later or missing.
  Responses < 0.6 s: 12% UCLA / 21% UW of responses (mean of mice; Fig 1H), and at 100% coherence they are 58% correct
  vs 88% for slower ones (Fig 1G). Responses after 5 s are common (UCLA 16.5%, UW 13.3% of control trials) and are
  mostly real, coherence-dependent choices (S6). UW correct RTs depend little on coherence (Fig 1E). *(FINAL, from
  `fig1_behaviour.py`)*
- **R2 Motion energy** (Fig 2). Short; details in Methods. *(FINAL)*
- **R3 Hidden coherence** (Fig 3). SD at 0% 3.3% / 5.9%; k ≈ 0.50 (95% CI 0.15–0.90), positive in 8/10 mice
  (Wilcoxon p ≈ 0.02); 0.35–0.50 across versions, CI excludes 1 in all (log §3.3). Implication for kernels. *(FINAL)*
- **R4 A DDM for mouse RT behaviour** (Fig 4, S2–S6).
  - Measured Monte Carlo noise sets the threshold (per mouse SD 4–6 NLL at 50 reps; summed 13–21). *(FINAL)*
  - sv (9/10 mice) and fast guesses (7/10) pass; leak (4/10) and urgency (3/10) don't; sz doesn't help. Common model:
    sv + fast guesses (guess delay ≤ 0.3 s), chosen by the pre-agreed parsimony rule (decision 2026-10-22). *(FINAL)*
  - Leak/urgency gains are a difference between mice, not power: the other 7 mice pooled (12,307 trials) gain ~0; in
    PSUIM5/6/7 they mainly fit the flat share of > 5 s responses. Report as a cohort observation with the leak +
    urgency model as secondary baseline. *(FINAL; interpretation "delayed engagement" SUSPECTED, not modelled by
    choice)*
  - Fit quality, guess bias (free vs 0.5), recovery. *(PENDING)* Control-only check: the strict model holds
    (step 3.3: −sv +1,018, −guess +858, +leak −21, +urgency +26 summed held-out NLL; report 2026-10-23). *(FINAL)*
  - **Integration vs extrema detection on control trials** (Fig 4D; amendment 4). Wording rule until this is done:
    R4 says the data are *consistent with* bounded accumulation, never that they *show* it (Stine et al. 2020).
    Expect the comparison to be informative only in the mice with the most trials (their simulations needed ~1,000
    trials per stimulus strength; ours have ~50–800 per signed coherence). *(PENDING)*
  - Non-decision time is free in every fit; Stine et al. constrain it with a speeded block we don't have. State as a
    limitation; check whether RTs at 100% coherence bound it.
  - Known misfit to state, not hide: psychometric asymptotes imply 16–53% lapses at 100% coherence that the fitted
    lapse (≤ 1.5%) doesn't capture; high-coherence errors are probably absorbed by sv (SUSPECTED; check in fit-quality
    plots).
- **R5 Pulses** (Fig 5, S7–S8). Order fixed by the plan: predicted pulse effects of both models (S7, frozen) → gate 1
  → strategy test (amendment 4, item 5) → then branch (a1/a2), (b) or (c) from §1. Report every item in primacy plan §10 that is reached; anything outside the locked plan, including
  a model revision after a failed gate, labelled as such.

### Discussion
1. The main answer, by branch: (a1) mice detect rather than integrate, and what that means for rodent accumulation
   claims; (a2) why mice might over-weight brief strong pulses; (b) what the data can and can't say about timing, and
   what design would answer it; (c) primacy/recency and mechanism.
1b. Comparison with Stine et al. 2020: their constraints (separate signal-to-noise and non-decision-time estimates)
   vs ours (pulse predictions made in advance); which works for animals that can't be instructed.
2. Hidden coherence: consequences for kernel analyses in RDK tasks (needs citations; careful).
3. Fast guesses and lapses in mice; the gap between fitted and psychometric lapses.
4. Late responses and the cohort difference (PSUIM5/6/7): a delayed start of integration is a hypothesis, not tested.
5. Limitations: 10 mice in two cohorts, rig confounded with cohort; late pulses UW-only; UW floor rule approximate;
   UCLA replay not exact frame-by-frame; screen geometry not corrected; simulation-based likelihood with Monte Carlo
   noise; 5 s censoring is an analysis choice.

### Methods (largely writable now)
- **Animals, rigs, training:** MISSING (strain, sex, ages, housing, water restriction, ethics approvals for both sites,
  training stages, session/trial exclusion criteria from notebook 0.1).
- **Trial timeline:** the stimulus ran until a response (up to 60 s on UCLA; 5, 25 or 60 s on UW, `stimulus_duration`);
  analyses censor at 5 s. Withholding, reward and time-out durations differ by rig; values from the data columns are
  in `figure_captions.md` (Fig 1 notes), meanings to confirm.
- **Stimulus and task** per rig: log §6b; pulse timings from Fig 1C.
- **Trial labelling:** scheduled vs RT-relabelled pulse type, control definition (log §3.2, §4.1).
- **Motion energy:** ME methods §3 + log §2.2.
- **Hidden coherence analysis:** notebook 2.14 §5.
- **DDM:** model (log §4.2), outcome mapping and censoring (§4.3), censored QMLE (§4.4), optimizer and warm starts
  (§5.5), CV, Monte Carlo noise threshold and parsimony rules (§5.6; next steps), guess forms, recovery.
- **Pulse analysis:** primacy plan §3–9 and amendments 1–3, locking commit `aeb0a22`; gate pass rule
  `GATE_MIN_INSIDE = 0.8` (accepted 2026-10-22); blinding rule (`--unblind`).
- **Statistics:** mouse as unit for group claims; Bayesian GLMM (PyMC 5.25.1) priors.
- **Software and data/code availability:** MISSING.

### Supplement
Fitting pitfalls useful to others (empty-cell exploit, relative DE tolerance, urgency sign flip, under-optimized
nested fits; log §6.2, §5.5).

---

## 4. Writing order

1. **Now:** Methods (task, ME, hidden coherence, DDM likelihood/fitting/selection, pulse analysis plan); R1–R3 with
   Figs 1–3; R4's model-selection part with Fig 4B and S2, S4, S6. None of this depends on gate 1.
2. **After the final fast-only fits:** Fig 4C (fit quality), guess bias; then gate 1.
3. **After gate 1:** pick branch (a)/(b)/(c); R5, Fig 5, S7–S8; then Introduction, Discussion, Abstract, Title.
4. **After step 4 (recovery):** S3; trim R4 claims to what is recoverable.

---

## 5. Decisions and fixes for the authors

- [x] **Amendment 4 (integration vs extrema detection): adopted 2026-10-23** (primacy plan, amendment 4: leak
      20–200 /s, 3 SD and 6/10 mice rule, no snapshot model). Gate 1 waits for its fits and frozen predictions.
- [ ] Fig 1F / caption: "no response by 5 s" is wrong for most of these trials (60–100% per mouse are responses after
      5 s). Relabel as "P(RT > 5 s or no response)" and fix the caption. *(I can do this.)*
- [x] Primacy plan states that the poster's raw pulse effects were known before locking (in amendment 4).
- [ ] Before gate 1: is a design result (what pulse strength/duration would give power) wanted for branch (b)? It is
      a simulation with existing code (`primacy_sensitivity.py` with larger pulses), cheap to add now, and it is only
      credible if done before the gate.
- [ ] Target journal/format. MISSING.
- [ ] Author list, order, CRediT roles. Poster authors: Vaibhav Thakur, Carlos Garcia, Edgar Walker, Michele A. Basso;
      confirm.
- [ ] Funding statement (poster: NINDS UF1NS122040-01; Burroughs Wellcome Fund); confirm complete.
- [ ] Have these data appeared in an earlier paper/thesis? MISSING.
- [ ] Make the locked primacy plan public with a timestamp before unblinding (currently a local commit).
- [ ] ARRIVE 2.0 checklist alongside Methods.
- [x] SC WFV inactivation: excluded (2026-10-20).
- [x] Session count: 50 mouse-sessions (the poster's 26 was a counting bug).
- [x] Common model: strict, sv + fast guesses (2026-10-22).
- [x] Primacy power: run gate 1 first (2026-10-22).

## 6. References to verify

From project docs: Kiani, Hanks & Shadlen 2008; Adelson & Bergen 1985; Okazawa et al. 2018; Andermann et al. 2011;
Usher & McClelland 2001; Brunton et al. 2013; Nienborg & Cumming 2009. From the poster: Shadlen & Newsome 1996;
Yates et al. 2017; Odoemene et al. 2018; Marques et al. 2018. Confirm what each reports before citing.
Read 2026-10-23 (web page, via summary; figures and decision letter not seen): Stine GM, Zylberberg A, Ditterich J,
Shadlen MN (2020) Differentiating between integration and non-integration strategies in perceptual decision making.
eLife 9:e55365. Verify the extrema-detection definition and the sample-size result against the full text before
citing them.
Still needed: rodent RDK/accumulation tasks; primacy/recency; fast-guess and lapse models; urgency/collapsing bounds;
simulation-based likelihoods; sensitivity to transient/salient motion (branch a).

---

## Changes on 2026-10-23
- After reviewing Stine et al. 2020: new core question 5 (do mice integrate?), tested on control trials (Fig 4D) and
  out of sample on pulse trials (Fig 5C); branch (a) split into a1 (extrema detection) / a2 (pulse over-weighting);
  R4 wording rule ("consistent with"); non-decision time limitation; draft amendment 4; step 3.3 result added.

## Changes on 2026-10-22
- Core story: R4 updated to the chosen strict model; R5 reframed into three outcome branches after the power result;
  the "null with sensitivity bound" headline dropped as the main option (the bound would be "undetectable").
- Censored trials described as late responses (log 5.6), which also resolves the poster's "60 s" stimulus duration.
- Figure plan: Figs 1–2 drafted; Fig 4 contents fixed; Fig 5 restructured around gate 1; new S6 (late responses) and
  S7 (power); S numbering shifted.
- Decisions: session count and model choice closed; new items for Fig 1F, the poster-as-prior-knowledge note and a
  pre-gate design simulation.
