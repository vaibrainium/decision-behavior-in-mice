"""Assemble manuscript Figure 1: task, pulse schedule, and control behaviour.

The behavioral panels use scheduled-control trials.  Mouse-level summaries are
computed before group means and SEMs.  Every plotted value is exported beside
the figure so the legend can state exact denominators.

Usage
-----
python -m scripts.paper.fig1_task_behaviour
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle

from scripts.paper.style import (
    FULL_WIDTH,
    LEFT_COLOR,
    MM,
    NEUTRAL_COLOR,
    RIGHT_COLOR,
    RIG_COLOR,
    RIG_LABEL,
    RIG_MARKER,
    RIGS,
    TIMING_LABEL,
    apply_style,
    label_panel,
    load_trials,
    mouse_mean_sem,
    save_publication,
)

MIN_VIEWING_S = 0.3
DEADLINE_S = 5.0
MIN_TRIALS_PER_RT_CELL = 10
CORRECT_COLOR = "#009E73"
ERROR_COLOR = "#CC79A7"
COHERENCES = np.array([-100, -36, -18, -9, 0, 9, 18, 36, 100])
ABS_COHERENCES = np.array([0, 9, 18, 36, 100])


def _mean_sem(values):
    values = pd.Series(values).dropna()
    return values.mean(), values.std(ddof=1) / np.sqrt(len(values)), len(values)


def _coherence_axis(ax, absolute=False):
    if absolute:
        ax.set_xticks(ABS_COHERENCES)
        ax.set_xlim(-5, 105)
        ax.set_xlabel("Absolute coherence (%)")
    else:
        ax.set_xticks([-100, -36, 0, 36, 100])
        ax.set_xticks([-18, -9, 9, 18], minor=True)
        ax.set_xlim(-108, 108)
        ax.set_xlabel("Signed coherence (%)\n(leftward ←   → rightward)")


def panel_task(ax):
    """Compact vector schematic of the head-fixed choice task."""
    ax.set_axis_off()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)

    # Display and random-dot stimulus.
    ax.add_patch(Rectangle((0.35, 2.05), 2.65, 3.75, facecolor="#F2F2F2", edgecolor="0.2", lw=0.8))
    dots = np.array([
        [0.72, 2.55], [1.12, 3.08], [1.64, 2.52], [2.22, 3.28], [2.62, 2.68],
        [0.76, 4.12], [1.35, 4.55], [1.90, 3.82], [2.55, 4.65], [1.15, 5.18], [2.18, 5.28],
    ])
    ax.scatter(dots[:, 0], dots[:, 1], s=5, c="0.25", zorder=3)
    ax.add_patch(FancyArrowPatch((0.85, 3.55), (2.55, 3.55), arrowstyle="-|>", mutation_scale=8,
                                 lw=1.1, color=RIGHT_COLOR))
    ax.text(1.67, 6.15, "dynamic random-dot\nmotion", ha="center", va="center", fontsize=6.2)

    # Mouse head, eye, head post and lick ports.
    ax.add_patch(Ellipse((5.10, 3.67), 2.65, 2.15, facecolor="#D9D9D9", edgecolor="0.25", lw=0.8))
    ax.add_patch(Ellipse((4.35, 4.72), 0.72, 0.95, angle=25, facecolor="#D9D9D9", edgecolor="0.25", lw=0.7))
    ax.add_patch(Circle((4.45, 3.94), 0.105, color="0.1"))
    ax.add_patch(Polygon([[6.22, 3.80], [6.72, 3.57], [6.18, 3.34]], closed=True,
                         facecolor="#D9D9D9", edgecolor="0.25", lw=0.8))
    ax.add_patch(Rectangle((4.82, 5.02), 0.55, 1.30, facecolor="0.65", edgecolor="0.25", lw=0.7))
    ax.plot([5.10, 5.10], [6.32, 6.72], color="0.25", lw=1.1)
    ax.text(5.72, 6.22, "head post", ha="left", va="center", fontsize=5.8)
    ax.plot([6.69, 7.83], [3.40, 2.65], color=LEFT_COLOR, lw=1.4)
    ax.plot([6.69, 7.83], [3.54, 4.28], color=RIGHT_COLOR, lw=1.4)
    ax.add_patch(Circle((7.92, 2.58), 0.13, facecolor=LEFT_COLOR, edgecolor="none"))
    ax.add_patch(Circle((7.92, 4.35), 0.13, facecolor=RIGHT_COLOR, edgecolor="none"))
    ax.text(8.18, 2.58, "left port", va="center", fontsize=6.2)
    ax.text(8.18, 4.35, "right port", va="center", fontsize=6.2)

    # Minimal event sequence.  The 5-s line is explicitly analytical.
    y = 0.72
    ax.annotate("", xy=(9.4, y), xytext=(0.7, y), arrowprops=dict(arrowstyle="->", lw=0.7, color="0.25"))
    for x, label, align in [(1.0, "motion\nonset", "left"), (3.8, "0.3 s minimum\nviewing", "center"),
                            (8.6, "5 s analysis\ncutoff", "center")]:
        ax.plot([x, x], [y - 0.12, y + 0.12], color="0.25", lw=0.7)
        ax.text(x, y - 0.23, label, ha=align, va="top", fontsize=5.8)
    ax.add_patch(FancyArrowPatch((4.0, 1.50), (7.6, 1.50), arrowstyle="<->", mutation_scale=7,
                                 lw=0.7, color="0.35"))
    ax.text(5.8, 1.67, "left or right lick", ha="center", va="bottom", fontsize=5.8)
    ax.set_title("Head-fixed motion discrimination", loc="left", pad=2)


def make_schedule(data):
    pulsed = data[data["sched_pulse_type"] != 0].copy()
    pulsed["timing"] = pulsed["sched_pulse_type"].abs()
    pulsed["pulse_sign"] = np.sign(pulsed["sched_pulse_type"]).astype(int)
    schedule = (pulsed.groupby(["data_source", "timing", "pulse_sign"], as_index=False)
                .agg(n_trials=("subject_id", "size"), n_mice=("subject_id", "nunique"),
                     onset_median_s=("pulse_onset", "median"), onset_min_s=("pulse_onset", "min"),
                     onset_max_s=("pulse_onset", "max"), duration_median_s=("pulse_duration", "median")))
    return schedule


def panel_schedule(ax, schedule):
    ax.set_xlim(-0.03, 0.56)
    ax.set_ylim(-0.75, 2.8)
    ax.axvspan(0, MIN_VIEWING_S, color="0.93", zorder=0)
    ax.axvline(MIN_VIEWING_S, color="0.35", lw=0.8, ls=":")
    ax.text(MIN_VIEWING_S, 2.71, "responses allowed", ha="center", va="bottom", fontsize=5.8)
    y_by_rig = {"ucla": 1.85, "uw": 0.45}
    for rig in RIGS:
        y0 = y_by_rig[rig]
        ax.hlines(y0, 0, 0.53, color="0.45", lw=1.0)
        ax.text(-0.025, y0, RIG_LABEL[rig], color=RIG_COLOR[rig], fontweight="bold", ha="right", va="center")
        sub = schedule[schedule["data_source"] == rig]
        for timing in sorted(sub["timing"].unique()):
            # The two signs share the same nominal time window; use their pooled median.
            pair = sub[sub["timing"] == timing]
            onset = pair["onset_median_s"].median()
            duration = pair["duration_median_s"].median()
            for sign, offset, color in [(-1, -0.22, LEFT_COLOR), (1, 0.22, RIGHT_COLOR)]:
                row = pair[pair["pulse_sign"] == sign].iloc[0]
                ax.add_patch(Rectangle((onset, y0 + offset - 0.10), duration, 0.20,
                                       facecolor=color, edgecolor="none", alpha=0.92))
                ax.text(onset + duration / 2, y0 + offset + (0.16 if sign > 0 else -0.16),
                        TIMING_LABEL[int(timing)][0], color=color, ha="center",
                        va="bottom" if sign > 0 else "top", fontsize=5.3)
                # UCLA onset is jittered; show its observed onset span as a fine line.
                if rig == "ucla":
                    ax.hlines(y0 + offset, row["onset_min_s"], row["onset_max_s"], color=color, lw=0.45, alpha=0.7)
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_xlabel("Time from motion onset (s)")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title("Scheduled ±100% coherence pulses", loc="left", pad=2)
    handles = [Line2D([0], [0], color=RIGHT_COLOR, lw=4, label="Rightward pulse"),
               Line2D([0], [0], color=LEFT_COLOR, lw=4, label="Leftward pulse")]
    ax.legend(handles=handles, loc="lower right", ncols=1, handlelength=1.2, columnspacing=0.9)


def psychometric_table(ctrl):
    resp = ctrl[~ctrl["censored"]]
    mouse = (resp.groupby(["subject_id", "data_source", "signed_coherence"], as_index=False)
             .agg(n_trials=("choice", "size"), p_right=("choice", lambda x: (x == 1).mean())))
    group = (mouse.groupby("signed_coherence")["p_right"].apply(_mean_sem)
             .apply(pd.Series).reset_index())
    group.columns = ["signed_coherence", "mean", "sem", "n_mice"]
    totals = resp.groupby("signed_coherence").size().rename("n_trials").reset_index()
    return mouse, group.merge(totals, on="signed_coherence")


def panel_psychometric(ax, mouse, group):
    for _, sub in mouse.groupby("subject_id"):
        ax.plot(sub["signed_coherence"], sub["p_right"], color="0.72", lw=0.45, alpha=0.65, zorder=1)
    ax.errorbar(group["signed_coherence"], group["mean"], yerr=group["sem"], color="k", marker="o",
                ms=3.8, lw=1.15, elinewidth=0.8, capsize=0, zorder=3, label="mean ± SEM")
    ax.axhline(0.5, color="0.8", lw=0.6, ls=":")
    ax.axvline(0, color="0.88", lw=0.5)
    _coherence_axis(ax)
    ax.set_ylim(0, 1)
    ax.set_ylabel("P(rightward response)")
    ax.set_title("Direction reports track coherence", loc="left")
    ax.legend(loc="upper left", handlelength=1.3)


def rt_table(ctrl):
    resp = ctrl[~ctrl["censored"]].copy()
    resp["response_class"] = np.where(resp["abs_coherence"] == 0, "zero coherence",
                                      np.where(resp["outcome"] == 1, "correct", "error"))
    mouse = (resp.groupby(["subject_id", "data_source", "abs_coherence", "response_class"], as_index=False)
             .agg(n_trials=("reaction_time", "size"), median_rt_s=("reaction_time", "median")))
    mouse["eligible"] = mouse["n_trials"] >= MIN_TRIALS_PER_RT_CELL
    shown = mouse[mouse["eligible"]].copy()
    group = (shown.groupby(["abs_coherence", "response_class"])["median_rt_s"].apply(_mean_sem)
             .apply(pd.Series).reset_index())
    group.columns = ["abs_coherence", "response_class", "mean", "sem", "n_mice"]
    totals = (shown.groupby(["abs_coherence", "response_class"])["n_trials"].sum()
              .rename("n_trials_in_eligible_cells").reset_index())
    return mouse, group.merge(totals, on=["abs_coherence", "response_class"])


def panel_rt(ax, mouse, group):
    specs = [("correct", CORRECT_COLOR, "o", "-"), ("error", ERROR_COLOR, "s", "--")]
    for label, color, marker, linestyle in specs:
        sub = mouse[(mouse["response_class"] == label) & mouse["eligible"]]
        for _, m in sub.groupby("subject_id"):
            ax.plot(m["abs_coherence"], m["median_rt_s"], color=color, lw=0.4, alpha=0.24, ls=linestyle)
        g = group[group["response_class"] == label]
        ax.errorbar(g["abs_coherence"], g["mean"], yerr=g["sem"], color=color, marker=marker,
                    ls=linestyle, lw=1.15, ms=3.6, elinewidth=0.8, capsize=0, label=label.capitalize())
    z = mouse[(mouse["response_class"] == "zero coherence") & mouse["eligible"]]
    ax.scatter(z["abs_coherence"] + np.linspace(-1.4, 1.4, len(z)), z["median_rt_s"], s=9,
               facecolors="white", edgecolors=NEUTRAL_COLOR, linewidths=0.45, alpha=0.7, zorder=2)
    gz = group[group["response_class"] == "zero coherence"].iloc[0]
    ax.errorbar([0], [gz["mean"]], yerr=[gz["sem"]], color=NEUTRAL_COLOR, marker="D", ms=3.6,
                elinewidth=0.8, capsize=0, label="0% coherence")
    _coherence_axis(ax, absolute=True)
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Within-mouse median RT (s)")
    ax.set_title("Response time depends on outcome", loc="left")
    ax.legend(loc="upper right", handlelength=1.4)


def no_response_table(ctrl):
    mouse = (ctrl.groupby(["subject_id", "data_source", "signed_coherence"], as_index=False)
             .agg(n_trials=("censored", "size"), n_no_response=("censored", "sum"),
                  p_no_response=("censored", "mean")))
    group = (mouse.groupby("signed_coherence")["p_no_response"].apply(_mean_sem)
             .apply(pd.Series).reset_index())
    group.columns = ["signed_coherence", "mean", "sem", "n_mice"]
    totals = (ctrl.groupby("signed_coherence").agg(n_trials=("censored", "size"),
                                                    n_no_response=("censored", "sum")).reset_index())
    return mouse, group.merge(totals, on="signed_coherence")


def panel_no_response(ax, mouse, group):
    for rig in RIGS:
        sub = mouse[mouse["data_source"] == rig]
        for _, m in sub.groupby("subject_id"):
            ax.plot(m["signed_coherence"], m["p_no_response"], color=RIG_COLOR[rig], lw=0.45,
                    alpha=0.35, marker=RIG_MARKER[rig], ms=1.5)
    ax.errorbar(group["signed_coherence"], group["mean"], yerr=group["sem"], color="k", marker="o",
                lw=1.15, ms=3.8, elinewidth=0.8, capsize=0, zorder=3, label="mean ± SEM")
    _coherence_axis(ax)
    ax.set_ylim(bottom=0)
    ax.set_ylabel("P(no response by 5 s)")
    ax.set_title("No responses remain explicit", loc="left")
    rig_handles = [Line2D([0], [0], color=RIG_COLOR[r], marker=RIG_MARKER[r], lw=0.6,
                          ms=3, label=RIG_LABEL[r]) for r in RIGS]
    ax.legend(handles=rig_handles, loc="upper right", handlelength=1.2)


def overview_table(data, ctrl):
    rows = [{"scope": "all", "rig": "all", "n_mice": data["subject_id"].nunique(),
             "n_mouse_sessions": data.groupby(["subject_id", "idx_session"]).ngroups,
             "n_trials": len(data), "n_responded": (~data["censored"]).sum(),
             "n_no_response": data["censored"].sum(), "n_scheduled_controls": len(ctrl)}]
    for rig in RIGS:
        d = data[data["data_source"] == rig]
        c = ctrl[ctrl["data_source"] == rig]
        rows.append({"scope": "all", "rig": rig, "n_mice": d["subject_id"].nunique(),
                     "n_mouse_sessions": d.groupby(["subject_id", "idx_session"]).ngroups,
                     "n_trials": len(d), "n_responded": (~d["censored"]).sum(),
                     "n_no_response": d["censored"].sum(), "n_scheduled_controls": len(c)})
    return pd.DataFrame(rows)


def _write_sources(base: Path, tables):
    for suffix, table in tables.items():
        table.to_csv(base.parent / f"{base.name}_source_{suffix}.csv", index=False)


def main():
    apply_style()
    data = load_trials()
    ctrl = data[data["sched_pulse_type"] == 0].copy()
    schedule = make_schedule(data)
    psych_mouse, psych_group = psychometric_table(ctrl)
    rt_mouse, rt_group = rt_table(ctrl)
    nr_mouse, nr_group = no_response_table(ctrl)

    fig = plt.figure(figsize=(FULL_WIDTH, 124 * MM), layout="constrained")
    outer = fig.add_gridspec(2, 1, height_ratios=[0.88, 1.12])
    top = outer[0].subgridspec(1, 2, width_ratios=[0.95, 1.25], wspace=0.15)
    bottom = outer[1].subgridspec(1, 3, wspace=0.23)
    axes = {
        "A": fig.add_subplot(top[0, 0]), "B": fig.add_subplot(top[0, 1]),
        "C": fig.add_subplot(bottom[0, 0]), "D": fig.add_subplot(bottom[0, 1]),
        "E": fig.add_subplot(bottom[0, 2]),
    }
    panel_task(axes["A"])
    panel_schedule(axes["B"], schedule)
    panel_psychometric(axes["C"], psych_mouse, psych_group)
    panel_rt(axes["D"], rt_mouse, rt_group)
    panel_no_response(axes["E"], nr_mouse, nr_group)
    for letter, ax in axes.items():
        label_panel(ax, letter, x=-0.10 if letter in "AB" else -0.24, y=1.05)

    base = save_publication(fig, "fig1_task_behaviour")
    plt.close(fig)
    _write_sources(base, {
        "overview": overview_table(data, ctrl),
        "schedule": schedule,
        "psychometric_mouse": psych_mouse,
        "psychometric_group": psych_group,
        "rt_mouse": rt_mouse,
        "rt_group": rt_group,
        "no_response_mouse": nr_mouse,
        "no_response_group": nr_group,
    })
    print(overview_table(data, ctrl).to_string(index=False))
    print("\nRT display denominators (threshold >= 10 trials/mouse/cell):")
    print(rt_group.to_string(index=False))


if __name__ == "__main__":
    main()
