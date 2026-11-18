# Report: Shared psychometric helper multistart
Date: 2026-11-18   Agent: Codex   Commit: 6c0d164 (base; helper update uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Should the shared psychometric helper use multiple starting points after the paired-fit optimization audit?

## Summary
Implemented deterministic multistart by default, retaining the original candidate and choosing minimum WLS among successful finite solutions. Added exact legacy opt-out, diagnostics and regression tests. Kept equations, bounds, weights and fitted-object API. Existing preprocessing/figures not rerun.

## Findings
- VERIFIED: five unittest methods pass, including the two observed local-solution cases, exact original-solver reproduction with multistart=False, all three models/custom bounds, NaN-response handling, sklearn cloning, failed starts and invalid inputs. Source: tests/test_psychometric_multistart.py and command below.
- VERIFIED: all20 saved individual pulse curves have equal or lower weighted SSE. Two material improvements (>1e-5): DBM12-left0.03055059 and DBM13-left0.53392423, agreeing with the previous audit's objective improvements. Source: dissemination/psychometric_helper_multistart_2026-11-18/comparison.csv, manifest.json.
- VERIFIED: all19 starts converged for each of the20 saved four-parameter curves. Source: same comparison table. Success does not establish parameter identification.
- VERIFIED: equations/bounds/weights and coefficient/covariance API preserved. Additional attribute weighted_sse_ and fit_diagnostics_; constructor option multistart defaults True. Source: src/utils/pmf_utils.py.

## What didn't work
An initial attempt to switch the logistic calculation to expit changed the returned coefficients along nearly flat objectives even in legacy mode. Reverted this change to retain original numerical evaluation and exact opt-out compatibility. Additional starts address optimization without changing the model calculation. No parameter-identification fix claimed.

## How to reproduce
`.venv/bin/python -m unittest tests.test_psychometric_multistart -v`
Exact20-curve check code, usage and source paths: dissemination/psychometric_helper_multistart_2026-11-18/README.md. Input/script/test hashes: manifest.json. Existing .venv; no package installation.

## Caveats
Helper is also used in preprocessing and other figure scripts. Future default reruns can change coefficients and parameter-based selection; use multistart=False for historical behavior and version any new selection. Current datasets/figures untouched. Weakly identified alpha/beta can differ across equally good solutions; do not equate numerical improvement with precise parameters. More starts increase cost. This implementation uses a support-scaled grid for general input units; it is not the exact historical paper audit's fixed grid, so accepted figures remain tied to their saved audit code/outputs.

## Open questions and next steps
- [x] User requested a separate helper commit; helper, tests, verification and handoff included.
- [ ] Resume Figure4C review; no automatic figure or preprocessing reruns.
