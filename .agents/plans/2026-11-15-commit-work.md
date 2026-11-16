# Plan: commit accumulated work in reviewable chunks
Status: done
Created: 2026-11-15 by Codex (client date)
Related reports: ../reports/2026-11-15-commit-work.md; ../reports/2026-11-16-figures-first-draft.md; ../reports/2026-11-15-nhp-pulse-hmm-pilot.md

## Goal
Commit all tracked modifications and nonignored accumulated work in focused scientific/code/documentation commits, preserve existing results and manuscript versions, and finish with a clean working tree. No push.

## Context
Author explicitly requests committing everything so far in digestible chunks. Work includes evidence audits, pulse diagnostics, literature, delay/gain/history/HMM code and outputs, publication direction and a figures-first manuscript packet. Current branch mouse-motion-energy, starting HEAD b63c9d9. Client date is November 15; some existing artifacts are labeled November 16 by the execution environment and will retain their original provenance dates.

## Assumptions
- Explicit user authorization covers local git add/commit of this accumulated work, including scientific outputs and drafts.
- Do not stage ignored data/environments, edit raw inputs, install packages, rerun model fits or push commits.
- Preserve generated tables, logs and earlier layout/draft versions unless they contain actual credentials; inspect content without printing secrets.

## Steps
- [x] 1. Read status, current writing plan/recent reports, git status/log and file-size inventories.
- [x] 2. Inspect all candidate files, check for secrets/temporary data and validate code/tests appropriate to the checkpoint.
- [x] 3. Define and record nonoverlapping commit groups covering the full working set.
- [x] 4. Commit groups sequentially with concise descriptions; verify staged content before each commit.
- [x] 5. Save a commit map/report, update STATUS and verify git log and a clean working tree.

## Out of scope
New scientific analysis, model fitting, deleting historical output versions, dependency changes, remote publication/push or finishing the remaining manuscript sections.

## Log
- 2026-11-15: Started on the author's explicit commit request. Inventory is about 98 MiB of nonignored untracked work; two derived RT histogram CSVs are the largest files. No secrets printed. All groups will be committed locally; no push authorized.
- 2026-11-15: Defined 12 disjoint scientific/code/manuscript commits plus a final handoff commit in /tmp/decision_commit_groups.json. All current nonignored paths are covered exactly once. Largest derived CSV is about 45 MiB; preserve it with its diagnostic sources as requested. No ignore rules changed.
- 2026-11-15: Preflight scanned 647 candidate files with no high-confidence credential patterns, invalid Python/JSON or symlinks. Five focused test modules passed in the original environment; the SSM emission test requires the intentionally separate NHP environment and is being checked there. No dependency changes.
- 2026-11-15: Six focused test modules passed in intended environments; SSM-specific emissions passed in /mnt/data/venvs/nhp-glmhmm-2026-11-15. DOCX XML/metadata scan also found no credential patterns. Python syntax and JSON parse checks passed. Proceeding with 12 topic commits and a final handoff commit; no push.
- 2026-11-15: Created all 12 topic commits sequentially; hashes and paths are in ../reports/2026-11-15-commit-map.json. Final handoff commit includes this completed plan, the map, test/preflight records and STATUS. Verify final tree immediately after committing; no push.
