# Report: paired model recovery (job 42579825), cohort-level test for the control paper
Date: 2026-10-30   Agent: Claude (Opus 5.5)   Commit: 57a47c0 (+ script commit below)
Plan: plans/2026-10-29-control-paper.md (step 3b; rule D004, approved at G1 before any recovery likelihood was read)

## Question
If mice used rapid forgetting (E) or the paper-exact Stine models (DDMx, ESx), would the real Fig 3 result (common
model C beats each alternative over 10 mice) still come out? This is the THESIS selection rule from G1.

## Summary
The 320 paired fits are valid: complete, all on the same CPU datasets, with equal train/test splits per dataset. **E is
separated.** No E-generated cohort reproduces "C beats E" (0/1,024), and every C-generated cohort does (1,024/1,024).
Bonferroni x4 and Holm over the 3 available alternatives agree. ES is not decided yet, because the ES fits (180 jobs)
have not been submitted. The thesis variant is therefore I_E or A, never B. **PROVISIONAL** until ES is in.

## Findings
Source: `python -m scripts.ddm.recovery_cohorts`; tables
`dissemination/paper_control/tables/recovery_{cohorts,cohort_rates,per_dataset,confusion}_2026-10-30.csv`.
d = (NLL_X - NLL_C) / n_test * 1000 per dataset (one held-out split; 20 datasets per generator = 10 mice x 2).
- VERIFIED. Validity: 320 outputs, 16 cells x 20, 80 datasets, `datasets_dir` set in all, no train/test mismatch,
  all NLL finite.
- VERIFIED. Share of 1,024 cohorts that reproduce "C beats X" (Holm-3 / Bonferroni-4):
  - X = E: C-generated 1.000 / 1.000; E-generated 0.000 / 0.000; DDMx-generated 0.151 / 0.063; ESx-generated 0 / 0.
    -> **E separated** (rule: <= 0.10 and >= 0.50).
  - X = DDMx: C-generated 1.0; E-generated 1.0. X = ESx: C-generated 1.0; E-generated 0.908 / 0.623.
    Not decisive (D004), but the "C beats DDMx / ESx" result also appears when E generates the data, so those two
    comparisons do not show integration. They only show that the paper-exact models (no sv, no guesses) fit worse.
- VERIFIED. Per dataset (> 10 NLL), E vs C: C-generated 15/20 favor C (CP 95% CI 0.51-0.91), 0/20 favor E;
  E-generated 9/20 favor E (0.23-0.68), 0/20 favor C. Mean d: C-generated +31.1, E-generated -10.8 per 1,000.
- VERIFIED. Best held-out candidate per dataset (row generator): C 19/20 correct (1 E); E 15/20 (3 C, 2 ESx);
  DDMx 14/20 (4 ESx, 2 C); ESx 13/20 (4 DDMx, 2 E, 1 C). DDMx and ESx confuse with each other, as in Stine 2020.
- OBSERVATION (not part of the rule). Real data C vs E is +12.8 per 1,000 (5-fold; heldout_group_2026-10-29), which is
  between the E-generated (-10.8) and C-generated (+31.1) means. The units match (per 1,000 held-out trials), but the
  CV schemes differ, so this is not a formal test.

## What didn't work
- Nothing failed. The earlier unpaired F1a result (k = 5/20 E-generated scored as accumulator) is superseded. Here 3/20
  E-generated datasets are best fit by C, but none by more than 10 NLL.

## How to reproduce
`cd /src && .venv/bin/python -m scripts.ddm.recovery_cohorts` (CPU, < 1 min). Inputs:
`processed/ddm/recovery_full_cpu_resp/*.pkl` (Slurm 42579825, synced 2026-10-29); datasets
`processed/ddm/recovery_datasets_cpu_2026-10-29` (sha256 manifest).

## Caveats
- The 1,024 cohorts reuse 20 datasets per generator, so they are not independent. The rates show how reproducible the
  group test is; they are not p values.
- The fits use one train/test split per dataset, not the 5-fold CV of the real comparison.
- Generators use each mouse's fitted parameters. Recovery is only as good as those fits (e.g. E's leak range 20-200/s).
- Holm over 4 needs the ES fits. The E verdict holds under the conservative Bonferroni x4, so ES cannot overturn it.

## Open questions and next steps
- [ ] Author: rsync the datasets (20 ES added), git pull on Hyak, submit the ES cells (180), and then rerun this script.
  The final variant (A or I_E) depends on ES.
- [ ] Add N-rows for C010-C012 once ES is final; update the THESIS selection in decisions.md.
- [ ] Nominal-coherence refits (150) still to submit (plan 3c).
