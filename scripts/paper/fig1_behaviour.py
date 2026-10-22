"""Figure 1: task, pulse schedule and behaviour on control trials (no scheduled pulse).

Layout follows the SfN 2025 poster (Figs 1, 2A, 3A).

Panels
  A  mouse/rig illustration (placeholder; drawn by hand from the poster, Fig 1)
  B  trial timeline (epochs only, not to scale)
  C  coherence time course of control and pulse trials (UW timing; UCLA timing in the caption)
  D  psychometric function, all mice
  E  chronometric functions (median RT, correct trials) per rig
  F  no-response-by-5 s rate per rig
  G  accuracy vs RT by |coherence|, both rigs
  H  RT distributions per rig

The mouse is the unit: per-mouse values are computed first, then mean +- SEM across mice. Prints every number the
caption uses.

Usage: python -m scripts.paper.fig1_behaviour
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle

from scripts.paper.style import (
    ABS_COHERENCES,
    FULL_WIDTH,
    MM,
    RIG_COLOR,
    RIG_LABEL,
    RIG_MARKER,
    RIGS,
    TIMING_LABEL,
    apply_style,
    coherence_colors,
    label_panel,
    load_trials,
    mouse_mean_sem,
    save,
)
from src.utils.pmf_utils import fit_psychometric_function

MIN_VIEWING_S = 0.3
DEADLINE_S = 5.0
RT_BIN_EDGES = np.array([0.3, 0.45, 0.6, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0, 4.0, 5.0])
MIN_TRIALS_PER_CELL = 10  # per mouse, for a per-mouse accuracy or RT value in a bin
MIN_MICE_PER_CELL = 3
MIN_VIEWING_COLOR = "#C0392B"
EXAMPLE_BASE_COHERENCE = 18


def per_mouse(df, value, by):
    """Table mice x `by` of a per-mouse statistic (value: function of a trial group)."""
    return df.groupby(["subject_id", by]).apply(value, include_groups=False).unstack(by)


def mean_band(ax, x, table, color, marker=None, label=None, lw=1.0):
    for _, row in table.iterrows():
        ax.plot(x, row.values, color=color, lw=0.4, alpha=0.3)
    mean, sem, _ = mouse_mean_sem(table)
    ax.errorbar(x, mean.values, yerr=sem.values, color=color, marker=marker, lw=lw, capsize=0, elinewidth=0.8,
                label=label)
    return mean, sem


def coherence_axis(ax):
    ax.set_xticks([-100, -36, 0, 36, 100])
    ax.set_xticks([-18, -9, 9, 18], minor=True)
    ax.set_xlim(-108, 108)
    ax.set_xlabel("Motion coherence (%)\n(+ rightward)")


def panel_timeline(ax):
    """Epoch sequence of one trial, not to scale (durations differ by rig; see caption)."""
    h = 0.55

    def box(x0, x1, y, color, text, text_color="white"):
        ax.add_patch(Rectangle((x0, y - h / 2), x1 - x0, h, color=color, lw=0))
        ax.text((x0 + x1) / 2, y, text, ha="center", va="center", fontsize=6, color=text_color)

    box(0, 2.2, 1.5, "0.55", "Withhold\nlicking")
    box(2.2, 6.4, 1.5, "0.15", "Motion stimulus")
    ax.add_patch(Rectangle((2.2, 1.5 - h / 2 - 0.2), 0.9, 0.14, color=MIN_VIEWING_COLOR, lw=0))
    ax.text(2.65, 1.5 - h / 2 - 0.3, f"minimum viewing {MIN_VIEWING_S:g} s", ha="left", va="top", fontsize=5.5,
            color=MIN_VIEWING_COLOR)
    ax.annotate("lick left\nor right", xy=(6.4, 1.5 + h / 2), xytext=(6.4, 2.35), ha="center", fontsize=5.5,
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color="k", mutation_scale=6))
    for y, outcome, label, color in ((2.55, "correct", "Reward", "#6A3D9A"), (0.45, "error", "Time-out", "0.35")):
        ax.add_patch(FancyArrowPatch((6.45, 1.5), (7.1, y), arrowstyle="-", lw=0.6, color="k"))
        ax.text(6.85, (y + 1.5) / 2 + (0.15 if y > 1.5 else -0.15), outcome, fontsize=5.5, ha="left", va="center",
                style="italic")
        box(7.1, 8.9, y, color, label)
        box(8.9, 10.0, y, "0.85", "ITI", text_color="k")
    ax.set_xlim(-0.1, 10.1)
    ax.set_ylim(-0.1, 3.0)
    ax.set_axis_off()
    ax.set_title("Trial structure (not to scale)", loc="left")


def panel_pulse_traces(ax, data):
    """Programmed coherence over time for a control trial and the six pulse conditions (UW timing, as on the poster)."""
    pulsed = data[data["sched_pulse_type"] != 0].copy()
    pulsed["timing"] = pulsed["sched_pulse_type"].abs()
    for rig in RIGS:
        for timing in (1, 2, 3):
            sub = pulsed[(pulsed["data_source"] == rig) & (pulsed["timing"] == timing)]
            if sub.empty:
                continue
            onset = sub["pulse_onset"] * 1000
            print(f"[C] {RIG_LABEL[rig]} {TIMING_LABEL[timing]}: onset {onset.mean():.0f} ms (SD {onset.std():.0f}), "
                  f"duration {sub['pulse_duration'].median() * 1000:.0f} ms, scheduled pulse trials {len(sub)} "
                  f"(incl. no-response), per mouse {sub.groupby('subject_id').size().min()}-"
                  f"{sub.groupby('subject_id').size().max()}")

    uw = pulsed[pulsed["data_source"] == "uw"]
    timing = {t: (uw.loc[uw["timing"] == t, "pulse_onset"].median() * 1000,
                  uw.loc[uw["timing"] == t, "pulse_duration"].median() * 1000) for t in (1, 2, 3)}
    t = np.linspace(0, 600, 1201)
    rows = [("Control", None, 0)] + [(TIMING_LABEL[k], k, s) for k in (1, 2, 3) for s in (1, -1)]
    spacing = 2.4
    for i, (label, k, sign) in enumerate(rows):
        y0 = -i * spacing
        c = np.full_like(t, EXAMPLE_BASE_COHERENCE, dtype=float)
        if k is not None:
            on, dur = timing[k]
            c[(t >= on) & (t < on + dur)] = 100 * sign
        ax.axhline(y0, color="0.85", lw=0.3, zorder=0)
        ax.plot(t, y0 + c / 100, color="0.5" if k is None else "k", lw=0.8)
        if sign >= 0:
            ax.text(-12, y0 - (spacing / 2 if k else -0.2), label, ha="right", va="center", fontsize=6)
    top = 1.9
    ax.add_patch(Rectangle((0, top), MIN_VIEWING_S * 1000, 1.0, color=MIN_VIEWING_COLOR, lw=0))
    ax.text(MIN_VIEWING_S * 500, top + 0.5, "minimum viewing", ha="center", va="center", fontsize=5.5,
            color="white")
    # scale bar: 100% coherence
    ax.plot([615, 615], [0, 1], color="k", lw=0.8, clip_on=False)
    ax.text(625, 0.5, "100%", fontsize=5.5, va="center", ha="left", clip_on=False)
    ax.set_ylim(-(len(rows) - 1) * spacing - 1.3, top + 1.1)
    ax.set_xlim(0, 600)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Time from motion onset (ms)")
    ax.set_title("Coherence on control and pulse trials", loc="left")


def panel_psychometric(ax, ctrl):
    resp = ctrl[~ctrl["censored"]]
    table = per_mouse(resp, lambda g: (g["choice"] == 1).mean(), "signed_coherence")
    mean, sem, _ = mouse_mean_sem(table)
    x = table.columns.to_numpy(float)
    ax.errorbar(x, mean.values, yerr=sem.values, fmt="o", color="k", ms=4, elinewidth=0.8, capsize=0, zorder=3)
    fit = fit_psychometric_function(x, mean.values, trial_counts=None, model_type="logit_4")
    xx = np.linspace(-100, 100, 200)
    ax.plot(xx, fit.predict(xx), color="k", lw=1.2)
    n_sessions = resp.groupby(["subject_id", "idx_session"]).ngroups
    ax.text(0.97, 0.04, f"{table.shape[0]} mice, {n_sessions} sessions\n{len(resp):,} control trials",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6)
    print(f"[D] all mice: P(right) at -100/+100% = {mean.iloc[0]:.2f}/{mean.iloc[-1]:.2f} (mean of mice); "
          f"{len(resp)} responded control trials, {n_sessions} sessions; fit {fit.coefs_}")
    coherence_axis(ax)
    ax.set_ylim(0, 1)
    ax.set_ylabel("P(rightward choice)")
    ax.set_title("Psychometric function", loc="left")


def panel_chronometric(ax, ctrl):
    resp = ctrl[~ctrl["censored"]]
    # correct trials; at 0% coherence there is no correct answer, so all responded trials are used
    use = resp[(resp["outcome"] == 1) | (resp["signed_coherence"] == 0)]
    for rig in RIGS:
        sub = use[use["data_source"] == rig]
        table = per_mouse(sub, lambda g: g["reaction_time"].median() if len(g) >= MIN_TRIALS_PER_CELL else np.nan,
                          "signed_coherence")
        x = table.columns.to_numpy(float)
        mean, _ = mean_band(ax, x, table, RIG_COLOR[rig], marker=RIG_MARKER[rig],
                            label=f"{RIG_LABEL[rig]} ({table.shape[0]} mice)")
        print(f"[E] {RIG_LABEL[rig]}: median RT (mean of mice) at 0% = {mean.loc[0]:.2f} s, at -/+100% = "
              f"{mean.loc[-100]:.2f}/{mean.loc[100]:.2f} s")
    coherence_axis(ax)
    ax.set_ylabel("Median RT, correct trials (s)")
    ax.set_ylim(bottom=0)
    ax.legend(loc="lower left", handlelength=1)


def panel_no_response(ax, ctrl):
    for rig in RIGS:
        sub = ctrl[ctrl["data_source"] == rig]
        table = per_mouse(sub, lambda g: g["censored"].mean(), "signed_coherence")
        x = table.columns.to_numpy(float)
        mean, _ = mean_band(ax, x, table, RIG_COLOR[rig], marker=RIG_MARKER[rig])
        overall = sub.groupby("subject_id")["censored"].mean()
        print(f"[F] {RIG_LABEL[rig]}: no response by 5 s, mean of mice {overall.mean():.3f} "
              f"(range {overall.min():.3f}-{overall.max():.3f}); at 0% {mean.loc[0]:.3f}, at -/+100% "
              f"{mean.loc[-100]:.3f}/{mean.loc[100]:.3f}")
    coherence_axis(ax)
    ax.set_ylabel("P(no response by 5 s)")
    ax.set_ylim(bottom=0)


def panel_accuracy_vs_rt(ax, ctrl):
    resp = ctrl[~ctrl["censored"] & (ctrl["abs_coherence"] > 0)].copy()
    resp["rt_bin"] = pd.cut(resp["reaction_time"], RT_BIN_EDGES, right=False, labels=False)
    centers = resp.groupby("rt_bin")["reaction_time"].median()
    colors = coherence_colors()
    for coh in ABS_COHERENCES[1:]:
        sub = resp[resp["abs_coherence"] == coh]
        table = per_mouse(sub, lambda g: g["outcome"].mean() if len(g) >= MIN_TRIALS_PER_CELL else np.nan, "rt_bin")
        mean, sem, n = mouse_mean_sem(table)
        keep = n >= MIN_MICE_PER_CELL
        x = centers.loc[table.columns].to_numpy()
        ax.errorbar(x[keep], mean[keep], yerr=sem[keep], color=colors[coh], marker="o", ms=2.5, lw=1.0,
                    elinewidth=0.7, capsize=0, label=f"{coh}%")
    fast = resp["reaction_time"] < 0.6
    acc_fast = resp[fast & (resp["abs_coherence"] == 100)].groupby("subject_id")["outcome"].mean()
    acc_slow = resp[~fast & (resp["abs_coherence"] == 100)].groupby("subject_id")["outcome"].mean()
    print(f"[G] accuracy at 100% coherence, RT < 0.6 s vs >= 0.6 s (mean of mice): {acc_fast.mean():.2f} vs "
          f"{acc_slow.mean():.2f}; bins kept where >= {MIN_MICE_PER_CELL} mice have >= {MIN_TRIALS_PER_CELL} trials")
    ax.axhline(0.5, color="0.6", lw=0.5, ls=":")
    ax.set_xlim(0, 5)
    ax.set_ylim(0.4, 1.0)
    ax.set_xlabel("Reaction time (s)")
    ax.set_ylabel("P(correct)")
    ax.legend(title="|coherence|", ncols=2, loc="lower right", title_fontsize=6.5, columnspacing=0.8,
              handlelength=1.2)


def panel_rt_distribution(ax, ctrl):
    edges = np.arange(MIN_VIEWING_S, DEADLINE_S + 1e-9, 0.05)
    for rig in RIGS:
        sub = ctrl[(ctrl["data_source"] == rig) & ~ctrl["censored"]]
        dens = np.stack([np.histogram(g["reaction_time"], edges, density=True)[0]
                         for _, g in sub.groupby("subject_id")])
        ax.stairs(dens.mean(axis=0), edges, color=RIG_COLOR[rig], lw=0.9, label=RIG_LABEL[rig])
        fast = sub.groupby("subject_id")["reaction_time"].apply(lambda r: (r < 0.6).mean())
        print(f"[H] {RIG_LABEL[rig]}: fraction of responses < 0.6 s, mean of mice {fast.mean():.3f} "
              f"(range {fast.min():.3f}-{fast.max():.3f})")
    ax.set_xlim(0, DEADLINE_S)
    ax.set_xlabel("Reaction time (s)")
    ax.set_ylabel("Density (1/s)")
    ax.legend(loc="upper right", handlelength=1)


def print_counts(data, ctrl):
    for rig in RIGS:
        sub = data[data["data_source"] == rig]
        per = sub.groupby("subject_id").agg(sessions=("idx_session", "nunique"),
                                            responded=("censored", lambda c: (~c).sum()), censored=("censored", "sum"))
        print(f"[counts] {RIG_LABEL[rig]}: {len(per)} mice, {per['sessions'].sum()} sessions "
              f"({per['sessions'].min()}-{per['sessions'].max()} per mouse), {per['responded'].sum()} responded + "
              f"{per['censored'].sum()} no-response trials (responded per mouse {per['responded'].min()}-"
              f"{per['responded'].max()}); scheduled controls {(ctrl['data_source'] == rig).sum()}")
        resp = sub[~sub["censored"]]
        for col in ("fixation_duration", "reinforcement_duration", "intertrial_delay"):
            q = resp.groupby("outcome")[col].quantile([0.05, 0.5, 0.95]).unstack().round(2)
            print(f"[B] {RIG_LABEL[rig]} {col} by outcome (5/50/95%): {q.to_dict('index')}")


def main():
    apply_style()
    data = load_trials()
    ctrl = data[data["sched_pulse_type"] == 0]
    print_counts(data, ctrl)

    fig = plt.figure(figsize=(FULL_WIDTH, 165 * MM), layout="constrained")
    rows = fig.subfigures(3, 1, height_ratios=[1.0, 1.1, 1.0])
    axs = {}
    axs.update(rows[0].subplot_mosaic([["A", "B", "C"]], width_ratios=[0.55, 1.6, 1.25]))
    axs.update(rows[1].subplot_mosaic([["D", "E", "F"]], width_ratios=[1.3, 1, 1]))
    axs.update(rows[2].subplot_mosaic([["G", "H"]], width_ratios=[2, 1]))
    ax = axs["A"]
    ax.set_axis_off()
    ax.text(0.5, 0.5, "Mouse / rig\nillustration\n(poster Fig 1)", ha="center", va="center", color="0.5",
            fontsize=6.5, transform=ax.transAxes)
    panel_timeline(axs["B"])
    panel_pulse_traces(axs["C"], data)
    panel_psychometric(axs["D"], ctrl)
    panel_chronometric(axs["E"], ctrl)
    panel_no_response(axs["F"], ctrl)
    panel_accuracy_vs_rt(axs["G"], ctrl)
    panel_rt_distribution(axs["H"], ctrl)
    for letter, ax in axs.items():
        label_panel(ax, letter, x={"A": -0.1, "B": -0.08, "C": -0.22, "D": -0.22, "G": -0.1}.get(letter, -0.3))
    save(fig, "fig1_behaviour")


if __name__ == "__main__":
    main()
