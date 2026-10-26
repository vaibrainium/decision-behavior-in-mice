"""Figure 5: control-fitted models misplace the pulse effect in time.

Publication redraw of the audited package-E diagnostic tables.  The figure is
descriptive: it does not perform a paired model-versus-data test and does not
turn the pulse time course into a confirmatory timing/primacy analysis.

Usage
-----
    python -m scripts.paper.fig5_model_mismatch
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from scripts.paper.style import FULL_WIDTH, LEFT_COLOR, MM, NEUTRAL_COLOR, RIGHT_COLOR, apply_style, label_panel, save_publication

RUN_ID = "20261023T191030Z_fa8de8b"
RUN = Path("/mnt/data/processed/pulse_followup") / RUN_ID / "diagnostics"
MICE = ["DBM5", "DBM6", "DBM12", "DBM13", "DBM14", "DBM15", "PSUIM5", "PSUIM6", "PSUIM7", "PSUIM10"]
DIAGNOSTIC_MICE = ("PSUIM6", "PSUIM7")


def load_tables():
    curves = pd.read_csv(RUN / "e4_model_vs_D_curves.csv.gz")
    summary = pd.read_csv(RUN / "e4_model_vs_D_summary.csv")
    profiles = pd.read_csv(RUN / "e2_e3_profiles.csv.gz")
    optima = pd.read_csv(RUN / "e3_optima.csv")
    verdict = pd.read_csv(RUN / "e3_tradeoff_verdict.csv")
    return curves, summary, profiles, optima, verdict


def mean_curve(curves, source, gain_label=None):
    q = curves[(curves.source == source) & (curves.quantity == "direction")].copy()
    if source == "model":
        q = q[(q.baseline == "primary") & (q.gain_label == gain_label)]
    if q.mouse.nunique() != 10:
        raise ValueError(f"Expected ten mice for {source}/{gain_label}")
    out = q.groupby("u").value.agg(["mean", "std", "count"]).reset_index()
    crit = stats.t.ppf(0.975, out["count"] - 1)
    half = crit * out["std"] / np.sqrt(out["count"])
    out["low"], out["high"] = out["mean"] - half, out["mean"] + half
    return out


def panel_curves(ax, curves):
    specs = [
        ("observed_ddm_rows", None, "Observed", "black", "-", 1.6),
        ("model", "w1", "Model, gain = 1", LEFT_COLOR, ":", 1.2),
        ("model", "w_all_stored", "Model, joint gain", LEFT_COLOR, "--", 1.3),
        ("model", "w_choice_only", "Model, choice gain", RIGHT_COLOR, "-", 1.4),
    ]
    for source, gain, label, color, ls, lw in specs:
        d = mean_curve(curves, source, gain)
        ax.plot(d.u, 100*d["mean"], color=color, ls=ls, lw=lw, label=label)
    ax.axhline(0, color="0.7", lw=0.7, ls=":")
    ax.set_xlim(0, 4.58)
    ax.set_xlabel("Time from logged pulse onset (s)")
    ax.set_ylabel("Cumulative directional contrast\n(percentage points)")
    ax.set_title("Observed and predicted time courses", loc="left")
    ax.legend(loc="lower right", ncols=2, columnspacing=0.9, handlelength=2.0)


def summary_row(summary, source, gain_label, feature):
    q = summary[(summary.source == source) & (summary.quantity == "direction") &
                (summary.feature == feature)]
    if source == "model":
        q = q[(q.baseline == "primary") & (q.gain_label == gain_label)]
    if len(q) != 1:
        raise ValueError(f"Expected one row for {source}/{gain_label}/{feature}, found {len(q)}")
    return q.iloc[0]


def panel_windows(ax, summary):
    features = ["window_0-0.5", "window_0.5-1", "window_1-2", "window_2-4.58"]
    labels = ["0–0.5", "0.5–1", "1–2", "2–4.58"]
    specs = [
        ("observed_ddm_rows", None, "Observed", "black", "o"),
        ("model", "w_all_stored", "Joint gain", LEFT_COLOR, "s"),
        ("model", "w_choice_only", "Choice gain", RIGHT_COLOR, "^"),
    ]
    x = np.arange(len(features))
    offsets = (-0.20, 0.0, 0.20)
    for off, (source, gain, label, color, marker) in zip(offsets, specs):
        rows = [summary_row(summary, source, gain, f) for f in features]
        m = np.array([r["mean"] for r in rows]) * 100
        lo = np.array([r.ci_low for r in rows]) * 100
        hi = np.array([r.ci_high for r in rows]) * 100
        ax.errorbar(x+off, m, yerr=[m-lo, hi-m], fmt=marker, color=color, ms=3.8,
                    capsize=1.7, elinewidth=0.8, label=label)
    ax.axhline(0, color="0.7", lw=0.7, ls=":")
    ax.set_xticks(x, labels)
    ax.set_xlabel("Window after onset (s)")
    ax.set_ylabel("Change within window\n(percentage points)")
    ax.set_title("When the contrast changed", loc="left")
    ax.legend(loc="lower left", handletextpad=0.3)


def panel_profiles(ax, profiles, optima):
    mouse_colors = {"PSUIM6": "#009E73", "PSUIM7": "#CC79A7"}
    for mouse in DIAGNOSTIC_MICE:
        q = profiles[(profiles.baseline == "primary") & (profiles.mouse == mouse) &
                     (profiles.scope == "in_sample") & (profiles.gain <= 10)].sort_values("gain")
        o = optima[(optima.baseline == "primary") & (optima.mouse == mouse) & (optima.scope == "in_sample")]
        if len(o) != 1:
            raise ValueError(f"Missing in-sample optimum for {mouse}")
        o = o.iloc[0]
        for field, objective, optimum, ls in [
            ("choice_given_resp", "choice", o.w_choice_only, "-"),
            ("total", "joint", o.w_joint, "--"),
        ]:
            y = q[field] - q[field].min()
            scale = y.max()
            yn = y / scale if scale > 0 else y
            color = mouse_colors[mouse]
            ax.plot(q.gain, yn, color=color, ls=ls, lw=1.25, label=f"{mouse}, {objective}")
            ax.scatter([optimum], [0], color=color, marker="o" if objective == "choice" else "s",
                       s=20, zorder=3)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.04, 1.04)
    ax.set_xlabel("Pulse gain\nJoint → choice optimum: PSUIM6 2.4 → 7.0; PSUIM7 1.4 → 4.0")
    ax.set_ylabel("Normalized ΔNLL\n(within objective)")
    ax.set_title("Choice and joint objectives disagree in two mice", loc="left")
    ax.legend(loc="upper center", ncols=2, columnspacing=0.8, handlelength=1.7)


def panel_heldout(ax, verdict):
    d = verdict[(verdict.baseline == "primary")].set_index("mouse").loc[MICE].reset_index()
    y = np.arange(len(d))[::-1]
    choice_change = -d.heldout_choice_gain_sum_mean.to_numpy()
    rest_change = d.heldout_rest_cost_sum_mean.to_numpy()
    for i in range(len(d)):
        ax.plot([choice_change[i], rest_change[i]], [y[i], y[i]], color="0.82", lw=0.7, zorder=0)
    ax.scatter(choice_change, y, marker="o", s=18, facecolor="white", edgecolor=RIGHT_COLOR,
               linewidth=0.8, label="choice term", zorder=2)
    ax.scatter(rest_change, y, marker="s", s=18, facecolor="white", edgecolor=LEFT_COLOR,
               linewidth=0.8, label="remaining objective", zorder=2)
    strong = d.mouse.isin(DIAGNOSTIC_MICE)
    ax.scatter(choice_change[strong], y[strong], marker="o", s=22, color=RIGHT_COLOR, zorder=3)
    ax.scatter(rest_change[strong], y[strong], marker="s", s=22, color=LEFT_COLOR, zorder=3)
    ax.axvline(0, color="0.65", lw=0.7, ls=":")
    ax.set_yticks(y, d.mouse)
    ax.set_xlabel("Held-out NLL change at choice-optimal gain\n(relative to joint gain; lower is better)")
    ax.set_title("Held-out tradeoff across mice", loc="left")
    ax.legend(loc="center right", handletextpad=0.3)
    ax.text(0.98, 0.98, "filled: prespecified tradeoff demonstrated",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.0, color="0.3")


def write_source_data(base, curves, summary, profiles, optima, verdict):
    curve_keep = curves[(curves.quantity == "direction") & (
        curves.source.eq("observed_ddm_rows") |
        (curves.source.eq("model") & curves.baseline.eq("primary") &
         curves.gain_label.isin(["w1", "w_all_stored", "w_choice_only"])))].copy()
    features = ["window_0-0.5", "window_0.5-1", "window_1-2", "window_2-4.58"]
    summary_keep = summary[(summary.quantity == "direction") & summary.feature.isin(features) & (
        summary.source.eq("observed_ddm_rows") |
        (summary.source.eq("model") & summary.baseline.eq("primary") &
         summary.gain_label.isin(["w_all_stored", "w_choice_only"])))].copy()
    profile_keep = profiles[(profiles.baseline == "primary") & profiles.mouse.isin(DIAGNOSTIC_MICE) &
                            (profiles.scope == "in_sample") & (profiles.gain <= 10)].copy()
    optima_keep = optima[(optima.baseline == "primary") & optima.mouse.isin(DIAGNOSTIC_MICE) &
                         (optima.scope == "in_sample")].copy()
    verdict_keep = verdict[verdict.baseline.eq("primary")].copy()
    for suffix, data in [
        ("source_curves", curve_keep), ("source_windows", summary_keep),
        ("source_profiles", profile_keep), ("source_optima", optima_keep),
        ("source_heldout_tradeoff", verdict_keep),
    ]:
        data.to_csv(base.with_name(base.name + f"_{suffix}.csv"), index=False)


def main():
    apply_style()
    curves, summary, profiles, optima, verdict = load_tables()
    fig = plt.figure(figsize=(FULL_WIDTH, 137*MM), layout="constrained")
    outer = fig.add_gridspec(2, 2, height_ratios=[0.90, 1.05], width_ratios=[1.25, 1.0])
    ax_a = fig.add_subplot(outer[0, 0])
    ax_b = fig.add_subplot(outer[0, 1])
    ax_c = fig.add_subplot(outer[1, 0])
    ax_d = fig.add_subplot(outer[1, 1])
    panel_curves(ax_a, curves)
    panel_windows(ax_b, summary)
    panel_profiles(ax_c, profiles, optima)
    panel_heldout(ax_d, verdict)
    for letter, ax in (("A", ax_a), ("B", ax_b), ("C", ax_c), ("D", ax_d)):
        label_panel(ax, letter, x=-0.18 if letter != "D" else -0.24, y=1.06)
    base = save_publication(fig, "fig5_model_mismatch")
    write_source_data(base, curves, summary, profiles, optima, verdict)

    windows = ["window_0-0.5", "window_0.5-1", "window_1-2", "window_2-4.58"]
    obs = [100*summary_row(summary, "observed_ddm_rows", None, f)["mean"] for f in windows]
    pred = [100*summary_row(summary, "model", "w_choice_only", f)["mean"] for f in windows]
    print("observed window increments (pp):", ", ".join(f"{x:.3f}" for x in obs))
    print("choice-gain model increments (pp):", ", ".join(f"{x:.3f}" for x in pred))
    for mouse in DIAGNOSTIC_MICE:
        r = verdict[(verdict.baseline == "primary") & (verdict.mouse == mouse)].iloc[0]
        print(f"{mouse}: held-out choice benefit {r.heldout_choice_gain_sum_mean:.3f}, "
              f"remaining-objective cost {r.heldout_rest_cost_sum_mean:.3f}")


if __name__ == "__main__":
    main()
