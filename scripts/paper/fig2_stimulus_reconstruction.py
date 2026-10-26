"""Assemble manuscript Figure 2: stimulus reconstruction and replay audit.

This figure deliberately uses trials, seeds, or trial-by-convention replays as
its units; it contains no across-mouse uncertainty.  Numerical source tables
are exported beside the vector and raster artwork.

Usage: python -m scripts.paper.fig2_stimulus_reconstruction
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle
from scipy.stats import t as student_t

from scripts.compute_motion_energy_full import convert_to_frame_units
from scripts.paper.style import (
    FULL_WIDTH,
    LEFT_COLOR,
    MM,
    NEUTRAL_COLOR,
    PROCESSED,
    RIGHT_COLOR,
    RIG_COLOR,
    RIG_LABEL,
    RIG_MARKER,
    RIGS,
    apply_style,
    label_panel,
    load_trials,
    save_publication,
)

FRAME_S = 1 / 60
MEAN_WINDOW = slice(20, 300)  # 0.33--5 s, after the onset transient
AUDIT_DIR = PROCESSED / "pulse_followup" / "20261023T191030Z_fa8de8b" / "stimulus"
COHERENCES = np.array([-100, -36, -18, -9, 0, 9, 18, 36, 100])


def load_motion_energy():
    archive = np.load(PROCESSED / "motion_energy_mouse" / "me_calibrated.npz")
    trials = convert_to_frame_units(load_trials().query("~censored"))
    row = {code: i for i, code in enumerate(archive["agg_code"])}
    trials = trials[trials["agg_code"].isin(row)].reset_index(drop=True)
    me = archive["global"][[row[code] for code in trials["agg_code"]]].astype(float)
    return trials, me


def panel_reconstruction(ax):
    ax.set_axis_off()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    boxes = [(1.0, 4.15, "logged seed + task parameters"),
             (1.0, 2.55, "rendered dot frames (60 Hz)"),
             (1.0, 0.95, "causal filter  →  spatial mean\nrig calibration  →  model input")]
    for x, y, text in boxes:
        ax.add_patch(Rectangle((x, y), 8.0, 0.95, facecolor="0.95", edgecolor="0.3", lw=0.7))
        ax.text(x + 4.0, y + 0.475, text, ha="center", va="center", fontsize=5.8)
    for y0, y1 in [(4.15, 3.50), (2.55, 1.90)]:
        ax.add_patch(FancyArrowPatch((5.0, y0), (5.0, y1), arrowstyle="-|>", mutation_scale=7,
                                     color="0.35", lw=0.7))
    # Small visual cues that make the boxes more than a text flowchart.
    rng = np.random.default_rng(2)
    xy = rng.uniform([6.85, 2.70], [8.60, 3.35], size=(12, 2))
    ax.scatter(xy[:, 0], xy[:, 1], s=2.7, color="0.25", zorder=3)
    ax.plot([1.40, 2.25], [1.18, 1.66], color=RIGHT_COLOR, lw=0.9)
    ax.plot([1.40, 2.25], [1.66, 1.18], color=LEFT_COLOR, lw=0.9)
    ax.text(5.0, 5.45, "Model-derived history; not a frame-perfect display record",
            ha="center", va="center", fontsize=5.5, color="0.3")
    ax.set_title("Reconstruction pipeline", loc="left")


def calibration_table(trials, me):
    rows = []
    trial_rows = []
    for rig in RIGS:
        mask = (trials["data_source"].to_numpy() == rig) & (trials["sched_pulse_type"].to_numpy() == 0)
        values = me[mask, MEAN_WINDOW].mean(axis=1)
        sub = trials.loc[mask, ["agg_code", "data_source", "signed_coherence"]].copy()
        sub["mean_me_pct_equiv"] = values
        trial_rows.append(sub)
        for coh, group in sub.groupby("signed_coherence"):
            rows.append({"rig": rig, "signed_coherence": coh, "n_trials": len(group),
                         "mean": group["mean_me_pct_equiv"].mean(),
                         "sd": group["mean_me_pct_equiv"].std(ddof=1)})
    return pd.concat(trial_rows, ignore_index=True), pd.DataFrame(rows)


def panel_calibration(ax, group):
    for rig in RIGS:
        g = group[group["rig"] == rig]
        ax.errorbar(g["signed_coherence"], g["mean"], yerr=g["sd"], color=RIG_COLOR[rig],
                    marker=RIG_MARKER[rig], mfc="white" if rig == "uw" else RIG_COLOR[rig],
                    ms=3.8, mew=0.8, lw=0.9, elinewidth=0.6, capsize=0, label=RIG_LABEL[rig])
    ax.plot([-105, 105], [-105, 105], color="0.55", lw=0.6, ls=":", label="identity")
    ax.set_xlim(-108, 108)
    ax.set_ylim(-120, 120)
    ax.set_xticks([-100, -36, 0, 36, 100])
    ax.set_xlabel("Programmed coherence (%)")
    ax.set_ylabel("Mean motion energy\n(% coherence equivalent)")
    ax.set_title("Calibration preserves signed coherence", loc="left")
    ax.legend(loc="upper left", handlelength=1.2)


def panel_seed_variation(ax, trial_values):
    rng = np.random.default_rng(20261026)
    positions = [0, 1]
    handles = []
    for pos, rig in zip(positions, RIGS):
        values = trial_values[(trial_values["data_source"] == rig) &
                              (trial_values["signed_coherence"] == 0)]["mean_me_pct_equiv"].to_numpy()
        violin = ax.violinplot(values, positions=[pos], widths=0.72, showextrema=False)
        for body in violin["bodies"]:
            body.set_facecolor(RIG_COLOR[rig]); body.set_edgecolor("none"); body.set_alpha(0.22)
        jitter = rng.uniform(-0.24, 0.24, len(values))
        ax.scatter(pos + jitter, values, s=3, color=RIG_COLOR[rig], alpha=0.24, linewidths=0)
        mean, sd = values.mean(), values.std(ddof=1)
        ax.errorbar([pos], [mean], yerr=[sd], fmt=RIG_MARKER[rig], color=RIG_COLOR[rig],
                    mfc="white", mew=0.8, ms=4, elinewidth=0.9, capsize=2, zorder=5)
        handles.append(Line2D([0], [0], color=RIG_COLOR[rig], marker=RIG_MARKER[rig], mfc="white",
                              lw=0, label=f"{RIG_LABEL[rig]} (n={len(values):,})"))
    ax.axhline(0, color="0.55", lw=0.6, ls=":")
    ax.set_xticks(positions, ["UCLA", "UW"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylabel("Mean motion energy\n0.33–5 s (% coh. equiv.)")
    ax.set_title("Seed variation at 0%", loc="left")
    ax.legend(handles=handles, loc="upper right", handlelength=0.8)


def paired_trace_table():
    archive = np.load(AUDIT_DIR / "traces.npz")
    metrics = pd.read_csv(AUDIT_DIR / "per_trial_replay_metrics.csv")
    index = pd.DataFrame({"trace_index": np.arange(len(archive["trial_id"])),
                          "trial_id": archive["trial_id"], "variant": archive["variant"]})
    meta = index.merge(metrics[["trial_id", "variant", "rig", "pulse_sign", "replay_onset_index",
                                "n_pulse_frames"]], on=["trial_id", "variant"], validate="one_to_one")
    meta = meta[meta["variant"] == "replay"].copy()
    rel_frames = np.arange(-12, 73)
    rows = []
    for rig in RIGS:
        traces = []
        for row in meta[meta["rig"] == rig].itertuples():
            idx = row.replay_onset_index + rel_frames
            trace = np.full(len(rel_frames), np.nan)
            valid = (idx >= 0) & (idx < archive["diff_global_pct"].shape[1])
            trace[valid] = archive["diff_global_pct"][row.trace_index, idx[valid]] * row.pulse_sign
            traces.append(trace)
        traces = np.asarray(traces)
        n = np.sum(np.isfinite(traces), axis=0)
        mean = np.nanmean(traces, axis=0)
        sd = np.nanstd(traces, axis=0, ddof=1)
        sem = sd / np.sqrt(n)
        crit = student_t.ppf(0.975, n - 1)
        rows.extend({"rig": rig, "time_from_pulse_s": frame * FRAME_S, "n_trials": int(nn),
                     "mean": m, "ci_low": m - c * s, "ci_high": m + c * s}
                    for frame, nn, m, s, c in zip(rel_frames, n, mean, sem, crit))
    return pd.DataFrame(rows), meta


def panel_paired_trace(ax, trace_group, meta):
    for rig in RIGS:
        g = trace_group[trace_group["rig"] == rig]
        ax.fill_between(g["time_from_pulse_s"].to_numpy(), g["ci_low"].to_numpy(),
                        g["ci_high"].to_numpy(), color=RIG_COLOR[rig], alpha=0.18, lw=0)
        n = meta[meta["rig"] == rig]["trial_id"].nunique()
        ax.plot(g["time_from_pulse_s"], g["mean"], color=RIG_COLOR[rig], lw=1.15,
                marker=RIG_MARKER[rig], markevery=12, ms=2.5, label=f"{RIG_LABEL[rig]} (n={n})")
    ax.axvspan(0, 4 * FRAME_S, color="0.85", alpha=0.55, lw=0, label="pulse window")
    ax.axvline(0, color="0.35", lw=0.6, ls=":")
    ax.axhline(0, color="0.55", lw=0.6, ls=":")
    ax.set_xlim(-0.2, 1.2)
    ax.set_xlabel("Time from pulse onset (s)")
    ax.set_ylabel("Pulse − physical omission\n(% coh. equiv.; sign aligned)")
    ax.set_title("Paired replays isolate the pulse-associated input", loc="left")
    ax.legend(loc="upper right", handlelength=1.2)


def alternative_table():
    summary = json.loads((AUDIT_DIR / "summary.json").read_text())
    labels = [
        ("ucla__replay", "stored replay"),
        ("ucla__ucla_nofreeze", "no freeze"),
        ("ucla__ucla_pass_R150_L95", "150-Hz pass\nemulation"),
        ("ucla__ucla_pass_R190_L95", "190-Hz pass\nemulation"),
    ]
    rows = []
    for key, label in labels:
        entry = summary["pulse_energy"][key]
        estimate = entry["signed_sum_0_333ms_per_pct_delta"]
        rows.append({"key": key, "label": label, "n_trials": estimate["n"], "mean": estimate["mean"],
                     "ci_low": estimate["ci_low"], "ci_high": estimate["ci_high"],
                     "ratio_to_replay": entry["ratio_to_replay"]})
    return pd.DataFrame(rows)


def panel_alternatives(ax, table):
    y = np.arange(len(table))[::-1]
    colors = [NEUTRAL_COLOR, "#0072B2", "#E69F00", "#D55E00"]
    for yi, row, color in zip(y, table.itertuples(), colors):
        ax.errorbar(row.mean, yi, xerr=[[row.mean - row.ci_low], [row.ci_high - row.mean]],
                    fmt="o", color=color, ms=4, elinewidth=1.0, capsize=2)
        ax.text(row.ci_high + 0.08, yi, f"×{row.ratio_to_replay:.2f}", ha="left", va="center",
                fontsize=5.8, color=color)
    ax.axvline(table.iloc[0]["mean"], color="0.55", lw=0.6, ls=":")
    ax.set_yticks(y, table["label"])
    ax.set_ylim(-0.65, len(table) - 0.35)
    ax.set_xlim(1.5, 3.75)
    ax.set_xlabel("Pulse energy per 1% programmed change\n(% coherence-equivalent frames, 0–333 ms)")
    ax.set_title("UCLA replay alternatives", loc="left")
    ax.text(0.98, 0.03, "Alternatives are labeled assumptions,\nnot acquisition-setting estimates",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=5.5, color="0.35")


def _write_sources(base: Path, tables):
    for suffix, table in tables.items():
        table.to_csv(base.parent / f"{base.name}_source_{suffix}.csv", index=False)


def main():
    apply_style()
    trials, me = load_motion_energy()
    calibration_trials, calibration_group = calibration_table(trials, me)
    trace_group, trace_meta = paired_trace_table()
    alternatives = alternative_table()

    fig = plt.figure(figsize=(FULL_WIDTH, 128 * MM), layout="constrained")
    outer = fig.add_gridspec(2, 1, height_ratios=[0.90, 1.10])
    top = outer[0].subgridspec(1, 3, width_ratios=[1.05, 1.0, 0.92], wspace=0.20)
    bottom = outer[1].subgridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.20)
    axes = {"A": fig.add_subplot(top[0, 0]), "B": fig.add_subplot(top[0, 1]),
            "C": fig.add_subplot(top[0, 2]), "D": fig.add_subplot(bottom[0, 0]),
            "E": fig.add_subplot(bottom[0, 1])}
    panel_reconstruction(axes["A"])
    panel_calibration(axes["B"], calibration_group)
    panel_seed_variation(axes["C"], calibration_trials)
    panel_paired_trace(axes["D"], trace_group, trace_meta)
    panel_alternatives(axes["E"], alternatives)
    for letter, ax in axes.items():
        label_panel(ax, letter, x=-0.10 if letter == "A" else -0.25, y=1.05)

    base = save_publication(fig, "fig2_stimulus_reconstruction")
    plt.close(fig)
    _write_sources(base, {"calibration_trials": calibration_trials,
                          "calibration_group": calibration_group,
                          "paired_trace_group": trace_group,
                          "paired_trace_trials": trace_meta,
                          "ucla_alternatives": alternatives})
    print(calibration_group.groupby("rig")["n_trials"].sum().to_string())
    print(alternatives.to_string(index=False))


if __name__ == "__main__":
    main()
