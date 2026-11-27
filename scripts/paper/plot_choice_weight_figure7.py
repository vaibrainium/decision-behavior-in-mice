"""Compare Figure 7 pulse signatures across choice-likelihood weights.

All decision-model parameters are fixed at their saved full-pulse fits.  Panel
A uses the already simulated full-fit choice cells.  Panels B and C use the
same onset-stage and dilution-adjusted descriptive readouts as Figure 7B.
"""
from __future__ import annotations

import argparse
import json
import pickle
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from scripts.paper.build_paper_2026_11_15 import STYLE, plt


BASE = Path("dissemination/paper_accumulation/draft_2026-11-15")
FIG4 = BASE / "figure4_final_2026-11-18/source_data"
BASELINE_ONSET = BASE / "pulse_model_primacy_2026-11-18/model_readout_by_seed.csv"
OBSERVED_ONSET_COEFFICIENTS = BASE / "pulse_time_ordinal_2026-11-18/coefficients.csv"
BASELINE_PERSISTENCE = Path("dissemination/pulse_dynamics_2026-11-13/all_readouts.csv")
BASELINE = "pulse_norm_ugm_no_sv"
ORDER = [
    BASELINE,
    "pulse_norm_ugm_choice_w2",
    "pulse_norm_ugm_choice_w4",
    "pulse_norm_ugm_choice_w8",
    "pulse_norm_ugm_choice_only",
]
LABELS = dict(zip(ORDER, ["1×", "2×", "4×", "8×", "Choice only"]))
COLORS = dict(zip(ORDER, ["#B3CDE3", "#8CADD3", "#5F8CC3", "#2F69A8", "#B44C43"]))


def t_ci(values: pd.Series) -> tuple[float, float]:
    values = values.dropna()
    return stats.t.interval(0.95, len(values) - 1, loc=values.mean(), scale=stats.sem(values))


def choice_contrast(score_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    cells = pd.read_csv(score_dir / "control/cells.csv.gz")
    cells = cells[cells.scored.eq("pulse") & cells.scheduled_pulse.ne(0)].copy()
    cells["direction"] = np.sign(cells.scheduled_pulse).astype(int)
    cells["stage"] = cells.scheduled_pulse.abs()
    observed = cells[["mouse", "coherence", "stage", "direction", "n", "k"]].drop_duplicates()
    observed["p_right"] = observed.k / observed.n
    observed = observed.pivot(
        index=["mouse", "coherence", "stage"], columns="direction", values="p_right"
    ).dropna()
    observed["contrast"] = observed[1] - observed[-1]
    observed_mouse = observed.groupby("mouse", as_index=False).contrast.mean()
    observed_mouse["family"] = "data"

    predicted = cells.pivot_table(
        index=["family", "seed", "mouse", "coherence", "stage"],
        columns="direction", values="p1",
    ).dropna()
    predicted["contrast"] = predicted[1] - predicted[-1]
    predicted_mouse_seed = predicted.reset_index().groupby(
        ["family", "seed", "mouse"], as_index=False
    ).agg(contrast=("contrast", "mean"))
    predicted_mouse = predicted_mouse_seed.groupby(
        ["family", "mouse"], as_index=False
    ).agg(contrast=("contrast", "mean"))
    mouse = pd.concat([observed_mouse, predicted_mouse], ignore_index=True)
    rows = []
    for family, group in mouse.groupby("family", sort=False):
        lo, hi = t_ci(group.contrast)
        rows.append(
            {"family": family, "mean": group.contrast.mean(), "ci_lo": lo, "ci_hi": hi,
             "n_mice": group.mouse.nunique()}
        )
    return mouse, pd.DataFrame(rows)


def onset(weighted_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed = pd.read_csv(FIG4 / "fig4_C_timing_curves.csv")
    observed = observed[
        observed.comparison.eq("all_available_10")
        & observed.objective.eq("wls")
        & observed.stage_index.isin([1.0, 2.0, 3.0])
    ][["stage_index", "influence", "ci_lo", "ci_hi"]].copy()
    observed["family"] = "data"
    seeds = pd.concat(
        [
            pd.read_csv(BASELINE_ONSET).query("family == @BASELINE"),
            pd.read_csv(weighted_dir / "onset/model_readout_by_seed.csv"),
        ], ignore_index=True,
    )
    rows = []
    for record in seeds.itertuples():
        for stage in [1, 2, 3]:
            rows.append(
                {"family": record.family, "seed": record.seed, "stage_index": stage,
                 "influence": record.w_middle + record.slope_per_stage * (stage - 2)}
            )
    seed_curves = pd.DataFrame(rows)
    summary = seed_curves.groupby(["family", "stage_index"], as_index=False).influence.agg(
        ["mean", "min", "max"]
    ).reset_index().rename(columns={"mean": "influence", "min": "ci_lo", "max": "ci_hi"})
    return pd.concat([observed, summary], ignore_index=True), seeds


def persistence(weighted_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed = pd.read_csv(FIG4 / "fig4_D_dilution_adjustment.csv")
    observed = observed[observed.bin.between(1, 6)][
        ["bin", "lo_s", "hi_s", "gammaT", "lo", "hi"]
    ].rename(columns={"lo": "ci_lo", "hi": "ci_hi"})
    observed["family"] = "data"
    baseline = pd.read_csv(BASELINE_PERSISTENCE).query(
        "family == @BASELINE and scope == 'all_coherences' and bin.between(1, 6)"
    )
    weighted = pd.read_csv(weighted_dir / "persistence/all_readouts.csv").query(
        "family != 'data' and scope == 'all_coherences' and bin.between(1, 6)"
    )
    seeds = pd.concat([baseline, weighted], ignore_index=True)
    summary = seeds.groupby(["family", "bin", "lo_s", "hi_s"], as_index=False).gammaT.agg(
        ["mean", "min", "max"]
    ).reset_index().rename(columns={"mean": "gammaT", "min": "ci_lo", "max": "ci_hi"})
    return pd.concat([observed, summary], ignore_index=True), seeds


def adequacy(
    score_dir: Path, weighted_dir: Path, choice_summary: pd.DataFrame,
    onset_seeds: pd.DataFrame, persistence_seeds: pd.DataFrame,
) -> pd.DataFrame:
    heldout = pd.read_csv(score_dir / "pareto_summary.csv").set_index("family")
    b = heldout.loc[BASELINE]
    observed_persistence = pd.read_csv(FIG4 / "fig4_D_dilution_adjustment.csv")
    observed_persistence = observed_persistence[observed_persistence.bin.between(1, 6)].set_index("bin").gammaT
    observed_slope = float(
        pd.read_csv(OBSERVED_ONSET_COEFFICIENTS)
        .query("comparison == 'all_available_10' and objective == 'wls' and parameter == 'direction_time_offset'")
        .estimate.iloc[0]
    )
    records = []
    for family in ORDER:
        onset_family = onset_seeds[onset_seeds.family.eq(family)]
        persistence_family = persistence_seeds[persistence_seeds.family.eq(family)]
        rmse = []
        for _, group in persistence_family.groupby("seed"):
            curve = group.set_index("bin").gammaT.loc[observed_persistence.index]
            rmse.append(float(np.sqrt(np.mean((curve - observed_persistence) ** 2))))
        max_nonresponse = np.nan
        if family != BASELINE:
            values = []
            for path in (weighted_dir / "persistence/cache").glob(f"{family}_*_seed*_r30.pkl"):
                with path.open("rb") as stream:
                    values.append(pickle.load(stream)["simulated_nonresponse_fraction"])
            assert len(values) == 20
            max_nonresponse = max(values)
        records.append(
            {
                "family": family,
                "label": LABELS[family],
                "full_fit_choice_contrast": choice_summary.set_index("family").loc[family, "mean"],
                "heldout_choice_delta_nll": heldout.loc[family, "choice_nll"] - b.choice_nll,
                "heldout_rt_delta_nll": heldout.loc[family, "rt_nll"] - b.rt_nll,
                "heldout_joint_delta_nll": heldout.loc[family, "joint_nll"] - b.joint_nll,
                "onset_slope": onset_family.slope_per_stage.mean(),
                "onset_slope_error": abs(onset_family.slope_per_stage.mean() - observed_slope),
                "persistence_rmse": np.mean(rmse),
                "max_simulated_nonresponse": max_nonresponse,
            }
        )
    return pd.DataFrame(records)


def render(
    choice: pd.DataFrame, onset_frame: pd.DataFrame, persistence_frame: pd.DataFrame,
    output: Path,
) -> None:
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 3, figsize=(180 / 25.4, 88 / 25.4))
        fig.subplots_adjust(left=0.075, right=0.985, bottom=0.34, top=0.67, wspace=0.42)

        ax = axes[0]
        x = np.arange(len(ORDER))
        data = choice[choice.family.eq("data")].iloc[0]
        ax.axhspan(data.ci_lo, data.ci_hi, color="black", alpha=0.08, linewidth=0)
        ax.axhline(data["mean"], color="black", lw=1.05, label="Observed mean ± 95% CI")
        models = choice.set_index("family").loc[ORDER]
        y = models["mean"].to_numpy()
        ax.errorbar(
            x, y, yerr=[y - models.ci_lo.to_numpy(), models.ci_hi.to_numpy() - y],
            fmt="none", ecolor="0.45", elinewidth=0.8, capsize=2, zorder=2,
        )
        for i, family in enumerate(ORDER):
            ax.plot(i, y[i], "o", color=COLORS[family], ms=4.2, zorder=3)
        ax.plot(x, y, color="0.55", lw=0.8, zorder=1)
        ax.set(xticks=x, xticklabels=[LABELS[f] for f in ORDER],
               ylabel="Pulse-direction contrast\nΔP(right)",
               xlabel="Relative choice weight")
        ax.tick_params(axis="x", labelrotation=25)
        ax.set_title("Pulse-direction choice effect", loc="left", fontsize=7.4)

        ax = axes[1]
        data = onset_frame[onset_frame.family.eq("data")].sort_values("stage_index")
        stages = data.stage_index.to_numpy()
        ax.errorbar(stages, data.influence,
                    yerr=[data.influence - data.ci_lo, data.ci_hi - data.influence],
                    fmt="o-", color="black", lw=1.1, ms=3.4, capsize=2, label="Observed")
        for family in ORDER:
            group = onset_frame[onset_frame.family.eq(family)].sort_values("stage_index")
            style = "--" if family.endswith("choice_only") else "-"
            ax.plot(stages, group.influence, style, color=COLORS[family], marker="o", ms=2.8,
                    lw=1.05, label=LABELS[family])
        ax.axhline(0, color="0.8", lw=0.55)
        ax.set(xticks=[1, 2, 3], xticklabels=["Early", "Middle", "Late"],
               xlabel="Pulse onset stage", ylabel="Pulse influence\n(% coherence equivalent)")
        ax.set_title("Influence across onset", loc="left", fontsize=7.4)

        ax = axes[2]
        data = persistence_frame[persistence_frame.family.eq("data")].sort_values("bin")
        xx = np.arange(len(data))
        ax.errorbar(xx, data.gammaT, yerr=[data.gammaT - data.ci_lo, data.ci_hi - data.gammaT],
                    fmt="o-", color="black", lw=1.1, ms=3.4, capsize=2)
        for family in ORDER:
            group = persistence_frame[persistence_frame.family.eq(family)].sort_values("bin")
            style = "--" if family.endswith("choice_only") else "-"
            ax.plot(xx, group.gammaT, style, color=COLORS[family], marker="o", ms=2.6, lw=1.0)
        ax.axhline(0, color="0.8", lw=0.55)
        ax.set(xticks=xx, xticklabels=[f"{a:g}–{b:g}" for a, b in zip(data.lo_s, data.hi_s)],
               xlabel="Pulse-to-response bin (s)",
               ylabel="Dilution-adjusted influence\nγT (% coherence × s)")
        ax.tick_params(axis="x", labelrotation=35)
        ax.set_title("Influence across response time", loc="left", fontsize=7.4)

        for letter, ax in zip("ABC", axes):
            ax.text(-0.18, 1.08, letter, transform=ax.transAxes, fontweight="bold", fontsize=9)
        fig.text(0.035, 0.965, "Choice weighting does not rescue all pulse signatures", fontsize=9.3, va="top")
        fig.text(0.035, 0.89, "Fixed full-pulse fits; same descriptive readouts and trial selections as Figure 7B",
                 fontsize=6.4, color="0.25", va="top")
        handles, labels = axes[1].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.53, 0.075), ncol=6,
                   fontsize=5.4, handlelength=2.0, columnspacing=1.2)
        fig.text(0.075, 0.018,
                 "Model curves: mean of independent simulation seeds. Choice only is dashed; model uncertainty is not animal uncertainty.",
                 fontsize=5.2, color="0.3")
        for ext in ["png", "pdf", "svg"]:
            fig.savefig(output / f"choice_weight_figure7.{ext}", dpi=300, facecolor="white")
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--score-dir", type=Path, required=True)
    parser.add_argument("--weighted-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    choice_mouse, choice_summary = choice_contrast(args.score_dir)
    onset_frame, onset_seeds = onset(args.weighted_dir)
    persistence_frame, persistence_seeds = persistence(args.weighted_dir)
    table = adequacy(args.score_dir, args.weighted_dir, choice_summary, onset_seeds, persistence_seeds)
    choice_mouse.to_csv(args.output / "panel_A_choice_contrast_by_mouse.csv", index=False)
    choice_summary.to_csv(args.output / "panel_A_choice_contrast_summary.csv", index=False)
    onset_frame.to_csv(args.output / "panel_B_onset_curves.csv", index=False)
    onset_seeds.to_csv(args.output / "panel_B_onset_seed_readouts.csv", index=False)
    persistence_frame.to_csv(args.output / "panel_C_persistence_curves.csv", index=False)
    persistence_seeds.to_csv(args.output / "panel_C_persistence_seed_readouts.csv", index=False)
    table.to_csv(args.output / "adequacy_summary.csv", index=False)
    render(choice_summary, onset_frame, persistence_frame, args.output)
    manifest = {
        "decision_model_refit": False,
        "panel_A": "Full-fit simulated choice probabilities; matched direction contrast averaged across coherence and onset stage within mouse; 95% t interval across 10 mice.",
        "panel_B": "Figure 4C ordinal readout; 30 repetitions and two independent seeds.",
        "panel_C": "Figure 4D dilution-adjusted readout; 30 repetitions and two independent seeds.",
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
