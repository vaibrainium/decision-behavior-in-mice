# Report: Are 100%-coherence errors triggered by incongruent pulses? Error hazard aligned to pulse onset
Date: 2026-11-19   Agent: Claude (Opus 5.5)   Commit: 57f7c72 (criteria pre-registered) + this report's commit
Plan: plans/2026-11-19-choice-misfit-followup.md, criteria B (written before the analysis was run)

## Question
At 100% coherence, do incongruent pulses produce errors clustered 150–400 ms after pulse onset (pulse-triggered)? Or are the extra errors spread out?

## Summary
The pre-registered clustering criterion is NOT met in any group: the 150–400 ms window hazard ratio CI includes 1 everywhere. Any excess of errors after incongruent pulses lies after 400 ms. For the other 8 mice, the out-of-window ratio is 1.50 [1.09, 1.92]. The window-minus-outside contrast does not separate either: log-ratio CI [−0.77, 0.23] (all mice). So there is no evidence that pulses trigger fast responses. Reading the flat-or-late ratio as "lapses" is not supported either; see Interpretation.

## Findings
Error hazard is P(error with RT − onset in the window | undecided at the window start). Control trials have 20 pseudo-onsets each, drawn from the mouse's own 100% pulse-onset distribution. Counts are pooled over mice. CIs are 95%, from 2,000 hierarchical bootstrap resamples (mice, then trials). Source: `dissemination/paper_accumulation/draft_2026-11-15/pulse_onset_hazard_2026-11-19/hazard_*.csv`.

- VERIFIED: **Primary analysis.** 100% coherence, incongruent pulses, all timings. Pulse/control hazard ratio:

  | group | 150–400 ms (pre-registered window) | 400–1500 ms |
  |---|---|---|
  | all 10 mice (71 errors / 1,462 at risk) | 1.15 [0.76, 1.54] | 1.38 [1.00, 1.87] |
  | PSUIM6/7 (29 / 681) | 1.18 [0.65, 1.71] | 1.14 [0.69, 2.08] |
  | other 8 (42 / 781) | 1.09 [0.61, 1.65] | 1.50 [1.09, 1.92] |

- VERIFIED: **By timing**, 150–400 ms ratio: early 1.11 [0.68, 1.76], middle 1.20 [0.67, 1.77], late 0.78 [0.00, 1.92]. Late pulses come from 6 mice, with only 7 window errors; PSUIM6/7 have no late pulses. In the 50 ms bins from 0 to 1500 ms, all bin CIs include 1.
- VERIFIED: **Check**, 36% coherence with congruent pulses. Here 100% has no congruent pulses at all: all 1,538 pulse trials are incongruent, a deviation recorded in the plan. This follows from the design: pulses replace baseline motion with ±100% coherence, and a replacement equal to the baseline is not a pulse. It is now stated in methods.md. The 150–400 ms ratio is 0.97 [0.63, 1.30], as expected.
- VERIFIED: **Data scope.** 272 errors in 1,538 incongruent pulse trials at 100%, against 622 errors in 4,529 control trials. Pulse onsets fall at 17–117 ms (early), 200–283 ms (middle) and 417 ms (late) after stimulus onset.

## Interpretation (SUSPECTED; flags a problem in criteria B)
Lapses occur on control trials as well, so they cancel in the pulse/control ratio. Lapses alone predict a ratio near 1 everywhere, not a flat ratio above 1. A ratio above 1 spread over time is what integrating the pulse into the evidence would produce: the pulse shifts the decision variable, and errors then come at ordinary RTs. That is the pattern in the other 8 mice after 400 ms. The pre-registered statement that a flat ratio means lapses is therefore applied only as written ("not clustered"). It should not be read as evidence for lapses. This does not change the guess_lapse decision; the excess at 100% coherence was already small.

## What didn't work
- The first run crashed on late pulses because PSUIM6/7 have none. Empty groups are now skipped, and the whole analysis was rerun from the same seed (20261119). Primary numbers are identical across the two runs.

## How to reproduce
`PYTHONPATH=/src .venv/bin/python -W ignore -m scripts.paper.pulse_onset_error_hazard --output dissemination/paper_accumulation/draft_2026-11-15/pulse_onset_hazard_2026-11-19` (CPU, about 1 min).

## Caveats
- Event counts are small (7 to 71 errors per window). Many 50 ms bins hold fewer than 10 errors.
- The window uses the pre-registered 150–400 ms, not per-mouse fitted ndt.
- Pseudo-onsets match each mouse's onset distribution but not session or time in session.

## Open questions and next steps
- [x] Author approved the corrected reading (2026-11-19): ratio ≈ 1 = no effect; peak at 150–400 ms = triggered; ratio > 1 spread later = integrated. Recorded in the plan as a post-hoc correction.
- Conclusion (author): pulse-triggered responses ruled out. The pulse goes through the accumulator. The models under-weight it, mostly in PSUIM6/7.
