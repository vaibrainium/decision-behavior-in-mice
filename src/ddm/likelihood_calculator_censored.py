"""Ratcliff quantile likelihood (QMLE) with a censored outcome, for tasks where some trials get no response
within the analysed window.

Per condition cell:
  outcome term  multinomial over {choice 0, choice 1, censored}: -sum_k n_k log p_k, with p_k from the
                simulated trials of the cell
  RT term       for each choice, data RT quantile bins (nbins + 1 edges) and the simulated share of that
                choice's RTs in each bin: -sum_b n_b log p_b
Probabilities are smoothed with `alpha` pseudo-counts per category, so a choice or bin the model never produces
costs a large but finite penalty. A cell with no simulated trials at all (e.g. every simulated RT dropped by a
truncation rule) would smooth to uniform probabilities, which is the best possible RT score because the bins are
data quantiles; such cells instead cost EMPTY_CELL_PENALTY per data trial. (The plain QMLE skips cells without
predictions, which a model can exploit the same way.)

Data and predictions use rt = inf and choice = -1 for censored trials. Condition labels can be any numbers.

include_censored=False scores responded data only (no censored data trials): the outcome term is then a binomial over
{choice 0, choice 1} among the simulated responses, i.e. the likelihood conditional on a response within the window.
"""

import numpy as np

CENSORED = -1
EMPTY_CELL_PENALTY = 20.0  # per data trial, ~ -log(2e-9)


class CensoredQMLE:
    def __init__(self, nbins: int = 9, rt_nllh_weight: float = 1.0, alpha: float = 0.5, include_censored: bool = True):
        self.include_censored = include_censored
        self.nbins = nbins
        self.rt_nllh_weight = rt_nllh_weight
        self.alpha = alpha

    def _multinomial_nll(self, data_counts: np.ndarray, model_counts: np.ndarray) -> float:
        p = (model_counts + self.alpha) / (model_counts.sum() + self.alpha * len(model_counts))
        return float(-(data_counts * np.log(p)).sum())

    def _rt_nll(self, rt_data: np.ndarray, rt_model: np.ndarray) -> float:
        if len(rt_data) < self.nbins:
            return 0.0  # too few data trials for stable quantiles; depends on the data only, so same for every model
        edges = np.quantile(rt_data, np.linspace(0, 1, self.nbins + 1))
        edges[0], edges[-1] = -np.inf, np.inf  # outer bins take model RTs beyond the data range
        data_counts = np.histogram(rt_data, bins=edges)[0]
        model_counts = np.histogram(rt_model, bins=edges)[0]
        return self._multinomial_nll(data_counts, model_counts)

    def compute_nll(self, rt_pred, choice_pred, rt_data, choice_data, cond_pred, cond_data) -> float:
        rt_pred, choice_pred, cond_pred = (np.asarray(x) for x in (rt_pred, choice_pred, cond_pred))
        rt_data, choice_data, cond_data = (np.asarray(x) for x in (rt_data, choice_data, cond_data))
        if not self.include_censored and (choice_data == CENSORED).any():
            raise ValueError("include_censored=False expects responded data only")
        outcomes = np.array([0, 1, CENSORED] if self.include_censored else [0, 1])
        total = 0.0
        for cond in np.unique(cond_data):
            d, m = cond_data == cond, cond_pred == cond
            data_counts = np.array([(choice_data[d] == k).sum() for k in outcomes])
            model_counts = np.array([(choice_pred[m] == k).sum() for k in outcomes])
            if model_counts.sum() == 0:
                total += EMPTY_CELL_PENALTY * data_counts.sum()
                continue
            total += self._multinomial_nll(data_counts, model_counts)
            for k in (0, 1):
                rt_d = rt_data[d & (choice_data == k)]
                if len(rt_d):
                    total += self.rt_nllh_weight * self._rt_nll(rt_d, rt_pred[m & (choice_pred == k)])
        return float(total)
