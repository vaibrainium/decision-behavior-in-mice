"""Preview the best all-trial joint model against control and pulse data.

Uses saved full-fit simulations from the fit browser.  The decision model is not
refitted here; only descriptive four-parameter psychometric display curves are
fit to the saved equal-mouse summaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from scripts.paper.build_paper_2026_11_15 import BLUE, ORANGE, STYLE, plt


SOURCE = Path("dissemination/figures/qc/fit_browser_2026-11-12_v7.json")
MODEL = "power_leak_urgency"
MODEL_LABEL = "Power-law input + leak + urgency, with sᵥ"
LEFT = BLUE
RIGHT = ORANGE
CONTROL = "#333333"
MODEL_CONTROL = "#6A51A3"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cells() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    browser = json.loads(SOURCE.read_text())
    assert MODEL in browser["families"]
    parts = []
    for family, tables in [
        ("data", browser["data"]),
        (MODEL, browser["families"][MODEL]),
    ]:
        for mouse in browser["mice"]:
            rows = pd.DataFrame(tables[mouse]["rows"], columns=browser["columns"])
            rows["mouse"] = mouse
            rows["family"] = family
            parts.append(rows)
    cells = pd.concat(parts, ignore_index=True)
    keys = ["mouse", "cond", "coh"]
    observed_keys = cells.loc[cells.family.eq("data"), keys].drop_duplicates()
    predicted_keys = cells.loc[cells.family.eq(MODEL), keys].drop_duplicates()
    match = observed_keys.merge(predicted_keys, on=keys, how="outer", indicator=True)
    assert match["_merge"].eq("both").all()
    cells = cells.merge(observed_keys, on=keys, how="inner", validate="many_to_one")

    group = (
        cells.groupby(["family", "cond", "coh"], as_index=False)
        .agg(
            p=("p", "mean"),
            sem_p=("p", "sem"),
            rt=("rt", "mean"),
            sem_rt=("rt", "sem"),
            n_mice=("mouse", "nunique"),
            n_rows=("n", "sum"),
        )
        .sort_values(["family", "cond", "coh"])
    )
    return cells, group, browser


def render(
    output: Path,
    cells: pd.DataFrame,
    group: pd.DataFrame,
) -> None:
    data = cells[cells.family.eq("data")]
    columns = [
        ("control", ["control"]),
        ("early", ["early left", "early right"]),
        ("middle", ["middle left", "middle right"]),
        ("late", ["late left", "late right"]),
    ]
    direction_style = {
        "control": (CONTROL, "o"),
        "left": (LEFT, "v"),
        "right": (RIGHT, "^"),
    }

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(2, 4, figsize=(180 / 25.4, 112 / 25.4))
        fig.subplots_adjust(
            left=.075, right=.985, bottom=.245, top=.835, wspace=.32, hspace=.48
        )
        for col, (stage, conditions) in enumerate(columns):
            n_mice = data[data.cond.isin(conditions)].mouse.nunique()
            title = "Control trials" if stage == "control" else f"{stage.capitalize()} pulses"
            axes[0, col].set_title(f"{title} ({n_mice} mice)", loc="left", fontsize=7.7)

            for cond in conditions:
                direction = "control" if cond == "control" else cond.split()[-1]
                color, marker = direction_style[direction]
                observed = group[
                    group.family.eq("data") & group.cond.eq(cond)
                ].sort_values("coh")
                predicted = group[
                    group.family.eq(MODEL) & group.cond.eq(cond)
                ].sort_values("coh")
                assert observed.coh.tolist() == predicted.coh.tolist()

                axes[0, col].errorbar(
                    observed.coh,
                    observed.p,
                    yerr=observed.sem_p,
                    fmt=marker,
                    color=color,
                    ms=3.1,
                    capsize=1.5,
                    ls="none",
                    zorder=4,
                )
                model_color = MODEL_CONTROL if cond == "control" else color
                axes[0, col].plot(
                    predicted.coh,
                    predicted.p,
                    "-D",
                    color=model_color,
                    markerfacecolor="white",
                    markeredgecolor=model_color,
                    markeredgewidth=.75,
                    markersize=2.8,
                    lw=1.25,
                )

                axes[1, col].fill_between(
                    observed.coh,
                    observed.rt - observed.sem_rt,
                    observed.rt + observed.sem_rt,
                    color=color,
                    alpha=.12,
                    linewidth=0,
                )
                axes[1, col].plot(
                    observed.coh,
                    observed.rt,
                    ":",
                    color=color,
                    lw=.8,
                    marker=marker,
                    ms=3.1,
                    zorder=4,
                )
                axes[1, col].plot(
                    predicted.coh,
                    predicted.rt,
                    "-",
                    color=model_color,
                    lw=1.45,
                )

            for row in range(2):
                axes[row, col].set(
                    xlim=(-110, 110),
                    xticks=[-100, -36, 0, 36, 100],
                    xlabel="Signed baseline coherence (%)",
                )
            axes[0, col].set_ylim(0, 1)
            axes[0, col].axhline(.5, color=".85", lw=.5, zorder=0)

        rt_values = group[group.family.isin(["data", MODEL])]
        rt_low = max(.25, float((rt_values.rt - rt_values.sem_rt.fillna(0)).min()) - .08)
        rt_high = float((rt_values.rt + rt_values.sem_rt.fillna(0)).max()) + .12
        for ax in axes[1]:
            ax.set_ylim(rt_low, rt_high)
        axes[0, 0].set_ylabel("P(right response)")
        axes[1, 0].set_ylabel("Mean RT, all responses (s)")
        axes[0, 0].text(
            -.23, 1.09, "A", transform=axes[0, 0].transAxes, fontweight="bold", fontsize=10
        )
        axes[1, 0].text(
            -.23, 1.09, "B", transform=axes[1, 0].transAxes, fontweight="bold", fontsize=10
        )
        fig.text(
            .035,
            .965,
            "Figure 6a variation | Best all-trial model fits",
            fontsize=10,
            va="top",
        )
        fig.text(
            .035,
            .915,
            MODEL_LABEL,
            fontsize=7,
            color=".3",
            va="top",
        )
        handles = [
            Line2D([], [], color=CONTROL, marker="o", ls="none", label="Control data ± mouse SEM"),
            Line2D([], [], color=LEFT, marker="v", ls="none", label="Left-pulse data ± mouse SEM"),
            Line2D([], [], color=RIGHT, marker="^", ls="none", label="Right-pulse data ± mouse SEM"),
            Line2D([], [], color=MODEL_CONTROL, marker="D", mfc="white", ls="-", lw=1.25, label="Model points (control)"),
            Line2D([], [], color=".2", marker="D", mfc="white", ls="-", lw=1.25, label="Model points (pulse; direction color)"),
        ]
        fig.legend(
            handles=handles,
            loc="lower center",
            bbox_to_anchor=(.52, .055),
            ncol=3,
            fontsize=5.8,
            columnspacing=1.4,
        )
        fig.text(
            .075,
            .018,
            "Full-fit descriptive predictions from saved simulations; curves are not held-out validation. "
            "Observed uncertainty is between-mouse SEM.",
            fontsize=5.7,
            color=".3",
        )
        for ext in ["png", "pdf", "svg"]:
            fig.savefig(output / f"figure6a_all_trial_model_fit.{ext}", dpi=300)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    cells, group, browser = load_cells()
    cells.to_csv(args.output / "mouse_cells.csv", index=False)
    group.to_csv(args.output / "group_summaries.csv", index=False)
    group[group.family.eq(MODEL)].to_csv(args.output / "model_display_points.csv", index=False)
    render(args.output, cells, group)

    counts = (
        cells[cells.family.eq("data")]
        .groupby("cond", as_index=False)
        .agg(n_trials=("n", "sum"), n_mice=("mouse", "nunique"))
    )
    counts.to_csv(args.output / "observed_counts.csv", index=False)
    verification = {
        "model": MODEL,
        "all_prediction_cells_match_observed_support": True,
        "n_observed_mouse_cells": int((cells.family == "data").sum()),
        "n_model_mouse_cells": int((cells.family == MODEL).sum()),
        "n_mice": int(cells.mouse.nunique()),
        "new_decision_model_fits": False,
        "new_simulations": False,
        "psychometric_display": "observed points with SEM; saved model probabilities as points connected across tested coherences; no logistic display fit",
        "observed_uncertainty": "between-mouse SEM",
        "model_uncertainty_displayed": False,
        "saved_summary_precision": "four decimal places",
    }
    (args.output / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    caption = (
        "Figure 6a variation. Best all-trial model fit preview. The power-law input model with leak, urgency, and persistent "
        "across-trial drift variability was selected by both equal-mouse held-out joint bits per trial and "
        "full-fit BIC in the all-trial comparison. Columns show control trials and early, middle, and late "
        "pulse conditions. Points are equal-mouse observed means; vertical error bars and RT ribbons are "
        "between-mouse SEM. Downward blue and upward orange triangles denote leftward and rightward pulses. "
        "(A) Right-choice probability. Observed probabilities are points with between-mouse SEM; open "
        "diamonds are saved model probabilities at the same tested coherences, joined by straight segments. "
        "No psychometric function is fitted to either series for display. "
        "(B) Arithmetic mean response time across both choices. Dotted point-lines show observations and "
        "solid lines show model predictions at tested coherences. The decision model was fitted jointly to "
        "control and pulse trials. Displayed predictions use saved full-fit parameters and simulations of "
        "each mouse's responded trial schedules (30 repetitions, seed 0); therefore the overlays are "
        "descriptive fits, not held-out validation. Model summaries are matched to the exact observed "
        "mouse/condition/coherence support. The display population is the fit browser's symmetric scheduled-"
        "pulse responded-trial selection and is not the narrower post-pulse-end selection used in Figure 4."
    )
    (args.output / "caption.md").write_text(caption + "\n")
    manifest = {
        "source": str(SOURCE),
        "source_sha256": sha256(SOURCE),
        "code_sha256": sha256(Path(__file__)),
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "model": MODEL,
        "model_label": MODEL_LABEL,
        "figure_variation": "6a",
        "browser_made": browser.get("made"),
        "scope": "Preview only; saved full-fit simulations; no decision-model refit or manuscript selection change.",
        "population_counts": counts.to_dict("records"),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(counts.to_string(index=False))


if __name__ == "__main__":
    main()
