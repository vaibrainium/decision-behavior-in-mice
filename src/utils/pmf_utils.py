import warnings

import numpy as np
from scipy.optimize import OptimizeWarning, curve_fit
from sklearn.base import BaseEstimator, RegressorMixin


class PsychometricFunction(BaseEstimator, RegressorMixin):
    """
    Fits a logistic regression model for psychometric analysis.

    Models:
        - "logit_2": Logistic function with mean and variance (without lapse rate).
        - "logit_3": Logistic function with lapse rate.
        - "logit_4": Logistic function with lapse and guess rates.
    """

    def __init__(
        self,
        model="logit_4",
        mean_lims=(-100, 100),
        var_lims=(1e-5, 30),
        lapse_rate_lims=(0, 0.1),
        guess_rate_lims=(0, 0.1),
        multistart=True,
    ) -> None:
        self.model = model
        self.mean_lims = mean_lims
        self.var_lims = var_lims
        self.lapse_rate_lims = lapse_rate_lims
        self.guess_rate_lims = guess_rate_lims
        self.multistart = multistart

        if model not in ["logit_2", "logit_3", "logit_4"]:
            msg = f"Unknown model: {model}. Choose 'logit_2', 'logit_3' or 'logit_4'."
            raise ValueError(msg)

    def logit_2(self, x, mean, var):
        """Logistic function with only mean and variance."""
        return 1 / (1 + np.exp(-var * (x - mean)))

    def logit_3(self, x, mean, var, lapse_rate):
        """Logistic function with lapse rate."""
        return lapse_rate + ((1 - 2 * lapse_rate) / (1 + np.exp(-var * (x - mean))))

    def logit_4(self, x, mean, var, lapse_rate, guess_rate):
        """Logistic function with lapse and guess rates."""
        return lapse_rate + ((1 - guess_rate - lapse_rate) / (1 + np.exp(-var * (x - mean))))

    def fit(self, x, y, trial_counts=None):
        """Fit weighted least squares, selecting the best converged starting point.

        By default, retain the original single-start fit and try a deterministic
        grid of additional starts. ``multistart=False`` uses the original starting
        point and solver defaults. Bounds and weights are identical in both modes.
        ``fit_diagnostics_`` records each attempt and parameter-bound contacts;
        numerical convergence does not establish parameter identifiability.
        """
        x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
        if x.ndim != 1 or y.shape != x.shape:
            raise ValueError("x and y must be one-dimensional arrays of equal length")
        if trial_counts is not None:
            trial_counts = np.asarray(trial_counts, dtype=float)
            if trial_counts.shape != y.shape:
                raise ValueError("trial_counts must match x and y")
        # Preserve the original missing-response mask.
        # Remove NaNs
        mask = ~np.isnan(y)
        x, y = x[mask], y[mask]
        if trial_counts is not None:
            trial_counts = trial_counts[mask]

        if len(x) == 0 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
            raise ValueError("Fit requires nonempty, finite x and y after removing NaN responses")
        if trial_counts is not None and (not np.all(np.isfinite(trial_counts)) or np.any(trial_counts <= 0)):
            raise ValueError("trial_counts must be finite and strictly positive")

        # Choose fitting function based on model
        if self.model == "logit_2":
            self._fit_func = self.logit_2
            param_lims = [self.mean_lims, self.var_lims]  # Only mean and variance
        elif self.model == "logit_3":
            self._fit_func = self.logit_3
            param_lims = [self.mean_lims, self.var_lims, self.lapse_rate_lims]
        elif self.model == "logit_4":
            self._fit_func = self.logit_4
            param_lims = [self.mean_lims, self.var_lims, self.lapse_rate_lims, self.guess_rate_lims]

        bounds = list(zip(*param_lims, strict=False))
        initial_guess = [np.mean(param_lims[0])] + [np.min(lim) for lim in param_lims[1:]]

        # Compute weights: More trials → Higher weight
        if trial_counts is not None:
            weights = np.sqrt(trial_counts)  # Square root scaling to balance influence
            sigma = 1 / weights  # Use inverse for curve fitting
        else:
            sigma = None  # No weighting if trial_counts is not provided

        # The legacy candidate is included unchanged; extra starts cannot make
        # the selected weighted residual error worse than a successful legacy fit.
        starts = [np.asarray(initial_guess, dtype=float)]
        lower, upper = np.asarray(bounds, dtype=float)
        if self.multistart:
            span = max(float(np.ptp(x)), np.finfo(float).eps)
            centers = np.linspace(float(x.min()), float(x.max()), 5)[1:4]
            slopes = np.array([3., 10., 30.]) / span
            nuisance = [(), ()] if len(param_lims) == 2 else [
                tuple(lo + fraction * (hi - lo) for (lo, hi), fraction in
                      zip(param_lims[2:], fractions, strict=False))
                for fractions in [(0.125, 0.125), (0.625, 0.375)]
            ]
            for center in centers:
                for slope in slopes:
                    for tail in nuisance:
                        candidate = np.clip([center, slope, *tail], lower, upper)
                        if not any(np.array_equal(candidate, old) for old in starts):
                            starts.append(candidate)

        attempts, solutions = [], []
        for index, start in enumerate(starts):
            # Retain scipy defaults for the original candidate; refine extra starts.
            options = {} if index == 0 else dict(max_nfev=3000, ftol=1e-10, xtol=1e-10, gtol=1e-10)
            try:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always", OptimizeWarning)
                    params, covariance = curve_fit(
                        self._fit_func, x, y, p0=start, bounds=bounds,
                        sigma=sigma, absolute_sigma=False, **options,
                    )
                residual = self._fit_func(x, *params) - y
                if sigma is not None:
                    residual = residual / sigma
                error = float(np.sum(residual ** 2))
                if not np.all(np.isfinite(params)) or not np.isfinite(error):
                    raise RuntimeError("Nonfinite fit parameters or residual error")
                attempts.append(dict(start=start.tolist(), success=True, weighted_sse=error,
                                     warnings=list(dict.fromkeys(str(w.message) for w in caught))))
                solutions.append((error, index, params, covariance, caught))
            except (RuntimeError, ValueError, FloatingPointError) as exc:
                attempts.append(dict(start=start.tolist(), success=False, error=str(exc)))
        self.fit_diagnostics_ = dict(n_starts=len(starts), n_success=len(solutions), attempts=attempts)
        if not solutions:
            raise RuntimeError(f"All {len(starts)} psychometric fit attempts failed: {attempts[-1]['error']}")
        self.weighted_sse_, selected, popt, pcov, selected_warnings = min(solutions, key=lambda result: result[0])
        self.fit_diagnostics_.update(
            selected_start=selected, weighted_sse=self.weighted_sse_,
            covariance_finite=bool(np.all(np.isfinite(pcov))),
            at_bound=(np.isclose(popt, lower, rtol=1e-5, atol=1e-8) |
                      np.isclose(popt, upper, rtol=1e-5, atol=1e-8)).tolist(),
        )
        # Surface selected covariance warnings once; numerical warnings from
        # intermediate solver evaluations remain recorded in the diagnostics.
        for message in dict.fromkeys(str(w.message) for w in selected_warnings if issubclass(w.category, OptimizeWarning)):
            warnings.warn(message, OptimizeWarning, stacklevel=2)
        # Store results
        self.coefs_ = {"mean": popt[0], "var": popt[1]}
        if self.model in ("logit_3", "logit_4"):
            self.coefs_["lapse_rate"] = popt[2]
        if self.model == "logit_4":
            self.coefs_["guess_rate"] = popt[3]

        self.covar_ = pcov
        return self

    def predict(self, x):
        """Predict using the fitted model."""
        return self._fit_func(x, **self.coefs_)


def fit_psychometric_function(x_data, y_data, trial_counts, model_type, **kwargs) -> PsychometricFunction:
    """Fit psychometric function with user-defined or default parameters."""
    params = {
        "model": model_type,
        "mean_lims": (-100, 100),
        "var_lims": (1e-5, 30),
        "lapse_rate_lims": (1e-5, 0.4),
        "guess_rate_lims": (1e-5, 0.4),
        **kwargs,  # Override defaults with user input
    }
    return PsychometricFunction(**params).fit(x_data, y_data, trial_counts)


def get_psychometric_data(
    data,
    positive_direction="right",
    fit=True,
    model_type="logit_4",
    x_model_range=None,
    **kwargs,
):
    """Extracts psychometric data and optionally fits a model."""
    unique_coh = np.unique(data["signed_coherence"])
    x_data = np.where(positive_direction == "left", -unique_coh, unique_coh)
    y_data = []
    trial_counts = []
    for coh in unique_coh:
        mask = data["signed_coherence"] == coh
        total_trials = np.sum(mask)

        if total_trials == 0:
            continue  # Skip coherence levels with no trials

        prop_positive = np.mean(data["choice"][mask] == (positive_direction == "right"))
        y_data.append(prop_positive)
        trial_counts.append(total_trials)

    # Convert to numpy arrays and sort
    x_data, y_data, trial_counts = map(np.array, zip(*sorted(zip(x_data, y_data, trial_counts, strict=False)), strict=False))

    if not fit:
        return x_data, y_data
    # Fit the model using the specified model_type (logit_2, logit_3, logit_4)
    model = fit_psychometric_function(x_data, y_data, trial_counts=trial_counts, model_type=model_type, **kwargs)
    # Generate model predictions over a range of x values
    x_model = np.linspace(x_model_range[0], x_model_range[1], 100) if x_model_range is not None else np.linspace(min(x_data), max(x_data), 100)
    y_model = model.predict(x_model)

    return x_data, y_data, model, x_model, y_model


def get_chronometric_data(data, positive_direction="right"):
    """Computes reaction time statistics for different coherence levels."""
    unique_coh = np.unique(data["signed_coherence"])
    coherences, rt_median, rt_mean, rt_sd = [], [], [], []

    for coh in unique_coh:
        trials = data[(data["signed_coherence"] == coh) & (data["outcome"] == 1)]
        if trials.empty:
            continue

        coherences.append(coh if positive_direction == "right" else -coh)
        rt_median.append(np.median(trials["response_time"]))
        rt_mean.append(np.mean(trials["response_time"]))
        rt_sd.append(np.std(trials["response_time"]))

    return map(np.array, zip(*sorted(zip(coherences, rt_median, rt_mean, rt_sd, strict=False)), strict=False))


def get_accuracy_data(data, positive_direction="right"):
    """Computes accuracy across coherence levels."""
    unique_coh = np.unique(data["signed_coherence"])
    coherences = np.where(positive_direction == "left", -unique_coh, unique_coh)
    accuracy = np.array([np.mean(data["outcome"][data["signed_coherence"] == coh] == 1) for coh in unique_coh])

    return map(np.array, zip(*sorted(zip(coherences, accuracy, strict=False)), strict=False))
