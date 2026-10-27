# Report: pulse psychometric functions (control / congruent / incongruent), data vs responded-only variants
Date: 2026-10-27   Agent: Claude Opus 5.5   Commit: 85d4f8d (+ uncommitted scripts/ddm/pulse_psychometric.py)
Plan: plans/2026-10-27-pulse-psychometric-variants.md

## Question
Author request: psychometric functions for congruent, incongruent and control trials, data and every responded-only model variant.

## Summary
All seven variants predict pulse effects of 0.35-1.9 pp, below the observed ones (congruent 2.0 pp, incongruent 4.0 pp,
|c| <= 36). Adding a cross-validated pulse gain or using ES gets closest but still predicts about half the incongruent effect.
Observed effects are noisy per coherence (SEM 1-6 pp), so the per-coherence shape is not informative. Descriptive only.

## Findings (VERIFIED; mean ± SEM over 10 mice of per-mouse means over |c| <= 36, pp, P(pulse direction | response), pulse - control;
source dissemination/figures/qc/pulse_psychometric_variants_2026-10-27_effects.csv)
| source | congruent | incongruent |
|---|---|---|
| observed | 1.97 ± 1.33 | 4.01 ± 2.17 |
| primary (L0U0V1Z0G1) | 0.60 ± 0.16 | 0.98 ± 0.06 |
| secondary (L1U1V1Z0G1) | 0.35 ± 0.09 | 0.71 ± 0.13 |
| primary + pulse gain (CV) | 1.06 ± 0.32 | 1.85 ± 0.50 |
| secondary + pulse gain (CV) | 0.80 ± 0.23 | 1.33 ± 0.46 |
| E rapid forgetting (leak 20-200, cap) | 0.76 ± 0.18 | 1.41 ± 0.19 |
| ES extrema samples (cap) | 1.11 ± 0.15 | 1.61 ± 0.16 |
| free leak 0-200 (cap) | 0.35 ± 0.15 | 0.63 ± 0.15 |
- Control psychometric functions are captured by all variants (figure top row).
- Check: fresh CPU re-simulation of saved primary predictions (PSUIM10): corr 0.975, predicted effect 0.55 vs 0.58 pp.

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_psychometric` (simulation cache processed/ddm/pulse_psychometric_resp/; saved
pulse predictions primacy_resp/{primary,secondary,extrema_samples}, primacy_revised_resp/{primary,secondary}).

## Caveats
- Includes UW asymmetric-coherence sessions (only rightward pulses; known issue): congruent vs incongruent at a given
  coherence then come from different sessions. Data and models use identical trials, so the data-model comparison is
  fair, but the congruent-vs-incongruent difference in the data is confounded by session.
- Congruent vs incongruent difference in pp is also shaped by the baseline (ceiling); not tested.
- E cap refit's bound check is still pending in the refit plan. No inferential test here.

## Open questions and next steps
- [ ] Rerun excluding UW asymmetric sessions if the congruent/incongruent asymmetry is to be interpreted.
