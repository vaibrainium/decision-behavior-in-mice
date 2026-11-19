# Report: Standalone pulse exponential preview
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Develop a separate exponential description of PDF page 9 compensated pulse influence. Author clarification identifies the PDF rather than earlier Figure 3; page-9 interpretation communicated.

## Summary
VERIFIED descriptive zero-asymptote exponential fitted to six displayed compensated bins. tau=1.11194 s, saved whole-mouse bootstrap percentile interval 0.45057–3.72549 s. This is a phenomenological approximation, not an intrinsic integration constant. Figure4 unchanged.

## Findings
- VERIFIED saved data aligned to loader-derived mean physical pulse-to-response times; trial counts per bin match. Source: preview observations.csv and scripts/paper/preview_pulse_exponential.py.
- VERIFIED all 600 saved mouse-bootstrap curves fitted; seven reach the slow-decay search boundary. Source: bootstrap_parameters.csv/manifest.json.
- VERIFIED log-grid SSE profile agrees with optimizer minimum; negative late estimate retained. PNG/PDF/SVG inspected. Sources: sse_profile.csv and exponential_preview.*.

## What didn't work
A single exponential does not reproduce an initial plateau followed by a sharper decline; residuals retained. No post hoc bin removal or additional flexible decay model was introduced.

## How to reproduce
`.venv/bin/python -m scripts.paper.preview_pulse_exponential --output <fresh-directory>` from /src. Uses dissemination/pulse_dynamics_2026-11-13/data_{readouts,bootstrap_readouts}.csv and the loader's existing trial table. Code/input hashes in manifest.json. Final SSE diagnostic: /tmp/finish_exponential_preview.py.

## Caveats
Unweighted fit to pooled bin readouts; whole-mouse bootstrap preserves dependence across estimated y values, conditional on observed mean time coordinates. Zero asymptote/amplitude constraints and few bins limit interpretation. No new significance test, decision-model comparison or experiment. PDF's original reference curve is reciprocal dilution, not an exponential.

## Open questions and next steps
- [ ] Author assess the standalone descriptive preview and exact intended PDF display.
