# Plan: does the behavioural pulse effect scale with the coherence change?
Status: done (report: reports/2026-10-27-pulse-effect-vs-coherence-change.md)
Created: 2026-10-27 by Claude Opus 5.5
Related reports: reports/2026-10-27-pulse-me-old-vs-new-filter.md, reports/2026-10-27-pulse-contrast-responders-only.md,
reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md

## Goal
A model-free answer to whether the pulse acts like evidence (effect proportional to the coherence change it adds) or like
a discrete event (effect independent of it). Exploratory, author-approved 2026-10-27 ("yes"); not part of the closed primacy protocol.

## Context
All DDM variants underpredict the pulse effect ~8x (refit plan log). The pulse sets coherence to +-100% for 3-4 frames,
so the change |D| = 100 - s*c (s = pulse sign, c = baseline signed coherence) runs 64-136% within |c| <= 36.

## Design (fixed before computing)
- Input: package C cells.csv, analysis_set primary_coherence, contrasts positive_vs_control (s=+1) and control_vs_negative
  (s=-1); responders only (R/L counts; no-response trials dropped, per author rule).
- Per mouse x arm (c, s): pool supported cells; effect = s * [logit P(R | pulse) - logit P(R | control)], Haldane +0.5.
  Logit, so the ceiling at high with-coherence baseline does not by itself shrink the effect.
- Per mouse: inverse-variance weighted regression of effect on |D|. Proportionality index
  PI = slope * mean|D| / mean effect (1 = evidence-like proportional scaling, 0 = event-like constant).
- Group: mean PI and slope across 10 mice, one-sample t (df 9) for slope = 0 and PI = 1; report both; mouse is the unit.
- Secondary: pooled arm means by |D| (plot); pulse-vs-negative at +-100% baseline (|D| = 200) descriptive only.

## Assumptions
- Logistic approximation: added evidence shifts choice logit by a constant times |D|, regardless of baseline. A bounded
  DDM with RT is not exactly logistic; check the sign of this bias against model predictions if results are borderline.
- |D| is confounded with baseline coherence and with/against-coherence direction (amendment 6 asymmetry matched the
  control fit's slope error). Cannot be removed with this design; stated as a caveat.

## Steps
- [x] 1. Script scripts/pulse_followup/effect_vs_delta.py (reads cells.csv, writes to <run>/behaviour_delta/).
- [x] 2. Run; per-mouse table, group stats, figure.
- [x] 3. Verify: pooled positive-vs-control effect in pp reproduces the package value (6.08 pp responders).
- [x] 4. Report + STATUS.

## Out of scope
Model fitting, front-end changes, new trial selection.

## Log
- 2026-10-27: PI (pre-declared) is ill-conditioned (divides by mean effects near 0; DBM14 PI 35, DBM12 -10). Added a
  direct test, per-mouse slope minus own proportional slope, after seeing the first run; labelled as post hoc in the script.
- 2026-10-27: done. Inconclusive: slope 0.27 [-0.16, 0.69] per 100%, proportional prediction 0.17; the |D| range (64-136%)
  is too narrow for this design to separate the hypotheses.
