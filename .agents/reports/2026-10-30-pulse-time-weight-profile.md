# Report: would separate pulse weights per pulse time help? (cheap likelihood check)
Date: 2026-10-30   Agent: Claude (Opus 5.5)   Commit: see git log for this file
Plan: plans/2026-10-30-pulse-time-weight-profile.md

## Question
Before fitting per-pulse-time weights on Hyak: does the likelihood prefer a weight different from 1 for any pulse-time bin?

## Summary
Mostly no. In 8/10 mice the likelihood barely sees the pulse at all: removing it entirely (w = 0) changes train NLL by
<= 12 (<= 9 in 7 of them), so per-time weights there cannot be identified. Only the two densest mice (PSUIM6, PSUIM7,
~2300-2700 pulse trials) show structure: the early bin tolerates or prefers w >= 1.5, the later bin prefers w <= 1 and is
penalised strongly above 1.5 (PSUIM7: +42 at w = 2, +98 at w = 3, sv model). Gains beyond 10 NLL: 2 of 50 bin x model
profiles (sv PSUIM6 early -18.5 at w = 3; no-sv PSUIM7 early -12.5 at w = 2). Fitting per-time weights in all mice is not
justified; the early > late hint in two mice is suggestive only. Moderate confidence.

## Findings
- Method: joint all-trial fit (fits_joint_unfreeze_integrators, L0U0V1Z0G1 and L0U0V0Z0G1), all other parameters fixed,
  pulse component of one pulse-time bin scaled by w in {0, 0.5, 1, 1.5, 2, 3}, train NLL with the fixed evaluation seed
  (common random numbers across w). Bins: UW onsets 0.05 / 0.23 / 0.42 s; UCLA jittered onsets 0.02-0.12 vs 0.20-0.30 s
  (split at 0.15 s). Source: scripts/ddm/pulse_time_weight_profile.py,
  dissemination/figures/qc/pulse_time_weight_profile_2026-10-30.csv (NLL minus the w = 1 baseline per mouse x model).
- Cost of removing the pulse in one bin (w = 0), worst bin per mouse, sv / no-sv: PSUIM7 38.8 / 25.9, PSUIM6 21.7 / 19.4,
  DBM6 12.1 / 4.8, all others <= 8.9. VERIFIED.
- PSUIM6 (sv): early bin -6.2 / -9.8 / -18.5 at w = 1.5 / 2 / 3 (still falling at 3); later bin best at 0.5 (-1.3),
  +18.7 at 3. No-sv: early -3.1 / +0.2 / -3.9; later -1.3 at 1.5, +17.8 at 3. VERIFIED.
- PSUIM7 (sv): early best 1.5 (-2.6), +49 at 3; later best 0 (-3.0), +13.6 / +42.2 / +98.1 at 1.5 / 2 / 3. No-sv: early
  -6.7 / -12.5 / +6.1 at 1.5 / 2 / 3; later -6.0 at 1.5, +30.9 at 3. VERIFIED.
- UW mice (3 bins): every profile within -6.1 to +11.4 of w = 1; no consistent ordering across bins. VERIFIED.
- Direction in PSUIM6 and PSUIM7: best early weight >= best later weight in both models (primacy-like). SUSPECTED: two mice,
  same rig, gains near the noise threshold; UCLA "early" and "later" are only ~0.2 s apart.

## What didn't work
- Nothing failed. The likelihood is insensitive to the pulse in small mice, which limits what any pulse-weight fit can show.

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_time_weight_profile MOUSE` per mouse (NUMBA_NUM_THREADS=3, 10 in parallel, ~45 min
for the largest mice on this CPU machine), then concatenate the per-mouse CSVs. Inputs ddm/ddm_inputs_global_ucla_nofreeze.npz,
ddm/pulse_timing_global.npz.

## Caveats
- Other parameters fixed: a refit could trade the weight against drift_gain or sv and gain more (or less).
- Train NLL, one bin at a time; no penalty for the extra parameters; MC noise ~10 per mouse.
- The likelihood (condition = coherence x pulse type, 9 RT bins) does not condition on pulse time or on RT relative to
  the pulse, which is where a pulse-time effect would show; it is a weak test of pulse weighting.

## Open questions and next steps
- [ ] Author decision: (a) stop; (b) fit two weights (early, later) only in PSUIM6 and PSUIM7 on Hyak (4 jobs per model,
      all + cv), to see if the early > late hint survives held-out; (c) change the likelihood so pulse trials are binned by
      pulse time (and RT relative to pulse) before any weight fitting.
