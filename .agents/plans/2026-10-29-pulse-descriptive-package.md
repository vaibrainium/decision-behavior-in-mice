# Plan: pulse descriptive package on all 10 mice (S1, S2, S3)
Status: done
Created: 2026-10-29 by Claude (Opus 5.5)
Related reports: reports/2026-10-29-pulse-leak-vs-urgency.md (route step 1), reports/2026-10-28-pulse-time-comparison.md

## Goal
Model-free pulse signatures on all 10 mice, computed with the same code paths the simulations use, so later models can
be judged against them: S1 pulse-to-response profile per onset, S2 onset effect by |coherence|, S3 RT shifts by onset.
Author approved ("ok", 2026-10-29) after the leak-vs-urgency report recommended this as the next cheap step.

## Context
- Helpers in scripts/ddm/pulse_leak_urgency_signatures.py (observed, with_bins, effect, rt_shift, bootstrap_profile).
- Responded trials only (D003), symmetric cells, |coh| <= 36, onset = scheduled (UW) else recorded (UCLA). Late
  pulses exist only in the 6 DBM mice. Rig is a covariate only; no site split.

## Assumptions
- The pulse-count-weighted pp effect (P(choice = pulse sign | pulse) - P(same | control), matched on coherence) is the
  shared effect measure; it is what the simulations report.
- Control trials get the stage's median onset as a pseudo-onset for S1 (as in the illustration).

## Steps
- [x] 1. Script scripts/ddm/pulse_descriptive_package.py (data only, local CPU, no fits).
- [x] 2. S1: per mouse x stage x bin effect with trial-bootstrap SE; group mean over mice per stage x bin with 95% CI
      (mouse bootstrap). Pre-specified tests, mice as unit: (a) effect in 0.3-1.2 s > 0; (b) effect after 1.2 s
      differs from 0 (the "no reversal" claim; report CI, not just p); (c) early minus late window difference.
      Holm over the S1 family.
- [x] 3. S2: per mouse x stage x |coh| effect; group means; per-mouse slope of (early - middle) over |coh| (10 mice),
      t and Wilcoxon, dz. Flag as likely underpowered.
- [x] 4. S3: per mouse x stage, RT quantile shifts and mean/SD RT shifts (pulse minus control) for choices toward
      and against the pulse, coherence-matched; group means and CIs; sign counts across mice.
- [x] 5. Figure + CSVs (dissemination/figures/qc/pulse_descriptive_package_<date>*), trial counts per cell.
- [x] 6. Verify: S1 pooled-window values reproduce the illustration's stage effects for PSUIM6/7/DBM6; report;
      STATUS.

## Out of scope
Model fits, simulations of other mice, leak/urgency inference, manuscript changes.

## Log
- 2026-10-29: plan written and started (cheap, local, no fits).
- 2026-10-29: done. S1 windows tested on pp and logit; S2/S3 descriptive. Report reports/2026-10-29-pulse-descriptive-package.md.
