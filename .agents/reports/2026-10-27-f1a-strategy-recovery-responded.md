# Report: F1a comparison recovery (accumulator vs rapid forgetting), responded-only, with the no-response cap
Date: 2026-10-27   Agent: Claude (Opus 5.5)   Commit: 27d9b23
Plan: plans/2026-10-26-v2-refits-and-strategy-recovery.md; thesis rule D002 (dissemination/paper_accumulation/np/spine.md)

## Question
When the rapid-forgetting model E (L1U0V1Z0G1, leak 20-200/s) generates control-trial data, how often does the
control-only comparison score those data as favoring the accumulator C (L0U0V1Z0G1)? *k* of 20 selects the
accumulation-first paper's THESIS (k <= 2: A; k >= 5: B; 3-4: B-rate).

## Summary
*k* = 5/20, so under the D002 rule **THESIS_B** applies: the comparison favored the accumulator on real data but also
on a quarter of E-generated datasets, so it does not reliably distinguish the two strategies. The 5 are not optimizer
failures: in each, C's held-out NLL is lower than E's at E's own generating parameters (by 15-80). Confidence in k:
high for these 20 datasets; k itself has binomial uncertainty (2 replicates x 10 mice).

## Findings
- VERIFIED. E-generated (20): scored accumulator (E - C > 10) 5, scored E (< -10) 9, within 10: 6; median -9.5.
  The 5: DBM12 rep0 84.9, DBM15 rep0 80.1, DBM15 rep1 15.0, PSUIM10 rep0 24.4, PSUIM6 rep1 61.1.
- VERIFIED. C-generated (20): scored accumulator 16, scored E 3, within 10: 1; median 27.9.
- VERIFIED. The 5 are genuine: held-out NLL C fit vs E at true parameters: DBM12 2216.6 vs 2291.7; DBM15 r0 1278.9 vs
  1357.9; DBM15 r1 1370.9 vs 1383.7; PSUIM10 528.1 vs 552.8; PSUIM6 7953.3 vs 8001.5. E's training
  NLL at its fit is 10.8-15.3 below truth in all five (optimizer reached the optimum).
- VERIFIED. Precondition of the rule holds: real-data control comparison E - C summed 278.9, C better > 10 in 5/10
  mice, E in 0/10 (fits_resp_fast_only_leak20-200_cap vs fits_resp_fast_only, ccv0-4).
- VERIFIED. E cap fits: drift_gain max 6.98 (limit 20) -> no amendment-5 refit; leak at its lower bound 20/s in 4/60.
- VERIFIED. Pulse strategy test E (a) vs primary (b), responded-only: pulse statistic z 1.43 (7/10 same sign), total
  z 0.00 -> not distinguished (ddm/primacy_resp/results_strategy.pkl).
- SUSPECTED. C's advantage on E data comes from its flexibility (sv and the bound absorb what a 5-50 ms leak produces in
  the RT distribution), i.e. hypothesis H5 of the spine; not tested directly.

## What didn't work
- Pre-cap F1a (42451102) was cancelled when degenerate E fits were found (amendment 11); this run uses the capped fits.

## How to reproduce
Hyak 42489714: `model_recovery --responded_only --strategy --fits_dir ddm/fits_resp_final ddm/fits_resp_fast_only_leak20-200_cap
--out_dir ddm/recovery_strategy_resp_cap` (80 jobs, code 40dc38e). Scoring: inline pandas pivot of test_nll by
(generator, mouse, replicate), E fit minus C fit, thresholds +-10 (session transcript 2026-10-27). Inputs sha256
1a6c88ec...69980.

## Caveats
- 20 datasets; k = 5 is at the rule's boundary between B-rate (3-4) and B (>= 5). One dataset either way changes the
  wording, not the conclusion that the comparison is imperfect.
- Generating parameters are the real-data E control fits, several with leak near its lower bound (time constants ~30-50 ms).

## Open questions and next steps
- [ ] Author: G1_v3 decision 1 (thesis variants and rule) is still open; the rule now selects THESIS_B. Record k in
      decisions.md and swap the THESIS line at lock (`np.py lock-spine`).
- [ ] Report with the Stine-exact models (ESx/DDMx, amendment 13) when the DDMx refit recovery (42497999) lands.
