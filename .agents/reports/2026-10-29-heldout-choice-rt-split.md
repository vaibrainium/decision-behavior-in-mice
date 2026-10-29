# Report: held-out comparison reproduced, split into choice and RT parts, leave-one-mouse-out
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: 21d3690 (+ table commit)
Plan: plans/2026-10-29-control-paper.md (D003; steps 3d)

## Question
Where does the common model's held-out advantage on control trials come from (choice vs RT terms), and does it depend
on any one mouse? Also: restore provenance of the held-out table used by the thesis.

## Summary
`scripts/ddm/control_heldout.py` reproduces paper_accumulation heldout_per_trial_2026-10-28 exactly. The common model's
advantage is mostly in the RT terms. Against ES, ESx and DDMx the choice part is about 0 and not significant. Against
rapid forgetting (E) there is a small, consistent choice advantage (2.5 per 1,000 trials, positive in 10/10 mice). The
group results survive dropping any one mouse.

## Findings
Units: held-out NLL per 1,000 control trials, alternative minus C (> 0: C better); mice as unit; Holm over the 4
alternatives within each part. Source: dissemination/paper_control/tables/heldout_group_2026-10-29.csv,
heldout_diff_per_mouse_2026-10-29.csv; command `python -m scripts.ddm.control_heldout --split`.
- VERIFIED. Total: E 12.8 (t Holm 0.037, W Holm 0.059), ES 18.7 (0.023/0.055), DDMx 28.2 (0.037/0.059),
  ESx 30.2 (0.037/0.059). Identical to the 2026-10-28 table (max |diff| 0.00). Re-scored NLL equals stored test_nll
  (max |diff| 0.01).
- VERIFIED. Choice part: E 2.5 [min 0.7, max 4.8] (t Holm 0.002, W Holm 0.008, dz 1.73); ES 1.2 (Holm 1.0); DDMx 3.6
  (Holm 0.34); ESx 0.1 (Holm 1.0).
- VERIFIED. RT part: E 10.2 (t Holm 0.048, W Holm 0.082); ES 17.5 (0.009/0.008, dz 1.33); DDMx 24.6 (0.033/0.082);
  ESx 30.1 (0.033/0.082).
- VERIFIED. Leave-one-mouse-out (total): mean stays > 0 for every alternative; max uncorrected p_t 0.037, Wilcoxon
  0.074 (tables/heldout_lomo_2026-10-29.csv).

## What didn't work
- n/a

## How to reproduce
`cd /src && .venv/bin/python -m scripts.ddm.control_heldout --split` (CPU, about 10 min). CV fits: fits_resp_fast_only (C),
fits_resp_fast_only_leak20-200_cap (E), fits_resp_fast_only_es_cap (ES), fits_resp_nominal_ddm_g001 (DDMx),
fits_resp_nominal_es (ESx).

## Caveats
- The choice part is per-condition choice proportions: it is not trial-level use of motion energy.
- In small mice (PSUIM10, about 52 test trials per fold) the RT term often drops out (fewer than 9 trials per
  condition x choice), so their difference is mostly the choice part.
- The C CV fits predate the 50% cap code. The alternatives' "_cap" fits had it. C's fits need not have hit the cap
  (NOT CHECKED).

## Open questions and next steps
- [ ] Thesis wording: the advantage over the matched extrema model is an RT-distribution result (H0b in the spine).
- [ ] Check that C's CV fits respect the 50% cap (simulated non-response share at the fitted parameters).
