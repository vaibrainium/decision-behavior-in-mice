# Report: absolute BIC preview
Date: 2026-11-17   Agent: Codex   Commit: 294cddc (base; uncommitted rendering change)
Plan: plans/2026-10-26-paper-accumulation-variant.md, step R

## Question
Show absolute BIC instead of ΔBIC in the approved connected-point style.

## Summary
Rendering-only change using existing independently scored, seed-averaged per-mouse BIC. Equal-mouse means with no reference subtraction or error bars. Lower is better. No new fits, scoring or inference.

## Findings
- VERIFIED: all 10 mice contribute all five candidates without duplicate rows; values are finite. Differences between plotted mean absolute BIC and C reproduce previous mean ΔBIC to numerical precision.
- VERIFIED: numeric means are exported in figure3_absolute_bic_2026-11-17/group_absolute_bic.csv; source copied as source_bic_per_mouse.csv. Paths are under dissemination/paper_accumulation/draft_2026-11-15/. Input is figure3_information_metrics_2026-11-17/bic_per_mouse.csv in the same draft directory. Source/script hashes and checks in manifest.json.
- VERIFIED: PNG visually inspected; PDF/SVG also exported. Source compiles.

## What didn't work
No failed approaches in this rendering change.

## How to reproduce
From /src:
```bash
.venv/bin/python -m scripts.paper.figure3_absolute_bic --input dissemination/paper_accumulation/draft_2026-11-15/figure3_information_metrics_2026-11-17 --output dissemination/paper_accumulation/draft_2026-11-15/figure3_absolute_bic_FRESH
```

## Caveats
QMLE-based approximation at saved fits, as detailed in reports/2026-11-17-figure3-bits-bic.md. Two independent training scoring seeds averaged per mouse/model. Tight explicitly labeled nonzero axis. Line is a categorical visual guide. No group significance or exact Bayesian evidence claim.

## Open questions and next steps
- [ ] Author assess absolute BIC preview and continue Figure 3 panel review.
