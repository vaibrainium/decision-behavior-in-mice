# Report: control C sensitivity and bounded optimization pilot
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; new work uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, authorized control-C pilot subsection

## Question
Can existing C parameters be improved to address shallow psychometric slope without sacrificing joint choice/RT fit?

## Summary
Completed270 all-mouse grid evaluations and9 local restart runs (1758 objective evaluations) on3 pilot mice. Independent higher-repetition checks did not identify a consistent joint-score improvement. PSUIM10 slope deficit improves with a joint/RT cost; DBM12 changes negligibly and inconsistently; DBM13 joint fit worsens. Keep existing manuscript fits. Conditional CV expansion not run because no selected candidate produced a useful consistent numerical gain; this is not evidence that global improvement is impossible.

## Findings
- VERIFIED: all10 mice/27 grid settings use common draws at seed42,15 repetitions/input. Same original bounds,9-free-parameter family, and guarded QMLE objective. Gain factors0.8/1/1.2, sv and guess factors0.75/1/1.25 clipped to original bounds. All270 pass response guard. Source */control/sensitivity.json and sensitivity_all_mice.csv.
- VERIFIED: setting with minimum psychometric-proportion RMSE worsens joint score in8/10 mice; original setting joint-best on coarse grid for6/10. Source summary_v2/sensitivity_tradeoffs.csv. Choice-fit improvement frequently costs RT, especially in larger-deficit mice. This is a fixed-draw training diagnostic, not a statistical population result.
- VERIFIED:9 named restarts,200 function-evaluation cap, same9 parameters/bounds, on DBM13/DBM12/PSUIM10. Total1758 evaluations.3 optimizer runs report convergence;6 reach cap. Some named starts coincide; no claim of9 distinct solutions. Original full fits used50 repetitions; pilot optimization15 for bounded exploration, then independent30/60/100 repetitions. Sources local_restart_summary.csv and per-run traces.
- VERIFIED: independent selection seeds10101/20202 (30 reps), chosen solely by mean joint score with original included. Winners: DBM13 refit_map_choice_best; DBM12 refit_map_choice_best; PSUIM10 refit_map_joint_best. Initial60-rep confirmation at30303 worsens joint score in all3.
- VERIFIED: fixed selected candidates checked at100 repetitions and new seeds123456/234567/345678. Mean new−original NLL: DBM12−0.096868 (range−0.781021 to+0.681044), DBM13+1.537016 (+0.611076 to+2.295897), PSUIM10+1.564826 (−0.136611 to+3.007158). Higher positive=worse. Source confirmation_100reps/new_minus_original.csv and summary_v2/confirmation_summary.csv. Seeds are numerical checks, not biological replicates; no p-values.
- VERIFIED: confirmation mean middle-coherence signed deficit change: DBM12+0.6661pp (worse), DBM13−0.0316pp, PSUIM10−2.9055pp (improved). PSUIM10 psychometric RMSE improves0.6111pp but RT NLL worsens1.6121 units on average. Source same confirmation outputs. No claim that every choice/RT statistic moves together.
- VERIFIED: independent objective-equivalence checks for all3 pilots agree with original guarded fitting function and saved profile baseline at seed42/15 reps. Bounds/evaluation-budget/trace-min checks pass; original fit hashes checked. Corrected immutable baselines exactly match actual fit parameters. Source objective_verification.json, verification.json. Scripts compile, final plot visually inspected after fixing clipped label in fresh summary_v2.

## What didn't work
A comparison dictionary used original for both archived baseline and a restart label, replacing the baseline. Detected before interpretation, original independent_evaluation.json files explicitly invalidated; original source frozen as executed_pilot_source_v1.py. Maps and optimizer results were unaffected. Corrected validator prefixes candidate names and asserts archived baseline equality; only validation_v2 and confirmation_100reps used for findings. Initial independent30-rep gains did not survive60/100-rep checks consistently. No CV fits launched, no existing artwork changed.

## How to reproduce
All outputs: dissemination/paper_accumulation/draft_2026-11-15/control_C_optimization_pilot_2026-11-18/. README lists exact fresh commands for scripts.paper.control_c_optimization_pilot (map/pilot), control_c_pilot_validation, control_c_pilot_confirm and summarize_control_c_optimization. Original input /mnt/data/processed/ddm/ddm_inputs_global.npz; C fit paths /mnt/data/processed/ddm/fits_resp_final/<mouse>_L0U0V1Z0G1_control.pkl. Original/input hashes in profile and validation metadata, executed/current code hashes retained. Never replace original fit files. Current source prevents name collision; caches reject changed source fingerprints, so fresh reruns use fresh output paths.

## Caveats
Small exploratory local pilot, no global optimization/identifiability claim. All confirmations use same observed control data, so no unseen-trial validation obtained.15 training repetitions differ from original50 and can overfit draws despite same QMLE formula. Finite confirmation seeds/no parameter uncertainty; cap-limited runs. Mice selected using full-control residuals. Coarse grid cannot establish best three-parameter combination or causal mechanism. This result supports a possible structural choice–RT tradeoff but does not prove one. It does not establish that a nonlinear mapping will help. No pulse analysis, installations, cluster submissions, raw-data changes, commits or pushes.

## Open questions and next steps
- [ ] Author review tradeoff and confirmation results; retain current fits for paper.
- [ ] If pursuing improved adequacy, separately scope a minimal nonlinear evidence-to-drift mapping or higher-precision broader optimization. Any changed fitting/model procedure must undergo matched control CV before score/parameter replacement.
- [ ] Continue main Figure3 artwork/recovery review independently; RT diagnostic remains supplementary draft.
