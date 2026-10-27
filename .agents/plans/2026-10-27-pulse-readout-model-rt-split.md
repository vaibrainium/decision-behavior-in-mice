# Plan: RT-split pulse checks on the primary model's simulated trials
Status: done (report: reports/2026-10-27-pulse-readout-model-rt-split.md)
Created: 2026-10-27 by Claude Opus 5.5
Related reports: reports/2026-10-27-pulse-readout-bias-checks.md, reports/2026-10-27-pulse-psychometric-variants.md

## Goal
Show where in RT the primary model (L0U0V1Z0G1, fits_resp_final control fits) falls short of the observed pulse effect,
using exactly the statistics of scripts/ddm/pulse_readout_checks.py. Author approved ("yes", 2026-10-27). Exploratory.

## Design (fixed before computing)
- Same trials as the data checks (responded, symmetric cells). Simulate each with primacy.predict_mouse(keep_sim=True),
  200 reps, seed 0, CPU; keep simulated responses only (conditional on response, as the fit).
- Each simulated rep = one copy of the trial; pooled per mouse. RT bins: the OBSERVED control quintile edges per
  mouse x |coherence| (same absolute RTs as the data). Secondary: model's own control quintiles.
- Statistics 1-3 of the data checks, mean ± SEM over mice; plotted with the data.
- Primary model only (other variants differ from it by < 1.3 pp in the overall pulse effect).

## Steps
- [x] 1. Refactor pulse_readout_checks: bins from given edges (data output unchanged; verify csv identical).
- [x] 2. scripts/ddm/pulse_readout_model.py; simulation cache processed/ddm/pulse_readout_model_resp/.
- [x] 3. Run; figure + csv; report + STATUS; commit as its own packet.

## Log
- 2026-10-27: refactor verified (data by_bin and rt_given_choice csv byte-identical). Simulation running locally (CPU, background).
- 2026-10-27: done. Added per-bin data - model paired t (Holm over 5 bins) after the first run (not in the design; labelled in the report).
