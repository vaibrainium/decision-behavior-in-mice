"""Fitted sv versus the across-trial spread of motion-energy drift within a pulse cell (signed coherence x
scheduled pulse), for linear-front-end pulse-only sv families (drift(t) = drift_gain * ME(t) + offset + sv draw).
Per trial, mean drift = drift_gain * mean ME over a window; spread = within-cell SD, trial-weighted over cells.
Windows: first 0.25 s, first 0.5 s, and each trial's own decision time (observed RT - fitted ndt, >= 0.05 s).
Usage: python -m scripts.paper.sv_vs_me_drift_spread --output <new dir>"""
import argparse
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.ddm.fit_mouse_ddm import select
from scripts.ddm.pulse_joint_signatures import model_path
from scripts.ddm.rescore_fits import inputs

FAMILIES = ["pulse_linear_primary", "pulse_linear_leak", "pulse_linear_urgency", "pulse_linear_leak_urgency"]

def main(out):
    out.mkdir(parents=True, exist_ok=False)
    x = inputs(); rows = []
    for mouse in np.unique(x["subject_id"]):
        idx = np.flatnonzero((x["subject_id"] == mouse) & (x["sched_pulse_type"] != 0))
        data, stim = select(x, idx)
        cs = np.nancumsum(np.nan_to_num(stim), axis=1)  # 1 ms steps
        for fam in FAMILIES:
            r = pickle.load(model_path(fam)(mouse).open("rb"))
            p = r["parameters"]; assert r.get("front_end") is None and not r.get("ugm", False)
            dec_ms = np.clip(np.round(1000 * (data["rt"] - p["ndt"])).astype(int), 50, stim.shape[1])
            windows = {"0.25s": np.full(len(idx), 250), "0.5s": np.full(len(idx), 500), "decision_time": dec_ms}
            for w, ms in windows.items():
                drift = p["drift_gain"] * cs[np.arange(len(idx)), ms - 1] / ms
                sd = pd.Series(drift).groupby(data["condition"]).agg(["std", "size"]).dropna()
                rows.append(dict(mouse=mouse, family=fam, window=w, sv=p["sv"], drift_gain=p["drift_gain"],
                                 me_drift_sd=np.sqrt(np.average(sd["std"] ** 2, weights=sd["size"]))))
    t = pd.DataFrame(rows); t["ratio_sv_to_me_sd"] = t.sv / t.me_drift_sd
    t.to_csv(out / "sv_vs_me_spread.csv", index=False)
    print(t.pivot_table(index=["family", "window"], values=["sv", "me_drift_sd", "ratio_sv_to_me_sd"],
                        aggfunc="median").round(3).to_string())
    print("\nratio by mouse (decision_time, median over families):")
    print(t[t.window == "decision_time"].groupby("mouse").ratio_sv_to_me_sd.median().round(2).to_string())

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument("--output", required=True, type=Path)
    main(ap.parse_args().output)
