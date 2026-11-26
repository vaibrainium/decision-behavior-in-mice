# Report: Choice–RT Pareto refit preparation
Date: 2026-11-26   Agent: Codex   Commit: 00ce548
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Can the Figure 6B pulse-only winner recover the pulse-choice signatures when choice likelihood is given more relative influence, and how much response-time fit must be sacrificed?

## Summary
The checkpointed production sweep and common-scale scorer are prepared but no new model has been fitted or interpreted. The prespecified RT weights are 0.5, 0.25, 0.125 and 0, corresponding to relative choice weights 2, 4, 8 and a choice-only endpoint; the existing weight-1 model is the baseline. The table contains 240 new fits (10 mice × 6 pulse splits × 4 weights), estimated at 420.2 baseline-equivalent compute-hours. Cluster submission remains an author action under repository rules.

## Findings
- VERIFIED: `fit_mouse_ddm` now accepts `--rt_nllh_weight`, records it in each fit, rejects negative/nonfinite values and preserves the production default exactly at 1. Source: `scripts/ddm/fit_mouse_ddm.py`; test: `.venv/bin/python tests/test_choice_rt_weight.py` (3 tests pass).
- VERIFIED: `scripts/slurm/tasks_2026-11-26_choice_weight.csv` contains 240 unique output paths, 60 tasks per weight and no duplicate `(batch,index)`. Every command uses the normalized UGM/no-sv architecture, responded-only pulse splits, 15 repetitions and warm starts from the matching `fits_pulse_norm_ugm` fit. Source/command: `.venv/bin/python -m scripts.slurm.make_choice_weight_tasks --check`.
- VERIFIED: all 60 existing weight-1 baseline fits are present with `rt_nllh_weight=1`. The new scorer registers all four families and currently reports the expected 240 missing new fits. Source/command: `.venv/bin/python -m scripts.paper.score_choice_weight_fits --check`.
- VERIFIED: generated fit command reconstructs a 60-job grid (10 mice × `pcv0`–`pcv4` plus `pulse`) in list-only mode.

## What didn't work
- The repository `.venv` does not include `pytest`, so the existing pytest checkpoint suite could not be rerun without an unauthorized installation. The new tests use standard-library `unittest`; compile, CLI and task-grid smoke checks passed.

## How to reproduce
Prepare/validate only:
```bash
.venv/bin/python tests/test_choice_rt_weight.py
.venv/bin/python -m scripts.slurm.make_choice_weight_tasks --check
.venv/bin/python -m scripts.paper.score_choice_weight_fits --check
```

On the cluster, first inspect the proposed submissions:
```bash
python3 scripts/slurm/autosubmit.py --tasks scripts/slurm/tasks_2026-11-26_choice_weight.csv --state slurm-logs/autosubmit_state_choice_weight.json --dry_run
```
Then, only after reviewing the dry run, the author may start the checkpointed watcher:
```bash
tmux new -s choice-weight 'python3 scripts/slurm/autosubmit.py --tasks scripts/slurm/tasks_2026-11-26_choice_weight.csv --state slurm-logs/autosubmit_state_choice_weight.json --watch 10'
```

After all fits sync locally:
```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore -m scripts.paper.score_choice_weight_fits --output dissemination/paper_accumulation/draft_2026-11-15/choice_rt_pareto_2026-11-26
```

## Caveats
Weighted training objectives and BIC values are not comparable across weights. All selection must use the scorer's original unweighted held-out choice, conditional-RT and joint NLL components. This is exploratory architecture diagnosis, not a confirmatory test. Full-pulse fits are needed for Figure 7 predictions; `pcv` fits are needed for honest held-out comparison.

## Open questions and next steps
- [ ] Author runs the dry run and cluster watcher.
- [ ] Sync and validate all 240 fit files.
- [ ] Run five-seed common-scale scoring, construct the subject-level Pareto frontier and then generate the Figure 7 readouts.
