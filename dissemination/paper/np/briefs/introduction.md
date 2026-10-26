<!-- np-contract
stage: S3 ; section: introduction ; agent: np-architect ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C010, C011, C012, C015, C019, C020, C021
numbers:
sources: caballero2022rt, carland2016evidence, cisek2009decisions, douglas2006motion, huk2005neural, hyafil2023temporal, kiani2008bounded, koay2020amplitude, marques2018mousev1, odoemene2018visual, okazawa2018psychophysical, palmer2005effect, pinto2018visualpulses, ratcliff2008diffusion, samonds2018motion, steinemann2024direct, stine2020differentiating, stine2023termination, stirman2016touchscreen, tsetsos2012timevarying, winkel2014early, you2022dynamics
-->
# Brief: introduction

Purpose (one sentence): Frame joint held-out prediction and randomized pulses as complementary tests of a model-and-input pipeline, while locating the mouse contribution within established RDK, discrete-evidence and response-time modelling literatures.

Venue constraints: words 700; 4 paragraphs; present tense for established knowledge, past tense only for the study preview; eLife-style 2–4-sentence result preview in the final paragraph; only verified source keys; no numerical results.

Reader question this section answers: Why is an out-of-condition pulse test needed after fitting choices and response times, and what is specifically new without claiming broad mouse novelty?

Paragraph plan:

| # | Move (from section-specs) | Content | Claims | Numbers | Sources | Figure |
|---|---|---|---|---|---|---|
| 1 | Opening/framework and conflict | Evidence accumulation is useful but familiar accuracy/weighting signatures are shared by tested alternatives; joint choice/RT distributions add constraints; discrete-sample comparisons favour integration only within their tested sets. | C010, C011, C015 | — | stine2020differentiating; tsetsos2012timevarying; cisek2009decisions; okazawa2018psychophysical; ratcliff2008diffusion; palmer2005effect; winkel2014early; hyafil2023temporal | 3 |
| 2 | Known plus untested assumption | Pulses can affect choice and RT, but timing, commitment and policy alter their efficacy; motivate prospective transfer from control fits rather than treating pulse timing as a mechanism fingerprint. | C012 | — | huk2005neural; kiani2008bounded; tsetsos2012timevarying; carland2016evidence; stine2023termination; steinemann2024direct | 4–5 |
| 3 | Preparation-specific gap | Mouse continuous RDK, discrete visual accumulation and visual choice/RT diffusion modelling each exist; only the exact conjunction was not found in the bounded search. | C019, C020, C021 | — | douglas2006motion; stirman2016touchscreen; marques2018mousev1; samonds2018motion; pinto2018visualpulses; odoemene2018visual; koay2020amplitude; you2022dynamics; caballero2022rt | 1 |
| 4 | Competing hypotheses; Here we | State H1–H3, the randomized-assignment and held-out-fitting controls, and preview relative control support, directional pulse effect, failed transfer and withheld timing test. | cross-reference C001, C002, C004–C008 only | — | — | 1–5; S6 |

Promises this section creates: The paper will compare specified accumulator and rapid-forgetting implementations on jointly scored held-out controls; establish what randomized pulses do behaviourally; test whether the frozen pipelines transfer; report failed gates and sensitivity limits; and keep the exact mouse gap bounded to the documented search.

Promises it must deliver: A genuine model-identification conflict, distinct H1–H3 predictions, a key control against outcome-conditioned pulse labels, and a final paragraph whose answer matches Discussion D1.

Must include: The phrases “among the tested implementations” or equivalent and “in a bounded search”; positive descriptions of prior mouse work; the distinction between behavioural perturbation and mechanism identification; only verified source keys.

Must not include: A first-in-mice claim; a universal absence claim; data/statistics; a primacy hypothesis presented as answered; statements that pulses independently prove accumulation; a claim that macaque neural findings transfer directly to mice.

Known risks / reviewer bait: The gap can sound manufactured unless the exact conjunction is concise; too many mouse precedents can turn P3 into a literature list; “strong pulse” must not imply physiological naturalism; the preview must disclose the negative S6 outcome rather than hiding it.

Acceptance criteria (the reviewer instantiates these at commit time):

- Four paragraphs total no more than 700 words, with the claim by the final paragraph.
- C010, C011, C012, C015 and C019–C021 each appear once as primary claims and carry their verified citations.
- The bounded gap explicitly rejects broad mouse novelty.
- H1–H3 and the control-to-pulse transfer question are understandable without reading Methods.
- Every promise maps to a Results subsection and Discussion D1.
