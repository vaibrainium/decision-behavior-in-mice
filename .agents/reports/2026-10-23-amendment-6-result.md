# Report: amendment 6 (pulse gain) result and calibration; primacy question not answerable with this design
Date: 2026-10-23   Agent: Claude (Opus 5.5)   Commit: see the commit adding this report
Plan: plans/2026-10-23-amendment-6-pulse-gain.md

## Question
After the original gate failed, does a per-mouse pulse gain (cross-validated) give a model that predicts pulse trials,
and could the timing test detect primacy if present?

## Summary
No to both. The revised gate fails for both baselines (departure +0.24 / +0.31 logit). The calibration shows the
procedure is valid under the null, but the timing test detects 0–5% of datasets with 10–40% primacy. Per amendment 6
item 8, the timing test is not run and no further revision is made. The data show a between-mouse-variable excess
pulse sensitivity, not an answer about primacy.

## Findings
- VERIFIED: pulse gains 0.06–7 (primary); revised gate +0.24 (0.09, 0.37) vs predicted 0.057; RT check 62% inside.
  Source: `ddm/primacy_revised/`, analysis log 5.11.
- VERIFIED: calibration (20 datasets per level): gate pass 0.95 / 0.70 / 0.35 / 0.05; detection 0 / 0 / 0.05 / 0;
  false positives 0/20 (UW late 1/20); mean β_middle ~0 (SD 0.05–0.06).
- SUSPECTED: on pulse trials, choices follow coherence more steeply than predicted (with +0.25 to +0.35; against at 36%
  −0.18), and the RT-sensitive likelihood keeps the gain from matching the choice effect.

## Caveats
- Calibration holds the control fits fixed (by design); gate-pass rates under decay are partly a construction effect.
- Gain intervals are coarse (evaluated grid points).
- Location is not analysed separately (site confounded with cohort; standing decision).

## Next steps
- [ ] Paper: R5 becomes "pulse sensitivity exceeds motion-energy prediction; primacy not resolvable with these pulses"
      (outline outcome a2/b), with the calibration as the power statement.
