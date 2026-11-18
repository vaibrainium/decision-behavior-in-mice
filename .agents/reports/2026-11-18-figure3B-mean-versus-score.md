# Report: mean-curve agreement versus held-out score
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; diagnostic uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Why do E/ES appear closer to plotted means despite C having better held-out LL?

## Summary
The visual impression is supported for mean RT under an equal-cell descriptive metric. It does not contradict archived held-out quantile log-score ranking. Curves and scores differ in fit source, summary statistic and weighting. Exact contributing RT ranges/cells are not established by this diagnostic.

## Findings
- VERIFIED: unweighted RMSE across displayed group mean-RT coherence/choice cells: C0.0917039983s, E0.0734549438s, ES0.0815820596s, DDMx0.1410786509s, ESx0.1460930519s. Source: figure3B_control_fits_2026-11-18/rt_group.csv under dissemination/paper_accumulation/draft_2026-11-15. This is a descriptive error of group means, not a subject-level test, uncertainty estimate or replacement model-selection criterion.
- VERIFIED: corresponding unweighted RMSE of displayed P(right) group means: C0.0340868139, E0.0366152589, ES0.0352120396, DDMx0.0371764611, ESx0.0326640446. Source: same directory psychometric_group.csv. Thus E/ES do not improve this psychometric metric over C.
- VERIFIED: archived held-out mean per1000-trial NLL advantages for C versus E: choice2.5463479401, conditional RT10.2101159573; versus ES: choice1.2166813821, RT17.5282818109. Source: figure3_control_results_2026-11-17/source_data/fig3_AB_group_statistics.csv. These are different estimands from plotted group-cell RMSE.
- EXPLANATION: full-control fitted mean curves and CV test scores use distinct parameter sets. Quantile objective scores choice and conditional RT-bin probabilities, not mean-RT squared error. Condition trial counts weight score contributions; plots equally average eligible mouse means and the RMSE equally weights displayed cells. Averaging can hide subject-specific discrepancies. None establishes which exact tail/coherence/subject explains the ranking here.

## What didn't work
No failed checks. No claim that C must have the closest mean curve; no selective adjustment of curves to enforce the LL rank.

## How to reproduce
From /src, existing .venv:
```python
import pandas as pd, numpy as np
from pathlib import Path
p=Path('dissemination/paper_accumulation/draft_2026-11-15/figure3B_control_fits_2026-11-18')
for filename,keys in [('psychometric_group',['coh']),('rt_group',['coh','choice'])]:
    t=pd.read_csv(p/(filename+'.csv'))
    d=t[t.model=='data'].set_index(keys)['mean']
    for model in ['C','E','ES','DDMx','ESx']:
        z=t[t.model==model].set_index(keys)['mean']
        print(filename,model,np.sqrt(np.mean((z-d)**2)))
```
Score arithmetic/provenance: reports/2026-11-17-ddm-likelihood-audit.md. Plot provenance: reports/2026-11-18-figure3B-control-fits.md. Exact source hashes already recorded in panel manifests.

## Caveats
Single finite simulation seed for displayed means. No new significance or adequacy inference. RT quantiles/sparse-cell rules remain as audited; held-out score is not continuous RT density or trial-specific stimulus-outcome density.

## Open questions and next steps
- [ ] If author wants to locate why C scores better, inspect matched per-mouse/per-condition conditional RT quantiles and score contributions with the same CV parameters and scoring bins.
- [ ] Retain honest C mean-fit discrepancies and avoid calling it best on every behavioral summary.
