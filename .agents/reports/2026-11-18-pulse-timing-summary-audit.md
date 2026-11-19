# Report: Misleading mean of timing-specific midpoints
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Why did the timing plot show nearly equal negative early alpha for left/right pulses?

## Summary
Verified direction coding and genuine observed directional separation. The prior mean-of-individual-parameters plot is a misleading population summary: sparse time-split curves produce weakly identified midpoints, including a−100-bound solution; free asymptotes also make alpha refer to different response probabilities across curves. Arithmetic was correct but the interpretation/display was unsuitable. Withdrew that interpretation and produced data-first curves plus a clearly different shared-asymptote population sensitivity, without excluding mice or forcing signs.

## Findings
- VERIFIED:0 physical-direction mismatches against raw pulse_coherence_pct; left/right pulses are−100/+100%. Source: audit script, manifest and verification.json.
- VERIFIED: early-left individual alpha mean−12.845829, median−0.473554; DBM12 early-left hits−100. Source: original timing/fits.csv and verification.json. This average does not equal a midpoint fitted to the population choice curve.
- VERIFIED: at0% baseline coherence, observed right-minus-left P(right) averages0.132762 (SEM0.063831) early and0.128845 (SEM0.090851) middle across10 mice. Source: zero_coherence_mouse_choices.csv; no new test performed.
- VERIFIED: population free-asymptote early-right alpha+2.491609 despite a negative P=.5 crossing, illustrating midpoint/criterion distinction. Source: independent_population_fits.csv; exact crossing exported.
- VERIFIED: explicitly shared-asymptote sensitivity gives population alpha early left+4.677965/right−10.330814; middle left+5.596517/right−11.547455. Source: shared_parameters.csv. These are parameters of population curves, not corrected individual means.
- VERIFIED: observed means/SEM and joint squared-error objectives independently reproduced.120 whole-mouse resamples per stage,3 curves each=720 coefficient rows; no alpha/beta bound contacts. Source: verification.json, bootstrap_parameters.csv. Bootstrap uncertainty is conditional on shared-asymptote model, not a model-free timing test.

## What didn't work
Averaging unreliable individual coefficients after splitting trials by time produced a plausible-looking but misleading population summary. Marked v2 interpretation withdrawn. Fitting independent population curves alone does not resolve free-midpoint/asymptote ambiguity. Shared asymptotes are an explicit sensitivity assumption, not a discovered truth or evidence from a chosen expected sign. No numerical coefficient bug or trial-coding reversal found.

## How to reproduce
`.venv/bin/python -m scripts.paper.audit_pulse_timing_summary --source dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18 --output <fresh-directory>`
Existing .venv. Actual output: dissemination/paper_accumulation/draft_2026-11-15/pulse_timing_summary_audit_2026-11-18/. Script, input hashes and independent checks exported.

## Caveats
Only10 mice.120 bootstrap draws are exploratory; no formal timing-effect claim. Joint asymptotes may be misspecified, group means can include different mice by coherence, and group-curve estimand differs from mean individual coefficients. Existing Figure4 and pooled paired-fit results unchanged; this audit addresses time-split population summaries.

## Open questions and next steps
- [ ] Author review actual curves and choice of parameter estimand before adopting a timing panel.
- [ ] Retain raw observed curve display and shared-versus-free sensitivity if pursuing group parameters.

## Individual-fit clarification — 18 November 2026
User requests per-mouse evidence. Original timing plot indeed used per-mouse fits then across-mouse mean/SEM; no timing tests were run. Population-curve sensitivity is explicitly a separate estimand, not a replacement for subject-level inference. New pulse_timing_individual_review_2026-11-18/ shows all10 saved early pairs and DBM12 early-left observed data/fitted curve. VERIFIED:105 trials, coherence support−18 to+100, alpha−100 lower bound, lower/upper asymptotes0.4/0.636156. Saved objective reconstructed; no refitting/exclusions. Reproduce with scripts.paper.show_pulse_timing_individual, source/output flags as its README. Next: address per-mouse identification before group testing.

## Exact-reproduction correction — 18 November 2026
See 2026-11-18-pulse-time-exact-reproduction.md. Original notebook joint population model reproduces saved coefficients and screenshot exactly. Earlier individual and alternate population fits changed the specification/aggregation/alpha convention; their behavior does not explain a failure of the original fit. DBM12 boundary remains a separate finding, not an explanation for the reference population plot.
