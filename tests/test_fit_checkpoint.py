"""Checks for checkpoint / resume of DecisionModel.fit (plans/2026-11-08-fit-checkpointing.md).

  toy (fast, no data):  python -m tests.test_fit_checkpoint
    1. the step-by-step DE loop (DecisionModel._run_de) gives exactly scipy's differential_evolution(seed=...) result;
    2. a DE run killed mid-generation and resumed from its checkpoint gives exactly the uninterrupted result.
  real fit (needs the processed data, ~10 min on CPU):  python -m tests.test_fit_checkpoint --real
    3. fit_mouse_ddm.run_job on PSUIM10 cv0, norm front end, leak+urgency, n_reps 2, 6 generations: uninterrupted;
       killed in generation 4 then rerun (resumes at 3); killed in the refinement then rerun (resumes after DE);
       all three give the same train and held-out NLL and parameters; a checkpoint from another fit is ignored.
"""

import argparse
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.optimize import differential_evolution, rosen
from scipy.optimize._differentialevolution import DifferentialEvolutionSolver

from src.ddm.ddm import DecisionModel, _load_checkpoint, _restore_solver

BOUNDS = [(-2.0, 2.0)] * 5
BASELINE = (591.1979745571091, 56.36794951275008)  # tests 3: PSUIM10 cv0 norm L1U1V1Z0G1 n_reps 2, 6 generations, old code, CPU
SETTINGS = dict(popsize=15, tol=0.0, atol=1e-3, polish=False, disp=False)


class Killed(Exception):
    pass


def run(objective, max_iterations, ckpt=None, kill_at=None):
    """DecisionModel._run_de on `objective`, optionally resuming from / writing `ckpt`, raising Killed at evaluation kill_at."""
    calls = [0]
    best_nll, best_vals = [np.inf], [None]

    def f(x):
        calls[0] += 1
        if kill_at is not None and calls[0] == kill_at:
            raise Killed
        v = objective(x)
        if v < best_nll[0]:
            best_nll[0], best_vals[0] = v, np.array(x, dtype=float)
        return v

    solver = DifferentialEvolutionSolver(f, BOUNDS, maxiter=max_iterations, rng=np.random.RandomState(42), **SETTINGS)
    iteration = [0]
    state = _load_checkpoint(ckpt, "fp")
    if state is not None:
        _restore_solver(solver, state)
        best_nll[0], best_vals[0] = state["best_nll"], state["best_vals"]
        iteration[0] = state["generation"]
    dummy = SimpleNamespace(fit_keys=[f"x{i}" for i in range(len(BOUNDS))])
    return DecisionModel._run_de(dummy, solver, max_iterations, iteration, best_nll, best_vals, False, ckpt, "fp"), state


def same(a, b):
    assert np.array_equal(a.x, b.x), (a.x, b.x)
    assert a.fun == b.fun and a.nit == b.nit and a.nfev == b.nfev and a.success == b.success, (a, b)
    assert np.array_equal(a.population, b.population) and np.array_equal(a.population_energies, b.population_energies)


def test_matches_scipy():
    for maxiter in (0, 1, 7, 300):  # 300: stops on convergence
        ref = differential_evolution(rosen, BOUNDS, maxiter=maxiter, seed=42, **SETTINGS)
        mine, _ = run(rosen, maxiter)
        same(mine, ref)
        assert mine.message == ref.message, (mine.message, ref.message)
    print("ok: step-by-step DE == scipy differential_evolution (maxiter 0, 1, 7, 300)")


def test_resume():
    full, _ = run(rosen, 40)
    pop = 15 * len(BOUNDS)
    tmp = Path(tempfile.mkdtemp())
    try:
        for kill_at in (pop + 3, pop * 12 + 40, pop * 25 + 1):  # in generation 1, 12, 25
            ckpt = tmp / f"k{kill_at}.ckpt"
            try:
                run(rosen, 40, ckpt, kill_at)
                raise AssertionError("not killed")
            except Killed:
                pass
            resumed, state = run(rosen, 40, ckpt)
            if kill_at <= 2 * pop:  # killed before the first checkpoint: starts over
                assert state is None or state["generation"] == 0
            else:
                assert state["generation"] == (kill_at - pop - 1) // pop, state["generation"]
            same(resumed, full)
        print("ok: killed in generation 1, 12, 25 of 40 and resumed == uninterrupted")
    finally:
        shutil.rmtree(tmp)


def test_real():
    import torch

    import scripts.ddm.fit_mouse_ddm as F
    from config import dir_config

    processed = Path(dir_config.data.processed)
    inputs = F.responded_only(F.load_inputs(processed / "ddm/ddm_inputs_global_ucla_nofreeze.npz"))
    job = {"mouse": "PSUIM10", "variant": "L1U1V1Z0G1", "split": "cv0"}
    kw = dict(n_reps=2, max_iterations=6, guess_model="fast_only", front_end="norm", likelihood_params=F.RESPONDED_LIKELIHOOD_PARAMS)  # = --responded_only
    tmp = Path(tempfile.mkdtemp())
    original = F.MouseDDM._objective_function

    def killed_run(out, kill_at):
        calls = [0]

        def obj(self, *a, **k):
            calls[0] += 1
            if calls[0] == kill_at:
                raise Killed
            return original(self, *a, **k)

        F.MouseDDM._objective_function = obj
        try:
            F.run_job(inputs, job, out, **kw)
            raise AssertionError("not killed")
        except Killed:
            pass
        finally:
            F.MouseDDM._objective_function = original
        assert F.checkpoint_path(out, job).exists()
        return F.run_job(inputs, job, out, **kw)

    try:
        full = F.run_job(inputs, job, tmp / "full", **kw)
        assert full["resumed_from_generation"] is None and not F.checkpoint_path(tmp / "full", job).exists()
        # the code before checkpointing (commit c4d48b8), same fit from the command line, gave exactly these on the same machine
        assert (full["train_nll"], full["test_nll"]) == BASELINE, (full["train_nll"], full["test_nll"])
        n_free = len(full["free_parameters"])
        pop = 15 * n_free
        mid = killed_run(tmp / "mid", pop * 4 + 20)  # in generation 4
        late = killed_run(tmp / "late", pop * 7 + 2)  # DE ends after 6 generations (1 + 6 populations): early in the refinement
        assert mid["resumed_from_generation"] == 3, mid["resumed_from_generation"]
        assert late["resumed_from_generation"] == -1, late["resumed_from_generation"]
        for name, r in (("mid", mid), ("late", late)):
            assert r["train_nll"] == full["train_nll"] and r["test_nll"] == full["test_nll"], (name, r["train_nll"], full["train_nll"], r["test_nll"], full["test_nll"])
            assert r["parameters"] == full["parameters"] and r["n_iterations"] == full["n_iterations"], name
            assert not F.checkpoint_path(tmp / name, job).exists(), name
        # a checkpoint from another fit (split cv1, killed in generation 2) is ignored
        other = tmp / "other"
        other.mkdir()
        shutil.copy(_make_ckpt(F, inputs, kw, tmp, pop), F.checkpoint_path(other, job))
        r = F.run_job(inputs, job, other, **kw)
        assert r["resumed_from_generation"] is None and r["train_nll"] == full["train_nll"]
        print(f"ok: real fit uninterrupted / resumed at generation 3 / resumed after DE: train NLL {full['train_nll']:.6f}, "
              f"test NLL {full['test_nll']:.6f} in all three; foreign checkpoint ignored")
    finally:
        F.MouseDDM._objective_function = original
        shutil.rmtree(tmp)
        torch.cuda.empty_cache() if torch.cuda.is_available() else None


def _make_ckpt(F, inputs, kw, tmp, pop):
    """A checkpoint of PSUIM10 cv1 (another fit), killed in generation 2."""
    out = tmp / "x"
    job = {"mouse": "PSUIM10", "variant": "L1U1V1Z0G1", "split": "cv1"}
    original = F.MouseDDM._objective_function
    calls = [0]

    def obj(self, *a, **k):
        calls[0] += 1
        if calls[0] == pop * 2 + 5:
            raise Killed
        return original(self, *a, **k)

    F.MouseDDM._objective_function = obj
    try:
        F.run_job(inputs, job, out, **kw)
    except Killed:
        pass
    finally:
        F.MouseDDM._objective_function = original
    return F.checkpoint_path(out, job)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="also run the real-fit test (needs processed data, ~10 min)")
    args = ap.parse_args()
    test_matches_scipy()
    test_resume()
    if args.real:
        test_real()
