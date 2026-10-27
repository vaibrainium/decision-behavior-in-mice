# Report: no-response trials look like disengagement, not slow decisions
Date: 2026-10-27   Agent: Claude (Opus 5.5)   Commit: 2e19e30
Plan: none (read-only descriptive check)

## Question
Was treating the 4,537 no-response-by-5 s trials as censored DDM outcomes ("the same diffusion, not yet at the bound")
justified, or did it push the fits toward wrong assumptions?

## Summary
The data contradict the censoring assumption for most of these trials: non-response stays high at 100% coherence,
rises steeply at the end of sessions and comes in runs. This matches lapse/disengagement states, not unfinished
diffusion. Effects on the fits are SUSPECTED, not tested; the responded-only refits (src-85) will test them.

## Findings
Source: /mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv (in_ddm_input rows, 30,030;
none = response_side == "none", 4,537); inline Python, this session.
- VERIFIED: no-response rate by |coh|: 0% 19.1, 9% 17.3, 18% 16.9, 36% 15.2, 100% 9.1. A bounded diffusion fitted to
  these mice should rarely fail to respond at 100% within 5 s.
- VERIFIED: by within-session decile: 14.2, 9.7, 10.4, 10.6, 10.0, 11.2, 13.6, 15.7, 17.9, 37.7 %.
- VERIFIED: runs: P(none | previous trial none) 33.7% vs P(none | previous responded) 11.8%.
- VERIFIED: the 4,102 responses after 5 s have median 7.7 s (IQR 6.0-11.5, max 59.7 s).
- VERIFIED: per-mouse no-response %: DBM15 24.5, PSUIM5 22.5, PSUIM6 21.7, PSUIM10 14.5, DBM5 13.7, DBM6 13.3,
  DBM13 11.5, DBM14 11.5, PSUIM7 8.2, DBM12 7.3 (ddm_inputs_global.npz, choice < 0).
- SUSPECTED: the bound at its cap (a = 9.5; parameter table 2026-10-23) in DBM15 and PSUIM6 (two of the three
  highest-non-response mice) and the leak/urgency gains in PSUIM5/6/7 (already traced to the coherence-flat > 5 s rate;
  reports/2026-10-22-leak-urgency-diagnosis.md) are artefacts of fitting disengaged trials as unfinished diffusion.
- SUSPECTED: part of the pulse predictive-gate failure (predicted 0.057 vs observed +0.24/+0.31 logit) comes from this:
  a bound inflated to fit non-responses shrinks the predicted effect of a 50 ms pulse. Testable with the refits.
- VERIFIED: the behavioural pulse contrast was diluted by counting non-response as an outcome (5.84 -> 7.52 pp;
  reports/2026-10-27-pulse-contrast-responders-only.md).

## Literature (checked 2026-10-27; not yet added to the paper source list)
- Ashwood et al. 2022, Nat Neurosci 25:201-212: mice switch between an engaged state and biased/disengaged states
  that last tens to hundreds of trials; lapses concentrate in those states.
- Pisupati et al. 2021, eLife 10:e55490: rat lapses are not pure noise (exploration account).
- Ratcliff & Tuerlinckx 2002, Psychon Bull Rev 9:438-481: contaminant RTs bias diffusion-model fits (ML badly so);
  handled with a contaminant mixture or cut-offs.
- Hawkins et al. 2015, J Neurosci 35:2476-2484 (already a verified source): support for urgency/collapsing bounds
  depends on paradigm and procedure.

## Caveats
- Responded trials near 5 s, and early-session or late-session responded trials, may also be disengaged; dropping
  non-responses removes only part of the contamination. The model's fast-guess component covers fast guesses only.
- I haven't simulated the fitted model's predicted censored rate at 100% coherence (would sharpen finding 1).

## Open questions and next steps
- [ ] Compare the responded-only refits (src-85) against the current fits: a, sv, leak/urgency selection, predicted pulse effect.
- [ ] Option: an engagement filter (e.g. GLM-HMM state, or dropping end-of-session blocks), defined before outcomes.
