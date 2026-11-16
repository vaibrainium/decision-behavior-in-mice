# Report: installed NHP SSM and pulse-state pilot
Date: 2026-11-15   Agent: Codex   Commit: b63c9d9 (base; new changes uncommitted)
Plan: plans/2026-11-15-nhp-install-pulse-pilot.md

## Question
Does the author's pinned SSM fork run here, and do state-specific pulse coefficients improve future choice prediction beyond changing baseline/history coefficients?

## Summary
Installation and runtime/mathematical checks passed in a separate Python 3.10 environment. The latest user selection governs the pilot: six physical direction × stage inputs, congruency summaries on nonzero coherence. Shared-pulse HMMs improve choice predictions in PSUIM6/7. Freeing pulse coefficients worsens PSUIM6 and gives an unresolved PSUIM7 change. This is not a joint RT model or an identification of attention/integration memory.

## Findings
- VERIFIED: pinned vaibrainium/ssm a109af369797d852904fd9496f3532524de8f15a installed in `/mnt/data/venvs/nhp-glmhmm-2026-11-15`. Exact versions/provenance, build logs and passed checks are under `dissemination/nhp_pulse_hmm_2026-11-15/`. Original DDM NumPy remains 1.26.4. Source: `environment_freeze.txt`, `ssm_smoke.log`, `emission_tests.log` and install logs.
- VERIFIED: 108 prescribed training fits plus 24 training-only shape-start checks completed; all converged. Eighteen selected outer models have no failed observation M-step. Extra starts found better PSUIM6 middle-prefix modes; use version 2 results. Source: `fit_audit.csv`, `search_check.csv`, `assessment_v2/assessment_audit.json`.
- VERIFIED: choice evaluation uses 3,461 / 4,020 identical outer test choices in PSUIM6/7. Shared-pulse HMM gains 0.03757 [0.02165, 0.05350] / 0.01483 [0.00336, 0.02703] bits/trial over static. Free-pulse minus shared gives −0.00296 [−0.00461, −0.00127] / +0.00065 [−0.00436, 0.00570], or +7.11 / −1.82 NLL. Intervals are pointwise, conditional-on-model fifty-original-record block intervals, not animal-population tests. Source: `assessment_v2/heldout_differences.csv`; command `python -m scripts.behavior.assess_nhp_pulse_pilot --version 2` in the new environment.
- VERIFIED: current RT was unused in state inference. Its adjusted association is unresolved in PSUIM6; PSUIM7 shared-model slope is +0.0897 log-RT [0.0228, 0.1537], corresponding to slower responses with higher baseline choice contrast, and is unresolved in the free model (+0.0243 [−0.0277, 0.0761]). This is not a consistent attention/engagement interpretation. Source: `assessment_v2/rt_external_validation.csv`.
- VERIFIED: pilot mice have no late-stage pulse trials under existing strata. All six feature categories remain encoded, but late coefficients are nonestimable. Source: physical-six input pickle and `assessment_v2/coefficients.csv`; counts in detailed RESULTS.
- VERIFIED: marginal nonzero-coherence pulse summaries retain discrepancies. These pool retained RTs and differ from the earlier response-conditioned pulse estimator. Source: `assessment_v2/pulse_congruency_validation.csv`.
- DECISION/INTERPRETATION: retain shared pulse coefficients as the simpler state benchmark. No consistent held-out justification for a broader state-specific pulse-weight campaign. This does not establish equivalence or exclude smaller hidden-state effects; no mechanism recovery was run.

## What didn't work
- System Python 3.10 lacks ensurepip. The created isolated interpreter worked, and existing uv installed packages without system changes.
- Four bias-oriented starts did not always find the best mode. Added two sensitivity-oriented starts to each selected HMM before inspecting test comparisons, retaining fixed priors and training-only selection. Preserve first-pass results; report the changed PSUIM6 comparison.
- Fork EM progress is not the actual post-update model objective (old E-step LL combined with new prior). Selection/convergence use actual `log_probability` after chunks; fork code unchanged.
- State-specific pulse freedom does not consistently improve future choices and does not fix the joint RT/pulse residual.

## How to reproduce
Exact module commands, input/source hashes, environment freeze and figure/table paths: `dissemination/nhp_pulse_hmm_2026-11-15/RESULTS.md`, `pilot_manifest.json`, `search_manifest.json`, `assessment_v2/assessment_audit.json`. Core modules: `fit_nhp_pulse_pilot`, `check_nhp_pulse_search`, `assess_nhp_pulse_pilot --version 2`; plotting: `plot_nhp_pulse_pilot` in the original plotting environment. Use new output versions for reruns. Cached signatures prevent incompatible reuse. No raw inputs or previous DDM fits modified.

## Caveats
Two selected mice, responded-only conditional choices, same-session prefix generalization, no unseen-session forecast. State probabilities use prior outcomes; the model includes previous RT, not current RT. Masks preserve saved-record transitions but do not model outcome-dependent missingness. Block intervals do not refit training uncertainty. Late coefficients unavailable. States need not be literally discrete; longer history/continuous bias remain alternatives. Choice-only pulse fits cannot predict a joint RT-conditioned pulse profile.

## Open questions and next steps
- [ ] If continuing mechanistically, use shared-pulse state model as a nuisance benchmark and test a compact joint choice/RT accumulator with constrained baseline bias/sensitivity variation.
- [ ] Require both signed early pulse amplitudes, RT adequacy, held-out gain and matched recovery before a mechanism claim.
- [ ] Do not call inferred states attention or infer an accumulation-memory time constant from this pilot.
