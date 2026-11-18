# Report: begin control-results Figure 3 review
Date: 2026-11-17   Agent: Codex   Commit: a20629e
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Move from accepted model-introduction Figure 2 to the control-results figure.

## Summary
Figure 2/split checkpointed at author request. Current Figure 3 remains the exported comparison/recovery starting layout. Recommend opening with observed and predicted choice/RT behavior, followed by held-out comparisons and recovery. No new predictions, fits or inference performed this turn.

## Findings
- VERIFIED: current Figure 3 panels are score differences, choice/RT score decomposition, dataset recovery and cohort recombinations. Sources: draft_2026-11-15/figure3_control_results_2026-11-17/figure3.png and adjacent caption/source tables; unchanged from prior audit.
- VERIFIED: dissemination/paper_control/tables/control_chronometry_2026-10-29.csv contains sources data/common/E and 10 mouse IDs, with absolute coherence/outcome summaries. It does not contain all five model predictions or signed-choice summaries needed for the proposed new overlays. Inspection command: pandas read_csv; inspect source.unique(), mouse.nunique(), columns.
- VERIFIED: scripts/ddm/control_descriptives.py documents common-model predictions from fits_resp_final and E from fits_resp_fast_only_leak20-200_cap; these are distinct fit sources. Do not present that export as a uniform held-out five-model comparison.
- JUDGMENT: new opening panels should show what models capture/miss in observed psychometric and choice-conditioned mean RT functions. Trial population, fitting split and prediction source must match the stated comparison. Source audit is next, not an assumed validation.

## What didn't work
No new build attempted. Legacy chronometry alone is insufficient for the proposed complete overlay; no substitution or fabricated ES/reference curves.

## How to reproduce
Read the current Figure 3 artwork/caption and the old chronometry CSV plus scripts/ddm/control_descriptives.py and control_heldout.py. Comparison/recovery extraction reproduces with `.venv/bin/python -m scripts.paper.review_control_results --output <fresh-directory>`.

## Caveats
Current Figure 3 is a starting layout. Model schematic is illustrative; observed/predicted results must use separately audited prediction sources. Old manuscript numbering remains pending figure selection. No push performed.

## Open questions and next steps
- [ ] Agree on opening choice/RT panels and overall Figure 3 arrangement.
- [ ] Audit saved prediction artifacts for matched fit splits and all five candidates before plotting.
- [ ] Build and inspect the agreed results revision, preserving old artwork.

## Author-directed absolute NLL panel
2026-11-17: Author requests A use NLL directly rather than differences, keeping results raw. This supersedes the suggested opening behavior overlays for the current A. Built figure3A_raw_nll_2026-11-17 with total saved held-out NLL for C/E/ES/DDMx/ESx, separately for each mouse, without subtraction or trial-count normalization. Each axis has independent labeled limits; trial counts shown; caption discourages comparing absolute levels across animals.

VERIFIED: 50 score points match the summed 250 saved fold scores and their test counts from reviewer_2026-11-13/control_fold_inventory.csv. Counts sum to 14,014 control trials; each mouse uses the same count across its five candidates. Original model-difference totals reproduced as a consistency check only, not plotted. Sources: paper_control/tables/heldout_nll_per_mouse_2026-10-29.csv, heldout_diff_per_mouse_2026-10-29.csv; output absolute_nll.csv, fold_scores.csv and manifest with hashes. Render inspected. No new score evaluations, fits, simulation, uncertainty estimate or group test.

Reproduce: `.venv/bin/python -m scripts.paper.figure3_raw_nll --output <fresh-directory>`. Base 294cddc; changes uncommitted. Earlier full Figure 3 remains preserved; B onward pending. Next: author assess A, then proceed panel by panel.

## Direct NLL bar display and Stine check
2026-11-17 author requests a bar graph of NLL and inspection of Stine. VERIFIED primary source: Stine et al. 2020, https://pmc.ncbi.nlm.nih.gov/articles/PMC7217695/, Figure 7B caption and Statistical analysis section. Published render inspected at https://cdn.elifesciences.org/articles/55365/elife-55365-fig7-v2.jpg. Figure 7B uses horizontal subject-specific ΔBIC bars; Tables 1–2 also report ΔBIC. It is not a raw-NLL bar precedent. Adopted horizontal-bar/subject emphasis while retaining the author's explicit direct held-out NLL metric.

Current A: figure3A_raw_nll_bars_2026-11-17_v2. Every candidate is a zero-baseline horizontal bar; each mouse has separately labeled NLL scale and control-trial n; numeric labels show two decimals. No subtraction/normalization, score reevaluation, fits, error estimate or statistical test. VERIFIED: exact absolute_nll.csv and fold_scores.csv identity to the earlier raw-score preview, plus original fold totals/count/difference checks in the builder; render inspected. New verification.json and caption adjacent. Raw NLLs are similar relative to their overall magnitudes, so bars can be similar despite meaningful predictive differences; no equivalence inference.

What did not work: first bar layout clipped long rightmost numeric/count labels; preserved it and corrected margins, numeric-label space and abbreviated n labels in v2. Reproduce `.venv/bin/python -m scripts.paper.figure3_raw_nll --output <fresh-directory>`. Base 294cddc; edits uncommitted. Next: author assess raw-NLL bar A before proceeding to B.

## Single cohort panel
2026-11-17 author requests removing mouse breakdown. Current A: figure3A_group_nll_2026-11-17, one five-bar display of equal-mouse arithmetic mean raw five-fold NLL ± SEM across 10 mice. No reference subtraction/trial normalization. Original scores/folds identical to previous preview; means and SEM independently checked from exported subject rows (verification.json). Computed descriptive aggregation only, no new fitting/scoring/inference. Caption notes that variation in raw totals reflects differing trial counts, and SEM is not uncertainty in paired model differences. Bars can appear nearly equal on this absolute scale; no equivalence inference. Render inspected. Per-mouse mode retained with --display mouse. Reproduce scripts.paper.figure3_raw_nll --output <fresh-directory>. Base 294cddc, changes uncommitted. Next: author assess A before B.

## Correction: SEM was inappropriate for communicating the comparison
2026-11-17 author flags apparent lack of significance in the raw-total SEM bars. Confirmed: these intervals reflect between-mouse raw-score variation (including trial counts), not uncertainty in paired model differences. Adding them was a presentation error for the model-comparison goal; interval overlap cannot test the paired hypothesis. Removed the error bars in figure3A_group_nll_no_sem_2026-11-17 while retaining every raw/fold/group value exactly. Render inspected. Existing paired tests exported separately from heldout_group_2026-10-29.csv with their source hash; no new tests or stars. Tests operate on within-mouse per-1,000-trial differences, not raw means. Holm t p: E .037352, ES .022766; corresponding Wilcoxon p .058594/.054688. Do not suppress the differing robustness conclusion or infer equivalence from raw-bar similarity. Adjacent caption explicitly separates plotted estimand and existing tests. Base 294cddc; changes uncommitted. Next: author assess A; consider paired uncertainty only if displaying the corresponding estimand.

## Point display
2026-11-17 author requests points instead of bars. Current A: figure3A_group_nll_points_2026-11-17_v3. Five equal-mouse mean raw NLL points, numeric labels, no error bars; axis tightened with explicitly labeled nonzero limits, without changing values. VERIFIED: raw/fold/group CSVs identical to preceding bar export. Render inspected; caption updated. A syntax error in the first axis edit prevented execution and was corrected before successful export. Reproduce scripts.paper.figure3_raw_nll with a fresh output directory. No new scoring, tests or fits. Base 294cddc, changes uncommitted. Next: author assess A.

## Connected mean points
2026-11-17 author requests connecting line. Current A: figure3A_group_nll_connected_2026-11-17. Solid visual-guide line joins the same five raw mean points; axis limits, labels and all raw/fold/group CSVs unchanged from points v3 (identity verified). No error bars/new inference. Render inspected; caption identifies categorical line semantics. Base 294cddc, changes uncommitted; reproduce scripts.paper.figure3_raw_nll with fresh output. Next: author assess A before B.
