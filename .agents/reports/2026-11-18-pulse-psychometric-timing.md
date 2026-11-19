# Report: Pulse-time α/β plots
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Can direction-specific α/β plots versus early/middle/late pulse time strengthen Figure4?

## Summary
Generated independent time-specific fits and mouse-level summaries. Current v2 honors author clarification: absolute midpoint α, β remains a control-relative change. Three-time comparison uses identical6 UW mice, companion earlier-times uses10. Identification and sensitivity problems prevent a clean timing claim. Figure4 unchanged.

## Findings
- VERIFIED notebook audit: notebooks/1.0-psychometric-analysis.ipynb cell5 uses coh+alpha, opposite current midpoint sign; get_param_and_se returns differences by omitting baseline. Cells15–17 add SE2+time*SE4, omitting shared-time/covariance terms. Model imposes linear stage dependence. These are not independent evidence for a linear trend or valid contrast error bars.
- VERIFIED:21,725 eligible responses, including19,313 early/middle and2,412 late;8,529 early/middle pulses exactly match Figure4.595 occupied subject/coherence cells,78 free4 fits and78 sensitivity rows (including duplicated controls). Eight free4 covariance condition numbers nonfinite. Sources: base-output eligible_trials.csv, fits.csv, verification.json.
- VERIFIED: late only6 UW mice, onsets50.010/233.380/416.750ms. UCLA earlier schedules differ. Three-time view retains identical6 mice, earlier-time companion identical10. Sources: timing.csv and manifest.json.
- VERIFIED: paired subtractions, subject means/SEM and eligibility independently checked. v2 absolute α matches fitted midpoints, β means/SEM unchanged; no refits. Sources: group_parameters.csv, verification.json.
- INTERPRETATION: splitting sparse curves by time worsens identification; shared-control-asymptote sensitivity changes some trends. No formal timing test, and no inference of no timing effect.

## What didn't work
Free4 individual timing fits are unstable despite multistart optimization; fixing pulse asymptotes does not yield a consistently robust story. Initial control-subtracted α superseded by user-requested absolute α. Original outputs preserved. One documentation command used system Python with incompatible pandas; reran with existing .venv, without installing packages.

## How to reproduce
From /src, existing .venv:
`.venv/bin/python -m scripts.paper.pulse_psychometric_timing --output <fresh-directory>`
Then `.venv/bin/python -m scripts.paper.pulse_psychometric_timing --from-results <first-directory> --output <fresh-v2-directory>`.
Actual outputs: dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/ and matching_v2/. Source/helper/notebook hashes in manifests. Caption/current definitions in v2/caption.md. Script: scripts/paper/pulse_psychometric_timing.py.

## Caveats
SEM conditions on fitted coefficients; curve-estimation uncertainty is not propagated. Late support is restricted to one site/cohort. No old exclusion was silently changed in Figure4: restoring late trials occurs only in this separate exploratory analysis. No significance tests or adopted figure change.

## Open questions and next steps
- [ ] Author assess absolute-alpha preview; resolve identification before paper timing claims.

## Primary-display decision — 18 November 2026
Author selects early/middle with all10 mice as primary; same6-mouse three-time view retained separately. VERIFIED: each direction/time has exactly the10 listed subjects, with means/SEM reproduced from fits.csv and paired_control_differences.csv. Current selection.json and primary_caption.md in v2 identify the primary artwork. No fitting, exclusion, definitions or inference changed; no full Figure4 integration yet.

## Exact-reproduction correction — 18 November 2026
See 2026-11-18-pulse-time-exact-reproduction.md. Original notebook joint population model reproduces saved coefficients and screenshot exactly. Earlier individual and alternate population fits changed the specification/aggregation/alpha convention; their behavior does not explain a failure of the original fit. DBM12 boundary remains a separate finding, not an explanation for the reference population plot.
