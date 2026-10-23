# Report: first prose draft of the evidence integration paper
Date: 2026-10-22   Agent: Codex   Commit: a39ea6b (source snapshot; drafting changes uncommitted)
Plan: plans/2026-10-20-paper-writeup.md

## Question
Begin the paper while final Hyak fits are queued, using integration versus the extrema approximation as the primary
paper question and temporal weighting as secondary. The user explicitly approved this framing and manuscript work.

## Summary
Created `dissemination/paper/manuscript_2026-10-22.md`: Introduction, established Results, Methods and bounded
Discussion prose, with pending strategy/timing sections and an incomplete abstract. Added source, paragraph-claim
and numeric-consistency records. Corrected censoring language in the existing captions and qualified the outline.
The parent paper plan remains active: scientific results, author facts, figures and final verification remain unfinished.

## Findings
- VERIFIED (saved output, not reanalysis): notebook `notebooks/2.14-psychophysical-kernel-analysis.ipynb`, zero-based
  cell 25, reports shared k = 0.50, profile interval 0.15–0.90, positive hidden-weight p = 0.0186 and paired
  hidden-versus-nominal coefficient p = 0.492. The latter does not support a consistent population discount. Draft
  distinguishes the common-ratio likelihood estimate from across-mouse inference. Snapshot a39ea6b.
- VERIFIED (code inspection): the notebook's cells 7 and 18 define controls using the RT-dependent `pulse_type`;
  `scripts/ddm/build_ddm_inputs.py::scheduled_pulse` uses scheduled coherence changes. Draft labels these as distinct
  analysis sets. SUSPECTED: partial pulse exposure/selection may affect the notebook estimates; no effect size was
  computed. A scheduled-control sensitivity check is explicitly pending.
- VERIFIED (documentation inspection): descriptive and DDM response counts differ because invalid pulse durations
  are excluded only from the latter. Sources: `figure_captions.md` Fig. 1 author notes; analysis log section 4.1;
  `build_ddm_inputs.py::main`. Preserved both analysis sets rather than silently equating counts.
- VERIFIED (local checks): source-schema, numeric-consistency and reference-syntax checks pass. Claim audit has
  only expected unverified-human-evidence errors; no missing evidence IDs or paragraph hash mismatches were reported.
  Lint identifies unfinished TODOs and absent confidentiality-manifest verification. This is an incomplete internal
  draft, not a submission-ready manuscript. These are document checks, not scientific-result validation.

## What didn't work
- Default shell sandbox cannot start (bwrap namespace permission error); approved escalated shell calls used.
- `python` is unavailable in the shell; dependency-free checks use `python3 -B`.
- Direct publisher retrieval for the motion-energy paper failed; publisher search returned its abstract and metadata.
  Its source record explicitly retains that limitation. Stine's full article opened through PMC; Okazawa's full
  article opened through the authors' NYU PDF. No unpublished text was sent to literature search services.
- Human-verification gates intentionally remain unverified; the drafting agent did not impersonate an author.

## How to reproduce
From `/src`, with the current draft and Python 3 standard library (no package installation):

```bash
python3 -B .claude/skills/scientific-writing/scripts/validate_manifest.py dissemination/paper/sources_2026-10-22.json --kind source
python3 -B .claude/skills/scientific-writing/scripts/check_consistency.py dissemination/paper/consistency_2026-10-22.json
python3 -B .claude/skills/scientific-writing/scripts/check_references.py dissemination/paper/sources_2026-10-22.json
python3 -B .claude/skills/scientific-writing/scripts/audit_claims.py dissemination/paper/manuscript_2026-10-22.md dissemination/paper/claims_2026-10-22.csv dissemination/paper/sources_2026-10-22.json
python3 -B .claude/skills/scientific-writing/scripts/lint_manuscript.py dissemination/paper/manuscript_2026-10-22.md
git diff --check
```

The final two manuscript checks intentionally return nonzero for unfinished content and unverified sources. Registry
records identify original analysis commands or locators; no fits, notebook analyses or pulse comparisons were run.

## Caveats
Source-schema and reference-syntax passes do not verify numerical results or bibliography content. Numeric consistency
checks compare the supplied registry, not an independent re-extraction of every manuscript number. All sources and
claims remain awaiting accountable human verification. New prose is linked to existing reports and code at a39ea6b;
the completed scientific runs must supply exact execution commits and environments later. Dates use client date;
pre-existing records dated 2026-10-23 are retained unchanged.

## Open questions and next steps
- [ ] Inspect arriving Hyak fits, settle guess bias, assess predictive fit and recovery.
- [ ] Complete extrema bounds/refit checks, strategy sensitivity and frozen predictions before pulse comparison.
- [ ] Keep the original analysis order and thresholds; new paper emphasis is not an analysis-plan amendment.
- [ ] Check hidden-coherence robustness on scheduled controls, and agree how to handle exploratory multiplicity.
- [ ] Supply animals/ethics/training/exclusions, authorship, journal and availability details.
- [ ] Complete Fig. 3 and pending panels; Fig. 1F image/script still need censoring-label correction. No images regenerated.
- [ ] Fill pending Results, then finalize abstract, opening Discussion, title and author-verified source records.

## Drafting tools
Used the local scientific-writing skill and the Pages write-page skill's repository-format guidance; saved only to
the established local paper directory. The draft includes the skill-library reference and a provisional drafting
assistance note; final disclosure wording awaits author and journal decisions.
