"""Summarize the choice--RT weight sweep on a common held-out scale.

The fit objective differs across families, so this script reads only scores
recomputed with ``rt_nllh_weight=1``.  Simulation seeds are averaged within
mouse before mice are treated as the independent sampling units.  Positive
changes in bits/trial mean improvement over the weight-1 baseline.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from scripts.paper.build_paper_2026_11_15 import BLUE, ORANGE, STYLE, plt


BASELINE = "pulse_norm_ugm_no_sv"
ORDER = [
    BASELINE,
    "pulse_norm_ugm_choice_w2",
    "pulse_norm_ugm_choice_w4",
    "pulse_norm_ugm_choice_w8",
    "pulse_norm_ugm_choice_only",
]
LABELS = {
    BASELINE: "1×",
    "pulse_norm_ugm_choice_w2": "2×",
    "pulse_norm_ugm_choice_w4": "4×",
    "pulse_norm_ugm_choice_w8": "8×",
    "pulse_norm_ugm_choice_only": "Choice only",
}


def ci95(values: pd.Series) -> tuple[float, float]:
    values = values.dropna()
    assert len(values) == 10
    if np.allclose(values, values.iloc[0]):
        return float(values.iloc[0]), float(values.iloc[0])
    return stats.t.interval(
        0.95, len(values) - 1, loc=values.mean(), scale=stats.sem(values)
    )


def summarize(source: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scores = pd.read_csv(source / "pareto_scores_by_mouse_seed.csv")
    assert set(scores.family) == set(ORDER)
    assert scores.groupby("family").mouse.nunique().eq(10).all()
    assert scores.groupby("family").seed.nunique().eq(5).all()
    assert not scores.isna().any().any()
    mouse = (
        scores.groupby(["family", "mouse"], as_index=False)
        .agg(
            choice_nll=("choice_nll", "mean"),
            rt_nll=("rt_nll", "mean"),
            joint_nll=("joint_nll", "mean"),
            n=("n", "first"),
        )
    )
    baseline = mouse[mouse.family.eq(BASELINE)].set_index("mouse")
    rows = []
    for family in ORDER:
        current = mouse[mouse.family.eq(family)].set_index("mouse").loc[baseline.index]
        for component in ["choice", "rt", "joint"]:
            improvement = (
                baseline[f"{component}_nll"] - current[f"{component}_nll"]
            ) / (baseline.n * np.log(2))
            for animal, value in improvement.items():
                rows.append(
                    {
                        "family": family,
                        "label": LABELS[family],
                        "mouse": animal,
                        "component": component,
                        "improvement_bits_per_trial": value,
                    }
                )
    changes = pd.DataFrame(rows)
    summary_rows = []
    for keys, group in changes.groupby(["family", "label", "component"], sort=False):
        lo, hi = ci95(group.improvement_bits_per_trial)
        summary_rows.append(
            {
                "family": keys[0],
                "label": keys[1],
                "component": keys[2],
                "mean": group.improvement_bits_per_trial.mean(),
                "ci_lo": lo,
                "ci_hi": hi,
                "median": group.improvement_bits_per_trial.median(),
                "mice_improved": int((group.improvement_bits_per_trial > 0).sum()),
                "n_mice": len(group),
            }
        )
    summary = pd.DataFrame(summary_rows)

    control = pd.read_csv(source / "control/cells.csv.gz")
    control["g2"] = 2 * (control.choice_nll - control.sat)
    control_mouse = (
        control.groupby(["family", "seed", "mouse", "scored"], as_index=False)
        .agg(g2=("g2", "sum"), n=("n", "sum"))
        .groupby(["family", "mouse", "scored"], as_index=False)
        .agg(g2=("g2", "mean"), n=("n", "first"))
    )
    guardrail_rows = []
    for scored in ["pulse", "control"]:
        base = control_mouse[
            control_mouse.family.eq(BASELINE) & control_mouse.scored.eq(scored)
        ].set_index("mouse")
        for family in ORDER:
            current = control_mouse[
                control_mouse.family.eq(family) & control_mouse.scored.eq(scored)
            ].set_index("mouse").loc[base.index]
            delta = current.g2 / current.n - base.g2 / base.n
            lo, hi = ci95(delta)
            guardrail_rows.append(
                {
                    "family": family,
                    "label": LABELS[family],
                    "scored": scored,
                    "mean_delta_g2_per_trial": delta.mean(),
                    "ci_lo": lo,
                    "ci_hi": hi,
                    "mice_improved": int((delta < 0).sum()),
                    "n_mice": len(delta),
                }
            )
    guardrail = pd.DataFrame(guardrail_rows)
    return changes, summary, guardrail


def render(changes: pd.DataFrame, summary: pd.DataFrame, output: Path) -> None:
    colors = {"choice": BLUE, "rt": ORANGE, "joint": "#4D4D4D"}
    titles = {
        "choice": "Held-out choices",
        "rt": "Held-out response times",
        "joint": "Original joint score",
    }
    x = np.arange(len(ORDER))
    rng = np.random.default_rng(20261127)
    jitter = {mouse: value for mouse, value in zip(sorted(changes.mouse.unique()), rng.uniform(-0.11, 0.11, 10))}
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 3, figsize=(180 / 25.4, 76 / 25.4))
        fig.subplots_adjust(left=0.075, right=0.985, bottom=0.29, top=0.68, wspace=0.42)
        for ax, component, letter in zip(axes, ["choice", "rt", "joint"], "ABC"):
            part = changes[changes.component.eq(component)].copy()
            for mouse, group in part.groupby("mouse"):
                group = group.set_index("family").loc[ORDER]
                ax.plot(x, group.improvement_bits_per_trial, color="0.78", lw=0.55, zorder=1)
                ax.scatter(x + jitter[mouse], group.improvement_bits_per_trial, s=8, color="0.62", alpha=0.8, zorder=2)
            group = summary[summary.component.eq(component)].set_index("family").loc[ORDER]
            y = group["mean"].to_numpy()
            ax.errorbar(
                x, y, yerr=[y - group.ci_lo.to_numpy(), group.ci_hi.to_numpy() - y],
                fmt="o-", color=colors[component], lw=1.25, ms=3.8, capsize=2.2, zorder=4,
                label="Equal-mouse mean ± 95% CI",
            )
            ax.axhline(0, color="black", lw=0.65, ls="--", zorder=0)
            ax.set_xticks(x, [LABELS[f] for f in ORDER], rotation=25, ha="right")
            ax.set_title(titles[component], loc="left", fontsize=7.4)
            ax.text(-0.18, 1.06, letter, transform=ax.transAxes, fontweight="bold", fontsize=9)
            ax.set_xlabel("Relative choice weight")
        axes[0].set_ylabel("Improvement over 1× (bits/trial)\npositive is better")
        axes[1].set_ylim(-0.62, 0.12)
        axes[2].set_ylim(-0.62, 0.12)
        fig.text(0.035, 0.965, "Choice–RT likelihood trade-off", fontsize=9.3, va="top")
        fig.text(
            0.035, 0.875,
            "Original unweighted held-out score; five simulation seeds averaged within each of 10 mice",
            fontsize=6.4, color="0.25", va="top",
        )
        fig.text(
            0.075, 0.025,
            "Gray points/lines: individual mice. Intervals use mice—not trials—as the sampling unit.",
            fontsize=5.4, color="0.3",
        )
        for ext in ["png", "pdf", "svg"]:
            fig.savefig(output / f"choice_rt_pareto.{ext}", dpi=300, facecolor="white")
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    changes, summary, guardrail = summarize(args.source)
    changes.to_csv(args.output / "heldout_mouse_changes.csv", index=False)
    summary.to_csv(args.output / "heldout_group_summary.csv", index=False)
    guardrail.to_csv(args.output / "full_fit_choice_guardrail.csv", index=False)
    render(changes, summary, args.output)
    manifest = {
        "source": str(args.source),
        "estimand": "Equal-mouse mean change in unweighted held-out bits/trial after averaging five simulation seeds within mouse.",
        "uncertainty": "Two-sided 95% Student-t interval across 10 mice; descriptive exploratory analysis.",
        "positive_direction": "Positive held-out bits/trial is better; negative full-fit G2/trial change is better.",
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
