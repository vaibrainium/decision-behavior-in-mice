# Status
Last updated: 2026-10-23 by Claude (Opus 5.5)

## Current focus
DDM model selection for the mouse pulse task (next-steps plan steps 1–3) and starting the paper write-up.

## Active plans
- plans/2026-10-23-amendment-4-extrema.md : code done and checked; next: Hyak fits (commands in analysis log 8.4d)
- plans/2026-10-22-primacy-analysis-code.md : done; next: predictive check (gate 1) first pass when 8.4c batch 1 lands
- plans/2026-10-20-paper-writeup.md : paper outline done; next, authors settle open decisions and Methods drafting starts
- ../dissemination/reports/mouse-ddm-next-steps.md : analysis plan (kept in dissemination/reports); steps 0–3 done
  (3.3 confirmed the strict model); next: guess-bias fits, fit quality, gate 1 first pass, recovery (jobs running)

## Recent reports (newest first, keep about 10)
- reports/2026-10-23-control-only-selection.md : strict model holds under control-only CV (sv, guesses needed;
  leak/urgency not); batches 1, 3b and recovery resubmitted
- reports/2026-10-22-primacy-power.md : primacy pipeline built (synthetic-only checks); predicted pulse effect
  ~0.025 logit, so the timing test has ~no power under the fitted model; decision pending
- reports/2026-10-22-leak-urgency-diagnosis.md : leak/urgency gains are specific to PSUIM5/6/7 and mostly fit the
  coherence-flat rate of > 5 s responses (likely late engagement); not a power issue
- reports/2026-10-21-ddm-common-model-selection.md : sv and fast guesses pass the noise threshold in most mice; leak
  and urgency only in the 3–4 best-sampled mice; sz out; fast_only guess form preferred
- ../dissemination/reports/primacy-analysis-plan.md : locked confirmatory primacy plan (commit aeb0a22), 2 amendments
- ../dissemination/reports/mouse-ddm-analysis-log.md : full analysis log (ME, hidden coherence, DDM generations)
- ../dissemination/reports/motion-energy-methods.md : motion-energy method review and corrections

## Known issues
- Primacy test: predicted pulse effect ~0.025 logit; test likely cannot detect primacy (analysis log 5.7).
- Psychometric lapses (9–53%) are not captured by the fitted lapse; high-coherence errors probably absorbed by sv.
- Screen geometry not corrected in ME (ME methods §3.7).

## Decisions
- 2026-10-23: primacy plan amendment 5 adopted by V. Thakur (strategy test: pulse-specific statistic, paired sampling SD; E's
  drift_gain refit rule; implementation-note corrections); null calibration done.
- 2026-10-23: primacy plan amendment 4 adopted (integration vs extrema detection; leak 20–200 /s; 3 SD and 6/10 mice);
  gate 1 waits for its fits and frozen predictions (plans/2026-10-23-amendment-4-extrema.md).
- 2026-10-22: primacy power issue: run the predictive check (gate 1) first; gates 2–3 rule ≥ 80% inside
  (analysis log 5.7).
- 2026-10-22: common DDM model = L0U0V1Z0G1 + fast_only guesses (strict rule 2); secondary baseline L1U1V1Z0G1;
  primacy plan amendment 3 (reports/2026-10-22-leak-urgency-diagnosis.md; analysis log 5.6).
- 2026-10-22: delayed-engagement parameter not pursued (V. Thakur).
- 2026-10-21: no second warm-start round (gaps ≤ 5.9 NLL, below noise); sz out; fast_only guess form preferred
  (reports/2026-10-21-ddm-common-model-selection.md).
- 2026-10-20: primacy analysis plan locked (primacy-analysis-plan.md, commit aeb0a22); parsimony rules agreed
  (next-steps plan).
- 2026-10-20: SC WFV inactivation excluded from the paper; separate study (V. Thakur).
