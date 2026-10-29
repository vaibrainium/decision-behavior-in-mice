# Report: UCLA pulse motion energy without the replay freeze; DDM accumulation check
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: (this commit)
Plan: plans/2026-10-29-ucla-pulse-me-nofreeze.md

## Question
Is the UCLA pulse understated in the DDM inputs by the replay's one-frame freeze, and by how much? Does the model
accumulate the current inputs as intended on both rigs?

## Summary
Removing the freeze raises the UCLA pulse template by 1.13x (0-333 ms sum) to 1.15x (peak). The UW/UCLA pulse
ratio falls from 1.65 to 1.45, close to the 1.33 expected from pulse length alone (4 vs 3 frames). The DDM kernel is
implemented as intended, and control inputs are matched across rigs. In the fitted model, the pulse moves the
decision variable by about 2-4% of the bound separation, which is why predicted pulse effects are tiny. A 1.13x input
correction cannot close the 4-10x gap to the observed effect.

## Findings (VERIFIED)
- New inputs: /mnt/data/processed/ddm/ddm_inputs_global_ucla_nofreeze.npz (+ _summary.json); 6,030 responded UCLA
  pulse trials replayed with ucla_nofreeze; all other rows identical to v1 (asserted); v1 untouched.
  Script scripts/ddm/ucla_pulse_me_nofreeze.py; 1,092 s on 30 workers.
- Check: the existing convention, replayed by the same code, reproduces v1 S+N (40 trials, max error 4.8e-7 fraction).
- Pulse template (ME per % coherence change; sums over frames):
  | | peak | sum 0-333 ms | sum 0-1 s |
  |---|---|---|---|
  | UCLA v1 (replay) | 0.272 | 2.67 | 2.69 |
  | UCLA no-freeze | 0.312 | 3.02 | 3.06 |
  | UW v1 | 0.420 | 4.28 | 4.43 |
- The stimulus audit's per-convention means (stimulus/per_trial_replay_metrics.csv, 76 UCLA trials, signed mean ME
  0-333 ms): replay 13.9, no-freeze 16.6, display loop R150 16.0, R190 16.7, i.e. 1.15-1.20x. The audit report's
  "1.28 to 1.40" is a per-trial ratio summary, not these means. All alternatives agree on about 1.13-1.20x.
- DDM accumulation (scripts/ddm/ddm_accumulation_examples.py; figures/qc/ddm_accumulation_examples_2026-10-29.png;
  PSUIM6 and DBM6 control fits, v1 inputs): a trajectory version of the model equations reproduces every RT and choice
  of src/ddm/simulator._simulate_ddm_trials_numba with the same random numbers. Control inputs per coherence and their
  integrals coincide across rigs (100% reaches about 183 % coh x s at 2 s on both). Accumulated pulse input at 0%
  coherence: UCLA 4.5, UW 7.4 % coh x s. In decision units (drift_gain x pulse): PSUIM6 0.10, DBM6 0.26, against bound
  separations 5.30 and 6.78 and a diffusion SD of 1 at 1 s.

## What didn't work
Nothing failed. Display-loop conventions were not recomputed (they change every UCLA frame, needing recalibration).

## How to reproduce
`.venv/bin/python -B -m scripts.ddm.ucla_pulse_me_nofreeze --workers 30` (refuses to overwrite the output);
`.venv/bin/python -m scripts.ddm.ddm_accumulation_examples`.

## Caveats
Which convention matches the UCLA acquisition is still unknown; the correction is bounded at about 1.13-1.20x by all
alternatives. Only responded UCLA pulse rows were replaced; no-response rows keep v1 values (never analysed, D003).

## Open questions and next steps
- [ ] Refit the 4 UCLA mice on all trials with the new inputs (Hyak; deferred by the author, "for now just work on
      motion energy"). Expected effect small: the input changes by about 13%.
- [ ] The STATUS known issue (UCLA all-trial vs control-fit shift) is unlikely to be explained by this correction alone.
