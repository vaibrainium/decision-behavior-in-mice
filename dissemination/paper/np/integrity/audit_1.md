<!-- np-contract
stage: S5 ; section: manuscript_integrity_audit_1 ; agent: np-integrity-auditor ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021
numbers: N001, N004, N005, N006, N009, N010, N011, N016, N018, N019, N020, N021, N022, N023, N026, N027, N030, N034, N035, N036, N051, N052, N053, N054, N055, N056, N057, N058, N059, N060, N061, N062, N063, N064, N065, N066, N067, N068, N069, N070, N071, N072, N073, N074, N075, N076, N077, N078, N079, N080, N081, N082, N083, N084, N087, N088, N089, N090, N091, N092, N093, N094, N095, N096, N097, N098, N099, N102, N103, N104, N105, N106, N107, N108
sources: adelson1985spatiotemporal, bogacz2006physics, caballero2022rt, carland2016evidence, cisek2009decisions, douglas2006motion, hawkins2015discriminating, huk2005neural, hyafil2023temporal, kiani2008bounded, koay2020amplitude, luken2025parameter, marques2018mousev1, odoemene2018visual, okazawa2018psychophysical, palmer2005effect, pinto2018visualpulses, ratcliff2008diffusion, samonds2018motion, steinemann2024direct, stine2020differentiating, stine2023termination, stirman2016touchscreen, tsetsos2012timevarying, wiecki2013hddm, winkel2014early, yates2017functional, you2022dynamics, zhou2009time
-->
# S5 manuscript integrity audit 1 — resolved after bounded-fix recheck

VERDICT: PASS

Resolution: the initial B1--B3 findings below were corrected and independently re-audited. The canonical PASS record
is `np/integrity/audit_1_recheck.md`; it confirms deterministic assembly, exact source reconciliation and zero remaining
integrity blockers. The original findings are retained below for audit history.

Audit date: 2026-10-26  
Mode: manuscript integrity, audit 1  
Repository base commit inspected: `e7f1e04` with the documented dirty S5 worktree  
Stage disposition: remain at S5; G5 was not crossed

## Bottom line

The scientific result and source reconciliation passes. The selected manuscript rebuilds deterministically, the
locked thesis is unchanged, the quantitative findings and analysis populations agree across Results, Methods and
legends, and the selected artwork agrees with its adjacent source tables. Independent recomputation reproduced the
critical Supplementary Figure S6 departures, coverage counts, strategy sensitivity and timing-calibration counts.
The prose also preserves the scope boundaries around descriptive model--data comparisons, two-mouse diagnostics,
failed gates and the unrun timing test.

Three bounded integrity repairs are required before this audit can pass: the Abstract's result sentences are not
bound to their approved claims; the S6 legend does not describe the plotted gate-pass series; and one literature note
retains an incorrect PMID even though the authoritative source ledger is correct. None requires a new claim, a spine
change, a new analysis or author judgment.

## Initial blocking findings and bounded patches (resolved)

### B1. Abstract/impact claim bindings are incomplete

**Location:** `np/drafts/title_abstract/v3.md:4` and `:14-18`; rendered at `manuscript.md:7-11`.

The contract declares only C001, and the sole marker occurs after the control-comparison/pipeline-failure sentence.
The same paragraph then makes approved quantitative or interpretive claims C005 (directional effect and cumulative
contrast), C006 (observed--predicted temporal mismatch), C009 (PSUIM6/7 gain tradeoff), C007 (failed gates and unrun
timing test) and C008 (mechanism non-localization) without sentence-level bindings. The impact statement is also an
unmarked restatement of C008. All values are correct; this is a marker/contract coverage failure, not a result error.

**Bounded patch:** add C004/C005/C006/C007/C008/C009 to the contract as applicable; attach `[[C005]]` to the pulse
effect/cumulative-contrast sentences, `[[C006]]` to the descriptive temporal-mismatch sentence, `[[C009]]` to the
two-mouse sentence, `[[C007]]` to the gate/timing sentence and `[[C008]]` to the concluding and impact sentences.
Retain C001 on the thesis sentence. Do not change prose or numbers.

### B2. Supplementary Figure S6 legend omits a plotted quantitative series

**Location:** selected `figures/figS6_gates_sensitivity_2026-10-26_v2.{png,pdf,svg}`, panel E;
`np/drafts/figure_legends/v5.md:104-106`; rendered at `manuscript.md:369-372`.

Panel E plots and labels both gate-pass counts (`19/20`, `14/20`, `7/20`, `1/20`) and primacy-detection counts
(`0/20`, `0/20`, `1/20`, `0/20`). The legend describes only the detection series. The artwork is correct and both
series independently reproduce from `figS6_gates_sensitivity_2026-10-26_v2_source_E_calibration.csv`, but the caption
does not fully define what is rendered. Existing N037 records only the null gate-pass numerator; no current ledger
record binds the complete four-level gate-pass sequence.

**Bounded patch:** add one new compound number row for the four gate-pass counts, sourced directly to the selected
S6 source-E CSV and frozen calibration CSVs; add its token to the Figure S6 legend and relevant contracts. Amend panel
E's legend sentence to state the gate-pass sequence before the existing detection sequence. No artwork or analysis
change is required. Separately, reposition panel label `D` slightly right/up on any later artwork export because the
current label visually reads as part of the neighbouring `Coverage` heading; this readability fix is non-numeric.

### B3. One citation note has stale identity metadata

**Location:** `np/lit/notes/you2022dynamics.md:3`.

The note states PMID `35273103`, whereas `np/ledger/sources.csv`, DOI `10.1523/ENEURO.0161-21.2022`, PMCID
`PMC8925649`, the earlier `mouse_dynamic_visual_audit.md`, and the current PubMed record all identify PMID
`35228308`. The cited scientific scope is supported: the primary article includes a DDM analysis of correct/incorrect
RT distributions. The rendered citation is not misidentified because the authoritative source ledger is correct.

**Bounded patch:** replace only the stale PMID in the note with `35228308`. Do not alter the source key, DOI, claim or
manuscript citation.

## Quantitative and population audit

- **PASS:** 174 number-token occurrences comprising 74 unique IDs resolve from `numbers.csv`; there are no unresolved
  tokens or duplicate-unit patterns in either assembly. Plain and marker-preserving temporary rebuilds matched
  `manuscript.md` and `np/integrity/manuscript_marked_s5.md` byte-for-byte.
- **PASS:** Figure 1 source tables reproduce 10 mice, 50 mouse-sessions, 30,045 accepted trials, 25,508 responses and
  4,537 no-response trials; panel-specific 14,015 responded controls, 16,522 total controls and every N105 count match.
- **PASS:** Figure 2 source tables reproduce UCLA/UW responded-control denominators 9,258/4,757, nominal-zero
  denominators 872/443, paired-replay trials 76/108 and 76 trials per UCLA alternative. Trial-level dispersion is not
  presented as mouse-level uncertainty.
- **PASS:** Figure 3 source tables reproduce strategy delta 345.741323 NLL, 6/10 mice above the working +10 threshold,
  no mouse below -10, component sums +1017.779, +858.111, -21.350, +25.773 and -33.266, and panel-D denominators
  14,014 choice, 16,521 no-response, 10,620 correct-RT and 3,394 error-RT observations. Held-out comparison and
  in-sample fit-quality displays remain explicitly separated.
- **PASS:** Figure 4 source tables reproduce 10,281 supported trials, 717 cells, 118 pre-onset responses, 1,709
  no-response trials, mouse-level effect 5.844356 pp (95% Student-t CI 1.799491--9.889221), raw p 0.00970514512,
  Holm p 0.01941029024 and endpoint 5.798136 pp at 4.58 s. Mice, not cells/trials, are the group unit.
- **PASS:** Figure 5 source tables reproduce the 10-mouse observed and predicted window summaries and the PSUIM6/7
  held-out choice benefits 10.3998/10.0055 NLL with remaining-objective costs 96.0103/106.6094 NLL. The manuscript
  limits the strong tradeoff claim to these two one-seed diagnostics and labels group overlays descriptive.
- **PASS:** Methods, Results and legends preserve the differing descriptive, legacy-model, common-row and scheduled
  analysis populations. The 16,522 Figure-1 scheduled controls versus 16,521 DDM-input controls are not conflated.
  Confidence intervals, multiplicity correction, censoring and simulated-replicate limitations are stated consistently.

## Independent S6 recomputation

Read-only recomputation from the frozen inputs, without importing the figure builder, gave:

| Input | SHA-256 / result |
|---|---|
| original primary gate pickle | `51ab63ab317ef9b6e2c99d92cc725b24c00df7ecf3e82940cb7ec9f81ceb0aab`; departure 0.295968634567205; RT 34/50; no response 9/10; FAIL |
| original secondary gate pickle | `0e56d99fd4cddeef506c2880b90240b343bd115129a45a0168f59de935231ee1`; departure 0.3174069864244733; RT 34/50; no response 5/10; FAIL |
| revised primary gate pickle | `69f28e273475b5aec78b38cfd121800a72136345564264288cfe6cb8a6927ea4`; departure 0.24176887886851925; RT 31/50; no response 9/10; FAIL |
| revised secondary gate pickle | `a858531f7b233539f43f713576992b36769da375d424fc4af3f6d59789e9479d`; departure 0.3088816475149114; RT 35/50; no response 6/10; FAIL |
| strategy sensitivity CSV | `3944aa0dcb264dbd9b193d3d22a00872879a76746c72ad8e4f10c67f5dc205b3`; rapid-forgetting 1/20, accumulator 0/20 correct |
| timing calibration CSVs | gate passes 19/20, 14/20, 7/20, 1/20 and detections 0/20, 0/20, 1/20, 0/20 at 0%, 10%, 20%, 40% decline |

These values match the selected S6 source CSVs and artwork. They support gate failure and low sensitivity, not absence
of primacy, recency or temporal weighting. The manuscript preserves that distinction.

## Citation audit

- **PASS after B3:** all 29 cited keys occur in the authoritative 44-row `sources.csv`, every cited row has
  `verified=yes`, and the cited notes support the sentence scope with the stated species/task/model limitations.
- No `np/ledger/citations.csv` exists. This is not a manuscript defect: the installed neuropaper workflow defines
  `np/ledger/sources.csv` as the canonical citation ledger, and that file is complete. Future dispatch packets should
  name `sources.csv` or explicitly document an alias rather than creating a second authoritative ledger.
- The bounded novelty statement remains appropriately scoped to the searched conjunction; it does not claim broad
  mouse visual-decision novelty.

## AI-writing failure modes and cross-section consistency

| Check | Verdict |
|---|---|
| Overclaiming / scope drift | PASS: relative model preference, descriptive temporal mismatch and unresolved mechanism are maintained. |
| Faux causality | PASS: scheduled assignment supports the directional effect; pipeline failure is not localized to sensory, decision or motor stages. |
| Repetition / generic transitions | PASS: prior coherence repairs removed adjacent duplications; remaining opening/conclusion recurrence is functional. |
| Contradictions | PASS: Abstract, Results, Discussion, Methods and legends agree on gates, sensitivity, populations and the unrun timing test. |
| Denominator or uncertainty slippage | PASS: biological, trial, cell and simulation units are explicitly separated. |
| Claim-marker coverage | REVISE: B1. |
| Artwork--caption--source mapping | REVISE: B2; all plotted values themselves match source data. |

## Deterministic checks run

`np.py --root . check-all` returned 0 errors. Its warnings were the declared missing fields, section-length/style
advisories and two false-positive `±1` matches inside `±100%`. `git diff --check` passed. The manuscript contains no
contracts, writer notes, claim markers or number tokens; the marked copy retains contracts/claim markers and contains
no number tokens. Main figure callouts remain 1 through 5, followed by S6.

## Author-supplied missing facts (not integrity errors)

Ten explicit placeholders remain: author order/affiliations/corresponding author; animal strain/sex/age/provenance,
housing/welfare/sample-size rationale and ethics IDs; blinding; training/session/hardware details; acknowledgements;
funding/funder role; author contributions; competing interests; final software/data availability; and final AI-use
disclosure. These require author or final-production input. They do not explain or excuse B1--B3, and they do not
require invented boilerplate.

CHANGE REQUEST: none. The bounded repairs use already approved claims and verified sources and do not alter the locked
spine, scientific interpretation, analysis population or figure selection.

BLOCKER: none. B1--B3 are resolved and the independent re-audit returned PASS. Entry into S6 panel review is allowed;
this audit does not approve or cross G5.
