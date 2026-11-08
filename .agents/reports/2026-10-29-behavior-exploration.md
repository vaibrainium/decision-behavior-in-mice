# Report: behavioural data exploration before new modelling
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: 57a47c0 (script uncommitted at writing)
Plan: plans/2026-10-29-behavior-exploration.md

## Question
Author: "before I start modeling work, I want to understand my data as much as I can." Where do the analysed trials
come from, how do the mice behave (engagement, psychometry, RT, history, sessions), and what should change the
modelling?

## Summary
The analysed data are 50 of 298 sessions (17%) from 10 of 14 mice; every session had pulses, so 77% of responded pulse
trials sit in excluded sessions. Exclusion uses control-trial behaviour only, so it is valid, but it is strict. Five
findings matter for modelling: (1) choices after the 5 s deadline (14% of trials, excluded) are as accurate as on-time
choices, so they are not disengaged guesses; (2) RTs are floored at 0.3 s with a pile-up there and low accuracy below
0.5 s (a fast-guess population); (3) choice history moves choices about as much as the pulse (repeat-the-last-choice
after errors in 8/10 mice); (4) no-response rises through the session (9/10 mice); (5) the pulse effect is stable across
sessions within a mouse (no heterogeneity, no trend) and the mice that ignore it in included sessions also ignore it in
excluded sessions.

## Findings
Source: `python -m scripts.behavior.explore_behavior --date 2026-10-29` (about 15 s). Tables
`dissemination/paper_accumulation/tables/behavior_exploration_2026-10-29_*.csv`; figures
`dissemination/paper_accumulation/figures/qc/behavior_exploration_2026-10-29_*.png`. Mice are the unit; Wilcoxon on
per-mouse values, Holm within each family listed in `_tests.csv`.

Provenance (`_sessions`, `_provenance`; VERIFIED, the re-applied criteria reproduce valid_data exactly)
- Raw: 134,537 trials, 14 mice, 298 sessions; all sessions contain scheduled pulses. After dropping correction trials
  and RT outside [0.15, 5] s: 105,119. Kept: 50 sessions, 25,508 trials, 10 mice. notebooks/0.1 prints "26 sessions";
  that counts distinct session_id strings, which repeat across mice; the real count is 50.
- Sessions failing (first criterion): too few trials (< 300 responded) 125, guess rate 56, lapse 41, bias 26.
  Median accuracy at 100%: kept 0.87, excluded 0.72.
- DBM8, DBM11, DBM16, PSUIM9 have no passing session. Kept sessions per mouse: 1 (DBM13, DBM14, PSUIM10) to 15 (PSUIM6).
  Kept sessions are spread through each mouse's history (median position 0.45 vs 0.55 for excluded).
- Pulse trials (responded, pulse seen before the response): 11,169 kept of 49,440 (23%; pulse_responded columns).

Task parameters (`_task_parameters`; VERIFIED)
- Same coherence set in all mice; pulses always to 100%. UW: pulse 67 ms at fixed 50/233/417 ms; UCLA: 51 ms at
  10-111 / 192-302 ms, no late pulse. Fixation 0.55 (UW) vs 1.0 s (UCLA); median ITI 0.5 vs 0.25 s. Reward size does
  not differ by side (|left - right| <= 0.012).

Late choices (`_late_choice_accuracy`, `_provenance`; VERIFIED)
- In kept sessions 13.7% of non-correction trials end in a choice after 5 s (median 6.9-8.9 s per mouse). Their
  accuracy matches on-time choices: mouse means 0.51 / 0.60 / 0.66 / 0.70 / 0.83 at 0 / 9 / 18 / 36 / 100% vs
  0.52 / 0.56 / 0.61 / 0.70 / 0.83 on time. The stimulus stays on (25-60 s), so these are stimulus-driven choices.
- SUSPECTED: they are mice that paused and re-engaged, not slow diffusion (the earlier report found their rate rises
  at session end and comes in runs). Either way, calling them "no response" understates what they are. The
  responded-only rule (D003) is unchanged; this is a flag.

RT (`_rt_summary`, `_chronometric`, control figure; VERIFIED)
- RT has a hard floor at 0.300 s in both rigs (aggregate minimum), so the 0.15 s criterion never acts. SUSPECTED: the
  recorded RT includes the 0.3 s minimum viewing time mentioned in notebooks/0.1; confirm with the task code.
- Pile-up at the floor in DBM12, PSUIM7, DBM5, DBM6 (RT < 0.5 s: 32 / 16 / 20 / 17% of control trials; PSUIM5/6/10
  3-7%). Accuracy at 100% for RT < 0.5 s is 0.33-0.71 vs 0.75-0.94 otherwise: a fast-guess population.
- Errors faster than correct at high coherence in most mice (also reports/2026-10-29-control-descriptives.md).
- Psychometric curves: DBM12, DBM13, DBM15 shallow and non-monotonic in the middle; PSUIM5/6/10 steep.

Engagement within session (`_within_session`; VERIFIED)
- No-response rate rises with position in session: 9/10 mice, mean rho 0.59, Holm 0.020. Accuracy, side bias and RT
  show no consistent trend (Holm >= 0.34).

Across sessions (`_per_session`, `_pulse_heterogeneity`; VERIFIED)
- Within included sessions (6 mice with >= 3): no trend in pulse effect, accuracy, RT or no-response (Holm >= 0.47).
- Pulse effect heterogeneity across included sessions (Cochran Q): p 0.07-0.87 per mouse; none < 0.05.
- Exploratory, all sessions: PSUIM6 and PSUIM7 positive in nearly every session including excluded ones; DBM mice near
  zero throughout (figure). No trend with session number (7/14 mice positive rho, p 0.33). So the session filter does
  not explain why some mice ignore the pulse.

History (`_history`; logit per mouse with coherence and pulse direction; VERIFIED)
- After an unrewarded choice, mice repeat it: lose weight positive in 8/10, mean 0.26, Holm 0.039. After a rewarded
  choice the weight varies in sign (7/10 positive, mean 0.21, Holm 0.32; negative in DBM6, DBM12, DBM14). PSUIM5/6/7
  have win and lose weights 0.3-0.8, as large as or larger than their pulse weight (0.26-0.41).
- Post-error slowing: median RT after an error minus after a reward, 9/10 positive, mean 0.21 s, Holm 0.082.
- prev_none weights are unusable (0-98 such trials per mouse).

## What didn't work
- First history fit failed (singular) in mice without choice-less previous trials; terms with no variance are now
  dropped per mouse.

## How to reproduce
`cd /src && .venv/bin/python -m scripts.behavior.explore_behavior --date 2026-10-29`. Inputs:
`/mnt/data/processed/aggregate_data.csv`, `valid_data.csv`; criteria from config/main.yaml.

## Caveats
- History regressors use the immediately preceding trial, including late and correction trials.
- Targets repeat less often than chance: P(target repeats) 0.40-0.48 per mouse (non-correction trials, all sessions;
  inline check, this session). Current coherence is in the model, so this matters mainly at 0%; the mice repeat their
  choices although the schedule favours switching. Source of the anti-repeat (task code) not checked.
- Session-level tests have little power in mice with 1-3 kept sessions.
- Excluded-session results are descriptive; the inclusion fit uses pulse_type == 0, which is RT-dependent.
- Numbers for the pulse effect are logits from per-mouse fits; not comparable to the pp effects in earlier reports.

## Open questions and next steps
- [ ] Author: model fast guesses explicitly (the common model has p_guess) and decide whether the 0.3 s floor is
      RT truncation or an offset (check the task code).
- [ ] Author: add choice history (start-point bias by previous choice and outcome) before reading pulse effects off a
      model; the history weights are as large as the pulse.
- [ ] Find why targets repeat less than chance (task randomization) and add P(repeat) to the script.
- [ ] Decide whether late choices (> 5 s) can enter any analysis (e.g. as a separate engagement state); D003 stands.
- [ ] Optional: relax inclusion as a labelled sensitivity analysis (123 excluded sessions have >= 300 trials).
