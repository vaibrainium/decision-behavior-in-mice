"""
ddm_simple.py - Simplified DDM simulation and fitting engine.

Classes
-------
ParamSpec            (default, bounds) for a free parameter
LikelihoodCalculator quantile-based NLL
DecisionModel        abstract fitting engine (subclass in ddm_model.py)

Parameters are passed as plain dicts. Use DEFAULT_PARAMS as a base and
override keys as needed. validate_params() checks required fields.
"""

from __future__ import annotations
import hashlib
import logging
import os
import pickle
import warnings
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from scipy.optimize import OptimizeResult, minimize
from scipy.optimize._differentialevolution import DifferentialEvolutionSolver
from scipy.stats import qmc

from .simulator import DriftDiffusionSimulator
from .likelihood_calculator import LikelihoodCalculator
from .likelihood_calculator_censored import CensoredQMLE
from .likelihood_calculator_qmle import LikelihoodCalculator as QMLELikelihoodCalculator

LIKELIHOOD_CALCULATORS = {"qmle": QMLELikelihoodCalculator, "kl": LikelihoodCalculator, "qmle_censored": CensoredQMLE}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIGNED_COH_COL: int = 0  # column index of coherence in the stimulus array

REQUIRED = {
    "ndt",
    "a",
    "z",
    "drift_gain",
    "drift_offset",
    "variance",
    "dt",
    "leak_rate",
    "time_constant",
    "sv",
    "sz",
}

# ---------------------------------------------------------------------------
# Parameters as plain dict
# ---------------------------------------------------------------------------


def validate_params(p: dict) -> None:
    for k in REQUIRED:
        if k not in p:
            raise ValueError(f"Missing {k}")
    if not (0 < p["a"] < 10):
        raise ValueError(f"Invalid boundary separation: {p['a']}")
    if not (0 < p["z"] < 1):
        raise ValueError(f"Invalid starting point: {p['z']}")
    if not (0 < p["dt"] < 0.01):
        raise ValueError(f"Invalid time step: {p['dt']}")
    if p["ndt"] < 0:
        raise ValueError(f"Invalid non-decision time: {p['ndt']}")
    if not (0 < p["variance"]):
        raise ValueError(f"Invalid variance: {p['variance']}")
    if p["sv"] < 0:
        raise ValueError(f"Invalid sv (drift variability): {p['sv']}")
    if not (0 <= p["sz"] < 1):
        raise ValueError(f"Invalid sz (starting point variability): {p['sz']}")
    if not (0 <= p.get("p_guess", 0.0) < 1):
        raise ValueError(f"Invalid p_guess: {p['p_guess']}")
    if not (0 <= p.get("guess_bias", 0.5) <= 1):
        raise ValueError(f"Invalid guess_bias: {p['guess_bias']}")
    if p.get("p_guess", 0.0) > 0 and not p.get("guess_tau", 0.0) > 0:
        raise ValueError(f"Invalid guess_tau: {p.get('guess_tau')}")
    if not (0 <= p.get("p_lapse", 0.0) < 1 - p.get("p_guess", 0.0)):
        raise ValueError(f"Invalid p_lapse: {p.get('p_lapse')} (with p_guess {p.get('p_guess', 0.0)})")


def apply_guesses(sim: pd.DataFrame, params: dict, draws: np.ndarray) -> pd.DataFrame:
    """Contaminant components that replace a trial's DDM outcome:
      fast guess  with probability p_guess: choice 1 with probability guess_bias, at RT = guess_t0 + an exponential
                  delay with mean guess_tau (s);
      lapse       with probability p_lapse: choice 1 with probability guess_bias, at an RT uniform between lapse_t0
                  and lapse_t1 (s).

    `draws` is (n_trials, 3) uniform [0, 1): which component (u0 < p_guess: guess; p_guess <= u0 < p_guess + p_lapse:
    lapse), the choice, and the delay. Passing the same draws on every evaluation keeps the objective deterministic in
    the parameters (common random numbers).
    """
    p_guess, p_lapse = float(params.get("p_guess", 0.0)), float(params.get("p_lapse", 0.0))
    if p_guess <= 0 and p_lapse <= 0:
        return sim
    choice = (draws[:, 1] < float(params.get("guess_bias", 0.5))).astype(float)
    is_guess = draws[:, 0] < p_guess
    is_lapse = ~is_guess & (draws[:, 0] < p_guess + p_lapse)
    rt = np.asarray(sim["rt"], dtype=float).copy()
    if p_guess > 0:
        rt[is_guess] = float(params.get("guess_t0", 0.0)) - float(params["guess_tau"]) * np.log1p(-draws[is_guess, 2])
    if p_lapse > 0:
        t0, t1 = float(params.get("lapse_t0", 0.0)), float(params["lapse_t1"])
        rt[is_lapse] = t0 + (t1 - t0) * draws[is_lapse, 2]
    replaced = is_guess | is_lapse
    return sim.assign(choice=np.where(replaced, choice, sim["choice"]), rt=rt)


@dataclass
class FreeParam:
    """Default value and (lo, hi) bounds for a single free parameter."""

    lower_bound: float
    upper_bound: float


@dataclass
class FixedParam:
    value: float


# ---------------------------------------------------------------------------
# Abstract fitting engine
# ---------------------------------------------------------------------------


class DecisionModel:
    """
    Abstract DDM fitting engine. Subclass and implement:
      - param_specs property  -> dict[str, ParamSpec]
      - _build_params(values, condition_idx) -> DDMParams
      - _objective_function(values, data, stimulus, n_reps, seed, l1_weight) -> float
    """

    def __init__(
        self,
        free_params: dict[str, FreeParam] | None = None,
        fixed_params: dict[str, FixedParam] | None = None,
        device: str | None = None,
        likelihood_params: dict | None = None,
        seed: int = 42,
        censor_at: float | None = None,
        min_rt: tuple[float, str] | None = None,
    ):
        """How simulated RTs map onto the recorded outcomes (both off by default, as for the NHP fits):

        censor_at  RT (s) after which a trial counts as "no response": simulated trials that do not cross a bound
                   within the stimulus, or respond later than this, become censored (rt = inf, choice = -1)
                   instead of being dropped. Use with the "qmle_censored" likelihood.
        min_rt     (rt, mode) for responses earlier than `rt`: "floor" registers them at `rt` (a rig that ignores
                   early licks and takes the next one), "truncate" drops them (data selected to exclude them).
        """
        if min_rt is not None and min_rt[1] not in ("floor", "truncate"):
            raise ValueError(f"min_rt mode must be 'floor' or 'truncate', got {min_rt[1]!r}")
        self.seed = seed
        self.censor_at = censor_at
        self.min_rt = min_rt
        self._labels: np.ndarray | None = None
        self._precomputed: dict | None = None
        self.simulator = DriftDiffusionSimulator(device=device)

        self._free_params = free_params or {}
        self.fit_keys = list(self._free_params.keys())
        self.fixed_params = fixed_params or {}
        self._validate_configuration()

        # likelihood_params["method"] picks the objective: "qmle" (Ratcliff quantile likelihood, the
        # default and what the NHP fits used) or "kl" (KL + chronometric + CAF). The remaining keys are
        # passed to that calculator's constructor, so a key it does not accept raises instead of being
        # silently ignored.
        lp = dict(likelihood_params or {})
        method = lp.pop("method", "qmle")
        if method not in LIKELIHOOD_CALCULATORS:
            raise ValueError(f"Unknown likelihood method {method!r}; expected one of {sorted(LIKELIHOOD_CALCULATORS)}")
        self.likelihood_method = method
        self.likelihood_calc = LIKELIHOOD_CALCULATORS[method](**lp)
        logger.info(
            "Initialized %s | device=%s | likelihood=%s %s",
            type(self).__name__,
            getattr(self.simulator, "device", "CPU"),
            method,
            lp,
        )

    def _validate_configuration(self):
        for k, v in self._free_params.items():
            if not isinstance(v, FreeParam):
                raise ValueError(f"free_params['{k}'] must be a FreeParam, got {type(v).__name__}. Did you swap free_params and fixed_params?")
        for k, v in self.fixed_params.items():
            if not isinstance(v, FixedParam):
                raise ValueError(f"fixed_params['{k}'] must be a FixedParam, got {type(v).__name__}. Did you swap free_params and fixed_params?")
        overlap = set(self._free_params) & set(self.fixed_params)
        if overlap:
            raise ValueError(f"Parameters both fixed and fitted: {overlap}")
        missing = REQUIRED - set(self._free_params) - set(self.fixed_params)
        if missing:
            raise ValueError(f"Missing parameters (not fixed or fitted): {missing}")

    @property
    def fit_param_specs(self):
        return self._free_params

    def _build_params(self, values):

        if len(values) != len(self.fit_keys):
            raise ValueError(f"Expected {len(self.fit_keys)} values, got {len(values)}")

        p = {}
        for key, val in self.fixed_params.items():
            p[key] = val.value if isinstance(val, FixedParam) else val
        for key, val in zip(self.fit_keys, values):
            p[key] = val

        missing = REQUIRED - set(p.keys())
        if missing:
            raise ValueError(f"Incomplete parameter set: {missing}")

        validate_params(p)

        return p

    def _objective_function(
        self,
        values: np.ndarray,
        data: dict,
        stimulus: np.ndarray,
        n_reps: int,
        l1_weight: float,
    ) -> float:
        raise NotImplementedError

    @staticmethod
    def _set_seed(seed: int) -> None:
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    @staticmethod
    def _stimulus_shape(stimulus) -> tuple[int, int]:
        return (stimulus[0] if isinstance(stimulus, tuple) else stimulus).shape

    def _simulate_condition(
        self,
        stimulus: np.ndarray | tuple,
        params: dict,
        n_reps: int,
    ) -> pd.DataFrame | None:
        """Run repeated simulations and concatenate the trials, applying `censor_at` and `min_rt`."""
        simulations = []

        for rep in range(n_reps):
            if self._precomputed is not None:
                rep_noise = self._precomputed["unit_noise"][rep]
                rep_sv = self._precomputed["unit_sv"][rep]
                rep_sz = self._precomputed["unit_sz"][rep]
                rep_guess = self._precomputed["unit_guess"][rep]
            else:
                rep_noise = rep_sv = rep_sz = None
                rep_guess = np.random.uniform(size=(self._stimulus_shape(stimulus)[0], 3))
            try:
                sim = self.simulator.simulate_trials(
                    stimulus,
                    params,
                    unit_noise=rep_noise,
                    unit_sv=rep_sv,
                    unit_sz=rep_sz,
                    labels=self._labels,
                )
            except Exception as exc:
                logger.warning("Simulation failed: %s", exc)
                return None

            sim = self._map_outcomes(apply_guesses(sim, params, rep_guess))

            if len(sim) < 1:
                continue

            simulations.append(sim)

        if not simulations:
            return None

        return pd.concat(simulations, ignore_index=True)

    def precompute(self, n_trials: int, n_timepoints: int, n_reps: int) -> None:
        """Draw all random numbers for `n_reps` simulations of `n_trials` once (diffusion noise, sv, sz and the
        fast-guess draws), so every objective evaluation sees the same ones."""
        self._precomputed = self.simulator.precompute_noise(n_trials, n_timepoints, n_reps=n_reps)
        self._precomputed["unit_guess"] = np.random.uniform(size=(n_reps, n_trials, 3))

    def _map_outcomes(self, sim: pd.DataFrame) -> pd.DataFrame:
        responded = np.isfinite(sim["rt"]) & np.isfinite(sim["choice"])
        if self.censor_at is not None:
            late = ~responded | (sim["rt"] > self.censor_at)
            sim = sim.assign(rt=np.where(late, np.inf, sim["rt"]), choice=np.where(late, -1.0, sim["choice"]))
            keep = np.ones(len(sim), dtype=bool)
        else:
            keep = responded.to_numpy()
        if self.min_rt is not None:
            early = (sim["rt"] < self.min_rt[0]).to_numpy()
            if self.min_rt[1] == "floor":
                sim = sim.assign(rt=np.where(early, self.min_rt[0], sim["rt"]))
            else:
                keep &= ~early
        return sim.loc[keep]

    def fit(
        self,
        data: dict[str, np.ndarray],
        stimulus: np.ndarray | tuple,
        max_iterations: int = 100,
        n_reps: int = 5,
        l1_weight: float = 0.01,
        verbose: bool = True,
        labels: np.ndarray | None = None,
        tol: float = 0.01,
        atol: float = 0.0,
        seeds: list[np.ndarray] | None = None,
        checkpoint: str | Path | None = None,
    ) -> dict:
        """
        Fit parameters via differential evolution, then a gradient-free local
        refinement.

        `seeds` are parameter vectors (in `fit_keys` order) placed in the initial population, e.g. the solutions of
        nested models, so the fit starts at least as well as each of them; they are clipped to the bounds. The rest of
        the population is Latin-hypercube sampled, as in the default initialization.

        `tol`/`atol` are differential evolution's stopping tolerances (population NLL spread <= atol +
        tol * |mean NLL|). The default relative tol stops once the spread is within 1% of the NLL, which for
        thousands of trials is coarser than the NLL differences between models; use tol=0 and an absolute atol.

        `checkpoint`: file for resuming an interrupted fit (preemption, requeue, time limit). The DE state (population,
        its NLLs, the DE random generator, evaluation count, running best) is written atomically after every
        generation, and the DE result once DE ends (a restart then repeats only the refinement). On start, a checkpoint
        whose fingerprint (fit keys, bounds, settings, seed, data, stimulus, seeds) matches is resumed; any other is
        ignored. The objective is deterministic (common random numbers), so a resumed fit gives the same result as an
        uninterrupted one on the same hardware. The caller deletes the file once the result is saved.

        Returns dict with keys: success, parameters, likelihood,
        n_iterations, optimization_result, resumed_from_generation (None if not resumed; -1 = from the refinement).
        """
        if verbose:
            logger.info("Starting optimization (%s)...", type(self).__name__)

        if not self.fit_keys:
            raise ValueError("No fitted parameters specified.")

        specs = self.fit_param_specs
        bounds = [(s.lower_bound, s.upper_bound) for s in specs.values()]

        self._set_seed(self.seed)
        self._labels = labels
        self.simulator.clear_cache()  # arrays from a previous fit (e.g. another CV fold) would stay on the GPU

        # Precompute all unit draws once so every objective evaluation sees the
        # same random numbers (Common Random Numbers): noise, sv, and sz alike.
        # This makes the objective deterministic in the parameters, which is what
        # lets DE navigate it at all.
        n_trials, n_timepoints = self._stimulus_shape(stimulus)
        self.precompute(n_trials, n_timepoints, n_reps)

        best_nll = [np.inf]
        best_vals = [None]

        def objective(values: np.ndarray) -> float:
            nll = self._objective_function(values, data, stimulus, n_reps, l1_weight)
            if nll < best_nll[0]:
                best_nll[0] = nll
                best_vals[0] = np.asarray(values, dtype=float).copy()
            return nll

        iteration = [0]
        ckpt = Path(checkpoint) if checkpoint is not None else None
        fingerprint = None
        if ckpt is not None:
            fingerprint = _fit_fingerprint(
                fit_keys=list(self.fit_keys), bounds=bounds, max_iterations=max_iterations, n_reps=n_reps, l1_weight=l1_weight,
                tol=tol, atol=atol, seed=self.seed, popsize=15, data=data, stimulus=stimulus, labels=labels, seeds=seeds,
            )
        state = _load_checkpoint(ckpt, fingerprint)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            init = "latinhypercube"
            if seeds:
                lo, hi = np.array(bounds).T
                pop = lo + (hi - lo) * qmc.LatinHypercube(d=len(bounds), seed=self.seed).random(15 * len(bounds))
                for i, x in enumerate(seeds[: len(pop)]):
                    pop[i] = np.clip(np.asarray(x, dtype=float), lo, hi)
                init = pop

            if state is not None and state["stage"] == "refine":
                de_result = state["de_result"]
                best_nll[0], best_vals[0] = state["best_nll"], state["best_vals"]
                resumed_from = -1
                logger.info("Resuming from checkpoint %s: DE done (%d generations), refinement restarts", ckpt.name, de_result.nit)
            else:
                # As scipy's differential_evolution(seed=...), run step by step so that the state can be saved. The
                # function wraps exactly this solver; tests/test_fit_checkpoint.py checks the two give the same result.
                solver = DifferentialEvolutionSolver(
                    objective,
                    bounds=bounds,
                    init=init,
                    maxiter=max_iterations,
                    popsize=15,  # modest bump from 10; cheap insurance for the
                    # 9-10 dim space, not the main fix.
                    rng=np.random.RandomState(self.seed),  # = differential_evolution(seed=int), the legacy generator
                    tol=tol,
                    atol=atol,
                    polish=False,  # the built-in polish is L-BFGS-B, which needs
                    # finite-difference gradients. On a CRN
                    # simulation objective those are ~0 for
                    # sub-dt perturbations, so the polish is at
                    # best a no-op and at worst misleading.
                    disp=False,
                )
                resumed_from = None
                if state is not None:
                    _restore_solver(solver, state)
                    best_nll[0], best_vals[0] = state["best_nll"], state["best_vals"]
                    iteration[0] = resumed_from = state["generation"]
                    logger.info("Resuming from checkpoint %s at generation %d (NLL %.4f)", ckpt.name, resumed_from, best_nll[0])
                de_result = self._run_de(solver, max_iterations, iteration, best_nll, best_vals, verbose, ckpt, fingerprint)
                if ckpt is not None:
                    _save_checkpoint(ckpt, {"fingerprint": fingerprint, "stage": "refine", "de_result": de_result,
                                            "best_nll": best_nll[0], "best_vals": best_vals[0]})

            # Local refinement with a gradient-free simplex method that tolerates
            # the piecewise-constant structure of the simulation objective.
            refine_result = minimize(
                objective,
                x0=de_result.x,
                bounds=bounds,
                method="Nelder-Mead",
                options={
                    "maxiter": max_iterations,
                    "xatol": 1e-4,
                    "fatol": 1e-4,
                    "disp": False,
                },
            )

        # Return the best objective ACTUALLY observed, across DE, the refinement,
        # and the running best tracked inside `objective`. Never trust a single
        # optimizer's reported x over a better value we already evaluated.
        candidates = [
            (float(de_result.fun), np.asarray(de_result.x, dtype=float)),
            (float(refine_result.fun), np.asarray(refine_result.x, dtype=float)),
        ]
        if best_vals[0] is not None:
            candidates.append((float(best_nll[0]), best_vals[0]))

        best_fun, best_x = min(candidates, key=lambda t: t[0])
        best = self._build_params(best_x)

        success = bool(np.isfinite(best_fun) and best_fun < 1e6)

        if verbose:
            logger.info("Optimization done. Cost: %.4f", best_fun)
            for name, val in best.items():
                logger.info("  %s = %.4f", name, val)

        if success:
            logger.info("Optimization successful.")
            self.fitted_params_ = best
            self.optimization_result_ = de_result

        return {
            "success": success,
            "parameters": best,
            "likelihood": best_fun,
            "n_iterations": int(getattr(de_result, "nit", 0)),
            "optimization_result": de_result,
            "refine_result": refine_result,
            "resumed_from_generation": resumed_from,
        }

    def _run_de(self, solver, max_iterations, iteration, best_nll, best_vals, verbose, ckpt, fingerprint) -> OptimizeResult:
        """scipy's DifferentialEvolutionSolver.solve() loop (scipy 1.15, polish off, no constraints, no maxfun),
        continuing from generation iteration[0], with a checkpoint after each generation that does not end the run."""
        if np.all(np.isinf(solver.population_energies)):  # fresh start: initial energies, as solve() does
            solver.feasible, solver.constraint_violation = solver._calculate_population_feasibilities(solver.population)
            solver.population_energies[solver.feasible] = solver._calculate_population_energies(solver.population[solver.feasible])
            solver._promote_lowest_energy()
        warning_flag, message = False, "Optimization terminated successfully."
        nit = iteration[0]
        if nit >= max_iterations:
            warning_flag, message = True, "Maximum number of iterations has been exceeded."
        while nit < max_iterations:
            next(solver)
            nit += 1
            iteration[0] = nit
            if verbose:
                params_str = "  ".join(f"{k}={v:.4f}" for k, v in zip(self.fit_keys, best_vals[0]))
                c = solver.tol / (solver.convergence + np.finfo(float).eps)
                logger.info("Iter %3d | NLL=%.4f | convergence=%.4f | %s", nit, best_nll[0], c, params_str)
            if solver.converged():
                break
            if nit >= max_iterations:
                warning_flag, message = True, "Maximum number of iterations has been exceeded."
                break
            if ckpt is not None:
                _save_checkpoint(ckpt, {"fingerprint": fingerprint, "stage": "de", "generation": nit, **_solver_state(solver),
                                        "best_nll": best_nll[0], "best_vals": None if best_vals[0] is None else best_vals[0].copy()})
        return solver._result(nit=nit, message=message, warning_flag=warning_flag)


_SOLVER_STATE = ("population", "population_energies", "feasible", "constraint_violation", "_nfev", "_random_population_index")
# _random_population_index: shuffled in place when drawing mutation partners, so it carries over between generations


def _solver_state(solver: DifferentialEvolutionSolver) -> dict:
    """Everything a DE generation changes (scipy 1.15, 'immediate' updating): the rest of the solver is fixed by its
    arguments."""
    state = {k: np.copy(getattr(solver, k)) if isinstance(getattr(solver, k), np.ndarray) else getattr(solver, k) for k in _SOLVER_STATE}
    state["rng_state"] = solver.random_number_generator.get_state()
    return state


def _restore_solver(solver: DifferentialEvolutionSolver, state: dict) -> None:
    for k in _SOLVER_STATE:
        setattr(solver, k, np.copy(state[k]) if isinstance(state[k], np.ndarray) else state[k])
    solver.random_number_generator.set_state(state["rng_state"])


def _fit_fingerprint(**parts) -> str:
    """Hash of everything that determines a fit, so a checkpoint is only resumed by the same fit."""
    h = hashlib.sha256()

    def add(x):
        if isinstance(x, dict):
            for k in sorted(x):
                h.update(str(k).encode())
                add(x[k])
        elif isinstance(x, (list, tuple)):
            h.update(f"[{len(x)}".encode())
            for v in x:
                add(v)
        elif isinstance(x, (np.ndarray, torch.Tensor)):
            a = np.ascontiguousarray(x.detach().cpu().numpy() if isinstance(x, torch.Tensor) else x)
            h.update(f"{a.dtype}{a.shape}".encode())
            h.update(a.tobytes())
        elif isinstance(x, (pd.Series, pd.DataFrame)):
            add(x.to_numpy())
        else:
            h.update(repr(x).encode())

    add(parts)
    return h.hexdigest()


def _save_checkpoint(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(state, f)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)  # atomic: a kill during the write leaves the previous checkpoint


def _load_checkpoint(path: Path | None, fingerprint: str | None) -> dict | None:
    if path is None or not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            state = pickle.load(f)
    except Exception as e:  # truncated or unreadable: start over
        logger.warning("Ignoring unreadable checkpoint %s (%s); starting from scratch", path, e)
        return None
    if state.get("fingerprint") != fingerprint:
        logger.warning("Ignoring checkpoint %s: made by a different fit (settings, data or seeds differ); starting from scratch", path)
        return None
    return state

    def simulate(
        self,
        stimulus: np.ndarray | tuple,
        params: dict | None = None,
        n_reps: int = 1,
        seed: int | None = None,
        labels: np.ndarray | None = None,
    ) -> pd.DataFrame:
        """Forward pass with fresh noise: one row per simulated trial with rt, choice, signed_coherence (the
        trial's label) and trial (index of the input trial). Fast guesses (p_guess) are included; `censor_at` and
        `min_rt` are not applied here."""
        if params is None:
            raise ValueError("Must provide params for simulation.")
        validate_params(params)
        if n_reps < 1:
            raise ValueError("n_reps must be >= 1")

        self._set_seed(seed if seed is not None else self.seed)
        n_trials = self._stimulus_shape(stimulus)[0]
        simulations = []
        for rep in range(n_reps):
            sim = self.simulator.simulate_trials(stimulus, params, labels=labels)
            sim = apply_guesses(sim, params, np.random.uniform(size=(n_trials, 3)))
            simulations.append(sim.assign(trial=np.arange(n_trials), rep=rep))
        return pd.concat(simulations, ignore_index=True)
