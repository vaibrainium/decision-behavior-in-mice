# NHP SSM source and task-relative pulse inputs

**Completed continuation:** the user authorized installation and then selected physical direction × time inputs as primary. The exact fork is now installed in `/mnt/data/venvs/nhp-glmhmm-2026-11-15`; runtime checks and a bounded pilot are complete. See [pilot results](../nhp_pulse_hmm_2026-11-15/RESULTS.md). Setup-not-yet-run statements below describe the earlier dependency audit. The alternate target-relative export remains available.

The NHP project obtains SSM from **the author's fork, `vaibrainium/ssm`**. Both [requirements.txt](https://github.com/vaibrainium/prior-encoding-in-nhp-sc/blob/b42fb00ed243ace8dc831a6c72caca7c7494d8d2/requirements.txt) and [pyproject.toml](https://github.com/vaibrainium/prior-encoding-in-nhp-sc/blob/b42fb00ed243ace8dc831a6c72caca7c7494d8d2/pyproject.toml) specify it. The [NHP uv.lock](https://github.com/vaibrainium/prior-encoding-in-nhp-sc/blob/b42fb00ed243ace8dc831a6c72caca7c7494d8d2/uv.lock) pins the exact source:

```text
ssm @ git+https://github.com/vaibrainium/ssm.git@a109af369797d852904fd9496f3532524de8f15a
```

The package's version string is `0.0.1`; the Git commit identifies this implementation more precisely. Source snapshots and original GitHub blob hashes are recorded in `dependency_audit.json` and ignored `cache/source_audit/`.

## Dependencies and setup

Relevant NHP lock versions: Autograd 1.8.0, Cython 3.2.4, NumPy 2.2.6, SciPy 1.15.3, Numba 0.65.0 and scikit-learn 1.7.2. The fork compiles the C++/Cython extension `ssm.cstats`; its build specification requires NumPy >=2.0. The NHP project selects Python 3.10 and declares >=3.10, with lock resolutions also covering 3.12.

The existing mouse environment is Python 3.12.12 / NumPy 1.26.4 and lacks SSM, Autograd and Cython. Installation/build compatibility has **not** been tested here. `requirements-build.txt` and `requirements-glmhmm.txt` prepare a small direct-dependency specification from the NHP lock, rather than a complete transitive environment lock.

Commands for a **separate** Python 3.10 environment, prepared but not executed:

```bash
python3.10 -m venv /mnt/data/venvs/nhp-glmhmm-2026-11-15
/mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m pip install -r /src/dissemination/nhp_ssm_2026-11-15/requirements-build.txt
/mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m pip install --no-build-isolation -r /src/dissemination/nhp_ssm_2026-11-15/requirements-glmhmm.txt
cd /src
/mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m scripts.behavior.check_nhp_ssm_install
```

The final command checks exact Git provenance, input-driven observations, mask invariance, transition convention, coefficient sign, prediction before current choice, and the EM interface. Its syntax was checked; its runtime checks remain pending installation. No packages were installed or upgraded during this audit.

## Important source-level details

- `observations="input_driven_obs"` resolves to the required `InputDrivenObservations`. It supports masks and the prior used by the NHP fitter.
- `HMM.filter` returns the current state distribution given **preceding** outcomes in this pinned fork. Its implementation transitions the preceding posterior and prepends the initial distribution. This supports the intended pre-choice state analysis.
- Standard transition parameters are **log probabilities**, so initializing a desired transition matrix `A` requires `(log(A),)`. The legacy NHP utility passes its constructed matrix directly; that does not initialize the numerical transition probabilities stated by that construction. This affects initialization, not proof that its fitted results are invalid. Audit/correct this when adapting the fitter.
- For binary observations the fork places its learned weights on class 0 and uses class 1 as the reference. With 0=left/1=right, a positive stored coefficient increases left-choice odds. Report right-choice effects with the corresponding sign conversion.

Sources: pinned fork `ssm/hmm.py`, `ssm/observations.py`, `ssm/messages.py`, `ssm/transitions.py`; exact URLs/hashes in `dependency_audit.json`. These are source-level checks, not a successful installation test.

## Six pulse types relative to the task-assigned correct side

The author's clarified definition is implemented: **three onset stages × congruent/incongruent with the task target**. Control trials are the all-zero reference. The retained sample includes 1,388 zero-coherence pulse trials; they remain classified using the task target. All 25,493 original scored choices and 30,146 saved records remain in the same order with identical masks.

Use the corrected export:

```text
target_inputs_v2/cache/nhp_target_congruency6_inputs.pkl
```

It contains session-wise observations, inputs, masks, aggregate row IDs, original physical pulse types, task target directions, and six ordinary 0/1 pulse-type indicators. The **model input** columns carry target sign for a right/left choice outcome, so target-left congruent pulses lower right-choice odds and target-right congruent pulses raise them under a positive right-choice sensitivity. This avoids pooling opposite directions into one unsigned right-choice effect. The six category labels themselves remain ordinary one-hot indicators in `pulse_type_indicators`.

Export command executed:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.behavior.make_nhp_pulse_inputs --encoding target_congruency --output /src/dissemination/nhp_ssm_2026-11-15/target_inputs_v2
```

`target_encoding_verification.json` checks the categories independently against schedule/target, confirms unchanged masks/choices/order and confirms that the first and second exports have identical arrays. The first export had a **manifest-only** missing-target counter error caused by a reused variable; v2 corrects that counter. Preserve both, use v2.

Target provenance differs between rigs. UW logs its assigned target, and the previously pinned task source verifies target assignment before response, including randomized sides at zero coherence. UCLA's processed target is reconstructed from `Response` and `Correct`; its raw file has no independent target column. The scheduled pulse congruency agrees with raw `BurstCoh` in every retained UCLA pulse. The previously cited UCLA task repository currently returns 404, so this audit cannot newly verify its assignment code. The target-relative interpretation relies on the author's definition and the existing task-side reconstruction; do not describe UCLA targets as independently logged or claim that consistency proves the absence of response leakage.

Unknown targets on masked rows remain masked and receive no target-dependent choice emission. This preserves sequence order without inventing a target or a choice. Outcome-dependent filtering still limits interpretation.

No exact NHP model fit was run. Next: install the pinned fork after authorization, pass the prepared smoke test, then compare common versus state-dependent pulse coefficients with the same future-block prediction target.
