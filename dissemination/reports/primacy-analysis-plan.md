# Primacy test: analysis plan (written before looking at pulse residuals)

**Status: LOCKED** (2026-10-20, agreed with V. Thakur; locking commit recorded in
[`mouse-ddm-next-steps.md`](mouse-ddm-next-steps.md), step 6.1). This version is the confirmatory analysis; change it
only by a new, dated commit that says why. Anything decided after looking at pulse-trial residuals is reported as
exploratory.
Context: plan step 6 in [`mouse-ddm-next-steps.md`](mouse-ddm-next-steps.md); model and data in
[`mouse-ddm-analysis-log.md`](mouse-ddm-analysis-log.md).

Decisions taken when locking are listed in section 11.

---

## 1. Question and hypotheses

Do mice weight motion evidence early in a trial more than a constant-weight bounded accumulator predicts?

In a reaction-time task, a later pulse affects fewer choices even with constant weights, because some trials have
already ended or are within the non-decision time when it arrives (Okazawa et al. 2018). The test therefore compares
each pulse's observed effect with the effect predicted by a model fitted to control trials only, which already contains
that reduction.

- **H1 (primacy):** within mice, the observed effect of a pulse on choice, relative to the model's prediction, is
  smaller for later pulses.
- **H0:** observed-minus-predicted pulse effects do not differ between pulse timings.
- Recency (larger relative effects for later pulses) is the other possible departure; the test is two-sided.

## 2. Design facts the plan relies on

| | UCLA (4 mice) | UW (6 mice) |
|---|---|---|
| Early pulse onset | 61 ms (SD 15, drawn per trial) | 50 ms (frame 3) |
| Middle pulse onset | 241 ms (SD 15) | 233 ms (frame 14) |
| Late pulse onset | none | 417 ms (frame 25) |
| Pulse | ±100% coherence, ~50 ms | ±100% coherence, 67 ms |
| Scheduled pulse trials per mouse, early / middle | 94–1,482 | 98–706 |
| Late pulse trials per mouse | — | 165–798 |

Early and middle onsets are nearly the same on both rigs, so all 10 mice contribute to the early-vs-middle contrast.
Late pulses exist only on UW.

## 3. Model whose predictions are used

- **Primary baseline:** the common model chosen in plan step 3, fitted per mouse to control trials only (no scheduled
  pulse) with the final settings of step 5 (50 simulation repetitions, warm starts).
- **Secondary baseline:** the same model without leak (step 5), because leak itself shapes temporal weighting (it
  discounts early evidence).
- Predictions are simulated for each pulse trial from its own motion energy (pulse included), with the same outcome
  rules as the fits (censoring at 5 s, 0.3 s floor) and the trial's scheduled pulse; ≥ 200 simulated repetitions per
  trial so prediction noise is negligible against trial-level noise.

## 4. Trials

- All trials with a scheduled pulse (`sched_pulse_type` ≠ 0), labelled by scheduled timing and pulse direction,
  **regardless of RT** (including responses before or during the pulse): the model predictions apply the same RT
  dynamics, so the comparison stays fair, and selecting on RT would reintroduce the outcome-dependent grouping that
  preprocessing's `pulse_type` has.
- Choice outcomes use trials with a response (0.3–5 s); trials with no response by 5 s are excluded from the choice
  measure (their share is checked in the predictive check).
- Coherence range: **|coherence| ≤ 36%** (choices not saturated, so a pulse can move them) for the primary analysis;
  all coherences as a robustness check.
- The 15 trials with invalid pulse durations are already excluded from the DDM inputs.

## 5. Outcome

For trial *i*, let *y_i* = 1 if the choice was in the pulse direction, and *p̂_i* the model's predicted probability of
a choice in the pulse direction for that trial (among simulated responses).

- **Primary outcome:** the trial-level residual on the logit scale, via a mixed-effects logistic regression of *y_i*
  with offset logit(*p̂_i*) (section 6). The coefficients then measure departures from the model's prediction.
- **Secondary outcome:** RT residuals (observed minus predicted mean RT) by timing.

## 6. Statistical model

Binomial generalized linear mixed model:

    logit P(y_i = 1) = logit(p̂_i) + β0 + β_timing[timing_i] + β_rig · rig_i + u_mouse + v_mouse · timing_i

- `timing` coded with early as reference; random intercept and timing slope per mouse (mouse is the unit of
  replication); `rig` as a fixed covariate.
- **Primary test (all 10 mice):** β_middle (middle vs early). H1 predicts β_middle < 0. Two-sided, α = 0.05.
- **Secondary test (UW only, 6 mice):** β_late vs early, and the trend early → middle → late, fitted on UW mice only;
  reported as secondary and not pooled with UCLA.
- **Rig:** the timing × rig interaction is reported descriptively (two cohorts of 4 and 6 mice cannot show
  replication; a null is "no evidence of a difference").
- Fitting tool: **Bayesian GLMM** (`pymc`, weakly informative priors: Normal(0, 1) on the logit-scale fixed effects,
  half-Normal(0, 1) on random-effect SDs); report the posterior of β_middle, its 95% interval and P(β_middle < 0). The
  primary test is "the 95% interval of β_middle excludes 0". Chosen because 10 mice make random-slope variances unstable
  in frequentist fits.
- **Per-mouse estimates** of the timing effect are shown alongside the group estimate.

## 7. Gate: predictive check before the timing test (plan step 6.2)

Done first, and does not involve the timing contrast:
1. β0 (overall departure, all timings pooled) is reported; the model passes if the 95% interval of the pooled pulse
   effect contains the model's prediction, or the departure is < 25% of the predicted pulse effect.
2. Pulse-trial RT distributions (quantiles, pooled over timing) are within the spread of the model's predictions.
3. The fraction of no-response-by-5 s trials on pulse trials matches the prediction.

If the check fails, the model is revised (and the revision documented) before the timing test; the timing test is not
run on a model that fails the gate.

## 8. Model-based test (plan step 6.5)

In parallel, the common model is extended with a time-varying evidence weight (drift gain multiplied by
exp(−t / τ_w), with 1/τ_w free and allowed to be negative for recency) and fitted to all trials (the pulses carry the
timing information). It is compared with the common model by the same 5-fold cross-validation as the model comparison.
Primacy is supported if the extension improves held-out fit beyond the Monte Carlo noise threshold (step 3.1) in most
mice and 1/τ_w > 0.

## 9. Sensitivity (plan step 6.6)

Simulate each mouse's real trials from its fitted control-only model with added primacy: drift gain decaying by 10%,
20% and 40% over the first 0.5 s (≥ 20 simulated datasets per level). Run sections 5–6 unchanged on each. Report the
smallest decay detected in ≥ 80% of datasets; if the real result is null, report "a decay larger than X over 0.5 s is
unlikely".

## 10. Reported regardless of outcome

- Predictive-check results (section 7), including failures and revisions.
- β_middle with interval, per-mouse estimates, the UW late-pulse result, the rig interaction, both baselines.
- The model-based test (section 8) and the sensitivity result (section 9).
- Any deviation from this plan, labelled exploratory.

## 11. Decisions taken when locking

1. Coherence range: |coherence| ≤ 36% primary; all coherences as a robustness check (section 4).
2. Bayesian GLMM with the priors above; primary test is the 95% interval of β_middle (section 6).
3. Predictive-check threshold: 95% interval contains the prediction, or departure < 25% of the predicted effect
   (section 7).

---

## Amendment 1 (2026-10-20, before any pulse residuals were examined)

**Change:** section 8 tests a second primacy mechanism alongside the time-varying evidence weight: a **self-exciting
accumulator** (negative leak, `leak_rate` down to −1/s; `fit_mouse_ddm.py --signed_leak`).

**Why:** urgency and the bound change *when* decisions end, not the relative weight of early and late evidence, and the
fitted leak is restricted to ≥ 0 (recency only). Two standard accounts produce primacy: a gain that declines over time
(`gain_decay`, already in section 8) and a self-exciting accumulator (Usher & McClelland 2001; Brunton et al. 2013).
They make different predictions: gain decay depends only on time, while self-excitation depends on the accumulated
evidence (primacy strongest when early evidence was strong). Testing both avoids attributing primacy to one mechanism
by default.

**Procedure:** as section 8, for each mechanism separately and together: the common model with `--time_varying_gain`,
with `--signed_leak`, and with both, fitted to all trials and compared with the common model by the same 5-fold
cross-validation. Primacy is supported if either extension improves held-out fit beyond the Monte Carlo noise threshold
in most mice with gain_decay > 0 or leak_rate < 0. Sections 1–7 and 9 are unchanged.

---

## Amendment 2 (2026-10-20, before any pulse residuals were examined)

**Changes:**
1. **Section 8 / amendment 1, one mechanism at a time.** Gain decay (`--time_varying_gain`) and negative leak
   (`--signed_leak`) are each added separately to the common model (one extra parameter each) and compared with it by
   cross-validation. The combined variant is dropped. Neither extension becomes part of the reported model unless it
   passes the complexity budget (next-steps plan, parsimony rule 2): better held-out fit beyond the Monte Carlo noise
   threshold in most mice, recoverable, interpretable.
2. **Supplementary model-free check.** Mixed-effects logistic regression on pulse trials with |coherence| ≤ 36%:
   choice toward the pulse direction ~ signed coherence (aligned to the pulse direction) + timing, random intercept and
   timing slope per mouse, rig as a covariate; Bayesian, priors as section 6. Restricted to trials with RT ≥ pulse onset
   + 0.5 s, the same window for every timing, so each pulse could influence the choice. This conditions on RT and is
   reported as a supplementary consistency check, not the confirmatory test: if it agrees with section 6 the conclusion
   does not hinge on the DDM; a disagreement is reported and discussed.

**Why:** to keep the reported model as simple as the data justify (each added mechanism must earn its place), and to
make sure the primacy conclusion does not depend only on DDM assumptions.

---

## Amendment 3 (2026-10-22, before any pulse residuals were examined)

**Context:** the common model was chosen in next-steps step 3 (analysis log, section 5.6): **L0U0V1Z0G1 with fast-only
guesses** (sv + fast guesses, guess delay ≤ 0.3 s; no leak, no urgency, no sz). It was chosen by parsimony rule 2:
leak and urgency improve held-out fit beyond Monte Carlo noise in only 4 and 3 of 10 mice. Pooled over the other mice
they give no improvement, and where they help (PSUIM5/6/7) they mainly fit the share of responses after 5 s rather
than the timing of evidence weighting. Decided by V. Thakur, 2026-10-22.

**Changes:**
1. **Section 3, baselines.** Primary baseline: L0U0V1Z0G1 (fast-only guesses), fitted per mouse to control trials only,
   with the final settings of step 5. It weights evidence equally over time, so it is the constant-weight model of H0.
   **Secondary baseline: L1U1V1Z0G1 (leak + urgency, fast-only guesses)**, fitted the same way, replacing "the same
   model without leak", which would now be identical to the primary. The secondary baseline is reported alongside the
   primary for every result in section 10. Both must pass the section 7 gate; the confirmatory test uses the primary.
2. **Section 8 and amendments 1–2, extensions.** Each extension adds one parameter to L0U0V1Z0G1:
   - gain decay (`--time_varying_gain`, variant L0U0V1Z0G1);
   - signed leak (`--signed_leak`, variant L1U0V1Z0G1, leak_rate from −1 to 5 /s).

   Because the common model has no leak, the signed-leak extension tests both directions. Primacy is supported by
   gain_decay > 0 or leak_rate < 0, recency by gain_decay < 0 or leak_rate > 0. Each requires better held-out fit than
   L0U0V1Z0G1 beyond the Monte Carlo noise threshold in most mice (parsimony rule 2), as before.
3. **Guess bias.** If the planned comparison (next-steps step 2) shows that a free guess_bias does not clearly improve
   held-out fit, guess_bias is fixed at 0.5 in both baselines and all extensions. This is decided before the primacy
   test and recorded in the analysis log.

**Unchanged:**
- Sections 1–2, 4–7 and 9–11.
- The step 3.3 control-only check of the model choice, which is still to be run before the final fits.

**Why:** the plan named its baselines relative to a provisional common model that included leak. The chosen model has
no leak, so the "without leak" contrast no longer exists. The alternative most likely to change the predicted pulse
effects is the leak + urgency model, which fits the long-RT behaviour of PSUIM5/6/7 better.

---

## Amendment 4 (2026-10-23, before any pulse residuals were examined): integration vs extrema detection

**Adopted by V. Thakur, 2026-10-23.** Gate 1 (section 7) had not been run: no `ddm/primacy` output existed and no
recorded pulse-trial outcome had been read when this amendment was committed.

**Prior knowledge, stated for the record.** The raw pulse effects shown on the SfN 2025 poster (psychometric shifts by
pulse timing, trials grouped by preprocessing's RT-dependent `pulse_type`) were known when this plan was locked
(2026-10-20) and when this amendment was written. No model-based comparison of pulse trials had been made.

**Why.** The plan assumes the mice integrate evidence. Stine, Zylberberg, Ditterich & Shadlen (2020, eLife 9:e55365)
showed that the usual signs of integration (sigmoid psychometric functions, accuracy rising with viewing time, good
DDM fits, flat kernels) are also produced by strategies that do not integrate, notably extrema detection, and that an
integration model can fit such data well when signal-to-noise and non-decision time are free, as in our fits. The two
strategies should predict different effects of a brief ±100% pulse (to be computed, item 4), which our design can test
out of sample. Without this amendment a failed gate would show only that the integrator is wrong.

**Changes:**
1. **Extrema-detection model (E).** The common model (L0U0V1Z0G1, fast-only guesses, guess bias as decided under
   amendment 3) with a fast-forgetting accumulator: variant L1U0V1Z0G1 with leak_rate free in **[20, 200] /s**
   (time constant 5–50 ms); all other parameters and bounds as in the common model. The decision variable then tracks
   the motion energy of roughly the last 5–50 ms (on top of the ~100 ms in the motion-energy filters), so a bound
   crossing is a threshold crossing by momentary evidence: a continuous-time analogue of Stine et al.'s extrema
   detection, not their discrete-sample rule. `fit_mouse_ddm.py --leak_bounds 20 200`; `primacy.py --baselines
   extrema`. Implementation note: with the common model's lower bound a ≥ 0.3, the threshold at leak 200 /s is at
   least ~3 SD of the stationary noise; fitted leak rates at the upper limit are reported as such.
2. **Integration-time model (descriptive).** The same model with leak_rate free over [0, 200] /s, fitted to all
   control trials per mouse; its leak is reported as an estimated integration time constant. Not used for any test.
3. **Control-trial comparison (before gate 1).** E and the common model, fitted per mouse to the control-only CV
   splits (ccv0–ccv4) and to all control trials. Held-out NLL per mouse and summed, against the Monte Carlo noise
   threshold (analysis log 5.6). Reported as is; it gates nothing.
4. **Frozen pulse predictions (before gate 1).** From each mouse's control-only E fit, pulse-trial predictions with
   `primacy.py` exactly as for the baselines (≥ 200 repetitions, same trials and outcome rules), saved, with the commit
   hash, before any pulse-trial outcome is read.
5. **Pulse test of strategy (after gate 1; confirmatory).** For each mouse, the log-likelihood of the observed
   pulse-trial choices (section 4 trial set: |coherence| ≤ 36%, responded trials) under each model's frozen per-trial
   predictions. Statistic: the summed difference over mice, E minus common model, against its Monte Carlo SD from the
   prediction repetitions; per-mouse differences shown alongside. Neither model is fitted to pulse trials. **Decision
   rule:** a model is favoured if the summed difference exceeds 3 Monte Carlo SDs in its favour and has the same sign
   in at least 6 of 10 mice; otherwise "not distinguished".
6. **Timing pattern under each model.** The predicted pulse effect by timing (early / middle / late) under E and the
   common model is reported next to the observed effects, descriptively. If E is favoured in item 5, the section 6
   timing test is interpreted against E's prediction: a timing pattern that E predicts is not evidence of primacy in
   evidence weighting.

**Not added:** the snapshot model (a single sample at a random time), which fits a free-response task poorly.

**Unchanged:** sections 1–11 and amendments 1–3. Gate 1 and the primary test are as before; this amendment adds a
comparison, and gate 1 waits until items 3–4 are done.

---

## Amendment 5 (2026-10-23, before any pulse residuals were examined): the strategy test statistic and E's gain bound

**Adopted by V. Thakur, 2026-10-23.**

**Context:** a review of amendment 4 before any extrema-detection (E) fit or prediction existed. Gate 1 has not been
run; no `ddm/primacy` output exists; no recorded pulse-trial outcome has been read.

**Changes to amendment 4:**
1. **Item 5, the statistic is pulse-specific.** For each responded pulse trial in the section 4 set and each model,
   the per-trial log-likelihood of the observed choice under the model's frozen prediction with the pulse (p̂) and
   without it (p̂ for the same trial with the pulse removed, as in gate 1). The **primary statistic** is the paired
   difference in the log-likelihood each model's predicted pulse effect gains, [ll(p̂_E) − ll(p̂0_E)] − [ll(p̂_C) −
   ll(p̂0_C)], summed over trials and mice. It isolates the pulse effect from how well each model predicts choices in
   general (already compared in item 3). **Secondary:** the paired difference of total log-likelihood, ll(p̂_E) −
   ll(p̂_C), as in amendment 4.
2. **Item 5, the SD is the sampling SD.** The SD of each sum is the paired per-trial SD (variance of the per-trial
   differences across trials × number of trials, summed over mice; a Vuong-type SD). It replaces "the Monte Carlo SD
   from the prediction repetitions", which measured only simulation noise and is far smaller than trial-sampling
   variability, so almost any difference would have passed. Each trial's prediction noise is part of the per-trial
   spread and is not added separately. Thresholds unchanged: a model is favoured if the sum exceeds 3 SDs in its
   favour and the per-mouse sums have that sign in at least 6 of 10 mice; otherwise "not distinguished".
   Calibration (synthetic, 3 mice, a model against itself with independent predictions, 150 datasets): z SD 1.01
   (pulse gain) and 0.97 (total); 0/150 beyond 3 SD (`primacy.strategy_test`; check in the analysis log 8.4d).
3. **E's drift-gain bound.** With leak λ, E's steady-state signal is drift_gain × motion energy / λ, so the common
   model's upper bound drift_gain ≤ 20 can cap E's signal-to-noise and make E lose by construction. Rule, decided
   now from E's control-trial fits only: if drift_gain is within 1% of 20 in any mouse's all-control fit, or in more
   than 10% of its control-only CV fits, E is refitted for all mice and splits with drift_gain ≤ 200
   (`fit_mouse_ddm.py --drift_gain_max 200`), and the refits are used for items 3–5. Both are reported.
4. **Power of item 5 before unblinding.** Once E is fitted, simulate pulse-trial datasets from each mouse's E fit and
   from its common-model fit (≥ 20 each) and run item 5 on them. Report how often it favours the generating model.
   If it rarely does, item 5 is reported as underpowered, whatever its outcome.

**Corrections to amendment 4's implementation note:**
- The decision threshold at leak 200/s is at least ~3 SD of the stationary noise only for an unbiased start (z = 0.5).
  At z = 0.2 the nearer bound is ~1.1 SD away.
- The simulator applies leak as e[t] = (1 − λ·dt) e[t−1] + …, dt = 1 ms. At λ = 200/s the equivalent continuous rate
  is ~223/s and the stationary variance ~11% higher (≤ 1% at 20/s). Fitted leak rates and the descriptive time
  constants (item 2) are reported on the model's discrete-time scale, with this caveat.

**Unchanged:** amendment 4's items 1–4 and 6, its thresholds, and the order (E fits and frozen predictions before
gate 1).

---

## Amendment 6 (2026-10-23): pulse gain, a model revision prompted by the failed predictive check

**Adopted by V. Thakur, 2026-10-23, with the corrections in this text.** This is a **model revision prompted by the
failed predictive check**, specified before any timing contrast was examined. It is a bounded follow-up. It does not
restore the original, untouched confirmatory status of the timing test: the decision to revise was made after seeing
the gate fail, and results from it are reported as such.

**The original result stands and is reported prominently.** Gate 1 (section 7), run on the 15-rep control-only fits,
failed for both baselines: pooled departure +0.30 logit (95% CI 0.18–0.41) against a predicted pulse effect of 0.03;
RT-quantile check 68% inside (analysis log 5.10). So the pre-specified models do not predict pulse-trial behaviour,
and under the original plan the timing test is not run on them. Only pooled, timing-agnostic quantities were examined
(by pulse direction relative to coherence, and by mouse). The section 6 timing contrast has not been computed.

**Why.** Mice respond to the ±100% pulses more than their motion energy predicts under a model fitted to control
trials, and by an amount that differs between mice. At 0% coherence the pooled share of choices in the pulse direction
is 0.574 observed vs 0.508 predicted (n = 1,388); per mouse up to ~12 percentage points above the prediction. Neither
the integrator nor extrema detection predicts this (0.03 and 0.04 logit). The primacy question is whether pulse
weight depends on timing. It can still be asked against a model whose overall pulse weight is fitted, provided the
test's behaviour is shown by calibration (item 6), not assumed.

**Changes:**
1. **Revised baselines.** Each baseline (primary L0U0V1Z0G1, secondary L1U1V1Z0G1; fast-only guesses, guess bias free)
   gains one parameter per mouse, the **pulse gain** w_p ∈ [0, 50]. The input is the trial's no-pulse motion energy
   plus w_p times its pulse component: coherence × onset response + w_p × (pulse change × pulse response) + N, using
   the `build_ddm_inputs.py` decomposition; w_p = 1 is the current model.
   - w_p is the same at every timing, so the model has no explicit timing preference. It can still change the
     predicted timing pattern, because a stronger pulse changes bound-crossing times and so which decisions are
     still open when later pulses arrive. That is acceptable: the timing test asks whether the observations depart
     from the revised model's own prediction, whatever pattern it implies.
   - All other parameters stay at the mouse's control-only fit (plan step 5, final settings); only w_p is fitted.
   - w_p also absorbs any mismatch between the replayed and displayed pulse. On one rig the replay's one-frame freeze
     makes the pulse energy ~25–35% too small (analysis log 5.10). So w_p is not a pure behavioural weight and is
     interpreted relative to 1 with that caveat.
2. **Fitting w_p by cross-validation over pulse trials.**
   - **Folds:** 5 per mouse, stratified by `condition` (coherence × scheduled pulse type).
   - **Fit:** for each fold, w_p is fitted to the other 4 folds' pulse trials with the censored QMLE likelihood
     (choices, RTs and censoring), at 50 repetitions with common random numbers, by bounded one-dimensional
     minimisation. This likelihood uses trials from all timings, including the timing-specific conditions.
   - **What this guarantees:** no timing-specific gain is fitted, and each trial's prediction uses a gain estimated
     without that trial (≥ 200 repetitions from its fold's w_p). Cross-validation prevents direct own-trial fitting.
     It does not make the revision independent of the observed failure, and the overlapping training folds introduce
     dependence between folds that the calibration (item 6) checks.
   - **Reporting:** w_p fitted to all pulse trials, with a profile-likelihood interval, per mouse.
3. **Gate for the revised baselines** (section 7, applied to the out-of-fold predictions):
   - gate 1: the pooled departure must have a 95% interval containing 0, or be smaller than 25% of the predicted
     pulse effect;
   - gates 2–3 as before (GATE_MIN_INSIDE = 0.8);
   - descriptive calibration checks, observed vs predicted by coherence and by mouse, are reported alongside.

   If the revised primary baseline fails, the timing test is not run. The outcome is then the gate result plus the
   w_p estimates.
4. **Timing test** (sections 5–6, unchanged in form): offsets logit(p̂) from the out-of-fold predictions of the
   revised baselines. Primary: β_middle, all mice, rig as a covariate. Secondary: UW-only late pulses and trend. Both
   baselines reported.
5. **Extensions** (section 8, amendments 1–2): gain decay and signed leak are fitted to all trials with w_p free as
   well, and compared with the revised common model by the same cross-validation.
6. **Calibration and power, before the timing test** (replaces section 9 for the revised analysis).
   - **Data:** synthetic data from each mouse's revised model (its control fit and w_p), with the drift gain
     decaying by 0% (null), 10%, 20% and 40% over 0.5 s, ≥ 20 datasets per level.
   - **Pipeline:** each dataset goes through the whole revised pipeline: cross-validated w_p fitting, out-of-fold
     predictions, the gate, and the timing test.
   - **Report:**
     - how often the gate passes, per level;
     - the false-positive rate of the timing test under zero primacy;
     - detection rates under known primacy, both conditional on passing the gate and across all simulated datasets.
   - **What it checks:** the test's validity (null calibration), the dependence from overlapping folds, and whether
     the gain fitting absorbs part of a timing departure.
   - **No claim about power is made in advance.** Stronger pulse sensitivity may help, but fitting w_p may absorb
     part of a timing effect; only this simulation establishes the net result.
   - The timing test is run only after this has been reported.
7. **Order:**
   1. step 5 final control-only fits (50 reps; step 5 had not been run when gate 1 was computed, which used the
      15-rep fits);
   2. w_p cross-validated fits and out-of-fold predictions;
   3. gate;
   4. calibration and power (item 6);
   5. timing test.
8. **No further model expansion for this question.** If the revised gate fails, or the calibration shows the timing
   test is invalid or underpowered, the primacy result is reported as such: the gate failures, the w_p estimates,
   and the calibration. No further baseline revision is made for the primacy test.

**Not changed:** the strategy test (amendments 4–5) stays as run (not distinguished, underpowered), and E's
predictions stay frozen. The too-shallow control-trial psychometric fit at 18–36% coherence in some mice is not
addressed. Balancing pulse direction against coherence reduces this concern, but cancellation is not established
under nonlinear predictions, censoring and heterogeneous mice; the descriptive checks by coherence and mouse (item 3)
are kept.

---

## Closing note (2026-10-23): primacy analysis stopped under amendment 6, item 8

**Decided by V. Thakur, 2026-10-23.**

**Outcome.**
- The pre-specified baselines failed the predictive check (gate 1: departure +0.30 logit, 95% CI 0.18–0.41, against a
  predicted pulse effect of 0.03).
- The amendment 6 revision (cross-validated per-mouse pulse gain) also failed (+0.24, 0.09–0.37, primary baseline).
- Its calibration showed the procedure valid under the null (gate passes 95%, 0/20 false positives) but with
  essentially no sensitivity: primacy detected in 0–5% of datasets at 10–40% drift-gain decay over 0.5 s.
- Under the agreed stopping rule (amendment 6, item 8), the primacy analysis ends here. The section 6 timing test is not
  run, and no further baseline revision is made. Analysis log 5.10–5.11; report `.agents/reports/2026-10-23-amendment-6-result.md`.

**Not run, and why:**
- **Mechanism extensions** (section 8, amendments 1–2, amendment 6 item 5: gain decay, signed leak). They were tests of
  temporal weighting against a baseline that predicts pulse trials. The baseline failed predictive adequacy, before and
  after revision, and the revised procedure had low sensitivity to primacy. A cross-validated comparison would mostly
  reflect the unexplained pulse misfit, not temporal weighting.
- **Model-free timing check** (amendment 2): deferred for the current draft, optional.
  - It cannot resolve the failed model-based question. Conditioning on RT ≥ pulse onset + 0.5 s selects different
    subsets of trials at different timings.
  - Its sensitivity cannot be inferred from the DDM test's calibration.
  - If run for completeness, it is run exactly as specified in amendment 2 and reported descriptively, whatever the
    outcome.

**Reported** (section 10, as applicable): both gate failures, the per-mouse pulse gains, the descriptive calibration by
coherence and mouse, the strategy test (not distinguished, underpowered), and the calibration of the revised
procedure.

---

## Amendment 7 (2026-10-25, DRAFT for V. Thakur's decision): a visual front end with normalization

**Status: adopted by V. Thakur, 2026-10-25** (draft committed ddb51ba). This is a new decision by the authors after the stopping decision of
amendment 6, item 8 ("no further baseline revision for the primacy test"), and would override that item for this one
round only. **Everything in it is exploratory and post hoc.** The candidates below were chosen after seeing the
timing-agnostic pulse diagnostics (pooled departure, departure by pulse direction relative to coherence and by mouse;
analysis log 5.10–5.11). The original and revised gate failures stay the primary results and are reported first. No
timing contrast has been computed on recorded data when this draft is written.

**Why.** Every decision model tried so far reads linear opponent motion energy (Adelson–Bergen: linear filters,
squaring, opponency). Under that front end no fitted model predicts the pulse trials, and the misfit has a pattern:
- **at 0% coherence**, choices follow a 100% pulse far more than predicted (0.574 vs 0.512);
- **against 36% coherence**, a pulse has less effect than predicted;
- **on control trials**, the psychometric fit is too shallow at 18–36% in several mice.

Two standard visual nonlinearities predict such effects:
- **a static response nonlinearity:** strong signals weighted more than proportionally;
- **divisive normalization with adaptation** (normalization models of V1/MT; references to be verified before
  citing): sustained motion adapts, so a brief transient escapes adaptation and acts more strongly, and strong
  ongoing motion raises the normalization pool, which suppresses an opposite pulse.

If the decision process reads a normalized signal, the pulse failure says something about the visual representation,
not that integration is wrong. This amendment asks whether a front end fitted on control trials only predicts the
pulse trials out of sample. If it does, it revisits the strategy and timing questions with that front end.

**Changes:**

1. **Front-end candidates.** Each transforms the trial's opponent motion-energy trace x(t) (S + N at 60 Hz, the input of
   all fits so far) the same way on control and pulse trials, before the decision model. The drift gain is refitted
   and absorbs overall scale.
   - **F0 (current):** x' = x.
   - **F1, power law:** x' = sign(x)·|x|^γ, γ ∈ [0.3, 3] (one parameter; γ > 1 weights strong motion more than
     proportionally).
   - **F2, temporal divisive normalization** (approximation): x'(t) = x(t) / (1 + β·p(t)), where p is a causal
     exponential low-pass of |x| with time constant τ_n. β ∈ [0, 20], τ_n ∈ [0.02, 1] s (two parameters). The pool uses
     the opponent signal, so it cannot represent normalization by unsigned, non-opponent energy. A full
     normalization stage in the motion-energy computation is **not** part of this amendment.

   Implemented inside the simulator (both backends), so the input arrays stay fixed while parameters vary.
2. **Fitting, on control trials only.** Each of F1 and F2 is added to the common model (L0U0V1Z0G1, fast-only guesses,
   guess bias free), with all parameters refitted, warm-started from the F0 fits:
   - control-only CV (ccv0–ccv4, 15 repetitions, as in step 3.3);
   - all control trials, 50 repetitions, for predictions.
3. **Candidate selection, before any pulse outcome is read for these models.**
   - The selected front end is the candidate with the lowest summed held-out NLL on control trials (ccv0–ccv4).
   - It must beat F0 by more than the summed Monte Carlo noise (2 SD, analysis log 5.6) and be worse than F0 by more
     than 10 NLL in no more than 2 mice.
   - If F1 and F2 are within 20 summed NLL of each other, F1 (fewer parameters) is chosen.
   - If neither beats F0, F0 stays and the amendment stops at this step. That is reported as "no control-trial evidence
     for these front-end nonlinearities".
4. **Frozen predictions and gate.**
   - **Predictions:** pulse-trial predictions from the selected front end's all-control fit (≥ 200 repetitions),
     saved with the commit hash and SHA-256 checksums before gate 1 is computed.
   - **Gate:** gate 1–3 as in section 7 (GATE_MIN_INSIDE = 0.8), plus the descriptive checks by coherence and by mouse
     (amendment 6, item 3). No pulse gain is fitted.
   - **If the gate fails, the primacy and strategy analyses stop permanently.** The front-end comparison and the gate
     result are reported.
5. **Strategy comparison with the same front end** (amendments 4–5), run only if the gate passes:
   - E (leak 20–200 /s) is refitted on control trials with the selected front end, so the comparison stays fair;
   - frozen predictions, then the amendment 5 strategy test (pulse-gain statistic primary, paired SD, 3 SD and 6/10
     mice);
   - its power, computed from synthetic data from both refitted models before the observed test, as in amendment 5,
     item 4.
6. **Calibration before any timing contrast** (as amendment 6, item 6), run only if the gate passes.
   - **Data:** synthetic datasets from each mouse's selected model, whose pulse effects now match the data if the
     gate passed, with drift-gain decay of 0, 10, 20 and 40% over 0.5 s, ≥ 20 datasets each.
   - **Pipeline:** each dataset is put through items 4 and 7 unchanged.
   - **Report:** gate-pass rate, false-positive rate under zero decay, and detection overall and conditional on the
     gate, for both timing analyses in item 7.
7. **Timing analyses** (only after item 6 is reported):
   - **(a) Model-based:** the section 6 GLMM with offsets from the selected model's frozen predictions. Primary:
     β_middle, all mice, rig as a covariate. Secondary: UW late pulses.
   - **(b) Model-light, common response-time cut-off:**
     - **Trials:** responses with RT ≥ 0.92 s, i.e. after the latest scheduled pulse onset (0.417 s) plus 0.5 s. The
       same cut-off applies at every timing, so all pulses could act before the decision.
     - **Model:** Bayesian logistic GLMM of choice toward the pulse on timing (early as reference) and
       pulse-aligned signed coherence, with random intercept and timing slope per mouse, rig as a covariate, and priors
       as section 6; |coh| ≤ 36%.
     - **Flat-weighting reference:** the selection bias, i.e. the middle − early difference expected without primacy,
       is taken from simulations of F0, the selected model and E under the same cut-off. A prediction-only check
       (2026-10-25, 4 mice, 100 repetitions) gave −0.004 to +0.004 for the integrator, −0.008 to +0.031 for the
       integrator with 3× pulse, and +0.009 to +0.089 for E, i.e. bias toward apparent recency, not primacy.
     - **Claim rule:** primacy is claimed only if the 95% interval of β_middle lies below the most negative simulated
       flat-weighting bias. The UW late-vs-early contrast is reported descriptively, with the simulated bias (+0.02 to
       +0.06 in that check) subtracted.
   - **(c) Secondary:** gain decay and signed leak, each added to the selected model (one parameter), fitted on all
     trials and compared by 5-fold CV. Reported descriptively.
8. **Interpretation rules.**
   - Primacy or recency is stated only if analysis (a) or (b) excludes zero in that direction, the calibration's
     false-positive rate is ≤ 10%, and the result is labelled exploratory.
   - A null is reported with the calibration's detection rates, as "no evidence at this sensitivity", not as flat
     weighting.
   - Integration is supported out of sample only if the selected integrator passes the gate and the strategy test
     favours it under its own rule.
9. **One round, then stop.** No front-end or decision-model candidates beyond F1 and F2, no further revision after
   this amendment's gate, and no changes to thresholds after any result. Every item is reported whatever its outcome.

**Not changed:** amendments 1–6 and their results, which are reported as they stand.

**Cost (estimate):**
- code: front-end transforms in both simulator backends, checked against a numerical reference;
- Hyak: 100 ccv fits and 20 control fits, then, depending on the selection and the gate, E refits (~60),
  predictions (~30), strategy power, calibration (~800), and the extensions (~100).

**Amendment 7 stopped by V. Thakur, 2026-10-25, after item 3.**
- **Item 3 result:** F1 (power law) was selected on control-only CV: −64.0 summed held-out NLL vs F0, against a
  measured 2 SD of 28.9. The improvement is concentrated in two mice, and the fitted exponent is compressive
  (γ ≈ 0.6–0.8).
- **Not made:** no pulse-trial predictions from F1 or F2, and no gate.
- **Amendment 7a** (also gating F2, whose effect would mainly show on pulse trials) was proposed and not adopted.
- **Status:** the primacy analysis stays closed as stated in the closing note above. The front-end comparison on
  control trials is reported as exploratory.


---

## Amendment 8 (2026-10-26, before any recorded-choice kernel was computed): response-aligned kernel, integrator vs extrema detection

**Adopted by V. Thakur, 2026-10-26** ("add it if it pans out", G0 of the accumulation-first paper variant). Scope:
integration vs extrema detection on control trials only. Primacy stays closed (the stimulus-aligned primacy index has
no power; fluctuation-kernel report 2026-10-25). No refit, no new simulation, no pulse trials.

1. **Trials, fluctuation, bins, index:** exactly as in `.agents/plans/2026-10-25-fluctuation-kernel-power.md` step 3 and
   its v2 rerun: responded control trials, |coh| <= 36%, 48 mislabelled pulse trials excluded; f(t) = N(t) minus its
   frames 10-299 mean; response-aligned 100 ms bins -0.6..0 s (frames before the response and >= 0.1 s after onset);
   late-weight index = mean of the last two bins minus the first two (% coh), per mouse, from recorded choices and RTs.
2. **Predictions:** `pred_I` and `pred_E` per mouse as saved in `/mnt/data/processed/ddm/fluctuation_kernel_resp_power_v2.csv`
   (10 reps, seed 4000; fits_final primary control fit and fits_guess_fast_only_leak20-200 control fit). Not recomputed.
3. **Statistics:** S_I = sum over mice of (index - pred_I)^2, S_E likewise. Reference distributions: S_I over the 20
   synthetic I datasets and S_E over the 20 synthetic E datasets of the same file; q95 = 95th percentile (numpy linear).
4. **Verdict (fixed now):**
   - **Supports accumulation** if S_I < S_E, S_I <= q95(S_I | I) and S_E > q95(S_E | E).
   - **Supports extrema detection** if the mirror condition holds.
   - **Neither model fits** if S_I > q95(S_I | I) and S_E > q95(S_E | E).
   - **Not distinguished** otherwise.
5. **Descriptive only:** group mean index with a two-sided 95% t interval across mice (n = 10); per-mouse index next to
   both predictions. Per-mouse verdicts are not drawn (only PSUIM6/7 were reliably classified in the power check).
6. **Reporting:** whatever the verdict, the result is written to a report and given to the authors. "Supports
   accumulation" makes it eligible as supporting evidence for the control-trial comparison in the accumulation-first
   paper. "Supports extrema detection" bears on that claim and goes to the authors before any manuscript decision.
   "Neither" or "not distinguished" is reported as inconclusive.
7. **Caveats fixed in advance:** predictions come from fits to the same control trials (in-sample); the power check had
   no refit (optimistic); only two candidate models.

**Amendment 8, operating characteristics (2026-10-26, before the recorded-choice run).** The verdict rule applied to
the 20 + 20 saved synthetic datasets: I-generated 14 "supports accumulation", 5 "not distinguished", 1 "neither"; E-generated
19 "supports extrema detection", 1 "neither"; no wrong-model verdicts. (In-sample: the q95 thresholds come from the same datasets.)

---

## Amendment 9 (2026-10-27): responded-only re-analysis of the whole pulse pipeline (sensitivity re-analysis)

**Decided by V. Thakur, 2026-10-27** ("let's do full re-run"), after the rule that trials without a response by 5 s
(435 with no RT, 4,102 answered after 5 s; 4,537 in the DDM inputs) must not enter any analysis. This is a
re-analysis of a procedure that was closed (closing note, amendment 6 item 8) after its results were seen. It is
reported as a sensitivity re-analysis, never as the original prespecified test, and the original results stay reported.

1. **Data.** All fits, predictions, gates, gain fits, calibration and strategy checks use responded trials only
   (choice >= 0; RT 0.3–5 s): `--responded_only`, which removes those trials from the inputs on load.
2. **Likelihood.** The censored QMLE without its censored category (`include_censored=False`): per condition a binomial
   over left/right among simulated responses plus the unchanged RT term, i.e. conditional on a response by 5 s.
3. **Control fits.** Baselines and E from the responded-only refits (`ddm/fits_resp_final` control split, 50 reps, for
   primary and secondary, used for both the original-gate predictions and the pulse gain; `ddm/fits_resp_fast_only_leak20-200`
   control split for E). Originally the first-pass predictions used the 15-rep fits; the 50-rep fits are used for both here.
4. **Gates.** Gate 1 (departure) unchanged. Gate 2 (pulse-trial RT quantiles inside the 95% range in >= 80% of mouse x
   quantile cells) unchanged, computed on simulated responses. **Gate 3 (censored fraction) is dropped**: under the rule
   there is no observed censored fraction. Gate pass = gate 1 and gate 2.
5. **Calibration (amendment 6 item 6).** Unchanged design (4 levels x 20 datasets x 10 mice). Synthetic pulse-trial
   outcomes are generated on the mouse's responded pulse trials; synthetic trials without a response by 5 s are then
   dropped before the gain fits and the gate, as for real data.
6. **Strategy test and its power check.** Unchanged statistic (already computed on responded trials); predictions and
   synthetic datasets restricted to responded trials.
7. **Rules unchanged:** stopping rule (amendment 6 item 8) still applies: if the revised gate fails, the timing test is
   not run. No other model revision.
8. **Reporting:** original and responded-only results side by side; differences in denominators stated.

---

## Amendment 10 (2026-10-27, before any fit of this model): discrete-sample extrema detection (Stine et al. 2020)

**Decided by V. Thakur, 2026-10-27** ("lets do both"): keep the rapid-forgetting model of amendment 4 and add the
extrema-detection model as specified by Stine, Zylberberg, Ditterich & Shadlen (2020, eLife 9:e55365, Methods;
PMC7217695): momentary evidence sampled every Δt from N(κ(C − C0)Δt, Δt) (unit variance per second), each sample
compared with ±B, the first sample beyond a bound decides, sub-threshold samples are discarded (no integration); in a
free-response task the decision ends only at an extremum. They used Δt = 0.5 ms and report results unchanged at 1 ms.
Responded-only rules of amendment 9 apply throughout.

1. **Model (Es).** Sample s_t = (drift_gain · x(t) + drift_offset + sv draw) · Δt + ε_t, ε_t ~ N(0, Δt), Δt = 1 ms (the
   simulator step), x(t) the trial's motion-energy input (as for every model). Choice = sign of the first s_t with
   |s_t| ≥ B; RT = that time + ndt. B = b · √Δt with b free in **[2, 5]** (per-step noise SDs; b = 3 gives a mean
   zero-drift decision time of ~0.37 s, b = 4 ~16 s). a and z are unused (fixed). drift_offset plays the role of C0.
2. **Shared components (fairness, as in amendment 4):** drift variability sv, the fast-only guess mixture with free guess
   bias, ndt, drift_offset, same bounds; drift_gain bound **[0.5, 200]** from the start (amendment 5 allowed 200 for E).
   Stine et al.'s model has no sv or guesses; that difference is reported.
3. **Differences from Stine et al. stated in the paper:** continuous filtered motion energy (~100 ms filters) instead of
   independent stimulus samples, so stimulus fluctuations are correlated across samples while internal noise is not;
   Δt = 1 ms; sv and fast guesses added.
4. **Fits and comparison:** control-only CV (ccv0–ccv4) and all control trials, responded-only, 15 repetitions, same
   folds, seeds and held-out scoring; compared with the accumulator and with E (amendment 4) by the same > 10 held-out
   NLL rule. Nothing about Es changes the THESIS selection rule of the accumulation-first paper (which concerns E);
   how Es enters the spine is an author decision after the results.
5. **Recovery:** Es-generated datasets (2 replicates x 10 mice) fitted by the accumulator and by Es, same rule as F1a.
6. **Pulse:** frozen pulse predictions from the Es control fits, and the strategy test Es vs primary, as for E.
7. **Checks before fitting:** both simulator backends agree; zero-drift mean decision time matches 1/(2(1 − Φ(b))) steps.

---

## Amendment 11 (2026-10-27): plausible response rate in responded-only fits

**Decided by V. Thakur, 2026-10-27** (option 1). Found after the responded-only fits (amendments 9-10) had run and the
control-trial comparison had been computed: the likelihood conditional on a response by 5 s does not constrain how
often a model responds, and 7/50 rapid-forgetting (E) CV fits, 1/50 discrete-sample (ES) CV fits and the E all-control
fit of PSUIM10 converged to parameter sets predicting no response on ~98% of trials (bound ~7.5 noise SDs vs ~3.4 in
the other E fits), all in the two mice with the fewest trials (DBM13, PSUIM10). On held-out folds those fits leave whole
conditions without a simulated response (empty-cell penalty), which supplied 2,020 of the 2,291 summed E-minus-
accumulator difference. The accumulator (0/50 fits above 20%) was not affected. Code was checked and is not at fault.

1. **Rule.** In training (the fit objective of every responded-only model fit, model-recovery fits and pulse-gain fits),
   a parameter set whose simulated trials include more than **50%** without a response by 5 s is rejected (objective
   1e6, as for invalid parameters). Held-out scoring is unchanged.
2. **Justification and limit.** The analysed trials are those with a response; mice responded within 5 s on ~85% of
   trials overall (4,537 of 30,030 excluded). The cap uses only that aggregate fact, generously, not the excluded trials'
   outcomes. It is a model constraint introduced after seeing results, stated as such in the paper.
3. **Refits.** Every responded-only fit set in which any fit exceeds the cap is refitted with the rule (E and ES at
   least; others after an audit); fit sets in which no fit exceeds 50% are unchanged, because the rule cannot bind
   at their optimum. Downstream jobs using refitted models (P2, ES3, F1a, ES2) are rerun.
4. **Reported:** results before and after the cap, and the empty-cell penalty decomposition.

---

## Amendment 12 (2026-10-27): common model re-selected under the responded-only rule (parsimony rules 2-3 as written)

**Decided by V. Thakur, 2026-10-27** (option A: apply the rules as written). Responded-only control-only CV (amendments
9 and 11; analysis log 8.4g; plan 2026-10-26-v2-refits-and-strategy-recovery.md): removing sv worsens held-out fit
beyond the > 10 noise threshold in 4/10 mice only (summed +278), so sv fails rule 2 ("in most mice"); guesses pass
(8/10, +431); leak, urgency and both fail (alternative better > 10 in 2, 1, 1 mice; none better by most). A free guess
bias clearly helps in 1/10 mice (+50 summed), so rule 3 fixes guess_bias at 0.5.

1. **New common model (C'):** L0U0V0Z0G1, fast-only guesses, guess_bias fixed at 0.5. Secondary baseline: L1U1V0Z0G1,
   same guess form. Rapid forgetting (E'): L1U0V0Z0G1, leak 20-200/s, same guess form. Discrete-sample extrema (ES'):
   the C' components with the amendment-10 sample rule. Free-leak description: L1U0V0Z0G1, leak 0-200/s.
2. **Check of rule 3 on C':** after the C' fits, free versus fixed guess bias is compared on C' (existing free-bias
   L0U0V0Z0G1 CV fits vs the new fixed-bias ones); if a free bias clearly improves fit (> 10 in most mice), it is restored
   and the decision recorded here.
3. **Everything downstream is redone with C'** (amendments 9-11 apply): control comparisons with E' and ES', strategy
   recovery for E' and ES', pulse predictions, gates, pulse gain, calibration, strategy tests. Code: `--model_set nosv`.
4. **Reported:** the sv-model results (amendments 9-11) as a sensitivity analysis next to the C' results; that the common
   model changed because the analysed trial set changed; sv's earlier 8/10 versus 4/10 now.
