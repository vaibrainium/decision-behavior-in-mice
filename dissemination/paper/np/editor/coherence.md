<!-- np-contract
stage: S5 ; section: manuscript ; agent: np-editor ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021
numbers: N001, N004, N005, N006, N009, N010, N016, N018, N022, N023, N026, N027, N030, N034, N035, N036, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066, N067, N068, N069, N070, N071, N072, N073, N074, N075, N076, N077, N078, N079, N080, N081, N082, N083, N084, N087, N088, N089, N090, N091, N092, N093, N094, N095, N096, N097, N098, N099, N102, N103, N104, N105, N106, N107
sources:
-->

# S5 coherence audit

VERDICT: REVISE

The scientific story is coherent and remains inside the locked spine, but the assembled manuscript is not ready for integrity audit or panel review. The blocking defect is mechanical number rendering: `render_text()` always concatenates `value + unit`, even when `unit` is ledger metadata for a compound record or the draft already supplies the unit. This creates duplicated units and long metadata fragments throughout the rendered prose. The assembled source also omits required front/end-matter placeholders and calls out Supplementary Figure S2 without supplying its legend.

No patch below changes a claim, number, citation, scope boundary or analysis population. Patches are limited to rendering, terminology, hierarchy, transitions, repetition and explicit missing-field handling.

## Audit results

| Check | Result | Evidence and disposition |
|---|---|---|
| Challenge → Resolution | PASS | Introduction ¶4 asks whether control-selected pipelines transfer to randomized strong pulses; Discussion ¶1 and the conclusion answer with relative control support, behavioural redirection and failed pulse transfer without mechanism localization. |
| Promises ledger | PASS | All eleven promises in `np/spine.md` are delivered: Figure 3 handles the relative control comparison; Figures 4–5 separate the assignment effect from pipeline interpretation; S6 reports failed gates, sensitivity and the withheld timing test; Discussion supplies limits and a concrete discriminating experiment. |
| Glossary | REVISE | Several short forms obscure locked terms: “rapid forgetting,” “the accumulator,” “frozen pipelines,” “rapid-forgetting alternative,” and “non-perturbation trials.” Exact replacements appear below. |
| Tense | PASS | Established knowledge is present tense; study methods/findings are predominantly past tense; figure descriptions and interpretation are present tense. No systematic tense repair is needed. |
| Transitions | PASS with two trims | Figure-order transitions are clear. Two Results paragraphs repeat caveats already made immediately before them; bounded deletions are listed below. |
| Repetition | REVISE | The Figure 5 no-paired-test caveat and the S6 distinction between the two simulations are each stated twice in adjacent paragraphs. Discussion repetition is functional OCAR resolution and should remain. |
| Abstract ↔ conclusion | PASS | Both state the same qualified result: control trials favour the tested accumulator among tested implementations, whereas pulses expose failed transfer without identifying a unique mechanism. The conclusion appropriately omits detailed statistics. |
| Figure-callout order | REVISE | Main calls proceed 1 → 2 → 3 → 4 → 5, and S6 follows Figure 5. Supplementary Figure S2 is called out in Results but has no assembled legend; resolve without renumbering. |
| Topic/stress positions | PASS after renderer repair | Topic sentences carry the Results/Discussion story. Current compound-token expansions bury sentence stress positions in metadata; this is a rendering failure, not a narrative rewrite need. |
| Placeholders | REVISE / author facts remain open | Six visible placeholders are honest and must remain until supplied. Required author/funding/contribution/interest/acknowledgement placeholders from the approved outline are absent and must be restored. |
| Rendered token-unit duplication | FAIL | Examples include “10 mice mice” (line 143), “0.3 s-s” (304), “345.7 NLL units NLL units” (341), and compound records followed by semicolon-delimited `unit` metadata (for example lines 101, 105, 161–177 and 283–290). |

## Patch list

Apply in this order. Reassemble after patch 1 before judging any prose line, because many apparent sentence defects are renderer-generated.

### 1. Assembly and number rendering — blocking, manuscript-wide

1. Extend `np/ledger/numbers.csv` with a prose-display field (for example `display`) while preserving the existing `value`, `unit`, `n_unit`, source and note fields for audit. In `render_text()`, substitute `display` when non-empty and otherwise retain the existing `value + unit` fallback. Do not infer prose by appending metadata fields.
2. Populate `display` for every compound token N067–N107 used in the manuscript. Each display string should be a copy-edited rendering of the existing `value` only, with units embedded exactly where they belong; it must preserve every registered number. In particular, do not append the current multi-item `unit` field for N067–N107. Those fields describe heterogeneous contents and are not sentence suffixes.
3. Give simple tokens a single complete display form (for example N001 `10 mice`, N009 `0.3 s`, N016 `345.7 NLL units`, N051 `5.844356 percentage points`, N054 `0.01941029`, and N035 `0.62`). Formatting may suppress the ledger word `probability` or `fraction` when the surrounding prose already names the quantity; the numeric strings remain unchanged.
4. Strip all `<!-- writer-notes ... -->` blocks during assembly, as is already done for contracts and claim markers. Preserve the Figure S6 artwork warning in this audit or the production handoff rather than in the manuscript source.
5. Add a deterministic post-assembly failure check for immediate duplicate-unit patterns (`mice mice`, `trials trials`, `cells cells`, `s-s`, `logit logit`, `NLL units NLL units`, `percentage points percentage points`, `fit files fit files`, `repetitions per trial repetitions per trial`) and for any rendered compound-token metadata suffix.

Acceptance check: no number changes; every number token still resolves; `np.py check-all` passes; none of the duplicate patterns above occurs in `manuscript.md`; compound settings read as grammatical prose rather than ledger columns.

### 2. Title, abstract and impact statement

1. Restore the approved front-matter placeholder immediately below the title: `[MISSING: author list, order, affiliations and corresponding author]`.
2. Standardize locked terminology in the abstract:
   - Replace “selected under ordinary evidence” with “selected on control trials.”
   - Replace “over rapid forgetting” with “over the rapid-forgetting approximation.”
   - Replace “the frozen pipelines” with “the frozen model-and-input pipelines.”
3. Render the directional interval as `5.844356 percentage points (95% CI, 1.799491–9.889221 percentage points; Holm-adjusted P = 0.01941029)`. This changes presentation only; all four ledger numbers remain identical.
4. In the impact statement, replace “ordinary behaviour” with “control-trial behaviour” to match the glossary and the actual fitting population.

### 3. Introduction

No structural patch is required. The four paragraphs implement Opening → Challenge, the final paragraph previews H1–H3 and all downstream outcomes, and the tense is consistent. Preserve the bounded-search language and the final sentence’s explicit non-claims.

### 4. Results

1. Standardize the Figure 3 heading to “Held-out control trials favoured the tested accumulator over the rapid-forgetting approximation.”
2. In its first paragraph, replace:
   - “distinguished evidence retention from rapid forgetting” with “distinguished the tested accumulator from the rapid-forgetting approximation”;
   - “The accumulator retained evidence” with “The tested accumulator retained evidence”;
   - “rapid-forgetting minus accumulator negative log likelihood” with “rapid-forgetting-approximation minus tested-accumulator negative log likelihood.”
3. In the sensitivity paragraph, replace “equivalence between accumulation and rapid forgetting” with “equivalence between the tested accumulator and rapid-forgetting approximation.”
4. Remove the first two sentences of the fourth Figure 5 paragraph (“Using the same rows … formal paired group test.” and “This keeps … strong transient evidence.”). The immediately preceding paragraph already states both points. Retain its final sentence, beginning “It does not establish that the tested accumulator itself failed…”, as the paragraph’s scope-ending sentence.
5. Delete the standalone paragraph beginning “The two sensitivity analyses also answered different questions.” The preceding paragraph already distinguishes the generators, questions and non-pooling; the deletion removes repetition without deleting a claim or number.
6. Do not otherwise compress the Figure 4 timing caveats: the first paragraph defines what the cumulative curve cannot time, whereas the next explains the competing-outcome construction and establishes the Figure 5 predictive target.
7. After number-render repair, re-read all composite settings in the recovery, Figure 4 and S6 subsections (current manuscript lines 65, 73, 81, 83, 97, 101 and 105). Preserve the registered content but punctuate it as sentences or parenthetical settings rather than semicolon-delimited ledger output.

### 5. Discussion

1. In the future-experiment paragraph, replace “fitted on non-perturbation trials” with “fitted on control trials.”
2. In the conclusion, replace “specified rapid-forgetting alternative” with “specified rapid-forgetting approximation.”
3. Retain the opening and concluding synthesis. Their repetition is purposeful: the opening resolves the Introduction’s Challenge, while the final paragraph states the broader implication and returns to the title.

### 6. Materials and Methods

1. Change the top-level `# Methods` heading to `## Materials and Methods` so it matches the level and name approved in the outline; demote each current Methods `##` subsection to `###`.
2. Apply these source-context repairs so complete display tokens are not followed by the same unit again:
   - `{{N001}} mice tested in {{N004}} mouse-sessions` → `{{N001}} tested across {{N004}}`.
   - `giving {{N005}} within-window responses and {{N006}} censored trials` → `giving {{N005}} with a response in the window and {{N006}} classified as censored`.
   - `yielded {{N018}} fit files` → `yielded {{N018}}`.
   - `{{N055}} trials in {{N056}} cells` → `{{N055}} across {{N056}}`.
   - `including {{N057}} pre-onset responses and {{N058}} trials with no response` → `including {{N057}} that preceded onset and {{N058}} with no response`.
   - `{{N022}} prediction files` → `{{N022}} containing matched predictions`.
   - Every `{{N023}} repetitions per trial` occurrence → `{{N023}}`.
3. Replace “operational rapidly forgetting candidate” with “operational rapid-forgetting approximation.”
4. For N067–N107 compound settings, preserve every registered item but copy-edit their `display` strings into grammatical parameter lists. The most urgent locations are stimulus replay/input (N072–N074), model fitting/recovery (N075–N083), assignment and validation (N088–N091), pulse diagnostics (N092–N104), and the reproducibility table (N105–N107).
5. Consolidate the two overlapping software placeholders at the end of reproducibility into one explicit line: `[MISSING: final manuscript-wide software lock; final Figure 1–5/S6 run commits and executable provenance; data/code repository identifiers, access conditions and release timing]`. Do not fill any field from inference.
6. Keep the animal, ethics, blinding, training/session and hardware placeholders visible. They are genuine author-supplied facts and cannot be repaired editorially.

### 7. Figure legends

1. Figure 1 source-context repairs:
   - `{{N009}}-s` → `{{N009}}` and `{{N010}}-s` → `{{N010}}`.
   - `{{N001}} mice, {{N004}} mouse-sessions, {{N005}} within-window responses and {{N006}} no-response trials` → `{{N001}}, {{N004}}, {{N005}} with a response in the window and {{N006}} with no response by 5 s`.
2. Figure 3: `{{N016}} NLL units` → `{{N016}}`.
3. Figure 4:
   - Remove the literal “percentage points” after N051 and N059.
   - `{{N055}} trials in {{N056}} supported cells` → `{{N055}} across {{N056}} with both signs represented`.
   - `{{N057}} responses before logged onset and {{N058}} trials with no response` → `{{N057}} that preceded logged onset and {{N058}} with no response`.
4. Figure 5 heading: change singular “pipeline predicted” to “pipelines predicted” to match C006 and the locked figure plan.
5. Figure 5 panel D: remove the literal “NLL units” after N064; N063–N066 should each render once with their registered negative-log-likelihood unit.
6. Figure S6:
   - Remove literal “logit” after N026, N027 and N034 (N030 and N034 are a paired phrase, so render both consistently).
   - Replace “fractions {{N035}} and {{N036}} of … cells” with “coverage was {{N035}} and {{N036}} of … cells,” using display forms `0.62` and `0.7` in this grammatical context.
7. Retain all denominator and uncertainty content from N105–N107, but render it as sentences without appending their heterogeneous `unit` metadata.

### 8. Supplementary callout and end matter

1. Resolve the current orphan callout to Supplementary Figure S2 before integrity audit: either assemble the already-supported S2 legend and artwork into the supplementary package, or change “Supplementary Figure S2 reports…” to an unnumbered supplementary-analysis pointer until the complete supplementary numbering is frozen. Do not silently renumber S6.
2. Supplementary Figure S6 remains text-only and requires its already-declared artwork-specific cell-denominator audit before panel review. This is a production dependency, not permission to alter the S6 claims.
3. Restore the approved end-matter placeholders after Methods and before the figure legends:
   - `[MISSING: acknowledgements and contributor permissions]`
   - `[MISSING: funding and funder role]`
   - `[MISSING: author contributions]`
   - `[MISSING: competing interests]`
   - the consolidated data/software availability placeholder from Methods patch 5
   - `[MISSING: final AI-use disclosure wording after eLife policy recheck]`
4. Do not create a bibliography from unverified material; reference generation remains restricted to verified keys in `np/ledger/sources.csv`.

## Required verification after patches

1. Run `np.py check-all`, assemble both stripped and marker-preserving copies, and confirm the locked spine hash is unchanged.
2. Confirm every numeric string in the new manuscript comes from the same token as before and no citation key changed.
3. Confirm heading levels are title `#`, manuscript sections `##`, and subsections `###`.
4. Confirm first main-figure callouts are ordered 1, 2, 3, 4, 5 and that every supplementary callout has a corresponding assembled legend/package entry.
5. Search for `[MISSING:` and compare the result against the approved outline; no unknown fact may disappear except by author-supplied resolution.
6. Re-run this coherence audit only on patched sections before dispatching integrity audit 1.

## Change requests and blockers

CHANGE REQUEST: none. The locked thesis, approved claims, citations, numerical values and scientific scope do not need revision.

BLOCKER: integrity audit 1 should not begin from the current `manuscript.md`. First repair token rendering and the exact source contexts above, restore required placeholders, resolve the Supplementary Figure S2 legend/package mapping, and complete the planned S6 artwork denominator audit.
