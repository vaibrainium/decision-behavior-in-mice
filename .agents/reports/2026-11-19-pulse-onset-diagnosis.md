# Why pulse-only models miss the perturbation
Date: 2026-11-19   Agent: Codex   Commit: 300a223 (analysis base: 3b55eca)
Plan: plans/2026-10-26-paper-accumulation-variant.md (onset-discrepancy review)

## Question

Is the mismatch a general steep primacy law, excess pulse sensitivity in particular animals, or an artifact of the readout? What mechanisms can the literature and existing experiments distinguish?

## Summary

The strongest residual is an unusually large directional effect of early pulses in two well-sampled mice, repeated across sessions. The observed population slope halves when each mouse has equal total weight in the same psychometric regression. The three-stage slope remains a useful exploratory constraint, with heterogeneity and missing late support. Stronger encoding of the transient and pulse-dependent commitment are candidate explanations. Neural attention and intrinsic leak remain unidentified.

## Findings

- VERIFIED. Saved Figure 4C simulations and cohorts. Reweighting the same ordinal model changes the data slope from −5.40 to −2.39 and the predictive winner from −0.73 to −0.41 coherence units per stage. Equal-mouse UCLA E/M −5.34, UW E/M/L −0.19. Sources in the output package below, especially ordinal_weighting.csv. Eighteen descriptive fits, ten starts each, no bound contacts.
- VERIFIED. Probability of choosing right, right versus left early pulse: PSUIM6 17.47 pp, PSUIM7 25.10 pp. Their early estimates exceed the maxima of 60 trial-sized conditional predictions per animal (13.72 and 21.82 pp). Both early-minus-middle observed contrasts lie within the full ranges. Early residual positive in 12/15 and 9/11 sessions; prior full-data fit. Sources: conditional_prediction_ranges.csv, session_residuals.csv.
- VERIFIED. All ten, equal mouse/coherence, early/middle 7.74/8.78 pp; observed-overlap weighted 7.75/7.46. Five of ten show early > middle under either weighting. UCLA combined early/middle 15.40/12.74; UW 2.64/6.14. No new between-site test. Sources: mouse.csv, group.csv, overlap_weighted_mouse_by_seed.csv.
- VERIFIED. One second after early onset in UCLA, pulse-average minus sham probability of having responded was +4.22 pp vs model +0.98 pp. Conditional on responding by the deadline and being at risk at onset. Source: group.csv. Does not establish alerting.
- INTERPRETATION. Input amplification, nonlinear commitment and temporal expectation can change the same behavioral curve. Earlier shared/time-specific pulse weights, causal ME audits, pulse-only scoring, history/HMM and response-delay/gain pilots bound each claim. See linked review for sources and public primary literature.

## What did not work

An exploratory filename wildcard also selected neighboring model variants and the count assertion halted the first draft. Final script uses exact family/mouse/seed filenames. Fresh rerun reproduced all numeric CSVs. Equal coherence weighting gives noisy cells appreciable leverage; overlap weighting is reported independently. Early/middle trial-level caches omit late; no late cumulative-response estimate was attempted.

## Reproduce

`OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.diagnose_pulse_onset --output <fresh-dir>`. Fixed parameter simulation caches and source file hashes in verification.json. Independent reconstruction from eligible trial rows confirmed every observed early/middle mouse-level contrast. Source and outputs at [review and evidence](../../dissemination/paper_accumulation/draft_2026-11-15/pulse_onset_diagnosis_2026-11-19_final/REVIEW.md). Literature scope/searches in search.json.

## Caveats and next steps

- The direct contrast and the Figure 4C psychometric shift have different units. Rig is confounded with animal; conditional predictions omit fitted parameter uncertainty. These are descriptive, exploratory checks in a filtered population. Distinguish archival joint fits from the 22 pulse-only models.
- [ ] If extending modeling, compare a signed transient-input gain against a pulse-locked commitment change with a common pulse-only baseline, session holdout, and separate signed and any-response predictions. Check recoverability on the existing schedules. No change to accepted figures or manuscript.
