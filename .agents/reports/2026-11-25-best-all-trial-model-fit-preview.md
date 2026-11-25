# Report: Best all-trial model fit preview
Date: 2026-11-25   Agent: Codex   Commit: 9e04533
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Show the all-trial comparison winner on observed control and pulse choice/RT summaries for author review.

## Summary
VERIFIED `power_leak_urgency` has saved full-fit simulations for all displayed observed cells. A four-column control/early/middle/late preview compares equal-mouse observed summaries with matched model summaries. This is a descriptive full-fit overlay, not held-out validation. No decision-model fit or simulation was run.

## Findings
- VERIFIED 464 observed and 464 model mouse/condition/coherence cells match exactly across 10 mice. Source: `best_all_trial_model_fit_2026-11-25/mouse_cells.csv`; command below.
- VERIFIED the display includes 23,229 responded trials: 13,117 controls; 4,371 early; 4,281 middle; 1,460 late. Late schedules include 6 mice; other columns include 10. Source: `observed_counts.csv`.
- VERIFIED observed uncertainty is between-mouse SEM; psychometric display fits are unweighted four-parameter logistic fits over equal-mouse summaries. Model uncertainty is not displayed. Source: script and `verification.json`.

## What didn't work
- None. The saved browser summaries contained the selected family and all matched display cells.

## How to reproduce
`.venv/bin/python -m scripts.paper.figure6_best_all_trial_fit --output <fresh-directory>`

Input: `dissemination/figures/qc/fit_browser_2026-11-12_v7.json`. Script: `scripts/paper/figure6_best_all_trial_fit.py`. Source/code hashes are recorded in the output manifest. Validation used an independent pandas check of family cell counts, support equality, bounds and PNG metadata; `git diff --check` passed.

## Caveats
The display population is the browser's symmetric scheduled-pulse responded-trial selection and is smaller than the all-trial scoring population. Predictions use saved full-fit parameters with 30 simulations per responded schedule and seed 0. Saved summaries have four-decimal precision. Curves do not measure held-out generalization, and visual agreement is not a goodness-of-fit test.

## Open questions and next steps
- [ ] Author decide whether this becomes Figure 6 and whether control and pulse columns remain together.
- [ ] If selected, align panel lettering/caption with the final Figure 5 choice and manuscript sequence.

Naming update, 2026-11-25: author designated this alternative **Figure 6a**. Current labeled export: `figure6a_all_trial_model_fit_2026-11-25/`.
