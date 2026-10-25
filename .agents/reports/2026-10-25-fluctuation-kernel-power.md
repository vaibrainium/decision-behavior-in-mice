# Report: fluctuation-kernel power (synthetic only): primacy no, integrator vs extrema detection yes
Date: 2026-10-25   Agent: Claude (Opus 5.5)   Commit: ddc9993 (+ resp_power mode, this commit)
Plan: plans/2026-10-25-fluctuation-kernel-power.md

## Question
Can reverse correlation of choices on within-trial motion-energy fluctuations (control trials, |coh| <= 36%) detect
(a) primacy (drift-gain decay), (b) integration vs extrema detection, with these trial counts? No recorded choices used.

## Summary
(a) No. 40% gain decay moves the stimulus-aligned primacy index by ~0.1 % coh against a per-dataset SD of ~0.6; group
detection 0-5%. (b) Yes at the group level. A response-aligned late-weight index classifies 20/20 integrator and
20/20 extrema-detection datasets correctly (criterion >= 90%). Per mouse, only PSUIM6/7 (~3,200 trials) are reliably
classified (100%); the others are at 25-90%. Confidence: moderate. See the caveats (no refit; only two candidate models).

## Findings
- VERIFIED: Primacy index (mean over mice): decay 0 -0.081, 20% -0.042, 40% +0.014; detection 0/5/0%; false positives 0%.
  Source: /mnt/data/processed/ddm/fluctuation_kernel_power.csv; `--power --datasets 20 --ref_reps 10`.
- VERIFIED: The stimulus-aligned kernel is only ~0.1-0.4 % coh (fluctuation SD 5-6 % coh); choices carry little
  fluctuation information. Source: the same log.
- VERIFIED: Late-weight index (kernel over -0.2..0 s minus -0.6..-0.4 s before the response), mean over mice:
  integrator +0.22 (SD over datasets 0.26), E -0.71 (0.20). Distance classification correct 100% for both generators.
  The group sign test is significant (> 0) in 10% of integrator datasets and significant (< 0) in 85% of E datasets.
  Use classification, not the sign test. Source: /mnt/data/processed/ddm/fluctuation_kernel_resp_power.csv;
  `--resp_power --datasets 20 --ref_reps 10`.
- VERIFIED: Per-mouse classification (E/I correct): PSUIM6 1.00/1.00, PSUIM7 1.00/1.00, PSUIM5 0.90/0.85, DBM6 0.70/0.85,
  DBM13 0.80/0.75, DBM12 and DBM15 0.70/0.70, PSUIM10 0.55/0.50, DBM14 0.60/0.35, DBM5 0.25/0.60.
  The predictions of the two models nearly coincide in DBM5 and PSUIM10 (I -0.31 vs E -0.51; I -1.13 vs E -0.88).

## What didn't work
- Ratio statistic b = d/c for primacy: unstable with a small reference kernel; replaced before the run.

## How to reproduce
`.venv/bin/python -m scripts.ddm.fluctuation_kernel --power` and `... --resp_power` (defaults: 20 datasets, 10 ref reps), local CPU.
Fits: ddm/fits_final (primary model, control), ddm/fits_guess_fast_only_leak20-200 (E, control).

## Caveats
- Predictions use the generating parameters (no refit per dataset), so power is optimistic. Real-data predictions come
  from fits to the same trials.
- Binary choice between two fitted models. A mouse that fits neither would still be "classified"; amendment 8 needs a
  "neither" check (e.g. the observed index outside both models' simulated ranges).
- RT termination shapes the response-aligned kernel in both models; the test compares models and does not read
  the kernel's raw shape.

## Open questions and next steps
- [ ] Authors decide: draft amendment 8 (response-aligned integrator-vs-E test; primacy stays closed) or stop.
- [ ] If drafted: add a refit-based power check (or a parametric bootstrap with refits) before unblinding.

## Rerun without the 48 mislabelled pulse trials (v2, same day)
Excluded by agg_code from the frozen pulse trial table (37 were in |coh| <= 36; UCLA mice lost 3-19 trials each).
Outputs: /mnt/data/processed/ddm/fluctuation_kernel_power_v2.csv, fluctuation_kernel_resp_power_v2.csv (v1 kept).
- VERIFIED: primacy index -0.127 / -0.077 / -0.052 at decay 0 / 20 / 40%; detection 0 / 0 / 0%. Still no power.
- VERIFIED: late-weight index I +0.24 (SD 0.25), E -0.75 (0.21); classification 20/20 correct for both generators.
  Per mouse (E/I correct): PSUIM7 1.00/1.00, PSUIM6 0.95/0.95, PSUIM5 0.95/0.85; others 0.25-0.85.
- The conclusions are unchanged from v1. The v2 numbers supersede v1 for any later use.
