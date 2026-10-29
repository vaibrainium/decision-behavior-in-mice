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
