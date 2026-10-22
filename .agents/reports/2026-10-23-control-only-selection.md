# Report: control-only model selection (next-steps step 3.3)
Date: 2026-10-23   Agent: Claude (Opus 5.5)   Commit: see git log (this report's commit)
Plan: dissemination/reports/mouse-ddm-next-steps.md step 3.3

## Question
Does the strict common model (L0U0V1Z0G1, fast-only guesses) still win when model selection uses control trials only?

## Summary
Yes. sv and guesses are needed (8/10 and 7/10 mice by > 10 held-out NLL); leak and urgency are not (summed −21 / +26;
only PSUIM6 benefits). Part of the leak/urgency gain seen on all trials (PSUIM5, PSUIM7) came from pulse trials.

## Findings
- VERIFIED: summed held-out NLL change vs strict: − sv +1,017.8; − guess +858.1; + leak −21.3; + urgency +25.8;
  + leak + urgency −33.3. Source: `ddm/fits_guess_fast_only/*_ccv*.pkl` (300 fits, jobs 42134146).
- VERIFIED: nested pairs, larger model worse by > 5 NLL in 4/300 (max 11.2).
- VERIFIED: batches 1 and 3b produced no fast-only fits (`$W` empty); 400 recovery tasks stopped at the guard.

## Caveats
- No warm starts for ccv splits (slight bias against the larger models).
- Control-only folds have fewer trials than the all-trial folds; the > 10 NLL threshold is approximate (Monte Carlo
  SD per mouse 6.5–12.8 on all-trial folds).

## Next steps
- [ ] User resubmits batches 1, 3b and recovery (bash, `$W` checked).
- [ ] Then: free vs fixed guess bias, fit quality, predictive-check first pass, recovery analysis.
