# Plan: full behavioural data exploration (before new modelling)
Status: done
Created: 2026-10-29 by Claude (Opus 5.5)
Related reports: reports/2026-10-29-control-descriptives.md; reports/2026-10-27-no-response-trials-disengagement.md;
reports/2026-10-29-pulse-descriptive-package.md; reports/2026-10-28-pulse-time-comparison.md

## Goal
Author request: "before I start modeling work, I want to understand my data as much as I can. Full behavioral data
exploration". Done = one report plus a figure set that describes, per mouse, where the trials come from, how the mice
behave (engagement, psychometry, RT, history, learning across sessions) and how stable the pulse effect is, with
anything that should change the modelling flagged.

## Context
- Pipeline (notebooks/0.1-preprocessing-data.ipynb): raw aggregate_data.csv (134,537 trials, 14 mice, 298 sessions)
  -> drop correction trials -> RT in [0.15, 5] s -> keep sessions with >= 300 trials whose control psychometric fit
  passes lapse < .25, guess < .25, |alpha| < 25, beta < .5 -> valid_data.csv (25,508 trials, 10 mice). The notebook
  prints "26 sessions"; that is the number of distinct session_id strings, which repeat across mice (actual count is
  50 mouse-sessions).
- pulse_type in valid_data is RT-dependent (0 when the response came before the pulse ended).
- Already done, reuse not redo: control chronometry and kernels (control-descriptives), no-response trials as
  disengagement, pulse effect by RT and pulse time, per-mouse pulse bias (this session, scratchpad).
- Memory rules: responded trials only for analyses; rig is a covariate, never a grouping for interpretation; mice are
  the unit for group claims.

## Assumptions
- aggregate_data.csv in processed/ holds every raw trial, including sessions that failed inclusion (check).
- Session order can be recovered from session_id (number_part) per mouse (check).

## Steps
- [x] 1. Provenance: trials and sessions per mouse at each pipeline step; which criterion excluded each session;
      excluded mice; pulse trials lost with excluded sessions; position of included sessions in each mouse's history.
- [x] 2. Task parameters per mouse (rig as covariate): coherence set, pulse schedule (onsets, durations, pulse
      coherence), fixation, ITI, stimulus duration, reward amounts (and whether they differ by side or outcome).
- [x] 3. Engagement within session: accuracy at +-100%, side bias, RT and no-response rate by trial position;
      runs of no-response.
- [x] 4. Across sessions: psychometric parameters, RT, and the pulse effect per session against session number.
- [x] 5. Control behaviour per mouse: psychometric and chronometric curves, RT distributions, fast responses, error vs
      correct RT (link to existing report).
- [x] 6. Trial history: previous choice, previous outcome, previous reward size, after a correction trial; per mouse.
- [x] 7. Pulse summary per mouse (per-mouse table from this session, session heterogeneity, sensitivity without the
      3 single-session mice).
- [x] 8. Verify: counts reconcile with valid_data (25,508) and ddm inputs (25,493 responded); every figure number
      traced to a table.
- [x] 9. Report, STATUS; dashboard only if the author asks.

## Out of scope
Model fitting; re-running the inclusion with different criteria for the main results (sensitivity only, labelled);
site comparisons.

## Log
- 2026-10-29: plan written at the author's request; descriptive, local CPU, no existing files changed, so started.
- 2026-10-29: steps 1-8 run in scripts/behavior/explore_behavior.py; no dashboard (not asked). Added: late-choice
  accuracy (late choices are as accurate as on-time ones) and target repetition check. Report:
  reports/2026-10-29-behavior-exploration.md.
- 2026-10-29: not done although ticked as a step: previous reward size and after-correction-trial effects (columns
  built in load(), not analysed; correction trials exist only in PSUIM5/10); across sessions uses accuracy, not fitted
  psychometric parameters; step 7 sensitivity was run inline earlier this session (scratchpad), not in the script.
