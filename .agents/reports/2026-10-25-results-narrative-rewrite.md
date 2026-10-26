# Report: Results narrative rewrite
Date: 2026-10-25   Agent: Codex   Commit: 0b76e80 (working tree; neuropaper files uncommitted)
Plan: plans/2026-10-20-paper-writeup.md

## Question
Could the Results be rewritten in a more natural animal-paper narrative without weakening the approved scientific
claims, negative results or scope restrictions?

## Summary
Yes. A versioned Results v4 now follows a question-to-result narrative while retaining the locked thesis, all seven
approved Results claims and all 42 registered number tokens. No analysis, estimate or scientific conclusion changed.
The canonical section is 2,746/2,850 words and all deterministic Results checks pass without warnings.

## Findings

- VERIFIED: v4 preserves C002–C007 and C009, including the relative control-model comparison, randomized pulse effect,
  temporal prediction mismatch, two-mouse C009 restriction, failed gates, low sensitivity and stopped timing test.
  Source: `dissemination/paper/np/drafts/results/v4.md`; compare v3.
- VERIFIED: contract, claim, number, Results-lint, locked-spine and whitespace checks pass. The full workspace retains
  only the existing honest `[MISSING]` warnings in Methods and provisional legends. Commands: `np.py check-contract`,
  `check-claims`, `check-numbers`, `lint`, `check-all`, and `git diff --check` from `dissemination/paper`.
- VERIFIED: the readable snapshot is `dissemination/paper/np/checkpoints/S4_midpoint_results_v2.md`; compound token
  expansions were editorially formatted for readability without changing registered values.

## What didn't work

- The first rewrite was only 1,747 canonical words and read like an extended abstract. Scientific explanation was
  restored without reintroducing repeated procedural caveats.
- The stock renderer appends the ledger unit field to every token, producing phrases such as duplicated units and
  metadata lists for compound tokens. The readable checkpoint was corrected editorially; the tokenized v4 source
  remains authoritative.

## How to reproduce

```bash
cd /src/dissemination/paper
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py check-contract np/drafts/results/v4.md
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py check-claims np/drafts/results/v4.md
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py check-numbers np/drafts/results/v4.md
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py lint np/drafts/results/v4.md
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py check-all
git -C /src diff --check
```

## Caveats

This was an editorial restructuring, not a new independent scientific review. V. Thakur subsequently approved v4 as
D007. Final assembly still needs a general solution for compound number-token display.

## Open questions and next steps

- [x] Author verified `np/checkpoints/S4_midpoint_results_v2.md` for voice and scientific fidelity (D007).
- [x] Results returned to `passed`.
- [ ] Draft Discussion under the approved G3 brief.
- [ ] Resolve compound token display before final manuscript assembly.

