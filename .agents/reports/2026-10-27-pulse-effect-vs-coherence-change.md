# Report: does the behavioural pulse effect scale with the coherence change?
Date: 2026-10-27   Agent: Claude Opus 5.5   Commit: 85d4f8d (+ uncommitted scripts/pulse_followup/effect_vs_delta.py)
Plan: plans/2026-10-27-pulse-effect-vs-coherence-change.md

## Question
Evidence-like pulse (effect proportional to the coherence change |D| = 100 - s*c) or event-like (constant)? Bears on why
all DDM variants underpredict the pulse effect (~8x).

## Summary
Inconclusive, and this design cannot settle it. Pulses always go to +-100%, so within |c| <= 36 |D| only spans 64-136%.
The two hypotheses then predict effects that differ by ~0.12 logit across the range, below the per-arm uncertainty. The
overall pulse effect is clear (0.17 logit, p 0.009); its dependence on |D| is not resolved either way.

## Findings (responders only; mouse is the unit, n = 10, df 9; source <run>/behaviour_delta/, run = /mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b)
- VERIFIED: check reproduces package C responder positive-vs-control effect: 6.08 pp.
- VERIFIED: mean pulse effect 0.169 logit [0.053, 0.286], t 3.29, p 0.0094 (group.json).
- VERIFIED: slope 0.265 logit per 100% |D| [-0.164, 0.695], p 0.20 vs 0; 6/10 mice positive. Proportional prediction is
  ~0.17 (mean effect / mean |D|); slope minus each mouse's proportional slope 0.098 [-0.310, 0.506], p 0.60 (post hoc test).
  Neither constant nor proportional is rejected.
- VERIFIED: pre-declared proportionality index unusable (median 0.50; mean 3.1 [-5.5, 11.8]; DBM14 35, DBM12 -10).
- Arm means over mice (logit): |D| 64: 0.04, 82: 0.07, 91: 0.27, 100: 0.28, 109: -0.04, 118: 0.53, 136: 0.21 (SEM 0.08-0.23).
- SUSPECTED (rough): with slope SE ~0.19 across mice, power to detect the proportional slope (0.17) is ~15%.

## What didn't work
- The proportionality index as the primary statistic (ratio with a near-zero denominator).

## How to reproduce
`.venv/bin/python -m scripts.pulse_followup.effect_vs_delta` (reads <run>/behaviour/cells.csv; writes arms.csv, per_mouse.csv, group.json, effect_vs_delta.png).

## Caveats
- |D| is confounded with baseline coherence and with/against-coherence direction (|D| > 100 = pulse against the baseline).
- Logistic approximation to a bounded DDM; uncorrected single exploratory test, outside the closed primacy protocol.
- ±100% baselines (|D| 200) are not in the pulse-vs-control cells and were not used.

## Open questions and next steps
- [ ] A more powerful version within existing data would use the trial-level choice model (pulse x |D| term with mouse
      random effects) and could add +-100% baselines; still limited by the narrow |D| range. Author decision.
- [ ] Alternative route to evidence vs event: compare against the DDM's own predicted |D| dependence (it is evidence-like by construction).
