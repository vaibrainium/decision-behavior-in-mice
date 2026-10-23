# Report: new control-strategy and recovery results incorporated into the paper
Date: 2026-10-22   Agent: Codex   Commit: 17511ca (verification snapshot; manuscript changes uncommitted)
Plan: plans/2026-10-20-paper-writeup.md, results arrival steps E–F

## Question
What changed when the queued control fits and model-recovery outputs arrived, and what can now be written?

## Summary
Independently recomputed the control-strategy comparison and guess-bias score difference from saved fits, and
recomputed recovery rates and parameter correlations in memory. Incorporated these results into manuscript Results,
Abstract and Discussion, with uncertainty caveats. The independent pulse comparison remains pending: no primacy
output directory existed during this inspection, and no observed pulse outcomes were examined.

## Findings
- VERIFIED: free-bias control CV favours the integrator over the extrema approximation by summed 345.7 NLL units;
  differences exceed 10 in six mice, with none favouring extrema by that amount. `scripts.ddm.compare_strategy`
  recomputed this from `/mnt/data/processed/ddm/fits_guess_fast_only_leak20-200/*_ccv*.pkl` and matching
  `fits_guess_fast_only/*_L0U0V1Z0G1_ccv*.pkl` at 17511ca. This is a within-model-pair control comparison,
  not the independent pulse test or a population significance test.
- VERIFIED: extrema drift gain is not at either bound; amendment 5 does not trigger a gain-bound refit. In the
  free-bias saved fits, sv >= 2.97 in 2/60 extrema fits and 10/50 control-CV integrator fits. This remains a caveat.
- VERIFIED: fixed-minus-free guess-bias all-trial CV NLL is 65.4743 summed over mice. It exceeds 10 in three mice
  and is never below -10. Compared matching `*_L0U0V1Z0G1_cv[0-4].pkl` in `fits_guess_fast_only` and
  `fits_guess_fast_only_FB`; verified the documented free-bias decision rather than making a new one.
- VERIFIED: all 500 recovery pickles exist, all fast_only/free-bias. At threshold >10, guess hits are 20/20 and
  false positives 3/20; sv hits 17/20 and false positives 7/20; leak hits 7/20 and urgency hits 9/20, each with
  false positives 3/20. Each denominator pools ten mice and two replicates. Many added-mechanism generating
  values are near zero, so model labels alone do not define a meaningful present/absent contrast.
- VERIFIED: worst training-score gap (recovered minus generating parameters) across matched generator/candidate
  fits is -6.5601 NLL. The optimizer reached a better training score than this available reference in every case;
  global optimality is not established. Common-model parameter correlations: gain 0.924, guess probability 0.933,
  sv 0.848, guess delay 0.181. Source: recovery pickles, `parameters`, `true_parameters`, `truth_train_nll`.
- VERIFIED: free-bias descriptive leak fits are below 1/s for every mouse (maximum 0.824865/s), and training NLL
  is no higher than either matching restricted control fit. Sources: `fits_guess_fast_only_leak0-200/*_control.pkl`
  and matching common/extrema control fits. No interval for a biological integration time is available.
- VERIFIED (visual inspection): `dissemination/figures/ddm_fit_quality_L0U0V1Z0G1_fits_guess_fast_only.png`
  shows high-coherence error-time and late-response discrepancies. It uses all-trial fits on control trials and
  is descriptive; it is not independent validation of pulse predictions. Avoid calling fit quality uniformly good.

## What didn't work
No new execution failures. The existing all-model recovery exercise does not directly assess discrimination of
the high-leak extrema model from the common model on pulses. Its success rates must not substitute for the
amendment 5 strategy sensitivity simulations. Limited replicates and noisy scores also limit recovery interpretation.

## How to reproduce
Use the existing project environment; these commands read results and print summaries without writing tables:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.ddm.compare_strategy
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from pathlib import Path
import pickle
import numpy as np
base = Path('/mnt/data/processed/ddm')
def load(path):
    with path.open('rb') as f:
        return pickle.load(f)
C = 'L0U0V1Z0G1'
delta = sum(load(base/'fits_guess_fast_only_FB'/p.name)['test_nll'] - load(p)['test_nll']
            for p in (base/'fits_guess_fast_only').glob(f'*_{C}_cv[0-4].pkl'))
print('fixed minus free guess bias NLL:', delta)
results = [load(p) for p in (base/'recovery').glob('*.pkl')]
ix = {(r['mouse'], r['generator'], r['replicate'], r['candidate']): r for r in results}
for letter in ['G', 'V', 'L', 'U']:
    on, off = C.replace(letter+'0', letter+'1'), C.replace(letter+'1', letter+'0')
    for gen in [on, off]:
        ds = [ix[m,g,k,off]['test_nll'] - r['test_nll']
              for (m,g,k,c), r in ix.items()
              if g == gen and c == on and (m,g,k,off) in ix]
        print(letter, gen, len(ds), np.mean(np.array(ds) > 10))
same = [r for r in results if r['generator'] == r['candidate']]
print('worst training gap:', max(r['train_nll']-r['truth_train_nll'] for r in same))
common = [r for r in same if r['generator'] == C]
for param in common[0]['free_parameters']:
    print(param, np.corrcoef([r['true_parameters'][param] for r in common],
                             [r['parameters'][param] for r in common])[0, 1])
PY
```

Original analysis log section 5.8 was committed at 3c0a061. The reader script is at 17511ca; individual fitting
execution environments/commits still require run provenance. No new scientific fits or rescoring simulations were run.

## Caveats
Score deltas above are not p values. Monte Carlo thresholds from previous comparisons are approximate for this
comparison. Recovery rates pool very few replicates per mouse, and correlation across mice does not establish
within-mouse identifiability. Human evidence verification remains pending. The dated manuscript is updated in place;
scientific result files were not overwritten.

## Open questions and next steps
- [ ] Complete strategy sensitivity and freeze all required pulse predictions with commit hashes.
- [ ] Run predictive gate and strategy comparison in the agreed order, then condition timing interpretation on adequacy.
- [ ] Retain sv-bound, recovery and fit-quality caveats when discussing integration.
- [ ] Finish remaining author facts, hidden-coherence sensitivity and figures as tracked in the writing plan.
