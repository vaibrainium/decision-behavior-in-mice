<!-- np-contract
stage: S2 ; section: mouse_dynamic_visual_audit ; agent: np-integrity-auditor ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C003, C004, C005, C006, C009
numbers: none
sources: douglas2006motion, stirman2016touchscreen, pinto2018visualpulses, marques2018mousev1, samonds2018motion, odoemene2018visual, koay2020amplitude, you2022dynamics, caballero2022rt, chakravarty2025cross
-->
# Mouse dynamic-visual candidate integrity audit

VERDICT: **PASS after corrections**  
Access date: **2026-10-24**  
Mode: **sources plus exact-precedent classification**

## Counts

| Check | Count |
|---|---:|
| Candidate rows checked | 10 |
| DOI records resolved | 10/10 |
| Available PMID records resolved | 9/9 |
| Current rows verified | 10 |
| Current rows failed | 0 |
| Retracted or withdrawn | 0 |
| Deleted as nonexistent | 0 |

All ten DOIs resolved through Crossref. The nine journal records with PMIDs were also checked in PubMed; title,
authors, year and venue agree after the corrections below. Crossref `relation`/`update-to` metadata contained no
retraction or withdrawal relation, and none of the nine PubMed records had a retraction or withdrawal publication
type. The eLife reviewed-preprint record was additionally checked against the official v1 full text and showed no
withdrawal notice. The candidate CSV now records `verified=yes` with dated provenance for every row.

## Metadata corrections

1. `marques2018mousev1` originally combined the correct title and DOI with an incorrect author list. The row now
   carries the Crossref/PubMed list: Marques, Summers, Fioreze, Fridman, Dias, Feller and Petreanu.
2. `you2022dynamics` originally listed PMID `35273103`, which resolves to an unrelated cancer-immunology erratum.
   The correct PMID is `35228308`; the first author's indexed name is Wen-Kai You (游文愷), not Wen-Ke You.
3. Abbreviated author fields for `samonds2018motion` and `koay2020amplitude`, and middle initials for
   `stirman2016touchscreen`, were expanded to the resolved records. These were normalization fixes, not identity
   failures.

## Independent classification audit

| Source | Dynamics and perturbation | Choice/response-time analysis | Frozen pulse prediction? | Audit |
|---|---|---|---|---|
| `douglas2006motion` | Continuous RDK; coherence/frame parameters varied across conditions; no brief signed pulse | Coherence-threshold psychophysics | No | Confirmed from PubMed abstract |
| `stirman2016touchscreen` | Continuous touchscreen RDK; coherence and dot parameters varied; no embedded pulse | Weibull psychometric fit and response-time summaries, not a joint generative model | No | Corrected the table from an unqualified `no` to acknowledge RT summaries; PMC Abstract, Methods 2.3–2.7, Figs. 3–5 |
| `pinto2018visualpulses` | Randomly located 200-ms towers are the discrete evidence stream, not a perturbation of continuous RDK | Logistic and accumulation models for choices; no joint free-response RT likelihood | No | Confirmed; PMC Abstract, accumulating-towers Methods, Figs. 3, 4, 6 and 7 |
| `marques2018mousev1` | Continuous fixed-duration RDK; no embedded signed motion pulse | Choice psychometrics and supplementary reaction-time summaries, not a joint generative RT model | No | Corrected to acknowledge RT summaries; PMC Abstract, Results Figs. 1–2 and Fig. S1 |
| `samonds2018motion` | Continuous RDK with a prolonged (at least 10-s) directional adapter before a 4-s test, not a brief pulse | Lick/coherence sigmoid fits and lick-latency curves, not a joint generative model | No | Confirmed; PMC Methods and Results Figs. 4–8 |
| `odoemene2018visual` | Stochastic 20-ms flashes form a fixed 1-s evidence sequence; 5% of trials included randomized brightness manipulations | Psychometric and temporal-kernel analyses; no joint RT model | No | Corrected: a separate randomized brightness manipulation exists, but it is not a signed motion pulse; PMC Abstract, behavioral Methods and Figs. 1–3 |
| `koay2020amplitude` | Randomly located 200-ms towers are the discrete evidence stream | Behavioural choice weighting plus neural impulse-response models; no joint behavioural RT model | No | Confirmed; PMC Abstract, behavioural-task Methods and Fig. 1 |
| `you2022dynamics` | Sustained oriented grating (0.1–3 s or until response), not RDK; no signed pulse | Conditional-accuracy analysis **and a DDM fit to correct/incorrect RT distributions** | No | Corrected the false `no_DDM` classification; PMC Abstract, DDM Methods and Figs. 1–5 |
| `caballero2022rt` | Sustained visual discrimination with contrast and pharmacological conditions; no RDK pulse stream | DDM fit to mouse choices and escape-latency distributions | No | Confirmed at abstract level; PubMed abstract |
| `chakravarty2025cross` | Free-response streams of repeated discrete light pulses continuing until choice; no separate held-out perturbation | Fixed/collapsing/urgency DDMs and GLM/GLM-HMM analyses including choices and RTs | No | Confirmed from official eLife reviewed-preprint v1 Abstract, Results and Methods |

The classification corrections are material to broad novelty language: response-time summaries already appear in
mouse RDK studies, DDM fitting appears in both You and Mysore (2022) and Caballero et al. (2022), and Odoemene et
al. (2018) included randomized visual-brightness manipulation trials. None is an exact precedent for the conjunction
at issue.

## Duplicate status

`chakravarty2025cross` is the same source key and DOI already present and verified in
`np/ledger/sources.csv`. It is one of the ten candidate classifications audited here but must **not** be counted as an
additional authoritative-ledger source. No authoritative-ledger row was edited.

## Narrow claim verdict

**Survives this ten-source audit, with bounded-search wording.** None of the ten verified candidates combines all of:

1. continuous noisy random-dot motion;
2. a separately randomized strong signed motion pulse;
3. a model fitted only to unperturbed/control trials; and
4. frozen prediction of pulse-trial choices, response times and response/no-response outcomes.

The closest partial precedents divide across different axes: Marques provides continuous mouse RDK; Samonds adds a
prolonged adapter; Odoemene adds randomized brightness manipulation to a discrete-flash task; You, Caballero and
Chakravarty provide response-time/DDM precedents; Pinto, Koay and Chakravarty provide discrete pulse evidence. None
tests control-to-pulse predictive transfer. The defensible wording remains “in a bounded search, we found no prior
mouse study combining ...”, not “first” or a universal absence claim. A fresh pre-submission search and human field
check remain necessary because an absence claim cannot be established from ten retained records.

## Verification sources and method

- Crossref Works API, exact DOI retrieval for all ten records, accessed 2026-10-24.
- PubMed ESummary/EFetch, exact PMID and DOI/title retrieval for the nine indexed journal articles, accessed
  2026-10-24.
- PubMed Central full text for Stirman, Pinto, Marques, Samonds, Odoemene, Koay and You; official eLife JATS full
  text for Chakravarty; PubMed abstracts for Douglas and Caballero.
- Retraction screen: Crossref relation/update metadata, PubMed publication types where available, and the official
  eLife reviewed-preprint page for the non-PubMed record.
