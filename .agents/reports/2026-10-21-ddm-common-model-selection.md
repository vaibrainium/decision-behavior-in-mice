# Report: DDM warm-start refits, guess forms and Monte Carlo noise (next-steps plan steps 1, 2, 3.1)
Date: 2026-10-21   Agent: Claude (Opus 5.5)   Commit: 2954fad
Plan: dissemination/reports/mouse-ddm-next-steps.md (steps 1–3)

## Question
Once optimizer failures are fixed and the comparison noise is measured, which mechanisms belong in the common DDM, and
which guess/lapse form?

## Summary
Warm starts removed the optimizer failures. With measured noise, sv and fast guesses clearly improve held-out fit in
most mice; sz does not. Leak and urgency help only in the 3–4 mice with the most trials, so they fail parsimony rule 2
as written. The fast-only guess form (guess delay ≤ 0.3 s) is the best-supported guess form. The common model is not
chosen yet: the authors have to decide between strict rule 2 (L0U0V1Z0G1, fast-only guesses) and keeping leak and
urgency.

## Findings
- VERIFIED: merged fits_guess + fits_guess_warm (2,240 fits): largest nested-pair violation 5.9 NLL; 12 fits at 5–5.9,
  none > 20. Source: `compare_models --fits_dir ddm/fits_guess ddm/fits_guess_warm`, `find_refits` with the same dirs.
- VERIFIED: leading model by summed held-out NLL is still L1U1V1Z0G1; +sz is +16.7, L1U0V1Z1G1 is +16.8. RFX-BMS omnibus
  risk 0.72; family pxp sv 0.87, leak 0.75, guess 0.66, urgency 0.60, sz 0.40.
- VERIFIED: rescoring reproduced the saved test_nll in 350/350 folds. SD of a model difference across seeds, per mouse:
  median 6.5–12.8 NLL (15 reps), 4.1–5.9 (50 reps); summed 22–54 / 13–21. Source: `mc_noise --summarize`,
  `ddm/mc_noise/mc_noise_summary.csv`.
- VERIFIED: per-mouse cost of removing each mechanism (mean of 10 seeds × 50 reps, > 2 SE): sv 9/10 mice (+422 summed),
  guess 7/10 (+443), leak 4/10 (+93), urgency 3/10 (+99); +sz 2 for / 2 against (+10). Source:
  `ddm/mc_noise/mc_noise_per_mouse.csv`. These use the original fits; warm refits can only shrink the leak and urgency
  counts.
- VERIFIED: guess forms on L1U1V1Z0G1, held-out NLL vs single form: fast_only −69.9 (better in 9/10), guess_lapse
  −83.5, no guesses +377.1; p_lapse ≤ 0.015 in 8/10 mice. Source: `python -m scripts.ddm.compare_guess_forms`.
- VERIFIED: the psychometric asymptote implies lapses of 16–53% (9–47% at RT ≥ 0.6 s) at 100% coherence, far above the
  fitted uniform-RT lapse.
- SUSPECTED: high-coherence errors are absorbed by sv. Not checked against model predictions yet.
- SUSPECTED: the fast_only fits of DBM14 and DBM15 (drift_gain ≈ 0.9, bound ≈ 2) are a different solution regime;
  check their fit quality.

## What didn't work
- `mc_noise --summarize` failed locally: the pickles were written under NumPy 2 on Hyak and the local venv has NumPy
  1.26. Fixed with a remapping unpickler (no package change).
- Dividing the 15-rep deltas by the 50-rep noise SD is inconsistent (mixed noise levels); use either the 15-rep pair or
  the 10-seed 50-rep means.

## How to reproduce
On the NAS copy (`/mnt/data/processed/ddm`, synced from Hyak 2026-10-21), from the repo root with `.venv/bin/python`:
`-m scripts.ddm.compare_models --fits_dir ddm/fits_guess ddm/fits_guess_warm`; `-m scripts.ddm.find_refits --fits_dir
ddm/fits_guess ddm/fits_guess_warm`; `-m scripts.ddm.mc_noise --summarize`; `-m scripts.ddm.compare_guess_forms`.

## Caveats
- 10 mice with 497–7,458 trials; "most mice" is power-limited: in the four mice under 1,000 trials no mechanism except
  sv is detectable.
- The noise estimate covers evaluation noise only, not optimizer variability between refits.
- The guess-form comparison was made on L1U1V1Z0G1; if the common model drops leak and urgency it should be confirmed on
  that model.

## Open questions and next steps
- [ ] Authors: common model, strict rule 2 (L0U0V1Z0G1 + fast_only) or with leak and urgency.
- [ ] Fit the chosen model with fast_only, with guess_bias free and fixed at 0.5 (rule 3); needs a fixed-bias option
      in `fit_mouse_ddm.py`.
- [ ] Fit-quality plots of the chosen model (accuracy at 100% coherence; DBM14/DBM15 regime).
- [ ] Step 3.3 control-only CV check of the choice, then model recovery (set `COMMON` in `model_recovery.py`).
