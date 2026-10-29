# Report: the held-out likelihood does not use trial-by-trial motion energy
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: see git log (scripts/ddm/shuffle_me_check.py)
Plan: plans/2026-10-29-control-paper.md (D002 item 3, motion-energy ablation)

## Question
Before running the D002 ablation (refits on shuffled motion energy and nominal coherence): what can the existing model
comparison say about whether the trial-specific motion energy is used?

## Summary
Nothing. The likelihood (CensoredQMLE, src/ddm/likelihood_calculator_censored.py) scores per condition the choice counts and
the RT quantiles per choice. On control trials, condition = signed coherence (build_ddm_inputs.py line 149). So
predictions are pooled over the trials of a condition, and no trial's choice is matched to its own stimulus. Shuffling the
noise between trials of the same coherence leaves the likelihood unchanged up to Monte Carlo noise. The shuffled-ME refit
is a no-op by construction and should not be run. The input enters only through the distribution of stimuli within a
condition, which acts like between-trial drift variability. The only trial-level test of motion-energy use is the kernel,
which is null and underpowered (reports/2026-10-29-control-descriptives.md).

## Findings
- VERIFIED. Common model, control fit (fits_resp_final), all responded control trials, n_reps 15. NLL is shown as real /
  shuffled within coherence / real with another seed. DBM12 2295.9 / 2297.2 / 2298.4; PSUIM5 3713.3 / 3715.5 / 3713.0;
  PSUIM7 11500.9 / 11499.4 / 11506.7. The shuffle effect is within seed noise. The choice-only part is identical:
  500.5 / 500.4 / 500.8; 693.5 / 693.4 / 695.2; 2346.3 / 2346.9 / 2343.0. Script: scripts/ddm/shuffle_me_check.py.
- VERIFIED. The choice part is about 20% of the NLL (DBM12 500 of 2296; PSUIM7 2346 of 11501). RT terms dominate the
  comparisons.

## What didn't work
- Shuffled-ME ablation as planned: uninformative by design (above). Not run on the cluster.

## How to reproduce
`cd /src && .venv/bin/python scripts/ddm/shuffle_me_check.py` (CPU, a few min).

## Caveats
- Three mice and one model were checked. The result follows from the likelihood's structure, so it holds for every model
  and mouse.
- Nominal-coherence refits are still informative, but about within-condition stimulus variability, not trial-level use.

## Open questions and next steps
- [ ] Choice vs RT split of the existing held-out comparisons (C vs E, ES, DDMx, ESx; CV fits): local re-scoring with
      rt_nllh_weight 0.
- [ ] Thesis wording: "net motion energy" is the model input, not a demonstrated cue. Show trial-level use only with a
      trial-wise likelihood or the kernel.
- [ ] Optional: nominal-coherence refits of C, E and ES (needs make_params to allow sv and guesses with nominal input; cluster).
