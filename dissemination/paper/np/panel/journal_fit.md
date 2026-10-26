VERDICT: REVISE
<!-- np-contract
stage: S6 ; section: journal_fit ; agent: np-section-reviewer ; version: r1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009
numbers: N001, N016, N051, N052, N053, N054, N059
sources: eLife author/process guidance checked 2026-10-26; neuropaper S6 rubric; S5 integrity and coherence audits
-->

# S6 panel review: journal fit

Criteria file: `np/panel/criteria_journal_fit.md`  
Mode: journal-fit; provisional eLife Research Article / Reviewed Preprint pathway, with expanded thesis-chapter reuse  
Review status: working simulated assessment for accountable human verification; no submission or editorial action taken

## Simulated decision and venue assessment

**Internal neuropaper shorthand: major revision.** This is not an actual eLife decision: current eLife makes an
editorial-selection decision before review and publishes every paper it reviews as a Reviewed Preprint rather than
accepting or rejecting it after review. In that actual frame, the scientific manuscript is **plausibly selectable for
peer review after the four P0 submission blockers are closed**. The question is in scope, the control-to-perturbation
test gives expert review a clear purpose, and the paper is unusually transparent about failed gates, low sensitivity
and the unrun timing test. As submitted in its current rendered form, however, it is not triage-ready because required
animal/ethics, authorship/declaration, availability and reference/package elements are absent.

A likely eLife-style assessment, if the missing records are supplied and the prose is tightened, would describe the
findings as **valuable** for computational and systems-neuroscience model validation, with **solid** support for the
relative control-model preference, randomized directional pulse effect and bounded conclusion that the tested
model-and-input pipelines did not transfer. The manuscript appropriately does not claim a unique mechanism or a
primacy/recency result. The contribution is narrower than an “important beyond the subfield” claim because replay
fidelity, candidate scope and mechanism localization remain unresolved.

For the thesis, the expanded Methods, failed-procedure record and negative-result detail are assets. The journal version
should expose the same scientific record through a tighter article narrative plus a supplementary reproducibility
record; the two uses do not require different claims.

## Quantitative fit snapshot

| Element | Rendered manuscript | Provisional eLife rule in `np/config.md` | Assessment |
|---|---:|---:|---|
| Title | 75 characters | suggested up to 120 | Meets; specific and evidence-matched |
| Abstract | 198 words | normally 150–200 | Meets, but is at the ceiling and numerically dense |
| Impact statement | 19 words | 15–30 | Meets; clear and third-person |
| Introduction + Results + Discussion | 4,578 whitespace-delimited words | suggested no more than 5,000 | Meets with 422-word margin |
| Materials and Methods | 4,566 rendered words | excluded from suggested main-text count | No formal excess; article-facing compression is advisable |
| Figure legends | 1,803 rendered words | no fixed limit identified | Complete but too ledger-like in places |
| Displays | 5 main figures + 1 supplementary figure | no display-item cap identified | Proportionate to the claim hierarchy |
| Explicit `[MISSING]` records | 10 | must be resolved before submission | Submission blocking, but honestly exposed |

Counts above come from `manuscript.md` using `sed` section bounds plus `wc -w`; title length excludes the Markdown
heading marker. The neuropaper checker returned zero errors and only five lint plus two known false-positive number
warnings. S5 integrity recheck is PASS and confirms number/source/artwork reconciliation.

## Criterion results

| ID | Result | Evidence |
|---|---|---|
| JF1 | met | Title; Introduction lines 15–21; Results lines 47–94; Discussion lines 98–108 give a coherent life-science model-validation question and a reason public expert review would add value. |
| JF2 | met | Abstract line 7 and Discussion lines 98–108 distinguish significance from evidential scope and do not turn failed/inconclusive procedures into confirmation. |
| JF3 | partly met | The title and 19-word impact statement are strong; the 198-word abstract is complete but exact six-to-eight-decimal values compete with its editorial message. |
| JF4 | partly met | Figure-order arc is clear, but Results lines 53, 61–69 and 83–91 repeatedly switch from findings to registry-like procedural detail. |
| JF5 | partly met | Main text meets the suggested limit. The Methods reproducibility table at lines 254–263 and some Results detail are valuable for the thesis but should be separated from the journal narrative. |
| JF6 | partly met | Five main figures plus S6 are logically necessary and visually coherent. S6 remains dense, with the panel-C coverage inset and panel-D label competing at final-size viewing. |
| JF7 | not met | Required author/declaration fields are explicit placeholders at lines 3 and 265–275; a References section and submission-ready combined package are absent. |
| JF8 | not met for submission | Lines 114–120 lack animal, ethics, blinding, training, session and hardware records; line 273 lacks final software/data identifiers and access conditions. These are explicit rather than fabricated. |
| JF9 | met | The draft cleanly marks missing author facts. The issue list below keeps author facts, production work and scientific/editorial revision separate. |
| JF10 | partly met | Failed gates, low sensitivity and stopping are exemplary (lines 85–94; S6). Preprint route, persistent source-data/code access and final AI disclosure remain unresolved. |
| JF11 | partly met | The article stands alone scientifically, but local-path provenance and exhaustive registry strings at lines 254–263 are thesis/repository material rather than efficient journal prose. |
| JF12 | met | No new analysis is needed for journal fit; all requested remedies below are bounded completion, relocation, rounding or clarification. |

## Numbered issues

| # | Severity | Class | Exact location | Problem and why it matters | Bounded remedy |
|---:|:---:|---|---|---|---|
| 1 | P0 | **Submission-blocking author facts; not scientific revision** | `manuscript.md` lines 112–120, “Animals and experimental oversight” and “Figure 1: apparatus, task and analysis sets” | Strain, sex, age, provenance, housing/welfare, sample-size rationale, ethics bodies/protocol IDs, blinding, training criteria, session rules and complete rig/display hardware are missing. Animal oversight and reproducibility cannot be appraised or submitted from placeholders. | Authors supply the exact verified records, including an explicit “not performed” where applicable. Preserve unknowns until then; do not infer boilerplate and do not run a new analysis. |
| 2 | P0 | **Submission-blocking author/administrative facts; not scientific revision** | line 3; lines 265–271 | Author list/order/affiliations/corresponding author, acknowledgements/permissions, funding and funder role, contributions and competing interests are absent. | Obtain and insert author-approved records, then validate contribution/authorship and declaration consistency. This is factual completion, not manuscript-claim revision. |
| 3 | P0 | **Submission-production and reproducibility blocker; no new analysis requested** | lines 250–275, especially line 273 | The current record names local paths and commands but has no final manuscript-wide software lock, complete figure-run commits, persistent data/code/source-data identifiers, access conditions or release timing. eLife expects a Data Availability Statement and the original data needed to support claims, subject to justified restrictions. | Freeze the final code/software provenance; deposit or identify versioned data, code and per-figure source data under author-approved access terms; replace local-only paths in the public statement with persistent identifiers and precise restrictions/timing. Retain detailed commands in a repository or supplementary provenance table. |
| 4 | P0 | **Submission-package blocker; not a scientific defect** | citations throughout lines 15–200; end of file after line 373; line 275 | The rendered file ends after the S6 legend: Pandoc citation keys remain unresolved, no References section is assembled, selected figures are not embedded in this review document, and the preprint route/status plus final AI-use disclosure are not settled. These prevent a usable eLife submission even though the 44-source ledger is audited. | At S8, render the verified bibliography, build a readable combined PDF or accepted upload set with the six selected displays, record preprint/DOI status or planned eLife preprint route, and insert author-approved AI wording after the current policy recheck. Do not add unverified references. |
| 5 | P1 | Scientific framing / editor accessibility | Introduction line 19 and line 21; Abstract line 7; Impact line 11 | The core conceptual contribution is strong, but the Introduction devotes a full paragraph to the exact mouse-literature conjunction. At triage this can make the paper read as a narrow priority exercise even though the stronger contribution is a general lesson about out-of-condition validation. | Compress line 19 to the established positive precedents plus one bounded-gap sentence; make the last Introduction paragraph lead with why control-selected model transfer is informative. Keep the existing “bounded search” and no-priority language; add no novelty claim. |
| 6 | P1 | Scientific communication using existing evidence | Abstract line 7; Results lines 61, 83, 87 and 91; legends lines 331–370 | Six-to-eight-decimal estimates and full registry strings obscure effect scale and the inferential hierarchy. The values are traceable, but the rendered prose reads like a ledger rather than an article and is harder for a non-specialist editor to parse. | Round narrative estimates to defensible precision (for example, 5.84 pp, 95% CI 1.80–9.89, Holm-adjusted p=0.019) while retaining exact values in source data/ledger. Keep test, n, uncertainty and correction in the legend or a compact statistics/source-data table. No value or inference changes. |
| 7 | P1 | Article/thesis separation and narrative flow | Results lines 53–55, 61–69 and 83–91; Methods lines 182–200 and 254–263 | Results repeatedly pause for candidate codes, complete optimization/calibration settings and provenance strings; Methods then repeat much of the same record. This is useful thesis and reproducibility material but weakens the result-first eLife arc. | In Results retain the comparison, effect, gate outcome, sensitivity limit and one necessary caveat per paragraph. Move complete candidate strings, seeds, thresholds and calibration inventories to Methods or one supplementary reproducibility table. For the journal version, move the local execution table at lines 254–263 to supplement/repository; retain it in the thesis version. |
| 8 | P1 | Figure-legend burden | legends lines 279–373, especially Figures 1–3 and S6 | The legends are complete, but several reproduce long denominator/settings records already held in source tables and Methods. At 1,803 rendered words they slow figure-led reading and repeat the article's densest prose. | Keep panel purpose, population, n, uncertainty, tests and crucial caveats in each legend; move exhaustive cell-by-cell counts and parameter strings to clearly named source-data or supplementary tables. Preserve every registered denominator outside the narrative legend. |
| 9 | P2 | Figure polish | selected `figS6_gates_sensitivity_2026-10-26_v2.png`, panels C–D; legend lines 366–370 | At full-page review size, “Coverage” and the `D` label visually crowd the boundary between the gain-revised inset and frozen-strategy panel. The science remains interpretable, so this is polish rather than a blocker. | On the next versioned export, move `D` right/up onto the frozen-strategy panel and give the coverage inset a clearer panel-C subheading or boundary. Do not alter data or overwrite v2. |
| 10 | P2 | Abstract polish | Abstract line 7 | The abstract meets the 150–200-word recommendation but sits at 198 words and carries two related timing sentences plus the two-mouse diagnostic, leaving little breathing room for the central transfer result. | After P1 item 6, trim roughly 15–25 words by merging the endpoint/time-course sentences or removing the two-mouse detail; keep the failed gates, unrun timing test and mechanism limit. |

Counts: **P0 = 4; P1 = 4; P2 = 2.**

## Blockers and revision boundary

- **Submission blockers:** items 1–4. Items 1–2 require author-supplied facts; items 3–4 require final production,
  repository/policy and formatting work. None is evidence that a new scientific analysis is needed.
- **Scientific/editorial revisions using existing evidence:** items 5–8. These sharpen significance and readability
  without changing the thesis, claims, populations, numbers or selected figure set.
- **Optional polish:** items 9–10.
- **New analyses requested:** none.
- **Specialist limits:** statistical validity, field novelty and strongest alternative explanations belong to the
  parallel statistics, domain and devil's-advocate reviewers. This report relies on the PASS integrity audit for
  source reconciliation and does not supersede those reviews.

## Strengths relevant to the decision

- The title, abstract and impact statement are mutually consistent and appropriately avoid a unique-mechanism claim.
- The main text fits the provisional 5,000-word recommendation without hiding the negative result.
- Figure order is unusually clean: task -> reconstructed input -> control model selection -> randomized behavioural
  effect -> transfer mismatch, with S6 documenting the gate/calibration/stopping record.
- The distinction between a randomized behavioural effect and a descriptive model mismatch is maintained throughout.
- The explicit report of failed original and revised gates, low sensitivity and the decision not to run the planned
  timing test is well suited to eLife's public-review model and is especially valuable in a thesis chapter.

## Policy and evidence basis

Venue information was checked on 2026-10-26 against the project's dated author-instruction record and current public
eLife pages: [Submit your research](https://elifesciences.org/about/submit-your-research),
[Peer review and publishing at eLife](https://elifesciences.org/about/peer-review), and
[How and why eLife selects papers for peer review](https://elifesciences.org/articles/100571). Current eLife policy
means the accept/minor/major/reject label above is only neuropaper simulation shorthand. Author authorization for this
local simulated review is recorded in `np/decisions.md` D001 and D009. No conflict was identified from the supplied
record; unpublished manuscript content was not sent to external search or citation services.
