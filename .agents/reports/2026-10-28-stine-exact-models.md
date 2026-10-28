# Report: paper-exact Stine et al. (2020) extrema detection (ESx) and integration (DDMx) models, responded-only
Date: 2026-10-28   Agent: Claude (Opus 5.5)   Commit: 45e756a
Plan: plans/2026-10-27-paper-exact-stine-models.md; amendment 13 and its addendum in dissemination/reports/primacy-analysis-plan.md

## Question
With the free-response models exactly as Stine et al. specify them (nominal coherence input, κ, B, C0, tND; no drift
variability, guesses, leak or urgency), does control-trial prediction, pulse prediction or recovery distinguish
extrema detection from integration in these mice, and how do both compare with the common model C (L0U0V1Z0G1)?

## Summary
They are barely distinguishable. On held-out control trials DDMx is better than ESx by > 10 in 3/10 mice, ESx in none
(summed 62.7); the pulse strategy test does not distinguish them at any of three pulse latencies; and recovery is weak
(each model's own data recognised in 5-7/20, 12/20 within 10). Both fit far worse than C (summed 655-718, C better in
6/10 mice, neither better in any). Conclusion consistent with F1a (THESIS_B): without drift variability and fast
guesses, neither strategy model captures these mice, and these data do not separate the two strategies.

## Findings (all VERIFIED; inline scripts in the session transcript of 2026-10-27/28; per-mouse sums in plan log)
- Fits: 60 + 60 (ccv0-4 + control). DDMx first fitted with drift_gain >= 0.5 (bound at 0.5 in 31/60) -> refitted with
  >= 0.01 (addendum; fits_resp_nominal_ddm_g001): gains 0.25-1.13, held-out improved by 31.4 summed. ESx: no parameter
  at a bound (gain 3.7-13.1, b 3.25-3.60). DDMx tND at 0 in 17/60 (natural bound; fast responses without guesses).
  C0 (control fits): DDMx -0.26..0.18 (first fits), ESx -0.27..0.14.
- Held-out NLL, control-only CV summed over folds (positive = second model better):
  ESx - DDMx 62.7 (DDMx 3/10, ESx 0/10); DDMx - C 655.4 (C 6/10, DDMx 0/10); ESx - C 718.0 (C 6/10, ESx 0/10).
  Reference, same C: E - C 278.9 (C 5/10); ES - C 391.0 (C 6/10).
- Pulse strategy test ESx (a) vs DDMx (b), pulse statistic z / total z: lead rule (UCLA 54.3, UW 60.1 ms) 1.20 / 1.86;
  +50 ms -0.58 / 0.13; -50 ms 3.39 (same sign in 5/10 mice) / 1.27; "not distinguished" at all three.
  Files: ddm/primacy_exact2_resp{,_lead+50,_lead-50}/results_strategy_extrema_exact_vs_integration_exact.pkl.
- Recovery (recovery_exact2_resp, 80): DDMx-generated scored DDMx 5, ESx 3, within 12; ESx-generated scored ESx 7,
  DDMx 1, within 12. No fit > 5 NLL above its generating parameters on training data.

## What didn't work
- First DDMx fits: drift_gain lower bound 0.5 (from motion-energy models) bound in nominal units; superseded
  (v1 numbers in the plan log: ESx - DDMx 31.3).
- Mixed partitions on Hyak (gpu-a100,ckpt-all): InvalidQOS (one QOS per job); split arrays by hand instead.

## How to reproduce
Code 40dc38e + 038bbc8 (gain bound). Hyak: DDMx 42491645, ESx 42487747, predictions 42492100/42493231/42493235
(DDMx), 42488498/42488548/42488550 (ESx, copied into primacy_exact2_resp*), recovery 42493255 + 42497999 + 42498684.
Commands in the plan file. Pulse timing: ddm/pulse_timing_global.npz (sha256 01d4d378...55f4, build_pulse_timing.py).
Strategy tests: `python -m scripts.ddm.primacy --strategy_test --strategy_model extrema_exact --strategy_baseline
integration_exact --responded_only --unblind --out_dir ddm/primacy_exact2_resp[_lead±50]`.

## Caveats
- Fitted with this study's held-out choice + RT-quantile likelihood, conditional on a response (not their mean-RT fit);
  Δt 1 ms; 0.3 s response floor and 50% no-response cap apply. Their collapsing-bound version was not run.
- Early pulses whose latency-shifted start precedes 0 are clipped at 0 in the nominal input.
- The bound change for DDMx was made after its first results were seen (stated in the addendum).
- 20 datasets per recovery cell.

## Open questions and next steps
- [ ] Author: whether ESx/DDMx enter the accumulation-first paper (e.g. one supplementary panel: "the paper-exact
      models do not distinguish the strategies and both fit worse than the common model"), or are reported only here.
