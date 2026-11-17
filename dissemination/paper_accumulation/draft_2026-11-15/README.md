# Figures-first paper draft

Started 15 November 2026; first writing packet completed 16 November 2026. Target audience: a Neuron research article. This is a working draft with author-specific details still to complete.

## Current author-reviewed Figure 1 — 17 November 2026

Selected: [Figure 1, A–D](figure1_revision_2026-11-17_v6/figure1.pdf). Physical pulse directions are explicit; C uses control points and the author’s four-parameter logistic; D uses left/right-choice mean control RTs, solid traces and pointwise SEM bands. Panel E was removed; exclusions remain in Methods. Source tables and verification accompany each preserved revision. Current captions, Methods and Results reflect this update. The combined PDF and Word/Markdown packets below remain the earlier writing packet and have not been regenerated.

Reproduce Figure 1 with `.venv/bin/python -m scripts.paper.review_figure1 --output <fresh-directory>`.

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
