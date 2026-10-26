<!-- np-contract
stage: S5 ; section: manuscript_integrity_audit_1_recheck ; agent: np-integrity-auditor ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021
numbers: N001, N004, N005, N006, N009, N010, N011, N016, N018, N019, N020, N021, N022, N023, N026, N027, N030, N034, N035, N036, N051, N052, N053, N054, N055, N056, N057, N058, N059, N060, N061, N062, N063, N064, N065, N066, N067, N068, N069, N070, N071, N072, N073, N074, N075, N076, N077, N078, N079, N080, N081, N082, N083, N084, N087, N088, N089, N090, N091, N092, N093, N094, N095, N096, N097, N098, N099, N102, N103, N104, N105, N106, N107, N108, N109
sources: adelson1985spatiotemporal, bogacz2006physics, caballero2022rt, carland2016evidence, cisek2009decisions, douglas2006motion, hawkins2015discriminating, huk2005neural, hyafil2023temporal, kiani2008bounded, koay2020amplitude, luken2025parameter, marques2018mousev1, odoemene2018visual, okazawa2018psychophysical, palmer2005effect, pinto2018visualpulses, ratcliff2008diffusion, samonds2018motion, steinemann2024direct, stine2020differentiating, stine2023termination, stirman2016touchscreen, tsetsos2012timevarying, wiecki2013hddm, winkel2014early, yates2017functional, you2022dynamics, zhou2009time
-->
# S5 manuscript integrity audit 1 — bounded-fix recheck

VERDICT: PASS

Recheck date: 2026-10-26  
Prior audit: `np/integrity/audit_1.md`  
Scope: B1--B3 only, followed by confirmation that the prior whole-audit disposition still holds  
Stage disposition: S5 retained; G5 was not crossed

## Recheck result

All three bounded blockers in audit 1 are closed. The patches change no scientific claim, numerical result, analysis
population, spine content or selected artwork. The only rendered-prose addition is the source-bound description of
the gate-pass series already displayed in Supplementary Figure S6 panel E. The prior audit's quantitative,
cross-section, citation-scope, artwork-source and AI-writing checks otherwise remain PASS.

## B1 — Abstract and impact claim bindings: PASS

- `np/drafts/title_abstract/v3.md` now declares C001, C004, C005, C006, C007, C008 and C009.
- Sentence markers occur for every declared result claim: C001 once, C004 once, C005 twice, C006 once, C007 once,
  C008 twice and C009 once.
- A diff against the prior version confirms marker/contract additions only; stripped Abstract and impact prose and all
  number tokens are unchanged.
- The pinned contract checker reports `Contract OK` for this draft.

## B2 — S6 panel-E gate-pass series: PASS

- N109 records `null 19/20; 10% decline 14/20; 20% decline 7/20; 40% decline 1/20`, with the selected panel-E CSV and
  four frozen calibration CSVs named as sources.
- Independent read-only recomputation from `calibration_summary_levels{0,0.1,0.2,0.4}.csv` reproduced, respectively,
  `(level, gate passes, n, detections)` = `(0,19,20,0)`, `(10,14,20,0)`, `(20,7,20,1)`, `(40,1,20,0)`.
- These counts exactly match `figS6_gates_sensitivity_2026-10-26_v2_source_E_calibration.csv`.
- `np/drafts/figure_legends/v5.md` declares N109 and describes both plotted series: gate passes via N109 and detections
  via N098. N109 renders exactly once in each assembled manuscript and no unresolved N109 token remains.
- `assemble_neuropaper.py` consistently treats N067--N109 as value-complete compound records. The pinned contract
  checker reports `Contract OK` for the legend draft.
- The optional panel-letter placement note in audit 1 was explicitly non-numeric and non-blocking; it does not alter
  this integrity verdict.

## B3 — citation identity: PASS

- `np/lit/notes/you2022dynamics.md` now gives PMID `35228308` and no longer contains `35273103`.
- The note agrees with the authoritative `sources.csv` row: DOI `10.1523/ENEURO.0161-21.2022`, PMID `35228308`,
  `verified=yes`, and with the previously verified PMCID `PMC8925649`/article identity.
- The manuscript citation key and scientific scope are unchanged.

## Deterministic and regression checks

- Temporary local assembly produced 11,198 words plain and 12,050 words marked. Both outputs matched
  `manuscript.md` and `np/integrity/manuscript_marked_s5.md` byte-for-byte.
- Pinned `np.py --root . check-all`: 0 errors. Remaining warnings are the same declared missing-author facts,
  word-budget/style advisories and false-positive `±1` matches inside `±100%`; none is an integrity failure.
- `np.py check-contract` passes for both patched drafts.
- `git diff --check` passes.
- The locked spine hash remains `c5c9f5dc15704d67`; the project remains at `S5_assembly` with G5 pending.

## Whole-audit disposition

The conclusions of `audit_1.md` are confirmed with B1--B3 closed:

- quantitative values, denominators, units and uncertainty mappings: PASS;
- Methods--Results--legend population and analysis consistency: PASS;
- all cited manuscript keys verified and claim scope supported: PASS;
- claim-marker coverage: PASS;
- selected artwork--caption--source mapping, including S6: PASS;
- assembly and internal-marker handling: PASS;
- overclaiming, faux causality, repetition, generic transitions, contradictions and scope drift: PASS.

The ten explicit author/final-production placeholders listed in audit 1 remain genuine missing author-supplied facts,
not integrity errors. They must remain explicit until supplied and still block a submission-ready package, but they do
not block completion of S5 integrity audit 1 or entry into S6 panel review.

CHANGE REQUEST: none.

BLOCKER: none for integrity audit 1. This file records PASS only; it does not advance the stage or approve/cross G5.
