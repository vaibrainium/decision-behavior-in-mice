# Report: Figure 2 initial walkthrough
Date: 2026-11-17   Agent: Codex   Commit: 9f21e7f
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
After checkpointing Figure 1, begin author review of Figure 2.

## Summary
VERIFIED: inspected figures_v5/figure2.png, current caption, build code and cohort source CSV. Figure concerns matched control-model discrimination and completed paired recovery. No Figure 2 edits or new inference performed. Recommendation: explain model operations before presenting likelihood comparisons; retain RT score decomposition and recovery.

## Findings
- VERIFIED: A shows normalized held-out differences against the accumulator; positive favors accumulation. B splits those differences into choice/RT components. Source: figures_v5/source_data/fig2_AB_* and scripts/paper/build_paper_2026_11_15.py figure2.
- VERIFIED: C shows fixed-dataset recovery across five candidates, whereas D shows dependent cohort recombinations, not independent simulations. Source: fig2_C_recovery.csv and fig2_D_recombined_cohorts.csv; current caption. Original correction implementation is documented in scripts/ddm/recovery_cohorts.py (rep columns apply Holm).
- JUDGMENT: add a compact conceptual model schematic and clearer model names to orient readers before scores. Exact layout not yet chosen by author. Interpretation stays relative to tested models.

## What didn't work
No Figure 2 build was attempted; existing artwork is the current starting point.

## How to reproduce
View dissemination/paper_accumulation/draft_2026-11-15/figures_v5/figure2.png and read the Figure 2 caption and adjacent fig2_* source CSVs. Existing full builder can export to a fresh directory; no rerun required for this discussion.

## Caveats
Author-side initial review; no new statistical claims or journal-compliance certification. Recovery is conditional on tested candidates and parameters; recombined cohorts reuse simulated datasets.

## Open questions and next steps
- [ ] Review Figure 2 organization and model schematic with author.
- [ ] Implement chosen edits in a preserved new revision and show in chat.

## Panel A redesign
2026-11-17 author requests a full Figure 2 redo, beginning with model introduction A inspired by “stein”; interpreted as Stine et al. 2020 in the established conversation context. VERIFIED primary source: https://pmc.ncbi.nlm.nih.gov/articles/PMC7217695/, Figure 1 caption and Results model definitions; published figure visually inspected at https://cdn.elifesciences.org/articles/55365/elife-55365-fig1-v2.jpg. Publisher article HTML challenged; PMC text/CDN image accessible. Original drawing, no copied artwork.

Selected A draft: figure2A_revision_2026-11-17_v3. It shows C accumulation, E rapid leakage, and ES sample-by-sample threshold detection with identical constructed increments above each. No snapshot included. Rule sources: src/ddm/simulator.py _simulate_ddm_trials_numba and scripts/ddm/primacy.py; fixed-control specification in current methods.md. The shared sensory/response components are omitted, not removed from fits. DDMx/ESx remain reference implementations within these families and are not extra decision rules in A.

VERIFIED: C is cumulative sum; E matches an independently computed geometric convolution; ES uses instantaneous samples, with no connecting state trajectory. Every plotted trajectory ends at its first threshold crossing. Construction settings, coordinates, source hashes and checks accompany output. These illustrative trajectories are not empirical evidence or fitted model predictions. Thresholds are arbitrary (not claimed to match fitted bounds/ranges); E illustrative decay is within the actual fitted range. Caption.md explains the zero-mean interval and deliberate extreme sample. Render v3 inspected with visible markers; prior layout drafts preserved (v2 had a clipped ES marker, corrected by changing the explicitly illustrative construction in v3). No biological fits or group inference.

Reproduce: `.venv/bin/python -m scripts.paper.figure2_models --output <fresh-directory>`. Base commit b7fcfe9; current A edits uncommitted. Full Figure 2 and its old caption remain preserved until remaining panels are rebuilt. Next: author assess A, then redesign B onward.

## Five-implementation labels
2026-11-17 author asks about DDMx/ESx and approves their inclusion within the corresponding decision-rule families. Export v4 labels C/DDMx, E, ES/ESx, with notes distinguishing motion-energy versus nominal-coherence inputs and inclusion versus omission of drift variability/fast guesses. Updated standalone caption adds the reference integrator starting-point detail and explicitly avoids implying identical fitted predictions within a family. VERIFIED: all schematic coordinates identical to v3, all five labels present, render inspected. Source: v4/verification.json, schematic_manifest.json, caption.md; implementation basis in current Methods. No new behavioral fits. Reproduce scripts.paper.figure2_models with a fresh output directory. Base b7fcfe9, changes uncommitted. Next: author assess A before B.

## Separate model and results figures
2026-11-17 author approves separate figures. Current Figure 2: figure2_models_2026-11-17, with A three decision-rule schematics and B a compact five-implementation table replacing repeated prose. Table reports inclusion of across-trial drift variability and fast guesses, not whether fitted parameters differ from zero; within-trial noise is present in every candidate. Adjacent caption records this distinction and the reference integrator starting-point detail. Selected model coordinates are identical to prior v4; no fitted predictions implied. Figure visually inspected.

Current provisional Figure 3: figure3_control_results_2026-11-17, exported with scripts.paper.review_control_results. This separates/renumbers the existing likelihood comparison, choice/RT decomposition and completed recovery; it is a starting layout, not a completed results redesign. All source tables numerically identical to figures_v5's old Figure 2 after prefix renaming. Caption and manifests adjacent; render inspected. Observed-versus-predicted choice/RT panels remain pending. No new model fits, biological analyses or raw-data changes.

Organization and reproduction: draft_2026-11-15/FIGURE_REVIEW_INDEX.md. Proposed numbering: 1 task, 2 models, 3 control results, 4 pulse influence, 5 pulse/RT constraints. Existing full manuscript/Word/source ledgers retain old numbering pending selection of revised artwork; no claim that global renumbering is complete. README flags this. Base b7fcfe9, current work uncommitted. Next: author assess model Figure 2, then redesign results Figure 3 using existing predictions and comparison/recovery outputs.

## Accepted checkpoint
2026-11-17 author accepts the standalone model figure and requests commit/progression. Model scripts, all preserved schematic versions, selected Figure 2, separate provisional Figure 3, captions, sources and figure index committed as a20629e. No push. Python compilation, scoped whitespace checks, JSON reads and adjacent source-identity checks passed. Next review begins in reports/2026-11-17-figure3-review.md.
