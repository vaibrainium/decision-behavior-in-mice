# Report: independent review of the proposed pulse-filter pilot
Date: 2026-10-23   Agent: Codex   Commit: 475934ed5dc7d67d5aa072df79f89a47a1e25a79 (follow-up code/results untracked)
Plan: [pulse follow-up](../plans/2026-10-23-pulse-followup-parallel.md), review of E and proposed F1

## Question
Should the next step be a corrected input and reduced pulse-filter pilot, a full grid, or stopping? Which claims and implementation details need qualification first?

## Summary
Recommend a versioned input correction and the reduced exploratory pilot, with the safeguards below; this recommendation is not authorization to execute it. The behavioural result already supports a substantive thesis contribution. A temporal-filter pilot tests a specific predictive repair, not a neural mechanism. Several claims in E overstate what the stimulus audit and null behavioural contrasts establish.

## Findings

### Verified from existing files
- The primary tradeoff is reproduced in the saved `diagnostics/e3_optima.csv`: PSUIM6 in-sample joint/choice gains 2.446784/7, choice improvement 9.310756 NLL, RT cost 97.572555; PSUIM7 gains 1.401699/4, choice improvement 9.430640, RT cost 133.760355. Source root: `/mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/`. This verifies the table, not optimizer convergence or a calibrated inferential threshold.
- E's displayed early/late model table uses **choice-best gain**. The report also gives the stored joint-gain late-window contrast: −1.44 pp, versus −2.98 pp at choice-best gain; observed +0.12 pp. Keep the gain setting explicit. Source: E report E4 and `diagnostics/e4_model_vs_D_summary.csv`.
- The time-window quantities are increments of cumulative response contrasts, as implemented in `scripts/pulse_followup/diagnostics.py` (`at(v, hi) - at(v, lo)`). The late negative model increment is partial erosion of its earlier positive cumulative contrast; its final cumulative contrast remains positive. It is not necessarily an overall reversal of preference.
- The trial counts need reconciliation before a correction: A's `pulse_direction_recovered` identifies **43 rows = 38 genuine pulses + 5 null pulses**. Another **5 rows** have unknown direction. E's **43 mislabelled controls = 38 genuine pulses + those 5 unknown-direction rows**; these are different sets. The 5 recovered null pulses remain physically null. Verified by grouping `data/trial_table.csv`, and from `diagnostics/e1_mislabel_impact.csv` plus E's classification code.

### Interpretation corrections
- **“The stimulus cannot explain it” is too strong.** B measured factors 1.28–1.40 for specific UCLA replay alternatives under its ME representation. Acquisition frame rate, lifetime, refresh and geometry are unresolved; B explicitly did not test every alternative. Use: “The replay alternatives tested did not account for the model–data discrepancy.” These ratios are neither a universal error ceiling nor a confidence bound on all stimulus uncertainty.
- **“Shared latency is out” is too strong.** D found no clear common response-rate/latency effect; its intervals allow modest effects and averaging can hide heterogeneous ones. This makes a common-burst candidate lower priority; it does not exclude every engagement or response-delay model.
- **“Delayed and sustained internal pulse effect” is not established.** Responses carrying the directional difference mainly occur later. A cumulative difference can persist without additional late effect; G1's time-local generator demonstrates exactly that. An added internal filter is a candidate explanation of the output timing, not an identified sensory or integration time constant.
- Near-equality of group control and pulse coherence departures supports a shared-misfit explanation but does not by itself fully attribute the asymmetry within mice.
- The rounding-shift calculation is a rough slope-based sensitivity, not a strict upper bound on the effect of a small persistent stimulus change. Keep its assumptions explicit.

## Proposed pilot specification for the coordinator

1. **Correct the input independently of whether modelling proceeds.** Preserve old inputs/results. List exact affected trial IDs and distinguish genuine, null and unknown-direction cases. Unknown directions must not be silently treated as controls or assigned invented signs. Check conditions, pulse/no-pulse decomposition and whether affected ME replays encoded the pulse correctly; changing labels alone may be insufficient. If corrected replay is needed, benchmark that subset and update the time estimate.
2. **Use the same corrected inputs for reference and extension.** Freeze the original control parameter values for this diagnostic pilot, but disclose that the old control fits included affected outcomes. Do not call newly relabelled trials clean held-out predictions under those fits. Check whether the pilot ranking survives omitting all affected rows from scoring. Before a strong later validation, address control-fit contamination through a corrected refit or an explicitly justified sensitivity design.
3. **Freeze one added parameter per mouse:** causal exponential filtering of the existing pulse component, normalized to unit area, with tau = 0 exactly reproducing the reference. Normalize the kernel independently of each trial's RT and analysis deadline; do not renormalize a truncated tail to force its full area into the observed window. Keep controls unchanged. This is phenomenological additional filtering, not an acquisition correction established by B.
4. **Use the proposed coarse tau grid as a screen.** The gain grid must cover both the existing joint optimum and the choice-only optimum, including the reference values; a grid only around the choice optimum unfairly handicaps tau = 0. Both candidates use identical likelihood terms, smoothing, eligibility and censoring.
5. **Fit both tau and gain on training folds only**, then evaluate held-out joint score and diagnostic curves. Picking tau from all trials and cross-validating gain alone is insufficient. The two mice and candidate were selected after seeing the data, so the entire pilot stays exploratory.
6. **Define progression before running.** Require a reproducible held-out joint improvement in each target mouse beyond measured simulation variation, together with improvement in the specified temporal mismatch and no compensating deterioration in choice/no-response predictions. Inspect gain-optimum convergence as a diagnostic, not a sufficient pass criterion. Repeat the reference and leading candidate with independent simulation seeds; the existing dense-mouse profiles used one seed.
7. **Permit three outcomes:** promising; unsupported within the tested grid; inconclusive (flat profile, grid-edge optimum, unstable gain, numerical variation, or label sensitivity). Failure of this small fixed-parameter grid does not rule out every temporally filtered model. Do not automatically broaden the grid or launch full F/G.

The original estimates of roughly 30 minutes of correction work and 25 minutes for the reduced grid are planning estimates before these checks. E's timing extrapolation uses elapsed evaluation times on a multithreaded, variably loaded machine; its “CPU-hours” label should not be treated as a precise core-hour budget. Full validation remains a separate decision. Continue the behavioural write-up in parallel with any authorized pilot.

## What didn't work / what was not done
No model extension, correction, simulation, job or new inferential test was executed. The review cannot establish that the new model will help. A universal stimulus bound, exclusion of all latency mechanisms, and mechanistic inference from a cumulative curve are not supported by the current evidence.

## How to reproduce
Read the E, B, D and G1 reports linked by the master plan and the behavioural Results draft. Inspect these saved sources without rerunning analysis:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from pathlib import Path
import pandas as pd
r = Path('/mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b')
t = pd.read_csv(r/'data/trial_table.csv', low_memory=False)
print(t.loc[t.pulse_direction_recovered].groupby(['mouse','pulse_category']).size())
print(t.loc[t.pulse_category.eq('pulse_direction_unknown')].groupby('mouse').size())
print(pd.read_csv(r/'diagnostics/e1_mislabel_impact.csv').to_string(index=False))
o = pd.read_csv(r/'diagnostics/e3_optima.csv')
print(o[o.mouse.isin(['PSUIM6','PSUIM7']) & o.scope.eq('in_sample')].to_string(index=False))
s = pd.read_csv(r/'diagnostics/e4_model_vs_D_summary.csv')
print(s[s.quantity.eq('direction') & s.feature.eq('window_2-4.58')].to_string(index=False))
PY
```

## Caveats and next steps
- This is an independent review/handoff. The pulse coordinator retains ownership of STATUS, the master plan, code and manuscript integration; none was edited here.
- [ ] Coordinator qualifies the overclaims and distinguishes both sets of 43 rows.
- [ ] User decides whether to authorize correction and the bounded pilot; freeze the specification before running.
- [ ] Preserve the existing behavioural result and continue writing regardless of the pilot outcome. Any stronger mechanism claim still requires G2–G5.
