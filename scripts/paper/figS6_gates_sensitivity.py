"""Build Supplementary Figure S6 from frozen gate and calibration outputs.

The figure is deliberately diagnostic rather than inferential.  Every plotted
summary is also written to an adjacent CSV so denominators can be audited
without reading values from the artwork.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.paper.style import (
    FULL_WIDTH,
    NEUTRAL_COLOR,
    apply_style,
    label_panel,
    save_publication,
)


DATA = Path("/mnt/data/processed/ddm")
PRIMARY = "Accumulator"
SECONDARY = "Leak + urgency"
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
LIGHT = "#D9D9D9"


def _load_pickle(path: Path):
    with path.open("rb") as stream:
        return pickle.load(stream)


def gate_rows(directory: Path, revision: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    departures, coverage = [], []
    for filename, model in (
        ("results_primary_gate.pkl", PRIMARY),
        ("results_secondary_gate.pkl", SECONDARY),
    ):
        result = _load_pickle(directory / filename)
        summary = result["gate_departure"]
        b0 = summary["b0"]
        departures.append(
            {
                "revision": revision,
                "model": model,
                "observed_minus_predicted_logit": b0["mean"],
                "ci_low": b0["lo"],
                "ci_high": b0["hi"],
                "predicted_logit_effect": summary["predicted_effect"],
                "gate_pass": bool(result["gate_pass"]),
                "mice": 10,
                "interval": "95% posterior interval",
            }
        )
        distributions = result["gate_distributions"]
        rt_columns = [f"rt_q{q}_inside" for q in (10, 30, 50, 70, 90)]
        rt_inside = int(distributions[rt_columns].to_numpy().sum())
        censor_inside = int(distributions["censored_inside"].sum())
        coverage.extend(
            [
                {
                    "revision": revision,
                    "model": model,
                    "outcome": "RT quantiles",
                    "inside": rt_inside,
                    "total": int(distributions[rt_columns].size),
                    "fraction_inside": rt_inside / distributions[rt_columns].size,
                    "required_fraction": 0.8,
                },
                {
                    "revision": revision,
                    "model": model,
                    "outcome": "No response",
                    "inside": censor_inside,
                    "total": len(distributions),
                    "fraction_inside": censor_inside / len(distributions),
                    "required_fraction": 0.8,
                },
            ]
        )
    return pd.DataFrame(departures), pd.DataFrame(coverage)


def strategy_rows() -> pd.DataFrame:
    raw = pd.read_csv(DATA / "primacy" / "strategy_power.csv")
    rows = []
    for generator, label, expected in (
        ("extrema", "Rapid forgetting", "a"),
        ("primary", "Accumulator", "b"),
    ):
        group = raw.loc[raw.generator.eq(generator)]
        correct = int(group.pulse_gain_favoured.eq(expected).sum())
        rows.append(
            {
                "generator": label,
                "correct_verdicts": correct,
                "not_correct": len(group) - correct,
                "total_datasets": len(group),
                "fraction_correct": correct / len(group),
                "decision_rule": "frozen pulse-gain strategy rule",
            }
        )
    return pd.DataFrame(rows)


def calibration_rows() -> pd.DataFrame:
    frames = [
        pd.read_csv(DATA / "primacy_calibration" / f"calibration_summary_levels{suffix}.csv")
        for suffix in ("0", "0.1", "0.2", "0.4")
    ]
    raw = pd.concat(frames, ignore_index=True)
    rows = []
    for level, group in raw.groupby("level", sort=True):
        rows.append(
            {
                "decay_percent_over_0.5_s": int(round(100 * level)),
                "gate_passes": int(group.gate_pass.sum()),
                "primary_primacy_detections": int(group.primary_primacy.sum()),
                "total_datasets": len(group),
                "gate_pass_fraction": float(group.gate_pass.mean()),
                "detection_fraction": float(group.primary_primacy.mean()),
            }
        )
    return pd.DataFrame(rows)


def plot_departure(ax, frame: pd.DataFrame, title: str, show_legend: bool = True):
    colors = [BLUE, ORANGE]
    for y, (_, row), color in zip((1, 0), frame.iterrows(), colors):
        ax.errorbar(
            row.observed_minus_predicted_logit,
            y,
            xerr=[[row.observed_minus_predicted_logit - row.ci_low],
                  [row.ci_high - row.observed_minus_predicted_logit]],
            fmt="o", color=color, capsize=2, label="Observed − predicted" if y == 1 else None,
        )
        ax.plot(row.predicted_logit_effect, y, marker="D", ms=3.2, color="white",
                markeredgecolor=color, label="Predicted pulse effect" if y == 1 else None)
    ax.axvline(0, color="0.45", lw=0.7, ls=":")
    ax.set_yticks([1, 0], frame.model.tolist())
    ax.set_xlim(-0.02, 0.46)
    ax.set_xlabel("Choice departure (logit)")
    ax.set_title(title, loc="left")
    if show_legend:
        ax.legend(loc="center left", bbox_to_anchor=(0.43, 0.52), fontsize=5.5, handletextpad=0.4)


def plot_coverage(ax, frame: pd.DataFrame, title: str, compact: bool = False):
    models = [PRIMARY, SECONDARY]
    outcomes = ["RT quantiles", "No response"]
    if compact:
        ordered = frame.set_index(["model", "outcome"]).loc[
            [(model, outcome) for model in models for outcome in outcomes]
        ].reset_index()
        y = np.arange(len(ordered))[::-1]
        colors = [GREEN if outcome == "RT quantiles" else PURPLE for outcome in ordered.outcome]
        markers = ["o" if model == PRIMARY else "s" for model in ordered.model]
        for ypos, (_, row), color, marker in zip(y, ordered.iterrows(), colors, markers):
            ax.plot(row.fraction_inside, ypos, marker=marker, color=color, ms=4.2)
            ax.text(row.fraction_inside + 0.035, ypos,
                    f"{int(row.inside)}/{int(row.total)}", va="center", fontsize=5.6)
        ax.axvline(0.8, color=NEUTRAL_COLOR, ls="--", lw=0.8)
        ax.set_yticks(y, ["Acc. RT", "Acc. no resp.", "L+U RT", "L+U no resp."])
        ax.set_xlim(0.42, 1.08)
        ax.set_xlabel("Fraction inside")
        ax.set_title(title, loc="left")
        return
    x = np.arange(len(models))
    width = 0.32
    for offset, outcome, color, hatch in (
        (-width / 2, outcomes[0], GREEN, ""),
        (width / 2, outcomes[1], PURPLE, "//"),
    ):
        subset = frame.set_index(["model", "outcome"]).loc[[(m, outcome) for m in models]]
        bars = ax.bar(x + offset, subset.fraction_inside, width, color=color,
                      edgecolor="white", linewidth=0.5, hatch=hatch, label=outcome)
        for bar, (_, row) in zip(bars, subset.iterrows()):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.025,
                    f"{int(row.inside)}/{int(row.total)}", ha="center", va="bottom", fontsize=5.8)
    ax.axhline(0.8, color=NEUTRAL_COLOR, ls="--", lw=0.8, label="Gate threshold")
    ax.set_xticks(x, ["Accumulator", "Leak +\nurgency"])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Fraction inside 95% ranges")
    ax.set_title(title, loc="left")
    ax.legend(loc="lower left", fontsize=5.4, handlelength=1.4)


def build_figure(original_dep, original_cov, revised_dep, revised_cov, strategy, calibration):
    fig = plt.figure(figsize=(FULL_WIDTH, 165 / 25.4), constrained_layout=True)
    outer = fig.add_gridspec(3, 2, height_ratios=(1, 1, 1.05))

    ax_a = fig.add_subplot(outer[0, 0])
    ax_b = fig.add_subplot(outer[0, 1])
    plot_departure(ax_a, original_dep, "Original choice gate")
    plot_coverage(ax_b, original_cov, "Original predictive coverage")

    cell_c = outer[1, 0].subgridspec(1, 2, width_ratios=(1.12, 0.88), wspace=0.35)
    ax_c1 = fig.add_subplot(cell_c[0, 0])
    ax_c2 = fig.add_subplot(cell_c[0, 1])
    plot_departure(ax_c1, revised_dep, "Gain-revised gate", show_legend=False)
    plot_coverage(ax_c2, revised_cov, "Coverage", compact=True)

    ax_d = fig.add_subplot(outer[1, 1])
    x = np.arange(len(strategy))
    ax_d.bar(x, np.ones(len(strategy)), color=LIGHT, edgecolor="0.65", label="Not correct")
    bars = ax_d.bar(x, strategy.fraction_correct, color=[ORANGE, BLUE], edgecolor="white",
                    hatch=["//", ""], label="Correct verdict")
    for bar, (_, row) in zip(bars, strategy.iterrows()):
        ax_d.text(bar.get_x() + bar.get_width() / 2, max(row.fraction_correct + 0.04, 0.08),
                  f"{int(row.correct_verdicts)}/{int(row.total_datasets)}", ha="center", va="bottom")
    ax_d.set_xticks(x, ["Rapid-forgetting\ngenerator", "Accumulator\ngenerator"])
    ax_d.set_ylim(0, 1.08)
    ax_d.set_ylabel("Fraction correctly distinguished")
    ax_d.set_title("Frozen strategy sensitivity", loc="left")
    ax_d.legend(loc="upper right", fontsize=5.5)

    ax_e = fig.add_subplot(outer[2, 0])
    x = calibration["decay_percent_over_0.5_s"].to_numpy()
    ax_e.plot(x, calibration.gate_pass_fraction, "o-", color=GREEN, label="Gate passed")
    ax_e.plot(x, calibration.detection_fraction, "s--", color=PURPLE, label="Primacy detected")
    for _, row in calibration.iterrows():
        ax_e.annotate(f"{int(row.gate_passes)}/{int(row.total_datasets)}",
                      (row["decay_percent_over_0.5_s"], row.gate_pass_fraction),
                      xytext=(0, 5), textcoords="offset points", ha="center", fontsize=5.6, color=GREEN)
        ax_e.annotate(f"{int(row.primary_primacy_detections)}/{int(row.total_datasets)}",
                      (row["decay_percent_over_0.5_s"], row.detection_fraction),
                      xytext=(0, 5), textcoords="offset points", ha="center", fontsize=5.6, color=PURPLE)
    ax_e.set_xticks(x)
    ax_e.set_ylim(-0.04, 1.08)
    ax_e.set_xlabel("True decline over 0.5 s (%)")
    ax_e.set_ylabel("Fraction of simulated datasets")
    ax_e.set_title("Timing-test calibration", loc="left")
    ax_e.legend(loc="upper right", fontsize=5.5)

    ax_f = fig.add_subplot(outer[2, 1])
    ax_f.axis("off")
    steps = [
        ("Frozen original\npredictions", BLUE),
        ("Predictive\ngate failed", ORANGE),
        ("Cross-validated\npulse gain", BLUE),
        ("Revised gate\nfailed", ORANGE),
        ("Calibration:\nlow sensitivity", PURPLE),
        ("Timing test\nnot run", NEUTRAL_COLOR),
    ]
    positions = [(0.23, 0.78), (0.75, 0.78), (0.75, 0.50),
                 (0.23, 0.50), (0.23, 0.22), (0.75, 0.22)]
    for (label, color), (xpos, ypos) in zip(steps, positions):
        ax_f.text(xpos, ypos, label, ha="center", va="center", fontsize=5.7,
                  color="white", transform=ax_f.transAxes,
                  bbox=dict(boxstyle="round,pad=0.32", facecolor=color, edgecolor="none"))
    arrow_pairs = [
        ((0.37, 0.78), (0.60, 0.78)),
        ((0.75, 0.70), (0.75, 0.59)),
        ((0.61, 0.50), (0.38, 0.50)),
        ((0.23, 0.42), (0.23, 0.31)),
        ((0.37, 0.22), (0.60, 0.22)),
    ]
    for start, end in arrow_pairs:
        ax_f.annotate("", xy=end, xytext=start, xycoords=ax_f.transAxes,
                      textcoords=ax_f.transAxes,
                      arrowprops=dict(arrowstyle="->", lw=0.8, color="0.35"))
    ax_f.set_title("Analysis and stopping sequence", loc="left")

    for letter, ax in zip("ABCDEF", (ax_a, ax_b, ax_c1, ax_d, ax_e, ax_f)):
        label_panel(ax, letter, x=-0.24 if letter in "ACE" else -0.18, y=1.06)
    return fig


def write_source_data(base, original_dep, original_cov, revised_dep, revised_cov, strategy, calibration):
    original_dep.to_csv(base.with_name(base.name + "_source_A_departure.csv"), index=False)
    original_cov.to_csv(base.with_name(base.name + "_source_B_coverage.csv"), index=False)
    pd.concat([revised_dep, revised_cov], keys=["departure", "coverage"], names=["table"]).to_csv(
        base.with_name(base.name + "_source_C_revised_gate.csv"), index=False)
    strategy.to_csv(base.with_name(base.name + "_source_D_strategy.csv"), index=False)
    calibration.to_csv(base.with_name(base.name + "_source_E_calibration.csv"), index=False)
    pd.DataFrame(
        {
            "order": range(1, 7),
            "step": ["frozen original predictions", "original gate failed", "cross-validated pulse gain",
                     "revised gate failed", "timing calibration had low sensitivity", "timing test not run"],
        }
    ).to_csv(base.with_name(base.name + "_source_F_sequence.csv"), index=False)


def main():
    apply_style()
    original_dep, original_cov = gate_rows(DATA / "primacy", "original")
    revised_dep, revised_cov = gate_rows(DATA / "primacy_revised", "gain-revised")
    strategy = strategy_rows()
    calibration = calibration_rows()

    assert original_cov.query("outcome == 'RT quantiles'").inside.tolist() == [34, 34]
    assert original_cov.query("outcome == 'No response'").inside.tolist() == [9, 5]
    assert revised_cov.query("outcome == 'RT quantiles'").inside.tolist() == [31, 35]
    assert revised_cov.query("outcome == 'No response'").inside.tolist() == [9, 6]
    assert strategy.correct_verdicts.tolist() == [1, 0]
    assert calibration.gate_passes.tolist() == [19, 14, 7, 1]
    assert calibration.primary_primacy_detections.tolist() == [0, 0, 1, 0]

    fig = build_figure(original_dep, original_cov, revised_dep, revised_cov, strategy, calibration)
    base = save_publication(fig, "figS6_gates_sensitivity")
    write_source_data(base, original_dep, original_cov, revised_dep, revised_cov, strategy, calibration)
    plt.close(fig)
    print("original coverage:", original_cov[["model", "outcome", "inside", "total"]].to_dict("records"))
    print("revised coverage:", revised_cov[["model", "outcome", "inside", "total"]].to_dict("records"))
    print("strategy correct:", strategy[["generator", "correct_verdicts", "total_datasets"]].to_dict("records"))
    print("calibration:", calibration[["decay_percent_over_0.5_s", "gate_passes", "primary_primacy_detections", "total_datasets"]].to_dict("records"))


if __name__ == "__main__":
    main()
