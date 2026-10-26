# Report: editable notebooks for the five main figures
Date: 2026-10-26   Agent: Codex   Commit: b4cd5b0
Plan: plans/2026-10-20-paper-writeup.md (task AC)

## Question
Can each selected main figure be exposed as a maintainable notebook with one independently editable section per labeled panel, without duplicating or silently changing the canonical publication logic?

## Summary
Five notebooks now wrap the tested modules in `scripts/paper/`, prepare shared data once, and give every labeled panel its own Markdown heading and code cell. Figures 1–2 expose panels A–E; Figures 3–5 expose panels A–D. All five notebooks execute successfully with the project virtual environment. Source notebooks retain no outputs and contain no export calls, so running them cannot overwrite the selected artwork.

## Findings
- VERIFIED: dedicated notebooks are in `dissemination/paper/notebooks/`: `Figure_1_task_behaviour.ipynb`, `Figure_2_stimulus_reconstruction.ipynb`, `Figure_3_control_models.ipynb`, `Figure_4_pulse_behaviour.ipynb`, and `Figure_5_model_mismatch.ipynb`. Source: direct JSON inspection at commit b4cd5b0.
- VERIFIED: Figures 1–2 contain 15 cells each and panel sequences A–E; Figures 3–5 contain 13 cells each and panel sequences A–D. Every panel heading is followed by a code cell. Source: structural check in the command below.
- VERIFIED: every notebook executed to completion through `nbconvert` using a temporary kernelspec whose executable is `/src/.venv/bin/python` (NumPy 1.26.4, Matplotlib 3.10.3, ipykernel 6.29.5). Executed copies were written only to `/tmp/figure-notebook-checks`.
- VERIFIED: source code cells have null execution counts and empty outputs, and no notebook cell contains `savefig`. Source: structural check below.

## What didn't work
- The default system Jupyter kernel uses global Python 3.10 with NumPy 2.2.6 and a Matplotlib extension built for NumPy 1.x; execution failed during `%matplotlib inline` with `ImportError: numpy.core.multiarray failed to import`. This is an environment mismatch, not a panel-code failure. Validation therefore used a temporary kernelspec pointing at the existing project virtual environment. No package was installed or changed.

## How to reproduce
From `/src`, create a temporary kernelspec and execute copies without modifying the source notebooks:

```bash
.venv/bin/python -m ipykernel install --prefix /tmp/codex-figure-kernel --name project-venv --display-name "Python 3 (project venv)"
JUPYTER_PATH=/tmp/codex-figure-kernel/share/jupyter /usr/local/bin/jupyter-nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=project-venv --ExecutePreprocessor.timeout=300 --output-dir=/tmp/figure-notebook-checks dissemination/paper/notebooks/Figure_1_task_behaviour.ipynb dissemination/paper/notebooks/Figure_2_stimulus_reconstruction.ipynb dissemination/paper/notebooks/Figure_3_control_models.ipynb dissemination/paper/notebooks/Figure_4_pulse_behaviour.ipynb dissemination/paper/notebooks/Figure_5_model_mismatch.ipynb
```

The structural validation parsed each file with Python's `json` module, checked nbformat 4.4 and kernel metadata, asserted the panel-heading/code-cell pairing, asserted null execution counts and empty outputs, and rejected any cell containing `savefig`.

## Caveats
- The notebooks are interfaces to canonical figure modules, not independent analysis implementations. Changes to shared transformations or final export composition should be made and tested in `scripts/paper/`; notebooks are intended for panel-level exploration.
- Opening the notebooks with the global `python3` kernelspec may reproduce the NumPy/Matplotlib mismatch. Select `/src/.venv/bin/python` (display name `Python 3 (project venv)`) in the editor.

## Open questions and next steps
- [ ] Author visually reviews the five notebooks and selected main figures.
- [x] Commit the notebooks as b4cd5b0; commit the task-AC handoff separately so the artifact history remains atomic.

