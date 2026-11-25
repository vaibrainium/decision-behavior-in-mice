"""Render matched Figure 7 model checks for the Figure 6a/6b winners.

No decision-model parameters are fitted here.  Panel A pools saved fit-browser
predictions over pulse stages on support matched to the displayed observations.
Panel B applies the Figure 4C ordinal readout to fixed-parameter simulations.
Panel C reuses the Figure 4D dilution estimator applied to fixed-parameter
simulations, with the response-time bins shown categorically.
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


BASE = Path("dissemination/paper_accumulation/draft_2026-11-15")
BROWSER = Path("dissemination/figures/qc/fit_browser_2026-11-12_v7.json")
FIG4 = BASE / "figure4_final_2026-11-18/source_data"
DYNAMICS = Path("dissemination/pulse_dynamics_2026-11-13/all_readouts.csv")
ONSET = {
    "power_leak_urgency": BASE / "figure7_model_checks_2026-11-25/onset_stage_simulations/model_readout_by_seed.csv",
    "pulse_norm_ugm_no_sv": BASE / "pulse_model_primacy_2026-11-18/model_readout_by_seed.csv",
}
MODELS = {
    "7a": {
        "family": "power_leak_urgency",
        "label": "Power-law input + leak + urgency, with sᵥ",
        "scope": "all-trial fit",
        "color": "#6A51A3",
    },
    "7b": {
        "family": "pulse_norm_ugm_no_sv",
        "label": "Normalized input + urgency-gating region, no sᵥ",
        "scope": "pulse-only fit",
        "color": "#238B45",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choice_curves(family: str) -> pd.DataFrame:
    browser = json.loads(BROWSER.read_text())
    assert family in browser["families"]
    parts = []
    for source, tables in [("data", browser["data"]), ("model", browser["families"][family])]:
        for mouse in browser["mice"]:
            d = pd.DataFrame(tables[mouse]["rows"], columns=browser["columns"])
            d["mouse"] = mouse
            d["source"] = source
            parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    d = d[d.cond.ne("control")].copy()
    d["direction"] = d.cond.str.split().str[-1].map({"left": -1, "right": 1})
    assert d.direction.notna().all()
    d["count_right"] = d.p * d.n
    mouse = (
        d.groupby(["source", "mouse", "coh", "direction"], as_index=False)
        .agg(count_right=("count_right", "sum"), n=("n", "sum"))
    )
    mouse["p_right"] = mouse.count_right / mouse.n
    keys = ["mouse", "coh", "direction"]
    support = mouse[mouse.source.eq("data")][keys].merge(
        mouse[mouse.source.eq("model")][keys], on=keys, how="outer", indicator=True
    )
    assert support._merge.eq("both").all()
    group = (
        mouse.groupby(["source", "coh", "direction"], as_index=False)
        .agg(p_right=("p_right", "mean"), sem=("p_right", "sem"), n_mice=("mouse", "nunique"), n=("n", "sum"))
    )
    return group.sort_values(["source", "direction", "coh"])


def onset_curves(family: str) -> pd.DataFrame:
    observed = pd.read_csv(FIG4 / "fig4_C_timing_curves.csv")
    observed = observed[
        observed.comparison.eq("all_available_10")
        & observed.objective.eq("wls")
        & observed.stage_index.isin([1.0, 2.0, 3.0])
    ][["stage_index", "influence", "ci_lo", "ci_hi"]].copy()
    observed["source"] = "data"
    predicted = pd.read_csv(ONSET[family])
    predicted = predicted[predicted.family.eq(family)]
    rows = []
    for r in predicted.itertuples():
        for stage in [1, 2, 3]:
            rows.append({
                "stage_index": stage,
                "influence": r.w_middle + r.slope_per_stage * (stage - 2),
                "seed": r.seed,
            })
    seeds = pd.DataFrame(rows)
    summary = seeds.groupby("stage_index", as_index=False).influence.agg(["mean", "min", "max"]).reset_index()
    summary = summary.rename(columns={"mean": "influence", "min": "ci_lo", "max": "ci_hi"})
    summary["source"] = "model"
    return pd.concat([observed, summary], ignore_index=True), seeds


def persistence_curves(family: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed = pd.read_csv(FIG4 / "fig4_D_dilution_adjustment.csv")
    observed = observed[observed.bin.between(1, 6)][["bin", "lo_s", "hi_s", "gammaT", "lo", "hi"]].copy()
    observed = observed.rename(columns={"lo": "ci_lo", "hi": "ci_hi"})
    observed["source"] = "data"
    seeds = pd.read_csv(DYNAMICS)
    seeds = seeds[
        seeds.family.eq(family) & seeds.scope.eq("all_coherences") & seeds.bin.between(1, 6)
    ][["family", "seed", "bin", "lo_s", "hi_s", "gammaT"]].copy()
    assert seeds.seed.nunique() == 2 and seeds.groupby("seed").size().eq(6).all()
    summary = (
        seeds.groupby(["bin", "lo_s", "hi_s"], as_index=False).gammaT
        .agg(["mean", "min", "max"]).reset_index()
        .rename(columns={"mean": "gammaT", "min": "ci_lo", "max": "ci_hi"})
    )
    summary["source"] = "model"
    return pd.concat([observed, summary], ignore_index=True), seeds


def render(variation: str, output: Path) -> None:
    spec = MODELS[variation]
    family, color = spec["family"], spec["color"]
    choice = choice_curves(family)
    onset, onset_seeds = onset_curves(family)
    persistence, persistence_seeds = persistence_curves(family)
    output.mkdir(parents=True, exist_ok=False)
    choice.to_csv(output / "panel_A_choice_curves.csv", index=False)
    onset.to_csv(output / "panel_B_onset_summary.csv", index=False)
    onset_seeds.to_csv(output / "panel_B_onset_seed_readouts.csv", index=False)
    persistence.to_csv(output / "panel_C_persistence_summary.csv", index=False)
    persistence_seeds.to_csv(output / "panel_C_persistence_seed_readouts.csv", index=False)

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 3, figsize=(180 / 25.4, 70 / 25.4))
        fig.subplots_adjust(left=.075, right=.985, bottom=.26, top=.73, wspace=.42)

        ax = axes[0]
        for direction, data_color, marker, label in [
            (-1, BLUE, "v", "Left pulse"), (1, ORANGE, "^", "Right pulse")
        ]:
            data = choice[choice.source.eq("data") & choice.direction.eq(direction)].sort_values("coh")
            model = choice[choice.source.eq("model") & choice.direction.eq(direction)].sort_values("coh")
            assert data.coh.tolist() == model.coh.tolist()
            ax.errorbar(data.coh, data.p_right, yerr=data["sem"], fmt=marker, color=data_color,
                        ls="none", ms=3.3, capsize=1.5, zorder=4)
            ax.plot(model.coh, model.p_right, "-D", color=data_color, mfc="white", mec=data_color,
                    mew=.75, ms=2.8, lw=1.2)
        ax.axhline(.5, color=".85", lw=.55, zorder=0)
        ax.set(xlim=(-110, 110), ylim=(0, 1), xticks=[-100, -36, 0, 36, 100],
               xlabel="Signed baseline coherence (%)", ylabel="P(right response)")
        ax.set_title("Pulse direction shifts choices", loc="left", fontsize=7.4)

        ax = axes[1]
        data = onset[onset.source.eq("data")].sort_values("stage_index")
        model = onset[onset.source.eq("model")].sort_values("stage_index")
        x = data.stage_index.to_numpy()
        ax.errorbar(x, data.influence, yerr=[data.influence-data.ci_lo, data.ci_hi-data.influence],
                    fmt="o-", color="black", lw=1.0, ms=3.3, capsize=2, label="Data ± 95% CI")
        ax.fill_between(x, model.ci_lo, model.ci_hi, color=color, alpha=.14, linewidth=0)
        ax.plot(x, model.influence, "-D", color=color, mfc="white", mec=color, mew=.8, ms=3.1, lw=1.25,
                label="Model mean; two-seed range")
        ax.axhline(0, color=".8", lw=.55)
        ax.set(xticks=[1, 2, 3], xticklabels=["Early", "Middle", "Late"],
               xlabel="Pulse onset stage", ylabel="Pulse influence\n(% coherence equivalent)", ylim=(-2, 21))
        ax.set_title("Influence across pulse onset", loc="left", fontsize=7.4)

        ax = axes[2]
        data = persistence[persistence.source.eq("data")].sort_values("bin")
        model = persistence[persistence.source.eq("model")].sort_values("bin")
        x = np.arange(len(data))
        ax.errorbar(x, data.gammaT, yerr=[data.gammaT-data.ci_lo, data.ci_hi-data.gammaT],
                    fmt="o-", color="black", lw=1.0, ms=3.3, capsize=2)
        ax.fill_between(x, model.ci_lo, model.ci_hi, color=color, alpha=.14, linewidth=0)
        ax.plot(x, model.gammaT, "-D", color=color, mfc="white", mec=color, mew=.8, ms=3.1, lw=1.25)
        ax.axhline(0, color=".8", lw=.55)
        labels = [f"{a:g}–{b:g}" for a, b in zip(data.lo_s, data.hi_s)]
        ax.set(xticks=x, xticklabels=labels, xlabel="Pulse-to-response bin (s)",
               ylabel="Dilution-adjusted influence\nγT (% coherence × s)", ylim=(-24, 27))
        ax.tick_params(axis="x", labelrotation=35)
        ax.set_title("Influence across response time", loc="left", fontsize=7.4)

        for letter, ax in zip("ABC", axes):
            ax.text(-.18, 1.10, letter, transform=ax.transAxes, fontweight="bold", fontsize=9)
        fig.text(.035, .96, f"Figure {variation.upper()} | Fixed-parameter pulse predictions", fontsize=9.3, va="top")
        fig.text(.035, .895, f"{spec['label']}  ·  {spec['scope']}", fontsize=6.7, color=color, va="top")
        handles = [
            Line2D([], [], color="black", marker="o", lw=1, label="Observed data"),
            Line2D([], [], color=color, marker="D", mfc="white", lw=1.25, label="Fixed-parameter model"),
            Line2D([], [], color=BLUE, marker="v", ls="none", label="Left pulse (A)"),
            Line2D([], [], color=ORANGE, marker="^", ls="none", label="Right pulse (A)"),
        ]
        fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.52, .075), ncol=4,
                   fontsize=5.8, columnspacing=1.5, handlelength=2.2)
        fig.text(.075, .018,
                 "Panel-specific trial selections. B–C model bands: two-seed simulation range, not animal uncertainty.",
                 fontsize=5.35, color=".3")
        for ext in ["png", "pdf", "svg"]:
            fig.savefig(output / f"figure_{variation}.{ext}", dpi=300, facecolor="white")
        plt.close(fig)

    manifest = {
        "variation": variation,
        "model": spec,
        "decision_model_refit": False,
        "panel_A": "Saved fit-browser predictions; direct model points connected at tested coherences; pulse stages pooled within mouse using cell counts.",
        "panel_B": "Same 21-parameter WLS ordinal descriptive readout as Figure 4C; 30 repetitions x 2 independent seeds.",
        "panel_C": "Same grouped-binomial dilution readout as Figure 4D; bins 0.3-5 s; 30 repetitions x 2 independent seeds.",
        "source_sha256": {str(p): sha256(p) for p in [BROWSER, FIG4 / "fig4_C_timing_curves.csv", FIG4 / "fig4_D_dilution_adjustment.csv", DYNAMICS, ONSET[family], Path(__file__)]},
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "caption.md").write_text(
        f"**Figure {variation.upper()} variation | Fixed-parameter pulse predictions from the {spec['scope']}.** "
        "**(A)** Observed choice proportions (filled markers; between-mouse SEM) and model-predicted proportions "
        "(open diamonds connected across tested coherences), pooled over pulse stages. "
        "**(B)** Pulse influence across early, middle and late onset stages, estimated with the same descriptive "
        "ordinal regression used in Figure 4C. Black intervals are observed 95% confidence intervals; the model "
        "band spans two independent simulation seeds. **(C)** Coherence-equivalent pulse influence multiplied by "
        "mean response time, estimated in the Figure 4D response-time bins. Model bands again show only two-seed "
        "simulation variation. Decision-model parameters were held fixed throughout; the panels use the original "
        "panel-specific trial selections and therefore do not constitute one common trial population.\n"
    )


def main() -> None:
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("--variation", choices=MODELS, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    render(a.variation, a.output)


if __name__ == "__main__":
    main()
