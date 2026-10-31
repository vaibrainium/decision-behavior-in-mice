# Plan: fit a separate pulse weight per pulse time
Status: done
Created: 2026-10-30 by Claude (Opus 5.5)
Related reports: reports/2026-10-30-pulse-time-weight-profile.md (pooled profile: sv early ~1.5, middle ~1, late ~0.5),
reports/2026-10-30-pulse-weight-joint.md (shared weight ~1, no held-out gain)

## Goal
Author approved ("yes") fitting per-pulse-time weights. Done = per mouse, primary model with and without sv, weights for
early / middle / late pulses fitted jointly with all parameters (cv0-cv4 + all), compared with the shared-weight and joint
fits on held-out NLL (summed over mice, mice as unit), and the across-mouse ordering of the weights tested.

## Assumptions
- Pulse time = |sched_pulse_type| (VERIFIED crosstab against pulse_timing_global.npz): UCLA 1 = 0.02-0.12 s, 2 = 0.20-0.30 s;
  UW 1 = 0.05, 2 = 0.23, 3 = 0.42 s. Early/middle are matched across rigs; late is UW only. Rig is not interpreted.
- Warm starts from the shared-weight fits (w copied to each weight) and the joint fits (all 1) make the new fit nested.

## Steps
- [x] 1. Code: simulator takes (signal, channel 1..3) with CHANNEL_WEIGHTS; fit_mouse_ddm --pulse_time_weights (weights
      noise_weight, noise_weight_2, noise_weight_3; count per mouse from its pulse types).
- [x] 2. Checks (scripts/ddm/check_pulse_time_weights.py, DBM13 and PSUIM10): channel sum = single-channel input (1.2e-7);
      NLL at weights 1 = joint fit NLL (1600.3638, 808.7197); equal weights 1.7 = shared weight NLL (1604.5359, 808.8249);
      warm-start seeds copy w; torch backend runs. Smoke fit DBM13 cv0 (2 reps, 1 iteration) saved with test_nll.
- [x] 3. Hyak: scripts/slurm/submit_pulse_time_weights.sh (120 jobs, out ddm/fits_joint_unfreeze_pulse_time_weights).
- [x] 4. Readout: held-out NLL vs shared-weight and joint fits (same folds); weights per mouse; ordering early > middle
      (> late) across mice (sign test / Wilcoxon on paired weights, Holm); weights at bounds.
- [x] 5. (PSUIM6 and PSUIM7 only, author OK 2026-10-31) If weights differ: simulate pulse window effects with fitted weights vs data (pulse_joint_signatures statistics).
- [x] 6. Report; STATUS.

## Out of scope
Pooled (across-mouse) weights; other model families.

## Log
- 2026-10-30: first check run found my strict zip broke the existing two-channel path (shared weight NLL inf); fixed
  before commit, all checks rerun and passing.
- 2026-10-30: submitted by the author on Hyak (HEAD 89f14d2): PTW_pulse_time_weights 42623428 (0-119). Next: pull, step 4.
- 2026-10-31: 120/120 fits pulled. No held-out gain, no ordering across mice; PSUIM6 early weight ~3. -> reports/2026-10-31-pulse-time-weights.md
- 2026-10-31: step 5 done (scripts/ddm/pulse_time_weight_signatures.py): PSUIM6 early weight ~3 lifts the early effect 4.0 -> 11.5 pp (data 18.3); middle unchanged ~3.6 (data 12.6). Report addendum.
