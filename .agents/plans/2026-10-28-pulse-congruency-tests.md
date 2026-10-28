# Plan: pulse effects as congruent vs incongruent (author's chosen framing)
Status: active
Created: 2026-10-28 by Claude (Opus 5.5)
Related reports: reports/2026-10-27-pulse-contrast-responders-only.md, reports/2026-10-27-pulse-asymmetry-lapse-checks.md
Related plans: plans/2026-10-28-pulse-psychometric-by-stage.md

## Goal
Tested pulse effects in the congruent / incongruent framing, replacing positive-vs-negative as the paper's pulse contrast.

## Specification (written before computing)
- Trials: responded (D003), symmetric cells (as pulse_asymmetry_lapse), |coherence| 9-36% (the existing
  congruency_effects definition; ±100% has no congruent pulses and 0% has no direction).
- Per mouse and coherence, effect in the pulse direction: congruent = sign(c) * (P(R | congruent) - P(R | control));
  incongruent = -sign(c) * (P(R | incongruent) - P(R | control)); mean over coherences within the mouse; pp.
- Primary (stages pooled): congruent effect vs 0, incongruent effect vs 0, and congruent - incongruent; mice as unit
  (n = 10); one-sample t and Wilcoxon; Holm over these 3; dz.
- Secondary (descriptive with tests): the same per stage (early, middle: 10 mice; late: 6 mice), Holm over the 9.
- Known from earlier: congruent - incongruent ~0.5 pp, not significant (asymmetry report); expected again.

## Steps
- [x] 1. scripts/ddm/pulse_congruency_tests.py (reuses congruency_effects); tables in paper_accumulation/tables.
- [x] 2. Verify: pooled congruent - incongruent matches the asymmetry report's observed A sign and size.
- [ ] 3. Dashboard: congruency test table in section 5; decision D010; report.

## Out of scope
Model predictions; RT effects.

## Log
- 2026-10-28: plan written after author chose the congruency framing.
- 2026-10-28: results: congruent 3.0 pp (Holm 0.096), incongruent 3.6 (0.39), difference -0.5 (0.87); check vs asymmetry
  report passed. Step 3 held: author to choose which test the paper reports (reports/2026-10-28-pulse-congruency-tests.md).
