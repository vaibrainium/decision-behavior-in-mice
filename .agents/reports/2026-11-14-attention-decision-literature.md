# Report: attention, history and decision variability literature review
Date: 2026-11-14   Agent: Codex   Commit: b63c9d9 (review code/output uncommitted)
Plan: plans/2026-11-14-attention-decision-literature.md

## Question
After the negative response-delay pilot, which literature-supported analysis should be done next to explain the joint RT/pulse mismatch using existing data?

## Summary
Recommendation revised: investigate predictable history bias and persistent behavioral regimes before interpreting iid gain as attention. Positive evidence gain remains a compact simulation/fitting candidate; it is not itself a novel mechanism or an identified attentional process. Test a history-dependent accumulation-bias account against starting-point history and structured sensitivity alternatives, with a scoring target that can actually detect temporal ordering.

## Findings
- VERIFIED bibliographic scope: 32 selected reference records, including theoretical/background reviews and prior accumulation comparators; 26 fresh Crossref DOI identity checks; 10 XML bodies plus selected author-PDF/PMC assessment. This is a purposive narrative review, not a complete screening count. Sources: `dissemination/attention_decision_review_2026-11-14/evidence_matrix.csv`, `bibliography_audit.json`, retrieval/search logs. BibTeX validation: no errors/duplicates; two low-level article-identifier warnings preserved. Source: `bibtex_verified_validation.json`.
- VERIFIED literature: Ashwood 2022 and Hulsey 2024 support persistent mouse behavioral strategies with external RT/omission or physiological validation; Roy 2021 provides a continuous alternative. Urai 2019 supports testing ongoing history-dependent drift bias rather than presuming only starting-point shifts. Details/limitations/citations in REVIEW and evidence matrix.
- VERIFIED literature: attention can affect sensitivity, encoding/decision onset, integration and sensory noise; the failed pure postdecision-delay model did not test those mechanisms. Goris 2014 supports examining gain persistence without identifying attention. McGaughey & Gold 2026 is a close RDK encoding-versus-integration comparator, but its sensory/pupil observations do not identify this dataset's mechanism.
- VERIFIED repository context: substantial history effects are already reported in `reports/2026-10-29-behavior-exploration.md`; new work should test their dynamic choice/RT predictions. Generic GLM-HMM code exists, including a different human/color-task configuration; a validated aligned mouse pulse/RT state fit was not located in the inspected outputs/reports. The aligned trial table includes history/session/position but no pupil/movement columns. This does not prove no independent recording exists elsewhere.
- INFERENCE / RECOMMENDATION: prioritize history-conditioned bias versus RT, residual persistence and pretrial state prediction; run a bounded gain feasibility study; then fit one supported alternative. Current condition-pooled likelihood cannot establish the correct ordering of latent states. Do not infer attention, a precise memory cutoff or a circuit mechanism from fit alone.

## What didn't work
- Europe PMC XML returned HTTP 500 for several author manuscripts; publisher pages sometimes presented bot challenges. Some were recovered through author PDFs or PMC web text; access depth is labeled.
- The JATS helper's broad contributor extraction can include editors/reviewers in eLife files. Bibliography authors instead use authoritative Crossref/Europe PMC records and preserve collective authors.
- Repo `.venv` lacks `requests`, required by citation scripts. Existing system Python includes it and was used without installing/upgrading anything.
- Bibliography warnings initially mixed actual electronic-page ranges, article identifiers and missing preprint fields. True ranges/locator/type were corrected in a separate verified bibliography; identifier hyphens and absent preprint volume/pages were preserved.

## How to reproduce
See `dissemination/attention_decision_review_2026-11-14/README.md`. `retrieve.py` fetches selected public full texts/metadata and Crossref records; `build_evidence.py` joins saved authoritative metadata to manually assessed findings; `verify_bibtex.py` applies documented metadata corrections; the pinned citation validator checks the final bibliography. Search strings and extra database URLs are saved in JSON. All scientific recommendations are explicitly proposals, not fitted outcomes.

## Caveats
Single-reviewer narrative selection, heterogeneous tasks/species, variable full-text access, and limited correction/retraction checks. No meta-analysis or new behavioral statistics. Pupil/arousal/attention associations in other tasks do not identify their source here. Existing randomized pulse effects and response-conditioned pulse profiles have different causal interpretations.

## Open questions and next steps
- [ ] Implement chronology-aware history-conditioned choice-bias/RT diagnostics, using existing history findings rather than repeating their discovery.
- [ ] If residual persistence remains, compare static history, continuous changes and a small state model; infer current state from past information for pulse predictions.
- [ ] Forward-test positive sensory gain with the existing schedules, response mapping and pulse estimators before another fit campaign.
- [ ] Only after a candidate meets both RT and pulse constraints, undertake recovery/parameter uncertainty and full-cohort publication validation.
