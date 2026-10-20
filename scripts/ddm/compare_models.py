"""Compare the DDM variants of a fit grid (scripts/ddm/fit_mouse_ddm.py) across mice.

Reads <processed>/<fits_dir>/*.pkl and reports:
  1. completeness and nested-model consistency: switching a mechanism on can only lower the training NLL of the model
     it extends, so a larger model with a clearly worse NLL marks an optimizer failure;
  2. the best model per mouse by summed held-out NLL over the CV folds and by BIC on all trials;
  3. random-effects Bayesian model selection over all variants (Stephan et al. 2009) with protected exceedance
     probabilities (Rigoux et al. 2014), using the cross-validated log likelihood (-held-out NLL) as log evidence;
  4. per mechanism: mean held-out NLL change when it is switched on, over the matched model pairs, per mouse;
  5. family-level random-effects selection per mechanism (models with vs without it);
  6. summed held-out NLL per model.
Mechanism letters are read from the variant names (e.g. L1U1V1Z0G1 -> L, U, V, Z, G).

Usage:
    python -m scripts.ddm.compare_models                         # ddm/fits_guess, all complete CV folds
    python -m scripts.ddm.compare_models --fits_dir ddm/archive/fits_no_guess
"""

import argparse
import glob
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import digamma, gammaln, logsumexp

from config import dir_config

MECHANISM_NAMES = {"L": "leak", "U": "urgency", "V": "sv", "Z": "sz", "G": "guess", "K": "free k"}


def rfx_bms(log_evidence: np.ndarray, n_samples: int = 200_000, seed: int = 0):
    """Random-effects BMS (Stephan et al. 2009). Returns expected model frequencies, exceedance probabilities,
    protected exceedance probabilities and the Bayesian omnibus risk (Rigoux et al. 2014).
    log_evidence: (n_subjects, n_models)."""
    _, n_mod = log_evidence.shape
    alpha0 = np.ones(n_mod)
    alpha = alpha0.copy()
    for _ in range(1000):
        log_u = log_evidence + digamma(alpha) - digamma(alpha.sum())
        g = np.exp(log_u - log_u.max(axis=1, keepdims=True))
        g /= g.sum(axis=1, keepdims=True)
        new = alpha0 + g.sum(axis=0)
        converged = np.max(np.abs(new - alpha)) < 1e-8
        alpha = new
        if converged:
            break
    r = np.random.default_rng(seed).dirichlet(alpha, size=n_samples)
    xp = np.bincount(r.argmax(axis=1), minlength=n_mod) / n_samples
    log_u = log_evidence + digamma(alpha) - digamma(alpha.sum())
    kl_dir = (gammaln(alpha.sum()) - gammaln(alpha).sum() - gammaln(alpha0.sum()) + gammaln(alpha0).sum()
              + ((alpha - alpha0) * (digamma(alpha) - digamma(alpha.sum()))).sum())
    f1 = (g * log_u).sum() - (g * np.log(g + 1e-300)).sum() - kl_dir  # free energy of the RFX model
    f0 = logsumexp(log_evidence - np.log(n_mod), axis=1).sum()  # null: all models equally frequent
    bor = 1 / (1 + np.exp(f1 - f0))
    return alpha / alpha.sum(), xp, (1 - bor) * xp + bor / n_mod, bor


def mechanism_on(variant: str, letter: str) -> bool:
    return variant[variant.index(letter) + 1] == "1"


def load(fits_dir: Path) -> pd.DataFrame:
    rows = []
    for path in glob.glob(str(fits_dir / "*.pkl")):
        with open(path, "rb") as f:
            r = pickle.load(f)
        rows.append({"mouse": r["mouse"], "variant": r["variant"], "split": r["split"], "train_nll": r["train_nll"], "test_nll": r.get("test_nll"), "k": len(r["free_parameters"]), "n": r["n_train"]})
    return pd.DataFrame(rows)


def main(fits_dir: Path, folds: list[str] | None):
    df = load(fits_dir)
    letters = list(df.variant.iloc[0][0::2])
    mice, variants = sorted(df.mouse.unique()), sorted(df.variant.unique())
    complete = {s: df[df.split == s].groupby(["mouse", "variant"]).size().reindex(pd.MultiIndex.from_product([mice, variants])).notna().all() for s in sorted(df.split.unique())}
    folds = folds or [s for s in sorted(complete) if s.startswith("cv") and complete[s]]
    print(f"{fits_dir}: {len(df)} fits, {len(mice)} mice x {len(variants)} variants; complete splits: {[s for s, ok in complete.items() if ok]}")
    print(f"CV folds used: {folds}\n")

    allf = df[df.split == "all"].set_index(["mouse", "variant"])
    deltas = []
    for (m, v), r in allf.iterrows():
        for letter in letters:
            if mechanism_on(v, letter):
                i = v.index(letter) + 1
                sub = (m, v[:i] + "0" + v[i + 1:])
                if sub in allf.index:
                    deltas.append(r.train_nll - allf.loc[sub, "train_nll"])
    deltas = np.array(deltas)
    print(f"1. nested pairs (all trials): {len(deltas)}; larger model worse in {np.mean(deltas > 0):.0%}, by > 5 NLL in {np.mean(deltas > 5):.0%}, by > 20 in {np.mean(deltas > 20):.1%} (max {deltas.max():.1f})")

    cv = df[df.split.isin(folds)].groupby(["mouse", "variant"]).test_nll.sum().unstack()
    allr = allf.reset_index()
    allr["bic"] = 2 * allr.train_nll + allr.k * np.log(allr.n)
    bic = allr.pivot(index="mouse", columns="variant", values="bic")
    best = pd.DataFrame({"n_trials": allr.groupby("mouse").n.first(), "best_cv": cv.idxmin(axis=1), "best_bic": bic.idxmin(axis=1)})
    print("\n2. best model per mouse (held-out NLL summed over folds; BIC on all trials):")
    print(best.to_string())

    freq, xp, pxp, bor = rfx_bms(-cv.values)
    res = pd.DataFrame({"expected_freq": freq, "xp": xp, "pxp": pxp}, index=cv.columns).sort_values("pxp", ascending=False)
    print(f"\n3. random-effects BMS over {len(variants)} models (CV log likelihood); Bayesian omnibus risk {bor:.3f}:")
    print(res.head(6).round(3).to_string())

    long = cv.stack().rename("test_nll").reset_index()
    table, family = [], []
    for letter in letters:
        others = [c for c in letters if c != letter]
        key = lambda v: tuple(v[v.index(c) + 1] for c in others)  # noqa: E731
        on = long[long.variant.map(lambda v: mechanism_on(v, letter))].assign(rest=lambda x: x.variant.map(key)).set_index(["mouse", "rest"]).test_nll
        off = long[~long.variant.map(lambda v: mechanism_on(v, letter))].assign(rest=lambda x: x.variant.map(key)).set_index(["mouse", "rest"]).test_nll
        d = (on - off).groupby("mouse").mean()
        table.append({"mechanism": MECHANISM_NAMES.get(letter, letter), "mice_helped(>2)": int((d < -2).sum()), "mice_hurt(>2)": int((d > 2).sum()), "sum": round(d.sum(), 1), **{m: round(v, 1) for m, v in d.items()}})
        on_cols = [c for c in cv.columns if mechanism_on(c, letter)]
        off_cols = [c for c in cv.columns if not mechanism_on(c, letter)]
        fam_lme = np.stack([logsumexp(-cv[on_cols].values, axis=1) - np.log(len(on_cols)), logsumexp(-cv[off_cols].values, axis=1) - np.log(len(off_cols))], axis=1)
        fr, fxp, fpxp, fbor = rfx_bms(fam_lme)
        family.append({"mechanism": MECHANISM_NAMES.get(letter, letter), "P(freq on)": round(fr[0], 2), "xp(on)": round(fxp[0], 3), "pxp(on)": round(fpxp[0], 3), "omnibus_risk": round(fbor, 3)})
    print("\n4. per mechanism: held-out NLL change when switched on (mean over matched model pairs; negative = helps):")
    print(pd.DataFrame(table).set_index("mechanism").to_string())
    print("\n5. family-level random-effects selection per mechanism (with vs without):")
    print(pd.DataFrame(family).set_index("mechanism").to_string())

    tot = cv.sum()
    print("\n6. summed held-out NLL per model, relative to the best (top 10):")
    print((tot - tot.min()).sort_values().head(10).round(1).to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fits_dir", default="ddm/fits_guess", help="relative to the processed data directory")
    parser.add_argument("--folds", nargs="*", help="CV folds to use (default: every fold complete for all mice and variants)")
    args = parser.parse_args()
    main(Path(dir_config.data.processed) / args.fits_dir, args.folds)
