# Report: Figure 3B model fits on control data
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; new work uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, step R

## Question
Author replaces score-decomposition B with psychometric and choice-conditioned mean RT data/model overlays like Figure 1.

## Summary
Built B with five model columns, psychometric row above and mean RT conditional on physical left/right choice below. Observations are points, full-control model predictions lines, and data SEM shaded. Fifty saved full-control fits simulated at fixed parameters; no optimization or new tests. Initial preview inspected and ready for author review. Both finalized A alternatives preserved.

## Findings
- VERIFIED: 14,014 observed controls match original valid_data.csv choices/RTs and control membership by agg_code. These match the control population modeled/scored in A. Figure 1 contains 14,015 controls: extra PSUIM7_14_1_344, choice left, signed coherence −100%, RT 0.3004732132s, has pulse_onset 0.253864s but pulse_duration NaN. The input builder's invalid-pulse filter excludes such rows: offset = onset frame + rounded duration, hence missing, and not(offset > onset). Sources: valid_data.csv, scripts/compute_motion_energy_full.py convert_to_frame_units, scripts/ddm/build_ddm_inputs.py lines85–93, figure1_population_difference.csv. All other observed psychometric mouse/coherence cells match Figure 1.
- VERIFIED: every saved full-control fit is successful, split control, response-conditioned, matching nominal/extrema flags and n_train. Exact fit files/hashes in fit_inventory.csv and manifest.json. Same full-control source mapping as BIC: C fits_resp_final; E fits_resp_fast_only_leak20-200_cap; ES fits_resp_fast_only_es_cap; DDMx fits_resp_nominal_ddm_g001; ESx fits_resp_nominal_es.
- VERIFIED: 20 repetitions/input at seed34567 for each saved fit; 280,280 simulated outcomes per candidate before response filtering. Cache contains aggregated psychometric counts and choice-specific RT counts/sums for every mouse/model; response counts exported in simulation_response_counts.csv. Each simulation conditions on response between0.3–5s after existing simulator mapping. No observed choice/RT used to generate outcomes; inputs are actual retained stimulus schedules.
- VERIFIED: model and observed RT means use identical mouse/coherence/choice cells, selected only by observed count >=10. Group cells contain7–10 mice. Response counts/sums pooled within mouse, then equal-mouse means; SEM is across observed mouse means, not Monte Carlo or fitted-parameter uncertainty. Model RTs are conditioned on simulated choice, data RTs on observed choice.
- VERIFIED: independent checks of per-mouse choice ratios, RT sum/count ratios, group means/SEM/n, eligibility populations and original raw-data RT cell counts/means passed; verification.json. Source compiles; PNG visually inspected. PNG/PDF/SVG exported. No smoothing/logistic fit applied to model curves; predictions connected at tested coherences.
- VISUAL OBSERVATION: psychometric curves are close across candidates; conditional RT curves show more visible candidate differences. This is descriptive, not a new adequacy or significance conclusion.

## What didn't work
Archived pulse-psychometric caches retain unconditional mean RT, not choice-specific RT, and lack all five matched sources; not used. Initial assumption of exact Figure1 population equality failed and the single-trial difference was traced/documented. Importing the input builder to call its frame converter failed because cv2 requires missing libGL.so.1; no packages installed, verified the relevant converter/filter source directly instead. A pandas fillna future warning did not affect validated outputs.

## How to reproduce
From /src, existing .venv/CUDA environment:
```bash
.venv/bin/python -m scripts.paper.figure3B_control_fits --output dissemination/paper_accumulation/draft_2026-11-15/figure3B_control_fits_FRESH --n-reps 20 --seed 34567
```
Completed directory: dissemination/paper_accumulation/draft_2026-11-15/figure3B_control_fits_2026-11-18/. Resume interrupted work with --resume and same args; fit/input hashes checked. Input: /mnt/data/processed/ddm/ddm_inputs_global.npz. Per-fit aggregated predictions in prediction_cache/. Model/input/script hashes in manifest.json, verification dependency/raw-data hashes in verification_source_hashes.json. Source/export tables and caption adjacent.

## Caveats
Descriptive IN-SAMPLE full-control fits, distinct from A's held-out scores; do not label curves held-out. C full-control parameters come from a different folder than its CV parameters. Finite simulation draws; no parameter uncertainty bands. Five-column draft at230mm provisional width; journal assembly/layout pending. Data shaded SEM repeats for comparison across columns. One missing-timing control means Fig1/B data differ in one cell; no raw data or prior results altered. No commits, pushes, installations or cluster jobs.

## Open questions and next steps
- [ ] Author assess B layout and psychometric/choice-conditioned RT overlay design.
- [ ] Refine B artwork, then review recovery C; cohort-recombination placement remains undecided.
