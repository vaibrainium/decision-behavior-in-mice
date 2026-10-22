# Paper plan: evidence integration over time in mice (RT motion task with pulses)

**Status:** living outline, not prose. Started 2026-10-20. Update it as plan steps finish.
**Sources:** [`mouse-ddm-analysis-log.md`](../reports/mouse-ddm-analysis-log.md) (log),
[`mouse-ddm-next-steps.md`](../reports/mouse-ddm-next-steps.md) (next steps),
[`primacy-analysis-plan.md`](../reports/primacy-analysis-plan.md) (primacy plan),
[`motion-energy-methods.md`](../reports/motion-energy-methods.md) (ME methods).

Status tags used below:
- **FINAL**: result done and documented; can be written up now.
- **PROVISIONAL**: result exists but depends on a plan step still running; write the methods, leave numbers as `[TBD]`.
- **PENDING**: not run yet.
- **MISSING**: information the authors must supply (nothing in the repo says it).

No number goes into prose unless it is tagged FINAL here, with its source.

---

## 1. Core story

**Question.** Do mice weight early motion evidence more than late evidence (primacy), once you account for the
reasons a reaction-time task makes late evidence matter less anyway?

**The argument, in order:**
1. Mice do a reaction-time random-dot motion task on two rigs (UCLA, 4 mice; UW, 6 mice), with brief ±100% coherence
   pulses at early, middle and (UW only) late times.
2. To know what evidence the mice actually saw, we replay every trial's stimulus and compute motion energy with
   filters tuned to mouse vision, calibrated per rig. *(method, FINAL)*
3. In standard RDKs the stimulus noise is a **fixed bias per trial** ("hidden coherence"), not fresh noise over time.
   Mice use it but discount it to about 0.35–0.50 of programmed coherence. Consequence: noise-based psychophysical
   kernels **cannot** show when evidence is weighted in these tasks. Timing questions need the pulses. *(FINAL; a
   useful methods point for the field in its own right)*
4. A motion-energy-driven DDM with censoring at 5 s, a 0.3 s response floor and a fast-guess/lapse component
   explains choices, RTs and no-response rates. Mechanisms supported: `[TBD after plan step 3; recommended: sv +
   fast guesses (L0U0V1Z0G1, fast_only)]`. *(PROVISIONAL)*
5. Primacy test, with the analysis fixed before the residuals were seen: are pulse effects at later times smaller than
   this model, fitted without pulse trials, predicts? Within each mouse, plus a model extension test, a model-free
   check and a sensitivity analysis. *(PENDING)*

**Framing (from the SfN 2025 poster, `SfN Poster - 2025.pdf`):** comparative. Mice learn the primate random-dot
task and use bounded evidence accumulation like primates; the paper asks whether temporal weighting is also shared.
This framing works with either primacy outcome.

**How the paper moves past the poster.** The poster's conclusions are the starting observations; the paper tests them
properly:
- *Poster:* early pulses shift the psychometric function most (Weibull alpha, z = −3.95), read as primacy.
  *Paper:* in an RT task that pattern is expected even with flat weighting (Okazawa et al. 2018, already on the
  poster's reference list), so it becomes the descriptive observation (Fig 1/5) that motivates the model-based test
  (R5). The paper must not repeat the poster's primacy claim before R5 is done.
- *Poster:* accuracy rises with RT and then plateaus, read as bounded accumulation. *Paper:* the DDM fits
  (choices, RT distributions, no-response rates, held-out comparison) are the evidence for bounded accumulation; the
  accuracy-vs-RT curve is a descriptive panel.
- *Poster:* pulse windows given as Early 0–160 / Middle 160–320 / Late 320–480 ms. *Paper:* use the scheduled onsets
  per rig (primacy plan §2: UCLA 61 / 241 ms; UW 50 / 233 / 417 ms).

**Headline claim:** written once step 6 is done. Draft both versions now so the outcome doesn't shape the framing:
- *If primacy:* "Mice weight early evidence more than a constant-weight accumulator predicts", plus which mechanism
  (gain decay vs self-excitation) fits better.
- *If null:* "Mice weight evidence about evenly over the first ~0.4 s; primacy larger than X is unlikely"
  (X from the sensitivity analysis). With the sensitivity bound, the null result is still informative.
- In both cases, points 3 and 4 hold on their own.

**Possible titles** (placeholders): "Mice integrate motion evidence [evenly / with primacy] in a reaction-time task";
"Hidden stimulus noise and the timing of evidence integration in mice"; in the poster's style, a title that states the
result, e.g. "Mice accumulate visual evidence like primates[, but weight it evenly over time]".

---

## 2. Figure plan

| Fig | Content | Status | Source / existing asset |
|---|---|---|---|
| 1 | Task and rigs: trial structure (adapt poster Fig 1 schematic: withholding, 0.3 s minimum viewing, lick report, reward/time-out), pulse timings per rig (redraw poster Fig 3A with the scheduled onsets), psychometric and chronometric functions per rig, accuracy vs RT (poster Fig 2B), no-response rate vs coherence | Data FINAL; figure to make | notebooks 1.0, 1.2; `poster/accuracy_vs_rt_control.svg`; poster Figs 1–3A |
| 2 | Motion energy: filters vs mouse V1 tuning, stimulus replay, ME linear in coherence on both rigs, pulse response (~116 ms filter delay), per-rig calibration | FINAL | log §2; ME methods §3; notebook 2.11 |
| 3 | Hidden coherence: fixed per-trial noise bias, it explains ME noise (r = 0.87 / 0.97), mice's weight on it (k ≈ 0.50) per mouse, robustness versions; raw vs residual kernel and why it can't resolve timing | FINAL | log §3.3; notebook 2.14 §1–5; `figures/psychophysical_kernel_raw_vs_residual.png`, `motion_energy_kernel_summary.svg` |
| 4 | DDM: schematic (ME input, bound, urgency, leak, censoring, floor, guess/lapse); held-out NLL change per mechanism per mouse; fit quality (psychometric, chronometric incl. error RTs, no-response) | PROVISIONAL (steps 1–3) | log §4–5; notebook 3.0; `figures/ddm_fit_quality_L1U1V1Z0G1.png` (provisional) |
| 5 | Primacy: observed vs predicted pulse effect by timing per mouse; GLMM posterior for β_middle (all mice) and β_late (UW); gain-decay / negative-leak comparison; sensitivity curve | PENDING (steps 5–6) | primacy plan §5–9 |
| S1 | Rig behaviour check (response floor, pulse frames) | FINAL | log §6b |
| S2 | Monte Carlo noise of the model comparison; warm-start/optimizer checks; where leak/urgency help (censored-trial rate) | Results FINAL (log 5.5–5.6); figure to make | `scripts/ddm/mc_noise.py`, `diagnose_leak_urgency.py`, `figures/leak_urgency_diagnosis_20261022.png` |
| S3 | Model and parameter recovery | PENDING (step 4) | `scripts/ddm/model_recovery.py` |
| S4 | Guess/lapse forms; fitted lapse vs psychometric lapse | Results FINAL (log 5.5; fast_only chosen); figure to make | `scripts/ddm/compare_guess_forms.py` |
| S5 | Control-only model selection (does selection depend on pulse trials?) | PENDING (step 3.3) | next steps step 3 |
| S6 | Model-free pulse-timing regression; all-coherence robustness; no-leak baseline | PENDING | primacy plan amendment 2, §3 |
| S7 | Robustness: centre-of-screen ME, filter sensitivity | PENDING (step 7) | ME methods §5 |

Poster Figs 3B and 4 (`poster/pulse_effect_on_psych/alpha/beta`, Weibull fits per pulse timing) are the raw pulse
effects. Proposal: keep the psychometric shifts as Fig 5A ("what the raw data show"), then 5B onward show observed vs
model-predicted effects. That way readers see why the raw pattern alone is not evidence of primacy. They must not be
presented as the primacy test. Alpha/beta panels can go to the supplement.

Poster Fig 5 (chemogenetic inactivation of SC wide-field vertical cells) is **out of scope** for this paper (§5).

---

## 3. Section-by-section outline

### Introduction (write after Fig 5 exists; draft the background paragraphs now)
Follows the poster's Background: primate RDK integration (Shadlen & Newsome 1996) → bounded accumulation (Kiani et al.
2008) → time dependence / early evidence weighted more in primates (Kiani et al. 2008; Yates et al. 2017) → rodent
evidence from other tasks (Odoemene et al. 2018) → then the RT-task caveat (Okazawa et al. 2018), which the poster cited
but did not apply. Each of these claims must be checked against the paper before it goes into prose.
1. Temporal weighting of evidence: primacy/recency/flat, and what it says about the integration mechanism.
2. Why reaction-time tasks complicate this: late evidence affects fewer decisions even with flat weights
   (Okazawa et al. 2018). So the right comparison is against a model's prediction.
3. Mice as a model for evidence accumulation; the gap this fills: `[literature search needed]`.
4. Two obstacles specific to rodent RDK work, which this paper addresses: (a) stimulus-noise kernels confound timing
   when noise is fixed per trial; (b) mouse behaviour includes many fast near-chance responses that a plain DDM can't fit.
5. What we did and found (one paragraph, last).

### Results
- **R1 Task and behaviour** (Fig 1). Cohort sizes, trial counts per mouse, psychometric/chronometric. Fast
  responses < 0.6 s are 17% (UCLA) / 20% (UW) of responses and near chance (log §5.3), which sets up the guess component.
- **R2 Motion energy** (Fig 2). Keep short in Results; details in Methods.
- **R3 Hidden coherence** (Fig 3). SD at 0% coherence 3.3% (UCLA) / 5.9% (UW); k ≈ 0.50 (95% CI 0.15–0.90), positive
  in 8/10 mice (Wilcoxon p ≈ 0.02); robustness range 0.35–0.50, CI excludes 1 in every version (log §3.3).
  Implication for kernels.
- **R4 A DDM for mouse RT behaviour** (Fig 4, S2–S5). Mechanisms, guess/lapse form, recovery. Numbers `[TBD]`.
  Common model not yet chosen (next-steps step 3; analysis log 5.5–5.6). How each choice changes the story:
  - *Path A (recommended), sv + fast guesses, flat bound, no leak:* R4 says "a bounded accumulator with drift
    variability and ~20% fast guesses at chance explains mouse RT behaviour". The primacy baseline weights evidence
    equally, i.e. it is the null hypothesis itself; gain decay and signed leak are one-parameter tests in R5, so any
    leak (recency) or self-excitation (primacy) appears there as a finding about temporal weighting. Leak + urgency
    help only PSUIM5/6/7 and mainly fit the coherence-independent share of > 5 s responses; report this in S2/S5 as a
    cohort difference, with the leak + urgency model as the secondary baseline. Reviewer risk: "baseline misfits the
    largest mice"; answered by the predictive-check gate and the secondary baseline.
  - *Path B, leak + urgency + sv + guesses:* richer R4 ("leaky accumulator with collapsing bound"), but those claims
    rest on 3–4 mice and a rule relaxed after seeing results; the primacy baseline already discounts early evidence,
    so flat weighting would look like primacy against it, and the signed-leak test only widens an existing parameter.
  - Either way, add a third headline draft (recency / leak) next to "primacy" and "null".
- **R5 Primacy test** (Fig 5, S6). Report every item in primacy plan §10, in that order, whatever the outcome:
  predictive-check gate, β_middle, per-mouse estimates, UW late pulses, rig interaction, both baselines, mechanism
  extensions, sensitivity. Label anything outside the locked plan as exploratory.

### Discussion
1. Main answer and how strong it is (sensitivity bound if null).
2. Gain decay vs self-excitation, if either wins; otherwise what the data rule out.
3. Hidden coherence: consequences for earlier rodent and primate RDK kernel analyses (careful, needs citations).
4. Fast guesses/lapses in mice: what they could be (anticipation, impulsive licking), and the lapse vs psychometric
   asymptote check.
5. Limitations: 10 mice in two cohorts with rig and cohort confounded (only within-mouse contrasts avoid it); late
   pulses UW-only (6 mice); UW floor rule is an approximation (next lick onset); UCLA frame-by-frame replay is not exact
   (loop-rate settings, log §6b); screen geometry not corrected (ME methods §3.7); DDM fitted by simulation with
   Monte Carlo noise.

### Methods (largely writable now)
- **Animals, rigs, training:** MISSING (strain, sex, ages, housing, water restriction, ethics approvals for both sites,
  training stages, session/trial exclusion criteria from notebook 0.1).
- **Trial timeline** (from poster Fig 1, to verify against rig configs): 0.5 s response withholding before the stimulus,
  0.3 s minimum viewing, choice by lick, reward 0.5 s then ITI, time-out 1 s after errors. The poster's stimulus
  duration label ("60s") conflicts with the 5 s deadline used in the DDM (log §4.3); check which is correct and
  whether it differs by rig.
- **Stimulus and task** per rig: from log §6b and rig code (UW NeuRPi, UCLA RDK-Task). Pulse timings from primacy plan §2.
- **Trial labelling:** scheduled vs RT-relabelled pulse type, control definition (log §3.2, §4.1). Write carefully;
  this has caused errors before.
- **Motion energy:** ME methods §3 + log §2.2. Filter parameters, causal filtering, calibration slopes.
- **Hidden coherence analysis:** notebook 2.14 §5.
- **DDM:** model (log §4.2), outcome mapping (§4.3), censored QMLE likelihood (§4.4), optimizer and warm starts (§5.5),
  cross-validation, Monte Carlo noise threshold, family-level model comparison (protected exceedance), recovery.
- **Primacy analysis:** primacy plan §3–9 and amendments, with the locking commit `aeb0a22`.
- **Statistics:** mouse as unit for group claims; Bayesian GLMM priors; corrections.
- **Software and data/code availability:** MISSING (versions from `uv.lock`; repository/DOI decisions).

### Supplement
Fitting pitfalls that would affect others (empty-cell exploit, relative DE tolerance, urgency sign flip; log §6.2).
A short "lessons" section here could be useful to readers fitting similar models.

---

## 4. Writing order

1. **Now:** Methods (task, ME, hidden coherence, DDM likelihood/fitting, primacy plan) and Results R1–R3 with Figs 1–3.
   None of this depends on running fits.
2. **After steps 1–3 (common model):** R4 + Fig 4, S2, S4, S5.
3. **After step 4:** S3; adjust R4 claims to what is recoverable.
4. **After steps 5–6:** R5, Fig 5, then Introduction framing, Discussion, Abstract, Title (last).

---

## 5. Decisions for the authors (open)

- [ ] Target journal/format (sets length, figure count, Methods placement). MISSING.
- [ ] Author list, order, CRediT roles, both labs' contributions (who collected the UCLA vs UW data). Poster authors:
      Vaibhav Thakur, Carlos Garcia, Edgar Walker, Michele A. Basso (UW Neurobiology & Biophysics); confirm for the paper.
- [ ] Funding statement. Poster lists NINDS UF1NS122040-01 and Burroughs Wellcome Fund; confirm it is complete.
- [x] SC wide-field vertical cell inactivation (poster Fig 5): **excluded** (decided 2026-10-20 by V. Thakur; a
      different study, not written up yet).
- [ ] Session count: the poster says 25,508 trials from 26 sessions across 10 mice; the analysis log mentions 219 UW
      session configs. The 25,508 trial count matches the log (§2.2). Find out what "26 sessions" counted before using
      either number.
- [ ] Have the UCLA (or UW) behavioural data appeared in an earlier paper/thesis? Affects framing and self-citation. MISSING.
- [ ] One paper or two? (Hidden coherence + ME method could be a short standalone methods paper; default here: one paper.)
- [ ] Make the locked primacy plan public with a timestamp (e.g. OSF, or a public commit) before the primacy test runs,
      so "fixed before seeing the residuals" can be checked by readers. Right now it is only a local git commit.
- [ ] Reporting guideline: ARRIVE 2.0 (animal study) applies; fill its checklist alongside Methods.
- [ ] Preprint (bioRxiv) timing.

## 6. References to verify

Cited in the project docs (verify each against the paper before use): Kiani, Hanks & Shadlen 2008; Adelson & Bergen
1985; Okazawa et al. 2018; Andermann et al. 2011; Usher & McClelland 2001; Brunton et al. 2013; Nienborg & Cumming 2009.
Also on the SfN 2025 poster: Shadlen & Newsome 1996 (J Neurosci 16:1486); Yates et al. 2017 (Nat Neurosci 20:1285);
Odoemene et al. 2018 (J Neurosci 38:10143); Marques et al. 2018 (Curr Biol 28:1703). Confirm what each actually
reports about temporal weighting before citing it for that point.
Still needed, by topic: mouse/rodent RDK and evidence-accumulation tasks; primacy/recency in perceptual decisions;
fast guess / lapse models; urgency and collapsing bounds; simulation-based likelihoods (quantile MLE).
