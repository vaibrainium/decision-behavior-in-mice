# Report: urgency-gating (UGM) region of leak + urgency
Date: 2026-11-11   Agent: Claude (Opus 5.5)   Commit: 816ca21 (+ this report's commit)
Plan: plans/2026-11-10-ugm-corner-leak-urgency.md

## Question
Can the parameter region of L1U1 that corresponds to Cisek et al. 2009's urgency-gating model (strong low-pass filter,
leak 4-10 /s = tau 100-250 ms, with strong urgency) fit the data and the pulse? EXPLORATORY. Criteria confirmed by the
author 2026-11-11 before the comparison was run: viable for a mouse if (1) held-out NLL is within 10 of the best
standard integrator for that mouse (same input, same CV splits) and (2) the family's pulse profile has no late reversal
outside the data CI.

## Summary
- Given leak 2-20 /s and urgency 0-50 /s, the fits leave the UGM corner: 0 of 120 full-data fits are in it (leak 4-10
  and urgency >= 1); 14 of 720 fits are, all pulse-only CV folds, 9 of them PSUIM10 (fewest trials). Fits sit at
  the edge nearest the standard model (median tau 400-495 ms, median urgency 0.00-0.71 /s).
- So the criteria end up testing that edge, not the corner itself. On it: with sv, NLL within 10 of the best
  integrator in 5-7/10 mice, but every with-sv family has a late reversal outside the data CI (criterion 2 fails).
  Without sv, the late window is inside the CI but NLL is within 10 in only 3/10 mice (joint) or 6-7/10 (pulse-only).
- No UGM family passes both criteria in most mice; the corner proper is ruled out to the extent the optimizer's
  avoidance shows (moderately confident: it is not a profile likelihood over the corner).

## Findings
1. VERIFIED, fits valid (plan log 2026-11-11): 720/720, all converged, none at max iterations; no fit near drift_gain 50
   or a 9.5. Rescoring 3 fits with make_model(ugm=True) reproduces the stored test NLL (diff <= 0.08), incl. PSUIM10
   pulse linear (leak 11.0, urgency 49.3).
2. VERIFIED, where the fits sit (ugm_params_2026-11-11.csv; plan log step 5): full-data fits in the corner 0/120;
   all 720 fits: leak <= 2.18 /s in 388, urgency <= 0.5 /s in 571; corner 14/720.
3. VERIFIED, held-out NLL (ugm_nll_summary_2026-11-11.csv, ugm_nll_per_mouse_2026-11-11.csv; compare_ugm.py; same
   trials checked by n_test). UGM minus best standard integrator per mouse, summed over 10 mice / mice within 10:
   - joint, with sv: linear +116 (5/10), power +98 (7/10), norm +93 (7/10); vs the standard L1U1V1 of the same input
     +70 / +65 / +49 (worse by > 10 in 3 mice each; better by > 10 in 0 / 0 / 1).
   - joint, no sv: linear +574, power +619, norm +197 (3/10 each; PSUIM6 and PSUIM7 carry most: up to +329).
   - pulse-only: linear +106 (6/10) and +166 no sv (7/10); power +51 (7/10) and +184 no sv (6/10).
   - pulse-only norm: no standard pulse-only norm fit; held-out 16,931 (sv), 16,890 (no sv), not compared.
4. VERIFIED, pulse effect (pulse_effect_bootstrap_2026-11-11_ugm_models.csv; data mean early 5.48 [3.17, 7.87], late
   1.22 [-1.02, 3.36], trial bootstrap):
   - with sv (6 families): late -2.3 to -3.1, outside the data CI in all 6 (criterion 2 fails); early 3.5-4.3,
     chi-square over mice 107-138.
   - no sv (6 families): late +0.33 to +0.69, inside the CI; early 3.4-6.0. Per-mouse early chi-square 44.7
     (pulse norm) and 51.3 (joint norm), lower than the other no-sv UGM families (81-101) and all earlier families (91-143) but still
     well above 10 df.
5. Combined (criterion 1 per mouse, criterion 2 per family): only no-sv families pass criterion 2, and they pass
   criterion 1 in 3/10 (joint) or 6-7/10 (pulse-only linear/power) mice, at parameters off the UGM corner
   (only PSUIM10 pulse-only fits have strong urgency).

## What didn't work
- Nothing failed. The criteria, applied to free fits, test where the optimizer landed (mostly the region edge), not
  the corner; a fixed-parameter profile over (leak, urgency) would test the corner directly.

## How to reproduce
- `python -m scripts.ddm.compare_ugm` (NLL, parameters).
- `python -m scripts.ddm.pulse_joint_signatures --cache <sig cache> --tag _ugm_part{0,1,2} --families <4 UGM families
  each>`; `python -m scripts.ddm.pulse_effect_bootstrap --runs pulse_joint_signatures_2026-11-11_ugm_part{0,1,2} --tag _ugm`.
- `python -m scripts.ddm.build_fit_browser --cache <sim cache> --tag _v5 --html <out>` (fit_browser_2026-11-11_v5.json;
  artifact version 6; earlier families byte-identical in JSON).
- Families registered in pulse_joint_signatures.UGM_FAMILIES / UGM_PULSE_FAMILIES; primacy.make_model takes ugm.

## Caveats
- "Best integrator" is the minimum over 4-8 standard variants per mouse, which favours the reference by selection.
- The best standard set differs by input (linear joint includes no-sv; power/norm joint do not; pulse-only has 8).
- One fit per mouse and split; DE may miss a corner optimum, though the bounds included it and 14 folds found it.
- 10 mice; small mice (PSUIM10) dominate the corner fits.

## Open questions and next steps
- [ ] To test the corner itself: fix (leak, urgency) on a grid inside it (e.g. leak 4, 7, 10 x urgency 5, 20, 50),
      fit the rest, compare NLL (needs Hyak fits; author's call).
- [ ] The no-sv normalization fits give the smallest per-mouse early spread yet (chi-square 45-51): look at which
      mice it fits and why, alongside the across-trial variability question in reports/2026-11-11-pulse-only-fits.md.
