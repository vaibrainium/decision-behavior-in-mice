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
