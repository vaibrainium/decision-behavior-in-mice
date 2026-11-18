# Shared psychometric helper: multistart verification

The helper now defaults to deterministic multiple starting points, retaining the original solver candidate and choosing the smallest weighted residual error. No saved figure, preprocessing selection, or accepted model result was regenerated.

```python
from src.utils.pmf_utils import fit_psychometric_function
fit = fit_psychometric_function(x, p_right, counts, "logit_4")
legacy = fit_psychometric_function(x, p_right, counts, "logit_4", multistart=False)
print(fit.coefs_, fit.weighted_sse_, fit.fit_diagnostics_)
```

The class constructor also accepts multistart=False, including through sklearn get_params/clone. Equations, bounds, trial-count weights, coefficient names, covariance and return type are preserved. Additional starts cover three midpoint locations within observed coherence support, three slopes scaled to the coherence range, and two nuisance-parameter settings within supplied bounds. Duplicate starts are removed: normally19 total for logit3/logit4 and10 for logit2. The legacy candidate uses scipy defaults; extra candidates use tighter tolerances and a3000-evaluation limit. Failed/nonfinite candidates are recorded and skipped; if all fail a RuntimeError is raised. Selected covariance warnings are surfaced; numerical solver warnings are recorded without changing process-wide warning filters. Invalid counts/array shapes now raise ValueError.

Diagnostics include per-start errors/warnings, successful attempt count, selected start, boundary contacts, covariance finiteness and weighted SSE. These do not prove parameter identifiability or a global optimum. More starts increase fitting cost. Use multistart=False to reproduce historical solver behavior when rerunning old preprocessing or historical figure scripts. Reprocessing can change fitted-parameter-based inclusion; it must be treated as a new data version rather than silently replacing old selections.

Regression checks:
`.venv/bin/python -m unittest tests.test_psychometric_multistart -v`

Five tests cover real local-solution fixtures, weighted selection, exact single-start opt-out, all three model forms with custom bounds/missing responses, sklearn cloning, optimizer failures and invalid inputs. Independent saved-data check: all20 individual pulse curves improve or retain weighted SSE; material improvements (>1e-5) occur in the same2 audited curves. comparison.csv and manifest.json preserve results/input hashes. Reproduce the20-curve check with the following from repo root:

```python
import numpy as np
import pandas as pd
from src.utils.pmf_utils import fit_psychometric_function
p = "dissemination/paper_accumulation/draft_2026-11-15/figure4_revision_2026-11-18_v5/source_data/fig4_A_psychometric_mouse.csv"
t = pd.read_csv(p)
for key, z in t[t.pulse.isin([-1, 1])].groupby(["mouse", "pulse"]):
    args = (z.coherence_pct.to_numpy(), z["mean"].to_numpy(), z["size"].to_numpy(), "logit_4")
    old = fit_psychometric_function(*args, multistart=False)
    new = fit_psychometric_function(*args)
    assert new.weighted_sse_ <= old.weighted_sse_ + 1e-12
    print(key, old.weighted_sse_, new.weighted_sse_)
```
