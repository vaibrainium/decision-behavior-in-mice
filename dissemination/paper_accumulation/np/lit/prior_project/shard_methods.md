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
