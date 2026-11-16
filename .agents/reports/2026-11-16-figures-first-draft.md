# Report: figures-first manuscript packet and decision-making writing models
Date: 2026-11-16   Agent: Codex   Commit: b63c9d9 (base; new scripts/draft uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Start the paper using repository skills, follow the author's figures → captions → Methods → Results order, and adopt the language/structure of comparable decision-making papers.

## Summary
VERIFIED DELIVERABLE: first writing packet complete in `dissemination/paper_accumulation/draft_2026-11-15/`. Selected artwork is figures_v5; selected editable packet is working_draft_v3.docx. Sustained directional pulse influence remains central. Completed recovery and the matched score diagnosis are included. No new model fits/simulations or package installation. Introduction, Discussion, Summary and final title remain the next writing phase; full manuscript/submission completion is not claimed.

## Findings and decisions
- VERIFIED: four main figures exported as PDF, editable SVG and opaque 300-dpi PNG; combined native-size PDF and 23 panel-level source tables. Source: `figures_v5/figure_manifest.json`; command below. Layout versions are preserved. Core figures were visually inspected; final model figure rechecked after adding the existing cohort-mean interval.
- VERIFIED: figure argument is task/population → matched control discrimination/recovery → sustained pulse influence → joint pulse/RT constraints. Captions distinguish descriptive control responses (14,015) from model control responses (14,014), response-conditioned temporal observations (19,313) from the scheduled endpoint, mouse bootstrap from within-mouse intervals, and dependent recovery recombinations. Sources: figure manifest/panel tables; existing complete-results inventory and reports cited in the manuscript source ledger.
- VERIFIED: Methods settings were read back from 400 existing control fit files, not inferred solely from current defaults. Source: `evidence/control_fit_settings.json`; input inventory `dissemination/reviewer_2026-11-13/control_fold_inventory.csv`. Saved settings uniformly use 15 simulation repetitions and the responded-only nine-bin objective in the inspected control comparisons. No fitting rerun.
- VERIFIED METHOD CLARIFICATION: session-selection `var` is a logistic slope, not statistical variance. Source: `src/utils/pmf_utils.py logit_4()/fit()`, `config/main.yaml`, preprocessing notebook cell 12. Draft reports the performed filter and distinguishes its legacy response-dependent control label from downstream scheduled labels. No raw filtering changed.
- VERIFIED: editable packet contains four images and two editable Word math objects. The plain-text draft, separate captions/Methods/Results and current references accompany it. Source: `audit_v3/artifact_checks.json` and `draft_manifest_v3.json`.
- VERIFIED: 77 paragraph/line claims are mapped to source IDs with text hashes; assistant source inspection and pending human verification are recorded separately. No human verifier or author approval was fabricated. Source: `claims_v3.csv`, `evidence/annotated_draft_v3.md`, `source_manifest.json`.
- VERIFIED: source/manuscript schemas, local reference-identifier checks and the declared numeric/method-result consistency check pass. Remaining claim-audit findings concern uncompleted human verification; draft-lint findings concern uncompleted confidentiality/policy-review records. These are publication-readiness records, not new gates blocking authorized drafting. Source: `audit_v3/summary.json`. Local source entries have no public DOI; warnings are retained rather than assigning invented identifiers.

## Comparable-paper writing review
Primary source passages inspected and exact access notes are in `evidence/writing_models.json`.
- Huk & Shadlen 2005 (original PDF, behavioral persistence and bounded-model sections): positive persistence finding first, model interpretation afterward. https://doi.org/10.1523/JNEUROSCI.4684-04.2005
- Stine et al. 2020 (primary PMC and full XML): operational alternatives, discriminating comparison and simulation validation before interpreting the fitted strategy. https://pmc.ncbi.nlm.nih.gov/articles/PMC7217695/
- Odoemene et al. 2018 (primary PMC Results): task/behavior first, finding-based headings and explicit links from one scientific question to the next. https://pmc.ncbi.nlm.nih.gov/articles/PMC6246883/
- Stine et al. 2023, Neuron (primary PMC Results): compact task description, hypothesis-driven comparison and calibrated transitions from observation to mechanism. https://pmc.ncbi.nlm.nih.gov/articles/PMC10565788/
- Roy et al. 2021, Neuron (primary full-text indexed extraction, partial access): explain the model through its behavioral purpose; distinguish predictive description from mechanism. Direct PMC open challenged, full XML unavailable, author-lab page returned 502. Do not describe this as a complete full-text reading. https://pmc.ncbi.nlm.nih.gov/articles/PMC7897255/

JUDGMENT/APPLICATION: use question → comparison → figure-linked observation → short inference. Keep technical bookkeeping in Methods/captions and give the sustained pulse result a clear positive conclusion. No distinctive prose was copied, and neural causal claims from comparator papers were not imported into this behavioral study.

## What did not work
- Importing the old shared plotting module eagerly imported the replay pipeline/OpenCV, which failed because libGL.so.1 is absent. Moved the same import inside load_trials(); this preserves that function's behavior and enables plotting-only imports. New figures use the already exported behavior tables. No dependency installation.
- Optional citation CLI could not import requests. Retrieved public Crossref work records with the standard library and used the citation skill's dependency-free BibTeX renderer. Complete Adelson–Bergen pagination was enriched from its primary PubMed record. Source: `evidence/reference_metadata.json` / `bibliography_enrichment.json`.
- Neuron author page returned 403. Exact current format limits are not asserted; figures and STAR Methods structure are provisional. ARRIVE official guidance was accessible. This does not block a working draft.
- Initial layout placed legends over data and counted off-axis auto-ticks as clipped text. Preserved versions, moved/shortened legends and screened only displayed text. Source: figure-builder revision history recorded by the plan log and final figure manifest.
- Submission-oriented validation cannot pass without human verification/declarations. Do not relabel expected open records as a completed scientific or publication approval.

## How to reproduce
Existing source data and base commit are recorded above. All paths below are under `/src`.

```bash
.venv/bin/python -m scripts.paper.build_paper_2026_11_15 --output /tmp/mouse_paper_figures_reproduction
.venv/bin/python -m scripts.paper.package_paper_2026_11_15 --revision v4
.venv/bin/python .claude/skills/scientific-writing/scripts/validate_manifest.py dissemination/paper_accumulation/draft_2026-11-15/manuscript_manifest_v3.json --kind manuscript
.venv/bin/python .claude/skills/scientific-writing/scripts/check_consistency.py dissemination/paper_accumulation/draft_2026-11-15/consistency_manifest_v2.json
.venv/bin/python .claude/skills/scientific-writing/scripts/check_references.py dissemination/paper_accumulation/draft_2026-11-15/source_manifest.json
```

Use fresh output paths/revision labels. Actual selected builds used figures_v5 and packet revision v3. Figure source hashes match inspected inputs. Metadata requests contained public paper identifiers only; unpublished text/data were not placed in searches or sent to another external service. No raw data/previous model outputs changed, no cluster jobs submitted, no git commit/push performed.

## Caveats
This is a first writing packet, not a final journal submission. Five author-detail blocks remain in Methods (animal/ethics, design/blinding, apparatus/training, lead contact/materials/access facts); authorship/declarations remain unapproved. Source verification is assistant inspection, not named-human verification. Word package structure/math/images were checked, but an Office/PDF prose renderer was unavailable; actual Word pagination has not been certified. Figures were inspected as rendered PNGs with source-linked vector exports. Fit uncertainty and filtering limitations remain as stated in the scientific reports.

## Open questions and concrete next steps
- [ ] Continue from this packet to Introduction, Discussion, Summary and final title, maintaining the accumulation-first argument and source-backed claim strength.
- [ ] Resolve author-supplied animal/ethics/task facts and final resource/declaration statements without inventing boilerplate.
- [ ] Select supporting figures/tables from the preserved model, history/state, delay/gain and replay analyses; keep their exploratory status visible.
- [ ] Recheck current Neuron instructions and review Word pagination/final artwork in the authoring application before submission preparation.
