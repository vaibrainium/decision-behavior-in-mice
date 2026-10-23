# Report: paper story, figure arrangement and caption draft
Date: 2026-10-23   Agent: Codex   Commit: 84fedd7 (evidence snapshot; later input/pilot commits arrived during drafting)
Plan: [paper write-up](../plans/2026-10-20-paper-writeup.md), N–R

## Question
What paper can be written from the completed results, how should the main figures build its argument, and what should their captions say?

## Summary
Drafted a story that connects the control-trial preference for the tested accumulator to a model-independent directional pulse effect and a specific temporal prediction failure. Proposed five main figures, merging the old stimulus/hidden-coherence displays to give two main figures to pulses. Wrote complete proposed main captions, production notes and alt text, with supplementary content briefs. The new files preserve the existing manuscript/captions and do not incorporate an unevaluated model pilot.

## Outputs
- [Story, Results sequence and panel arrangement](../../dissemination/paper/story_and_figures_2026-10-23.md).
- [Main-figure captions and supplementary briefs](../../dissemination/paper/figure_captions_story_2026-10-23.md).
- [Sources](../../dissemination/paper/story_sources_2026-10-23.json), [claims](../../dissemination/paper/story_claims_2026-10-23.csv), [checks/source hashes](../../dissemination/paper/story_checks_2026-10-23.json).

## Findings
- VERIFIED: proposed numeric pulse captions reproduce the saved C/D/E tables, including Holm-corrected effects, the distinction between fixed-deadline and pulse-aligned endpoints, and held-out choice versus remaining-objective costs. The source JSON records exact rows/fields; the check JSON records hashes.
- VERIFIED: the primary signed contrast uses 10,281 supported pulse trials in 717 cells, retaining 118 pre-onset responses and 1,709 unresponded trials. These are sums of `behaviour/coverage.csv` rows where `analysis_set == primary_coherence`, not new analysis results.
- VERIFIED: source schema, all ten formal claim hashes and local document links pass; numerical source files remained unchanged during verification. `git diff --check` passes. Human evidence verification is explicitly incomplete.
- PROPOSED: figure count, panel arrangement, emphasis and new display conventions. The main composites are not rendered; caption descriptions of proposed panels must be reconciled with the future exports. Existing graphics were inspected as source figures.
- EDITORIAL RECOMMENDATION: retain failed gates and the unreached primacy test in main Results; give their detailed displays supplementary space. Do not turn cumulative pulse-response timing into a measured neural time constant, the tested replay alternatives into a universal stimulus bound, or the two-mouse gain tradeoff into a whole-cohort mechanism claim.

## What didn't work / outstanding limitations
The old outline has stale stronger claims and predates the completed follow-up, so it was preserved rather than silently overwritten. The new arrangement requires an audited Figure 1 control mask and a completed or clearly limited hidden-coherence scheduled-control sensitivity. New uncertainty displays need rendering, not just caption edits. The selected journal is unresolved. Input correction and a pilot specification were committed during drafting (`6b4cf2b`, `a5583fc`); the numeric captions remain tied to the recorded A–E/G1 outputs and must be updated together if the coordinator supplies revised results.

## How to reproduce the checks
No fitting, rendering or analysis pipeline was rerun. Sources are existing outputs under `/mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/`; numeric checks selected `behaviour/group.csv`, `behaviour/coverage.csv`, `response_time/contrast_table.csv`, `diagnostics/e4_model_vs_D_summary.csv` and `diagnostics/e3_optima.csv`. Exact selectors are in the source locators. Check links and claim text using:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from pathlib import Path
import csv, hashlib, json, re, sys
sys.path.insert(0, '.claude/skills/scientific-writing/scripts')
from audit_claims import claim_text_hash
from validate_manifest import validate_source_manifest
p = Path('dissemination/paper')
sources = json.loads((p/'story_sources_2026-10-23.json').read_text())
assert not [i for i in validate_source_manifest(sources, require_verified=False) if i.severity == 'error']
current = {}
for name in ['story_and_figures_2026-10-23.md', 'figure_captions_story_2026-10-23.md']:
    text = (p/name).read_text()
    for line in text.splitlines():
        m = re.search(r'\[claim:(C\d+)\]', line)
        if m: current[m.group(1)] = claim_text_hash(line)
    for link in re.findall(r'\]\(([^)]+)\)', text):
        link = link.strip('<>')
        if '://' not in link: assert (p/link).resolve().exists(), link
with (p/'story_claims_2026-10-23.csv').open() as f:
    for row in csv.DictReader(f):
        assert current[row['claim_id']] == row['claim_text_sha256']
checks = json.loads((p/'story_checks_2026-10-23.json').read_text())
for source in checks['sources']:
    assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest() == source['sha256'], source['path']
print('Draft records match; human verification and figure rendering remain pending.')
PY
git diff --check
```

Future changes to an evidence file should make the hash check fail and trigger a review; do not update hashes automatically without checking affected captions.

## Caveats
These are discussion-ready documents, not submission-ready figures or journal-compliant legends. Public Stine et al. primary-paper, ARRIVE and Scientific Agent Skills metadata were opened; unpublished data were not sent to external services. Skill attribution is in the story document's workflow note. Existing manuscript claim registries were not edited.

## Venue and thesis addendum — 2026-10-23

Author preference: provisional eLife target and an expanded thesis account of what worked and did not. Added a seven-section thesis outline, paper-to-thesis figure mapping, and guidance separating predictive failures, low sensitivity, weak identification and technical corrections. This is an editorial addition; formal scientific claims and their numeric sources remain unchanged. The earlier unresolved-journal note is superseded by a provisional preference, not a final submission decision.

VERIFIED: consulted the current [official eLife author guide](https://elife-rp.msubmit.net/html/elife-rp_author_instructions.html), specifically Research Articles, Abstract, and Figures and figure supplements, and the [submission process](https://elifesciences.org/about/submit-your-research). The linked outline records the applicable guidance; the five-main-figure recommendation is ours. No journal submission or figure export occurred. Caption claim hashes, source schema and local links rechecked; scientific input hashes are not refreshed by this editorial pass. The coordinator's STATUS and pulse plan remain untouched.

Next: use this outline to discuss title emphasis and chapter depth, then integrate the agreed structure into the manuscript. Preserve the same scientific conclusions and material limitations in paper and thesis.

## Open questions and next steps
- [ ] Authors settle the title emphasis and confirm the provisional eLife target; supply institutional thesis requirements when formatting is needed.
- [ ] Approve or revise the figure arrangement; then assemble figures from source tables and reconcile captions.
- [ ] Complete the Figure 1/2 mask checks and add any evaluated corrected-input/pilot result with its limits.
- [ ] Integrate this structure into the next manuscript version and its claim registry.
- [ ] Pulse coordinator adds this writing handoff to STATUS without replacing the active analysis focus; this pass preserves coordinator ownership of that file.
