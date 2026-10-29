# Plan: can pulse trials tell a leaky integrator from urgency? (research + route)
Status: done
Created: 2026-10-28 by Claude (Fable 5.1)
Related reports: reports/2026-10-29-pulse-leak-vs-urgency.md (this plan's report), reports/2026-10-22-leak-urgency-diagnosis.md, reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md,
reports/2026-10-23-pulse-tau-pilot-20261023T191030Z_fa8de8b.md, reports/2026-10-27-pulse-readout-model-rt-split.md,
reports/2026-10-28-pulse-time-comparison.md, dissemination/reports/pulse-thesis-research-2026-10-23.md

## Goal
A written answer to the author's question "what can we do to use pulse trials to tell if the DDM is leaky or urgency?":
what the repo has already tried and found, what the literature says pulses can and cannot discriminate, and a concrete,
calibrated route with decision rules. No cluster jobs, no new fits, no manuscript change.

## Context
Leak = OU decay toward the starting point (rate /s); urgency = gain (1 + u t) on accumulated evidence (collapsing bound
equivalent). Control-trial fits do not need either (component rows, D008); fitted values are small. The control-fitted
model underpredicts the pulse effect 2-7x (gain profile) and misplaces it in time; tau_p pilot failed. Descriptive
findings: no within-mouse change of the pulse effect across onsets; effect present at RT <= ~1.3 s and absent later,
no late reversal; toward-pulse choices faster.

## Assumptions
- The question is about the decision stage (leak vs urgency of the accumulator), not the sensory front end.
- Existing data only (author rule from 2026-10-23).

## Steps
- [x] 1. Orient: STATUS, leak/urgency, pulse reports, simulator equations, fitted leak/urgency, trial counts by pulse-to-response time.
- [x] 2. Literature (4 parallel researchers): theory of pulse signatures; primate/human pulse studies; rodent studies;
      identifiability and design methods. Notes in .agents/research_notes/Pulse tests of leak vs urgency/.
- [x] 3. Feasibility illustration (local CPU, exploratory, 2 dense mice): predicted pulse effect vs time from pulse to
      response under no leak/urgency, leak, urgency, from the primary control fit with the pulse gain matched to the
      observed effect; compare with the observed profile and per-bin trial counts. Label as illustration, not power.
- [x] 4. Report-writer synthesis -> dissemination/reports/pulse-leak-vs-urgency-literature-2026-10-29.md (path changed from the
      planned ...-research-2026-10-28.md; 11,818 words, 62 DOIs).
- [x] 5. Repo report (.agents/reports/2026-10-29-pulse-leak-vs-urgency.md): what was tried, what the literature says,
      recommended route with pre-specified statistics, power check and stop rules; update STATUS.
- [x] 6. Verify: every number in the report traces to a file or script; literature claims carry DOIs and locators.

## Out of scope
New model fits on the cluster; manuscript edits; any change to the closed primacy procedure.

## Log
- 2026-10-28: plan written; started immediately (no expensive steps).
- 2026-10-29: identifiability/design researcher (Claude Fable 5.1) wrote notes to .agents/research_notes/Pulse tests of leak vs urgency/identifiability_and_design.md (methods literature; step 2 partial, other three researchers' notes pending).
- 2026-10-29: all four researchers done (notes 60-82 KB each); report writer done. Feasibility illustration (step 3):
  first full run crashed at PSUIM6 urgency 1/s (grid proposed a = 11.65 > the simulator's limit of 10); fixed by
  clamping the grid and caching matched parameters; the five finished PSUIM6 settings were seeded from the log; rerun
  in progress (scripts/ddm/pulse_leak_urgency_signatures.py, outputs dissemination/figures/qc/pulse_leak_urgency_signatures_2026-10-29*).
- 2026-10-29: rerun finished (exit 0; whole set about 2 h on 16 threads, cache timestamps 00:07-01:52 UTC); figure re-rendered from cache (sparse simulated bins
  masked, empty late panels hidden, data trial counts added). SR1 not triggered in PSUIM6/7 (leak >= 1 /s separable by
  2-10 SE; urgency 0.3 /s not); but no variant reproduces the data's sustained 0.3-1.2 s effect and absent reversal.
  Report written (reports/2026-10-29-pulse-leak-vs-urgency.md); its two tables checked mechanically against the
  profile CSV (no mismatches). Plan done. Nothing committed (author has not asked).
