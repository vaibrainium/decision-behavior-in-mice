# Report: checkpoint accumulated work in focused commits
Date: 2026-11-15 (client date)   Agent: Codex
Commit: this handoff commit; previous topic commit 0abaa8e0
Plan: plans/2026-11-15-commit-work.md

## Question
Commit everything accumulated so far in digestible chunks, without pushing.

## Summary
Twelve topic commits preserve the scientific code, tests, derived outputs, literature, HMM work and manuscript packet. This additional handoff commit records their map and current status. Earlier output/draft versions are retained. Ignored data, environments and caches are not added. No remote push, new model fit, dependency installation or raw-data change.

## Commit map
| # | Commit | Scope |
|---|---|---|
| 1 | `f3c85275` | Audit completed control comparisons and paired strategy recovery |
| 2 | `de315ec1` | Compare pulse persistence with fixed accumulation models |
| 3 | `e089f685` | Decompose held-out pulse choice and reaction-time tradeoffs |
| 4 | `0540d128` | Review attention and decision-dynamics mechanisms |
| 5 | `f72a6cc2` | Add and evaluate a variable postdecision-delay model |
| 6 | `d9a56983` | Add positive evidence-gain variability and feasibility checks |
| 7 | `70a2dba2` | Audit trial chronology and compare persistent choice-bias models |
| 8 | `b1b2762c` | Prepare six pulse-type inputs and pin NHP SSM provenance |
| 9 | `f2560160` | Fit and assess the pulse-input GLM-HMM pilot |
| 10 | `18d6a5aa` | Define the accumulation-first paper and retain pulse-persistence evidence |
| 11 | `2fb072f8` | Assemble source-linked main figures for the accumulation paper |
| 12 | `0abaa8e0` | Draft figure captions, Methods and Results with evidence records |
| 13 | this commit | Commit map, validation record and updated STATUS |

Machine-readable paths, file counts and commit hashes: `reports/2026-11-15-commit-map.json`. Starting HEAD: `b63c9d919edc85e48446be48a8399ba6304b8df0`; branch: `mouse-motion-energy`. Existing artifact dates labeled November 16 are preserved; this report uses the current client date.

## Findings and verification
- VERIFIED: all initial nonignored modified/untracked paths were assigned to disjoint topic groups or final handoff documentation. Source: commit-map JSON and `git diff --name-only b63c9d9..HEAD`.
- VERIFIED: preflight scanned 647 candidate files, including 577 text files, with no high-confidence credential pattern, invalid Python/JSON or symlink findings. DOCX XML/metadata was separately scanned. This is a bounded pattern check, not a proof that a repository contains no sensitive information. Source: `reports/2026-11-15-commit-checks.json`.
- VERIFIED: six focused scientific test modules pass in their intended environments. The five non-SSM modules passed in `.venv`; the SSM emission module passed in the isolated NHP environment. Python whitespace checks passed before every topic commit. Source: commit-checks JSON; commands below.
- VERIFIED: generated tables and prior layout/draft versions were kept with related code. The large RT histogram sources remain in the RT-diagnostics commit; no scientific output was rewritten to reduce diffs.
- DECISION: this checkpoint does not change the publication argument or reopen prior scientific gates. Next writing step remains Introduction, Discussion, Summary and final title from the figures-first packet.

## What did not work
- Running the SSM-specific test in the original DDM environment failed because that environment intentionally lacks ssm. The identical test passed in `/mnt/data/venvs/nhp-glmhmm-2026-11-15`; no installation or change to the original environment.
- No active git hooks required extra tooling. Git author identity was already configured; no identity settings changed.

## How to reproduce

```bash
git log --reverse --oneline b63c9d9..HEAD
git status --short
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m tests.test_response_delay
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m tests.test_evidence_gain
.venv/bin/python -m tests.test_history_dynamics
.venv/bin/python -m tests.test_predictive_bias_states
.venv/bin/python -m tests.test_pulse_feature_encoding
/mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m tests.test_nhp_pulse_observations
```

All staging used explicit per-group path lists; every staged list was checked against its group before committing. No remote operation performed.

## Caveats
This is a local source-control checkpoint, not publication approval. The manuscript still contains explicit author-detail fields, and human source verification remains pending. Data/model inputs outside the repository and intentionally ignored environments remain dependencies documented by the scientific manifests.

## Open questions and next steps
- [ ] Continue the manuscript's remaining sections from `dissemination/paper_accumulation/draft_2026-11-15/working_draft_v3.docx` and the native-size figure PDF.
- [ ] Push only if the author requests it.
