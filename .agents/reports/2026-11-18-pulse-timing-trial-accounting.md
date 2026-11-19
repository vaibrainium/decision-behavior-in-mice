# Report: Trial differences in pulse-time fits
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Which trials differ between original notebook and newer eligibility used in per-mouse sensitivity?

## Summary
The25,508 original filtered trials become21,725 by excluding3,783. Crucially, no retained trial changes label. Earlier wording overemphasized relabeling; sensitivity bundles additional restrictions inherited from the post-pulse time-course workflow. No fit or final scientific mask selected here.

## Findings
- VERIFIED first-failure exclusions:15 not in model input;2,264 asymmetric-sign schedule;792 no-change pulse category;408 response before actual/virtual pulse end;304 additional response<100ms after onset. Sum3,783; exact eligible IDs reconstructed. Source: output flow.csv and manifest.json.
- VERIFIED:324 original control-coded rows have scheduled directional pulse labels, but all324 are excluded (116 asymmetric cells,208 before pulse end). Retained label differences0. Source: trial_accounting.csv and label_crosstab.csv.
- VERIFIED: no-change pulses are baseline±100 with equal pulse coherence.793 original rows,1 already removed by input membership,792 removed by category. Source: reason_by_category.csv and audited table fields.
- VERIFIED: asymmetric exclusions include897 true controls and1,367 positive pulses. Timing exclusions include200 controls before virtual pulse end, plus157 additional controls before100ms after virtual onset. Source: reason_by_category.csv.
- VERIFIED: retained11,968 controls and9,757 pulse-coded trials versus original14,339 and11,169. All15 model-input exclusions absent from current NPZ. Per-mouse counts exported. Source: trial_accounting.csv/model_input_exclusions.csv.

## What didn't work
An initial diagnostic mixed indexed boolean masks and printed overlapping712 as a sequential final-rule removal count. Recomputed with positional masks:712 fail the100ms rule before the pulse-end removal;304 are additional after that removal. Persisted script/counts are correct and exact trial-ID equality asserted.

## How to reproduce
`.venv/bin/python -m scripts.paper.audit_pulse_timing_trials --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --output <fresh-directory>`
Output: dissemination/paper_accumulation/draft_2026-11-15/pulse_timing_trial_accounting_2026-11-18/. Source/input hashes in manifest.json, full ID-level accounting and per-mouse summaries alongside. Existing .venv; no data edits or fits.

## Caveats
Sequential categories depend on declared order; independent exclusions overlap. Mask compares a post-pulse-timecourse population against the original psychometric population, not a pure label correction. Control virtual timing gates and null-pulse exclusions require question-specific justification.

## Open questions and next steps
- [ ] If assessing robustness, vary each rule separately under the same model; do not attribute all changes to pulse labeling.
