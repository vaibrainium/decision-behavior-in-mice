# Plan: checkpoint and resume DDM fits
Status: done
Created: 2026-11-08 by Claude (Opus 5.5)
Related reports: none yet. Context: plans/2026-11-06-input-mapping-x-accumulator.md log (ckpt-all preemptions, 373.5 h lost)

## Goal
Author request 2026-11-08: a fit that is preempted or requeued resumes where it stopped instead of starting from zero.
Done = fit_mouse_ddm writes a checkpoint every differential-evolution (DE) generation and after DE, resumes from it, and
a resumed fit gives the same result as an uninterrupted one (tested locally), with no change to fits that are never
interrupted.

## Context
- DecisionModel.fit (src/ddm/ddm.py): scipy differential_evolution (polish off), then Nelder-Mead refinement; objective
  deterministic given the common random numbers drawn after _set_seed(self.seed).
- DE mutable state between generations (scipy 1.15.3 DifferentialEvolutionSolver): population (unit scale),
  population_energies, feasible, constraint_violation, random_number_generator, _nfev. Plus our running best (best_nll,
  best_vals) and the generation count.
- Fits are skipped when the output .pkl exists; outputs are written atomically.

## Assumptions
- Same GPU model on restart gives bit-identical objectives; a different GPU model may differ in the last float bits
  (true already without checkpoints: a restarted fit can land on another GPU).
- Hyak runs the same scipy (uv.lock pins 1.15.3). VERIFIED 2026-11-08: toy tests pass in the Hyak container (srun job 43051219).

## Steps
- [x] 1. DecisionModel.fit: run DifferentialEvolutionSolver directly (same arguments as differential_evolution), optional
      `checkpoint` path: save state atomically after each generation (unless converged / last generation) and after
      DE (stage "refine"); on start, load a checkpoint whose fingerprint (fit keys, bounds, settings, seed, data and
      stimulus hash, warm-start seeds) matches, else ignore it with a warning. n_iterations counts all generations.
- [x] 2. fit_mouse_ddm.run_job: checkpoint at <out_dir>/<mouse>_<variant>_<split>.ckpt; deleted after the result is saved;
      result records resumed_from_generation.
- [x] 3. Verify locally: (a) no checkpoint: identical to scipy differential_evolution on a toy function and to the old
      code on a short real fit; (b) interrupted after k generations then resumed: identical result to uninterrupted
      (real fit, small max_iterations); (c) mismatched checkpoint ignored; (d) interrupt during refinement resumes there.
- [x] 4. Commit; give the author the pull command. Pending tasks pick it up; running tasks get it at their next restart.

## Out of scope
Checkpointing inside Nelder-Mead (short relative to DE); model_recovery / primacy_sensitivity (they can pass a path later).

## Log
- 2026-11-08: plan written.
- 2026-11-08: implemented. First resume test failed: scipy's solver also keeps _random_population_index (shuffled in
  place between generations); now saved. Tests (python -m tests.test_fit_checkpoint [--real]) all pass: step-by-step
  DE == scipy differential_evolution (maxiter 0/1/7/300); toy fit killed in generation 1/12/25 then resumed == uninterrupted;
  real fit PSUIM10 cv0 norm L1U1V1Z0G1 (n_reps 2, 6 generations, responded likelihood): uninterrupted, resumed at
  generation 3, resumed after DE all give train 591.1979745571091 / test 56.36794951275008, identical to the pre-change code
  run from the command line; a checkpoint of another fit is ignored. Sync script excludes *.ckpt. fit_seconds now = the
  last attempt only. Next: step 4 (author pulls on Hyak, runs the toy test in the container to confirm scipy 1.15).
- 2026-11-08: author ran tests.test_fit_checkpoint in the Hyak container on a compute node (srun job 43051219): both
  toy checks ok (singularity cannot start on the login node: /var/run/slurm mount). Plan done; no report needed beyond this log.
- 2026-11-08: in use on Hyak (author's sacct + logs): 9 of 9 checked norm fits resumed from their checkpoints, e.g.
  43015177_35 DBM6 cv0 at generation 553 (after a 3:52 preemption), 8 others at generations 142-215 at 05:47. The ~8 h
  ckpt-all cutoff is now VERIFIED as a pattern: 8 jobs started 2026-11-07 21:42:55 were all REQUEUED at elapsed 08:02:06-07
  (same moment); 43030945_235 earlier lost attempts of 08:06 and 08:12. Fits needing > 8 h finish over several attempts.
- 2026-11-08: BUG found and fixed: c902211 placed the module-level helpers inside DecisionModel, turning simulate() into
  dead code (AttributeError in pulse_joint_signatures). Fits unaffected (fit/heldout never call simulate; real-fit test
  passed); any simulation from fitted parameters with code between c902211 and the fix failed loudly (no silent wrong
  numbers). The explore_partial pulse run predates c902211 (module imported before the edit). Test now checks the methods.
