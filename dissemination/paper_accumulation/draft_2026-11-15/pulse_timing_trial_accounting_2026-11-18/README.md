# Exact trial-selection differences

Both analyses start from the already filtered valid_data.csv (25,508 trials). New post-pulse selection retains21,725;3,783 excluded. Exclusions in reproducible first-failure order:15 absent from model inputs;0 no response;2,264 from cells with only one pulse direction scheduled;792 no-change/null pulse trials;408 responses before actual/virtual pulse end;304 additional responses less than100ms after onset. These counts are mutually exclusive in that order. Independent-rule failure counts overlap; see flow.csv.

No retained trial changes its original versus scheduled pulse label.324 original pulse_type=0 rows were scheduled pulses, but all are excluded by the newer mask (116 at asymmetric-schedule stage,208 before pulse end). Thus the fitted sensitivity differences arise from trial exclusion, not relabeling of retained rows.

Controls are also gated on virtual onset and rig-median virtual duration:200 true controls fail the pulse-end criterion and157 additional controls fail the100ms criterion. No-change/null pulses have pulse coherence equal to baseline±100 and are control-like in the original analysis;793 occur originally, with1 excluded first by input membership and792 by category. One-direction exclusions include897 controls and1,367 positive pulses. Model-input exclusions15 are also absent from current NPZ, so this is not merely stale membership metadata.

Retained original-label counts:11,968 control and9,757 directional pulse trials. Original counts:14,339 control-coded and11,169 pulse-coded. Per-mouse accounting and all trial IDs/reasons are exported. Both original-model datasets retain10 mice; only6 UW mice have late pulses. Current mask was inherited from post-pulse temporal analysis and is not an intrinsic requirement of the joint psychometric equation. No final mask chosen and no fitting performed here.

Reproduce in a fresh directory:
`.venv/bin/python -m scripts.paper.audit_pulse_timing_trials --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --output <new-directory>`

Outputs: flow.csv; trial_accounting.csv; label_crosstab.csv; reason_by_category.csv; mouse_exclusions.csv; model_input_exclusions.csv; manifest.json. Trial-ID set matches saved newer eligibility exactly. Raw files unchanged.
