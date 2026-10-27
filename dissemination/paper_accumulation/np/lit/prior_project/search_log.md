# Literature search log

Search date: 2026-10-24

## Review scope

This is a reproducible narrative review supporting a neuroscience research article, not a systematic
review or meta-analysis. Searches used only general public topic terms; unpublished manuscript text,
data and figures were not sent to scholarly APIs.

## Inclusion criteria

- Empirical, computational or review work directly bearing on evidence accumulation, rapid
  forgetting/extrema alternatives, temporal weighting or brief evidence perturbations.
- Random-dot-motion, joint choice/response-time modelling, motion-energy reconstruction,
  cross-validation/predictive checks, or plausible sensory/urgency/response alternatives relevant to
  the locked spine.
- Human, non-human-primate or rodent work when the species and task are explicit.
- Published articles preferred; recent preprints retained only when no published version was found.

## Exclusion criteria

- Duplicate reports; preprints superseded by a published version.
- Papers without enough accessible abstract/full-text information to support a source-level note.
- Generic decision-making or motion-perception papers with no direct role in the framework, gap,
  methods or counter-evidence.
- Non-scholarly commentary and records whose identifiers or metadata could not be observed in a
  scholarly database.

## Combined shard logs

The four files below preserve every database, exact query, filter, hit count, screened count and kept
count. They are reproduced verbatim after this header.

---

## Shard record: framework

<!-- np-contract
stage: S2 ; section: literature_framework ; agent: np-librarian ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C003, C004, C005, C006, C008
numbers:
sources: stine2020differentiating, hyafil2023temporal, tsetsos2012timevarying, kiani2008bounded, huk2005neural, brunton2013rats, gold2007neural, bogacz2006physics, usher2001leaky, okazawa2018psychophysical, levi2018strategic, ratcliff2008diffusion
-->
# Literature shard: framework

Access date: 2026-10-24. This is a targeted narrative-paper search, not a systematic review.

## Scope and screening rules

Included primary studies, model papers and reviews that define evidence accumulation, compare it with rapid-forgetting/extrema or leaky alternatives, manipulate time-varying evidence, or explain how choices and response times constrain sequential-sampling models. Excluded clinical applications without a decision-mechanism contribution, unrelated multisensory integration, conference abstracts, editorials/corrections and papers whose relevance was only terminological.

PubMed returned 29 unique records across six bounded relevance-sorted searches. Four bounded OpenAlex searches returned 40 records; after normalized-title de-duplication across databases, 61 unique candidate titles/abstracts were screened. Twelve sources were retained. Full text was read for Stine et al. 2020, Hyafil et al. 2023, Tsetsos et al. 2012 and Kiani et al. 2008; the other eight were assessed from PubMed abstracts. Exact public API results are preserved in `search_framework_pubmed*.json`, `search_framework_openalex_*.json` and `search_framework_crossref_exact.json`.

## Query log

| # | Database | Exact query | Filters / order | Hits | Screened | Kept |
|---|---|---|---|---:|---:|---:|
| F1 | PubMed E-utilities | `"evidence accumulation"[Title/Abstract] AND "perceptual decision making"[Title/Abstract]` | relevance; first 8 | 193 | 8 | 0 |
| F2 | PubMed E-utilities | `("drift diffusion"[Title/Abstract] OR "sequential sampling"[Title/Abstract]) AND "motion discrimination"[Title/Abstract]` | relevance; first 8 | 21 | 8 | 0 |
| F3 | PubMed E-utilities | `("extrema detection"[Title/Abstract] OR "probability summation"[Title/Abstract]) AND perceptual decision[Title/Abstract]` | relevance; all 4 | 4 | 4 | 1 |
| F4 | PubMed E-utilities | `("temporal weighting"[Title/Abstract] OR "psychophysical kernel"[Title/Abstract]) AND ("motion discrimination"[Title/Abstract] OR "evidence accumulation"[Title/Abstract])` | relevance; all 1 | 1 | 1 | 1 |
| F5 | PubMed E-utilities | `(pulse[Title/Abstract] OR perturbation[Title/Abstract]) AND ("motion discrimination"[Title/Abstract] OR "random dot motion"[Title/Abstract]) AND decision[Title/Abstract]` | relevance; all 4 | 4 | 4 | 0 |
| F6 | PubMed E-utilities | `("leaky integration"[Title/Abstract] OR "leaky competing accumulator"[Title/Abstract]) AND perceptual decision[Title/Abstract]` | relevance; all 4 | 4 | 4 | 0 |
| F7 | OpenAlex | `search=evidence accumulation perceptual decision making` | relevance; first 10; bounded/partial | 33093 | 10 | 0 |
| F8 | OpenAlex | `search=extrema detection perceptual decision` | relevance; first 10; bounded/partial | 1232 | 10 | 2 |
| F9 | OpenAlex | `search=motion pulse evidence accumulation decision` | relevance; first 10; bounded/partial | 17163 | 10 | 2 |
| F10 | OpenAlex | `search=temporal weighting motion discrimination` | relevance; first 10; bounded/partial | 14058 | 10 | 1 |

The six broad PubMed result sets contained 29 unique records. OpenAlex searches were deliberately bounded and are partial; their very large hit counts are not coverage claims. The remaining retained papers entered by backward citation chasing from Stine, Hyafil, Tsetsos and Kiani, followed by exact DOI searches in PubMed/Crossref.

## Snowballing and exact-identifier checks

| Seed | Direction | Added keys |
|---|---|---|
| Stine et al. 2020 | backward / conceptual comparators | `gold2007neural`; `ratcliff2008diffusion`; `kiani2008bounded`; `brunton2013rats` |
| Hyafil et al. 2023 | backward / closest analysis precedents | `levi2018strategic`; `okazawa2018psychophysical`; `bogacz2006physics` |
| Tsetsos et al. 2012 | backward / competing models | `usher2001leaky`; `kiani2008bounded` |
| Kiani et al. 2008 | backward / pulse and neural integration precedent | `huk2005neural`; `gold2007neural` |

All twelve retained DOI strings resolved in either Crossref or PubMed during discovery, except that an initially guessed Kiani DOI resolved to an unrelated Neuron editorial and was rejected; the retained Kiani record uses DOI `10.1523/JNEUROSCI.4761-07.2008` seen in PubMed/PMC. Verification status remains blank for the independent auditor.

## Ten-line synthesis

1. Drift-diffusion and related bounded sequential-sampling models jointly constrain choices and response-time distributions; fitting only accuracy or a psychometric curve is not decisive.
2. Canonical neural and behavioural work used time-varying random-dot evidence and brief pulses to support persistent integration and bounded termination.
3. Kiani et al. reported weaker effects of later pulses, but Tsetsos et al. showed that primacy is compatible with both bounded diffusion and a leaky competing accumulator and depends on response pressure.
4. Stine et al. demonstrated formally and empirically that standard signatures of integration can be mimicked by non-integration strategies.
5. Hyafil et al. later found converging support for integration over extrema/snapshot models in discrete-sample datasets, while acknowledging that other non-integration implementations remain possible.
6. Brunton et al. illustrate how precisely controlled evidence events can separate noise in incoming evidence from noise in accumulator memory.
7. Psychophysical kernels are not pure sensory filters: decision bounds, integration and variable delays can distort them.
8. Temporal weighting is strategically adaptable, so primacy or recency alone does not identify leak, bound or memory duration.
9. The closest literature therefore supports comparing explicit model implementations and testing out-of-condition predictions rather than equating a temporal kernel with a mechanism.
10. No retained framework paper makes the exact combination of this study's claim: a control-selected model-and-input pipeline is challenged with randomized strong pulses while choices, response probabilities and response times are evaluated together.

## Alarming or framing-relevant evidence

- Hyafil et al. 2023 is a close prior study that explicitly favours integration over extrema and snapshot models across multiple datasets. The manuscript must distinguish its reaction-time/censoring likelihood and randomized out-of-condition pulse stress test from that paper's discrete-sample analyses.
- Tsetsos et al. 2012 directly undermines any inference from primacy alone to bounded accumulation; this supports the locked scope rather than the earlier poster claim.
- Kiani/Huk pulse findings were obtained in macaques with weak pulses and neural recordings; they do not guarantee that the present stronger mouse pulses enter the tested pipeline with the same dynamics.
- Okazawa and Levi show that temporal kernels can reflect decision processes and strategic adaptation, reinforcing the need to describe the observed curves as response-associated rather than as a direct integration kernel.

## Limitations

The search is targeted and bounded, not exhaustive. OpenAlex result counts are broad and its first pages were used only for discovery. Eight retained sources were read at abstract level only; any exact manuscript claim beyond the note must be checked against full text at synthesis or drafting. Recent-scoop coverage belongs primarily to the `gap_conflict` shard.


---

## Shard record: gap_conflict

<!-- np-contract
stage: S2 ; section: gap_conflict ; agent: np-librarian ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C004, C005, C006, C007, C009
numbers: none
sources: huk2005neural, kiani2008bounded, wong2007neural, zhou2009time, cisek2009decisions, tsetsos2012using, kiani2013integration, winkel2014early, carland2016evidence, yates2017functional, levi2018strategic, okazawa2018psychophysical, stine2020differentiating, kumano2024employment, chakravarty2025cross, parespujolras2025glimpses
-->

# Gap/conflict literature shard

Access date for all searches: **2026-10-24**. This is a targeted, single-reviewer search, not a systematic review. It used only general public topic queries and public scholarly APIs; no manuscript text, data or figures were sent externally.

## Inclusion and exclusion criteria

Included primary or mechanistic work that used brief/time-varying motion evidence to distinguish decision models, showed that sensory/response processes distort temporal weights, or directly tested integration against leaky/urgency/non-integration alternatives. Recent work was retained if it materially overlapped the pulse manipulation or its model-identification problem. Excluded clinical pulse stimulation, motor pulses without perceptual evidence, methods without a decision-model comparison, and discrete-pulse tasks that did not bear on transient-evidence generalization. Published versions were preferred; two 2025 preprints were retained and labelled because no version of record was found.

## Query log

| Database / tool | Exact query | Filters | Hits | Screened | Kept |
|---|---|---:|---:|---:|---:|
| PubMed E-utilities | `("motion pulse"[Title/Abstract] OR "motion pulses"[Title/Abstract]) AND (decision[Title/Abstract] OR perceptual[Title/Abstract])` | none | 8 | 8 | 3 |
| PubMed E-utilities | `("time-varying evidence"[Title/Abstract] OR "temporal weighting"[Title/Abstract]) AND ("evidence accumulation"[Title/Abstract] OR "decision making"[Title/Abstract])` | none | 20 | 20 | 3 |
| PubMed E-utilities | `("brief motion"[Title/Abstract] OR "motion perturbation"[Title/Abstract]) AND (decision[Title/Abstract] OR accumulation[Title/Abstract])` | none | 3 | 3 | 2 |
| PubMed E-utilities | exact-DOI OR query for the 13 published core candidates (DOIs listed in the candidate CSV) | metadata cross-check | 13 | 13 records checked | 13 |
| Europe PMC | `("evidence accumulation" AND ("motion pulse" OR "motion pulses")) AND PUB_YEAR:[2024 TO 2026]` | 2024-01-01--2026-12-31 | 6 | 6 | 1 |
| Europe PMC | `(SRC:"PPR" AND ("evidence accumulation") AND (pulse OR perturbation) AND decision) AND PUB_YEAR:[2024 TO 2026]` | preprints; 2024-01-01--2026-12-31 | 14 | 14 | 1 |
| OpenAlex | `filter=cites:W3018745833,from_publication_date:2024-10-24,to_publication_date:2026-10-24&search=motion pulse evidence accumulation` | forward citations of Stine 2020; last 24 months | 4 | 4 | 0 |
| eLife publisher metadata | `https://elifesciences.org/reviewed-preprints/105116` | reviewed preprint | 1 | 1 | 1 |
| Archived public-web discovery | 41 exact topic/title queries | targeted; no unpublished terms | ranked hits not reported | selectively screened | 12 core full texts |

The 41 archived query strings and access routes are preserved in `/src/dissemination/reports/pulse-thesis-searches-2026-10-23.json`. Across the four database discovery queries there were 45 query-level screening decisions after obvious cross-query duplicates; the target of 15--40 was exceeded slightly to complete the preprint sweep. Sixteen sources were kept. The exact-DOI PubMed query was metadata checking, not an independent discovery sample.

## Snowballing

Stine et al. (2020) was the central seed. Backward chaining retained Huk and Shadlen (2005), Kiani et al. (2008), Wong et al. (2007), Zhou et al. (2009), Tsetsos et al. (2012), Kiani et al. (2013), Yates et al. (2017), and Okazawa et al. (2018). Forward/topic chaining retained Kumano and Uka (2024) and the 2025 cross-species reviewed preprint. The targeted OpenAlex last-24-month forward-citation query returned four records, none of which directly tested held-out generalization of a control-fitted choice/RT model to brief strong motion pulses. The Europe PMC preprint sweep added Parés-Pujolràs et al. (2025).

## Ten-line synthesis

1. Brief motion perturbations have long been used to probe accumulation, but a pulse-associated choice or RT effect does not by itself identify integration (Huk and Shadlen, 2005; Stine et al., 2020).
2. The closest formal precedents show that time-varying perturbations can separate some integrate-to-threshold models only under suitable noise, timing and response assumptions (Zhou et al., 2009; Tsetsos et al., 2012).
3. Bounded commitment can itself make later evidence ineffective, so temporal weighting is not a direct readout of memory leak (Kiani et al., 2008; Okazawa et al., 2018).
4. Sensory dynamics can create apparent early weighting even with downstream integration, making the stimulus-to-evidence transformation part of the tested pipeline (Yates et al., 2017).
5. Task policy can reverse or reshape pulse efficacy and temporal weights, supporting genuine alternatives based on urgency, leak or strategic weighting (Cisek et al., 2009; Carland et al., 2016; Levi et al., 2018).
6. Conversely, early evidence can constrain later response-time distributions in ways that favour accumulation over simple urgency gating in some tasks (Winkel et al., 2014).
7. Retention across separated motion samples is established in other paradigms, but that manipulation is not equivalent to inferring retention from response latency after one pulse (Kiani et al., 2013).
8. Stine et al. (2020) is the closest identification warning: choice accuracy and kernels can be mimicked by non-integration strategies, whereas joint choice/RT constraints are more diagnostic.
9. Recent pulse work studies flexible/task-dependent weighting or repeated discrete evidence, not the present out-of-condition test of a control-fitted model-and-input pipeline (Kumano and Uka, 2024; Chakravarty et al., 2025; Parés-Pujolràs et al., 2025).
10. Scoop/conflict verdict: no published or preprint record found in the 2024-10-24--2026-10-24 sweep closes the paper's gap; the defensible novelty is predictive generalization failure, not a claim that pulses uniquely prove or disprove accumulation.

## Closest-paper comparison and disagreements

| Source | Overlap | Important difference / conflict |
|---|---|---|
| Stine et al. (2020) | Explicit integration-versus-non-integration identification using choice and RT | Demonstrates model mimicry; does not test a separately fitted control model on randomized strong pulse trials. |
| Huk and Shadlen (2005) | Brief motion pulses, choices, RT and bounded accumulation | Includes macaque LIP physiology; pulse effects therefore have neural evidence unavailable here. |
| Zhou et al. (2009) | Perturbation-based discrimination among RT decision models | Primarily a theoretical/simulation protocol; separability degrades with noise and delays. |
| Tsetsos et al. (2012) | Time-varying evidence tests diffusion versus leaky competition | Temporal weights vary by conditions and individuals; primacy does not uniquely imply one mechanism. |
| Carland et al. (2016) | Brief motion pulses used to oppose perfect integration and strong leak/urgency | Their pulse efficacy changed with instructed/induced decision policy, showing that a pulse result can conflict across task contexts. |

The literature therefore contains a real mechanistic disagreement rather than a settled benchmark: some tasks support bounded integration or retention, whereas others favour leaky/urgency-like processing. This strengthens the paper's decision to report the tested implementation and its failed pulse generalization without turning that failure into a universal anti-accumulation claim.


---

## Shard record: methods

<!-- np-contract
stage: S2 ; section: literature_methods ; agent: np-librarian ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C002, C003, C004, C005, C006, C009
numbers:
sources: adelson1985spatiotemporal, roitman2002response, palmer2005effect, huk2005neural, ditterich2006evidence, ratcliff2008diffusion, kiani2008bounded, drugowitsch2012cost, tsetsos2012timevarying, wiecki2013hddm, kiani2013integration, carland2016evidence, stine2020differentiating
-->
# Literature shard: methods

## Scope and screening criteria

**Question.** Which primary precedents support the random-dot motion task, motion-energy input reconstruction, joint choice/response-time modelling, model discrimination with time-varying evidence, and brief motion-pulse perturbations used in this paper?

**Included:** primary methods or empirical papers using random-dot direction discrimination, explicit speed-and-accuracy/response-time modelling, motion-energy filters, time-varying or pulsed evidence, or direct tests of integration versus non-integration. Reviews were retained only when they define the diffusion-model observables or a widely used fitting implementation. Human, macaque and rodent work was eligible, but species and response modality had to remain explicit.

**Excluded:** studies without a perceptual-decision or motion-analysis method relevant to the spine; clinical applications that merely reused a diffusion package; engineering motion filters without a perceptual link; confidence-only extensions; neural papers without a usable behavioural/task precedent; preprints when a journal version was available.

## Query log

Access date for every query: 2026-10-24. PubMed searches used NCBI E-utilities through `search_pubmed.py`, relevance/default ordering, first 20 records maximum. OpenAlex searches used `search_openalex.py`, relevance ordering. Hits are database totals; screened is the bounded returned set, so the two broad OpenAlex totals do not imply exhaustive screening.

| # | Database / tool | Exact query | Filters | Hits | Screened | Kept |
|---|---|---|---|---:|---:|---:|
| M1 | PubMed | `random dot motion reaction time decision making` | none; limit 20 | 64 | 20 | 3 |
| M2 | PubMed | `motion energy model visual motion spatiotemporal filters` | none; limit 20 | 32 | 20 | 0 |
| M3 | PubMed | `brief motion pulse perceptual decision evidence integration` | none; limit 20 | 3 | 3 | 3 |
| M4 | PubMed | `drift diffusion model choice response time parameter recovery` | none; limit 20 | 11 | 11 | 1 |
| M5 | PubMed | `hierarchical drift diffusion model Bayesian choice reaction time` | none; limit 20 | 13 | 13 | 1 |
| M6 | PubMed | `psychophysical reverse correlation motion evidence decision` | none; limit 20 | 5 | 5 | 1 |
| M7 | PubMed | `perceptual decision model cross validation posterior predictive choice response time` | none; limit 20 | 0 | 0 | 0 |
| M8 | OpenAlex | `random dot motion perceptual decision brief pulse` | none; limit 20 | 2,637 | 20 | 4 |
| M9 | OpenAlex | `motion energy model visual motion spatiotemporal filters` | none; limit 20 | 21,925 | 20 | 0 |
| M10 | OpenAlex | `Spatiotemporal energy models for the perception of motion` | none; limit 10 | 21,137 | 10 | 1 |
| M11 | PubMed targeted retrieval | `12417672 OR 16097871 OR 16280581 OR 17229111 OR 18085991 OR 18354005 OR 22423085 OR 22701399 OR 23935581 OR 24133253 OR 26609110 OR 32338595 [PMID]` | exact identifiers; records fetched individually | 12 | 12 | 12 |

Across discovery searches M1–M10, 122 returned rows were screened; M11 supplied the authoritative abstracts and metadata for 12 retained PubMed records. After DOI/title deduplication, 13 unique sources were kept. Candidate metadata remain unverified pending the S2 integrity audit.

## Kept methods precedents

| Key | Species / preparation | Method contribution | Why retained |
|---|---|---|---|
| `adelson1985spatiotemporal` | general vision model | Quadrature spatiotemporal filters, squared-and-summed motion energy and opponent stage | Foundational definition of the reconstructed motion-energy input. |
| `roitman2002response` | rhesus macaque | Reaction-time random-dot direction task measuring choice, RT and LIP activity | Direct task precedent for joint speed/accuracy constraints. |
| `palmer2005effect` | humans | Psychometric and chronometric functions under varying motion strength | Behavioural precedent for modelling choice and RT jointly. |
| `huk2005neural` | rhesus macaque | Brief motion pulses at multiple times during reaction-time random-dot decisions | Closest primary methods precedent for pulse effects on choices and RT. |
| `ditterich2006evidence` | humans plus macaque-recording comparison | Time-varying diffusion/urgency accounts of reaction-time motion decisions | Precedent for allowing decision policy to vary with time. |
| `ratcliff2008diffusion` | humans; review with demonstrations | Diffusion model constraining accuracy, mean RT and RT distributions | Defines why joint choice/RT fits are more restrictive than psychometrics alone. |
| `kiani2008bounded` | rhesus macaque | Fixed-duration random-dot decisions and reverse-correlation/pulse logic | Precedent for bounded integration and temporal weighting. |
| `drugowitsch2012cost` | two macaques and six humans | Diffusion modelling plus dynamic programming in reaction-time motion decisions | Precedent for time-dependent stopping policies and cost-of-time interpretations. |
| `tsetsos2012timevarying` | humans | Pulse and time-varying-evidence experiments comparing bounded diffusion with LCA | Demonstrates that temporal weighting and primacy are not model-unique. |
| `wiecki2013hddm` | methodological demonstrations | Hierarchical Bayesian diffusion fitting and recovery | Widely used parameter-estimation and recovery precedent; not the software used here. |
| `kiani2013integration` | humans | One- versus two-pulse random-dot task with variable temporal gaps | Precedent for testing retention across discrete evidence epochs. |
| `carland2016evidence` | humans | Brief pulses under different decision policies; low-pass-plus-urgency alternative | Direct counter-precedent to perfect-integration interpretation. |
| `stine2020differentiating` | humans plus simulations | Task-design/model comparisons separating integration from extrema/non-integration | Closest methods precedent for the paper's relative strategy test. |

## Summary

The method chain is well precedented: motion-energy filtering (`adelson1985spatiotemporal`), random-dot psychophysics that jointly constrains choice and RT (`roitman2002response`; `palmer2005effect`), diffusion modelling of full behavioural distributions (`ratcliff2008diffusion`), brief-pulse and time-varying-evidence perturbations (`huk2005neural`; `tsetsos2012timevarying`; `carland2016evidence`), and explicit integration-versus-non-integration discrimination (`stine2020differentiating`). The literature also warns against treating temporal pulse weighting as unique evidence for a specific accumulator: leaky competition, urgency and task policy can yield similar signatures.

## Coverage gaps

- No retained paper directly validates this project's exact likelihood treatment of responses after the fixed 5 s analysis window or unresponded trials. The manuscript should describe that likelihood from code and simulation, not imply that it is inherited from these precedents.
- No retained precedent validates reconstruction of actual display frames from task code. `adelson1985spatiotemporal` supports the filter computation, not the replay's physical fidelity.
- The closest pulse precedents are human or macaque studies. They motivate the manipulation but do not establish equivalent pulse processing in mice.
- Cross-validation and out-of-condition prediction are standard statistical ideas, but the bounded search did not identify a single neuroscience paper that exactly matches this paper's control-fit/pulse-test pipeline. That absence is a framing opportunity, not evidence of uniqueness.

## Reproducibility

Commands used:

```text
python3 .claude/skills/citation-management/scripts/search_pubmed.py '<query>' --limit 20 -o <output.json>
python3 .claude/skills/citation-management/scripts/search_openalex.py '<query>' --limit 20 -o <output.json>
```

Temporary normalized result files were written under `/tmp/np_methods_*.json` and are not part of the paper record. The exact queries and counts above are the durable provenance.


---

## Shard record: counter

<!-- np-contract
stage: S2 ; section: literature_counter ; agent: np-librarian ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C003, C004, C005, C006, C008, C009
numbers:
sources: stine2020differentiating, hyafil2023temporal, tsetsos2012timevarying, okazawa2018psychophysical, levi2018strategic, cisek2009decisions, thura2012urgency, carland2016evidence, hawkins2015revisiting, hawkins2015discriminating, evans2017computations, yates2017functional, wong2007neural, zhou2009timevarying, luken2025parameter
-->
# Literature shard: counter-evidence

Access date: 2026-10-24. This is a targeted narrative-paper search, not a systematic review.

## Scope and screening rules

Included primary studies, simulations and model-comparison papers that challenge unique accumulation, support rapid-forgetting/urgency or sensory-filter alternatives, expose non-identifiability of temporal kernels or evidence-accumulation parameters, or show conditions in which perturbations fail to distinguish candidate mechanisms. Also included strong evidence against the alternatives so that the counter search does not cherry-pick. Excluded non-perceptual uses of drift/diffusion, clinical or engineering applications without a decision-mechanism contribution, and papers whose relevance was only terminological.

Six bounded PubMed searches returned 51 total hits and 30 unique first-page candidates. Four bounded OpenAlex searches returned 16,294 total hits because the search terms are broad; only a prespecified first-page subset was used for discovery. After title normalization there were 66 unique retrieved records. Thirty PubMed title/abstract records and ten nonduplicative OpenAlex records were formally screened, for 40 screened candidates. Fifteen sources were retained, including five shared framework papers whose counter-evidence is essential. Full text or full publisher pages were available for Stine, Tsetsos, Okazawa, Cisek, Carland, Hawkins (both papers), Evans, Yates, Wong and Zhou; Hyafil, Levi, Thura and Lüken were assessed from database abstracts or publisher summaries. Raw API records are preserved in `np/lit/raw_counter/`.

## Query log

| # | Database | Exact query | Filters / order | Hits | Screened | Kept |
|---|---|---|---|---:|---:|---:|
| C1 | PubMed E-utilities | `("extrema detection"[Title/Abstract] OR "probability summation"[Title/Abstract] OR "snapshot strategy"[Title/Abstract]) AND ("perceptual decision"[Title/Abstract] OR "evidence accumulation"[Title/Abstract])` | relevance; all 5 | 5 | 5 | 1 |
| C2 | PubMed E-utilities | `("psychophysical kernel"[Title/Abstract] OR "temporal weighting"[Title/Abstract]) AND (bound[Title/Abstract] OR delay[Title/Abstract] OR strategy[Title/Abstract]) AND decision[Title/Abstract]` | relevance; all 6 | 6 | 6 | 1 |
| C3 | PubMed E-utilities | `("urgency gating"[Title/Abstract] OR urgency[Title/Abstract]) AND ("perceptual decision"[Title/Abstract] OR "motion discrimination"[Title/Abstract])` | relevance; first 8 | 27 | 8 | 1 |
| C4 | PubMed E-utilities | `(adaptation[Title/Abstract] OR persistence[Title/Abstract] OR latency[Title/Abstract]) AND ("motion pulse"[Title/Abstract] OR "brief motion"[Title/Abstract]) AND decision[Title/Abstract]` | relevance; no records | 0 | 0 | 0 |
| C5 | PubMed E-utilities | `("non-decision time"[Title/Abstract] OR motor[Title/Abstract] OR response[Title/Abstract]) AND "evidence accumulation"[Title/Abstract] AND perturbation[Title/Abstract]` | relevance; all 3 | 3 | 3 | 0 |
| C6 | PubMed E-utilities | `("model mimicry"[Title/Abstract] OR "model identifiability"[Title/Abstract] OR "model selection"[Title/Abstract]) AND ("drift diffusion"[Title/Abstract] OR "sequential sampling"[Title/Abstract])` | relevance; first 8 | 10 | 8 | 0 |
| C7 | OpenAlex | `search=urgency gating evidence accumulation motion decision` | relevance; first 10 retrieved, bounded/partial | 4,713 | 4 | 4 |
| C8 | OpenAlex | `search=psychophysical kernel sensory decision process` | relevance; first 10 retrieved, bounded/partial | 3,709 | 2 | 1 |
| C9 | OpenAlex | `search=motion pulse perceptual decision sensory adaptation` | relevance; first 10 retrieved, bounded/partial | 4,705 | 2 | 2 |
| C10 | OpenAlex | `search=model identifiability drift diffusion evidence accumulation` | relevance; first 10 retrieved, bounded/partial | 3,167 | 2 | 1 |

The OpenAlex hit counts are broad index counts, not coverage claims. The formal OpenAlex screen stopped after ten nonduplicative records; the remaining retrieved records are retained only as a reproducibility record.

## Snowballing and retained shared sources

| Seed | Direction / purpose | Added or retained keys |
|---|---|---|
| Stine et al. 2020 | backward: non-integration and urgency alternatives | `cisek2009decisions`; `thura2012urgency`; `hawkins2015discriminating`; `evans2017computations` |
| Huk & Shadlen 2005 / Wong et al. 2007 | pulse-model counterexamples | `wong2007neural`; `zhou2009timevarying`; `yates2017functional`; `carland2016evidence` |
| Tsetsos et al. 2012 / Levi et al. 2018 | temporal-kernel ambiguity | `okazawa2018psychophysical`; `levi2018strategic`; `tsetsos2012timevarying` |
| Recent model-identifiability sweep | 2024–2026 countercheck | `luken2025parameter` |

Hyafil et al. 2023 was deliberately retained as evidence against H2: a counter-evidence shard must include strong studies that favor accumulation rather than collect only alternatives.

## Ten-line synthesis

1. Standard choice and response-time patterns do not uniquely identify integration: extrema, snapshot and urgency-gating strategies can mimic important signatures under common task designs.
2. Cisek, Thura and Carland show that changing evidence or decision policy can reveal short-memory/urgency accounts that are difficult to distinguish under constant evidence.
3. Carland is the closest counterexample: the effect of brief motion pulses changed when subjects altered decision policy, so pulse efficacy is not a context-free assay of retained evidence.
4. The counter-literature is not one-sided: Hawkins and Evans found that carefully matched data and model comparisons often favor fixed-bound diffusion over urgency gating.
5. Temporal weighting is jointly shaped by sensory dynamics, decision bounds, delays and strategy; early or late weighting alone cannot locate the mechanism.
6. Yates shows that early weighting can already exist in sensory-area responses and propagate downstream even under ideal integration of the modeled sensory input.
7. Recurrent-attractor, diffusion, leaky and urgency models can all generate persistent or timing-dependent pulse effects under some conditions.
8. Zhou shows that perturbations distinguish candidate dynamics only in specified signal-to-noise regimes and may fail to separate constant- and time-varying-drift models.
9. Lüken demonstrates that even within evidence-accumulation families, parameter identifiability worsens with low error rates and limited trials; fitted parameters need recovery evidence.
10. These results support the locked spine: the present pulse mismatch constrains the tested model-and-input pipelines but cannot by itself select a unique sensory, decision or response mechanism.

## Strongest counter-arguments to the paper

- **Alternative to H1:** A short sensory filter combined with urgency can reproduce ramp-like behaviour and some pulse effects without long-lived evidence storage (`cisek2009decisions`, `thura2012urgency`, `carland2016evidence`).
- **Alternative to a decision-level pulse interpretation:** Sensory dynamics can create time-dependent behavioural weighting before downstream accumulation (`yates2017functional`), while bounds and delays distort reverse-correlation kernels (`okazawa2018psychophysical`).
- **Alternative to pulse-based identification:** Perturbation effects are discriminating only under adequate signal-to-noise and candidate separation (`zhou2009timevarying`); the present failed gates and low simulation sensitivity therefore matter scientifically.
- **Evidence against the alternatives:** Controlled comparisons can favor diffusion over urgency (`hawkins2015revisiting`, `hawkins2015discriminating`, `evans2017computations`) and multi-dataset analysis can favor integration over extrema/snapshots (`hyafil2023temporal`).
- **General identifiability warning:** Model components and parameter values can trade off even when aggregate fit is good (`stine2020differentiating`, `luken2025parameter`).

## Implications for the locked spine

No spine change is required. The literature strengthens the choice to call Figure 3 a relative comparison among tested implementations and Figure 5 an out-of-condition failure of a model-and-input pipeline. It argues against describing response-aligned pulse timing as direct evidence of sensory persistence, leak, accumulation or motor delay. The Discussion should compare the present result directly with Carland 2016, Hawkins 2015, Evans 2017, Yates 2017 and Zhou 2009, because together they show why a pulse can constrain models without uniquely identifying a mechanism.

## Limitations

This was a bounded single-reviewer search. The PubMed helper could not run because the installed environment lacks its declared `requests` dependency; no package was installed, and the documented public E-utilities endpoints were queried directly. One zero-result query illustrates vocabulary sensitivity rather than absence of literature. Four retained records were not read beyond abstracts or publisher summaries and must not support claims more specific than their notes. DOI/PMID resolution and retraction checks remain for the independent integrity auditor.



---

## Challenge-correction addendum

<!-- np-contract
stage: S2 ; section: gap_addendum ; agent: np-librarian ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C010, C011, C012, C014
numbers: none
sources: stine2023termination, steinemann2024direct, parespujolras2026glimpses
-->

# Gap literature addendum: three challenge records

Access date for every lookup: **2026-10-24**. Only exact public identifiers and public primary-source records were queried; no unpublished project text was submitted.

## Lookup log

| # | Public source | Exact lookup | Filter | Hits | Screened | Kept |
|---|---|---|---|---:|---:|---:|
| A1 | PubMed E-utilities | `10.1016/j.neuron.2023.05.028[doi]` | exact DOI | 1 | 1 | 1 |
| A2 | Europe PMC full-text API | `PMC10565788/fullTextXML` | Stine et al. 2023 primary full text | 1 | 1 | 1 |
| A3 | Crossref REST | `works/10.7554/eLife.90859.3` | exact versioned DOI | 1 | 1 | 1 |
| A4 | PubMed E-utilities | `PMID 39422555` | exact PMID | 1 | 1 | 1 |
| A5 | Europe PMC full-text API | `PMC11488853/fullTextXML` | Steinemann et al. 2024 Version of Record | 1 | 1 | 1 |
| A6 | eLife official record | `reviewed-preprints/107980v3` and `reviewed-preprints/107980v3.xml` | exact v3 DOI `10.7554/eLife.107980.3` | 1 | 1 | 1 |

## Fit-versus-test comparison

| Record | Fit condition | Pulse condition / strength | Outcomes modelled | Were pulse predictions genuinely held out? |
|---|---|---|---|---|
| Stine et al. 2023 | Bounded accumulation fit to monkey choice and mean RT; the Figure 1/S1 fit maximized a combined likelihood for choice data and mean RTs. The text does not report a no-pulse-only training split. | Interleaved on about half of trials; 100 ms; randomly signed and timed; 4.0% coherence in monkey M and 3.2% in monkey J; onset 0.1–0.8 s. | Choice and mean RT in the parsimonious behavioural fit; pulse effects on choice, RT and LIP/SC activity were also analysed. | **No.** Pulses were randomized evidence manipulations and supplied empirical support, but the paper does not report fitting on no-pulse controls and prospectively evaluating a frozen model on pulse trials. |
| Steinemann et al. 2024 | A racing bounded drift-diffusion model was fit per session to choice–RT data; neural coding directions/decoders were analysed with cross-validation for neural questions. | Same macaque dataset/manipulation: 100 ms on about half of trials; randomly timed 0.1–0.8 s; ±3.2% or 4.0% coherence for monkeys J and M. | Behavioural choice and RT; single-trial LIP signals, neural leverage on choice and RT. Pulse choice/RT effects are shown descriptively in Figure 1—figure supplement 1. | **No.** Neural decoder cross-validation is not a held-out pulse-generalization test, and the article does not report a control-only behavioural fit evaluated on pulse trials. |
| Parés-Pujolràs et al. 2026 v3 | Three-parameter bounded model fit separately by experiment to grand-averaged accuracy for all single- and two-pulse conditions; alternative models were likewise fit to all accuracy conditions. | Human intermittent-evidence task; one or two 200 ms motion epochs separated by specified gaps; individualised low/high coherences (group means 19.82–44.73% across experiment/level). | Accuracy only in the fitted decision models; CPP and motor-beta patterns were simulated from the accuracy-fitted model and compared qualitatively with EEG. RT was not the modelled decision outcome. | **No.** The pulse conditions constituted the fitting dataset; EEG simulations were not an untouched pulse test. |

## Addendum conclusion

Stine et al. and Steinemann et al. are the closest positive precedents because randomized weak pulses accompanied bounded choice/RT fits and macaque neural evidence for persistent accumulation. They materially narrow novelty, but do not perform the paper's control-only-fit to separately evaluated strong-pulse transfer test. Parés-Pujolràs v3 is a relevant counter/comparator because it localizes transient versus sustained signals and now compares bounded with reweighting alternatives; all decision models were fit to the pulse-task accuracy data, so it also does not close the predictive-generalization gap. These distinctions support a preparation- and pipeline-specific claim, not priority for motion pulses or a universal failure of accumulation.



---

## Mouse dynamic-visual novelty fact-check

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


---

## Independent mouse-novelty challenge

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

