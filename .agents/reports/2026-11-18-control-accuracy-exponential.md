# Report: Descriptive exponential conditional-accuracy fits
Date: 2026-11-18   Agent: Codex   Commit: eef364b (base; changes uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Does a saturating exponential provide a useful overlay for candidate Figure3D?

## Summary
Four nonzero-coherence exponentials and a zero-coherence constant fitted successfully. Curves visually describe the initial rise and plateau, most clearly at high coherence. Weak-coherence bootstrap fits expose poor time-constant identification. No mechanistic time-constant or bound claim is established.

## Findings
- VERIFIED: same 14,014 scheduled-control trials and all 613 previous mouse/coherence/time cells; counts and correct totals exactly match. Source: checks.json and trials.csv.
- VERIFIED: tau estimates in seconds for coherence100/36/18/9% are 0.269608/0.245166/0.284766/0.252939; asymptotes are0.913806/0.775069/0.668989/0.562187. Zero-coherence constant0.484788. Source: parameters.csv.
- VERIFIED: 200 whole-mouse resamples per coherence, all 1,000 fits converged. Tau-bound contacts:9%=11,18%=1,36%=0,100%=0. Source: bootstrap_parameters.csv and checks.json. 9% percentile tau interval0.134578–20s reaches the numerical upper bound; it is not a precise time estimate. Source: parameter_intervals.csv.
- VERIFIED: objective independently evaluated directly, analytic gradients checked against finite differences; curves monotonic and bounded within probabilities. Source: manifest.json and checks.json.
- INTERPRETATION: useful descriptive overlay at high coherence; late fluctuations remain, and the monotonic constraint cannot capture nonmonotonic patterns. No formal goodness-of-fit test performed.

## What didn't work
Weak-coherence bootstrap parameters are insufficiently identified despite numerical convergence. Retained all resamples and reported boundary contacts; did not narrow intervals by exclusion or adjust bounds to improve apparent precision.

## How to reproduce
From /src: `.venv/bin/python -m scripts.paper.control_accuracy_exponential --output dissemination/paper_accumulation/draft_2026-11-15/figure3_exponential_2026-11-18` (fresh output path for reruns).
Existing .venv; no installation. Raw/model input hashes in checks.json. Data-only panel source: figure3_conditional_accuracy_2026-11-18. Script: scripts/paper/control_accuracy_exponential.py. Output files under dissemination/paper_accumulation/draft_2026-11-15/figure3_exponential_2026-11-18/.

## Caveats
Trial-level weighted Bernoulli likelihood with equal total contribution per mouse/coherence is a descriptive composite criterion. It differs from equal-mouse weighting within RT bins. The common curve does not estimate individual trajectories. Pointwise percentile uncertainty resamples mice; 10 animals and 200 draws limit precision. Main artwork shows original data SEM; separate diagnostic shows curve bootstrap intervals. No inferential tests, held-out assessment or mechanistic tau interpretation.

## Open questions and next steps
- [x] Author selected exponential Figure3D on 18 November 2026.
- [x] Add selected caption and Methods/panel pointers; retain parameter-instability caveats.
- [ ] Assemble combined figure after final A choice.
