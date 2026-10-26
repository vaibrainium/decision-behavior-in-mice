# Report: neuropaper S5 assembly and Supplementary Figure S6
Date: 2026-10-26   Agent: Codex   Commit: be74283 (production); d1e5f29 (G4 approval)
Plan: plans/2026-10-20-paper-writeup.md

## Question
Could the G4-approved manuscript be assembled coherently and could the required gate/sensitivity record be converted
from a text-only placeholder into auditable Supplementary Figure S6 before panel review?

## Summary
VERIFIED: G4 was approved with the bounded N105–N107 Methods patch. The S5 manuscript was assembled with a
repository-local, marker-aware renderer because the pinned neuropaper renderer duplicated units for compound ledger
records. Independent coherence review found no scientific drift and specified eight bounded editorial repairs; those
repairs are applied and all contract checks pass. Supplementary Figure S6 v2 is selected, visually inspected and backed
by one adjacent source CSV per panel. It reports failed original and gain-revised gates, low frozen-strategy sensitivity,
low timing-test sensitivity and the resulting stopping sequence; it is not a null result for temporal weighting.

## Findings
- VERIFIED: original predictive coverage was accumulator RT 34/50 cells and no-response 9/10 mice; leak-plus-urgency
  RT 34/50 and no-response 5/10. Source: `figS6_gates_sensitivity_2026-10-26_v2_source_B_coverage.csv`, generated
  directly from `/mnt/data/processed/ddm/primacy/results_{primary,secondary}_gate.pkl`.
- VERIFIED: gain-revised coverage was accumulator RT 31/50 and no-response 9/10; leak-plus-urgency RT 35/50 and
  no-response 6/10. Source: `figS6_gates_sensitivity_2026-10-26_v2_source_C_revised_gate.csv`, generated from the
  corresponding `primacy_revised` gate pickles. Registered as N108.
- VERIFIED: the frozen pulse-specific strategy rule correctly distinguished 1/20 rapid-forgetting and 0/20
  accumulator full-cohort datasets. Source: `figS6_gates_sensitivity_2026-10-26_v2_source_D_strategy.csv` and
  `/mnt/data/processed/ddm/primacy/strategy_power.csv`.
- VERIFIED: gate passes at 0%, 10%, 20% and 40% decline were 19/20, 14/20, 7/20 and 1/20; primary primacy detections
  were 0/20, 0/20, 1/20 and 0/20. Source: `figS6_gates_sensitivity_2026-10-26_v2_source_E_calibration.csv` and the
  four `primacy_calibration/calibration_summary_levels*.csv` files.
- VERIFIED: the selected PNG is 2125 x 1948 pixels at 300 dpi; the same basename has editable PDF and SVG exports.
  Source: Pillow metadata check and visual inspection of `figS6_gates_sensitivity_2026-10-26_v2.png`.
- VERIFIED: the final and marker-preserving manuscripts rebuild deterministically with the local assembler. The final
  manuscript contains no contracts, writer notes, claim markers or unresolved number tokens. The pinned neuropaper
  `check-all` reports zero errors; remaining warnings are declared placeholders, word-budget/lint advisories and two
  false-positive `±1` matches inside `±100%`.

## What didn't work
- The first S6 layout crowded revised coverage and compressed the six-step flow. It is retained as v1 under the
  no-overwrite rule. V2 replaces revised coverage bars with a compact dot display and uses a two-column flow.
- The pinned neuropaper assembler concatenates ledger `value` and `unit`, producing phrases such as duplicated mice or
  units for compound records. The plugin was not edited. `scripts/paper/assemble_neuropaper.py` renders compound
  N067–N108 records as their complete value fields and fails on known duplicate patterns.

## How to reproduce
From `/src` in the project environment:

```bash
.venv/bin/python -m scripts.paper.figS6_gates_sensitivity
.venv/bin/python scripts/paper/assemble_neuropaper.py --project-root /src/dissemination/paper --output /src/dissemination/paper/manuscript.md
.venv/bin/python scripts/paper/assemble_neuropaper.py --project-root /src/dissemination/paper --output /src/dissemination/paper/np/integrity/manuscript_marked_s5.md --keep-markers
cd dissemination/paper
../../.venv/bin/python /root/.claude/plugins/marketplaces/neuropaper/skills/neuropaper/scripts/np.py --root . check-all
```

The figure script asserts every plotted count before export and refuses to overwrite an existing same-day basename by
creating a new version.

## Caveats
The original choice-gate fits each contain one sampler divergence. Calibration conditions on fitted control parameters
and uses 20 datasets per condition, giving 1/20 empirical resolution. Strategy and timing calibration answer different
questions and are not pooled. The tests' low sensitivity does not support absence of primacy, recency or flat weighting.

## Open questions and next steps
- [ ] Run independent integrity audit 1 against the assembled manuscript, marked copy, ledgers and selected artwork.
- [ ] Resolve any audit findings, then advance S5 to S6 and run the parallel panel review.
- [ ] Stop at G5 for explicit author disposition; do not silently cross the human gate.
