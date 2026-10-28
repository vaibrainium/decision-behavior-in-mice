# Plan: does the pulse effect change with pulse time (early vs middle vs late)?
Status: active (proposed; awaiting author approval of the approach; to start next session)
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
- [ ] 1. Primary: mixed-effects logistic regression on responded pulse trials (and control trials for the coherence
      term): right ~ coherence (categorical or logistic in c) + pulse_direction x stage + rig, random effects by mouse
      (intercept + pulse_direction, and by stage if it converges). Tests: pulse_direction x stage interaction
      (likelihood-ratio), planned contrasts early vs middle (10 mice) and early/middle vs late (6 DBM mice), linear trend.
      Check that statsmodels (BinomialBayesMixedGLM) or another installed package fits it; if none fits, tell the author
      rather than installing.
- [ ] 2. Per-mouse, model-free: right - left P(right) averaged over the coherences each mouse has in every stage;
      paired t and Wilcoxon (early vs middle: 10 mice; each vs late: 6 mice), Holm over the 3 comparisons, dz; count of
      mice with early > middle > late; Page's trend test on the 6 mice with all three stages.
- [ ] 3. Sensitivity: the same restricted to trials with RT > pulse onset + 100 ms (decision still open at the pulse).
      Report how many trials each stage keeps. Note that this selects slower trials.
- [ ] 4. Descriptive: per-mouse psychometric bias per stage (shared lapses) shown only as a figure, flagged as noisy.
- [ ] 5. Verify: model-free per-stage group means reproduce the sign and rough size of the per-stage bootstrap results;
      mixed-model per-stage pulse effects agree in sign with step 2.
- [ ] 6. Report, dashboard panel in section 5, STATUS.

## Out of scope
Congruency framing (D010); model predictions of the time course; per-site results.

## Log
- 2026-10-28: plan written at the author's request ("from here I want to see if earlier pulse had higher effect compared
  to middle compared to late"); approach proposed, not yet approved. Power caveat: early-middle gap (~5 % coherence)
  is small against per-stage CIs ~25 wide; a null is likely and must be reported as inconclusive, not as equal effects.
