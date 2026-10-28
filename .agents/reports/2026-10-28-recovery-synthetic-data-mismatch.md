# Report: recovery candidates were not scored on the same synthetic data (GPU-dependent synthesis)
Date: 2026-10-28   Agent: Claude (Opus 5.5)   Commit: d7c96ef
Plan: plans/2026-10-28-full-recovery-matrix.md

## Question
Before building the 4x4 recovery matrix (amendment 14): do all candidates fitted to one (mouse, generator, replicate)
dataset see the same synthetic train and test trials, as model_recovery.py assumes (seed = crc32(mouse|generator|rep))?

## Summary
No. Within one dataset, the number of responded synthetic trials (n_train / n_test) differs between candidates in many
datasets, so their held-out NLLs come from different trials and the "C - E" style differences that recovery is scored on
are not paired. This affects the full matrix and the existing pairwise recoveries, including F1a k = 5/20 (THESIS_B under
D002) and the ESx/DDMx and ES recoveries. Those results should be treated as invalid until rerun on fixed datasets.
Likely cause (SUSPECTED): synthesis runs on the GPU (torch.randn), whose draws for a given seed depend on the GPU model;
jobs ran on mixed hardware (A100 lab pool and ckpt-all).

## Findings
- VERIFIED. Datasets in which the candidates saw different n_train/n_test (a lower bound: equal counts do not prove
  equal data). Source: the pickles in /mnt/data/processed/ddm/recovery_*; script
  scratchpad xm/combine.py plus an inline groupby (session 2026-10-28).
  - recovery_strategy_resp_cap (F1a, C/E): 22 of 40.
  - recovery_strategy_es_resp_cap (ES): 21 of 40.
  - recovery_exact2_resp (DDMx/ESx): 4 of 40.
  - recovery_cross_resp (new, 160 fits): 0 of 80 within the folder.
  - Combined across folders: 63 of 80 datasets.
- VERIFIED. Size of the differences: for example, DBM12 E-generated rep0 has n_test 760 for candidate C and 771 for
  candidate E. Held-out NLL is about 3 per trial (DBM12 2303.7 / 784), so 11 trials is about 30 NLL. That is of the
  order of the 10-NLL decision threshold before any difference in the noise draws themselves.
- VERIFIED. CPU synthesis (Numba backend, NumPy seed) is reproducible. Two separate processes gave identical sha256 for
  DBM12, generators C and ESx (scratchpad xm/det.py).
- SUSPECTED. The cause is GPU-model dependence of CUDA random draws: PyTorch sizes its random kernels by the SM count.
  This is not checked against node lists. `sacct -j <ids> --format=JobID,NodeList` would confirm it.

## What didn't work
- The 4x4 matrix was computed (scratchpad xm/recovery_confusion.csv), but it is not valid because the cells are not
  paired. It is not reported or put on the dashboard.

## How to reproduce
`.venv/bin/python <scratchpad>/xm/combine.py <outdir>` prints the counts. `det.py` is the determinism check.

## Caveats
- The F1a "5 are genuine" check compared C's held-out NLL with E's at its true parameters. These were computed on
  different test sets whenever the counts differ, so that check is also affected.
- Results that use the real data (real-data comparisons, D006/D007 held-out numbers) are not affected.

## Open questions and next steps
- [ ] Generate the 80 datasets once on CPU and save them with sha256. Then make model_recovery load them
      (`--datasets`) and rerun all 16 cells x 20 datasets (320 fits). Needs the author's OK (cluster job).
- [ ] Until then, F1a k = 5 and THESIS_B under D002 are provisional.
