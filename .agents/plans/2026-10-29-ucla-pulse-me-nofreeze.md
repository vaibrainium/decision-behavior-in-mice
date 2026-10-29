# Plan: recompute UCLA pulse motion energy (no-freeze convention) and refit UCLA mice on all trials
Status: active
Created: 2026-10-29 by Claude (Opus 5.5)
Related reports: reports/2026-10-23-pulse-stimulus-20261023T191030Z_fa8de8b.md, STATUS known issue 2026-10-29
(all-trial vs control-fit parameters shift in UCLA mice only)

## Goal
Test whether the UCLA all-trial parameter shift (a x0.82, drift_gain x0.85, sv x0.76, ndt x1.9 vs control fits) comes
from understated UCLA pulse ME. Done = new inputs file with UCLA pulse trials replayed without the one-frame freeze,
and all-trial refits of the 4 UCLA mice compared with fits_resp_final.
Author approved ("okay let's recompute", 2026-10-29).

## Context
- The replay applies the UCLA burst update in a frame without a dot move ("freeze, 2 moving frames, freeze"); the rig
  probably moved dots in the same pass. ucla_nofreeze (scripts/pulse_followup/stimulus_audit.py) moves after the update.
- Only pulse frames change under no-freeze (controls identical), so the onset template and calibration stay as v1.
- Display-loop variants (ucla_pass_*) change every UCLA frame; out of scope (would need full recalibration).

## Steps
- [x] 1. Script scripts/ddm/ucla_pulse_me_nofreeze.py: replay responded UCLA pulse trials with no-freeze (local, 30
      workers); check the replay convention reproduces stored v1 S+N on a subset.
- [x] 2. Rebuild the UCLA pulse template from the new ME (same rule as build_ddm_inputs), signal and noise for those
      rows; write /mnt/data/processed/ddm/ddm_inputs_global_ucla_nofreeze.npz (v1 untouched). Report template and
      0-333 ms energy ratios against v1 computed on the same rows.
- [ ] 3. Hyak refit: PSUIM5/6/7/10 x L0U0V1Z0G1 x split all (and control as a no-change check), --responded_only,
      n_reps 50, warm start fits_resp_final, out ddm/fits_resp_ucla_nofreeze. Author transfers the inputs file and
      runs the jobs (commands in the log below).
- [ ] 4. Compare parameters (all vs control, old vs new inputs); report; STATUS.

## Out of scope
Display-loop conventions; UW; refitting other variants; pulse-gain or primacy reruns.

## Log
- 2026-10-29: plan written; started step 1.
- 2026-10-29: steps 1-2 done (1,092 s; template x1.13-1.15). Author: "for now just work on motion energy"; steps 3-4
  (Hyak refit) deferred, not started. Added a DDM accumulation check at the author's request. Report:
  reports/2026-10-29-ucla-pulse-me-nofreeze.md.
