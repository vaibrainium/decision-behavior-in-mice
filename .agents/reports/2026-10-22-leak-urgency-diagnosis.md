# Report: why leak and urgency help only PSUIM5/6/7
Date: 2026-10-22   Agent: Claude (Opus 5.5)   Commit: 6293e71
Plan: dissemination/reports/mouse-ddm-next-steps.md step 3.2; follows reports/2026-10-21-ddm-common-model-selection.md

## Summary
Not power: the other seven mice pooled (12,307 trials) gain ~0 from leak (+6.8 ± 4.0) and urgency (−0.3 ± 4.5). In
the mice where they help, they mostly fit the rate of censored (> 5 s) trials. That rate is nearly
coherence-independent (5–12% even at 100%), yet the late responses are coherence-dependent (accuracy 0.57–0.88 by
coherence): consistent with a delayed start of integration, not disengagement. Neither model captures it.

## Findings
- VERIFIED: pooled and per-rig gains (analysis log 5.6; `ddm/mc_noise/mc_noise_per_mouse.csv`).
- VERIFIED (in-sample, 20 reps): misfit removed by leak + urgency is mostly no-response (PSUIM6 +174, PSUIM7 +196).
  `python -m scripts.ddm.diagnose_leak_urgency`.
- VERIFIED: P(no response) by |coherence| flat 0–36%, 5–12% at 100%; models underpredict at 100%.
- VERIFIED: 60–100% of censored trials per mouse are responses after 5 s (median 7.7 s); their accuracy rises with
  coherence. Disengagement (first reading) is wrong: the 5 s cutoff is our censoring choice (V. Thakur).
- SUSPECTED: leak/urgency substitute for a missing delayed-engagement process (variable start of integration).

## How to reproduce
`python -m scripts.ddm.diagnose_leak_urgency` (all checks, ~10 min CPU) or `--data_only`; pooled gains from
`ddm/mc_noise/mc_noise_per_mouse.csv`.

## Caveats
Control trials only; all-trial fits; G statistic in-sample with simulation noise not quantified.

## Next steps
- [x] Delayed-engagement parameter: not pursued (V. Thakur, 2026-10-22).
- [ ] Authors: choose the common model (recommended strict: L0U0V1Z0G1 + fast_only; options and paper consequences in
      next-steps step 3 and dissemination/paper/outline.md R4).
- [ ] Then: fast_only with guess_bias fixed at 0.5 (needs a fixed-bias option), fit-quality plots, step 3.3, recovery.
