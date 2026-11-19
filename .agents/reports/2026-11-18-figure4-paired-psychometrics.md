# Report: paired pulse psychometric α/β panel
Date: 2026-11-18   Agent: Codex   Commit: eef364b (base; new analysis uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, paired psychometric subsection

## Question
Author requests a paired comparison of pulse psychometric α/β to examine pulse use.

## Summary
Added B with per-mouse left/right pairs from exact author four-parameter fits; A unchanged, original B–D relabeled C–E without result changes. Optional α/β clarification unanswered, so stated mapping α=mean midpoint, β=var coefficient used. Fits expose substantial instability. Comparisons are exploratory; corrected parameter tests do not establish a decisive pulse-use result.

## Findings
- VERIFIED:20 individual curves across10 mice, trial-count WLS helper/default bounds,6–8 coherence levels/curve, all mice retained. α right-minus-left mean−18.35696244, median−16.38428878 (% coherence);9/10 negative; dz−0.8063. β mean−0.30230144, median−0.00859959 (per% coherence); dz−0.2217. Sources fig4_B_paired_parameters/differences/tests.csv in figure4_revision_2026-11-18_v4/source_data/ under draft directory.
- VERIFIED: exact two-sided mean-difference sign-flip pα0.03515625, pβ0.703125; Holm across2 gives0.0703125/0.703125. Paired-t sensitivity pHolm0.0624010/0.5010653, separately corrected. Source intervals are unadjusted t95% intervals, conditional on coefficient estimates, not propagated curve uncertainty. No significance stars.
- VERIFIED: DBM12 left β at lower bound1e-5, covariance condition~8e20; PSUIM10 left β~4.18 and DBM15 right β~1.08 have very poorly conditioned covariance. Original sparse/asymmetric coherence support limits individual4-param identifiability. Fit warnings/bound flags and individual curves exported. Do not exclude these mice ad hoc.
- VERIFIED: sensitivity fixes pulse asymptotes to individual control estimates as in existing pulse_psychometric_stage.py. It remains boundary-sensitive for DBM12 and changes meanα difference. Kept separate, no replacement/significance selection. Source sensitivity CSV/summary JSON.
- VERIFIED: all A source points/group coefficients/curves identical to v3; original time-course/assignment tables equal after B→C,C→D,D→E rename.20 parameter curves and WLS SSE independently recomputed; paired alignment and all1024 sign patterns/Holm verified. Source compiles; both focused/full PNGs inspected; full layout reports no text clipping.

## What didn't work
Independent4-param fits are too weakly constrained in several mice to make this a clean standalone parameter test. Shared asymptotes reduce extreme slopes but do not solve all midpoint instability. Neither β null nor corrected α result should be overstated. Fitting/plotting performed successfully; scientific uncertainty is retained rather than filtered away.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.review_pulse_results --output dissemination/paper_accumulation/draft_2026-11-15/figure4_revision_FRESH --fit-pulse-psychometric --extend-pulse-curves --paired-psychometric
```
New computation helper scripts/paper/pulse_paired_psychometrics.py; exact equation src/utils/pmf_utils.py. Source hashes/definitions in figure_manifest.json; independent checks in verification.json; primary/sensitivity provenance in PAIRED_PARAMETER_NOTES.md. Current output figure4_revision_2026-11-18_v4/, all prior outputs preserved.

## Caveats
Exploratory analysis added after inspecting data;10 independent mice, not thousands of independent trial estimates. Distributions of fitted differences include extreme values, and support differs by direction. α is dynamic-range midpoint, not necessarily P(right)=.5; rawβ tested despite log display. Uncertainty from curve estimation/asymptotes not propagated, no claim of attention or accumulation mechanism. Group display A is not averaged individual coefficients. No decision-model fit, new pulse simulation, package installation, commit or push.

## Open questions and next steps
- [ ] Author review paired B and whether to retain it given fit instability.
- [ ] If stronger parameter inference is needed, separately scope a justified joint/hierarchical psychometric analysis without cherry-picking exclusions or targets.
- [ ] Continue temporal panels C–E minor edits afterward.
