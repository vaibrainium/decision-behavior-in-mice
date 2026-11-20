# Report: Pulse-only models and Figure 4C primacy
Date: 2026-11-18   Agent: Codex   Commit: 3b55eca (analysis uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Which pulse-only model reproduces the onset-stage decline of pulse influence?

## Summary
VERIFIED all22 fixed pulse-only models simulated on the same pre-response-selection schedules and analyzed with the Figure4C ordinal regression. Normalized UGM/no sv ranks closest in all-available curve RMSE and slope error in both seeds, but predicts a much shallower decline. Matched-six sensitivity changes ranking and observed primacy remains uncertain; no unique mechanism identified.

## Findings
- VERIFIED observed21725 responses and grouped cells exactly reproduce Figure4C from22437 preselection schedules. Source: preparation.json and observed_cells.csv.
- VERIFIED model slope−0.725790/stage (seed range−0.850621 to−0.600959), observed−5.400683. Predicted stage values4.85793/4.13214/3.40635 versus observed12.10521/6.70452/1.30384. Source: model_primacy_ranking.csv, model_stage_readouts.csv and saved ordinal influence_curves.csv.
- VERIFIED BIC winner linear leak predicts+0.444134/stage. Only normalizedUGM/no sv has negative mean slope across seeds in all-available case; this is descriptive, not a test of other models' recency.
- VERIFIED matched6 curve ranking favors linear_primary in the seed-mean summary, but winners differ across seeds. Observed matched6 slope−1.717220 is inconclusive. Source: model_primacy_ranking_matched6.csv; model_readout_matched6_by_seed.csv; original ordinal slope_tests.csv.
- VERIFIED440 mouse simulation jobs;88 descriptive regression fits×10 successful starts, all interior, positive coherence slopes. Replicate count scaling of residuals/Jacobians checked; code/input hashes in verification.json. Render inspected.

## What didn't work
Existing trial-level model caches exclude late pulses and cannot answer the three-stage question. New fixed-parameter simulations were necessary; no decision parameters were refitted. Earlier rounded browser summary curves were not substituted for the exact Figure4C estimator.

## How to reproduce
Full commands and scope in pulse_model_primacy_2026-11-18/README.md; scripts.paper.pulse_model_primacy phases prepare/simulate/analyze (all_available_10 and matched_6), then scripts.paper.plot_pulse_model_primacy. Simulation inputs and per-fit hashes retained.30 repetitions×2 seeds, CUDA backend, existing environment. Results new directory only. Finishing documentation: /tmp/finish_model_primacy.py.

## Caveats
Conditional fixed full-pulse fits and response-selected stimulus pool; no parameter uncertainty or calibrated model-rejection test. Data cohort mismatch and shared-effect regression assumptions matter. Seed ranges are simulation variability, not animal-population uncertainty. Low model RMSE relative to alternatives is not adequate absolute fit. No journal-level claim.

## Open questions and next steps
- [ ] Author assess whether this mismatch belongs in Figure5/6 or supporting diagnostics.
- [ ] If interpreting primacy biologically, retain matched-cohort uncertainty and distinguish onset effects from pulse persistence.
