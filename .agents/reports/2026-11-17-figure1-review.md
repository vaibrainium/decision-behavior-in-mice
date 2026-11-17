# Report: Figure 1 initial discussion
Date: 2026-11-17   Agent: Codex   Commit: ffc97d1 (base)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Begin author-led figure review with Figure 1.

## Summary
VERIFIED: visually inspected selected Figure 1, caption and group source tables. It establishes stimulus-guided performance in retained sessions and outcome-dependent RTs. No artwork/data changed. Recommendations below await author discussion.

## Findings
- VERIFIED: mouse-level summaries and individual curves are shown in panels C/D. Source: dissemination/paper_accumulation/draft_2026-11-15/figures_v5/figure1.png, source_data/fig1_C_psychometric_group.csv and fig1_D_rt_group.csv; figure_captions.md.
- JUDGMENT: clarify diagrammatic timing in A; show baseline → replacement pulse → baseline more explicitly in B.
- JUDGMENT: move population flow to supplement while retaining exclusions in caption/Methods; retain correct/error RT curves.
- JUDGMENT: this figure supports performance, not acquisition of the task or accumulation by itself.

## What didn't work
Sandbox namespace creation failed; bounded escalated reads succeeded. Unqualified python unavailable; python3 used for notes.

## How to reproduce
View selected PNG and read corresponding caption, results.md and fig1_* CSVs in the draft folder. No statistical recomputation.

## Caveats
Author-side working discussion, not formal journal peer review or compliance certification. Selected-session and response-window conditioning remain explicit.

## Open questions and next steps
- [x] Resolve Figure 1 with author; selected v6 accepted for checkpoint.
- [x] Proceed to Figure 2 after discussion.

## Author-directed wording revision
2026-11-17: Replaced +/− pulse legend labels with Rightward pulse (orange) and Leftward pulse (blue) in scripts/paper/fig1_task_behaviour.py, and removed sign shorthand from the current caption. Fresh Figure 1 PDF/SVG/PNG and source manifest: dissemination/paper_accumulation/draft_2026-11-15/figure1_revision_2026-11-17/. Render inspected; legend fits. Previous artwork and packaged Word draft remain preserved; Word packet has not been regenerated. No data or inference changed. Reproduce using Builder/figure1 with STYLE from scripts.paper.build_paper_2026_11_15 into a fresh output directory.

## Control-only points and psychometric fits
2026-11-17 author request implemented in figure1_revision_2026-11-17_v2. VERIFIED: archived C/D sources already use sched_pulse_type == 0; selection is explicit in scripts/paper/fig1_task_behaviour.py main. Four observation CSVs in the new export are numerically identical to figures_v5. C now shows observed points and the author's exact logit_4 curves, using src/utils/pmf_utils.py fit_psychometric_function defaults. Individual curves use trial-count weighting; the separate group curve uses unweighted mouse mean proportions. D shows observed RT points without connecting lines or a psychometric fit. Parameter and prediction CSVs accompany the figure. All 11 fits checked finite, bounded, monotonic, and equal to the saved equation predictions. One individual lower-asymptote parameter reaches its lower bound; these are descriptive curves, not parameter-inference results. Render visually inspected; caption and descriptive Methods updated. Packaged Word draft and earlier exports preserved. The old HTML viewer still contains the earlier image; current chat preview is the v2 PNG.

Reproduce: `.venv/bin/python -m scripts.paper.review_figure1 --output <fresh-directory>`. Base commit remains ffc97d1; current script changes are uncommitted. No new decision-model fitting, raw-data edits or population changes.

## Four-panel revision
2026-11-17 author requests removing E. Selected export: figure1_revision_2026-11-17_v6 (A–D, compact two-row layout). Updated caption and obsolete Figure 1E Results reference; exclusions remain in Methods, population source table retained as fig1_population.csv. VERIFIED: all source values match v5, with only population CSV name changed; verification.json records check. Render inspected. Reproduce `.venv/bin/python -m scripts.paper.review_figure1 --output <fresh-directory>`. Base ffc97d1; changes uncommitted. No underlying statistical changes; earlier exports preserved. Next: continue author figure review.

## Checkpoint
2026-11-17: Author requests committing revisions and moving to Figure 2. Figure/artwork/manuscript changes committed as 9f21e7f; no push. Python compile checks and source-table/summary verification passed as recorded above. A full git whitespace check flags standard Matplotlib SVG path formatting; generated artwork preserved, Python/Markdown whitespace checks pass. The local checkpoint also retains the superseded review versions. Figure 2 initial walkthrough follows in reports/2026-11-17-figure2-review.md.
