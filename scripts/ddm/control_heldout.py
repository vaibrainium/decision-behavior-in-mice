"""Held-out model comparison on responded control trials for the control-only paper (plan
.agents/plans/2026-10-29-control-paper.md, D003): per-mouse held-out NLL from the five control CV folds (ccv0-ccv4),
common model C against each alternative, with mice as the unit.

  - per 1,000 control trials: (NLL_alt - NLL_C) / n_control * 1000 (> 0: C predicts better), from the stored test_nll;
    checked against paper_accumulation/tables/heldout_per_trial_2026-10-28.csv (its producing script is not in the repo);
  - --split: the same difference split into a choice part (the likelihood with rt_nllh_weight 0: per-condition choice
    counts) and an RT part (total - choice), by re-scoring each test fold at the fitted parameters (EVAL_SEED);
  - leave-one-mouse-out: the group t-test and Wilcoxon with each mouse dropped;
  - --nominal: the nominal-coherence refits (fit_mouse_ddm --nominal_matched) against the motion-energy fits of the
    same model, (NLL_nominal - NLL_ME) per 1,000 control trials (> 0: motion energy predicts better), Holm over 3
    (plan step 3c); plus C_nom against E_nom and ES_nom.
The likelihood pools trials per signed coherence, so none of these terms uses trial-level motion energy
(reports/2026-10-29-likelihood-ignores-trial-me.md).

Usage: python -m scripts.ddm.control_heldout [--split] [--models C E ES DDMx ESx ...] [--nominal]
"""

import argparse
import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from config import dir_config
from scripts.ddm import model_recovery as mr
from scripts.ddm.fit_mouse_ddm import N_FOLDS, cv_folds, heldout_nll, load_inputs, responded_only, select

logger = logging.getLogger(__name__)

TABLES = Path(__file__).resolve().parents[2] / "dissemination/paper_control/tables"
REFERENCE = Path(__file__).resolve().parents[2] / "dissemination/paper_accumulation/tables/heldout_per_trial_2026-10-28.csv"
DATE = "2026-10-29"
# name: (fit folder, file variant, model_recovery variant, nominal input)
MODELS = {
    "C": ("ddm/fits_resp_fast_only", "L0U0V1Z0G1", mr.COMMON, False),
    "E": ("ddm/fits_resp_fast_only_leak20-200_cap", "L1U0V1Z0G1", mr.EXTREMA, False),
    "ES": ("ddm/fits_resp_fast_only_es_cap", "L0U0V1Z0G1", mr.EXTREMA_SAMPLES, False),
    "DDMx": ("ddm/fits_resp_nominal_ddm_g001", "L0U0V0Z0G0", "DDMx", True),
    "ESx": ("ddm/fits_resp_nominal_es", "L0U0V0Z0G0", "ESx", True),
    "C_nom": ("ddm/fits_resp_nominal_matched_C", "L0U0V1Z0G1", mr.COMMON, True),
    "E_nom": ("ddm/fits_resp_nominal_matched_E", "L1U0V1Z0G1", mr.EXTREMA, True),
    "ES_nom": ("ddm/fits_resp_nominal_matched_ES", "L0U0V1Z0G1", mr.EXTREMA_SAMPLES, True),
}
NOMINAL_DATE = "2026-10-30"
REFERENCE_NAMES = {"E": "Rapid forgetting (E)", "ES": "Extrema samples (ES)", "DDMx": "Paper-exact integration (DDMx)", "ESx": "Paper-exact extrema (ESx)"}


def load(processed: Path, name: str, mouse: str, fold: int) -> dict:
    folder, variant, _, _ = MODELS[name]
    with open(processed / folder / f"{mouse}_{variant}_ccv{fold}.pkl", "rb") as f:
        return pickle.load(f)


def rescore(inputs: dict, processed: Path, name: str, mouse: str) -> dict:
    """Total and choice-only held-out NLL summed over the five folds, re-scored at the fitted parameters."""
    _, _, variant, nominal = MODELS[name]
    rows = np.flatnonzero((inputs["subject_id"] == mouse) & (inputs["sched_pulse_type"] == 0))
    rig = str(np.unique(inputs["data_source"][rows]).item())
    folds = cv_folds(inputs["condition"][rows], N_FOLDS)
    model = mr.make_model(variant, rig, strategy=True, responded=True)
    out = {"total": 0.0, "choice": 0.0, "stored": 0.0}
    for k in range(N_FOLDS):
        fit = load(processed, name, mouse, k)
        test = rows[folds == k]
        if len(test) != fit["n_test"]:
            raise ValueError(f"{name} {mouse} ccv{k}: {len(test)} test trials, fit has {fit['n_test']}")
        data, stim = select(inputs, test, nominal=nominal)
        out["total"] += heldout_nll(model, fit["parameters"], data, stim, fit["n_reps"])
        model.likelihood_calc.rt_nllh_weight = 0.0
        out["choice"] += heldout_nll(model, fit["parameters"], data, stim, fit["n_reps"])
        model.likelihood_calc.rt_nllh_weight = 1.0
        out["stored"] += fit["test_nll"]
    model.simulator.clear_cache()
    return out


def group(x: np.ndarray) -> dict:
    t = stats.ttest_1samp(x, 0.0)
    return {"n_mice": len(x), "mean": x.mean(), "median": np.median(x), "min": x.min(), "max": x.max(), "t": t.statistic, "p_t": t.pvalue,
            "p_wilcoxon": stats.wilcoxon(x).pvalue, "dz": x.mean() / x.std(ddof=1)}


def holm(p: np.ndarray) -> np.ndarray:
    order, adj, run = np.argsort(p), np.empty(len(p)), 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(run, 1.0)
    return adj


def main(models: list[str], split: bool) -> None:
    processed = Path(dir_config.data.processed)
    inputs = responded_only(load_inputs(processed / "ddm/ddm_inputs_global.npz"))
    mice = sorted(np.unique(inputs["subject_id"]))
    n_control = {m: int(((inputs["subject_id"] == m) & (inputs["sched_pulse_type"] == 0)).sum()) for m in mice}
    rows = []
    for name in ["C", *models]:
        for mouse in mice:
            r = {"model": name, "mouse": mouse, "control_trials": n_control[mouse], "test_nll": sum(load(processed, name, mouse, k)["test_nll"] for k in range(N_FOLDS))}
            if split:
                r.update(rescore(inputs, processed, name, mouse))
                logger.info("%s %s %s", name, mouse, {k: round(v, 1) for k, v in r.items() if isinstance(v, float)})
            rows.append(r)
    df = pd.DataFrame(rows)
    c = df[df.model == "C"].set_index("mouse")
    per = []
    for name in models:
        a = df[df.model == name].set_index("mouse")
        for part, col in [("total", "test_nll")] + ([("rescored_total", "total"), ("choice", "choice")] if split else []):
            d = (a[col] - c[col]) / c.control_trials * 1000
            per += [{"model": name, "part": part, "mouse": m, "per_1000": v, "summed": a.loc[m, col] - c.loc[m, col]} for m, v in d.items()]
        if split:
            d = ((a.total - a.choice) - (c.total - c.choice)) / c.control_trials * 1000
            per += [{"model": name, "part": "rt", "mouse": m, "per_1000": v, "summed": v * c.loc[m, "control_trials"] / 1000} for m, v in d.items()]
    per = pd.DataFrame(per)
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / f"heldout_nll_per_mouse_{DATE}.csv", index=False)
    per.to_csv(TABLES / f"heldout_diff_per_mouse_{DATE}.csv", index=False)

    ref = pd.read_csv(REFERENCE)
    tot = per[per.part == "total"]
    for name in models:
        if name in REFERENCE_NAMES:
            r = ref[ref.model == REFERENCE_NAMES[name]].set_index("mouse").per_1000
            mine = tot[tot.model == name].set_index("mouse").per_1000.round(1)
            logger.info("check vs heldout_per_trial_2026-10-28 (%s): max |diff| %.2f per 1,000", name, (mine - r.loc[mine.index]).abs().max())

    g = []
    for (name, part), s in per.groupby(["model", "part"], sort=False):
        x = s.per_1000.to_numpy()
        g.append({"model": name, "part": part, **group(x), "c_better_10": int((s.summed > 10).sum()), "alt_better_10": int((s.summed < -10).sum())})
    g = pd.DataFrame(g)
    for part in g.part.unique():
        m = g.part == part
        g.loc[m, "p_t_holm"], g.loc[m, "p_wilcoxon_holm"] = holm(g.loc[m, "p_t"].to_numpy()), holm(g.loc[m, "p_wilcoxon"].to_numpy())
    g.to_csv(TABLES / f"heldout_group_{DATE}.csv", index=False)
    print(g.round(4).to_string())

    lomo = []
    for name in models:
        s = tot[tot.model == name].set_index("mouse").per_1000
        for drop in mice:
            x = s.drop(drop).to_numpy()
            lomo.append({"model": name, "dropped": drop, "mean": x.mean(), "p_t": stats.ttest_1samp(x, 0).pvalue, "p_wilcoxon": stats.wilcoxon(x).pvalue})
    lomo = pd.DataFrame(lomo)
    lomo.to_csv(TABLES / f"heldout_lomo_{DATE}.csv", index=False)
    print(lomo.groupby("model").agg(mean_min=("mean", "min"), mean_max=("mean", "max"), p_t_max=("p_t", "max"), p_w_max=("p_wilcoxon", "max")).round(4).to_string())


def nominal(processed: Path, mice: list[str], n_control: dict) -> None:
    """Nominal-coherence refits against the motion-energy fits of the same model (plan step 3c rule)."""
    nll = {name: pd.Series({m: sum(load(processed, name, m, k)["test_nll"] for k in range(N_FOLDS)) for m in mice})
           for name in ["C", "E", "ES", "C_nom", "E_nom", "ES_nom"]}
    n = pd.Series(n_control)
    per = [{"comparison": f"{b}_nom - {b}", "mouse": m, "per_1000": v} for b in ["C", "E", "ES"] for m, v in ((nll[f"{b}_nom"] - nll[b]) / n * 1000).items()]
    per += [{"comparison": f"{b}_nom - C_nom", "mouse": m, "per_1000": v} for b in ["E", "ES"] for m, v in ((nll[f"{b}_nom"] - nll["C_nom"]) / n * 1000).items()]
    per = pd.DataFrame(per)
    per.to_csv(TABLES / f"heldout_nominal_per_mouse_{NOMINAL_DATE}.csv", index=False)
    g = pd.DataFrame([{"comparison": c, **group(s.per_1000.to_numpy())} for c, s in per.groupby("comparison", sort=False)])
    for fam in [g.comparison.str.endswith("_nom - C_nom") == False, g.comparison.str.endswith("_nom - C_nom")]:
        g.loc[fam, "p_t_holm"], g.loc[fam, "p_wilcoxon_holm"] = holm(g.loc[fam, "p_t"].to_numpy()), holm(g.loc[fam, "p_wilcoxon"].to_numpy())
    g.to_csv(TABLES / f"heldout_nominal_group_{NOMINAL_DATE}.csv", index=False)
    print(g.round(4).to_string())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", default=["E", "ES", "DDMx", "ESx"], choices=[m for m in MODELS if m != "C"])
    parser.add_argument("--split", action="store_true", help="re-score test folds for the choice / RT split (CPU simulation)")
    parser.add_argument("--nominal", action="store_true", help="only score the nominal-coherence refits (plan step 3c)")
    args = parser.parse_args()
    if args.nominal:
        processed = Path(dir_config.data.processed)
        inputs = responded_only(load_inputs(processed / "ddm/ddm_inputs_global.npz"))
        mice = sorted(np.unique(inputs["subject_id"]))
        nominal(processed, mice, {m: int(((inputs["subject_id"] == m) & (inputs["sched_pulse_type"] == 0)).sum()) for m in mice})
    else:
        main([m for m in args.models if not m.endswith("_nom")], args.split)
