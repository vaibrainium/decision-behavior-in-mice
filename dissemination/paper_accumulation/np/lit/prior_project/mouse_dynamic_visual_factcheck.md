<!-- np-contract
stage: S2 ; section: mouse_dynamic_visual_factcheck ; agent: np-librarian ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C003, C004, C005, C006, C009
numbers: none
sources: douglas2006motion, stirman2016touchscreen, pinto2018visualpulses, marques2018mousev1, samonds2018motion, odoemene2018visual, koay2020amplitude, you2022dynamics, caballero2022rt, chakravarty2025cross
-->
# Mouse dynamic-visual decision-making: novelty fact-check

Access date: **2026-10-24**. This was a bounded narrative search, not a systematic review. Search strings contained only public topic terms.

## Question and decision rule

The claim tested was whether visual evidence accumulation or dynamic visual decision-making had not previously been shown in mice. That broad claim is false. The narrower question was whether an earlier mouse study combined (i) continuous noisy random-dot motion, (ii) a free-response choice/response-time model fit on unperturbed trials, and (iii) a separately randomized, strong signed motion pulse used as a held-out prediction test, including no-response outcomes.

Included records used mice in a visual discrimination/decision task and contained at least one of: random-dot motion, temporally varying/discrete visual evidence, a brief visual pulse, response-time modelling, or an explicit accumulation model. Passive vision papers, nonvisual tasks, and records in which “mouse” meant a computer pointing device were excluded. Virtual-navigation towers/flashes and repeated-pulse tasks were retained as counterexamples but classified separately from continuous random-dot motion.

## Search log

Database totals are broad discovery counts; only bounded result sets were screened. Across the searches below, 36 de-duplicated title/abstract records were screened and 10 were retained.

| Database | Exact query | Bound | Hits | Screened | Kept |
|---|---|---:|---:|---:|---:|
| PubMed | `mice[Title/Abstract] AND ("visual evidence accumulation"[Title/Abstract] OR "accumulation of evidence"[Title/Abstract])` | first 10 by relevance | 21 | 10 | 3 |
| PubMed | `(mouse[Title/Abstract] OR mice[Title/Abstract]) AND ("random dot motion"[Title/Abstract] OR "random dot kinematogram"[Title/Abstract])` | all | 4 | 4 | 1 |
| PubMed | `(mouse[Title/Abstract] OR mice[Title/Abstract]) AND ("random dot*"[Title/Abstract] OR "random-dot*"[Title/Abstract]) AND (discrimination[Title/Abstract] OR decision*[Title/Abstract])` | all | 2 | 2 | 1 |
| PubMed | `(mouse[Title/Abstract] OR mice[Title/Abstract]) AND "motion coherence"[Title/Abstract] AND (choice[Title/Abstract] OR discrimination[Title/Abstract])` | all | 1 | 1 | 1 |
| PubMed | `(mouse[Title/Abstract] OR mice[Title/Abstract]) AND visual[Title/Abstract] AND pulse*[Title/Abstract] AND decision*[Title/Abstract]` | all | 3 | 3 | 2 |
| PubMed | `(mouse[Title/Abstract] OR mice[Title/Abstract]) AND ("motion pulse"[Title/Abstract] OR "motion pulses"[Title/Abstract])` | all | 0 | 0 | 0 |
| PubMed | `(mouse[Title/Abstract] OR mice[Title/Abstract]) AND ("drift diffusion"[Title/Abstract] OR "diffusion decision"[Title/Abstract]) AND visual[Title/Abstract]` | all | 2 | 2 | 1 |
| PubMed | `(mouse[Title/Abstract] OR mice[Title/Abstract]) AND visual[Title/Abstract] AND evidence[Title/Abstract] AND (reaction time[Title/Abstract] OR response time[Title/Abstract])` | first 10 | 10 | 10 | 2 |
| PubMed | `(mouse[Title/Abstract] OR mice[Title/Abstract]) AND visual[Title/Abstract] AND ("brief pulse*"[Title/Abstract] OR perturbation[Title/Abstract]) AND choice[Title/Abstract]` | all | 1 | 1 | 0 |
| PubMed | exact-title retrieval for Douglas 2006, Stirman 2016, Pinto 2018, Marques 2018, Odoemene 2018, Samonds 2018, Koay 2020, You 2022, Caballero 2022, Chakravarty 2025 | metadata/full-text check | 10 | 10 | 10 |
| OpenAlex | `search=mouse visual evidence accumulation` | first 10, relevance | 103161 | 10 | 4 |
| OpenAlex | `search=mice random-dot motion discrimination` | first 10, relevance | 4401 | 10 | 3 |
| OpenAlex | `search=mouse visual pulse decision` | first 10, relevance | 25315 | 10 | 3 |
| Europe PMC | `mouse AND "visual evidence accumulation"` | first 10 | 16 | 10 | 5 |
| Europe PMC | `mouse AND "random dot motion"` | first 10 | 162 | 10 | 3 |
| Crossref | `query.bibliographic=mouse visual evidence accumulation` | first 10 | 2161464 | 10 | 3 |
| Crossref | `query.bibliographic=mice random-dot motion discrimination` | first 10 | 1285707 | 10 | 3 |

OpenAlex and Crossref full-text search totals are intentionally reported only as discovery totals; they are not evidence of exhaustive coverage. Title normalization and DOI/PMID matching were used to de-duplicate records across services.

## Retained-study map

| Source | Species | Stimulus/task | Dynamics | Evidence | Randomized pulse perturbation? | Choice/RT model? | Pulse outcomes held out? | Class |
|---|---|---|---|---|---|---|---|---|
| Douglas et al. 2006 | rat and mouse | RDK direction discrimination | dynamic dots; coherence varied across trials | continuous during display | no | no | no | continuous RDK psychophysics |
| Stirman et al. 2016 | mouse | touchscreen 2AFC global-motion discrimination | RDK; dot lifetime/speed/coherence varied | continuous during display | no | no | no | continuous RDK psychophysics |
| Marques et al. 2018 | mouse | head-fixed 2AFC left/right RDK | fixed-duration RDK; duration and aperture varied | continuous during display | no | choice psychometrics; no joint RT model | no | continuous RDK decision task |
| Samonds et al. 2018 | mouse | conditioned lick to RDK direction; motion aftereffect | 3–4 s RDK, sometimes preceded by prolonged adapter | continuous during display | no; adapter was a condition, not a brief randomized evidence pulse | lick/coherence and latency curves, not a joint generative model | no | continuous RDK conditioning |
| Pinto et al. 2018 | mouse | VR T-maze; choose side with more visual towers | 200-ms towers at random spatial Poisson locations | discrete repeated pulses | pulses are the primary evidence stream, not perturbations embedded in a control stimulus | logistic and accumulation models for choice; no joint free RT likelihood | no | discrete-pulse accumulation counterexample |
| Odoemene et al. 2018 | mouse | categorize whether 1-s flash count exceeded boundary | stochastic sequence of 20-ms full-field flashes | discrete repeated pulses | no separate perturbation; flashes constitute the evidence | psychometric/kernel analyses; fixed-duration, no joint RT model | no | discrete-flash accumulation counterexample |
| Koay et al. 2020 | mouse | VR accumulating-towers task with cortical recordings | randomly placed 200-ms towers over navigation | discrete repeated pulses | primary evidence events, not held-out perturbations | behavioural choice model/psychophysical weighting; no joint RT model | no | neural discrete-pulse counterexample |
| You and Mysore 2022 | mouse | freely moving touchscreen orientation discrimination | static grating present 0.1–3 s or until response | sustained, not RDK | no | conditional-accuracy/RT summaries; no DDM | no | visual RT comparator |
| Caballero et al. 2022 | mouse | freely moving visual discrimination with cortical inactivation | stimulus contrast varied | sustained visual stimulus, not RDK pulse stream | no | DDM fit to choices and escape latencies | no | mouse joint choice/RT-model comparator |
| Chakravarty et al. 2025 | mouse, rat, human | synchronized pulse-based perceptual task | repeated discrete light evidence pulses | discrete repeated pulses | no separate held-out perturbation | cross-species decision-model comparison including RT | no | recent discrete-pulse/model counterexample |

## Verdict

**Broad novelty claim rejected.** By 2018, mouse studies had already demonstrated visual evidence accumulation using stochastic full-field flashes and VR towers (Pinto; Odoemene), and several studies had established mouse RDK discrimination (Douglas; Stirman; Marques). Caballero later fit a DDM to mouse choices and response latencies, while Chakravarty et al. compared pulse-task decision models across mice, rats and humans.

**No exact precedent found in this bounded search.** None of the retained mouse studies fit a joint choice/response-time model to continuous noisy random-dot motion on unperturbed trials and then tested frozen predictions on separately randomized strong signed motion pulses. The closest studies each contain only part of that combination: RDK without pulse transfer (Marques), discrete pulses without continuous RDK or a control-to-pulse transfer test (Pinto/Odoemene/Koay/Chakravarty), or mouse DDM response-time fitting without RDK pulses (Caballero).

## Narrowest defensible novelty sentence

> In a bounded search, we found no prior mouse study that fit a joint choice/response-time model to continuous noisy random-dot motion on unperturbed trials and then tested its frozen predictions on separately randomized strong signed motion pulses, including no-response outcomes.

Use “we found no prior study” rather than “first” or “nobody has shown.” The claim is about the **combination and held-out transfer test**, not about mouse visual accumulation, dynamic visual decision-making, RDK discrimination, pulse-based evidence accumulation, or mouse diffusion modelling individually.

## Limits

- This is a single-reviewer, bounded narrative search and cannot prove universal absence.
- “Dynamic visual task” is too broad to sustain novelty because RDK, flash-sequence and VR-tower mouse tasks all qualify.
- The negative exact-precedent finding should be rechecked immediately before submission, especially against preprints and forward citations of Marques 2018, Pinto 2018, Caballero 2022 and Chakravarty 2025.
