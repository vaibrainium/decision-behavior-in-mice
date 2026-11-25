# Report: Figure 7 simulated pulse checks
Date: 2026-11-25   Agent: Codex   Commit: 6f4a678 (code), 479df88 (results/artwork)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
How do the best all-trial model from Figure 6a and the best pulse-only model from Figure 6b reproduce the behavioral pulse signatures displayed in Figure 4?

## Summary
Matched Figure 7A/7B previews are rendered from fixed fitted parameters; neither decision model was refitted. The all-trial power/leak/urgency winner reproduces neither the choice-shift amplitude nor the onset primacy and becomes strongly negative at long pulse-to-response delays. The pulse-only normalized UGM/no-sv winner is closer on all three displayed checks, but still predicts a substantially weaker choice shift and onset primacy than observed. Current previews are the `v3` directories listed below.

## Findings
- VERIFIED: Figure 7A (`power_leak_urgency`) predicts an onset-stage slope of +0.00014 percentage-coherence equivalents/stage, versus observed −5.40068. Figure 7B (`pulse_norm_ugm_no_sv`) predicts −0.72579/stage. Source: `figure7_7a...v3/panel_B_onset_summary.csv`, `figure7_7b...v3/panel_B_onset_summary.csv`; command: `.venv/bin/python -m scripts.paper.figure7_simulated_pulse_checks ...`.
- VERIFIED: At zero baseline coherence, the observed pooled right-minus-left pulse separation is 0.13630. The saved model predictions are 0.01792 for 7A and 0.06532 for 7B. Direct-point RMSE across displayed direction/coherence cells is 0.04912 and 0.04105, respectively. Source: each v3 `panel_A_choice_curves.csv`; aggregation is count-weighted over pulse stages within mouse, then equal-mouse averaged.
- VERIFIED: The observed Figure 4D early-bin mean γT is 15.15312 and late-bin mean is 2.29440. Figure 7A predicts 6.04853 early and −10.52547 late (six-bin RMSE 11.96068); Figure 7B predicts 9.96289 early and −0.38383 late (RMSE 5.13600). Source: each v3 `panel_C_persistence_summary.csv` and `dissemination/pulse_dynamics_2026-11-13/all_readouts.csv`.
- VERIFIED: The new 7A onset simulation reproduced the observed 21,725-trial Figure 4C cells exactly before simulation and produced 20 complete caches (10 mice × 2 seeds, 30 repetitions). Both ordinal optimizations completed 10/10 starts without bound parameters. Source: `figure7_model_checks_2026-11-25/onset_stage_simulations/`; commands are the `prepare`, `simulate`, and `analyze` phases of `scripts.paper.pulse_model_primacy`.

## What didn't work
- The initial render used attribute access for a column named `sem`, which pandas resolved as a method. The plotting-only error was corrected to explicit column access. Failed partial first-pass directories and successful v2 intermediates were removed after the verified v3 outputs were committed.
- A single whole-cohort simulation call stopped after a subset of CPU jobs. The simulator's per-mouse caches were restart-safe; the missing jobs were completed with the new `--mice` selector. No incomplete cache entered the analysis.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.pulse_model_primacy --output dissemination/paper_accumulation/draft_2026-11-15/figure7_model_checks_2026-11-25/onset_stage_simulations --phase prepare
CUDA_VISIBLE_DEVICES=0 .venv/bin/python -m scripts.paper.pulse_model_primacy --output dissemination/paper_accumulation/draft_2026-11-15/figure7_model_checks_2026-11-25/onset_stage_simulations --phase simulate --families power_leak_urgency --seeds 0 1 --reps 30
.venv/bin/python -m scripts.paper.pulse_model_primacy --output dissemination/paper_accumulation/draft_2026-11-15/figure7_model_checks_2026-11-25/onset_stage_simulations --phase analyze --families power_leak_urgency --seeds 0 1 --reps 30 --comparison all_available_10
.venv/bin/python -m scripts.paper.figure7_simulated_pulse_checks --variation 7a --output dissemination/paper_accumulation/draft_2026-11-15/figure7_7a_simulated_pulse_checks_2026-11-25_v3
.venv/bin/python -m scripts.paper.figure7_simulated_pulse_checks --variation 7b --output dissemination/paper_accumulation/draft_2026-11-15/figure7_7b_simulated_pulse_checks_2026-11-25_v3
```

## Caveats
Panel A uses matched fit-browser summaries pooled over pulse stages; it is the Figure 4A qualitative estimand but not the exact final Figure 4A trial table. Panels B and C use the exact Figure 4C and Figure 4D descriptive estimators, respectively. These panel-specific populations must not be described as one common cohort. Model bands show only the range of two simulation seeds, not parameter, mouse, or biological uncertainty. Full-fit simulations are posterior-style checks of fitted models, not held-out validation.

## Open questions and next steps
- [ ] Author decision: keep both 7A and 7B, or use 7B in the main text and move 7A to supplementary material.
- [ ] If selected, update manuscript Results/caption numbering and the eight-figure review index.
