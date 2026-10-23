# Report: frozen pulse predictions and low strategy discrimination
Date: 2026-10-22   Agent: Codex   Commit: 002fafb (reader snapshot; manuscript changes uncommitted)
Plan: plans/2026-10-20-paper-writeup.md, steps G–H

## Question
Do the newly frozen predictions separate the fitted strategies, and is the planned pulse test sensitive?

## Summary
All frozen prediction checksums match. Both strategies predict small and similar pulse effects. The completed
synthetic test rarely selects the generator with the primary pulse-specific statistic. Updated the manuscript
to distinguish control-trial model preference from limited independent pulse discrimination. No recorded pulse
choices or reaction times were read; no observed-analysis result files existed at the inspection.

## Findings
- VERIFIED: all 30 SHA-256 entries in `dissemination/reports/primacy_predictions_sha256_17511ca.txt` match
  `/mnt/data/processed/ddm/primacy/{primary,secondary,extrema}/*.pkl`. Each records prediction commit
  `17511ca598b3f92fad3e6d44aea4c38d114d8163` and 200 repetitions; trial rows match across models per mouse.
  Prediction tables do not contain observed choice, RT, responded or y columns.
- VERIFIED: at |coherence| <= 0.36, predicted pulse effects (mean of per-mouse means, logit) are integrator
  0.027989 / 0.029354 / 0.027378, extrema 0.039751 / 0.039060 / 0.035411, and secondary 0.024370 / 0.025035 /
  0.026771 for early/middle/late. Late includes UW only. Source: frozen tables, logit(p_hat)-logit(nopulse_p_hat).
  These are model predictions, not observed pulse effects or statistical timing comparisons.
- VERIFIED: `strategy_power.csv` has 20 full-cohort datasets per generator. Primary pulse_gain selects extrema
  in 1/20 extrema-generated datasets and integrator in 0/20 integrator-generated datasets; all other verdicts
  are not distinguished. Secondary total likelihood selects the correct generator in 5/20 and 7/20 respectively.
  File SHA-256: `3944aa0dcb264dbd9b193d3d22a00872879a76746c72ad8e4f10c67f5dc205b3`.
- VERIFIED (implementation inspection): `scripts/ddm/check_strategy_test.py::power` simulates outcomes for each
  mouse from the fitted generator and evaluates both frozen candidate tables via `primacy.strategy_test`.
  It does not read recorded outcomes to calculate these verdicts.
- INTERPRETATION: sensitivity is low under these fitted candidates and the frozen scoring procedure. This is not
  evidence that actual pulse effects are small, that the strategies are equivalent, or that primacy is absent.
  Preserve the prespecified statistic rather than promoting total likelihood after viewing its higher success rate.

## What didn't work
The initially inspected strategy_power.csv contained only the first dataset per generator; it completed during
inspection. Re-read the completed file and report the final hash and denominators above. No conclusion is based
on the incomplete first read. Did not rerun the simulation or overwrite its output.

## How to reproduce
From `/src`, existing project venv, no installs or simulations:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from pathlib import Path
import hashlib, pickle
import pandas as pd
from scipy.special import logit
b = Path('/mnt/data/processed/ddm/primacy')
for line in Path('dissemination/reports/primacy_predictions_sha256_17511ca.txt').read_text().splitlines():
    expected, name = line.split(maxsplit=1)
    assert hashlib.sha256((b/name.strip()).read_bytes()).hexdigest() == expected
tables = []
for model in ['primary', 'secondary', 'extrema']:
    for p in sorted((b/model).glob('*.pkl')):
        with p.open('rb') as f:
            r = pickle.load(f)
        assert r['n_reps'] == 200 and r['commit'].startswith('17511ca')
        t = r['trials']
        assert not {'choice', 'rt', 'responded', 'y'} & set(t.columns)
        t = t[t.coh.abs() <= .36+1e-9].copy()
        t['effect'] = logit(t.p_hat)-logit(t.nopulse_p_hat)
        t['model'] = model
        tables.append(t)
t = pd.concat(tables)
print(t.groupby(['model','mouse','timing']).effect.mean().groupby(['model','timing']).mean())
p = b/'strategy_power.csv'
print('power hash:', hashlib.sha256(p.read_bytes()).hexdigest())
d = pd.read_csv(p)
print(d.groupby('generator').size())
for stat in ['pulse_gain','total']:
    print(stat, d.groupby('generator')[stat+'_favoured'].value_counts())
PY
```

Original prediction/sensitivity implementation and freeze record: 002fafb. Predicted parameters/code: 17511ca.
The sensitivity CSV has no embedded execution commit; reader snapshot and byte hash identify the inspected result.

## Caveats
Twenty simulated datasets per generator give coarse empirical sensitivity estimates. The simulation conditions on
fitted parameters and a fixed set of predictions, without refitting or integrating parameter uncertainty.
It assesses the strategy statistic, not gain-decay/primacy sensitivity. Prediction integrity is not a new simulation
reproducibility check. Final-fit precision and gate prerequisites remain separate requirements.

## Open questions and next steps
- [ ] Resolve any remaining final-fit/gate prerequisites, then run the planned predictive check before observed strategy analysis.
- [ ] Report observed comparisons even if inconclusive, alongside this sensitivity result; do not claim pulse confirmation from a null.
- [ ] Complete separate temporal-weighting sensitivity before interpreting its absence.
- [ ] Obtain remaining author facts and finish figures/verification for the manuscript.
