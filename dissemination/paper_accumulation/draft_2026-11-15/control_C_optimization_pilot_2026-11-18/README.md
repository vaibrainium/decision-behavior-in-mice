# Control model C: sensitivity and bounded optimization pilot

Status: completed exploratory pilot, 18 November2026. Existing manuscript fits/artwork retained. Pulse trials not analyzed. No CV expansion: selected local refits did not show a consistent independently confirmed joint-score improvement.

[Summary figure](summary_v2/optimization_pilot.pdf) · [Confirmation table](summary_v2/confirmation_summary.csv) · [All-mouse trade-offs](summary_v2/sensitivity_tradeoffs.csv)

## What was run

- All10 mice:27 parameter settings each (gain×sv×fast-guess probability), common draws at seed42 with15 repetitions/input; other parameters fixed. Original bounds and joint response-conditioned QMLE objective retained.
- DBM13, DBM12 and PSUIM10:3 named local restart runs each, at most200 function evaluations/run, all9 existing free parameters allowed. These span little/moderate/strong slope deficit. Some starts coincide when the best grid solution is the archived one. They are not9 independent global optimizations.
- Candidate selection:2 fresh seeds10101/20202,30 repetitions/input. Baseline is the immutable original archived fit.
- Fixed selected candidate confirmation:seed30303 at60 repetitions, then seeds123456/234567/345678 at100 repetitions. Confirmation draws never change candidate selection.

Original full-control fits used50 training repetitions; this bounded pilot used15 for optimization to bound work, followed by higher-repetition independent evaluation. No objective weighting or parameter bounds changed. Local runs capped at200 evaluations do not establish global convergence.

## Findings

The grid setting closest to each mouse’s psychometric proportions worsens joint score in8/10 mice, predominantly through RT. Original parameters remain joint-best on the coarse grid for6/10 mice. At100-repetition confirmation, mean new-minus-archived joint NLL is−0.0969 for DBM12 (seed-dependent),+1.5370 for DBM13,+1.5648 for PSUIM10. These are numerical checks on the same observed controls, not unseen-trial validation or biological replication.

PSUIM10’s middle-coherence deficit improves by2.91 percentage points, but the mean joint/RT score worsens. DBM12’s middle-coherence deficit increases by0.67 points; its mean joint change is negligible and changes sign across seeds. The pilot has not found a reproducible way to improve both the shallow psychometric slope and joint fit within current C. It does not prove the model or archived parameters cannot improve with more extensive optimization.

## Important correction

DO NOT USE original */control/independent_evaluation.json: a baseline-label collision replaced archived parameters with the restart named original. This affected comparisons only, not maps/optimizers. Corrected validated results are in validation_v2/ and confirmation_100reps/. Original executed source preserved in executed_pilot_source_v1.py. See INVALID_OLD_EVALUATION.md. Current code prevents that collision and comparisons assert baseline identity against original fit pickles.

## Files and reproduction

- */control/sensitivity.json: parameters and diagnostic scores; metadata include original fit/input hashes.
- */control/*_restart.json: all evaluated parameter vectors, evaluation counts, termination status and best fixed-draw score.
- validation_v2/: correct immutable-baseline candidate selection and initial confirmation.
- confirmation_100reps/: final fixed-candidate confirmation, original/new scores and differences.
- summary_v2/: inspected plots/tables; summary/ is an earlier render preserved before fixing a clipped label.
- objective_verification.json: equivalence of diagnostic scorer and original guarded training objective.
- verification.json and source_hashes.json: other checks and current source hashes.

Fresh recomputation from /src (existing .venv/CUDA):
```bash
.venv/bin/python -m scripts.paper.control_c_optimization_pilot --output <fresh-pilot-directory> --stage map
.venv/bin/python -m scripts.paper.control_c_optimization_pilot --output <same-pilot-directory> --stage pilot
.venv/bin/python -m scripts.paper.control_c_pilot_validation --pilot <same-pilot-directory>
.venv/bin/python -m scripts.paper.control_c_pilot_confirm --pilot <same-pilot-directory>
.venv/bin/python -m scripts.paper.summarize_control_c_optimization --pilot <same-pilot-directory> --output <fresh-summary-directory>
```

Current source corrects the name collision; the preserved source hashes identify the original executed fitting code. Existing cached metadata intentionally refuse mismatched source hashes; use fresh directories with current code. Raw data and original fits remain untouched. Report: .agents/reports/2026-11-18-control-C-optimization-pilot.md from repo root.
