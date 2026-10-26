<!-- np-contract
stage: S3 ; section: discussion ; agent: np-architect ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C008, C013, C014
numbers:
sources: carland2016evidence, hawkins2015discriminating, okazawa2018psychophysical, steinemann2024direct, stine2020differentiating, stine2023termination, tsetsos2012timevarying, yates2017functional, zhou2009time
-->
# Brief: discussion

Purpose (one sentence): Explain why relative control-model support and failed pulse transfer are jointly informative while keeping the missing sensory, decision or response mechanism unresolved.

Venue constraints: words 1,200; present tense for implications and established literature, past tense for the study's findings; six paragraphs in D1–D5 plus conclusion order; no new results or statistics; limitations stated once with a concrete remedy.

Reader question this section answers: What has this study established about accumulation and pulse processing, what remains unidentified, and what experiment would resolve the mismatch?

Paragraph plan:

| # | Move (from section-specs) | Content | Claims | Numbers | Sources | Figure |
|---|---|---|---|---|---|---|
| 1 | D1 plain answer | Controls favoured the tested accumulator, pulses redirected behaviour, and neither pipeline transferred; separate stable behavioural effects from unresolved process localization. | C008; synthesis cross-reference C001 | — | — | 3–5; S6 |
| 2 | D2 literature/conflict | Compare integration-favouring work, urgency/leak/policy counterexamples and recent positive macaque pulse/neural findings; explain dataset-specific separability. | C013 | — | stine2020differentiating; hawkins2015discriminating; carland2016evidence; tsetsos2012timevarying; zhou2009time; stine2023termination; steinemann2024direct | 3, 5, S6 |
| 3 | D3 alternatives/limitations | Sensory dynamics as a concrete alternative, then replay fidelity, input geometry/filtering, control misfit, legacy labels, sparse RT terms, simulation noise, recovery/bounds and rig confounding; pair each with what remains valid and its remedy. | C014 | — | yates2017functional; okazawa2018psychophysical | 2–5; S2–S5 |
| 4 | D4 cannot speak to | No unique proof of accumulation, primacy/recency, memory time constant, processing-stage localization, site biology or cohort-wide gain tradeoff. | cross-reference C007, C008, C009 | — | — | 5; S6 |
| 5 | D5 implications/next experiment | Advocate out-of-condition prediction; propose display-verified, synchronized, multi-amplitude/timing pulses plus an independent retention/gap manipulation, optionally combined with neural localization. | — | — | — | prospective |
| 6 | Conclusion | Re-state that model selection under controls and transfer to strong transients are distinct empirical demands; the perturbation revealed a concrete pipeline limitation. | synthesis cross-reference C001, C008 | — | — | 3–5 |

Promises this section creates: One actionable next experiment only; it must target the identified ambiguity rather than promise a generic larger dataset.

Promises it must deliver: Every Introduction promise and Results-created interpretive debt; direct engagement with both integration-favouring and counterexample literature; explicit reasons the behavioural effect survives model/input uncertainty.

Must include: C008 as the opening scope boundary; C013 with regime-specific separability; C014 with sensory-stage inheritance; the fact that the confirmatory timing test was withheld; a remedy for each major limitation.

Must not include: P values or detailed result repetition; the tau-p pilot as evidence; a first-in-mice claim; claims of primacy, unique accumulation, integration time, sensory persistence or a motor mechanism; vague “more work is needed” language.

Known risks / reviewer bait: Calling the control winner “the accumulator” can overgeneralize beyond the tested pair; the macaque literature can make the mouse mismatch appear contradictory unless preparation/pipeline differences are explicit; a long limitation list can obscure the stable randomized behavioural result.

Acceptance criteria (the reviewer instantiates these at commit time):

- D1 answers the final Introduction paragraph in plain language and contains no p values.
- C008, C013 and C014 each appear once as primary claims with appropriate evidence boundaries.
- Both supporting and conflicting literature are compared rather than listed.
- Each limitation says what remains supported and what specific test would resolve it.
- The conclusion matches the locked thesis without adding a mechanism claim.
