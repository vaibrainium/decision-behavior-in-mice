# Status
Last updated: 2026-10-22 by Claude (Opus 5.5)

## Current focus
DDM model selection for the mouse pulse task (next-steps plan steps 1–3) and starting the paper write-up.

## Active plans
- plans/2026-10-20-paper-writeup.md : paper outline done; next, authors settle open decisions and Methods drafting starts
- ../dissemination/reports/mouse-ddm-next-steps.md : analysis plan (kept in dissemination/reports); steps 0–2 and 3.1
  done; common model chosen (strict); next: guess-bias fits, fit quality, step 3.3, recovery

## Recent reports (newest first, keep about 10)
- reports/2026-10-22-leak-urgency-diagnosis.md : leak/urgency gains are specific to PSUIM5/6/7 and mostly fit the
  coherence-flat rate of > 5 s responses (likely late engagement); not a power issue
- reports/2026-10-21-ddm-common-model-selection.md : sv and fast guesses pass the noise threshold in most mice; leak
  and urgency only in the 3–4 best-sampled mice; sz out; fast_only guess form preferred
- ../dissemination/reports/primacy-analysis-plan.md : locked confirmatory primacy plan (commit aeb0a22), 2 amendments
- ../dissemination/reports/mouse-ddm-analysis-log.md : full analysis log (ME, hidden coherence, DDM generations)
- ../dissemination/reports/motion-energy-methods.md : motion-energy method review and corrections

## Known issues
- Psychometric lapses (9–53%) are not captured by the fitted lapse; high-coherence errors probably absorbed by sv.
- Screen geometry not corrected in ME (ME methods §3.7).

## Decisions
- 2026-10-22: common DDM model = L0U0V1Z0G1 + fast_only guesses (strict rule 2); secondary baseline L1U1V1Z0G1;
  primacy plan amendment 3 (reports/2026-10-22-leak-urgency-diagnosis.md; analysis log 5.6).
- 2026-10-22: delayed-engagement parameter not pursued (V. Thakur).
- 2026-10-21: no second warm-start round (gaps ≤ 5.9 NLL, below noise); sz out; fast_only guess form preferred
  (reports/2026-10-21-ddm-common-model-selection.md).
- 2026-10-20: primacy analysis plan locked (primacy-analysis-plan.md, commit aeb0a22); parsimony rules agreed
  (next-steps plan).
- 2026-10-20: SC WFV inactivation excluded from the paper; separate study (V. Thakur).
