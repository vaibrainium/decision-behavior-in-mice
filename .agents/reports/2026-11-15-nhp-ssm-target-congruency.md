# Report: NHP SSM provenance and target-relative pulse encoding
Date: 2026-11-15   Agent: Codex   Commit: b63c9d9 (base; changes uncommitted)
Plan: plans/2026-11-14-history-state-diagnostics.md

## Question
Where does the author's NHP project obtain SSM, and can its pulse inputs use the clarified task-assigned correct side?

## Summary
The NHP requirements and project metadata specify vaibrainium/ssm. Its lockfile pins a109af369797d852904fd9496f3532524de8f15a. The exact fork has input-driven observations, mask support and a pre-current-choice filter. Task-relative six-category inputs are now exported without dropping zero-coherence pulses or changing the observed population. No packages were installed; runtime build/fitter verification remains pending.

## Findings
- VERIFIED: NHP `requirements.txt` and `pyproject.toml` name `git+https://github.com/vaibrainium/ssm.git`; `uv.lock` pins a109af369797d852904fd9496f3532524de8f15a. NHP source commit: b42fb00ed243ace8dc831a6c72caca7c7494d8d2. Original lock blob: e884de5bc19171b4ee7f59221352836106880869. Source paths/URLs/hashes: `dissemination/nhp_ssm_2026-11-15/dependency_audit.json`.
- VERIFIED: relevant lock versions are Autograd 1.8.0, Cython 3.2.4, NumPy 2.2.6. The fork builds C++/Cython `ssm.cstats` and its build file requires NumPy >=2.0. Current mouse environment has NumPy 1.26.4 and no SSM/Autograd/Cython. Separate setup files prepared, not installed. Source: pinned NHP lock, fork setup files, `dependency_audit.json`.
- VERIFIED BY SOURCE: pinned fork supports `input_driven_obs` and masks. `HMM.filter` returns the current state distribution conditional on preceding observations. Transition parameters accept log probabilities; binary learned weights favor class 0, so sign conversion is needed for right-choice interpretation. Source: fork `ssm/hmm.py`, `observations.py`, `messages.py`, `transitions.py`, preserved source snapshots.
- VERIFIED: six categories are onset stage × congruent/incongruent with the recorded task target. All 25,493 observed choices and 30,146 saved records keep identical masks/order, including 1,388 observed zero-coherence pulse trials. All scored targets are known. Source: `scripts/behavior/make_nhp_pulse_inputs.py --encoding target_congruency --output /src/dissemination/nhp_ssm_2026-11-15/target_inputs_v2`; `target_encoding_verification.json` and adjacent v2 counts/audit.
- VERIFIED: target and outcome are consistent in every retained response; nonzero-coherence target matches baseline sign; UCLA scheduled pulse congruency agrees with raw BurstCoh in all retained pulses. UW directly logs target; its pinned task code assigns it before response. UCLA target is reconstructed from Response/Correct and is not independently logged. The previously cited UCLA source repo currently returns 404, so its code could not be newly checked. INTERPRETATION/ASSUMPTION: use the author's task-assigned-target definition with this provenance limitation, rather than claiming independent UCLA target validation.

## What didn't work
- Large-file `fetch_file` returned empty lockfile content; the repository contents fetch retrieved the full lock. Extracted selected package records, without confusing an empty response with an empty lockfile.
- Original task source URL vaibrainium/RDK-Task is unavailable (404); inspected prior audit, raw fields and accessible pinned UW code instead. No new verification of UCLA source claimed.
- First target export had a manifest-only missing-target count collision from a reused variable. Corrected in `target_inputs_v2`; independently verified v1/v2 arrays are identical. Use v2; preserve v1.
- No installation/build or post-install smoke test was attempted. Prepared smoke code is syntax-checked only; do not report it as passed.

## How to reproduce
From `/src`, existing `.venv`, single-thread BLAS:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m tests.test_pulse_feature_encoding
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.behavior.make_nhp_pulse_inputs --encoding target_congruency --output /src/dissemination/nhp_ssm_2026-11-15/target_inputs_v2
.venv/bin/python -m py_compile scripts/behavior/check_nhp_ssm_install.py scripts/behavior/make_nhp_pulse_inputs.py
```

These document executions; use a new output directory for reruns. The independent export verification iterated every session, compared masks/choices/aggregate row order with the physical-six export, and recomputed pulse membership from target/schedule; recorded in `target_encoding_verification.json`. Source hashes, source snapshots and the precise fork install specification are in the adjacent dependency audit and README. No raw data or previous results modified.

## Caveats
Target-relative model columns carry target sign for right/left outcomes; ordinary unsigned category indicators are also saved separately. Current-choice-derived target reconstruction in UCLA must be stated, especially at zero coherence. Masking preserves logged chronology, not noninformative missingness. Dependency files pin direct requirements, not a complete independently resolved transitive environment. Source compatibility checks do not certify a successful local build.

## Open questions and next steps
- [ ] With package-install authorization, create an isolated environment using the prepared files; run `scripts.behavior.check_nhp_ssm_install` there.
- [ ] Correct transition initialization to log probabilities when adapting the NHP utility, and account for its binary coefficient sign.
- [ ] Then run the small common-versus-state-specific pulse comparison with the same prefix prediction target; do not interpret a choice-only state win as accumulation-memory or attention identification.
