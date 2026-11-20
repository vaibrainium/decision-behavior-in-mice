# Report: Pulse-only held-out bits per trial
Date: 2026-11-18   Agent: Codex   Commit: 3b55eca (uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Calculate Figure3-style bits for pulse-only models.

## Summary
VERIFIED all22 candidates/10 mice scored using within-mouse -NLL/(n_test ln2), then equal-mouse mean. Winner remains pulse_norm_ugm_no_sv, -1.540348251 bits/trial. No new fits or significance tests.

## Findings
- VERIFIED matched per-mouse trial denominators for every candidate; formula inversion checked. Source: pulse_only_bits_2026-11-18/manifest.json and bits_per_mouse.csv.
- VERIFIED mean ranking changes below winner relative to summed NLL because per-trial mouse normalization changes weighting. All22 mean/pooled values and ranks in bits_summary.csv. Pooled trial-weighted winner agrees.

## What didn't work
Previous answer supplied control-model values; these pulse-only values supersede that scope for the user's question.

## How to reproduce
`.venv/bin/python -m scripts.paper.pulse_only_bits --output <fresh-directory>`. Source dissemination/figures/qc/model_ic_per_mouse_2026-11-12_rescored.csv; hashes in manifest.json.

## Caveats
Rounded saved scores; descriptive ranking, not inferred model superiority. Joint choice/RT score, not choice-only gain over a null.

## Open questions and next steps
- [ ] Decide whether pulse-only bits replace raw NLL in Figure5.
