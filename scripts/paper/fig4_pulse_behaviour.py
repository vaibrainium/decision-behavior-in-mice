"""Figure 4: randomized signed pulses shift response direction.

This is a publication redraw of the already-audited exploratory package C/D
outputs.  It performs no re-estimation.  Mouse-level values, group Student-t
intervals, multiplicity-adjusted p values and cumulative curves are read from
the immutable run ``20261023T191030Z_fa8de8b``.

Usage
-----
    python -m scripts.paper.fig4_pulse_behaviour
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.paper.style import (
    FULL_WIDTH,
    LEFT_COLOR,
    MM,
    NEUTRAL_COLOR,
    RIGHT_COLOR,
    apply_style,
    label_panel,
    save_publication,
)

RUN_ID = "20261023T191030Z_fa8de8b"
RUN = Path("/mnt/data/processed/pulse_followup") / RUN_ID
PRIMARY = "primary_coherence"
T_METHOD = "student_t_95_across_mice"
MOUSE_ORDER = ["DBM5", "DBM6", "DBM12", "DBM13", "DBM14", "DBM15", "PSUIM5", "PSUIM6", "PSUIM7", "PSUIM10"]
RIG_MARKER = {"uw": "s", "ucla": "o"}


def load_tables():
    pm = pd.read_csv(RUN / "behaviour" / "per_mouse.csv")
    group = pd.read_csv(RUN / "behaviour" / "group.csv")
    curves = pd.read_csv(RUN / "response_time" / "contrast_curves_group.csv.gz")
    mouse_curves = pd.read_csv(RUN / "response_time" / "contrast_curves_per_mouse.csv.gz")
    coverage = pd.read_csv(RUN / "behaviour" / "coverage.csv")
    return pm, group, curves, mouse_curves, coverage


def select_primary(pm, group):
    p = pm[(pm.analysis_set == PRIMARY) & (pm.contrast == "positive_vs_negative")].copy()
    g = group[(group.analysis_set == PRIMARY) & (group.contrast == "positive_vs_negative") &
              (group.method == T_METHOD)].copy()
    if len(p) != 10 or set(p.mouse) != set(MOUSE_ORDER):
        raise ValueError("Primary mouse table is not the frozen ten-mouse set")
    if set(g.endpoint) != {"Delta_direction", "Delta_R", "Delta_L", "Delta_unresponded"}:
        raise ValueError("Primary group table does not contain the four frozen endpoints")
    return p, g


def group_row(group, contrast, endpoint="Delta_direction"):
    q = group[(group.analysis_set == PRIMARY) & (group.contrast == contrast) &
              (group.endpoint == endpoint) & (group.method == T_METHOD)]
    if len(q) != 1:
        raise ValueError(f"Expected one group row for {contrast}/{endpoint}, found {len(q)}")
    return q.iloc[0]


def panel_mouse_effect(ax, primary, group):
    d = primary.set_index("mouse").loc[MOUSE_ORDER].reset_index()
    y = np.arange(len(d))[::-1]
    for rig, marker in RIG_MARKER.items():
        use = d.rig.eq(rig)
        ax.scatter(d.loc[use, "Delta_direction"], y[use], marker=marker, s=21,
                   facecolor="white", edgecolor=NEUTRAL_COLOR, linewidth=0.8,
                   label="UW" if rig == "uw" else "UCLA", zorder=3)
    ax.axvline(0, color="0.65", lw=0.7, ls=":", zorder=0)
    group_y = -1.15
    ax.set_yticks(np.r_[y, group_y], list(d.mouse) + ["Group mean"])
    ax.set_xlabel("Positive − negative pulse effect (percentage points)\n$\\Delta_{direction}=(\\Delta_R-\\Delta_L)/2$")
    ax.set_title("Directional effect in each mouse", loc="left")
    ax.legend(loc="lower right", handletextpad=0.3)

    r = group_row(group, "positive_vs_negative")
    ax.axhline(-0.55, color="0.82", lw=0.6, zorder=0)
    ax.errorbar(r.estimate, group_y, xerr=[[r.estimate-r.ci_low], [r.ci_high-r.estimate]],
                fmt="D", color="black", ms=4.5, capsize=2, elinewidth=1.0, zorder=4)
    ax.set_ylim(-1.8, len(d)-0.2)
    ax.text(0.98, 0.98, f"n = 10; p$_{{Holm}}$ = {r.p_holm:.3f}", transform=ax.transAxes,
            ha="right", va="top", fontsize=6.3)


def panel_components(ax, primary, group):
    endpoints = ["Delta_R", "Delta_L", "Delta_unresponded"]
    labels = ["Right\nresponse", "Left\nresponse", "No response\nby 5 s"]
    colors = [RIGHT_COLOR, LEFT_COLOR, NEUTRAL_COLOR]
    x = np.arange(3)
    vals = primary.set_index("mouse").loc[MOUSE_ORDER, endpoints].to_numpy()
    for row in vals:
        ax.plot(x, row, color="0.82", lw=0.55, zorder=1)
        ax.scatter(x, row, s=8, facecolor="white", edgecolor="0.55", linewidth=0.45, zorder=2)
    for i, (ep, color) in enumerate(zip(endpoints, colors)):
        r = group_row(group, "positive_vs_negative", ep)
        ax.errorbar(i, r.estimate, yerr=[[r.estimate-r.ci_low], [r.ci_high-r.estimate]],
                    fmt="o", color=color, mec=color, ms=4.8, capsize=2, elinewidth=1.0, zorder=4)
    ax.axhline(0, color="0.65", lw=0.7, ls=":", zorder=0)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Positive − negative pulse\n(probability points)")
    ax.set_title("Response components", loc="left")
    ax.text(0.02, 0.02, "Components sum to zero within mouse", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=6.1, color="0.3")


def panel_control_contrasts(ax, pm, group):
    contrasts = ["positive_vs_control", "control_vs_negative"]
    labels = ["Positive − control\n$ p_{Holm}$ = 0.004", "Control − negative\n$ p_{Holm}$ = 0.393"]
    colors = [RIGHT_COLOR, LEFT_COLOR]
    markers = ["^", "v"]
    for i, (contrast, color, marker) in enumerate(zip(contrasts, colors, markers)):
        d = pm[(pm.analysis_set == PRIMARY) & (pm.contrast == contrast)]
        ax.scatter(np.full(len(d), i), d.Delta_direction, s=15, facecolor="white",
                   edgecolor=color, marker=marker, linewidth=0.65, alpha=0.8, zorder=2)
        r = group_row(group, contrast)
        ax.errorbar(i, r.estimate, yerr=[[r.estimate-r.ci_low], [r.ci_high-r.estimate]],
                    fmt=marker, color=color, ms=5.5, capsize=2, elinewidth=1.0, zorder=4)
    ax.axhline(0, color="0.65", lw=0.7, ls=":", zorder=0)
    ax.set_xticks(range(2), labels)
    ax.set_ylabel("Directional contrast\n(percentage points)")
    ax.set_title("Pulse–control comparisons", loc="left")
    ax.margins(y=0.12)


def panel_timecourse(ax, curves, mouse_curves):
    key = dict(summary="all_scheduled", comparison="pos_vs_neg", onset_stratum="all")
    g = curves[(curves.summary == key["summary"]) & (curves.comparison == key["comparison"]) &
               (curves.onset_stratum == key["onset_stratum"])].sort_values("t")
    p = mouse_curves[(mouse_curves.summary == key["summary"]) &
                     (mouse_curves.comparison == key["comparison"]) &
                     (mouse_curves.onset_stratum == key["onset_stratum"])]
    if len(g) != 459 or g.n_mice.nunique() != 1 or int(g.n_mice.iloc[0]) != 10:
        raise ValueError("Unexpected all-scheduled group curve")
    for _, d in p.groupby("mouse"):
        ax.plot(d.t, 100*d.d_direction, color="0.75", lw=0.45, alpha=0.65, zorder=1)
    ax.fill_between(g.t, 100*g.d_direction_ci_low, 100*g.d_direction_ci_high,
                    color=RIGHT_COLOR, alpha=0.18, lw=0, zorder=2)
    ax.plot(g.t, 100*g.d_direction, color=RIGHT_COLOR, lw=1.4, zorder=3,
            label="equal-mouse mean")
    ax.axhline(0, color="0.65", lw=0.7, ls=":", zorder=0)
    ax.axvline(0, color="0.65", lw=0.7, zorder=0)
    ax.set_xlim(0, 4.58)
    ax.set_xlabel("Time from logged pulse onset (s)")
    ax.set_ylabel("Cumulative directional contrast\n(percentage points)")
    ax.set_title("Response-associated time course", loc="left")
    ax.legend(loc="lower right", handlelength=1.6)
    end = g.iloc[-1]
    ax.annotate(f"{100*end.d_direction:.1f} pp",
                xy=(end.t, 100*end.d_direction), xytext=(3.45, 10.5), fontsize=6.3,
                arrowprops={"arrowstyle": "-", "lw": 0.6, "color": "0.35"}, ha="left")
    ax.text(0.02, 0.02, "thin lines: mice; band: pointwise 95% t CI",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=6.1, color="0.3")


def write_source_data(base, pm, group, curves, mouse_curves, coverage):
    primary, primary_group = select_primary(pm, group)
    comparison_pm = pm[(pm.analysis_set == PRIMARY) & pm.contrast.isin(
        ["positive_vs_control", "control_vs_negative"])].copy()
    comparison_group = group[(group.analysis_set == PRIMARY) & group.contrast.isin(
        ["positive_vs_control", "control_vs_negative"]) & (group.method == T_METHOD)].copy()
    points = pd.concat([
        primary.assign(panel="A-B"),
        comparison_pm.assign(panel="C"),
    ], ignore_index=True, sort=False)
    groups = pd.concat([
        primary_group.assign(panel="A-B"),
        comparison_group.assign(panel="C"),
    ], ignore_index=True, sort=False)
    key = (curves.summary.eq("all_scheduled") & curves.comparison.eq("pos_vs_neg") &
           curves.onset_stratum.eq("all"))
    key_m = (mouse_curves.summary.eq("all_scheduled") & mouse_curves.comparison.eq("pos_vs_neg") &
             mouse_curves.onset_stratum.eq("all"))
    points.to_csv(base.with_name(base.name + "_source_mouse_estimates.csv"), index=False)
    groups.to_csv(base.with_name(base.name + "_source_group_estimates.csv"), index=False)
    curves.loc[key].to_csv(base.with_name(base.name + "_source_timecourse_group.csv"), index=False)
    mouse_curves.loc[key_m].to_csv(base.with_name(base.name + "_source_timecourse_mice.csv"), index=False)
    coverage[coverage.analysis_set.eq(PRIMARY)].to_csv(
        base.with_name(base.name + "_source_coverage.csv"), index=False)


def main():
    apply_style()
    pm, group, curves, mouse_curves, coverage = load_tables()
    primary, _ = select_primary(pm, group)

    fig = plt.figure(figsize=(FULL_WIDTH, 132*MM), layout="constrained")
    axs = fig.subplot_mosaic(
        [["A", "B"], ["C", "D"]],
        width_ratios=[0.90, 1.25], height_ratios=[1.08, 1.0],
    )
    panel_mouse_effect(axs["A"], primary, group)
    panel_components(axs["B"], primary, group)
    panel_control_contrasts(axs["C"], pm, group)
    panel_timecourse(axs["D"], curves, mouse_curves)
    for letter, ax in axs.items():
        label_panel(ax, letter, x=-0.22 if letter in ("A", "C") else -0.16, y=1.06)

    base = save_publication(fig, "fig4_pulse_behaviour")
    write_source_data(base, pm, group, curves, mouse_curves, coverage)
    cov = coverage[coverage.analysis_set.eq(PRIMARY)]
    r = group_row(group, "positive_vs_negative")
    print(f"primary: {r.estimate:.6f} pp [{r.ci_low:.6f}, {r.ci_high:.6f}], "
          f"p={r.p_value:.6g}, Holm p={r.p_holm:.6g}, n={int(r.n_mice)} mice")
    print(f"coverage: {cov.n_signed_trials_in_support.sum()} trials, {cov.n_cells_supported.sum()} cells, "
          f"{cov.n_pre_onset_responses_retained_in_support.sum()} pre-onset responses, "
          f"{cov.n_unresponded_in_support.sum()} no-response trials")


if __name__ == "__main__":
    main()
