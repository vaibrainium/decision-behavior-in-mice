<!-- np-contract
stage: S2 ; section: literature ; agent: np-devils-advocate ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims:
numbers:
sources:
-->
# Mouse dynamic-visual novelty challenge

ROLE: np-devils-advocate  
STAGE: S2  
DATE: 2026-10-24  
LOCKED THESIS: Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence.

## Scope and standard of evidence

This was a bounded, adversarial search intended to falsify a possible novelty claim, not a systematic review. The phrase “nobody has shown it in mice with a dynamic visual decision-making task” is ambiguous, so it was decomposed into four claims. A claim is marked **contradicted** when a primary source supplies a counterexample, **supported** only when direct evidence establishes it, and **not found in bounded search** when no counterexample appeared in the targeted search. “Not found” is not proof of absence.

## Verdicts

| Claim | Verdict | Reason |
|---|---|---|
| **A. Mice perform dynamic visual decisions.** | **CONTRADICTED as a novelty claim** | Multiple mouse studies use stochastic or temporally extended visual evidence during decisions. Odoemene et al. used stochastic full-field flash sequences; Pinto et al. and Koay et al. used randomly timed visual towers; the cross-species study used random visual pulse trains continuing until choice. |
| **B. Mice accumulate visual evidence.** | **CONTRADICTED as a novelty claim** | Pinto et al. reported modelling and nonparametric evidence for accumulation across visual pulses. Odoemene et al. estimated psychophysical kernels and found that evidence across the stimulus affected choice. Koay et al. explicitly studied pulsatile evidence accumulation. Marques et al. found duration- and area-dependent performance in a mouse random-dot-motion task, consistent with temporal and spatial integration, although that experiment alone is not the strongest mechanistic accumulation test. |
| **C. Randomized motion pulses have been used in mouse continuous random-dot motion.** | **NOT FOUND IN BOUNDED SEARCH** | Mouse random-dot-motion tasks were found, and randomized visual-pulse accumulation tasks were found, but no primary mouse study was located that combined continuous random-dot motion with randomized signed motion/coherence pulses embedded in the stimulus. The novelty lies in this conjunction, not in dynamic evidence or visual pulses generally. |
| **D. A control-fitted joint choice/response-probability/RT model was tested on held-out strong pulses.** | **NOT FOUND IN BOUNDED SEARCH** | No located mouse study combined continuous random-dot motion, a model fitted only to unpulsed/control trials, frozen predictions for strong randomized motion pulses, and joint evaluation of choices, response probability/censoring, and response times. This is the narrowest and most defensible novelty boundary. |

## Primary counterexamples and near neighbours

1. **Pinto et al. (2018), “An Accumulation-of-Evidence Task Using Visual Pulses for Mice Navigating in Virtual Reality.”** Mice viewed brief visual tower pulses drawn from random spatial processes while navigating. The paper reports that mice combined multiple cues over the cue period and uses modelling/nonparametric analyses to support accumulation. This is a direct counterexample to “first dynamic visual evidence task,” “first randomized visual pulses,” or “first visual evidence accumulation in mice.” Primary source: PubMed PMID **29559900**; PubMed Central **PMC5845651**.

2. **Odoemene et al. (2018), “Visual Evidence Accumulation Guides Decision-Making in Unrestrained Mice.”** Unrestrained mice judged stochastic full-field visual flash sequences; psychophysical kernels showed that evidence throughout the stimulus influenced choice. This directly contradicts broad novelty claims about dynamic visual evidence accumulation in mice. Primary source: PubMed Central **PMC6246883**.

3. **Koay et al. (2020), “Amplitude modulations of cortical sensory responses in pulsatile evidence accumulation.”** Mice performed the accumulating-towers task with randomly timed transient visual cues. This is a strong counterexample for mouse pulsatile visual evidence, but it is not continuous random-dot motion or a held-out strong-motion-pulse prediction test. Primary source: *eLife* 9:e60628, DOI **10.7554/eLife.60628**; PubMed Central **PMC7811404**.

4. **Marques et al. (2018), “A Role for Mouse Primary Visual Cortex in Motion Perception.”** Head-fixed mice discriminated random-dot-kinematogram direction. Performance depended on stimulus duration and spatial coverage, establishing mouse global-motion discrimination and suggesting integration. The task used fixed-duration stimuli rather than the randomized embedded signed motion pulses relevant here. Primary source: *Current Biology*, DOI **10.1016/j.cub.2018.04.012**; PMID **29779878**; PubMed Central **PMC5988967**.

5. **Stirman et al. (2016), “A touchscreen based global motion perception task for mice.”** Mice performed a two-alternative random-dot-motion discrimination task and yielded coherence thresholds. This defeats novelty at the level of mouse RDK psychophysics, but does not report the present perturbation-and-generalization test. Primary source: *Vision Research*, DOI **10.1016/j.visres.2016.07.006**; PMID **27497283**; PubMed Central **PMC5035629**.

6. **“A cross-species framework for investigating perceptual evidence accumulation.”** The study includes mice in a free-response task with randomly occurring brief visual pulses continuing until choice and analyses choices and response times. It is a close neighbour for pulse-based decision modelling, but not continuous random-dot motion with embedded strong signed-coherence pulses and the stated control-to-perturbation test. Primary source: *eLife* reviewed preprint, DOI **10.7554/eLife.105116**.

7. **“Dynamics of Visual Perceptual Decision-Making in Freely Behaving Mice.”** This is another direct counterexample to a broad “dynamic visual decision-making in mice” claim, including response-time/conditional-accuracy analyses, but it is not the exact continuous-RDK pulse generalization design. Primary source: PubMed Central **PMC8925649**.

## Exact query log

Public scholarly and publisher searches were run on 2026-10-24 with the following exact topic queries:

1. `mouse mice random dot motion decision making evidence accumulation pulse psychophysical kernel`
2. `mouse visual evidence accumulation dynamic visual decision task pulses virtual reality towers`
3. `mouse random dot kinematogram reaction time drift diffusion model`
4. `mice brief motion pulse random dot discrimination choice response time`
5. `"mice" "random dot" "motion pulse" decision`
6. `"mouse" "motion pulse" "random dot" discrimination`
7. `"mice" random dot motion psychophysical kernel decision`
8. `"mouse" continuous random dot motion evidence accumulation reaction time`
9. `site:pubmed.ncbi.nlm.nih.gov mice "random dot" "pulse"`
10. `site:pubmed.ncbi.nlm.nih.gov mouse random dot motion reaction time accumulation`
11. `site:pmc.ncbi.nlm.nih.gov mice "random dot motion" evidence accumulation`
12. `site:elifesciences.org mice visual evidence accumulation pulse task`

Records and cited/referencing links were checked through PubMed, PubMed Central/Europe PMC, publisher pages, and DOI records using exact titles or identifiers. Searches also returned randomized motion-pulse studies in macaques and continuous random-motion accumulation studies in rats or humans; these are relevant conceptual precedents but are not mouse counterexamples to claims C or D.

## Recommended novelty language

Safest factual wording for the manuscript:

> In a bounded literature search, we found no prior mouse study combining continuous random-dot-motion discrimination with randomized signed motion pulses and a frozen control-only model tested against joint choice, response-probability, and response-time outcomes.

If journal style calls for a “first” claim, use only the qualified, narrow version:

> To our knowledge, this is the first test in mice performing continuous random-dot-motion discrimination of whether a model fitted only to unpulsed trials predicts the joint choice, response-probability, and response-time consequences of randomized strong motion pulses.

Do **not** claim the first dynamic visual decision task in mice, the first use of randomized visual pulses in mice, the first mouse random-dot-motion task, or the first demonstration of visual evidence accumulation in mice. Refresh the search immediately before submission, and make the task/model conjunction explicit wherever novelty is claimed.

## Residual uncertainty

- Terminology is heterogeneous: relevant papers may describe “transient coherence changes,” “motion impulses,” “motion-energy perturbations,” or “kernels” without using “pulse.” Citation chaining from the closest mouse RDK and pulse-task papers should therefore accompany the pre-submission refresh.
- Claim C remains an absence claim. Its present status is **not found**, not established as historically first.
- Claim D is more distinctive but bundles several features; weakening any element of that conjunction increases the number of likely precedents.
