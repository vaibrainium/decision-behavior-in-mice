"""Parameter table of the common model (L0U0V1Z0G1, fast-only guesses, guess bias free) from the final all-trial fits
(plan step 5; `ddm/fits_final`, 50 repetitions), or from the control-trial fits with --split control.

Checks each fit's settings (variant, guess form, repetitions) and flags parameters within 1% of a bound. guess_tau is
reported but marked as not interpreted: model recovery did not recover it (r = 0.18, analysis log 5.8). Also reports
the group median and range over mice, and the recovery correlation of each parameter.

Writes <out_dir>/parameters_common_model[_control]_<date>.csv and .md (a new file per date; existing files are kept).

Usage: python -m scripts.ddm.parameter_table [--fits_dir ddm/fits_final] [--split all|control] [--out_dir dissemination/paper]
"""

import argparse
import datetime
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import make_params

VARIANT, GUESS_MODEL = "L0U0V1Z0G1", "fast_only"
SHOWN = {"ndt": "non-decision time (s)", "a": "bound separation", "z": "starting point (fraction of a)", "drift_gain": "drift gain",
         "drift_offset": "drift offset", "sv": "drift variability (sv)", "p_guess": "fast-guess probability",
         "guess_bias": "fast-guess bias (P right)", "guess_tau": "fast-guess delay (s)"}
NOT_INTERPRETED = {"guess_tau": "not recovered in model recovery (r = 0.18)"}


def to_markdown(df: pd.DataFrame, index: bool = True) -> str:
    """Pipe table without the optional `tabulate` dependency."""
    d = df.reset_index() if index else df
    cells = [[f"{v:.3f}" if isinstance(v, float) else str(v) for v in row] for row in d.itertuples(index=False)]
    lines = ["| " + " | ".join(map(str, d.columns)) + " |", "|" + "---|" * len(d.columns)]
    return "\n".join(lines + ["| " + " | ".join(c) + " |" for c in cells])


def main(fits_dir: Path, split: str = "all", out_dir: Path = Path("dissemination/paper")):
    processed = Path(dir_config.data.processed)
    rec = pd.read_csv(processed / "ddm/recovery/summary_parameters.csv").set_index(["generator", "parameter"])
    free, _ = make_params(VARIANT, GUESS_MODEL)
    rows, flags = [], []
    for path in sorted(fits_dir.glob(f"*_{VARIANT}_{split}.pkl")):
        with open(path, "rb") as f:
            r = pickle.load(f)
        assert (r["variant"], r.get("guess_model"), r.get("fixed_guess_bias", False), r["split"]) == (VARIANT, GUESS_MODEL, False, split), path
        p = r["parameters"]
        rows.append({"mouse": r["mouse"], "n_trials": r["n_train"], "n_reps": r["n_reps"], "train_nll": r["train_nll"],
                     "warm_started": bool(r.get("warm_start_seeds")), **{k: p[k] for k in SHOWN}})
        for k in SHOWN:
            lo, hi = free[k].lower_bound, free[k].upper_bound
            tol = 0.01 * (hi - lo)
            if p[k] <= lo + tol or p[k] >= hi - tol:
                flags.append(f"{r['mouse']} {k} = {p[k]:.3g} at its {'lower' if p[k] <= lo + tol else 'upper'} bound [{lo:g}, {hi:g}]")
    df = pd.DataFrame(rows).set_index("mouse")
    summary = pd.DataFrame({
        "parameter": [SHOWN[k] for k in SHOWN],
        "median": [df[k].median() for k in SHOWN],
        "min": [df[k].min() for k in SHOWN],
        "max": [df[k].max() for k in SHOWN],
        "recovery_r": [rec.loc[(VARIANT, k), "r"] if (VARIANT, k) in rec.index else np.nan for k in SHOWN],
        "note": [NOT_INTERPRETED.get(k, "") for k in SHOWN],
    }, index=list(SHOWN))
    print(f"{len(df)} fits; repetitions {sorted(df.n_reps.unique())}; warm-started {int(df.warm_started.sum())}/{len(df)}")
    print(df[list(SHOWN)].round(3).to_string())
    print("\nsummary over mice:")
    print(summary.round(3).to_string())
    print("\nat a bound:" if flags else "\nno parameter at a bound", *flags, sep="\n  ")
    out = out_dir / f"parameters_common_model{'' if split == 'all' else '_' + split}_{datetime.date.today():%Y-%m-%d}"
    df.to_csv(out.with_suffix(".csv"))
    with open(out.with_suffix(".md"), "w") as f:
        f.write(f"# Common-model parameters ({VARIANT}, fast-only guesses, guess bias free; {'all trials' if split == 'all' else split + ' trials'}, {sorted(df.n_reps.unique())} repetitions)\n\n")
        f.write(f"Source: `{fits_dir}`; script `scripts/ddm/parameter_table.py`. Recovery r from `ddm/recovery/summary_parameters.csv`.\n\n")
        f.write(to_markdown(df[list(SHOWN)].rename(columns=SHOWN)) + "\n\n")
        f.write(to_markdown(summary, index=False) + "\n\n")
        f.write(("Parameters at a bound:\n" + "\n".join(f"- {x}" for x in flags) + "\n") if flags else "No parameter at a bound.\n")
    print(f"\nwritten {out}.csv / .md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fits_dir", default="ddm/fits_final", help="relative to processed")
    parser.add_argument("--split", choices=["all", "control"], default="all", help="fit split: all trials or control trials only")
    parser.add_argument("--out_dir", default="dissemination/paper")
    args = parser.parse_args()
    main(Path(dir_config.data.processed) / args.fits_dir, args.split, Path(args.out_dir))
