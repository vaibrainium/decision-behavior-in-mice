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
