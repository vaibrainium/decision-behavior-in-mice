# Plan: cheap check whether separate weights per pulse time would help
Status: done
Created: 2026-10-30 by Claude (Opus 5.5)
Related reports: reports/2026-10-30-pulse-weight-joint.md

## Goal
Author: "run a cheap simulation to see if separate weight per pulse time would help and if it does we can do model fitting
like that". Done = per mouse, NLL profile over a weight on one pulse-time bin at a time (others at 1, all other parameters
at the joint all-trial fit), sv and no-sv; decision rule below applied.

## Assumptions
- Profiling one bin at a time with other parameters fixed gives a lower bound on the train-NLL gain a fit could reach.
- Common random numbers (fixed eval seed) make NLL differences across w within one mouse paired.

## Steps
- [x] 1. Bins: UW onsets 0.05 / 0.23 / 0.42 s (3 bins); UCLA jittered onsets split at 0.15 s (2 bins); rig only sets the
      binning (pulse_timing_global.npz).
- [x] 2. Script scripts/ddm/pulse_time_weight_profile.py: w_b in {0, 0.5, 1, 1.5, 2, 3}, 10 mice, L0U0V1Z0G1 and L0U0V0Z0G1.
- [x] 3. Verify: profile at w = 1 for every bin equals the baseline NLL exactly (same stimulus).
- [x] 4. Decision rule: separate weights worth fitting if, in several mice, the best w differs across bins with gains
      > 10 NLL (MC noise ~10) relative to w = 1 in the same bin, in a consistent direction across mice.
- [x] 5. Report; STATUS.

## Out of scope
Fitting (Hyak) until step 4 says yes; simulating window effects.

## Log
- 2026-10-30: step 3 by construction (w = 1 uses the identical stimulus; baseline row per mouse x model). Done in ~45 min
  locally. Rule not met: gains > 10 in 2/50 profiles (PSUIM6, PSUIM7, early bin). -> reports/2026-10-30-pulse-time-weight-profile.md
