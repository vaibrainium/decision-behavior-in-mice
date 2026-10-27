# Report: descriptive checks of a pulse readout-bias (slow-trial) account
Date: 2026-10-27   Agent: Claude Opus 5.5   Commit: 85d4f8d (+ uncommitted scripts/ddm/pulse_readout_checks.py)
Plan: plans/2026-10-27-pulse-readout-bias-checks.md

## Question
Does the pulse effect live in slow trials, are slow ±100% control trials near chance, and are RTs unchanged given choice?

## Summary
None of the three expectations holds. The pulse effect is in fast-to-middle RTs (median ~0.5-1.3 s) and absent in the
two slowest quintiles; slow ±100% control trials are the most accurate (0.91), the fast ones the least (0.66); and
pulse-direction choices are faster on pulse trials (median -71 ms, 0.9 quantile -152 ms; noisy). This pattern looks more
like the pulse acting as evidence on trials still deciding shortly after it than like a readout bias on slow trials. Descriptive; exploratory.

## Findings (VERIFIED; responded trials, symmetric cells, 10 mice, mean ± SEM; source dissemination/figures/qc/pulse_readout_checks_2026-10-27_{by_bin,rt_given_choice}.csv)
- RT quintiles from controls; median RT per quintile (±100%: 0.45, 0.80, 1.15, 1.62, 2.78 s; |c| <= 36: 0.46, 0.88, 1.30, 1.92, 3.45 s).
- 1. Pulse effect (pp), |c| <= 36: 4.9 ± 1.2, 4.3 ± 2.6, 6.2 ± 2.2, -0.2 ± 1.7, -0.4 ± 2.5. ±100%: 2.3 ± 4.8, 11.8 ± 2.4, 2.3 ± 2.5, 0.5 ± 2.8, 3.7 ± 5.8.
- 2. Control accuracy at ±100%: 0.66 ± 0.03, 0.85, 0.88, 0.90, 0.91 ± 0.03.
- 3. RT pulse - control given choice (ms; q 0.1-0.9): toward pulse 16, -23, -71, -109, -152 (SEM 23-84); against pulse -11, -4, 39, 42, -48 (SEM 18-79).
- 4. No-response rates not run (author rule). Existing value, from before the rule: positive - negative pulse +2.07 pp [-0.36, 4.49], p 0.086 (package C).
  Author 2026-10-27: no exception granted (lapse capture ruled out); not run.

## Caveats
RT bins condition on an outcome the pulse changes (a pulse that speeds pulse-direction choices moves trials between bins).
Bins use control edges, so pulse-trial bin counts differ. ±100% has only incongruent pulses and few trials per bin.

## Open questions and next steps
- [ ] The fast errors at ±100% (0.66 in Q1) are the fast-guess component; the pulse effect at ±100% sits in Q2 (~0.8 s), not Q1.
- [ ] Evidence-like but larger than predicted: compare these RT-conditioned effects with the primary model's on the same bins (needs per-trial simulated RTs; cache stores only summaries).
