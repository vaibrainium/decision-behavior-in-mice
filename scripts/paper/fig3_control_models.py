"""Figure 3: control trials favour the tested accumulator.

Panels B-C read held-out control-CV scores from saved fit objects.  Panel D
simulates the final all-trial fit on each mouse's own control inputs with a
fixed seed; it is explicitly descriptive/in-sample and is kept visually
separate from the held-out comparisons.

Usage
-----
    python -m scripts.paper.fig3_control_models
"""

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import CENSOR_AT, LIKELIHOOD_PARAMS, MIN_RT, MouseDDM, load_inputs, make_params, select
from scripts.paper.style import FULL_WIDTH, LEFT_COLOR, MM, NEUTRAL_COLOR, OUT_DIR, RIGHT_COLOR, apply_style, label_panel, save_publication

PROCESSED = Path(dir_config.data.processed)
DDM = PROCESSED / "ddm"
FOLDS = [f"ccv{k}" for k in range(5)]
MICE = ["DBM5", "DBM6", "DBM12", "DBM13", "DBM14", "DBM15", "PSUIM5", "PSUIM6", "PSUIM7", "PSUIM10"]
STRICT = "L0U0V1Z0G1"
EXTREMA = "L1U0V1Z0G1"
N_REPS = 20


def fit_score(folder, mouse, variant):
    values = []
    for split in FOLDS:
        path = DDM / folder / f"{mouse}_{variant}_{split}.pkl"
        with path.open("rb") as f:
            fit = pickle.load(f)
        values.append(float(fit["test_nll"]))
    return sum(values)


def score_tables():
    component_variants = {
        "Remove sv": "L0U0V0Z0G1",
        "Remove fast guesses": "L0U0V1Z0G0",
        "Add leak": "L1U0V1Z0G1",
        "Add urgency": "L0U1V1Z0G1",
        "Add leak + urgency": "L1U1V1Z0G1",
    }
    strategy, components = [], []
    for mouse in MICE:
        base = fit_score("fits_guess_fast_only", mouse, STRICT)
        e = fit_score("fits_guess_fast_only_leak20-200", mouse, EXTREMA)
        strategy.append({"mouse": mouse, "rig": "UCLA" if mouse.startswith("PSUIM") else "UW",
                         "delta_nll": e-base})
        for label, variant in component_variants.items():
            value = fit_score("fits_guess_fast_only", mouse, variant) - base
            components.append({"mouse": mouse, "comparison": label, "variant": variant, "delta_nll": value})
    return pd.DataFrame(strategy), pd.DataFrame(components)


def box(ax, xy, width, height, text, fc="white", ec="0.35"):
    p = FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.02", fc=fc, ec=ec, lw=0.8)
    ax.add_patch(p)
    ax.text(xy[0]+width/2, xy[1]+height/2, text, ha="center", va="center", fontsize=6.4)


def arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=7, lw=0.8, color="0.35"))


def panel_schematic(ax):
    ax.set_axis_off()
    box(ax, (0.02, 0.38), 0.18, 0.24, "Reconstructed\nmotion energy", fc="#F3F3F3")
    box(ax, (0.30, 0.64), 0.22, 0.22, "Accumulator\n(no leak)", fc="#DCEEF8", ec=LEFT_COLOR)
    box(ax, (0.30, 0.14), 0.22, 0.22, "Rapid forgetting\n(leak 20–200 s⁻¹)", fc="#FCE4D6", ec=RIGHT_COLOR)
    box(ax, (0.62, 0.38), 0.15, 0.24, "Bound\ncrossing")
    box(ax, (0.84, 0.38), 0.14, 0.24, "Choice, RT,\nno response")
    arrow(ax, (0.20, 0.50), (0.30, 0.75)); arrow(ax, (0.20, 0.50), (0.30, 0.25))
    arrow(ax, (0.52, 0.75), (0.62, 0.54)); arrow(ax, (0.52, 0.25), (0.62, 0.46)); arrow(ax, (0.77, 0.50), (0.84, 0.50))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title("Candidate control-trial models", loc="left")


def panel_strategy(ax, strategy):
    d = strategy.set_index("mouse").loc[MICE].reset_index()
    y = np.arange(len(d))[::-1]
    for rig, marker in (("UW", "s"), ("UCLA", "o")):
        q = d.rig.eq(rig)
        ax.scatter(d.loc[q, "delta_nll"], y[q], marker=marker, s=22, facecolor="white",
                   edgecolor=NEUTRAL_COLOR, lw=0.8, label=rig, zorder=3)
    ax.axvline(0, color="0.5", lw=0.8)
    ax.axvline(10, color="0.65", lw=0.7, ls="--")
    ax.axvline(-10, color="0.65", lw=0.7, ls="--")
    ax.set_yticks(y, d.mouse)
    ax.set_xlabel("Held-out NLL: rapid forgetting − accumulator")
    ax.set_title("Per-mouse strategy comparison", loc="left")
    ax.text(0.98, 0.98, f"sum = {d.delta_nll.sum():.1f}; 6/10 > 10",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.2)
    ax.text(0.98, 0.06, "positive favours accumulator", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6.0, color="0.3")


def component_axis(ax, components, labels, title):
    colors = [LEFT_COLOR, RIGHT_COLOR, "#009E73"]
    for i, label in enumerate(labels):
        d = components[components.comparison == label]
        ax.scatter(np.full(len(d), i), d.delta_nll, s=12, facecolor="white",
                   edgecolor=colors[i % len(colors)], linewidth=0.65, zorder=2)
        ax.scatter(i, d.delta_nll.mean(), marker="D", s=24, color=colors[i % len(colors)], zorder=3)
        ax.text(i, ax.get_ylim()[1] if ax.get_ylim()[1] else 0, "", ha="center")
    ax.axhline(0, color="0.6", lw=0.7)
    display = {
        "Remove sv": "Remove\nsv",
        "Remove fast guesses": "Remove fast\nguesses",
        "Add leak": "Leak",
        "Add urgency": "Urgency",
        "Add leak + urgency": "Leak +\nurgency",
    }
    ax.set_xticks(range(len(labels)), [display[x] for x in labels])
    ax.set_title(title, loc="left")
    for i, label in enumerate(labels):
        total = components.loc[components.comparison == label, "delta_nll"].sum()
        ax.text(i, 0.94, f"Σ {total:+.0f}", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=5.8,
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.5, "alpha": 0.85})


def summarize_frame(df, source, mouse):
    rows = []
    responded = df[df.choice >= 0].copy()
    responded["correct"] = np.where(responded.coh == 0, np.nan, (responded.choice == 1) == (responded.coh > 0))
    for coh, q in responded.groupby("coh"):
        rows.append({"mouse": mouse, "source": source, "metric": "p_right", "x": coh,
                     "value": q.choice.mean(), "n": len(q)})
    responded["abs_coh"] = responded.coh.abs()
    for outcome, q0 in (("rt_correct", responded[(responded.correct == 1) | (responded.coh == 0)]),
                        ("rt_error", responded[responded.correct == 0])):
        for coh, q in q0.groupby("abs_coh"):
            rows.append({"mouse": mouse, "source": source, "metric": outcome, "x": coh,
                         "value": q.rt.mean(), "n": len(q)})
    for coh, q in df.groupby("coh"):
        rows.append({"mouse": mouse, "source": source, "metric": "p_no_response", "x": coh,
                     "value": (q.choice == -1).mean(), "n": len(q)})
    return rows


def fit_quality_table():
    inputs = load_inputs(DDM / "ddm_inputs_global.npz")
    rows = []
    for mouse in MICE:
        idx = np.flatnonzero((inputs["subject_id"] == mouse) & (inputs["sched_pulse_type"] == 0))
        rig = str(np.unique(inputs["data_source"][idx])[0])
        data, stim = select(inputs, idx)
        with (DDM / "fits_final" / f"{mouse}_{STRICT}_all.pkl").open("rb") as f:
            params = pickle.load(f)["parameters"]
        free, fixed = make_params(STRICT, "fast_only")
        model = MouseDDM(free, fixed, device="cpu", likelihood_params=LIKELIHOOD_PARAMS,
                         censor_at=CENSOR_AT, min_rt=MIN_RT[rig])
        sim = model._map_outcomes(model.simulate(stim, params, n_reps=N_REPS, seed=0, labels=data["condition"]))
        coh = inputs["signed_coherence"][idx] * 100
        observed = pd.DataFrame({"coh": coh, "rt": data["rt"], "choice": data["choice"]})
        predicted = pd.DataFrame({"coh": coh[sim["trial"].to_numpy()], "rt": sim["rt"].to_numpy(),
                                  "choice": sim["choice"].to_numpy().astype(int)})
        rows += summarize_frame(observed, "Observed", mouse)
        rows += summarize_frame(predicted, "Model", mouse)
    out = pd.DataFrame(rows)
    # Error-RT cells are displayed only where the observed mouse/coherence cell has at least five errors.
    ok = out[(out.source == "Observed") & (out.metric == "rt_error") & (out.n >= 5)][["mouse", "x"]]
    ok_keys = set(map(tuple, ok.to_numpy()))
    keep_error = out.apply(lambda r: r.metric != "rt_error" or (r.mouse, r.x) in ok_keys, axis=1)
    return out[keep_error].reset_index(drop=True)


def load_or_simulate_quality():
    cached = sorted(OUT_DIR.glob("fig3_control_models_*_source_fit_quality.csv"))
    if cached:
        print(f"using deterministic fit-quality cache: {cached[-1]}")
        return pd.read_csv(cached[-1])
    return fit_quality_table()


def group_summary(table, metric):
    q = table[table.metric == metric]
    g = q.groupby(["source", "x"]).value.agg(["mean", "sem", "count"]).reset_index()
    return g


def panel_fit_quality(axes, table):
    ax_p, ax_rt, ax_n = axes
    for metric, ax, ylabel in (("p_right", ax_p, "P(right)"), ("p_no_response", ax_n, "P(no response by 5 s)")):
        g = group_summary(table, metric)
        for source, color, marker, ls in (("Observed", "black", "o", "none"), ("Model", LEFT_COLOR, None, "-")):
            d = g[g.source == source]
            if source == "Observed":
                ax.errorbar(d.x, d["mean"], yerr=d["sem"], fmt=marker, color=color, ms=3.2,
                            capsize=1.5, elinewidth=0.7, label=source)
            else:
                ax.plot(d.x, d["mean"], color=color, ls=ls, lw=1.2, label=source)
        ax.set_xlabel("Signed coherence (%)")
        ax.set_ylabel(ylabel)
        ax.set_xticks([-100, -36, 0, 36, 100])
    for metric, color, marker, label in (("rt_correct", "#009E73", "o", "Correct"),
                                          ("rt_error", RIGHT_COLOR, "s", "Error")):
        g = group_summary(table, metric)
        for source, ls in (("Observed", "none"), ("Model", "-")):
            d = g[g.source == source]
            if source == "Observed":
                ax_rt.errorbar(d.x, d["mean"], yerr=d["sem"], fmt=marker, color=color, mfc="white" if metric == "rt_error" else color,
                               ms=3.2, capsize=1.5, elinewidth=0.7, label=f"{label}, data")
            else:
                ax_rt.plot(d.x, d["mean"], color=color, ls=ls, lw=1.2, label=f"{label}, model")
    ax_rt.set_xlabel("|Coherence| (%)"); ax_rt.set_ylabel("Mean response time (s)")
    ax_p.set_title("Choice", loc="left"); ax_rt.set_title("Response time", loc="left"); ax_n.set_title("No response", loc="left")
    ax_p.legend(loc="lower right", handlelength=1.2)
    ax_rt.legend(loc="upper right", ncols=2, fontsize=5.5, handlelength=1.1, columnspacing=0.6)
    ax_n.set_ylim(bottom=0)


def main():
    apply_style()
    strategy, components = score_tables()
    quality = load_or_simulate_quality()

    fig = plt.figure(figsize=(FULL_WIDTH, 178*MM))
    outer = fig.add_gridspec(3, 6, height_ratios=[0.78, 0.82, 1.0],
                             left=0.08, right=0.98, bottom=0.08, top=0.96,
                             hspace=0.78, wspace=1.15)
    ax_a = fig.add_subplot(outer[0, 0:3]); ax_b = fig.add_subplot(outer[0, 3:6])
    ax_c1 = fig.add_subplot(outer[1, 0:3]); ax_c2 = fig.add_subplot(outer[1, 3:6])
    dax = [fig.add_subplot(outer[2, 0:2]), fig.add_subplot(outer[2, 2:4]), fig.add_subplot(outer[2, 4:6])]

    panel_schematic(ax_a); panel_strategy(ax_b, strategy)
    component_axis(ax_c1, components, ["Remove sv", "Remove fast guesses"], "Required components")
    component_axis(ax_c2, components, ["Add leak", "Add urgency", "Add leak + urgency"], "Extra dynamics")
    ax_c1.set_ylabel("Held-out NLL: comparator − strict model")
    ax_c2.set_ylabel("Held-out NLL: extension − strict model")
    ax_c1.set_ylim(-30, 540); ax_c2.set_ylim(-50, 22)
    panel_fit_quality(dax, quality)
    dax[0].text(-0.10, 1.28, "Final-fit quality on control trials (descriptive; in-sample)",
                transform=dax[0].transAxes, ha="left", va="bottom", fontsize=7.5)
    for letter, ax, x in (("A", ax_a, -0.10), ("B", ax_b, -0.25), ("C", ax_c1, -0.18), ("D", dax[0], -0.25)):
        label_panel(ax, letter, x=x, y=1.10 if letter != "D" else 1.25)

    base = save_publication(fig, "fig3_control_models")
    strategy.to_csv(base.with_name(base.name + "_source_strategy.csv"), index=False)
    components.to_csv(base.with_name(base.name + "_source_components.csv"), index=False)
    quality.to_csv(base.with_name(base.name + "_source_fit_quality.csv"), index=False)
    print(f"strategy sum E-C: {strategy.delta_nll.sum():.3f}; >10: {(strategy.delta_nll > 10).sum()}/10")
    print("component sums:", components.groupby("comparison").delta_nll.sum().round(3).to_dict())
    print(f"fit-quality source rows: {len(quality)}; simulation repetitions per control trial: {N_REPS}")


if __name__ == "__main__":
    main()
