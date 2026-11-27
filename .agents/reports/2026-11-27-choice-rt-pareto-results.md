# Report: Choice–RT Pareto refits and pulse signatures
Date: 2026-11-27   Agent: Codex   Commit: 5f0a30e, 646f2d5
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Does increasing the relative contribution of choice likelihood let the pulse-only normalized UGM/no-sv model recover the pulse-choice and temporal signatures, without unacceptable loss of response-time prediction?

## Summary
No moderate weight provides a meaningful rescue. At 4× and 8× relative choice weight, pooled held-out choice NLL improves by only 1.84 and 2.14 across 11,479 pulse trials, while conditional-RT NLL worsens by 15.40 and 47.41; the equal-mouse choice changes are inconsistent. Moderate reweighting also leaves the predicted onset decline far shallower than observed. Choice-only fitting moves the onset slope toward the data, but destroys RT prediction, worsens the persistence profile and produces up to 46% simulated nonresponses. Treat this as an exploratory architecture diagnostic: the Figure 7 mismatch is not explained by the original joint likelihood simply underweighting choices.

## Findings
- VERIFIED: all four weighted families contain the expected 60 fits (10 mice × `pulse`/`pcv0`–`pcv4`) and pass stored metadata checks. Five common simulation seeds were scored with the original unweighted choice + conditional-RT likelihood. Every family/seed contains 11,479 held-out pulse trials. Source: `scripts/paper/score_choice_weight_fits.py`; command: `.venv/bin/python -m scripts.paper.score_choice_weight_fits --check`; output: `dissemination/paper_accumulation/draft_2026-11-15/choice_rt_pareto_2026-11-27_v2/`.
- VERIFIED: relative to weight 1, pooled held-out `(choice, RT, joint)` NLL changes are `( +0.322, −0.862, −0.540)` at 2×, `(−1.838, +15.398, +13.560)` at 4×, `(−2.144, +47.407, +45.263)` at 8× and `(−14.504, +4196.822, +4182.317)` for choice only. Negative is better. Source: `choice_weight_figure7_preview_2026-11-27_v5/adequacy_summary.csv`.
- VERIFIED: after averaging simulation seeds within mouse and normalizing by each mouse's held-out trial count, the equal-mouse choice improvements in bits/trial are 2× `0.000386` (95% t CI `−0.000703, 0.001475`; 4/10 mice improve), 4× `0.000128` (`−0.001247, 0.001502`; 4/10), 8× `−0.002163` (`−0.006629, 0.002304`; 6/10) and choice only `−0.001809` (`−0.009497, 0.005878`; 4/10). Thus the small pooled 4×/8× gains are not a consistent animal-level effect. Source: `choice_rt_pareto_preview_2026-11-27_v3/heldout_group_summary.csv`; script: `scripts/paper/plot_choice_weight_pareto.py`.
- VERIFIED: the observed model-free full-fit pulse-direction contrast is `0.06863`; predictions are `0.04728`, `0.04739`, `0.05437`, `0.05520` and `0.07401` for 1×, 2×, 4×, 8× and choice only. This in-sample choice readout improves gradually, but does not establish held-out generalization. Source: `choice_weight_figure7_preview_2026-11-27_v5/panel_A_choice_contrast_summary.csv`.
- VERIFIED: the observed Figure 4C onset slope is `−5.40068` coherence-equivalent units/stage. Fixed-fit predictions are 1× `−0.72579`, 2× `−0.74547`, 4× `−0.83931`, 8× `−1.07983` and choice only `−3.13361`. Each weighted estimate uses 30 repetitions × 2 seeds; all 80 mouse/seed caches are complete, all readout optimizations succeed from 10/10 starts and no readout parameter is on a bound. Source: `choice_weight_figure7_2026-11-27/onset/` and `choice_weight_figure7_preview_2026-11-27_v5/adequacy_summary.csv`.
- VERIFIED: Figure 4D persistence-profile RMSE values are 1× `5.13865`, 2× `4.95573`, 4× `4.73533`, 8× `5.06229` and choice only `6.49514`. The 4× improvement is small and does not fix the missing late influence. Source: `choice_weight_figure7_2026-11-27/persistence/all_readouts.csv`; script: `scripts/paper/plot_choice_weight_figure7.py`.
- VERIFIED: choice-only fits produce maximum simulated nonresponse fractions of `0.4626` across the weighted persistence simulations (DBM12; the second seed is `0.459`). The maximums for 2×, 4× and 8× are `0.1055`, `0.1072` and `0.0706`. Source: ignored, reproducible fixed-parameter caches under `choice_weight_figure7_2026-11-27/persistence/cache/`; summary: `choice_weight_figure7_preview_2026-11-27_v5/adequacy_summary.csv`.
- VERIFIED: the original uninterrupted scorer and the checkpointed rerun produced byte-identical `pareto_summary.csv` files. Validation found 250 mouse-seed rows, 80 onset caches and 80 persistence caches; all model persistence slopes used by the readout are positive.

## What didn't work
- The first scorer was launched before per-family checkpointing was added. It ultimately completed, but output collection was ambiguous during the long run. The scorer now checkpoints each family and supports `--resume`; the independent rerun reproduced the final summary exactly.
- Early weighted Figure 7 render attempts exposed two table-schema assumptions and crowded layout. These were corrected in new versioned previews; no existing result was overwritten. Final reviewed preview is `choice_weight_figure7_preview_2026-11-27_v5/`.
- Choice-only conditional-RT NLL can be zero for sparse mice/cells under the existing condition-by-choice qMLE construction; this is not missing data. The aggregate endpoint is nevertheless clearly inadequate because RT NLL explodes in other mice and fixed simulations reveal extreme nonresponse behavior.

## How to reproduce
Common-scale scoring and Pareto summary:
```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore -m scripts.paper.score_choice_weight_fits \
  --output dissemination/paper_accumulation/draft_2026-11-15/choice_rt_pareto_2026-11-27_v2
.venv/bin/python -m scripts.paper.plot_choice_weight_pareto \
  --source dissemination/paper_accumulation/draft_2026-11-15/choice_rt_pareto_2026-11-27_v2 \
  --output dissemination/paper_accumulation/draft_2026-11-15/choice_rt_pareto_preview_2026-11-27_v3
```

Fixed-parameter pulse signatures:
```bash
.venv/bin/python -m scripts.paper.pulse_model_primacy --output <weighted>/onset --phase prepare
.venv/bin/python -m scripts.paper.pulse_model_primacy --output <weighted>/onset --phase simulate \
  --families pulse_norm_ugm_choice_w2 pulse_norm_ugm_choice_w4 pulse_norm_ugm_choice_w8 pulse_norm_ugm_choice_only \
  --seeds 0 1 --reps 30
.venv/bin/python -m scripts.paper.pulse_model_primacy --output <weighted>/onset --phase analyze \
  --families pulse_norm_ugm_choice_w2 pulse_norm_ugm_choice_w4 pulse_norm_ugm_choice_w8 pulse_norm_ugm_choice_only \
  --seeds 0 1 --reps 30 --comparison all_available_10
.venv/bin/python -m scripts.ddm.pulse_dynamics_bridge --output <weighted>/persistence --prepare \
  --families pulse_norm_ugm_choice_w2 pulse_norm_ugm_choice_w4 pulse_norm_ugm_choice_w8 pulse_norm_ugm_choice_only
# Run --simulate once with --seed 0 and once with --seed 1, then:
.venv/bin/python -m scripts.ddm.pulse_dynamics_bridge --output <weighted>/persistence --analyze \
  --families pulse_norm_ugm_choice_w2 pulse_norm_ugm_choice_w4 pulse_norm_ugm_choice_w8 pulse_norm_ugm_choice_only \
  --seeds 0 1 --reps 30
.venv/bin/python -m scripts.paper.plot_choice_weight_figure7 \
  --score-dir dissemination/paper_accumulation/draft_2026-11-15/choice_rt_pareto_2026-11-27_v2 \
  --weighted-dir dissemination/paper_accumulation/draft_2026-11-15/choice_weight_figure7_2026-11-27 \
  --output dissemination/paper_accumulation/draft_2026-11-15/choice_weight_figure7_preview_2026-11-27_v5
```

Validation: `.venv/bin/python tests/test_choice_rt_weight.py`, module compile, scorer `--check`/`--resume`, exact duplicate-summary comparison, cache counts, optimizer checks, positive-slope checks and 300-dpi raster inspection were run on 2026-11-27.

## Caveats
- This sweep was designed after seeing the original Figure 7 mismatch and is exploratory. The intervals across 10 mice describe mouse heterogeneity; they are not confirmatory tests and no multiplicity-adjusted hypothesis family was introduced.
- The 2-seed bands in temporal panels quantify Monte Carlo variation only, not animal or parameter uncertainty.
- The full-fit choice contrast is in-sample for the pulse-only `pulse` fits; held-out scores are the appropriate generalization check.
- Trials were filtered before these fits. All comparisons use the same repository DDM input and panel-specific audited selections, so the sweep cannot address selection bias outside that analyzed population.
- The persistence cache is intentionally git-ignored because it is large; its fingerprints and compact readout/coverage tables are tracked and the cache is reproducible from the commands above.

## Open questions and next steps
- [x] Do not replace the Figure 6B/7B model with a weighted fit. Retain weight 1 as the predictive model.
- [ ] Decide whether the compact weighted diagnostic belongs in the supplement or only in reviewer-response/internal records.
- [ ] In the Discussion, interpret the residual pulse timing mismatch as evidence that likelihood weighting alone cannot supply the missing temporal computation; do not claim that this sweep identifies the missing mechanism.
