# Status
Last updated: 2026-10-22 by Codex (client date; prior entries dated 2026-10-23 retained)

## Current focus
Draft in dissemination/paper/manuscript_2026-10-22.md includes frozen predictions and completed strategy sensitivity.
Primary paper question: integration versus extrema detection; primacy secondary, conditional on adequacy/sensitivity.

## Active plans
- plans/2026-10-23-amendment-4-extrema.md : code done and checked; next: Hyak fits (commands in analysis log 8.4d)
- plans/2026-10-22-primacy-analysis-code.md : done; next: predictive check (gate 1) first pass when 8.4c batch 1 lands
- plans/2026-10-20-paper-writeup.md : first prose pass and provenance records done; next: queued results, missing author facts, figures and verification
- ../dissemination/reports/mouse-ddm-next-steps.md : analysis plan (kept in dissemination/reports); steps 0–3 done
  (3.3 confirmed the strict model); next: guess-bias fits, fit quality, gate 1 first pass, recovery (jobs running)

## Recent reports (newest first, keep about 10)
- reports/2026-10-22-prediction-sensitivity.md : all frozen hashes match; pulse-specific test selects generator in 1/20 extrema and 0/20 integrator simulations; observed pulse analysis pending
- reports/2026-10-22-arriving-results.md : independently verified control preference for integrator, free guess bias and completed recovery; manuscript updated; pulse predictions/comparison pending
- reports/2026-10-22-paper-first-draft.md : first manuscript prose; qualified hidden-coherence population claim, separated analysis sets; final strategy results pending
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
- Gate 1 FAILS for both baselines (departure +0.30 logit vs predicted pulse effect 0.03), concentrated in UCLA
  mice; timing test not run; model revision needed (analysis log 5.10).
- Pulse-specific strategy test has low sensitivity under frozen fitted candidates (1/20 extrema, 0/20 integrator correct); predicted effects differ by ~0.01 logit. Do not infer equivalence or independent pulse confirmation from an inconclusive result.
- Recovery: sv false-positive rate 7/20 at working threshold; guess-delay parameter poorly recovered. sv bounds and high-coherence error/late-response misfit limit mechanism interpretation (arriving-results report).
- Hidden-coherence k = 0.50 is a shared-model estimate; paired across-mouse coefficient comparison p = 0.492. Notebook controls use RT-dependent labels; scheduled-control sensitivity remains pending (first-draft report).
- Manuscript contains explicit pending/missing sections and unverified author-source records; Fig. 1F image/script still need censoring-label correction.
- Primacy test: predicted pulse effect ~0.025 logit; test likely cannot detect primacy (analysis log 5.7).
- Psychometric lapses (9–53%) are not captured by the fitted lapse; high-coherence errors probably absorbed by sv.
- Screen geometry not corrected in ME (ME methods §3.7).

## Decisions
- 2026-10-23: guess_bias free (V. Thakur; fixed costs 65.5 held-out NLL). Control trials favour the integrator over
  extrema detection (+346 NLL); no E refit (analysis log 5.8).
- 2026-10-22 (client date): user approved integration-versus-extrema discrimination as primary paper question, primacy secondary; draft established sections while Hyak jobs queue. Preserve existing confirmatory rules/order (first-draft report).
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
