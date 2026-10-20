# Primacy test: analysis plan (written before looking at pulse residuals)

**Status: DRAFT for review** (2026-10-20). Once agreed, commit it unchanged and record the commit here; that version is
the confirmatory analysis. Anything decided after looking at pulse-trial residuals is reported as exploratory.
Context: plan step 6 in [`mouse-ddm-next-steps.md`](mouse-ddm-next-steps.md); model and data in
[`mouse-ddm-analysis-log.md`](mouse-ddm-analysis-log.md).

**Items marked ⟨decide⟩ need a choice before the plan is locked.**

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
- Coherence range ⟨decide⟩: **(a)** |coherence| ≤ 36% (choices not saturated, so a pulse can move them), or **(b)** all
  coherences. Proposal: (a) primary, (b) as a robustness check.
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
- Fitting tool ⟨decide⟩: frequentist GLMM (e.g. `statsmodels` / `lme4`) or a Bayesian one (`pymc`, weakly informative
  priors; report the posterior of β_middle and P(β_middle < 0)). Proposal: Bayesian, since 10 mice make random-slope
  variance estimates unstable in frequentist fits.
- **Per-mouse estimates** of the timing effect are shown alongside the group estimate.

## 7. Gate: predictive check before the timing test (plan step 6.2)

Done first, and does not involve the timing contrast:
1. β0 (overall departure, all timings pooled) is reported; the model passes if the 95% interval of the pooled pulse
   effect contains the model's prediction, or the departure is < 25% of the predicted pulse effect ⟨decide threshold⟩.
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

## 11. Decisions to make before locking ⟨decide⟩

1. Coherence range for the primary analysis (section 4).
2. Frequentist or Bayesian GLMM (section 6).
3. Predictive-check threshold (section 7).
