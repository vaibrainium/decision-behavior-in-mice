# Plan: Test the urgency-gating (UGM) corner of the leak + urgency model
Status: done (report reports/2026-11-11-ugm-corner.md)
Created: 2026-11-10 by Claude (Opus 5.5)
Related reports: reports/2026-10-29-pulse-leak-vs-urgency.md, reports/2026-10-22-leak-urgency-diagnosis.md,
reports/2026-11-09-mapping-accumulator-exploratory.md; literature: dissemination/reports/pulse-leak-vs-urgency-literature-2026-10-29.md

## Goal
Find out whether the parameter region of L1U1 that corresponds to Cisek et al. 2009's urgency-gating model
(strong filter, L about 4-10 /s, i.e. tau 100-250 ms, together with strong urgency) can match the control trials and
the pulse profile in the three dense mice. "Done" means a table of control-NLL cost vs base and pulse-profile
misfit for each (L, u) pair, plus a report saying whether the UGM corner is ruled out, viable, or unresolved.

## Context
- The simulator already has the UGM structure: a leaky integrator (= low-pass filter) of gain*ME + noise, with the
  displacement multiplied by (1 + u t) and compared with fixed bounds (src/ddm/simulator.py:47-70). UGM is the region
  L ~ 4-10 /s, u large (u = m/b; pure Cisek 2009 urgency with no intercept is u -> infinity).
- Fitted L1U1 values never got there: leak 0.07-2.7 /s, urgency -0.08 to +0.14 /s (all-trial fits; fit bounds
  L 0-5, u -0.15-2 in scripts/ddm/fit_mouse_ddm.py:78-79).
- scripts/ddm/pulse_leak_urgency_signatures.py imposed leak (1, 3, 10) OR urgency (0.3, 1, 3), never both.
  Leak 10 /s cost +1,747 / +553 / +304 control NLL (PSUIM6 / PSUIM7 / DBM6; DBM6 missed the non-response cap);
  urgency >= 1 /s pushed a to the limit. In the UGM, urgency is what drives a strongly filtered signal to the bound,
  so single-factor tests do not test the UGM.

## Assumptions
- Re-matching only a and drift gain (other parameters at the L0U0V1Z0G1 control fit) is enough to give each pair a
  fair chance. It may not be: sv, NDT and guesses were fitted without leak or urgency. Upper bound on cost, as before.
- u = 20 /s approximates zero-intercept urgency (gain is >= 90% proportional to t after 0.5 s).
- The a < 10 limit (A_LIMIT, validate_params) is a validation range, not a numerical requirement. To check in step 1.
- Mice: PSUIM6, PSUIM7, DBM6 (as in the earlier grid). Responded-only trials (no response by 5 s excluded).
  Rig is not a factor in any summary.

## Steps
(Scope changed 2026-11-10 by the author: fit the UGM as a model variant on Hyak instead of the 3-mouse imposed grid; see Log.)
- [x] 1. Simulator: optional fixed parameter urgency_ref (s). Urgency gain (1 + u t) / (1 + u urgency_ref), implemented
      exactly by scaling a by (1 + u urgency_ref) in DriftDiffusionSimulator.simulate_trials (all backends), so `a`
      keeps its 0-10 range and large u approaches zero-intercept urgency. Check: tests/test_normalized_urgency.py
      (independent NumPy loop vs numba and torch backends, 3 settings: choices 100% and RTs within one step agree;
      no urgency_ref -> output unchanged).
- [x] 2. fit_mouse_ddm.py --ugm (L1U1 variants only): leak 2-20 /s (tau 50-500 ms), urgency 0-50 /s normalized at
      1 s, drift_gain up to 50, urgency_ref = 1 stored in parameters; result["ugm"] = True. Smoke fit (PSUIM10,
      L1U1V1Z0G1, pcv2, n_reps 2, 2 iterations, scratch output) runs and saves.
- [x] 3. Task table scripts/slurm/tasks_2026-11-10_ugm.csv (make_task_table --ugm; batches UGM_{joint,pulse}_
      {linear,power}; L1U1V1Z0G1 and L1U1V0Z0G1; joint splits cv0-cv4 + all, pulse splits pcv0-pcv4 + pulse; 480 tasks;
      out ddm/fits_{joint,pulse}_{linear,power}_ugm). Time limits from the same mouse's joint L1U1V1Z0G1 fit with
      the same input (>4 h -> 16 h: 96 tasks, power). Indices verified against build_grid (0 mismatches).
- [x] 3b. Norm input appended (UGM_{joint,pulse}_norm, rows 481-720; first 480 rows byte-identical; 0 index
      mismatches; limits from fits_joint_norm_integrators L1U1V1Z0G1: 168 of 240 at 16 h). Smoke fit norm + ugm OK.
- [x] 4. Author: pull and submit on Hyak (720 tasks):
      python3 scripts/slurm/autosubmit.py --tasks scripts/slurm/tasks_2026-11-10_ugm.csv --state slurm-logs/autosubmit_state_ugm.json --watch 10
      (--dry_run first). Do not change the table once pulled.
- [x] 5. Sync; check bound-hitting (leak at 2 or 20, urgency at 0 or 50, drift_gain at 50, a at 9.5) and convergence.
- [x] 6. Compare with the standard L1U1 (same splits, same input): held-out NLL per mouse (joint CV and pulse CV),
      fitted leak and urgency, pulse profile and late-window effect (simulate fits; add to fit browser).
      Viability criteria for the UGM (author to confirm before looking): held-out NLL within 10 units of the best
      integrator per mouse, and pulse profile without a late reversal outside the data CI.
- [x] 7. Report; update STATUS.

## Out of scope
- A full refit of all mice (only if step 7 says the corner is viable).
- A policy (speed-accuracy) manipulation test; the design has none.
- Control-only splits and nominal input (can be added as a new table).
- Noise injected after the filter (an alternative UGM variant with different variance growth).
- Rig-split interpretation.

## Log
- 2026-11-10: plan created after comparing Cisek et al. 2009 with L0U1/L1U1 (conversation). Awaiting author approval of
  the step 3 criteria and step 4 runtime.
- 2026-11-10: author: "add this as a variant for our above models and I will run it on hyak (all variants)". Replaced
  the imposed 3-mouse grid with full fits of a UGM variant (steps 1-3 done). Interpreted "all variants" as leak +
  urgency with and without sv, linear and power input, joint and pulse-only splits (480 tasks); stated to the author.
  Assumption change: urgency_ref replaces the u = 20 approximation; a < 10 limit kept (normalization makes it unnecessary
  to lift).
- 2026-11-10: author added the normalized input to the same table. Appended as new batches (not regenerated in
  place) so any already-pulled batch:index stays valid.
- 2026-11-10: author submitted (loop --watch 10, state slurm-logs/autosubmit_state_ugm.json; 2026-11-09 20:10 Hyak time):
  first pass 333 tasks: UGM_joint_linear all 120 (jobs 43092429-43092433), UGM_joint_norm all 120 (43092434-43092436),
  UGM_joint_power 93 (43092437-43092441); 27 joint power and all pulse-only batches pending for free slots.
  autosubmit grouped the table limits into 2/3/4/6/8/16 h arrays.
- 2026-11-10: Hyak maintenance reservation November10_Maintenance 2026-11-10 09:00 to 2026-11-11 09:00 blocked the
  long arrays (ReqNodeNotAvail). Added autosubmit --cap_pending HOURS (b7bcbb6; lowers PENDING tasks' limit in Slurm and
  state together, cut not counted as an attempt; stub-tested). Author ran it with 11.0 h: 34 UGM tasks capped (joint
  power 16 h array 43092441; dry run listed 35, one started running in between); PO/PLU had none above 11 h.
  Capped fits that do not converge time out, are resubmitted at 22 h and resume from their checkpoints after maintenance.
- 2026-11-11: after the Hyak maintenance all tmux loops were gone (login node restart). Synced status: PO 480/480 and
  PLU 480/480 done; UGM 313/720 done (joint linear 120, joint power 91, joint norm 102). Author restarted the ugm loop;
  the remaining 389 tasks submitted (arrays 43112068-43112083). One start-up failure (UGM_joint_power:117, PSUIM5
  L1U1V0Z0G1 all; FAILED after 9 s: Lmod cache rename race in ~/.cache/lmod when many jobs start at once); the loop
  retries it; no other task hit it. If it repeats: rm -rf ~/.cache/lmod, or retry `module load` in fit_mouse_ddm.slurm.
- 2026-11-11: (Claude, pulse-only session) after the Hyak restart, synced UGM fits: 313/720 (joint linear 120/120, joint
  norm 102/120, joint power 91/120, all three pulse-only batches 0/120). Synced files all valid (12 resumed from a
  checkpoint). Missing 407: 47 joint, 360 pulse-only; 164 of them have 16 h table limits. To resume: restart the ugm
  autosubmit loop (state slurm-logs/autosubmit_state_ugm.json); fits resume from their .ckpt files on gscratch.
- 2026-11-11: author synced the remaining UGM fits. Step 5 (scratch script, not committed: checks every .pkl in
  ddm/fits_{joint,pulse}_{linear,power,norm}_ugm): 720/720 present (120 per folder, 10 mice, no duplicates); all
  ugm=True, urgency_ref 1, name = content, front end matches folder, finite NLL, success True, none at max_iterations
  (1000); 91 resumed from a checkpoint; fit time median 0.5-1.9 h, max 7.2 h. Bounds (1% of range): no fit near
  drift_gain 50 or a 9.5 (max a 8.88). The fits sit at the edge nearest the standard L1U1, away from the UGM corner:
  leak <= 2.18 /s (lower bound 2) in 388/720, urgency <= 0.5 /s (lower bound 0) in 571/720, both in 303. In the UGM
  region (leak 4-10 /s and urgency >= 1 /s): 14/720, all pulse-only CV folds of PSUIM10 (9), DBM13 (4), DBM14 (1),
  none on a full-data split. Urgency >= 1 /s: PSUIM10 53/72 fits (the mouse with fewest trials), other mice 66/648.
  sv at its upper bound in 50 fits (with-sv variants). Reading (descriptive): given the freedom, the likelihood pulls
  these fits back toward slow leak and weak urgency. Step 6 decides whether the corner is ruled out (NLL cost).
  Note: the pulse-only norm UGM fits have no standard pulse-only norm counterpart (pulse-only fits were linear and power).
- 2026-11-11: author confirmed the step 6 criteria as written, before any NLL or pulse comparison was looked at:
  UGM viable for a mouse if held-out NLL is within 10 units of the best integrator for that mouse (same input, same
  CV splits), and the family's pulse profile has no late reversal outside the data CI.
- 2026-11-11: steps 6-7 done. primacy.make_model takes ugm; UGM families registered (pulse_joint_signatures.UGM_FAMILIES,
  UGM_PULSE_FAMILIES); rescoring reproduces stored test NLL (<= 0.08). compare_ugm.py (NLL vs best standard integrator,
  same trials checked); signatures _ugm_part0-2 + bootstrap _ugm; fit browser v5 data (71 families, earlier content
  identical) published as artifact version 6. Deviation: no standard pulse-only norm fits, so pulse-only norm UGM is
  described, not compared. Free fits avoid the corner, so the criteria tested the region edge (see report).
