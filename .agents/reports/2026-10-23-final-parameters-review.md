# Report: review of final common-model parameters
Date: 2026-10-23   Agent: Codex   Commit: bb52fe447df03984b695e0b9156db918681cb90d
Plan: plans/2026-10-20-paper-writeup.md (review of arriving results)

## Question
Are the final parameter summaries reproducible, and do the near-bound estimates require immediate refitting for the draft?

## Summary
The saved fits reproduce the table and reported medians/ranges. All ten fits have the expected common-model form, free guess bias, fifty simulation repetitions and warm starts. The boundary wording needs correction: the script flags proximity within 1% of the allowed parameter range, not exact boundary hits. Such estimates are potentially constrained; they are not established lower limits. Recommendation: retain the descriptive table, review fit quality and the ongoing diagnostics before prioritizing refits.

## Findings
- VERIFIED: CSV values match the saved fit parameters; settings and summaries reproduce. Sources: `/mnt/data/processed/ddm/fits_final/*_L0U0V1Z0G1_all.pkl`, `dissemination/paper/parameters_common_model_2026-10-23.csv`; command below.
- VERIFIED: eight parameter values meet the script's proximity rule, and none equals its boundary exactly. Bound separation is 9.465617 in DBM15 and 9.490357 in PSUIM6, with fitting ceiling 9.5. The simulator independently requires `0 < a < 10`. Sources: saved fits; `scripts/ddm/parameter_table.py::main`; `scripts/ddm/fit_mouse_ddm.py::BASE_FREE_PARAMS`; `src/ddm/ddm.py::validate_params`.
- VERIFIED: three guess delays meet the upper proximity cutoff of 0.2971 s. DBM15 is 0.296828 s, below that cutoff; rounding to three decimals conceals the distinction. Source: saved fits and the same proximity calculation.
- INTERPRETATION: replace “at the bound” with “within 1% of the allowed parameter range of a boundary,” and “lower limits” with “near the optimisation ceiling; potentially constrained estimates.” A likelihood profile or widened-bound sensitivity would be needed to establish whether the ceiling materially changes estimates/predictions. No such check was run.
- INTERPRETATION: near-zero fitted nondecision time is conditional on the evidence-input filtering and other model components. It does not establish negligible biological sensory/motor latency. The fast-guess probability is a fitted mixture weight, not a directly observed fraction of guesses. All-trial fit quality is an in-sample check; it does not replace the frozen held-out comparison.
- VERIFIED (script behaviour): despite its preservation comment, rerunning `parameter_table.py` on the same date overwrites that date's CSV/Markdown. It was not executed in this review. Add explicit output versioning/refusal before regenerating the table.

## What didn't work
No fits or new behavioural analyses were attempted. The final fit-quality figure was not available in the initial parameter review; see the subsequent visual review below. All claim hashes were not reviewed here. The inference that proximity alone establishes a lower limit is unsupported.

## How to reproduce
From `/src`, run this read-only check; it does not call the table writer:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from scripts.ddm.fit_mouse_ddm import make_params
variant = 'L0U0V1Z0G1'
table = pd.read_csv('dissemination/paper/parameters_common_model_2026-10-23.csv').set_index('mouse')
free, _ = make_params(variant, 'fast_only')
keys = ['drift_gain', 'sv', 'p_guess', 'guess_bias', 'a', 'z', 'ndt', 'guess_tau']
rows, flags = [], []
for path in sorted(Path('/mnt/data/processed/ddm/fits_final').glob(f'*_{variant}_all.pkl')):
    with path.open('rb') as f:
        fit = pickle.load(f)
    assert fit['variant'] == variant and fit['guess_model'] == 'fast_only'
    assert not fit.get('fixed_guess_bias', False) and fit['split'] == 'all'
    assert fit['n_reps'] == 50 and bool(fit.get('warm_start_seeds'))
    p, mouse = fit['parameters'], fit['mouse']
    for k in keys:
        assert np.isclose(p[k], table.loc[mouse, k], rtol=1e-12, atol=1e-12)
        lo, hi = free[k].lower_bound, free[k].upper_bound
        if p[k] <= lo + .01*(hi-lo) or p[k] >= hi - .01*(hi-lo):
            flags.append((mouse, k, p[k], lo, hi, p[k] == lo or p[k] == hi))
    rows.append({'mouse': mouse, **{k: p[k] for k in keys}})
assert len(rows) == 10 and set(table.index) == {r['mouse'] for r in rows}
print(pd.DataFrame(rows)[keys].agg(['median', 'min', 'max']))
print(flags)
PY
```

## Caveats
The pulse coordinator owns shared STATUS, plan and manuscript integration while parallel work runs. This separate review leaves those files and all analysis inputs/results unchanged. The ongoing trial audit reports input-label/exclusion issues; their effects on legacy parameter estimates are unquantified. Preserve the fitted-input version and address their relevance in the ongoing diagnostics before making mechanistic claims.

## Open questions and next steps
- [ ] Coordinator incorporates the boundary wording into the table/script, analysis log and C078, then updates its claim hash through the established provenance workflow.
- [x] Visually review the completed fit-quality figure (addendum below). Package E's diagnosis is still needed to judge whether a targeted boundary sensitivity is worth the cost.
- [ ] Retain descriptive parameter reporting and avoid biological interpretation of poorly identified components. No refit or cluster submission is authorized by this review.

## Addendum: committed fit-quality figure, 2026-10-23

Source commit: `475934ed5dc7d67d5aa072df79f89a47a1e25a79`. Read-only inspection of `dissemination/figures/ddm_fit_quality_L0U0V1Z0G1_fits_final.png` and the earlier `ddm_fit_quality_L0U0V1Z0G1_fits_guess_fast_only.png`, plus `notebooks/3.0-ddm-fit-quality.ipynb` code cells (zero-based notebook cell indices 1–3). No simulations or rerendering performed.

- VERIFIED VISUALLY: the broad choice/correct-RT patterns and principal error-RT discrepancies persist. Say “captured broad trends” rather than implying all psychometric or correct-RT points are well fitted. High-coherence error RTs are often overpredicted, with exceptions; in PSUIM5 the highest-coherence error prediction is faster than the observed mean. These are visual descriptions, not quantitative tests of residuals or convergence.
- VERIFIED VISUALLY: underprediction of no response by the deadline is apparent at negative 100% coherence in PSUIM5–7. Avoid implying an equal discrepancy at both stimulus directions. Source: right-column panels, signed-coherence axis.
- VERIFIED LABEL ISSUE: the final figure's right column says `P(RT > 5 s)`, whereas `summarize` computes `choice == -1`, including trials without an observed response. Use `P(no response by 5 s)`; the earlier PNG already uses that label. The plotting label in notebook cell 3 needs correction before a versioned rerender. The current notebook defaults to the earlier fit directory, so explicitly preserve the `FITS = "fits_final"` override when reproducing the final figure.
- INTERPRETATION: persistence after increasing fitting repetitions reduces the motivation for repeating the same fit solely to reduce simulation noise; it does not prove global optimization or identify the source of the misfit. These are in-sample control-trial diagnostics of models fitted to all trials.
- STATUS: the final-fit package has its parameter table and figure. The separate pulse-follow-up plan still lists E and H as incomplete at inspection; the whole follow-up is not complete. Shared tracking/manuscript files remain with that coordinator.

Coordinator handoff: correct the no-response axis wording in a versioned figure, retain the qualified fit-quality description, and integrate the previously identified boundary wording correction. This review does not request another fitting batch.
