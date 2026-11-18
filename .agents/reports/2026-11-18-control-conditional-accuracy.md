# Report: Control conditional accuracy versus RT
Date: 2026-11-18   Agent: Codex   Commit: eef364b (base; current changes uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Can the notebook accuracy-versus-RT analysis join the control-model figure as evidence consistent with bounded accumulation?

## Summary
Added candidate Figure 3D using the modeled scheduled controls and equal-mouse means/SEM. Audited and corrected response-dependent control selection. Retained a separate fixed-fit C/E/ES comparison: a late plateau is not specific to C. Accepted A–C and Figure 4 are unchanged.

## Findings
- VERIFIED: notebook cells 5/7/10/12 select pulse_type==0, truncate RT milliseconds and pool trials in 400-ms bins. This yields 14,339 nominal controls, including 324 scheduled pulse trials. Scheduled controls in valid_data number 14,015; modeled scheduled controls number 14,014. Source: notebook and script/manifest below. One otherwise valid control has missing pulse timing and is absent from model inputs (PSUIM7_14_1_344).
- VERIFIED: target-side mapping reproduces recorded outcomes exactly; nonzero target side matches coherence sign. Zero-coherence correctness is assigned-target agreement. Source: assertions in script.
- VERIFIED: 10 mice, 613 occupied individual cells and 65 group cells. Group cells contain 5–10 mice; 57 individual cells have one trial. All group means/SEM independently checked against individual-cell export. Sources: data_mouse_accuracy.csv and checks.json in output directory.
- VERIFIED: 30 original fit sources, three models × 10 mice; fixed-parameter simulations use 30 repetitions, seed45678. All model group summaries have the same contributing mouse-cell counts as data. Source: fit_inventory.csv, manifest.json, checks.json.
- INTERPRETATION, visual: accuracy initially rises most clearly at high coherence, then remains broadly level. Both alternative mechanisms can also show broadly flat later accuracy. No formal plateau or comparative CAF score was computed.

## What didn't work
The original pooled response-coded control plot is not suitable unchanged: it includes scheduled pulses and weights mice by trial counts. Preserved its summary for audit, not main artwork. No optimization or significance-seeking exclusions were attempted.

## How to reproduce
Input files: /mnt/data/processed/valid_data.csv and /mnt/data/processed/ddm/ddm_inputs_global.npz; hashes and saved-fit hashes are exported.
Command from /src: `.venv/bin/python -m scripts.paper.control_conditional_accuracy --output dissemination/paper_accumulation/draft_2026-11-15/figure3_conditional_accuracy_2026-11-18` (use a fresh destination on rerun).
Output directory contains caption.md, source tables, manifest.json, checks.json, data panel and model-comparison artwork. Python environment: existing .venv; no installation. Source script: scripts/paper/control_conditional_accuracy.py.

## Caveats
Self-selected RT is not experimentally controlled viewing time. Mouse composition changes across bins; sparse cells and SEM are visible but are not a formal uncertainty model. Fixed-fit predictions are descriptive training-data checks. Conditional accuracy depends on model variability assumptions and is not a unique test for bounds. Primary reference: Modeling Conditional Dependence of Response Accuracy and Response Time with the Diffusion Item Response Theory Model, https://pmc.ncbi.nlm.nih.gov/articles/PMC9677523/ .

## Open questions and next steps
- [ ] Author review candidate D and decide placement with A–C.
- [ ] Assemble Figure 3 after final A alternative is selected; keep original cohort recovery text-only.
