"""Psychometric functions for control, congruent and incongruent pulse trials: observed vs every responded-only model
variant fitted to control trials (plan .agents/plans/2026-10-27-pulse-psychometric-variants.md).

Responded trials only. Congruent = scheduled pulse toward the trial's coherence, incongruent = against it (0% pulses are
on neither curve). Model P(right | response) per trial: saved frozen pulse predictions where they exist
(primacy_resp, primacy_revised_resp), otherwise simulated here with primacy.predict_mouse (200 reps, seed 0) from the
variant's control fit; control trials are simulated for every base variant. Pulse-gain variants share their base
variant's control predictions (no pulse, so the gain does nothing). Mouse is the unit: cell means per mouse, then mean
+- SEM over mice.

Outputs: <processed>/ddm/pulse_psychometric_resp/<variant>/<mouse>.pkl (simulation cache),
         dissemination/figures/qc/pulse_psychometric_variants_<date>.{png,pdf} and _cells.csv, _effects.csv
Usage: python -m scripts.ddm.pulse_psychometric
"""

import pickle
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import EXTREMA_LEAK_BOUNDS, load_inputs, responded_only
from scripts.ddm.primacy import load_fit, predict_mouse

PROCESSED = Path(dir_config.data.processed)
CACHE = PROCESSED / "ddm" / "pulse_psychometric_resp"
OUT = Path(__file__).resolve().parents[2] / "dissemination" / "figures" / "qc"
N_REPS, SEED = 200, 0

# name: (fit dir, variant, leak bounds, extrema samples, saved pulse predictions or None, base variant for control trials)
VARIANTS = {
    "primary (accumulator)": ("fits_resp_final", "L0U0V1Z0G1", None, False, "primacy_resp/primary", None),
    "secondary (+ leak, urgency)": ("fits_resp_final", "L1U1V1Z0G1", None, False, "primacy_resp/secondary", None),
    "primary + pulse gain (CV)": (None, None, None, False, "primacy_revised_resp/primary", "primary (accumulator)"),
    "secondary + pulse gain (CV)": (None, None, None, False, "primacy_revised_resp/secondary", "secondary (+ leak, urgency)"),
    "E: rapid forgetting (leak 20-200)": ("fits_resp_fast_only_leak20-200_cap", "L1U0V1Z0G1", tuple(EXTREMA_LEAK_BOUNDS), False, None, None),
    "ES: extrema samples": ("fits_resp_fast_only_es_cap", "L0U0V1Z0G1", None, True, "primacy_resp/extrema_samples", None),
    "free leak 0-200": ("fits_resp_fast_only_leak0-200_cap", "L1U0V1Z0G1", (0.0, 200.0), False, None, None),
}
SLUG = {name: "".join(c if c.isalnum() else "_" for c in name).strip("_") for name in VARIANTS}
COLOURS = {"control": "0.3", "congruent": "tab:blue", "incongruent": "tab:red"}


def p_right(trials: pd.DataFrame) -> pd.Series:
    """P(right | response) from p_hat = P(choice in the pulse direction | response); control rows have direction 0, for
    which predict_mouse counts left choices as 'toward'."""
    return pd.Series(np.where(trials.direction > 0, trials.p_hat, 1 - trials.p_hat), index=trials.row.to_numpy())


def simulate(inputs, name, mouse, rows):
    fits_dir, variant, leak, es, _, _ = VARIANTS[name]
    path = CACHE / SLUG[name] / f"{mouse}_{'pulse' if (inputs['sched_pulse_type'][rows] != 0).all() else 'control'}.pkl"
    if path.exists():
        return pickle.load(open(path, "rb"))
    fit = load_fit(PROCESSED / "ddm" / fits_dir, mouse, variant, "control", False, leak, None, responded=True, extrema_samples=es)
    pred = predict_mouse(inputs, mouse, fit["parameters"], variant, N_REPS, SEED, False, leak, rows=rows)
    pred.update(fit_path=str(PROCESSED / "ddm" / fits_dir))
    path.parent.mkdir(parents=True, exist_ok=True)
    pickle.dump(pred, open(path, "wb"))
    return pred


def model_predictions(inputs, mice):
    """{variant: Series of P(right | response) indexed by input row} over control and pulse trials."""
    out = {}
    for name, (fits_dir, _, _, _, saved, base) in VARIANTS.items():
        parts = []
        for mouse in mice:
            m = inputs["subject_id"] == mouse
            pulse_rows = np.flatnonzero(m & (inputs["sched_pulse_type"] != 0))
            if saved:
                pred = pickle.load(open(PROCESSED / "ddm" / saved / f"{mouse}.pkl", "rb"))
                assert pred.get("responded_only") and np.array_equal(pred["trials"].row.to_numpy(), pulse_rows), (name, mouse)
            else:
                pred = simulate(inputs, name, mouse, pulse_rows)
            parts.append(p_right(pred["trials"]))
            if base is None:
                parts.append(p_right(simulate(inputs, name, mouse, np.flatnonzero(m & (inputs["sched_pulse_type"] == 0)))["trials"]))
        out[name] = pd.concat(parts)
    for name, (_, _, _, _, _, base) in VARIANTS.items():
        if base is not None:  # control trials: the base variant's (no pulse, so the gain is irrelevant)
            ctrl = out[base][out[base].index.isin(np.flatnonzero(inputs["sched_pulse_type"] == 0))]
            out[name] = pd.concat([out[name], ctrl])
    return out


def trial_table(inputs):
    sched, coh = inputs["sched_pulse_type"], np.round(inputs["signed_coherence"] * 100).astype(int)
    direction = np.sign(sched)
    category = np.select([direction == 0, (coh != 0) & (direction == np.sign(coh)), (coh != 0) & (direction == -np.sign(coh))],
                         ["control", "congruent", "incongruent"], "zero_coherence_pulse")
    return pd.DataFrame({"mouse": inputs["subject_id"], "coh": coh, "direction": direction, "category": category,
                         "right": (inputs["choice"] == 1).astype(float)})


def cells(t: pd.DataFrame, value: str) -> pd.DataFrame:
    per_mouse = t.groupby(["category", "coh", "mouse"])[value].mean()
    g = per_mouse.groupby(["category", "coh"])
    return pd.DataFrame({"mean": g.mean(), "sem": g.sem(), "n_mice": g.size()}).reset_index()


def effects(t: pd.DataFrame, value: str) -> pd.DataFrame:
    """Per mouse and coherence: pulse - control in P(pulse direction | response), for congruent and incongruent."""
    pm = t.groupby(["mouse", "coh", "category"])[value].mean().unstack("category")
    rows = []
    for cat in ("congruent", "incongruent"):
        sign = np.where(cat == "congruent", 1, -1) * np.sign(pm.index.get_level_values("coh"))  # pulse direction
        d = (sign * (pm[cat] - pm["control"])).dropna()
        rows.append(d.rename("effect").reset_index().assign(category=cat))
    return pd.concat(rows, ignore_index=True)


def main():
    inputs = responded_only(load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz"))
    t = trial_table(inputs)
    t = t[t.category != "zero_coherence_pulse"]
    mice = sorted(np.unique(inputs["subject_id"]))
    preds = model_predictions(inputs, mice)
    for name, p in preds.items():
        assert not p.index.duplicated().any(), name
        t[name] = p.reindex(t.index).to_numpy()
    assert not t[list(VARIANTS)].isna().any().any()

    table, eff = [], []
    for source in ["observed", *VARIANTS]:
        col = "right" if source == "observed" else source
        table.append(cells(t, col).assign(source=source))
        eff.append(effects(t, col).assign(source=source))
    table, eff = pd.concat(table), pd.concat(eff)

    fig, axes = plt.subplots(2, len(VARIANTS), figsize=(2.7 * len(VARIANTS), 6.2), sharey="row", sharex=True)
    obs = table[table.source == "observed"]
    obs_e = eff[eff.source == "observed"].groupby(["category", "coh"]).effect.agg(["mean", "sem"]).reset_index()
    for k, name in enumerate(VARIANTS):
        top, bot = axes[0, k], axes[1, k]
        mod = table[table.source == name]
        mod_e = eff[eff.source == name].groupby(["category", "coh"]).effect.agg(["mean", "sem"]).reset_index()
        for cat, col in COLOURS.items():
            o, m = obs[obs.category == cat].sort_values("coh"), mod[mod.category == cat].sort_values("coh")
            top.errorbar(o.coh, o["mean"], yerr=o["sem"], fmt="o", color=col, ms=3.5, lw=1, label=f"{cat} (data)")
            top.plot(m.coh, m["mean"], color=col, lw=1.5, label=f"{cat} (model)")
            if cat != "control":
                oe, me = obs_e[obs_e.category == cat].sort_values("coh"), mod_e[mod_e.category == cat].sort_values("coh")
                bot.errorbar(oe.coh, 100 * oe["mean"], yerr=100 * oe["sem"], fmt="o", color=col, ms=3.5, lw=1)
                bot.plot(me.coh, 100 * me["mean"], color=col, lw=1.5)
        top.set_title(name, fontsize=8)
        top.axhline(0.5, color="0.8", lw=0.6)
        bot.axhline(0, color="0.6", lw=0.6)
        bot.set_xlabel("signed coherence (%)", fontsize=8)
        for ax in (top, bot):
            ax.tick_params(labelsize=7)
            ax.axvline(0, color="0.9", lw=0.6)
    axes[0, 0].set_ylabel("P(right | response)", fontsize=8)
    axes[1, 0].set_ylabel("pulse − control,\nP(pulse direction) (pp)", fontsize=8)
    axes[0, 0].legend(fontsize=6, frameon=False, loc="upper left")
    fig.suptitle("Pulse psychometric functions, responded trials (points: data, mean ± SEM over 10 mice; lines: model, same trials; "
                 "congruent = pulse toward the coherence, 0% pulses omitted)", fontsize=9)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / f"pulse_psychometric_variants_{date.today().isoformat()}"
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=170, bbox_inches="tight")
    table.round(4).to_csv(f"{stem}_cells.csv", index=False)

    # summary: mean pulse effect over |c| <= 36, per mouse then over mice (pp)
    e = eff[eff.coh.abs() <= 36].groupby(["source", "category", "mouse"]).effect.mean().groupby(["source", "category"]).agg(["mean", "sem"]) * 100
    e.round(2).to_csv(f"{stem}_effects.csv")
    print(e.round(2).unstack("category").reindex(["observed", *VARIANTS]).to_string())
    print(f"saved {stem}.png/.pdf, _cells.csv, _effects.csv")


if __name__ == "__main__":
    main()
