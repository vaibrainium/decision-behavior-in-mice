"""Data-only pulse effect by |coherence| x pulse timing, plus a bootstrap of the held-out model residual in pulse cells.

Effect (per mouse, |coh|, timing): mean over pulse trials of [choice in pulse direction] minus the control-trial
probability of choosing that direction at the same signed coherence (same mouse). Responded trials only (inputs()).
Cohort = equal-mouse mean. Hierarchical bootstrap: resample mice, then trials within mouse (pulse and control).
Residual: (observed - model) P(choice in pulse direction) from choice_g2_by_cell_type cells, bootstrapped the same way
(mice, then binomial resampling of each held-out cell's outcomes), for early x zero/low coherence and the rest.
Usage: python -m scripts.paper.pulse_effect_data_bootstrap --output <new dir> [--n_boot 2000]"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.ddm.rescore_fits import inputs

TIMING = {1: "early", 2: "middle", 3: "late"}


def trial_table():
    x = inputs()
    t = pd.DataFrame({"mouse": x["subject_id"], "coh": np.round(100 * x["signed_coherence"]).astype(int),
                      "pulse": x["sched_pulse_type"], "choice": x["choice"]})
    assert set(np.unique(t.choice)) <= {0, 1}
    return t


def effects(t):
    """Per mouse x |coh| x timing: pulse effect (pp-free proportion) and trial count."""
    ctrl = t[t.pulse == 0].groupby(["mouse", "coh"]).choice.mean()  # P(choice 1 | control, signed coh)
    p = t[t.pulse != 0].copy()
    p["dir"] = np.sign(p.pulse)  # +1: pulse toward choice 1 (checked below at 0% coherence)
    p["follow"] = np.where(p.dir > 0, p.choice, 1 - p.choice)
    base = ctrl.reindex(pd.MultiIndex.from_arrays([p.mouse, p.coh])).to_numpy()
    p["baseline"] = np.where(p.dir > 0, base, 1 - base)
    p = p.dropna(subset=["baseline"])
    p["effect"] = p.follow - p.baseline
    p["abs_coh"], p["timing"] = p.coh.abs(), p.pulse.abs().map(TIMING)
    return p.groupby(["mouse", "abs_coh", "timing"]).agg(effect=("effect", "mean"), n=("effect", "size")).reset_index()


def cohort(e):
    return e.groupby(["abs_coh", "timing"]).effect.mean()  # equal-mouse mean


def boot_data(t, n_boot, rng):
    mice = t.mouse.unique(); by = {m: t[t.mouse == m] for m in mice}; out = []
    for _ in range(n_boot):
        parts = []
        for i, m in enumerate(rng.choice(mice, len(mice))):
            d = by[m]
            parts.append(pd.concat([g.sample(len(g), replace=True, random_state=rng.integers(1 << 31))
                                    for _, g in d.groupby(d.pulse == 0)]).assign(mouse=f"{m}_{i}"))
        out.append(cohort(effects(pd.concat(parts))))
    return pd.concat(out, axis=1)


def residuals(cells, n_boot, rng, families):
    c = cells[cells.family.isin(families)].copy()
    c["group"] = np.where((c.timing == "early") & (c.abs_coh == 0), "early_zero",
                 np.where((c.timing == "early") & c.abs_coh.isin([9, 18]), "early_low", "other"))
    c["dir"] = np.sign(c.pulse)
    mice = c.mouse.unique(); rows = []
    def stat(d):
        follow = np.where(d.dir > 0, d.k_b, d.n - d.k_b); pmod = np.where(d.dir > 0, d.p1, 1 - d.p1) * d.n
        return d.assign(f=follow, m=pmod).groupby(["family", "group"])[["f", "m", "n"]].sum().pipe(lambda s: (s.f - s.m) / s.n)
    point = stat(c.assign(k_b=c.k))
    for _ in range(n_boot):
        pick = rng.choice(mice, len(mice))
        d = pd.concat([c[c.mouse == m] for m in pick])
        d = d.assign(k_b=rng.binomial(d.n.to_numpy(), (d.k / d.n).to_numpy()))
        rows.append(stat(d))
    b = pd.concat(rows, axis=1)
    return pd.DataFrame({"point_pp": 100 * point, "lo_pp": 100 * b.quantile(.025, axis=1), "hi_pp": 100 * b.quantile(.975, axis=1)})


def main(out, n_boot):
    out.mkdir(parents=True, exist_ok=False); rng = np.random.default_rng(20261119)
    t = trial_table()
    z = t[(t.pulse != 0) & (t.coh == 0)]
    print("convention check, 0% coherence P(choice 1) by pulse sign:", z.groupby(np.sign(z.pulse)).choice.mean().round(3).to_dict())
    for tag, d in (("all", t), ("no_PSUIM6_7", t[~t.mouse.isin(["PSUIM6", "PSUIM7"])])):
        e = effects(d); e.to_csv(out / f"effects_per_mouse_{tag}.csv", index=False)
        b = boot_data(d, n_boot, rng)
        s = pd.DataFrame({"effect_pp": 100 * cohort(e), "lo_pp": 100 * b.quantile(.025, axis=1), "hi_pp": 100 * b.quantile(.975, axis=1),
                          "mice": e.groupby(["abs_coh", "timing"]).size(), "trials": e.groupby(["abs_coh", "timing"]).n.sum()})
        s.to_csv(out / f"pulse_effect_{tag}.csv"); print(f"\n== data pulse effect ({tag}), pp, 95% hierarchical bootstrap ==\n{s.round(1).to_string()}")
    cells = pd.read_csv("dissemination/paper_accumulation/draft_2026-11-15/choice_g2_by_cell_type_2026-11-19/cells_typed.csv.gz")
    fams = ["pulse_norm_ugm_no_sv", "pulse_linear_no_sv", "pulse_power_leak", "pulse_linear_leak"]
    for tag, d in (("all", cells), ("no_PSUIM6_7", cells[~cells.mouse.isin(["PSUIM6", "PSUIM7"])])):
        r = residuals(d, n_boot, rng, fams); r.to_csv(out / f"residual_{tag}.csv")
        print(f"\n== model residual (obs - model follow), held-out ({tag}) ==\n{r.round(1).to_string()}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path); ap.add_argument("--n_boot", type=int, default=2000)
    a = ap.parse_args(); main(a.output, a.n_boot)
