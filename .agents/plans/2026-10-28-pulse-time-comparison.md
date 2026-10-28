# Plan: does the pulse effect change with pulse time (early vs middle vs late)?
Status: done
Created: 2026-10-28 by Claude (Opus 5.5)
Related reports: reports/2026-10-28-pulse-direction-by-time.md
Related decisions: D003 (responded only), D010 (right vs left pulse framing)

## Goal
Author question: is the pulse effect larger for earlier pulses (early > middle > late)? A direct, within-mouse test of
the change in the right - left pulse effect across pulse times, with effect sizes and corrected p values.

## Context
- Current per-time analysis (D010) bootstraps each stage separately; it gives per-stage effects (bias right - left
  -17.1 / -12.4 / -16.8 % coherence) but no test between stages.
- Pulse trials per mouse and stage (responded, symmetric cells; scripts/ddm/pulse_psychometric_stage.load_trials):
  min 84 / 78 / 102, median 300 / 268 / 198 (early / middle / late). Late exists only for the 6 DBM mice.
  Per-mouse psychometric fits are too noisy for the low-count mice (~4-5 trials per mouse x direction x coherence cell);
  not used except as a descriptive check.
- Pulse onsets differ by rig (early ~17-117 ms vs 50 ms; middle ~200-300 vs 233 ms; late 417 ms, one rig only). Rig is a
  covariate only; no site split (memory rule).

## Assumptions
- The right - left difference in P(right) captures the pulse effect for comparison across stages (same coherence set
  per mouse across stages; check it).
- RT is available per trial in ddm_inputs_global.npz for the RT-conditioned check (verify field name).

## Steps
- [x] 1. Primary: mixed-effects logistic regression on responded pulse trials (and control trials for the coherence
      term): right ~ coherence (categorical or logistic in c) + pulse_direction x stage + rig, random effects by mouse
      (intercept + pulse_direction, and by stage if it converges). Tests: pulse_direction x stage interaction
      (likelihood-ratio), planned contrasts early vs middle (10 mice) and early/middle vs late (6 DBM mice), linear trend.
      Check that statsmodels (BinomialBayesMixedGLM) or another installed package fits it; if none fits, tell the author
      rather than installing.
- [x] 2. Per-mouse, model-free: right - left P(right) averaged over the coherences each mouse has in every stage;
      paired t and Wilcoxon (early vs middle: 10 mice; each vs late: 6 mice), Holm over the 3 comparisons, dz; count of
      mice with early > middle > late; Page's trend test on the 6 mice with all three stages.
- [x] 3. Sensitivity: the same restricted to trials with RT > pulse onset + 100 ms (decision still open at the pulse).
      Report how many trials each stage keeps. Note that this selects slower trials.
- [x] 4. (dropped: per-mouse lines of the pp and logit measures shown instead) Descriptive: per-mouse psychometric bias per stage (shared lapses) shown only as a figure, flagged as noisy.
- [x] 5. Verify: model-free per-stage group means reproduce the sign and rough size of the per-stage bootstrap results;
      mixed-model per-stage pulse effects agree in sign with step 2.
- [x] 6. Report, dashboard panel in section 5, STATUS.

## Out of scope
Congruency framing (D010); model predictions of the time course; per-site results.

## Log
- 2026-10-28: plan written at the author's request ("from here I want to see if earlier pulse had higher effect compared
  to middle compared to late"); approach proposed, not yet approved. Power caveat: early-middle gap (~5 % coherence)
  is small against per-stage CIs ~25 wide; a null is likely and must be reported as inconclusive, not as equal effects.
- 2026-10-28: author approved the approach ("yes"); started.
- 2026-10-28: deviation, step 1: no frequentist logistic GLMM installed (statsmodels has only the variational
  BinomialBayesMixedGLM; no R, pymer4, bambi). Step 1 becomes a hierarchical Bayesian logistic model in PyMC (installed):
  logit P(right) = base[mouse, coherence] + direction x b[mouse, stage]; base cells partially pooled per coherence;
  b[m, s] ~ Normal(B_s + g_s * rig_centred[m], tau_s) (rig covariate for early/middle; late is one rig).
  Contrasts are within-mouse averages over the sample mice: early - middle (10 mice), early - late and middle - late
  (6 mice with late); posterior mean, 95% HDI, P(> 0). Frequentist tests come from step 2. Step 2 adds per-mouse
  logistic coefficients (statsmodels GLM: right ~ C(coh) + direction x stage) next to the model-free pp.
  Onsets: scheduled_onset_s (uw) else recorded_onset_s (ucla); 10.1% of responded late-pulse trials respond before
  onset (early 0%, middle 0%), 15.9% before onset + 100 ms.
- 2026-10-28: full run first killed (OOM) by az.rhat(...).to_array(); fixed. Figure adds the 6-late-mice means.
  Step 4 replaced by per-mouse lines of the pp/logit measures (psychometric fits per mouse too noisy, as planned).
  Result: no within-mouse change across pulse times (all intervals span 0). Dashboard version 18. Report:
  reports/2026-10-28-pulse-time-comparison.md.
