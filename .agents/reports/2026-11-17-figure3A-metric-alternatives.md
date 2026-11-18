# Report: panel A metric alternatives
Date: 2026-11-17   Agent: Codex   Commit: 294cddc (base; rendering changes uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, step R

## Question
Create two panel-A alternatives: NLL/BIC dual axes, and bits with BIC in a separate right subpanel.

## Summary
Both previews rendered from previously verified group means, with connected categorical points and no error bars. No new fits, scores or inference. Second layout interprets the author's words “right panel” literally; this interpretation was stated in commentary.

## Findings
- VERIFIED: exported source_panel_A.csv exactly combines approved mean test NLL, joint test bits/trial and absolute QMLE BIC. BIC differences match previous ΔBIC; NLL counts are 10 mice for each candidate; all values finite. Sources and hashes in manifest.json.
- VERIFIED: PNGs visually inspected; source compiles. PNG/PDF/SVG exports and full captions retained under dissemination/paper_accumulation/draft_2026-11-15/figure3A_metric_alternatives_2026-11-17/.
- Design: A1 blue solid/circles left test NLL, orange dashed/squares right training BIC. A2 separate grayscale bits and BIC subpanels, both within A. Tight labeled nonzero axes. No selected manuscript artwork replaced.

## What didn't work
No failed rendering attempts. Dual-axis curves overlap substantially; intersection or vertical alignment has no statistical meaning because units differ. Axes were automatically scaled independently, not manually aligned.

## How to reproduce
From /src:
```bash
.venv/bin/python -m scripts.paper.figure3A_metric_alternatives --draft dissemination/paper_accumulation/draft_2026-11-15 --output dissemination/paper_accumulation/draft_2026-11-15/figure3A_metric_alternatives_FRESH
```
Input sources: figure3A_group_nll_connected_2026-11-17/group_nll.csv; figure3_information_metrics_2026-11-17/group_metrics.csv; figure3_absolute_bic_2026-11-17/group_absolute_bic.csv, relative to the same draft directory. Output manifest records hashes, including the rendering script.

## Caveats
Likelihood means held-out NLL to retain the author's approved convention. BIC uses independently evaluated full-training QMLE, not displayed test NLL; it remains approximate. Joint bits are −NLL/(n_test ln2), not choice-only gain over a bias null. Means equally weight mice; raw total NLL and per-trial bits are different aggregations. See the preceding bits/BIC report for scoring provenance.

## Open questions and next steps
- [ ] Author choose panel A layout or clarify if the second version also needs dual axes.
- [ ] Continue remaining Figure 3 panels.

## LL revision — 2026-11-17
Author requests LL rather than NLL. VERIFIED: mean_test_ll exactly negates prior mean_test_nll; BIC/bits means exactly unchanged. Fresh output: figure3A_metric_alternatives_ll_2026-11-17/A1_ll_bic_dual_axis.png under draft directory. Reproduce earlier command with --likelihood ll and fresh output. PNG visually inspected; source compiles. Initial caption syntax error corrected before render; system Python pandas is binary-incompatible, so stdlib CSV used for independent checks (render uses existing .venv). No refits or scoring. Default CLI retains NLL for old-preview reproducibility. Next author assess LL/BIC.

## Both alternatives use dual axes — 2026-11-17
Author clarified both figures require two y-axes. Completed A1 LL left/BIC right and A2 joint test bits/trial left/BIC right, in figure3A_both_dual_axes_2026-11-17/ under the draft directory. VERIFIED all exported values exactly match prior LL source table; script compiles; both PNGs inspected. No refits/rescoring. Prior second-layout interpretation superseded. Reproduce from /src:
```bash
.venv/bin/python -m scripts.paper.figure3A_dual_axes --input dissemination/paper_accumulation/draft_2026-11-15/figure3A_metric_alternatives_ll_2026-11-17/source_panel_A.csv --output dissemination/paper_accumulation/draft_2026-11-15/figure3A_both_dual_axes_FRESH
```
PNG/PDF/SVG, captions, source CSV and source/script hashes retained. Both left measures higher better; right BIC lower better. Dual-axis curve crossings have no inferential meaning. Next author select A.
