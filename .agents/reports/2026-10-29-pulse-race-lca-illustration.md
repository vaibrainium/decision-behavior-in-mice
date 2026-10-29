# Report: race and LCA variants vs the pulse signatures (illustration)
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: e50f047 (+ this commit)
Plan: plans/2026-10-29-pulse-weight-joint.md (step 5)

## Question
Author: "would race type of model work better?", "should we also test LCA families?", plus the paper Kirkpatrick,
Turner & Sederberg 2021 (Psychol Rev 128:1051; LCA best in 36/39 humans, incl. vs a DDM-like model with BTV).
Can partially dependent (LCA) or independent (race) accumulation reproduce the pulse effect where the DDM fails?

## Summary
No. Matched to control trials in PSUIM6, PSUIM7 and DBM6, every race and LCA variant predicts 2.7-5.1 pp in the
0.3-1.2 s window, against 13.1 pp in these mice; none predicts the late reversal (none has sv). LCAs move the
toward-pulse RT shift from -34 to -45...-69 ms (data -166) and fit control trials worse than the DDM limit in 2 of 3
mice. Architecture does not fix the size problem. This is an illustration with coarse matching (bound and gain only),
not a fit; confidence moderate.

## Findings
- VERIFIED: LCA kernel equals the simulator kernel in the DDM limit (rho -1, k = beta = 0, no floor, z 0.5,
  a = 4 theta): 2000/2000 trials identical in each mouse.
- VERIFIED, means over the 3 mice (data: 13.05 / -1.39 pp, RT shift -166 ms):
  | variant | 0.3-1.2 s | 1.2-5 s | toward RT shift (ms) |
  |---|---|---|---|
  | DDM limit (no sv) | 4.33 | 0.97 | -34 |
  | race rho -0.5 / 0 | 4.22 / 4.63 | 1.18 / 1.67 | -29 / -24 |
  | LCA k=beta=3 | 3.93 | 0.12 | -69 |
  | LCA leak-dominant k6 b1 | 2.71 | 0.09 | -50 |
  | LCA inhibition-dominant k1 b6 | 4.43 | 0.15 | -66 |
  | LCA + baseline k=beta=3 | 5.07 | 0.90 | -45 |
  | LCA + baseline k4.5 b5.4 (KTS 2021) | 4.77 | 1.68 | -27 |
  Source: scripts/ddm/pulse_lca_signatures.py -> dissemination/figures/qc/pulse_lca_signatures_2026-10-29{.png,
  _windows.csv,_stage.csv,_match.csv}.
- VERIFIED: matched control NLL minus the DDM limit: LCAs +30 to +308 in PSUIM6 and DBM6; in PSUIM7 the floored LCAs
  without baseline are better (-74, -75), with baseline worse (+187, +199). Races within 2 NLL at rho -0.5.
- VERIFIED: models predict a flat effect across pulse times (inhibition-dominant LCA included: no primacy). Data per
  pulse time: PSUIM6 9.3 / 6.4, PSUIM7 12.8 / 8.4 (early / middle), DBM6 0.7 / 2.5 / 3.1 pp; the panel-C mean at
  "late" is DBM6 only.

## What didn't work
- First run printed the per-stage effect x100 (effect() already returns pp); fixed before this run; CSVs were right.

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_lca_signatures` (36 min, 32 CPU threads; `--check_only` for the DDM-limit check).
Base parameters: fits_joint_unfreeze_integrators/<mouse>_L0U0V1Z0G1_all.pkl (ndt, guesses, offset/gain).

## Caveats
- Only theta and gain matched (grid 7x7 + refine, 6 reps); leak, inhibition, rho, baseline fixed per variant. A full
  LCA fit could do better on control trials; it is unlikely to change a 3x gap in pulse effect size, but unverified.
- 3 mice. Input is the opponent (right - left) motion energy; the paper's two-channel input (separate E_R, E_L) is not
  stored (me_calibrated.npz holds the difference only; SpatioTemporalFilter computes both).
- Our likelihood is quantile-based (9 bins); KTS 2021 argue quantiles are not sufficient statistics.

## Open questions and next steps
- [ ] Hyak pulse-weight fits (job 42579333): does a free pulse weight close the size gap without breaking RTs?
- [ ] Only if LCA is pursued: recompute motion energy keeping E_R and E_L (local, ~20-30 min) for a two-input LCA.
