# Report: Figure4A pulse-only psychometric fits
Date: 2026-11-18   Agent: Codex   Commit: eef364b (base; this revision uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Author requests removing controls from A and showing fitted psychometrics for left/right pulses.

## Summary
New full-figure v2 shows only physical left/right pulse points with original SEM and smooth author logit_4 fits. B–D remain unchanged. Descriptive fits only; no new decision-model fits or pulse inference.

## Findings
- VERIFIED: all5 original source tables equal prior figure4_pulse_review_2026-11-18 sources. Control retained in archived source pool but not displayed in A. Pulse-only displayed-point CSV exported;8529 responses from10 mice, original temporal population retained.
- VERIFIED: unweighted least squares to equal-mouse group proportions, exact author logit_4 helper/default bounds as group Fig1. Each direction fitted separately. Parameters/401-point dense curves exported. Blue left restricted−36 to100% coherence; orange right−100 to36%; no extrapolation into absent combinations.
- VERIFIED: every exported curve recomputed from its coefficients with scipy.special.expit; probabilities finite/bounded/monotone, observed coherence ranges matched. Original B–D builder code untouched and B–D caption text identical. Numerical checks in verification.json, source hashes in figure_manifest.json. PNG inspected; source compiles.

## What didn't work
No failed fitting or rendering steps. New pulse psychometric curves are descriptive, not model C pulse predictions.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.review_pulse_results --output dissemination/paper_accumulation/draft_2026-11-15/figure4_revision_FRESH --fit-pulse-psychometric
```
Actual output figure4_revision_2026-11-18_v2. Source/coefs/curves in source_data, caption adjacent. Previous figure preserved; omit flag to reproduce earlier display.

## Caveats
Descriptive group fits do not estimate uncertainty in a between-curve shift. Available mouse counts vary by coherence. No raw data, exclusions, B–D estimates or significance results changed. Global manuscript/Word numbering pending assembly; new caption/Methods reflect this A revision. No commits/pushes.

## Open questions and next steps
- [ ] Author assess pulse-only fitted A.
- [ ] Continue B–D minor panel edits sequentially.

## Full-range display v3 — 2026-11-18
Author requests both fitted lines span−100 to100%. Added --extend-pulse-curves; fresh figure4_revision_2026-11-18_v3. VERIFIED original points/SEM and B–D source tables unchanged, all4 parameters exactly unchanged per direction, dense curves cover requested range and match exact equation. Caption/Methods disclose extrapolated portions with no added data. Render inspected, source compiles. Reproduce with prior command plus --extend-pulse-curves and fresh output. Next author assess A.
