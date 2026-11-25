"""Figure 5 preview ranked by held-out joint bits/trial; no new fits."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

from scripts.paper.build_paper_2026_11_15 import BLUE, ORANGE, STYLE, plt
from scripts.paper.figure5_pulse_only_opening import readable, save, schematic


BITS_SOURCE = Path(
    "dissemination/paper_accumulation/draft_2026-11-15/"
    "pulse_only_bits_2026-11-18/bits_summary.csv"
)
IC_SOURCE = Path("dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_scores() -> pd.DataFrame:
    bits = pd.read_csv(BITS_SOURCE)
    ic = pd.read_csv(IC_SOURCE)
    pulse_ic = ic.loc[ic["kind"].eq("pulse_only"), ["family", "bic", "n"]].copy()
    frame = bits.merge(pulse_ic, on="family", how="inner", validate="one_to_one")

    assert len(bits) == len(pulse_ic) == len(frame) == 22
    assert frame["family"].nunique() == 22
    assert frame["n_mice"].eq(10).all()
    assert frame["n_test_total"].nunique() == 1
    assert frame["n"].nunique() == 1
    assert np.isfinite(
        frame[["mean_joint_test_bits_per_trial", "bic"]].to_numpy()
    ).all()

    frame = frame.sort_values(
        "mean_joint_test_bits_per_trial", ascending=False
    ).reset_index(drop=True)
    expected_rank = np.arange(1, len(frame) + 1)
    np.testing.assert_array_equal(frame["rank"].to_numpy(), expected_rank)
    np.testing.assert_allclose(
        frame["difference_from_best_bits_per_trial"],
        frame["mean_joint_test_bits_per_trial"]
        - frame["mean_joint_test_bits_per_trial"].max(),
        atol=1e-12,
    )
    assert frame.iloc[0]["family"] == "pulse_norm_ugm_no_sv"
    assert frame.loc[frame["bic"].idxmin(), "family"] == "pulse_linear_leak"
    frame["display_label"] = frame["family"].map(readable)
    assert frame["display_label"].nunique() == 22
    return frame


def score_panels(fig: mpl.figure.Figure, frame: pd.DataFrame) -> None:
    y = np.arange(len(frame))
    specs = [
        (
            "mean_joint_test_bits_per_trial",
            "Held-out bits/trial",
            "Equal-mouse mean joint log score\n(bits/trial; higher is better)",
            [.405, .14, .235, .50],
            BLUE,
            int(frame["mean_joint_test_bits_per_trial"].idxmax()),
        ),
        (
            "bic",
            "BIC",
            "BIC (lower is better)",
            [.735, .14, .235, .50],
            ORANGE,
            int(frame["bic"].idxmin()),
        ),
    ]
    axes = []
    for metric, title, xlabel, position, color, winner_index in specs:
        ax = fig.add_axes(position)
        axes.append(ax)
        ax.scatter(frame[metric], y, c=".55", s=14, zorder=3)
        ax.scatter(
            frame.loc[winner_index, metric],
            winner_index,
            c=color,
            s=35,
            zorder=4,
        )
        ax.set(
            ylim=(len(frame) - .5, -.5),
            yticks=y,
            xlabel=xlabel,
        )
        ax.set_yticklabels(
            frame["display_label"] if metric.startswith("mean_joint") else [""] * len(frame),
            fontsize=6.4,
        )
        ax.tick_params(axis="y", length=0, pad=7)
        ax.tick_params(axis="x", labelsize=6.3)
        ax.set_title(title, loc="left", fontsize=8, pad=8)
        ax.margins(x=.15)
        for row in y:
            ax.axhline(row, color=".94", lw=.4, zorder=0)
    axes[0].xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.3f"))
    axes[0].xaxis.set_major_locator(mpl.ticker.MaxNLocator(4))
    axes[1].xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    axes[1].xaxis.set_major_locator(mpl.ticker.MaxNLocator(3))
    axes[0].text(
        -1.38,
        1.06,
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

    frame = load_scores()
    frame.to_csv(args.output / "pulse_only_candidates_bits_ranked.csv", index=False)

    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(220 / 25.4, 205 / 25.4))
        ax = fig.add_axes([.035, .72, .93, .20])
        schematic(ax)
        score_panels(fig, frame)
        fig.text(
            .035,
            .975,
            "Figure 5a variation | Pulse-only accumulation fits",
            fontsize=10,
            va="top",
        )
        fig.text(.035, .66, "Pulse-only candidate comparison", fontsize=8.5)
        fig.text(
            .035,
            .075,
            "Best held-out bits/trial: normalized UGM region, no sᵥ",
            color=BLUE,
            fontsize=7,
        )
        fig.text(
            .035,
            .045,
            "Lowest BIC: linear leaky accumulator, with sᵥ",
            color=ORANGE,
            fontsize=7,
        )
        fig.text(
            .035,
            .018,
            "All 22 pulse-only candidates; bits/trial averages 10 mice equally. No new fits or scores.",
            fontsize=6.5,
            color=".3",
        )
        save(fig, args.output / "figure5_bits_ranked")

    caption = """Figure 5 bits/trial ranking preview. (A) Components varied across the existing pulse-only accumulation fits. The diagram is a conceptual summary, not a fully crossed design or simulated trajectory. (B) The 22 pulse-only candidates are ordered by equal-mouse mean held-out joint log score in bits per trial (higher, or less negative, is better). For each mouse, bits/trial equals -held-out NLL divided by the number of held-out trials and ln(2); the plotted value then averages the 10 mice equally. This is a joint choice-and-response-time score, not choice-only information gain over a null model. The adjacent BIC values use the same candidate order but are independently rescored full-fit criteria; lower is better. Blue marks the best bits/trial candidate and orange the lowest-BIC candidate. The predictive winner remains normalized input in the urgency-gating region without drift variability; BIC favors the linear-input leaky accumulator with drift variability. The lower-rank order can differ from summed NLL because equal-mouse bits/trial and cohort-total NLL weight mice differently. Points are descriptive, with no inferential error bars or new group test. No fitting or rescoring was performed.
"""
    (args.output / "caption.md").write_text(caption)

    manifest = {
        "base_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "bits_source": str(BITS_SOURCE),
        "bits_source_sha256": sha256(BITS_SOURCE),
        "ic_source": str(IC_SOURCE),
        "ic_source_sha256": sha256(IC_SOURCE),
        "code_sha256": sha256(Path(__file__)),
        "definition": "within-mouse -heldout_nll/(n_heldout ln2), then equal-mouse mean",
        "n_candidates": len(frame),
        "n_mice": int(frame["n_mice"].iloc[0]),
        "n_test_total_per_candidate": int(frame["n_test_total"].iloc[0]),
        "bits_winner": frame.iloc[0]["family"],
        "bic_winner": frame.loc[frame["bic"].idxmin(), "family"],
        "new_fits": False,
        "new_scores": False,
        "figure_variation": "5a",
        "status": "author-review preview; original Figure 5 retained",
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        frame[["rank", "family", "mean_joint_test_bits_per_trial", "bic"]]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
