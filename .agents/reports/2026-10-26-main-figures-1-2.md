# Report: Main Figures 1–2 assembled and five-figure package reconciled
Date: 2026-10-26   Agent: Codex   Commit: 0b76e80 (dirty worktree)
Plan: plans/2026-10-20-paper-writeup.md, AB5–AB6

## Question
Can the task/behaviour and stimulus-reconstruction figures be rebuilt with exact panel denominators, honest uncertainty
units and artwork-matched legends, completing the five-main-figure paper package?

## Summary
Figures 1 and 2 are assembled, visually inspected and selected as versioned PDF/SVG/300-dpi PNG exports. Figure 1
uses mice for behavioural summaries and retains no-response trials explicitly; Figure 2 uses trials/seeds/replay
conventions and never presents stimulus dispersion as across-mouse uncertainty. Exact source tables accompany every
selected panel. The selected five-figure set, captions and neuropaper legends are reconciled, with no unresolved claim
or number tokens and no main-figure `[MISSING]` markers.

## Findings
- VERIFIED: the descriptive dataset contains 30,045 accepted trials from 10 mice and 50 mouse-sessions: 25,508
  responses by 5 s and 4,537 no-response trials. Scheduled controls contribute 14,015 responded trials to Figure 1C
  and 16,522 total trials to Figure 1E. Source: `fig1_task_behaviour_2026-10-26_v2_source_overview.csv`,
  `*_source_psychometric_group.csv`, `*_source_no_response_group.csv`; command
  `.venv/bin/python -m scripts.paper.fig1_task_behaviour`.
- VERIFIED: all 10 mice meet the Figure 1D threshold of at least 10 responses in every displayed
  outcome-by-absolute-coherence cell. Exact trial totals are in `fig1_task_behaviour_2026-10-26_v2_source_rt_group.csv`.
- VERIFIED: Figure 2B contains 9,258 UCLA and 4,757 UW responded control trials; Figure 2C contains 872 and 443
  nominal-zero trials. Figure 2D uses 76 UCLA and 108 UW paired same-seed trials, with pointwise 95% Student-t
  intervals across trials. Figure 2E uses the same 76 UCLA trials under each labelled convention. Sources:
  `fig2_stimulus_reconstruction_2026-10-26_v5_source_*.csv`; command
  `.venv/bin/python -m scripts.paper.fig2_stimulus_reconstruction`.
- VERIFIED: all five selected figures have PDF, SVG and PNG exports plus non-empty source CSVs. PNGs are 300 dpi;
  SVG widths are 510.24 pt (180 mm) with editable text. Scripts compile. Claim and number tokens in
  `np/drafts/figure_legends/v4.md` resolve, number IDs are unique, and `git diff --check` passes.

## What didn't work
- `pdfinfo`, ImageMagick `identify` and PyMuPDF are unavailable. No packages were installed. PNG dimensions/DPI and
  SVG dimensions were checked with installed Python libraries; the PDFs were generated in the same Matplotlib save
  calls as the checked SVG/PNG exports.
- Early Figure 2 layout drafts crowded schematic text and clipped long panel titles. Version 5 shortens the titles and
  uses a vertical reconstruction flow. Earlier versioned drafts remain on disk and are not selected.

## How to reproduce
```bash
cd /src
.venv/bin/python -m scripts.paper.fig1_task_behaviour
.venv/bin/python -m scripts.paper.fig2_stimulus_reconstruction
.venv/bin/python -m py_compile scripts/paper/style.py scripts/paper/fig1_task_behaviour.py \
  scripts/paper/fig2_stimulus_reconstruction.py scripts/paper/fig3_control_models.py \
  scripts/paper/fig4_pulse_behaviour.py scripts/paper/fig5_model_mismatch.py
```

Selected artwork and captions are indexed in
`dissemination/paper/figures/figure_build_2026-10-26.md`. Ledger audits are N105–N107 in
`dissemination/paper/np/ledger/numbers.csv`.

## Caveats
- Figure width is provisionally 180 mm pending final eLife production specifications.
- The reconstruction is not a frame-perfect acquisition record; UCLA replay alternatives remain labelled assumptions.
- Earlier same-day figure versions are retained under the no-overwrite rule and must not be mistaken for selected art.
- Supplementary Figure S6 remains text-only; its cell denominators require an artwork-specific audit if it is built.

## Open questions and next steps
- [ ] Author visual review of the selected five-figure set.
- [ ] Decide whether to build Supplementary Figure S6 before resuming Introduction/title/abstract work.
- [ ] At submission, apply the target journal's final dimensions and file-naming rules without changing scientific
      mappings or denominators.
