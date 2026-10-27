# Plan: is the incongruent > congruent pulse asymmetry real, and are +-100% pulse effects lapse capture?
Status: done (report: reports/2026-10-27-pulse-asymmetry-lapse-checks.md)
Created: 2026-10-27 by Claude Opus 5.5
Related reports: reports/2026-10-27-pulse-psychometric-variants.md

## Goal
Two model-free checks before any nonlinear-leak (sinh, Glaze et al. 2015) model is considered (author: "okay", 2026-10-27).

## Design (fixed before computing)
Responded trials only; asymmetric UW cells (trial_table signs_scheduled_symmetric False, pulses and controls) excluded.
1. Asymmetry: per mouse, congruent and incongruent effect = mean over |c| in {9, 18, 36} (both signs) of pulse - control
   in P(pulse direction | response) (pp; secondary: logit of cell means). A = incongruent - congruent. Per variant, paired
   t over mice of A_obs - A_model (df = mice - 1); Holm over the 7 variants. Also A_obs vs 0.
   Rule: asymmetry beyond the model only if A_obs - A_model > 0 with Holm p < 0.05 for the primary variant.
2. Lapses at +-100%: incongruent pulse trials vs control trials at the same coherence. Per mouse and RT bin
   (0.3-0.5, 0.5-1, 1-2, 2-5 s), errors per trial (pulse) - errors per trial (control). Lapse/guess capture predicts
   the excess concentrated in 0.3-0.5 s (fast-guess component: guess_t0 0.3 s, tau ~0.3 s). Descriptive, mean +- SEM over mice.

## Steps
- [x] 1. scripts/ddm/pulse_asymmetry_lapse.py (model predictions from the pulse_psychometric cache/saved files).
- [x] 2. Run; tables + figure in dissemination/figures/qc/.
- [x] 3. Report + STATUS.

## Log
- 2026-10-27: done; asymmetry absent once asymmetric UW cells are excluded; ±100% excess errors not concentrated in fast RTs.
