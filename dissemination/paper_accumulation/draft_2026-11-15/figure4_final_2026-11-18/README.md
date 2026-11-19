# Final Figure 4

Author-approved artwork: exact copy of compact, connected v13.

- [PDF](figure4.pdf), [PNG](figure4.png), [SVG](figure4.svg).
- [Final caption](caption.md), [acceptance](acceptance.json), [verification](verification.json), [provenance](figure_manifest.json).
- Source tables in source_data/; backup and supplementary drafts remain explicitly separate.

A: directional pulse psychometrics. B: paired psychometric parameters. C: pulse-onset-stage influence. D: compensated pulse influence with connected observations and the descriptive exponential.

Reproduce from /src into a fresh folder:

```bash
.venv/bin/python -m scripts.paper.assemble_figure4_timing --previous dissemination/paper_accumulation/draft_2026-11-15/figure4_revision_2026-11-18_v5 --timing dissemination/paper_accumulation/draft_2026-11-15/pulse_time_ordinal_2026-11-18 --interaction dissemination/paper_accumulation/draft_2026-11-15/pulse_time_direction_interaction_2026-11-18 --output <fresh-directory> --persistence-sequence --dilution-only --exponential-overlay dissemination/paper_accumulation/draft_2026-11-15/pulse_exponential_preview_2026-11-18 --compact-connected
```

This finalizes the author-approved figure, not journal submission requirements. Existing statistical limitations remain in the caption.
