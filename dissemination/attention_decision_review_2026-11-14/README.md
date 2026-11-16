# Attention and decision-making review

Start with [REVIEW.md](REVIEW.md). The conclusion is to prioritize existing-data history/state diagnostics, then a bounded gain feasibility study, rather than interpret a new gain parameter as attention.

- [NEXT_ANALYSES.md](NEXT_ANALYSES.md): ranked, concrete follow-up analyses; scoring and inference pitfalls.
- [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) / [CSV](evidence_matrix.csv): source finding, design, assessment depth, limitation and proposed test.
- [references_verified.bib](references_verified.bib): source-verified reference export, including correct preprint status and collective authors. The first export is preserved as `references.bib`.
- `search_log.json`, `supplementary_search_log.json`: dated web/OpenAlex queries and bounded retrievals.
- `metadata.json`, `metadata_enriched.json`: authoritative Europe PMC records; initial and enriched versions preserved.
- `retrieval_log.json`, `additional_metadata_provenance.json`: public API endpoints, access failures and metadata retrievals.
- `citation_identity_checks.json`, `bibliography_audit.json`, `bibliography_normalizations.json`, `bibtex_verified_validation.json`: identity, provenance and formatting checks.

This is a focused critical narrative synthesis, not an exhaustive systematic review or meta-analysis. It includes theoretical/background reports and references assessed in the earlier review. Access depth is explicitly labeled. The ignored `sources/` folder contains public retrieval caches; no unpublished mouse data were uploaded.

Reproduction from `/src` (network calls retrieve public scholarly content only):

```bash
.venv/bin/python dissemination/attention_decision_review_2026-11-14/retrieve.py --fetch
.venv/bin/python dissemination/attention_decision_review_2026-11-14/retrieve.py --crossref
python3 dissemination/attention_decision_review_2026-11-14/build_evidence.py
python3 dissemination/attention_decision_review_2026-11-14/verify_bibtex.py
python3 .claude/skills/citation-management/scripts/validate_citations.py dissemination/attention_decision_review_2026-11-14/references_verified.bib --report dissemination/attention_decision_review_2026-11-14/bibtex_verified_validation.json
```

The additional metadata and OpenAlex queries are recorded as complete URLs in their provenance JSON files; these preserve exact parameters for replay. The first helper captures the initial selected records; the enriched metadata combines a second targeted query. `build_evidence.py` requires the saved enriched records and contains the manual scientific extraction, not an automated summarizer. The system Python was used for citation rendering/checking because it already has `requests`; the repo `.venv` does not. No dependency was installed.

Review baseline: git `b63c9d9`; all new files uncommitted. The final audit hashes sources and delivered artifacts. No model fits or new behavioral inferential results were produced for this review.
