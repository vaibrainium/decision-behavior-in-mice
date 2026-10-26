<!-- np-contract
stage: S5 ; section: manuscript ; agent: np-editor ; version: v2
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021
numbers: N023, N030, N034, N035, N036, N074, N079, N081, N088, N090, N091, N092, N095, N096, N098, N102, N104
sources:
-->

# S5 coherence audit, round 2

VERDICT: REVISE

The patched manuscript preserves the locked thesis, approved scientific scope and Challenge → Resolution structure. The repository-local assembler is acceptable: it leaves the pinned plugin untouched, renders compound N067–N107 from the ledger `value` field, rejects unknown or unresolved number tokens, strips internal markers from the plain manuscript and fails on the declared duplicate-unit patterns. Independent temporary assemblies reproduced both checked-in outputs byte-for-byte.

A final bounded editorial pass is still needed before integrity audit 1. The remaining issues are grammatical joins around value-only compound tokens, one stranded Results sentence, one unremoved token-unit repetition, ambiguous token-range separators in the reproducibility table, and duplicated availability placeholders. No claim, number, citation, analysis population or scope change is requested.

## Verification against round-1 patches

| Round-1 item | Result | Evidence |
|---|---|---|
| 1. Assembly and number rendering | PASS except one missed source context | `/src/scripts/paper/assemble_neuropaper.py` implements value-only N067–N107, explicit simple-token exceptions, marker stripping and duplicate guards. Plain and marked rebuild SHA-256 values match their checked-in targets. Methods still has `{{N023}} repetitions`, which renders “200 repetitions per trial repetitions.” |
| 2. Title, abstract and impact | PASS | Author placeholder restored; control-trial, rapid-forgetting-approximation and model-and-input-pipeline terminology is present; interval rendering has one unit and unchanged numeric strings. |
| 3. Introduction | PASS | Unchanged four-paragraph Opening → Challenge structure; no drift. |
| 4. Results | PASS with two prose repairs | Locked terminology and both repetition cuts are present. The retained C006 scope sentence became a one-sentence paragraph with an unclear “It,” and N090 is joined to a singular verb incorrectly. |
| 5. Discussion | PASS | “Control trials” and “rapid-forgetting approximation” replacements are present; opening and conclusion remain complementary rather than redundant. |
| 6. Materials and Methods | PASS with bounded joins/duplication | Heading hierarchy and most source-context repairs pass. N074, N079, N081, N096, N102 and N104 need grammatical framing; availability/AI placeholders are duplicated between Methods and end matter. |
| 7. Figure legends | PASS with one S6 syntax repair | Duplicate units are removed; Figure 5 uses plural pipelines; denominators and uncertainty records remain. The Figure S6 C sentence needs a semicolon rather than “and coverage was” after an unheaded noun phrase. |
| 8. Supplementary callout and end matter | PASS with duplicate cleanup | The S2 orphan is now an unnumbered supplementary-analysis pointer. Required end-matter placeholders are present. S6 artwork remains a declared production dependency before panel review, not a coherence blocker for integrity audit 1. |

## Identity and deterministic checks

- Unique number-token, citation-key and claim-marker identities are unchanged in all five patched sections. Results intentionally removed four repeated C007 markers and two repeated C006 markers with the deleted redundant prose; the unique claim set is unchanged.
- `np.py check-all` returns zero errors. Its six warnings are the declared `[MISSING]` fields, passed-section word-budget/lint advisories and two false-positive `±1` matches inside `±100%`; none indicates identity drift.
- `manuscript.md` contains no `np-contract`, `writer-notes`, claim markers or number tokens. The marker-preserving copy retains contracts/claims for audit and has no unresolved number token.
- Heading hierarchy passes: one `#` title, `##` manuscript sections and `###` subsections.
- Main figure callouts remain 1 → 2 → 3 → 4 → 5; S6 follows Figure 5; there is no numbered S2 callout without a legend.
- The prior duplicate-unit patterns are absent from both assembled files.

## Remaining bounded patch list

### Results v5

1. Merge the standalone sentence at line 68 into the preceding paragraph and replace its pronoun for a clear topic position:
   - Current: `It does not establish that the tested accumulator itself failed, because ...`
   - Replace with the preceding paragraph's final sentence: `This descriptive mismatch does not establish that the tested accumulator itself failed, because a different stimulus representation, pulse transformation or response mapping could alter the same prediction [[C006]].`
   - Keep the existing C006 marker; do not add or remove a claim identity.
2. Repair the N090 join at line 56 without changing the token:
   - Current: `... reached {{N059}} at the shared endpoint; {{N090}} registers the curve grid ...`
   - Replace with: `... reached {{N059}} at the shared endpoint. The registered curve grid, endpoint, mouse denominator and interval convention were {{N090}} [[C005]].`
   - The following sentence should continue unchanged.

### Methods v4

3. Frame compound settings as records rather than predicates, preserving every token:
   - Line 46: `Input scaling and temporal expansion used the registered operations: {{N074}}. The expanded input extended across the full analysis window rather than ending at the animal's response.`
   - Line 80: replace `... penalties were {{N079}}.` with `The registered binning, sparse-term, smoothing, weighting and empty-cell settings were: {{N079}}.`
   - Line 86: replace `Control-only cross-validation followed {{N081}}:` with `Control-only cross-validation used the registered scheme ({{N081}}).` Capitalize the next word: `Folds were constructed ...`.
   - Line 144: replace the first sentence with `The revised calibration used {{N096}}. It repeated the gate-plus-timing procedure under each generator.`
   - Line 161: replace `Known run-specific environments and commands were {{N104}}.` with `Known run-specific environments and commands were recorded as follows: {{N104}}.`
4. Remove the last literal word in the missed N023 context at line 142:
   - `with {{N023}} repetitions` → `with {{N023}}`.
   - This must render exactly `with 200 repetitions per trial`.
5. Repair the N102 sentence at line 138 and remove the duplicated descriptive clause:
   - Replace `Observed and simulated ...; group overlays followed {{N102}} and were descriptive rather than a paired observed-minus-model test.`
   - With `Observed and simulated directional curves used common rows, cells and weights. Their registered group-overlay and interval conventions were {{N102}}.`
6. In the reproducibility table, replace token ranges that render as misleading numeric dashes with explicit semicolon-separated tokens:
   - Figure 3: `{{N079}}–{{N083}}` → `{{N079}}; {{N080}}; {{N081}}; {{N082}}; {{N083}}`.
   - Figure 4: `{{N088}}–{{N091}}` → `{{N088}}; {{N089}}; {{N090}}; {{N091}}`.
   - Figure S6: `{{N092}}, {{N095}}–{{N098}}` → `{{N092}}; {{N095}}; {{N096}}; {{N097}}; {{N098}}`.
7. Delete Methods lines 163–165 containing the consolidated software/data placeholder and AI-disclosure placeholder. Retain their single copies in `np/drafts/end_matter/v1.md`; no missing fact is resolved or hidden.

### Figure legends v5

8. Repair the Figure S6 panel-C syntax at lines 101–103:
   - Current: `choice departures {{N030}} and {{N034}} and coverage was {{N035}} and {{N036}} ...`
   - Replace with: `choice departures were {{N030}} and {{N034}}; coverage was {{N035}} and {{N036}} of mouse-by-quantile response-time cells inside simulated ranges for the primary and secondary baselines.`

## Recheck required

After these eight edits, rerun the local assembler for both outputs, `np.py check-all`, the unique token/citation/claim identity comparison, duplicate-pattern search and `git diff --check`. A clean recheck is sufficient for coherence PASS; no third full narrative review is needed.

CHANGE REQUEST: none.

BLOCKER: integrity audit 1 should wait for the eight bounded editorial repairs above and a clean reassembly. Supplementary Figure S6 artwork remains required before panel review, but it does not block the S5 integrity audit.
