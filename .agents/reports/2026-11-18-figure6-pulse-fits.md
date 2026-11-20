# Report: Tentative Figure 6 pulse psychometric and chronometric fits
Date: 2026-11-18   Agent: Codex   Commit: 3b55eca (uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Show psychometric and chronometric fits from pulse-only models for author selection, while Figure5 discussion is deferred.

## Summary
VERIFIED predictions exist for both criterion winners in saved browser v7. Comparison and two single-model previews exported, with six stages/directions, early/middle10 mice and late6. No decision fits or simulations; only descriptive four-parameter display fits to group probabilities. Figure4 unchanged.

## Findings
- VERIFIED equal-mouse mean/SEM and matching observed/predicted mouse/coherence support; source_data equivalents are mouse_cells.csv/group_summaries.csv and verification.json.
- VERIFIED 10112 observed responses in symmetric-schedule pulse subset; do not equate this display selection with full11479 pulse fit/score population or Figure4's response-after-pulse mask. Caption documents distinction.
- VERIFIED control observations and browser's control-borrowed psychometric endpoints excluded. Curves fit actual pulse coherence support only. Source: script and exported display parameters/curves.
- VERIFIED mean RT includes both response choices. Intervals are observed between-mouse SEM, not model simulation SE or parameter uncertainty. Saved inputs have four-decimal summary precision.

## What didn't work
Browser's precomputed psychometric fits borrowed control endpoints, so those fits were not used. Recomputed only descriptive logit_4 curves from saved pulse-only equal-mouse summaries.

## How to reproduce
`.venv/bin/python -m scripts.paper.figure6_pulse_fits --output <fresh-directory>`. Input: dissemination/figures/qc/fit_browser_2026-11-12_v7.json. Source/code hashes in output manifest.json. Finishing aggregation verification: /tmp/finalize_figure6_preview.py. Existing environment, no installs.

## Caveats
In-sample fixed-parameter simulation summaries, not held-out validation. Unequal stage cohort and coherence support; rounded source summaries; descriptive logistic approximation can differ from raw predicted proportions. No inferential model superiority claim from these overlays.

## Open questions and next steps
- [ ] Author assess both models, selection of panel content and chronology display.
