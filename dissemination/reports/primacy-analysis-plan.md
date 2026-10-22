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
