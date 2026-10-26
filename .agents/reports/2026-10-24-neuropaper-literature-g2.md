# Report: neuropaper verified literature stage at G2
Date: 2026-10-24   Agent: Codex + neuropaper agents   Commit: 0d5c2e0 (starting snapshot; current changes uncommitted)
Plan: [paper write-up](../plans/2026-10-20-paper-writeup.md) (steps AA / neuropaper S2)

## Question
Does the literature support the locked paper spine, and has prior work already tested the same control-fit to strong-pulse predictive transfer?

## Summary
VERIFIED: a four-shard public-source search, independent metadata audit, synthesis and adversarial scoop check produced 35 verified sources. An author-requested mouse-specific fact-check then added nine unique verified precedents, producing a 44-source ledger. Broad mouse novelty is false: continuous RDK, dynamic visual evidence accumulation and visual DDM/RT modelling were already established separately. No retained source performed the exact control-fit to randomized signed-motion-pulse transfer test across choice, response probability and response-time distributions.

## Findings

- VERIFIED: 56 retained shard rows de-duplicated to 33 initial sources; the challenge correction added Stine 2023 and Steinemann 2024 and replaced an obsolete Parés-Pujolràs preprint, yielding 35 current sources. Source: `dissemination/paper/np/lit/shard_*.csv`, `shard_gap_addendum.csv`, `ledger/sources.csv`.
- VERIFIED: the final audit matched all 44 DOI records in Crossref and all 41 PMID-linked records in PubMed; 0 failed, 0 retracted/withdrawn and 0 were deleted. Source: `dissemination/paper/np/integrity/lit_audit.md` v3.
- VERIFIED: Stine et al. 2023 and Steinemann et al. 2024 used weak randomized 100-ms macaque pulses with choice/RT and neural analyses, but did not report no-pulse-only fitting followed by frozen held-out pulse prediction. Parés-Pujolràs et al. 2026 v3 fit across pulse-task conditions. Source: `dissemination/paper/np/lit/shard_gap_addendum.md` and the three linked source notes.
- VERIFIED WITH SEARCH-SCOPE LIMIT: the corrected 35-source ledger contains no study closing the narrow question of quantitative transfer from ordinary evidence to separately randomized strong transient evidence in the specified pipeline. Source: `dissemination/paper/np/lit/gaps.md`, fit-versus-perturbation table and scoop check.
- VERIFIED: the broad claim that dynamic visual decision-making or visual evidence accumulation had not been shown in mice is contradicted. Nine unique mouse precedents were added after two independent bounded searches and source audit. Source: `dissemination/paper/np/lit/mouse_dynamic_visual_factcheck.md`, `np/reviews/mouse_dynamic_visual_novelty_challenge.md`, `np/integrity/mouse_dynamic_visual_audit.md`.
- DRAFTED: 12 source-bound background claims C010–C021 remain proposed pending author approval. C019–C021 state the established mouse RDK, discrete visual accumulation and visual DDM/RT precedents positively; no universal absence or “first” claim was created. Source: `dissemination/paper/np/ledger/claims.csv`.

## What didn't work

- The installed PubMed helper lacked `requests`; no package was installed. Librarians used documented public NCBI E-utilities directly and logged the queries.
- The first synthesis omitted two close macaque pulse studies and used an obsolete preprint version. The independent literature challenge caught these issues; the corrected ledger and synthesis were fully re-audited.
- The user's proposed broad mouse novelty statement did not survive fact-checking. The synthesis was corrected to distinguish established components from the exact conjunction not found in the bounded search.
- Four shards could not start simultaneously because only three worker slots were available beside the orchestrator. Three ran first and the counter shard started immediately when a slot freed; outputs and verification remained independent.

## How to reproduce

Search strings, databases, filters, dates, hits, screened and kept counts are in `dissemination/paper/np/lit/search_log.md` and the four shard Markdown files. Candidate metadata and notes are in the adjacent shard CSVs and `np/lit/notes/`.

From `/src/dissemination/paper`:

```bash
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py check-all
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py check-spine
/src/.venv/bin/python -c "import csv; r=list(csv.DictReader(open('np/ledger/sources.csv'))); assert len(r)==44 and all(x['verified']=='yes' for x in r); print(len(r))"
```

The API endpoint patterns and access date are recorded in `np/integrity/lit_audit.md`. The merge identity order was DOI, then PMID, then normalized title; the final ledger is independently auditable from the shard CSVs.

## Caveats

This is a reproducible narrative review, not a systematic review. Some notes are abstract-only and therefore support only narrowly recorded claims. Metadata verification does not replace later sentence-level citation fidelity checks. Public index coverage cannot prove that no relevant paper exists; the adversarial search makes the scoop conclusion bounded rather than absolute.

## Open questions and next steps

- [ ] Author approves or edits the corrected mouse-specific gap, names missing key papers, and approves C010–C021 at G2.
- [ ] After G2, lock the approved background claims and advance to S3 outline/briefs.
- [ ] Ensure Stine 2023, Steinemann 2024 and Parés-Pujolràs 2026 are prominent Discussion comparators.
