"""Figure 5 preview for all-trial joint fits ranked by held-out bits/trial."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from scripts.paper.build_paper_2026_11_15 import BLUE, ORANGE, STYLE, plt
from scripts.paper.figure5_pulse_only_opening import save


PER_MOUSE_SOURCE = Path(
    "dissemination/figures/qc/model_ic_per_mouse_2026-11-12_rescored.csv"
)
SUMMARY_SOURCE = Path(
    "dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pretty_family(family: str) -> str:
    exact = {
        "primary": "Linear · Integrator · sᵥ",
        "no_sv": "Linear · Integrator · no sᵥ",
        "leak": "Linear · Leak · sᵥ",
        "urgency": "Linear · Urgency · sᵥ",
        "leak_urgency": "Linear · Leak + urgency · sᵥ",
        "linear_ugm": "Linear · UGM region · sᵥ",
        "linear_ugm_no_sv": "Linear · UGM region · no sᵥ",
        "fixed_guess_bias": "Linear · Integrator · fixed guess bias",
        "no_guess": "Linear · Integrator · no fast guesses",
        "free_leak_0-200": "Linear · Free leak (0–200 s⁻¹)",
        "nominal_no_sv": "Nominal coherence · Integrator · no sᵥ",
        "pw_shared": "Linear · Shared pulse weight · sᵥ",
        "pw_shared_no_sv": "Linear · Shared pulse weight · no sᵥ",
        "pw_per_time": "Linear · Pulse weight by time · sᵥ",
        "pw_per_time_no_sv": "Linear · Pulse weight by time · no sᵥ",
        "extrema_E_leak20-200": "Linear · Extrema detection E",
        "extrema_sampling_ES": "Linear · Extrema sampling ES",
        "stine_nominal_DDM": "Nominal coherence · Stine DDM",
        "stine_nominal_ES": "Nominal coherence · Stine ES",
    }
    if family in exact:
        return exact[family]
    prefix_map = {
        "power_": "Power · ",
        "norm_": "Normalized · ",
        "nominal_": "Nominal coherence · ",
    }
    prefix = ""
    stem = family
    for token, label in prefix_map.items():
        if stem.startswith(token):
            prefix = label
            stem = stem[len(token) :]
            break
    suffix = " · sᵥ"
    if stem.endswith("_no_sv"):
        stem = stem.removesuffix("_no_sv")
        suffix = " · no sᵥ"
    names = {
        "primary": "Integrator",
        "power_primary": "Power-law integrator",
        "leak": "Leak",
        "urgency": "Urgency",
        "leak_urgency": "Leak + urgency",
        "ugm": "UGM region",
        "extrema_E_leak20-200": "Extrema detection E",
        "extrema_sampling_ES": "Extrema sampling ES",
    }
    if stem not in names:
        raise ValueError(f"unmapped joint family: {family}")
    return prefix + names[stem] + suffix


def load_scores() -> tuple[pd.DataFrame, pd.DataFrame]:
    per_mouse = pd.read_csv(PER_MOUSE_SOURCE)
    per_mouse = per_mouse.loc[per_mouse["kind"].eq("joint")].copy()
    assert len(per_mouse) == 420
    assert per_mouse["family"].nunique() == 42
    assert per_mouse["mouse"].nunique() == 10
    assert not per_mouse.duplicated(["family", "mouse"]).any()
    assert np.isfinite(per_mouse[["heldout_nll", "n_heldout"]]).all().all()
    assert (per_mouse["n_heldout"] > 0).all()
    counts = per_mouse.pivot(index="mouse", columns="family", values="n_heldout")
    assert counts.notna().all().all()
    assert counts.nunique(axis=1).eq(1).all()

    per_mouse["heldout_bits_per_trial"] = -per_mouse["heldout_nll"] / (
        per_mouse["n_heldout"] * np.log(2)
    )
    bits = (
        per_mouse.groupby("family", as_index=False)
        .agg(
            mean_joint_test_bits_per_trial=("heldout_bits_per_trial", "mean"),
            n_mice=("mouse", "nunique"),
            n_test_total=("n_heldout", "sum"),
            total_heldout_nll=("heldout_nll", "sum"),
        )
    )
    summary = pd.read_csv(SUMMARY_SOURCE)
    summary = summary.loc[
        summary["kind"].eq("joint"), ["family", "bic", "n", "group", "label"]
    ]
    frame = bits.merge(summary, on="family", validate="one_to_one")
    assert len(frame) == 42
    frame = frame.sort_values(
        "mean_joint_test_bits_per_trial", ascending=False
    ).reset_index(drop=True)
    frame["rank"] = np.arange(1, len(frame) + 1)
    frame["display_label"] = frame["family"].map(pretty_family)
    assert frame["display_label"].nunique() == 42
    assert frame.iloc[0]["family"] == "power_leak_urgency"
    assert frame.loc[frame["bic"].idxmin(), "family"] == "power_leak_urgency"
    return frame, per_mouse


def schematic(ax: mpl.axes.Axes) -> None:
    ax.set_axis_off()
    ax.set(xlim=(0, 1), ylim=(0, 1))
    boxes = [
        (.02, .18, "All-trial input", "Control + pulse\nmotion evidence"),
        (.265, .21, "Input mapping", "Linear / power / normalization\nNominal coherence"),
        (.54, .23, "Decision dynamics", "Integrator / leak / urgency / UGM\nExtrema detection or sampling"),
        (.825, .15, "Predictions", "Choice\nand RT"),
    ]
    for x, width, title, body in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, .35),
                width,
                .48,
                boxstyle="round,pad=.01",
                fc="#f3f5f7",
                ec=".55",
                lw=.7,
            )
        )
        ax.text(
            x + width / 2,
            .73,
            title,
            ha="center",
            va="center",
            fontsize=7.3,
            fontweight="bold",
        )
        ax.text(
            x + width / 2,
            .52,
            body,
            ha="center",
            va="center",
            fontsize=6.5,
            linespacing=1.5,
        )
    for x1, x2 in [(.20, .265), (.475, .54), (.77, .825)]:
        ax.annotate(
            "",
            xy=(x2 - .015, .59),
            xytext=(x1 + .01, .59),
            arrowprops={"arrowstyle": "->", "lw": .8, "color": ".4"},
        )
    ax.text(
        .655,
        .17,
        "Variants also test drift variability, pulse weights, and fast-guess assumptions",
        ha="center",
        fontsize=6.7,
    )
    ax.text(
        .02,
        .03,
        "42 fitted candidates; model coverage is not a balanced factorial design.",
        fontsize=6.5,
        color=".3",
    )
    ax.text(0, 1.03, "A", fontsize=11, fontweight="bold", transform=ax.transAxes)
    ax.set_title(
        "Candidate models fitted jointly to control and pulse trials",
        loc="left",
        fontsize=9,
        pad=12,
    )


def score_panels(fig: mpl.figure.Figure, frame: pd.DataFrame) -> None:
    y = np.arange(len(frame))
    panels = [
        (
            "mean_joint_test_bits_per_trial",
            "Held-out bits/trial",
            "Equal-mouse mean joint log score\n(bits/trial; higher is better)",
            [.405, .105, .235, .555],
            BLUE,
            int(frame["mean_joint_test_bits_per_trial"].idxmax()),
        ),
        (
            "bic",
            "BIC",
            "BIC (lower is better)",
            [.735, .105, .235, .555],
            ORANGE,
            int(frame["bic"].idxmin()),
        ),
    ]
    axes = []
    for metric, title, xlabel, position, color, winner in panels:
        ax = fig.add_axes(position)
        axes.append(ax)
        ax.scatter(frame[metric], y, c=".55", s=10, zorder=3)
        ax.scatter(frame.loc[winner, metric], winner, c=color, s=30, zorder=4)
        ax.set(ylim=(len(frame) - .5, -.5), yticks=y, xlabel=xlabel)
        ax.set_yticklabels(
            frame["display_label"] if metric.startswith("mean_joint") else [""] * len(frame),
            fontsize=4.6,
        )
        ax.tick_params(axis="y", length=0, pad=6)
        ax.tick_params(axis="x", labelsize=6.2)
        ax.set_title(title, loc="left", fontsize=8, pad=8)
        ax.margins(x=.14)
        for row in y:
            ax.axhline(row, color=".94", lw=.35, zorder=0)
    axes[0].xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.3f"))
    axes[0].xaxis.set_major_locator(mpl.ticker.MaxNLocator(4))
    axes[1].xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    axes[1].xaxis.set_major_locator(mpl.ticker.MaxNLocator(3))
    axes[0].text(
        -1.38,
        1.04,
        "B",
        transform=axes[0].transAxes,
        fontweight="bold",
        fontsize=11,
    )


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    frame, per_mouse = load_scores()
    frame.to_csv(args.output / "all_trial_candidates_bits_ranked.csv", index=False)
    per_mouse.to_csv(args.output / "all_trial_bits_per_mouse.csv", index=False)

    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(220 / 25.4, 275 / 25.4))
        ax = fig.add_axes([.035, .79, .93, .15])
        schematic(ax)
        score_panels(fig, frame)
        fig.text(
            .035,
            .982,
            "Figure 5b variation | All-trial model fits",
            fontsize=10,
            va="top",
        )
        fig.text(.035, .70, "All-trial candidate comparison", fontsize=8.5)
        fig.text(
            .035,
            .055,
            "Best bits/trial and BIC: power-law leak + urgency, with sᵥ",
            color=BLUE,
            fontsize=7,
        )
        fig.text(
            .035,
            .027,
            "42 candidates fitted jointly to control + pulse trials; 10 mice weighted equally for bits/trial.",
            fontsize=6.3,
            color=".3",
        )
        save(fig, args.output / "figure5_all_trials_bits")

    manifest = {
        "base_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "per_mouse_source": str(PER_MOUSE_SOURCE),
        "per_mouse_source_sha256": sha256(PER_MOUSE_SOURCE),
        "summary_source": str(SUMMARY_SOURCE),
        "summary_source_sha256": sha256(SUMMARY_SOURCE),
        "code_sha256": sha256(Path(__file__)),
        "scope": "kind=joint; fitted jointly to control and pulse trials",
        "definition": "within-mouse -heldout_nll/(n_heldout ln2), then equal-mouse mean",
        "n_candidates": len(frame),
        "n_mice": int(frame["n_mice"].iloc[0]),
        "n_test_total_per_candidate": int(frame["n_test_total"].iloc[0]),
        "bits_winner": frame.iloc[0]["family"],
        "bic_winner": frame.loc[frame["bic"].idxmin(), "family"],
        "matched_denominators_within_mouse": True,
        "new_fits": False,
        "new_scores": False,
        "figure_variation": "5b",
        "status": "author-review preview only",
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        frame[["rank", "family", "mean_joint_test_bits_per_trial", "bic"]]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
