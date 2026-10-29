"""Does between-trial drift variability (sv) cause the late pulse reversal the fitted models predict? (report
2026-10-29-joint-control-pulse-refits, next step; hypothesis: the pulse ends trials with eta toward the pulse early, so
late responses are enriched for eta against the pulse, and eta persists within the trial).

Model: the primary joint fit (fits_joint_unfreeze_integrators, L0U0V1Z0G1, split "all") per mouse, simulated with the
simulator kernel itself (src/ddm/simulator._simulate_ddm_trials_numba). Fast guesses are left out (they do not depend on
the pulse). Paired design: every responded pulse trial (symmetric cells, |coh| <= 36, as the descriptive package) is
simulated with and without its pulse (primacy.stimuli) using the same diffusion noise and the same eta = sv_scale x sv x xi,
xi ~ N(0, 1) per trial; sv_scale in SV_SCALES (1 = fitted). N_REPS repetitions, seed SEED, common random numbers across
scales. Responses: decision by 5 s (RT incl. ndt <= 5 s).

Per window of (RT - pulse onset) (0.3-1.2 s, 1.2-5 s):
  effect   P(choice = pulse sign | pulse twin ends in window) - P(... | no-pulse twin ends in window), pp;
  eta_sel  mean xi x pulse sign among trials ending in the window, pulse twin minus no-pulse twin (SD units of eta).
Mean over mice (unit = mouse), with the number of mice below 0.

Outputs: dissemination/figures/qc/pulse_sv_reversal_<date>.{png,pdf,csv}
Usage:   python -m scripts.ddm.pulse_sv_reversal
"""

import pickle
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.ddm.compare_joint_refits import DDM
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.primacy import stimuli
from scripts.ddm.pulse_leak_urgency_signatures import observed
from scripts.ddm.pulse_psychometric import OUT
from src.ddm.simulator import _simulate_ddm_trials_numba

SV_SCALES = (0.0, 0.5, 1.0, 1.5)
N_REPS, SEED, DT, CENSOR = 30, 0, 0.001, 5.0
WINDOWS = {"0.3-1.2": (0.3, 1.2), "1.2-5": (1.2, 5.0)}


def main():
    inputs = responded_only(load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz"))
    mice = sorted(set(inputs["subject_id"]))
    obs = observed(inputs, mice)
    rng = np.random.default_rng(SEED)
    rows_out = []
    for mouse in mice:
        with open(DDM / "fits_joint_unfreeze_integrators" / f"{mouse}_L0U0V1Z0G1_all.pkl", "rb") as f:
            p = pickle.load(f)["parameters"]
        t = obs[(obs.mouse == mouse) & (obs.stage > 0)]
        rows, s, onset = t.row.to_numpy(), t.s.to_numpy(), t.onset.to_numpy()
        w, wo = stimuli(inputs, rows)
        w, wo = np.ascontiguousarray(w, np.float32), np.ascontiguousarray(wo, np.float32)
        zeros = np.zeros(len(rows), np.float32)
        acc = {k: [] for k in SV_SCALES}
        for _ in range(N_REPS):
            noise = rng.normal(0, np.sqrt(p["variance"] * DT), w.shape[:1] + (w.shape[1] - 1,)).astype(np.float32)
            xi = rng.standard_normal(len(rows)).astype(np.float32)
            for k in SV_SCALES:
                eta = (k * p["sv"] * xi).astype(np.float32)
                out = [_simulate_ddm_trials_numba(x, noise, eta, zeros, p["drift_gain"], p["drift_offset"], p["a"], p["z"],
                                                  p["ndt"], DT, 0.0, 0.0, 0.0) for x in (w, wo)]
                acc[k].append(np.stack([np.r_[o[0]] for o in out] + [np.r_[o[1]] for o in out] + [xi * s, s, onset]))
        for k in SV_SCALES:
            a = np.concatenate(acc[k], axis=1)  # rt_w, rt_wo, ch_w, ch_wo, xi_signed, s, onset
            for twin, (rt, ch) in {"pulse": (a[0], a[2]), "no_pulse": (a[1], a[3])}.items():
                ok = ~np.isnan(rt) & (rt <= CENSOR)
                since = rt - a[6]
                for name, (lo, hi) in WINDOWS.items():
                    m = ok & (since >= lo) & (since < hi)
                    toward = (np.where(ch == 1, 1, -1) == a[5])[m]
                    rows_out.append({"mouse": mouse, "sv_scale": k, "sv": k * p["sv"], "twin": twin, "window": name, "n": int(m.sum()),
                                     "p_toward": toward.mean(), "xi_toward": a[4][m].mean(), "responded": ok.mean()})
        print(mouse, flush=True)
    r = pd.DataFrame(rows_out)
    piv = r.pivot_table(index=["mouse", "sv_scale", "window"], columns="twin", values=["p_toward", "xi_toward", "n"])
    d = pd.DataFrame({"effect_pp": 100 * (piv[("p_toward", "pulse")] - piv[("p_toward", "no_pulse")]),
                      "eta_sel": piv[("xi_toward", "pulse")] - piv[("xi_toward", "no_pulse")],
                      "n_pulse_twin": piv[("n", "pulse")]}).reset_index()
    g = d.groupby(["sv_scale", "window"]).agg(effect_pp=("effect_pp", "mean"), mice_below_0=("effect_pp", lambda v: int((v < 0).sum())),
                                              eta_sel=("eta_sel", "mean"), eta_mice_below_0=("eta_sel", lambda v: int((v < 0).sum())))
    pd.set_option("display.width", 200)
    print(g.round(3).to_string())
    print(d.pivot_table(index="mouse", columns=["window", "sv_scale"], values="effect_pp").round(1).to_string())
    stem = OUT / f"pulse_sv_reversal_{date.today().isoformat()}"
    d.round(5).to_csv(f"{stem}.csv", index=False)
    r.round(5).to_csv(f"{stem}_twins.csv", index=False)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for j, (col, lab) in enumerate((("effect_pp", "pulse effect, pulse twin - no-pulse twin (pp)"),
                                    ("eta_sel", "mean eta toward pulse, pulse - no-pulse twin (SD of eta)"))):
        for win, mk in zip(WINDOWS, ("o", "s")):
            v = d[d.window == win].pivot(index="mouse", columns="sv_scale", values=col)
            for m in v.index:
                ax[j].plot(v.columns, v.loc[m], color="C0" if win == "0.3-1.2" else "C3", alpha=0.25, lw=0.8)
            ax[j].plot(v.columns, v.mean(), mk + "-", color="C0" if win == "0.3-1.2" else "C3", lw=2.2, label=f"responses {win} s after pulse")
        ax[j].axhline(0, color="0.5", lw=0.6)
        ax[j].set_xlabel("sv scale (1 = fitted)"); ax[j].set_ylabel(lab, fontsize=9); ax[j].legend(fontsize=8, frameon=False)
    ax[0].set_title("A  paired pulse effect vs between-trial drift variability", fontsize=10)
    ax[1].set_title("B  selection on eta among responses in the window", fontsize=10)
    fig.suptitle("Primary joint fit, 10 mice, each pulse trial simulated with and without its pulse (same noise, same eta); thin = mice", fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{stem}.png", dpi=140); fig.savefig(f"{stem}.pdf")
    print(stem)


if __name__ == "__main__":
    main()
