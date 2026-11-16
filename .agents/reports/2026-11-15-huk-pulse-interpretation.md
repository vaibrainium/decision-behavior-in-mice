# Report: retain the pulse analysis and clarify the Huk/Shadlen interpretation
Date: 2026-11-15   Agent: Codex   Commit: b63c9d9 (base; new notes uncommitted)
Plan: plans/2026-11-15-huk-pulse-interpretation.md

## Question
Does Huk/Shadlen justify retaining the pulse-persistence analysis and interpreting its late decline as forgetting?

## Summary
AUTHOR PREFERENCE: retain the post-pulse analysis in the main paper. This is compatible with the prior direction report; the earlier conversational emphasis made the caveat sound like a reason to demote it. VERIFIED: Huk/Shadlen use persistent pulse effects as evidence for temporal integration, while explicitly warning that their persistence measurement does not estimate the intrinsic integration time constant. Keep the positive persistence result and observed decline central, with mechanism inference bounded by forward predictions.

## Findings
- VERIFIED — primary paper: Huk AC, Shadlen MN (2005), J Neurosci 25:10420–10436, DOI https://doi.org/10.1523/JNEUROSCI.4684-04.2005 . Original PDF read at https://www.gatsby.ucl.ac.uk/~pel/course_wuhan/2021/papers/huk_shadlen2005.pdf ; canonical full text https://pmc.ncbi.nlm.nih.gov/articles/PMC6725829/ . Original journal page was inaccessible and PMC open returned a challenge; the PDF and search-indexed original text agreed.
- VERIFIED — Fig. 4 / Eq. 8: behavioral effects were estimated in bins of response latency relative to pulse onset, using psychometric shifts in coherence-equivalent units. Methods assign virtual onsets to controls. Persistent influence was interpreted as evidence of integration. Source: primary PDF printed pp. 10423–10424 and 10427; PDF text lines 396–418, 720–753, 783–794.
- VERIFIED — Figs. 8–9: perfect bounded integration can yield declining pulse effects. Much of this explicit simulation comparison concerns neural trajectories, so it should not be called an exact replication of our behavioral dilution analysis. Source: primary PDF printed pp. 10430–10431, lines 955–1081.
- VERIFIED — Discussion explicitly says their experiment does not measure the integration time constant, and explains why stopping at a bound can produce finite apparent persistence without leak. Source: primary PDF printed p. 10434, lines 1302–1317. This is not a reason to remove the persistence analysis: the same paper treats persistent influence as a positive integration result.
- VERIFIED — our dilution-adjusted gamma-times-T statistic is an additional analysis, not Huk's Eq. 8 result. Its constant benchmark assumes a fixed retained contribution diluted by later evidence; the script explicitly notes that it ignores bound selection and disengagement. Source: scripts/behavior/pulse_dilution.py docstring and per_bin(). Do not attribute that benchmark's mechanistic interpretation to Huk/Shadlen.
- VERIFIED AGAINST EXISTING OUTPUTS — our zero-leak, zero-urgency, zero-drift-variability bounded model also shows a late decline under the behavioral estimator. The complete model includes response mapping and guesses; this establishes a counterexample to uniqueness, not a complete decomposition attributing the mouse decline specifically to decision bounds. Source: dissemination/pulse_dynamics_2026-11-13/RESULTS.md, section on the late decline, and adjacent summary_across_seeds.csv. No simulations rerun this turn.

## Decision / wording
Retain the main behavioral result: brief motion perturbations have a sustained directional influence on choices well after the pulse, followed by a reduction among later responses. Existing mouse results and uncertainty are in dissemination/pulse_dynamics_2026-11-13/ and the directional decomposition outputs cited by the replication report.

Suggested interpretation: persistence supports temporal integration on the behavioral timescale; the full trajectory provides constraints on accumulation accounts. The late reduction alone does not uniquely establish intrinsic forgetting. The existing zero-leak example does not show that the mice have zero leak, nor that its whole quantitative trajectory fits the data.

Use the observed response interval descriptively. It is not automatically the accumulator's intrinsic time constant or an independently measured sensory/decision memory duration. Keep the decay curve and compare forward predictions, rather than discarding the analysis or labeling a fitted curve as a direct forgetting measurement.

## What did not work
- Earlier emphasis on the caveat obscured the positive persistence result and the author's intended main-paper role.
- Equating the dilution correction with Huk's original behavioral analysis would conflate related but distinct estimators.

## How to reproduce
Read the primary PDF at the URL above, specifically Eq. 8 / Fig. 4, Figs. 8–9 and the Discussion paragraph on the integration time constant. Local commands used for method/source checking:

```bash
sed -n '1,125p' scripts/behavior/pulse_dilution.py
cat dissemination/pulse_dynamics_2026-11-13/RESULTS.md
cat .agents/reports/2026-10-29-huk-shadlen-replication.md
```

No new fits, statistics, packages or manuscript changes. Existing corrected output provenance is retained in the cited reports. Scientific-critical-thinking guidance was reused; workflow attribution is in the preceding paper-direction report.

## Caveats
The literature supports a distinction between persistence evidence and an intrinsic time constant; it does not by itself validate every claim in the mouse analysis. Behavioral and neural time courses are related but distinct. Neither the old dilution benchmark nor one no-leak example selects a unique mechanism.

## Open questions and next steps
- [ ] Keep the post-pulse persistence/decline result in the main figure and Results argument as requested.
- [ ] When editing prose/legends, distinguish observed persistence from intrinsic forgetting and identify gamma-times-T as our additional benchmark.
- [ ] Use existing quantitative predictions to assess the full trajectory; no new fitting campaign was authorized or launched in this clarification.
