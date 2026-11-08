# Report: ES recovery (partial) and nominal-coherence refits
Date: 2026-10-30   Agent: Claude (Opus 5.5)   Commit: 04959ce (+ uncommitted edits to control_heldout.py, recovery_cohorts.py)
Plan: plans/2026-10-29-control-paper.md (steps 3, 3b, 3c)

## Question
(1) With ES added, does the recovery separate E and ES (D004 rule)? (2) Does net motion energy predict held-out control
behavior better than nominal coherence (plan 3c rule)?

## Summary
E is separated, now with Holm over all 4 alternatives: 0/1,024 E-generated cohorts and 1,024/1,024 C-generated cohorts
reproduce C > E. ES is NOT decided. The 100 jobs on ES-generated data (job 42590287, array indices 40-89, 130-179)
produced no output, most likely because the ES datasets were not on Hyak. Only the C-generated half of the ES criterion
is known (1.000). Motion energy does not predict better than nominal coherence for any model, but the ranking C > E,
ES holds on nominal input.

## Findings
- VERIFIED. Recovery outputs: 400 of 500 (all fits on ES-generated data missing); 80 datasets, paired, datasets_dir
  set, NLL finite. Source: `python -m scripts.ddm.recovery_cohorts --suffix _v2`; tables recovery_*_2026-10-30_v2.csv.
- VERIFIED. Share of cohorts that reproduce C > X (Holm-4): X = E: C-gen 1.000, E-gen 0.000, DDMx-gen 0.085,
  ESx-gen 0 -> E separated (final). X = ES: C-gen 1.000, E-gen 0.000, DDMx-gen 0, ESx-gen 0; ES-gen missing.
  X = ESx: E-gen 0.767 (DDMx, ESx comparisons not diagnostic, as before).
- VERIFIED. Best held-out candidate per dataset: C-generated 19/20 C (1 ES); E-generated 10 E, 6 ES, 2 C, 2 ESx
  (E and ES confuse each other); DDMx 13/20; ESx 10/20 (4 DDMx, 4 ES).
- VERIFIED. Nominal minus motion-energy held-out NLL per 1,000 control trials (> 0: ME better), 10 mice, Holm over 3:
  C +0.96 (t p 0.60, Holm 0.60; Wilcoxon 0.92), E +3.84 (Holm 0.26), ES -7.51 (t p 0.059, Holm 0.18; Wilcoxon 0.037,
  Holm 0.11). Source: `python -m scripts.ddm.control_heldout --nominal`; tables heldout_nominal_{per_mouse,group}_2026-10-30.csv.
- VERIFIED. On nominal input, C still beats E: +15.6 (Holm-2 t 0.006, Wilcoxon 0.012, dz 1.27); and ES: +10.3
  (t Holm 0.048, Wilcoxon 0.065, dz 0.72).

## What didn't work
- ES-generated recovery jobs: no output (cause not checked on Hyak; SSH needs interactive login here).

## How to reproduce
`.venv/bin/python -m scripts.ddm.recovery_cohorts --suffix _v2`; `.venv/bin/python -m scripts.ddm.control_heldout --nominal`.
Fits: processed/ddm/recovery_full_cpu_resp (42579825 + 42590287 partial), fits_resp_nominal_matched_{C,E,ES}
(42590292, 42590294, 42590301).

## Caveats
- Thesis "of net motion energy" stays as a description of the model input (D004 item 2). Data give no evidence that
  ME beats nominal coherence, so the text must not imply it.
- The nominal refits keep z free (nominal_matched); the ME fits are the existing ones.

## Open questions and next steps
- [ ] Author: check the Slurm logs for 42590287 (indices 40-89, 130-179); rsync the datasets; resubmit those 100.
- [ ] Rerun recovery_cohorts (new suffix) -> final variant A or I_E; log in decisions.md.
