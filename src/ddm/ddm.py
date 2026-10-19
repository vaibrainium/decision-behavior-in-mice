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
import logging
import warnings
from dataclasses import dataclass
import numpy as np
import pandas as pd
import torch
from scipy.optimize import differential_evolution, minimize

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


def apply_guesses(sim: pd.DataFrame, params: dict, draws: np.ndarray) -> pd.DataFrame:
    """Fast-guess (contaminant) component: with probability p_guess a trial's DDM outcome is replaced by a guess,
    choice 1 with probability guess_bias, at RT = guess_t0 + an exponential delay with mean guess_tau (s).

    `draws` is (n_trials, 3) uniform [0, 1): whether the trial is a guess, its choice and its delay. Passing the same
    draws on every evaluation keeps the objective deterministic in the parameters (common random numbers).
    """
    p_guess = float(params.get("p_guess", 0.0))
    if p_guess <= 0:
        return sim
    is_guess = draws[:, 0] < p_guess
    choice = (draws[:, 1] < float(params.get("guess_bias", 0.5))).astype(float)
    rt = float(params.get("guess_t0", 0.0)) - float(params["guess_tau"]) * np.log1p(-draws[:, 2])
    return sim.assign(choice=np.where(is_guess, choice, sim["choice"]), rt=np.where(is_guess, rt, sim["rt"]))


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
    ) -> dict:
        """
        Fit parameters via differential evolution, then a gradient-free local
        refinement.

        `tol`/`atol` are differential evolution's stopping tolerances (population NLL spread <= atol +
        tol * |mean NLL|). The default relative tol stops once the spread is within 1% of the NLL, which for
        thousands of trials is coarser than the NLL differences between models; use tol=0 and an absolute atol.

        Returns dict with keys: success, parameters, likelihood,
        n_iterations, optimization_result.
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

        def callback(xk: np.ndarray, convergence: float) -> None:
            iteration[0] += 1
            params_str = "  ".join(f"{k}={v:.4f}" for k, v in zip(self.fit_keys, best_vals[0]))
            logger.info(
                "Iter %3d | NLL=%.4f | convergence=%.4f | %s",
                iteration[0],
                best_nll[0],
                convergence,
                params_str,
            )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            de_result = differential_evolution(
                objective,
                bounds=bounds,
                maxiter=max_iterations,
                popsize=15,  # modest bump from 10; cheap insurance for the
                # 9-10 dim space, not the main fix.
                seed=self.seed,
                tol=tol,
                atol=atol,
                polish=False,  # the built-in polish is L-BFGS-B, which needs
                # finite-difference gradients. On a CRN
                # simulation objective those are ~0 for
                # sub-dt perturbations, so the polish is at
                # best a no-op and at worst misleading.
                disp=False,
                callback=callback if verbose else None,
            )

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
        }

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
