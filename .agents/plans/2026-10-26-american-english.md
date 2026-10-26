# Plan: Convert manuscript-facing text to American English
Status: active
Created: 2026-10-26 by Claude
Related reports: reports/2026-10-26-neuropaper-s5-s6.md

## Goal
Every manuscript-facing text (section drafts, rendered ledger fields, locked spine, config, Word review copies) uses
American spelling, with no change to wording, numbers, claims or citations.

## Context
User request (2026-10-26): "can you update everything to use american english?". Paper is waiting at G5 (S6).
Assembler `scripts/paper/assemble_neuropaper.py` renders the highest `vN.md` per section, so drafts get new versions
(no-overwrite rule). Thesis contains "favoured", so the locked spine changes and must be re-locked.

## Assumptions
- Spelling-only edits are covered by the user's request and need no reviewer round; verified by a word-level diff
  that shows only mapped spelling pairs.
- Historical records (reviews, panel reports, audits, checkpoints, reports, decisions) stay as written.
- Code spans, file paths and identifiers (e.g. `fig1_task_behaviour`, `per_mouse.csv`) are not changed.

## Steps
- [x] 1. Deterministic converter with an explicit British→American word map; mask backtick spans; underscores/paths
        untouched.
- [x] 2. New draft versions for all 7 sections (contract thesis updated).
- [x] 3. Ledgers: claims.csv text fields, numbers.csv label/value/unit fields only (source_file untouched).
- [x] 4. Spine (locked block + glossary/promises) and config.md; add "Spelling: American English" to config;
        log decision D010; `np.py lock-spine`.
- [x] 5. Reassemble manuscript.md and marked copy; `np.py check-all`; diff check shows spelling pairs only.
- [x] 6. Regenerate Word review copies (new dated suffix, no overwrite).
- [ ] 7. Figure artwork strings (Fig 2 "labelled", Fig 3 "favours"): ask user; regenerating changes selected
        versions and provenance N105–N107.
- [x] 8. Verify: grep shows no mapped British forms in manuscript.md outside code spans.

## Out of scope
Rewording (e.g. "while" vs "whilst" style choices beyond spelling), historical records, figure regeneration unless
approved.

## Log
- 2026-10-26: First CSV pass rewrote line endings/quoting; ledgers restored from git and converter changed to edit raw
  records (diff now spelling-only, 9 lines). Added doubled-l whole-token forms after final scan found "equalled".
  New drafts: discussion v3, end_matter v2, figure_legends v6, introduction v3, methods v5, results v6,
  title_abstract v4. Spine re-locked 3e0ebc561cae58d1 (D010). check-all 0 errors; manuscript word count unchanged
  (11198). Word copies: review/*_2026-10-26_v2.docx. Step 7 (figure artwork) awaiting user decision.
