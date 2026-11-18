# Candidate Figure 3D: conditional accuracy

New candidate D alongside the accepted Figure 3A–C; combined assembly awaits panel review. This does not restore the previous cohort-recovery D, which remains in Results text.

- `figure3D_conditional_accuracy.pdf/png/svg`: mouse-balanced data with SEM.
- `model_comparison.pdf/png/svg`: identical data points and fixed original full-control C/E/ES predictions; no refits, no held-out validation. Thirty simulations per input, seed 45678. Model summaries use the same occupied mouse cells as the data; coverage verified identical.
- `caption.md`, `manifest.json`, `checks.json`: definitions, provenance and independent checks.
- CSVs retain all individual counts, group summaries, fit hashes and the original notebook-style pooled calculation.

The notebook's response-coded control selection included 324 scheduled pulse trials. Main artwork instead uses the same 14,014 scheduled controls as Figure 3B. All three candidate prediction plots can exhibit a broadly flat later-RT profile; this is a descriptive consistency check, not unique evidence for C. Fifty-seven individual mouse/coherence/time cells contain only one trial. Composition varies across time bins (5–10 contributing mice), and the SEM does not account for model-parameter uncertainty.

Reproduce in a fresh output directory:
`.venv/bin/python -m scripts.paper.control_conditional_accuracy --output <new-directory>`
