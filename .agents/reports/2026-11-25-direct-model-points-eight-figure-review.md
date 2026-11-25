# Report: Direct model-point psychometrics and eight-figure review
Date: 2026-11-25   Agent: Codex   Commit: 7aa080c (Figure 3); a68d2f0 (Figure 6)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Remove logistic display fits from DDM/model psychometric overlays and show the current eight figure variants directly for review.

## Summary
Figure 3's model-C psychometric and Figure 6a/6b now show observed probabilities as points with mouse SEM and saved model probabilities as open diamonds connected across tested coherences. No four-parameter logistic display fit is used in those panels. Figure 1 retains its descriptive data-only psychometric curve. The eight-image review assumes Figure 5 and Figure 6 are the two figures with two variations.

## Findings
- VERIFIED Figure 3 direct-point panel contains the archived data and model-C group rows and exports no logistic parameter/curve file. Source: `figure3B_direct_model_points_2026-11-25_v2/psychometric_group.csv`, manifest and script.
- VERIFIED Figure 6a and 6b each export 57 direct model condition/coherence summary points, byte-level table values reproduced from the selected model rows in `group_summaries.csv`; no psychometric display curve/parameter files are produced. Source: `model_display_points.csv` and validation command below.
- VERIFIED all eight selected PNGs exist at approximately 300 dpi. Pixel dimensions and paths are recorded by the validation command and `eight_figure_review_2026-11-25/README.md`.

## What didn't work
- The first Figure 3 rerender command referenced the stale `figure3B_model_c_2026-11-17` directory and created an empty intermediate output directory. It was rerun from the verified `figure3B_control_fits_2026-11-18` source into `_v2`; the empty intermediate is not selected.

## How to reproduce
- Figure 3 panel: `.venv/bin/python -m scripts.paper.figure3B_model_c --input dissemination/paper_accumulation/draft_2026-11-15/figure3B_control_fits_2026-11-18 --output <fresh-directory>`.
- Figure 3 assembly: `.venv/bin/python -m scripts.paper.assemble_figure3 --behavior-first --panel-b <new-panel-stem> --output <fresh-directory>`.
- Figure 6a/6b: run `scripts.paper.figure6_best_all_trial_fit` and `scripts.paper.figure6_best_pulse_only_fit` with fresh outputs.
- Figure 5a/5b: run `scripts.paper.figure5_pulse_only_bits` and `scripts.paper.figure5_all_trials_bits` with fresh outputs.

Independent validation used pandas table equality, manifest assertions, absence of smoothing exports, Pillow image metadata and `git diff --check`.

## Caveats
Straight segments are visual guides between tested coherences, not interpolated model predictions. Model Monte Carlo uncertainty is not displayed. Figure 6 curves use saved full-fit simulations and are not held-out validation. The choice of Figure 3 bits/BIC for this eight-image set is an explicit review assumption; its LL/BIC alternative remains archived.

## Open questions and next steps
- [ ] Author confirm that Figure 5 and Figure 6, rather than Figure 3 and Figure 6, are the two figures intended to retain two variations.
- [ ] Continue panel-level revisions from the in-chat previews.
