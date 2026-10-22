"""Extrema detection (E) vs the common model (C) on control trials (primacy plan, amendment 4 items 2-3; amendment 5
item 3). No pulse-trial outcome is used.

Reports:
  1. held-out NLL per mouse, summed over the control-only CV folds ccv0-ccv4, E minus C (negative = E better),
     and summed over mice; mice beyond THRESHOLD NLL either way (step 3.3 used the same > 10 NLL, about the
     per-mouse Monte Carlo SD at 15 repetitions, analysis log 5.6);
  2. E's fitted parameters at their bounds (within 1% of the range): leak_rate, a, drift_gain, per split;
  3. the amendment 5 refit rule: E is refitted with drift_gain <= 200 if drift_gain is within 1% of its upper bound
     in any mouse's all-control fit, or in more than 10% of its ccv fits;
  4. descriptive integration time constants from the leak 0-200 /s fits of all control trials (amendment 4 item 2),
     on the model's discrete-time scale (1 ms steps; ~10% off at 200 /s, amendment 5).
Missing fits are listed, not filled in, so the script can be run while jobs are still arriving.

Usage: python -m scripts.ddm.compare_strategy [--fixed_guess_bias] [--e_dir ...] [--c_dir ...] [--d_dir ...]
"""

import argparse
import glob
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import BASE_FREE_PARAMS, EXTREMA_LEAK_BOUNDS

E_VARIANT, C_VARIANT = "L1U0V1Z0G1", "L0U0V1Z0G1"
FOLDS = [f"ccv{k}" for k in range(5)]
THRESHOLD = 10.0
AT_BOUND = 0.01  # fraction of the parameter range
REFIT_CCV_FRACTION = 0.10


def load_dir(d: Path, variant: str) -> pd.DataFrame:
    rows = []
    for p in glob.glob(str(d / f"*_{variant}_*.pkl")):
        with open(p, "rb") as f:
            r = pickle.load(f)
        rows.append({"mouse": r["mouse"], "split": r["split"], "train_nll": r["train_nll"], "test_nll": r.get("test_nll"),
                     "leak_bounds": tuple(r["leak_bounds"]) if r.get("leak_bounds") else None, "drift_gain_max": r.get("drift_gain_max"),
                     "guess_model": r.get("guess_model"), "fixed_guess_bias": r.get("fixed_guess_bias", False), **r["parameters"]})
    return pd.DataFrame(rows)


def at_bounds(df: pd.DataFrame) -> pd.DataFrame:
    """Flags per fit: parameter within AT_BOUND of the range at the lower ('lo') or upper ('hi') end."""
    out = df[["mouse", "split"]].copy()
    for name in ["leak_rate", "a", "drift_gain"]:
        if name == "leak_rate":
            lo = df.leak_bounds.map(lambda b: b[0] if b else 0.0)
            hi = df.leak_bounds.map(lambda b: b[1] if b else 5.0)
        else:
            lo = BASE_FREE_PARAMS[name].lower_bound
            hi = pd.to_numeric(df.drift_gain_max, errors="coerce").fillna(BASE_FREE_PARAMS[name].upper_bound) if name == "drift_gain" else BASE_FREE_PARAMS[name].upper_bound
        tol = AT_BOUND * (hi - lo)
        out[name] = np.select([df[name] <= lo + tol, df[name] >= hi - tol], ["lo", "hi"], "")
    return out


def main(e_dir: Path, c_dir: Path, d_dir: Path, fixed_guess_bias: bool):
    E, C = load_dir(e_dir, E_VARIANT), load_dir(c_dir, C_VARIANT)
    for name, df, want_leak in [("E", E, EXTREMA_LEAK_BOUNDS), ("C", C, None)]:
        if len(df):
            forms = df[["guess_model", "fixed_guess_bias", "leak_bounds"]].drop_duplicates().to_dict("records")
            print(f"{name}: {len(df)} fits in {e_dir if name == 'E' else c_dir}; forms {forms}")
            bad = df[(df.guess_model != "fast_only") | (df.fixed_guess_bias != fixed_guess_bias) | (df.leak_bounds.map(lambda b: b != (tuple(want_leak) if want_leak else None)))]
            if len(bad):
                raise SystemExit(f"{name}: {len(bad)} fits with an unexpected form (guess model, bias or leak bounds); check the folders")
        else:
            print(f"{name}: no fits in {e_dir if name == 'E' else c_dir}")

    mice = sorted(set(E.mouse) | set(C.mouse))
    have = lambda df: set(zip(df.mouse, df.split))  # noqa: E731
    missing = {name: sorted({(m, s) for m in mice for s in FOLDS + ["control"]} - have(df) - ({(m, "control") for m in mice} if name == "C" else set())) for name, df in [("E", E), ("C", C)]}
    for name, miss in missing.items():
        if miss:
            print(f"missing {name} fits ({len(miss)}): {miss[:12]}{' ...' if len(miss) > 12 else ''}")

    # 1. held-out NLL on control-only CV
    cv = {}
    for name, df in [("E", E), ("C", C)]:
        f = df[df.split.isin(FOLDS)]
        complete = f.groupby("mouse").split.nunique() == len(FOLDS)
        cv[name] = f[f.mouse.isin(complete[complete].index)].groupby("mouse").test_nll.sum()
    both = cv["E"].index.intersection(cv["C"].index)
    if len(both):
        d = (cv["E"][both] - cv["C"][both]).rename("E - C")
        print(f"\n1. held-out NLL, CV within control trials, E minus C (negative = E better), {len(both)} mice:")
        print(d.round(1).to_string())
        print(f"summed: {d.sum():.1f}; E better by > {THRESHOLD:g} in {(d < -THRESHOLD).sum()}, C better by > {THRESHOLD:g} in {(d > THRESHOLD).sum()} of {len(d)}")

    # 2-3. E at bounds; refit rule
    if len(E):
        b = at_bounds(E)
        print("\n2. E parameters at a bound (lo/hi within 1% of the range), fits flagged:")
        for name in ["leak_rate", "a", "drift_gain"]:
            print(f"  {name}: lo {int((b[name] == 'lo').sum())}, hi {int((b[name] == 'hi').sum())} of {len(b)}")
        print("  leak_rate (/s) and drift_gain per mouse, all-control fit:")
        ctrl = E[E.split == "control"].set_index("mouse")
        if len(ctrl):
            print(ctrl[["leak_rate", "a", "drift_gain", "sv", "p_guess"]].round(3).to_string())
        hi_ctrl = b[(b.split == "control") & (b.drift_gain == "hi")].mouse.tolist()
        ccv = b[b.split.isin(FOLDS)]
        frac = float((ccv.drift_gain == "hi").mean()) if len(ccv) else float("nan")
        refit = bool(hi_ctrl) or frac > REFIT_CCV_FRACTION
        print(f"\n3. amendment 5 rule: drift_gain at its upper bound in all-control fits of {hi_ctrl or 'no mouse'}; in {frac:.0%} of ccv fits"
              f" -> {'REFIT E with --drift_gain_max 200 (analysis log 8.4d)' if refit else 'no refit'}"
              f"{' (provisional: fits missing)' if missing['E'] else ''}")

    # 4. descriptive integration time constant
    D = load_dir(d_dir, E_VARIANT)
    D = D[D.split == "control"] if len(D) else D
    if len(D):
        D = D.assign(tau_ms=1000 / D.leak_rate.where(D.leak_rate > 0))
        flags = at_bounds(D).set_index("mouse").leak_rate
        print(f"\n4. integration time constant, leak 0-200 /s, all control trials ({d_dir}):")
        print(D.set_index("mouse")[["leak_rate", "tau_ms", "train_nll"]].assign(at_bound=flags).round(2).to_string())
    else:
        print(f"\n4. no descriptive leak 0-200 fits in {d_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fixed_guess_bias", action="store_true", help="use the guess_bias = 0.5 folders (_FB)")
    parser.add_argument("--e_dir", help="E fits (default ddm/fits_guess_fast_only[_FB]_leak20-200)")
    parser.add_argument("--c_dir", help="common-model control-only CV fits (default ddm/fits_guess_fast_only[_FB])")
    parser.add_argument("--d_dir", help="descriptive leak 0-200 fits (default ddm/fits_guess_fast_only[_FB]_leak0-200)")
    args = parser.parse_args()
    processed = Path(dir_config.data.processed)
    fb = "_FB" if args.fixed_guess_bias else ""
    main(processed / (args.e_dir or f"ddm/fits_guess_fast_only{fb}_leak20-200"), processed / (args.c_dir or f"ddm/fits_guess_fast_only{fb}"),
         processed / (args.d_dir or f"ddm/fits_guess_fast_only{fb}_leak0-200"), args.fixed_guess_bias)
