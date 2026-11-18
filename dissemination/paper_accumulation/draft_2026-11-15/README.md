# Figures-first paper draft

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

Started 15 November 2026; first writing packet completed 16 November 2026. Target audience: a Neuron research article. This is a working draft with author-specific details still to complete.

## Current author-reviewed Figure 1 — 17 November 2026

Selected: [Figure 1, A–D](figure1_revision_2026-11-17_v6/figure1.pdf). Physical pulse directions are explicit; C uses control points and the author’s four-parameter logistic; D uses left/right-choice mean control RTs, solid traces and pointwise SEM bands. Panel E was removed; exclusions remain in Methods. Source tables and verification accompany each preserved revision. Current captions, Methods and Results reflect this update. The combined PDF and Word/Markdown packets below remain the earlier writing packet and have not been regenerated.

Reproduce Figure 1 with `.venv/bin/python -m scripts.paper.review_figure1 --output <fresh-directory>`.

## Current figure organization

See [the figure review index](FIGURE_REVIEW_INDEX.md). Model introduction is now Figure 2, with control-model results separated as provisional Figure 3. Pulse figures will shift to Figures 4–5 when reviewed. Earlier packets retain their original numbering.

## Earlier writing packet

- [Four main figures, native-size PDF](figures_v5/main_figures.pdf)
- [Editable packet: figures, captions, Methods, Results and references](working_draft_v3.docx)
- [Same packet in Markdown](working_draft_v3.md)
- [Figure captions](figure_captions.md)
- [Methods](methods.md)
- [Results](results.md)
- [Writing models, skill attribution and unresolved facts](WRITING_NOTES.md)

The production order followed the author's instruction: figures → captions → Methods → Results. Introduction, Discussion, Summary and final title are the next writing phase. Earlier manuscripts and earlier layout versions are preserved; figures_v5 and working_draft_v3 are the selected versions for this packet.

## Scientific argument

Figure 1 establishes stimulus-guided behavior and introduces the pulse task; population exclusions are detailed in Methods. Figure 2 presents matched control-model discrimination and the completed fixed-data recovery. Figure 3 makes the sustained directional influence of brief motion pulses a central result, retaining the later decline. Figure 4 compares pulse and RT predictions, showing individual discrepancies, cohort uncertainty and the concentration of one matched score tradeoff.

The Results uses the question → comparison → observation → bounded inference structure found in the primary decision-making papers listed in `evidence/writing_models.json`. The prose is original. Historical rules are not reintroduced as approval gates.

## Provenance and checks

- `figures_v5/source_data/`: 23 panel-level tables.
- `figures_v5/figure_manifest.json`: source hashes, populations, figure dimensions and layout checks.
- `evidence/control_fit_settings.json`: settings/hashes read from 400 existing control fit files.
- `source_manifest.json`, `claims_v3.csv`, `evidence/annotated_draft_v3.md`: paragraph/source mapping and text hashes. Source verification is recorded honestly as pending human review; `evidence/agent_inspection.json` records assistant inspection separately.
- `consistency_manifest_v2.json`: repeated values and method/result mappings.
- `references.bib`, `references.md`, `evidence/reference_metadata.json`: primary bibliographic records and formatted references.
- `audit_v3/`: final structural, reference, consistency and artifact checks. Submission-oriented claim/language audits remain open for human verification and policy review. Passing structure checks is not a claim of scientific or publication approval.

No new decision-model fits or simulations were run for this packet. Original data, fit files and results were not changed. The only shared plotting change defers a replay-related import until trial loading is requested, allowing plotting from existing tables without an unavailable OpenCV system library.

## Reproduce without overwriting

From `/src`, using the existing project environment:

```bash
.venv/bin/python -m scripts.paper.build_paper_2026_11_15 --output /tmp/mouse_paper_figures_reproduction
```

The output directory must not already exist. To package a later prose revision in the dated draft folder, use a new revision label:

```bash
.venv/bin/python -m scripts.paper.package_paper_2026_11_15 --revision v4
```

The package command expects the selected figure set and existing reference/source records. It refuses to overwrite that revision's packet. The initial packaging command is for a fresh workspace and will refuse to replace existing deliverables.

## Figure descriptions

**Figure 1:** A mouse reports motion direction at one of two lick ports. Pulse timing differs between task implementations. Individual psychometric functions follow motion direction. RT summaries distinguish outcomes, and the trial-flow panel gives each analysis population.

**Figure 2:** Mouse-level held-out scores favor accumulation on average over matched rapid-forgetting and sample-extrema models, mostly through RT terms. A full five-candidate recovery matrix and dependent cohort recombinations show the strategy-discrimination check.

**Figure 3:** Pulse direction changes choices and retains a directional influence after the pulse. The dilution-adjusted readout decreases for later responses. A separate panel displays the assignment-based directional endpoint and its mouse-level interval.

**Figure 4:** Selected fitted models predict different pulse trajectories. Individual pulse effects and the cohort mean are shown alongside matched choice/RT score differences. RT-quantile contributions and one explicitly selected diagnostic distribution locate the major RT constraint.

Current Figure3B preview: [control psychometric and choice-conditioned RT model overlays](figure3B_control_fits_2026-11-18/figure3B.pdf), with [caption](figure3B_control_fits_2026-11-18/caption.md). Author rejects earlier decomposition B. Predictions use saved full-control parameters (descriptive in-sample), not held-out curves. Five candidates; data points/SEM, model lines. One extra Figure1 missing-timing control is absent from modeled population and documented. B awaits author review; A alternatives unchanged.

Latest B: [model C psychometric and chronometric fits](figure3B_model_C_2026-11-18/figure3B_model_C.pdf), [caption](figure3B_model_C_2026-11-18/caption.md). Author chooses C alone, superseding the five-model B preview for current review. Full-control parameters/curves; held-out scores in A assess unseen controls. Pulse deferred. B awaits author review.

Current smooth-psychometric B: [model C artwork](figure3B_model_C_logit4_2026-11-18/figure3B_model_C.pdf), [caption](figure3B_model_C_logit4_2026-11-18/caption.md). Author logit_4 curves fitted separately to data and model C group probabilities; raw data points and RT plot unchanged. Coefficients/dense curves exported. Descriptive smoothing does not refit DDM parameters. Supersedes joined-segment psychometric preview for current review.

Held-out RT diagnostic (not yet a manuscript panel): [plot](control_rt_score_diagnostic_2026-11-18_v2/control_rt_diagnostic.pdf), [results](control_rt_score_diagnostic_2026-11-18_v2/RESULTS.md). Exact C/E/ES CV score decomposition and matched conditional-quantile errors explain mean-fit versus score ranking. Existing A/B untouched; author to decide placement.

Supplementary draft selected by author: [held-out control RT diagnostic](supplement_control_rt_diagnostic_2026-11-18/README.md), with [figure](supplement_control_rt_diagnostic_2026-11-18/control_rt_diagnostic.pdf) and [caption](supplement_control_rt_diagnostic_2026-11-18/caption.md). Further refinement pending; supplementary number unassigned. Source values/checks unchanged. This supersedes the earlier placement-undecided note for this diagnostic; it is separate from main Figure 3B.

Control-C shallow-slope sensitivity/local restart pilot completed: [results and provenance](control_C_optimization_pilot_2026-11-18/README.md), [diagnostic](control_C_optimization_pilot_2026-11-18/summary_v2/optimization_pilot.pdf). No useful consistent independent joint-score gain; original manuscript fits/artwork retained. This is exploratory diagnostics, not an additional selected manuscript figure.

## Selected Figure 3D — 18 November 2026

Author approved the [exponential conditional-accuracy panel](figure3_exponential_2026-11-18/figure3D_exponential.pdf), with [caption](figure3_exponential_2026-11-18/caption.md) and [acceptance record](figure3_exponential_2026-11-18/acceptance.json). Figure 3 now comprises A: model comparison (both accepted alternatives retained); B: model C psychometric/chronometric fits; C: model recovery; D: conditional accuracy with descriptive exponential fits. Main shading is data SEM, not fitted-curve uncertainty. Weak-coherence time constants remain poorly identified. This supersedes earlier candidate-D/selection-pending notes. The former cohort-recovery D remains in Results text. Final A choice and combined artwork assembly remain pending.

## Figure3 working order approved — 18 November 2026

Current order: **A conditional accuracy** (previous D), **B model comparison** (previous A), **C model fits** (previous B), **D model recovery** (previous C). [Current preview](figure3_story_order_2026-11-18/figure3_A1.png), [bits/BIC alternative](figure3_story_order_2026-11-18/figure3_A2.png), [captions in current order](figure3_story_order_2026-11-18/captions.md), and [mapping/source notes](figure3_story_order_2026-11-18/README.md). Both comparison alternatives remain open. Layout is provisional; earlier panel-letter references are historical. Source hashes, PNG dimensions and SVG structure verified in verification.json.
