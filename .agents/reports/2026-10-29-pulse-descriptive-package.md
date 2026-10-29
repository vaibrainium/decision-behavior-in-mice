# Report: pulse descriptive package on all 10 mice (S1, S2, S3)
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: 363aa3d (working tree; files below not yet committed)
Plan: plans/2026-10-29-pulse-descriptive-package.md

## Question
Route step 1 of reports/2026-10-29-pulse-leak-vs-urgency.md: model-free pulse signatures on all mice, with the same
selection and effect measure as the simulation script, so that models can be judged against them.

## Summary
The pulse effect lives in responses made 0.3 to 1.2 s after the pulse: 5.5 pp [0.8, 10.2] over 10 mice (t p 0.027,
Holm 0.08 over 3; logit 0.24 [0.01, 0.47], Holm 0.12). After 1.2 s the effect is 1.2 pp [-2.8, 5.2], so there is
no group-level reversal, but the interval admits a small one. The effect is carried by 5 mice (PSUIM5/6/7, DBM5, DBM6);
the 5 sparsest mice are near zero. The "no reversal" pattern is clear only in PSUIM6/7; DBM6 does reverse (late window
-3.4 to -7.2 pp in each stage, SE about 6 to 9 pp per bin). Toward-pulse choices are faster mainly in the slow tail, and
their RT SD shrinks after middle pulses. No coherence dependence of the onset effect is detectable. Moderate confidence
in S1 window results; S2 and the late-stage parts of S3 are underpowered.

## Findings (VERIFIED; scripts/ddm/pulse_descriptive_package.py; outputs
dissemination/figures/qc/pulse_descriptive_package_2026-10-29{.png,.pdf,_counts,_s1_profile,_s1_group,_s1_windows,
_s1_tests,_s2,_s2_group,_s2_tests,_s3,_s3_group}.csv)
Effect = pulse-count-weighted P(choice = pulse sign | pulse) - P(same | control), coherence-matched, pp. Mouse = unit.

S1 windows, stages pooled per mouse (s1_tests.csv; Holm over the 3 tests within each scale):
| Test | Mean | 95% CI | dz | p (t) | Holm | Wilcoxon p | Mice > 0 |
|---|---|---|---|---|---|---|---|
| pp, 0.3-1.2 s | 5.48 | [0.79, 10.17] | 0.84 | 0.027 | 0.081 | 0.027 | 8/10 |
| pp, 1.2-5 s | 1.22 | [-2.76, 5.20] | 0.22 | 0.51 | 0.51 | 0.43 | 7/10 |
| pp, difference | 4.26 | [-2.31, 10.82] | 0.46 | 0.18 | 0.35 | 0.19 | 7/10 |
| logit, 0.3-1.2 s | 0.24 | [0.01, 0.47] | 0.76 | 0.039 | 0.12 | 0.11 | 7/10 |
| logit, 1.2-5 s | 0.04 | [-0.13, 0.22] | 0.18 | 0.58 | 0.58 | 0.56 | 6/10 |
| logit, difference | 0.20 | [-0.11, 0.51] | 0.46 | 0.18 | 0.36 | 0.16 | 7/10 |

Per mouse, 0.3-1.2 s / 1.2-5 s (pp): PSUIM6 15.5 / 1.6; PSUIM7 13.5 / -1.0; PSUIM5 10.4 / 2.2; DBM6 10.2 / -4.8;
DBM5 3.9 / 1.2; DBM15 4.3 / 3.2; DBM13 1.1 / 4.5; PSUIM10 0.7 / 12.9; DBM12 -0.5 / -7.9; DBM14 -4.2 / 0.3.
DBM6 per stage, late window: -7.2, -3.7, -3.4 pp (s1_windows.csv).

S2 (s2_group.csv, s2_tests.csv): early-pulse effect 6.8, 3.6, 4.7, 4.0 pp at |coh| 0, 9, 18, 36 (CIs all span 0 or
nearly). Slope of (early - middle) per 100 % |coh|: -5.4 pp [-42.5, 31.6], p 0.75 (logit -0.15 [-1.64, 1.34]).
Uninformative at this sample size; not evidence of absence.

S3 (s3_group.csv; ms, pulse - control):
- Toward-pulse choices, 90th percentile: early -311 [-537, -85] (2/10 mice > 0), middle -401 [-569, -234] (1/10),
  late -133 [-351, 85] (6 mice). Medians: -77, -98, +69, all CIs span 0.
- Toward-pulse RT SD: middle -115 [-169, -60] (0/10 mice > 0); early -28 [-108, 52]; late -4 [-30, 22].
- Against-pulse choices: no CI excludes 0 (median +107, +181, +124).

Counts (counts.csv): S1 drops responses earlier than 0.3 s after onset: 1-8 % of early-pulse trials, 3-27 % of
middle and 12-43 % of late. Bins hold 29 to 336 pulse trials per mouse.

Check: the per-bin effects for PSUIM6/7 and DBM6 match the illustration's data profiles (49 cells, max difference
0.0005 pp); bootstrap SEs differ by up to 1.1 pp (different random stream).

## What didn't work
Nothing failed. Per-mouse slopes in S2 rest on 2 to 4 coherence levels (DBM12-14 lack 18 or 36 %).

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_descriptive_package` from /src (a few minutes; seed 0; 300 bootstrap resamples).

## Caveats
- Ten mice, five with few pulse trials; group means are diluted by mice with no measurable effect.
- The late stage selects slower trials (12-43 % excluded as too early), so S1/S3 late results are not comparable
  one-to-one with early and middle.
- S1 tests are pre-specified in the plan; S3 and S2 summaries are descriptive (no multiplicity correction applied).

## What this changes for the leak-vs-urgency route
- "No late reversal" holds in the two densest mice and at group level, but DBM6 reverses. The model mismatch in the
  earlier report is therefore mouse-specific, and step 3 (explain the missing reversal) should be judged per mouse.
- Re-running the leak/urgency illustration on all ten mice would not add discrimination: outside PSUIM5/6/7 the per-bin
  SEs are about 6 to 15 pp, larger than the differences between variants.

## Open questions and next steps
- [ ] Step 2 of the route: per-mouse non-decision-time interval from the ±100 % trials (local).
- [ ] Step 3: choose the first candidate for the missing reversal (author decision); judge on PSUIM5/6/7 and DBM6.
