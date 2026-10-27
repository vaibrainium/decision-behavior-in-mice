# Report: pulse directional contrasts without the 4,537 no-response-by-5 s trials
Date: 2026-10-27   Agent: Claude (Opus 5.5)   Commit: 18d0d4a (working tree has src-85's uncommitted refit edits; not used)
Plan: none (read-only recomputation from frozen package-C outputs; author rule: exclude-no-response-trials)

## Question
How much do the behavioural pulse results change if trials without a response by 5 s (435 no RT, 4,102 RT > 5 s;
response_side == "none" in the frozen trial table, exactly 4,537) are removed?

## Summary
They hold and get slightly larger. Positive vs negative pulse: 5.84 pp [1.80, 9.89] -> 7.52 pp [2.73, 12.30],
p 0.0097 -> 0.0062 (Holm over the 3 contrasts: 0.019 -> 0.012). The pulse does not significantly change the
response rate (+2.07 pp, p = 0.086), so conditioning on responding is unlikely to drive the effect. Model fits,
gates and calibration are not covered here (refits needed; src-85 owns the refits).

## Findings (all VERIFIED; source: /mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/behaviour/cells.csv, group.csv)
Responder-only estimand: per cell, P(R | responded, arm a) - P(R | responded, arm b); cell weight min(responders a,
responders b), normalized within mouse; cells need >= 1 responder per arm; group = mean over 10 mice, t-test across
mice (df 9). Primary set |coh| <= 36.
| Contrast | Original Delta_direction (all trials) | Responders only |
|---|---|---|
| positive vs negative | 5.84 [1.80, 9.89], p = 0.0097 | 7.52 [2.73, 12.30], p = 0.0062, dz = 1.12 |
| positive vs control | 4.86 [2.43, 7.29], p = 0.0014 | 6.08 [3.20, 8.96], p = 0.0010 |
| control vs negative | 1.40 [-2.13, 4.92], p = 0.39 | 1.59 [-2.16, 5.34], p = 0.36 |
Holm (3 contrasts, responders): 0.0030, 0.012, 0.36.
- The package's own pre-declared secondary (secondary_responder_only.csv; weights = all-trial min, renormalized) gives
  7.26 pp [2.49, 12.02], p = 0.0073. It agrees.
- Per mouse (responder weights, pp): DBM12 -3.13, DBM13 0.79, DBM14 1.32, DBM15 8.94, DBM5 5.63, DBM6 5.61,
  PSUIM10 14.96, PSUIM5 9.67, PSUIM6 14.34, PSUIM7 17.02. 8,550 responder trials in the positive-vs-negative cells.
- Pulse effect on non-response (positive - negative, original package C): +2.07 pp [-0.36, 4.49], p = 0.086.
- The scale is comparable: Delta_direction = (dR - dL)/2 equals dP(R) when every trial is answered.

## Caveats
- The original estimand counted non-response as an outcome. The responder estimand conditions on a post-pulse outcome
  (selection caveat stated in behaviour.py C3); the non-significant response-rate effect limits but does not remove it.
- Only the existing cells are reused; cell definitions and the support rule are not re-derived from a responders-only
  contract.
- Not recomputed: pulse-aligned cumulative response curves (response_time report), whose denominators include
  non-responders.

## Still including these trials (need redoing or flagging)
- All DDM fits (censored QMLE counts them as "no response by 5 s"): src-85 is refitting with --responded_only.
- Closed primacy pipeline (gates, calibration, pulse gain, amendment 6/7 selections) and the 2026-10-25 fluctuation
  power checks (they used the censored-fit parameters).

## How to reproduce
Inline Python on cells.csv (filter analysis_set == primary_coherence and the contrast; formulas above); the command
is in the 2026-10-27 session transcript.
