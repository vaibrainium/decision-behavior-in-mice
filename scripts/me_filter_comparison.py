"""Compare motion-energy filters: the pipeline's mouse filter vs Okazawa et al. (2018) as published and with only
their temporal filter (plan .agents/plans/2026-10-29-motion-energy-filter-comparison.md).

Inputs: raw ME shards per filter in <processed>/<dir>/me_shard_*.pkl (scripts/compute_motion_energy_full.py), the
trial table valid_data.csv (responses at 0.3-5 s only) and hidden_coherence.csv. Each filter is calibrated the same
way as the pipeline (scripts/assemble_motion_energy.py): per rig, raw ME divided by the slope of trial-mean ME vs
nominal % coherence on non-pulse trials after the 9-frame warm-up; global pooling only.

Per filter:
  tuning      preferred SF, TF and speed of the filters (peaks of the quadrature pairs' amplitude spectra)
  coherence   calibrated mean ME per rig x coherence; SD of trial-mean ME at 0% (noise in % coherence units) and its
              correlation with the hidden coherence (net dot motion at onset, methods report 5.1)
  pulse       ME response to a pulse per 100% change, per rig (as scripts/ddm/build_ddm_inputs.pulse_response):
              peak, time to peak, area; onset step response
  choices     per mouse, control trials (no scheduled coherence change): 5-fold CV logistic regression of choice on
              coherence (categorical) with and without residual ME (trial-mean ME over 150 ms to the response,
              minus its mean for the mouse x coherence); held-out log-likelihood gain in millibits per trial; and the
              weight of residual ME relative to coherence (|c| <= 36%, full data). Mice as unit: paired Wilcoxon
              between filters, Holm over the 3 pairs.

Outputs: dissemination/paper_accumulation/tables/me_filter_comparison_<date>_{tuning,coherence,pulse,choices,tests}.csv
         dissemination/paper_accumulation/figures/qc/me_filter_comparison_<date>.{png,pdf}
Usage: python -m scripts.me_filter_comparison [--filters mouse=motion_energy_mouse okazawa=... ...]
"""

import argparse
import math
from datetime import date
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from statsmodels.stats.multitest import multipletests

from config import dir_config
from scripts.assemble_motion_energy import WARMUP_FRAMES, load_shards
from scripts.compute_motion_energy_full import convert_to_frame_units
from scripts.ddm.build_ddm_inputs import PULSE_RESPONSE_FRAMES, pulse_response, scheduled_pulse, step_response
from scripts.motion_energy import mouse_me_kernels

PROCESSED = Path(dir_config.data.processed)
ROOT = Path(__file__).resolve().parents[1] / "dissemination" / "paper_accumulation"
FRAME_RATE = 60
DEFAULT_FILTERS = {"mouse": "motion_energy_mouse", "okazawa_temporal": "motion_energy_okazawa_temporal", "okazawa": "motion_energy_okazawa"}
COLOURS = {"mouse": "k", "okazawa_temporal": "tab:blue", "okazawa": "tab:red"}
N_FOLDS = 5


def tuning(params: dict) -> dict:
    """Preferred SF (c/deg), TF (Hz) and speed (deg/s) from the amplitude spectra of the quadrature pairs."""
    k = mouse_me_kernels(params)
    n = 1 << 16
    sf = np.fft.rfftfreq(n, params["dx_deg"])
    tf = np.fft.rfftfreq(n, params["dt_s"])
    fx = np.abs(np.fft.fft(k["fx"][0] + 1j * k["fx"][1], n))[: len(sf)]
    gt = np.abs(np.fft.fft(k["gt"][0] + 1j * k["gt"][1], n))[: len(tf)]
    gt_neg = np.abs(np.fft.fft(k["gt"][0] - 1j * k["gt"][1], n))[: len(tf)]
    sf_peak = sf[np.argmax(fx)]
    tf_peak = tf[np.argmax(np.maximum(gt, gt_neg))]
    return {"sigma_c_deg": params["sigma_c_deg"], "sigma_g_deg": params["sigma_g_deg"], "k_per_s": params["k_per_s"], "grid_deg": params["dx_deg"],
            "sf_cpd": sf_peak, "tf_hz": tf_peak, "speed_deg_s": tf_peak / sf_peak}


def load_filter(directory: str, data: pd.DataFrame) -> tuple[np.ndarray, dict, dict]:
    """Calibrated global ME (n_trials, n_frames) in data's row order, the filter params, and the per-rig slopes."""
    me, params, _ = load_shards(PROCESSED / directory)
    missing = ~data.agg_code.isin(me.keys())
    if missing.any():
        raise ValueError(f"{directory}: {missing.sum()} trials without ME, e.g. {data.agg_code[missing].tolist()[:3]}")
    x = np.stack([me[c]["global"] for c in data.agg_code]).astype(np.float64)
    slopes = {}
    control = ~data.is_pulse_trial.to_numpy(bool)
    for rig in data.data_source.unique():
        rows = (data.data_source == rig).to_numpy()
        slopes[rig] = np.polyfit(data.signed_coherence[rows & control], x[rows & control, WARMUP_FRAMES:].mean(axis=1), 1)[0]
        x[rows] /= slopes[rig]
    return x, params, slopes


def coherence_table(name, x, data, hidden):
    rows = []
    control = (data.sched_pulse_type == 0).to_numpy()
    trial_mean = x[:, WARMUP_FRAMES:].mean(axis=1)
    for rig in sorted(data.data_source.unique()):
        r = control & (data.data_source == rig).to_numpy()
        for c in sorted(data.signed_coherence.unique()):
            m = r & (data.signed_coherence == c).to_numpy()
            rows.append({"filter": name, "rig": rig, "coherence": c, "mean_me": trial_mean[m].mean(), "sd_me": trial_mean[m].std(ddof=1), "n": int(m.sum())})
        zero = r & (data.signed_coherence == 0).to_numpy()
        h = hidden.reindex(data.agg_code[zero]).to_numpy()
        ok = ~np.isnan(h)
        rows.append({"filter": name, "rig": rig, "coherence": "corr_hidden_at_0", "mean_me": np.corrcoef(trial_mean[zero][ok], h[ok])[0, 1], "n": int(ok.sum())})
    return rows


def pulse_table(name, x, data):
    """Onset step and pulse response per rig, per 100% coherence change, as in build_ddm_inputs."""
    rows, curves = [], []
    n_frames = x.shape[1]
    onset = data.pulse_onset_frame.fillna(0).to_numpy(int) - 1
    length = (data.pulse_offset_frame - data.pulse_onset_frame).fillna(0).to_numpy(int)
    delta = (data.pulse_coherence - data.signed_coherence).fillna(0).to_numpy(float)
    coh = data.signed_coherence.to_numpy(float)
    for rig in sorted(data.data_source.unique()):
        rows_rig = (data.data_source == rig).to_numpy()
        fit = rows_rig & (data.sched_pulse_type == 0).to_numpy() & (coh != 0)
        step = step_response(x[fit], coh[fit])
        pulsed = rows_rig & (data.sched_pulse_type != 0).to_numpy()
        lengths, counts = np.unique(length[pulsed], return_counts=True)
        main_length = lengths[np.argmax(counts)]
        usable = np.flatnonzero(pulsed & (length == main_length) & (onset >= 1) & (onset + PULSE_RESPONSE_FRAMES <= n_frames))
        resp = 100 * pulse_response(x[usable] - coh[usable, None] * step[None, :], onset[usable], delta[usable], PULSE_RESPONSE_FRAMES)
        t = np.arange(PULSE_RESPONSE_FRAMES) / FRAME_RATE
        rows.append({"filter": name, "rig": rig, "pulse_frames": int(main_length), "n_trials": len(usable), "peak": resp.max(), "time_to_peak_ms": 1000 * t[np.argmax(resp)],
                     "area_s": resp.sum() / FRAME_RATE, "nominal_area_s": main_length / FRAME_RATE,
                     "step_time_to_half_ms": 1000 * np.argmax(step >= 0.5) / FRAME_RATE})
        curves.append(pd.DataFrame({"filter": name, "rig": rig, "t_ms": 1000 * t, "pulse": resp, "step": step[:PULSE_RESPONSE_FRAMES]}))
    return rows, curves


def choice_table(name, x, data):
    """Per mouse, held-out gain from residual ME and its weight relative to coherence."""
    rows = []
    control = (data.sched_pulse_type == 0).to_numpy()
    rt = data.rt_frame.to_numpy(int)
    window = np.array([x[i, WARMUP_FRAMES:max(WARMUP_FRAMES + 1, min(rt[i], x.shape[1]))].mean() for i in range(len(x))])
    for mouse in sorted(data.subject_id.unique()):
        m = control & (data.subject_id == mouse).to_numpy()
        d = pd.DataFrame({"coh": data.signed_coherence[m].to_numpy(), "me": window[m], "y": data.choice[m].to_numpy()})
        d["resid"] = d.me - d.groupby("coh").me.transform("mean")
        base = pd.get_dummies(d.coh.astype(int), prefix="c").to_numpy(float)
        full = np.column_stack([base, d.resid / 10])
        gain = []
        for train, test in StratifiedKFold(N_FOLDS, shuffle=True, random_state=0).split(base, d.coh.astype(str) + d.y.astype(str)):
            ll = []
            for X in (base, full):
                p = LogisticRegression(C=1e4, max_iter=2000).fit(X[train], d.y.to_numpy()[train]).predict_proba(X[test])[:, 1]
                y = d.y.to_numpy()[test]
                ll.append(np.sum(y * np.log2(p) + (1 - y) * np.log2(1 - p)))
            gain.append(ll[1] - ll[0])
        low = d.coh.abs() <= 36
        w = LogisticRegression(C=1e4, max_iter=2000).fit(np.column_stack([d.coh[low] / 10, d.resid[low] / 10]), d.y[low]).coef_[0]
        rows.append({"filter": name, "mouse": mouse, "n_trials": int(m.sum()), "gain_mbit_per_trial": 1000 * np.sum(gain) / len(d),
                     "w_coherence": w[0], "w_resid": w[1], "resid_vs_coherence": w[1] / w[0], "resid_sd": d.resid.std()})
    return rows


def tests(choices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for measure in ["gain_mbit_per_trial", "resid_vs_coherence"]:
        wide = choices.pivot(index="mouse", columns="filter", values=measure)
        part = []
        for a, b in combinations(wide.columns, 2):
            diff = (wide[a] - wide[b]).dropna()
            part.append({"measure": measure, "contrast": f"{a} - {b}", "n_mice": len(diff), "median_diff": diff.median(), "mean_diff": diff.mean(),
                         "n_positive": int((diff > 0).sum()), "dz": diff.mean() / diff.std(ddof=1), "p_wilcoxon": wilcoxon(diff).pvalue})
        part = pd.DataFrame(part)
        part["p_holm"] = multipletests(part.p_wilcoxon, method="holm")[1]
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def figure(coherence, curves, choices, stem):
    names = list(dict.fromkeys(choices["filter"]))
    rigs = sorted(curves.rig.unique())
    fig, axes = plt.subplots(1, 2 + len(rigs), figsize=(4.2 * (2 + len(rigs)), 3.8))
    for j, rig in enumerate(rigs):
        ax = axes[j]
        for name in names:
            c = curves[(curves["filter"] == name) & (curves.rig == rig)]
            ax.plot(c.t_ms, c.pulse, color=COLOURS.get(name), label=name)
        n = 3 if rig == "ucla" else 4
        ax.step([0, 1000 * n / FRAME_RATE], [100, 100], where="post", color="0.6", lw=1, label="nominal pulse (100%)")
        ax.plot([0, 0], [0, 100], color="0.6", lw=1)
        ax.set_title(f"ME response to a 100% pulse, rig {rig}", fontsize=9)
        ax.set_xlabel("time from pulse onset (ms)"); ax.set_ylabel("ME (% coherence)")
        ax.legend(frameon=False, fontsize=7)
    ax = axes[-2]
    zero = coherence[coherence.coherence == 0]
    x = np.arange(len(names))
    for k, rig in enumerate(rigs):
        s = zero[zero.rig == rig].set_index("filter").loc[names]
        ax.bar(x + (k - 0.5) * 0.35, 100 / s.sd_me.astype(float), width=0.35, label=f"rig {rig}", color=["0.3", "0.7"][k])
    ax.set_xticks(x, names, fontsize=8); ax.set_ylabel("100% coherence / SD of trial ME at 0%"); ax.set_title("Direction signal vs stimulus noise", fontsize=9)
    ax.legend(frameon=False, fontsize=7)
    ax = axes[-1]
    wide = choices.pivot(index="mouse", columns="filter", values="gain_mbit_per_trial")[names]
    for _, r in wide.iterrows():
        ax.plot(x, r.to_numpy(), color="0.75", lw=0.8)
    ax.plot(x, wide.mean(), "o-", color="k")
    ax.axhline(0, color="0.6", lw=0.7)
    ax.set_xticks(x, names, fontsize=8); ax.set_ylabel("held-out gain (millibits / trial)")
    ax.set_title("Residual ME predicts choice (per mouse, control trials)", fontsize=9)
    fig.tight_layout()
    fig.savefig(f"{stem}.png", dpi=200)
    fig.savefig(f"{stem}.pdf")


def main(filters: dict):
    data = convert_to_frame_units(pd.read_csv(PROCESSED / "valid_data.csv"))
    data["sched_pulse_type"] = scheduled_pulse(data)
    hidden = pd.read_csv(PROCESSED / "hidden_coherence.csv").set_index("agg_code").hidden_coherence
    tune, coh_rows, pulse_rows, curves, choice_rows = [], [], [], [], []
    for name, directory in filters.items():
        x, params, slopes = load_filter(directory, data)
        print(f"{name}: slopes {slopes}")
        tune.append({"filter": name, **tuning(params)})
        coh_rows += coherence_table(name, x, data, hidden)
        p, c = pulse_table(name, x, data)
        pulse_rows += p
        curves += c
        choice_rows += choice_table(name, x, data)
    day = date.today().isoformat()
    stem = f"me_filter_comparison_{day}"
    (ROOT / "tables").mkdir(parents=True, exist_ok=True)
    (ROOT / "figures" / "qc").mkdir(parents=True, exist_ok=True)
    out = {"tuning": pd.DataFrame(tune), "coherence": pd.DataFrame(coh_rows), "pulse": pd.DataFrame(pulse_rows), "choices": pd.DataFrame(choice_rows)}
    if len(filters) > 1:
        out["tests"] = tests(out["choices"])
    for key, df in out.items():
        df.round(4).to_csv(ROOT / "tables" / f"{stem}_{key}.csv", index=False)
        print(f"\n== {key}\n{df.round(3).to_string(index=False)}")
    figure(out["coherence"], pd.concat(curves), out["choices"], ROOT / "figures" / "qc" / stem)
    print(f"saved tables/{stem}_*.csv and figures/qc/{stem}.png/.pdf")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--filters", nargs="+", default=[f"{k}={v}" for k, v in DEFAULT_FILTERS.items()], help="name=directory under processed/")
    main(dict(f.split("=", 1) for f in ap.parse_args().filters))
