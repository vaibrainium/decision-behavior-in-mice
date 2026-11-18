# Author-reviewed figure organization — 17 November 2026

## Current review: Figure 4 — pulse influence

Figure3 A–C panel review is checkpointed; A alternative choice remains deferred. Next: [pulse-influence Figure4 preview](figure4_pulse_review_2026-11-18/figure4.pdf), [caption](figure4_pulse_review_2026-11-18/caption.md). A: pulse psychometrics; B: directional/shared response-conditioned time course; C: dilution-adjusted influence; D: assignment-based directional contrast. Existing results/source values preserved. Start author review with A; this supersedes the earlier pointer to figures_v5/figure3.pdf for current preview only. Global manuscript numbering remains pending.

## Figure 3 panels approved — 18 November 2026

A: [both finalized alternatives](figure3A_final_alternatives_2026-11-17/README.md), final choice deferred. B: [approved model C fits](figure3B_final_2026-11-18/README.md). C: [approved recovery matrix](figure3C_final_2026-11-18/README.md). Former D result is in Results text only. All A–C panel reviews complete; combined figure assembly pending. This supersedes older C-review-pending notes below.

## Current Figure 3 layout — A–C

A: held-out model comparison with QMLE-based BIC (both accepted alternatives retained). B: approved model C psychometric/chronometric fits. C: model-recovery matrix (review pending). Cohort-level recombination recovery is reported in the [Results text](cohort_recovery_text_2026-11-18/results_paragraph.md), **not a figure panel**. This author decision supersedes older D preview/placement notes below. Earlier artwork remains archived.

## Approved Figure 3B — 18 November 2026

[Accepted model C psychometric/chronometric panel](figure3B_final_2026-11-18/figure3B_model_C.pdf), [caption and source record](figure3B_final_2026-11-18/README.md). Author approved the smooth four-parameter psychometric version. Original full-control C estimates retained; optimization pilot not adopted. This supersedes older B-preview status below. Next: panel C recovery.

## Finalized Figure 3A alternatives — selection pending

Both dual-axis versions are author-finalized and included in [figure3A_final_alternatives_2026-11-17](figure3A_final_alternatives_2026-11-17/README.md): [LL/BIC](figure3A_final_alternatives_2026-11-17/A1_ll_bic_dual_axis.pdf) and [bits/BIC](figure3A_final_alternatives_2026-11-17/A2_bits_bic_dual_axis.pdf). Keep both as alternatives for the same panel A. Author will choose later. This decision supersedes older preview-selection notes below.

This working figure organization supersedes the earlier four-figure outline. The earlier combined PDF, Word packet, paragraph/source maps and manuscript figure numbering are preserved until the revised artwork is selected. They have not been globally renumbered.

1. Figure 1: task and control behavior — figure1_revision_2026-11-17_v6/figure1.pdf (accepted checkpoint).
2. Figure 2: candidate decision models — figure2_models_2026-11-17/figure2.pdf. A: three rule schematics; B: five-implementation comparison. Illustrative trajectories only.
3. Figure 3: control-model results — figure3_control_results_2026-11-17/figure3.pdf. Existing comparisons and completed recovery, separated and renumbered as a starting point. Full results redesign and observed-versus-predicted behavior panels remain pending.
4. Proposed Figure 4: pulse influence — currently figures_v5/figure3.pdf, awaiting review and artwork/caption renumbering.
5. Proposed Figure 5: joint pulse/RT constraints — currently figures_v5/figure4.pdf, awaiting review and artwork/caption renumbering.

Captions and source manifests are adjacent to the new figures. Each figure's underlying observations/results are preserved. This is an author-approved organization, not a claim about journal figure limits.

Reproduce into fresh directories with scripts.paper.figure2_models and scripts.paper.review_control_results, each using --output.

## Current Figure 3 panel review

Author requests absolute NLL in A. Proposed panel: figure3A_raw_nll_2026-11-17/figure3A.pdf, with raw five-fold NLL totals per mouse and all five candidates. The existing full Figure 3 remains a starting layout; this panel is not yet assembled with revised B onward.

Current panel-by-panel Figure 3A preview: figure3A_raw_nll_bars_2026-11-17_v2/figure3A.pdf (direct held-out NLL, no subtraction/normalization; source uses per-mouse bars). Stine 2020 Figure 7B was inspected for style; its metric is ΔBIC. Earlier full Figure 3 and raw-point preview are preserved.

Latest Figure 3A: figure3A_group_nll_2026-11-17/figure3A.pdf, single five-bar cohort mean raw NLL ± SEM panel at author request. Per-mouse previews remain preserved; trial counts differ and the caption defines the descriptive aggregation.

Current A correction: figure3A_group_nll_no_sem_2026-11-17/figure3A.pdf. Raw mean bars unchanged; SEM removed because uncentered between-mouse variation does not show paired model-comparison uncertainty. Existing normalized paired tests are documented separately, including t/Wilcoxon differences.

Current point-display A: figure3A_group_nll_points_2026-11-17_v3/figure3A.pdf. Same raw mean scores, no error bars, labeled nonzero NLL limits. Earlier bars preserved.

Current A: figure3A_group_nll_connected_2026-11-17/figure3A.pdf — same raw mean points, now connected by an author-requested visual-guide line.


Current B/C preview: figure3_information_metrics_panels_2026-11-17/bits_and_delta_bic.pdf — joint held-out choice + RT log score in bits/trial (higher better), and mean QMLE-based ΔBIC relative to C (lower better). Same five connected points/no error bars as A. Author assessment pending. Individual figures, full source tables, checks and captions: figure3_information_metrics_2026-11-17/. Separate test_choice_gain_bits.pdf implements the Ashwood GLM-HMM choice-only training-bias-null convention; it is not the joint choice/RT metric. BIC uses independent full-training fixed-parameter scoring, never CV NLL. See .agents/reports/2026-11-17-figure3-bits-bic.md from repo root for reproducibility/caveats. Earlier Figure 3 unchanged.

Current C at author request: figure3_absolute_bic_2026-11-17/absolute_bic.pdf (absolute mean QMLE-based BIC; no reference subtraction). Same verified scores, five connected points, no error bars. Previous ΔBIC preview preserved. Author assessment pending.

Panel A alternatives requested after absolute BIC: figure3A_metric_alternatives_2026-11-17/A1_nll_bic_dual_axis.pdf and A2_bits_bic_side_by_side.pdf. A1 uses left test NLL/right training QMLE BIC axes; A2 uses left joint test bits/right separate BIC subpanel. Both provisional pending author selection; source/captions/manifests adjacent.

Latest A1: figure3A_metric_alternatives_ll_2026-11-17/A1_ll_bic_dual_axis.pdf — author-requested LL = −NLL on left, higher better; BIC unchanged on right.

Latest panel A alternatives: figure3A_both_dual_axes_2026-11-17/A1_ll_bic_dual_axis.pdf and A2_bits_bic_dual_axis.pdf. BOTH use left/right y-axes per author clarification; supersede separate-right-panel interpretation. No score changes.

Current Figure3B preview: [control psychometric and choice-conditioned RT model overlays](figure3B_control_fits_2026-11-18/figure3B.pdf), with [caption](figure3B_control_fits_2026-11-18/caption.md). Author rejects earlier decomposition B. Predictions use saved full-control parameters (descriptive in-sample), not held-out curves. Five candidates; data points/SEM, model lines. One extra Figure1 missing-timing control is absent from modeled population and documented. B awaits author review; A alternatives unchanged.

Latest B: [model C psychometric and chronometric fits](figure3B_model_C_2026-11-18/figure3B_model_C.pdf), [caption](figure3B_model_C_2026-11-18/caption.md). Author chooses C alone, superseding the five-model B preview for current review. Full-control parameters/curves; held-out scores in A assess unseen controls. Pulse deferred. B awaits author review.

Current smooth-psychometric B: [model C artwork](figure3B_model_C_logit4_2026-11-18/figure3B_model_C.pdf), [caption](figure3B_model_C_logit4_2026-11-18/caption.md). Author logit_4 curves fitted separately to data and model C group probabilities; raw data points and RT plot unchanged. Coefficients/dense curves exported. Descriptive smoothing does not refit DDM parameters. Supersedes joined-segment psychometric preview for current review.

Held-out RT diagnostic (not yet a manuscript panel): [plot](control_rt_score_diagnostic_2026-11-18_v2/control_rt_diagnostic.pdf), [results](control_rt_score_diagnostic_2026-11-18_v2/RESULTS.md). Exact C/E/ES CV score decomposition and matched conditional-quantile errors explain mean-fit versus score ranking. Existing A/B untouched; author to decide placement.

Supplementary draft selected by author: [held-out control RT diagnostic](supplement_control_rt_diagnostic_2026-11-18/README.md), with [figure](supplement_control_rt_diagnostic_2026-11-18/control_rt_diagnostic.pdf) and [caption](supplement_control_rt_diagnostic_2026-11-18/caption.md). Further refinement pending; supplementary number unassigned. Source values/checks unchanged. This supersedes the earlier placement-undecided note for this diagnostic; it is separate from main Figure 3B.

Control-C shallow-slope sensitivity/local restart pilot completed: [results and provenance](control_C_optimization_pilot_2026-11-18/README.md), [diagnostic](control_C_optimization_pilot_2026-11-18/summary_v2/optimization_pilot.pdf). No useful consistent independent joint-score gain; original manuscript fits/artwork retained. This is exploratory diagnostics, not an additional selected manuscript figure.

Current D clarity redesign: [direct-label cohort recovery](figure3D_intuitive_2026-11-18/figure3D.pdf), [caption](figure3D_intuitive_2026-11-18/caption.md). Generator→group-preference rows with identical existing percentages for C-vs-E and C-vs-ES. Draft pending author review/placement; A/B unchanged.

## Selected Figure 3D — 18 November 2026

Author approved the [exponential conditional-accuracy panel](figure3_exponential_2026-11-18/figure3D_exponential.pdf), with [caption](figure3_exponential_2026-11-18/caption.md) and [acceptance record](figure3_exponential_2026-11-18/acceptance.json). Figure 3 now comprises A: model comparison (both accepted alternatives retained); B: model C psychometric/chronometric fits; C: model recovery; D: conditional accuracy with descriptive exponential fits. Main shading is data SEM, not fitted-curve uncertainty. Weak-coherence time constants remain poorly identified. This supersedes earlier candidate-D/selection-pending notes. The former cohort-recovery D remains in Results text. Final A choice and combined artwork assembly remain pending.
