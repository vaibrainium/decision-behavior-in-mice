# Per-mouse timing-fit review

Original timing analysis fits each mouse × stage × direction separately, then averages parameters across mice with SEM. No formal timing-effect test was run. The population-curve sensitivity in the previous audit is a different estimand and is not a replacement for subject-level inference.

Left plot: all10 saved early left/right midpoint pairs, no exclusions. Right: DBM12 early-left observed right-choice fractions (point annotations are trial counts) and its saved fitted curve; dashed portion is outside the observed coherence range. Alpha=-100 is the lower allowed midpoint bound, not a measured choice threshold or a trial coherence.105 trials span-18 to+100 coherence; the fitted asymptotes are0.4 and0.636156, so alpha refers to fitted P(right)≈0.518, not necessarily0.5. The flat/noisy curve does not identify that midpoint reliably. No refitting or numerical changes.

Values and input hashes: manifest.json. Individual pairs and DBM12 cells exported alongside the figure. Squared residual objective independently reconstructed from saved coefficients and trial counts; render inspected.

Reproduce with fresh output:
`.venv/bin/python -m scripts.paper.show_pulse_timing_individual --source dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18 --output <new-directory>`
