"""Figure 2: motion energy (ME) of the replayed stimulus, mouse-tuned filters, calibrated per rig.

Panels
  A  space-time profile of a rightward-tuned filter (sum of the quadrature pair f1 g1 + f2 g2), with the dot speed
  B  mean ME over time by coherence, UCLA control trials
  C  same, UW
  D  time-averaged ME vs programmed coherence, both rigs
  E  ME response to a pulse (per 100% coherence change), aligned to pulse onset

ME is the calibrated full replay (`motion_energy_mouse/me_calibrated.npz`, `global` pooling, 60 Hz, 5 s, in equivalent %
coherence; not cut at the RT). Stimulus properties, so trials (not mice) are the unit here.

Usage: python -m scripts.paper.fig2_motion_energy
"""

import matplotlib.pyplot as plt
import numpy as np

from scripts.compute_motion_energy_full import convert_to_frame_units
from scripts.motion_energy import MOUSE_ME_PARAMS, mouse_me_kernels
from scripts.paper.style import (
    FULL_WIDTH,
    MM,
    PROCESSED,
    RIG_COLOR,
    RIG_LABEL,
    RIG_MARKER,
    RIGS,
    apply_style,
    label_panel,
    load_trials,
    save,
)

FRAME_S = 1 / 60
DOT_SPEED_DEG_S = 30  # replay settings (log section 2.2): ~30 deg/s on both rigs
MEAN_WINDOW = slice(20, 300)  # 0.33-5 s, after the onset response (as notebook 2.14)
PULSE_WINDOW = (-6, 36)  # frames around pulse onset (-100 to 600 ms)


def load_me():
    f = np.load(PROCESSED / "motion_energy_mouse" / "me_calibrated.npz")
    trials = convert_to_frame_units(load_trials().query("~censored"))
    row = {c: i for i, c in enumerate(f["agg_code"])}
    trials = trials[trials["agg_code"].isin(row)].reset_index(drop=True)
    me = f["global"][[row[c] for c in trials["agg_code"]]].astype(float)
    print(f"[data] {len(trials)} responded trials with ME; params {f['params']}")
    return trials, me


def panel_filter(ax):
    k = mouse_me_kernels()
    x = (np.arange(k["fx"].shape[1]) - k["fx"].shape[1] // 2) * MOUSE_ME_PARAMS["dx_deg"]
    t = np.arange(k["gt"].shape[1]) * MOUSE_ME_PARAMS["dt_s"]
    candidates = {"f1g1+f2g2": np.outer(k["gt"][0], k["fx"][0]) + np.outer(k["gt"][1], k["fx"][1]),
                  "f1g1-f2g2": np.outer(k["gt"][0], k["fx"][0]) - np.outer(k["gt"][1], k["fx"][1])}

    def response(filt, v):  # response to a bar moving at v deg/s through x = 0 at t = 0.25 s
        xi = np.round((v * (t - 0.25)) / MOUSE_ME_PARAMS["dx_deg"]).astype(int) + len(x) // 2
        ok = (xi >= 0) & (xi < len(x))
        return filt[np.flatnonzero(ok), xi[ok]].sum()

    # quadrature pairs are phase-sensitive; the direction preference shows in energy summed over bar positions
    def energy(filt, v):
        return sum(response(np.roll(filt, s, axis=1), v) ** 2 for s in range(-12, 13))

    name = max(candidates, key=lambda n: energy(candidates[n], DOT_SPEED_DEG_S) - energy(candidates[n], -DOT_SPEED_DEG_S))
    filt = candidates[name]
    ratio = energy(filt, DOT_SPEED_DEG_S) / energy(filt, -DOT_SPEED_DEG_S)
    print(f"[A] rightward-tuned combination {name}; energy ratio right/left at {DOT_SPEED_DEG_S} deg/s = {ratio:.1f}")
    lim = np.abs(filt).max()
    ax.imshow(filt, aspect="auto", origin="lower", cmap="RdBu_r", vmin=-lim, vmax=lim,
              extent=[x[0], x[-1], t[0] * 1000, t[-1] * 1000], interpolation="nearest")
    tt = np.array([0.05, 0.35])
    ax.plot(DOT_SPEED_DEG_S * (tt - 0.2), tt * 1000, color="k", lw=0.8, ls="--")
    ax.text(0.03, 0.97, f"{DOT_SPEED_DEG_S}°/s", transform=ax.transAxes, va="top", fontsize=6)
    ax.set_xlabel("Space (deg)")
    ax.set_ylabel("Time lag (ms)")
    ax.set_title("Rightward filter (x–t)", loc="left")


def panel_timecourse(ax, trials, me, rig):
    sel = (trials["data_source"] == rig).to_numpy() & (trials["sched_pulse_type"] == 0).to_numpy()
    cohs = np.sort(trials.loc[sel, "signed_coherence"].unique())
    cmap = plt.get_cmap("RdBu_r")
    t = np.arange(me.shape[1]) * FRAME_S
    for c in cohs:
        m = me[sel & (trials["signed_coherence"] == c).to_numpy()].mean(axis=0)
        ax.plot(t, m, color=cmap(0.5 + c / 220), lw=0.8, label=f"{c:+d}" if c else "0")
    ax.axhline(0, color="0.6", lw=0.4)
    ax.set_xlim(0, 2)
    ax.set_xlabel("Time from motion onset (s)")
    ax.set_ylabel("Motion energy (% coh. equiv.)")
    ax.set_title(f"{RIG_LABEL[rig]} control trials (n = {sel.sum():,})", loc="left")


def panel_linearity(ax, trials, me):
    for rig in RIGS:
        sel = (trials["data_source"] == rig).to_numpy() & (trials["sched_pulse_type"] == 0).to_numpy()
        sub = trials[sel]
        avg = me[sel][:, MEAN_WINDOW].mean(axis=1)
        g = sub.assign(me=avg).groupby("signed_coherence")["me"]
        x = g.mean().index.to_numpy(float)
        ax.errorbar(x, g.mean(), yerr=g.std(), fmt=RIG_MARKER[rig], color=RIG_COLOR[rig], elinewidth=0.7,
                    capsize=0, label=RIG_LABEL[rig], mfc="white" if rig == "uw" else RIG_COLOR[rig],
                    ms=4 if rig == "uw" else 2.5, mew=0.8, zorder=3 if rig == "ucla" else 2)
        slope, icpt = np.polyfit(sub["signed_coherence"], avg, 1)
        r = np.corrcoef(sub["signed_coherence"], avg)[0, 1]
        sd0 = g.std().loc[0]
        print(f"[D] {RIG_LABEL[rig]}: ME (0.33-5 s mean) = {slope:.3f} x coherence + {icpt:.2f}, r = {r:.3f}, "
              f"trial SD at 0% = {sd0:.2f}; n = {sel.sum()}")
    ax.plot([-100, 100], [-100, 100], color="0.5", lw=0.5, ls=":", zorder=0)
    ax.set_xticks([-100, -36, 0, 36, 100])
    ax.set_xlabel("Programmed coherence (%)")
    ax.set_ylabel("Mean motion energy\n0.33–5 s (% coh. equiv.)")
    ax.legend(loc="upper left", handlelength=1)


def panel_pulse(ax, trials, me):
    lags = np.arange(*PULSE_WINDOW)
    for rig in RIGS:
        rig_rows = (trials["data_source"] == rig).to_numpy()
        ctrl = rig_rows & (trials["sched_pulse_type"] == 0).to_numpy()
        ctrl_mean = {c: me[ctrl & (trials["signed_coherence"] == c).to_numpy()].mean(axis=0)
                     for c in trials.loc[ctrl, "signed_coherence"].unique()}
        pulsed = np.flatnonzero(rig_rows & (trials["sched_pulse_type"] != 0).to_numpy())
        resp = []
        for i in pulsed:
            row = trials.iloc[i]
            delta = row["pulse_coherence"] - row["signed_coherence"]
            onset = int(row["pulse_onset_frame"]) - 1
            if not np.isfinite(delta) or delta == 0 or onset + lags[0] < 0 or onset + lags[-1] >= me.shape[1]:
                continue
            resid = me[i] - ctrl_mean[row["signed_coherence"]]
            resp.append(100 * resid[onset + lags] / delta)
        resp = np.array(resp)
        m = resp.mean(axis=0)
        sem = resp.std(axis=0, ddof=1) / np.sqrt(len(resp))
        t = lags * FRAME_S * 1000
        ax.fill_between(t, m - sem, m + sem, color=RIG_COLOR[rig], alpha=0.25, lw=0)
        ax.plot(t, m, color=RIG_COLOR[rig], lw=1.0, label=f"{RIG_LABEL[rig]} (n = {len(resp):,})")
        peak = t[np.argmax(m)]
        half = t[np.argmax(m >= m.max() / 2)]
        print(f"[E] {RIG_LABEL[rig]}: pulse response peak {m.max():.1f} at {peak:.0f} ms after onset, half-max at "
              f"{half:.0f} ms; n = {len(resp)} pulse trials")
    ax.axhline(0, color="0.6", lw=0.4)
    ax.axvline(0, color="0.6", lw=0.4, ls=":")
    ax.set_xlabel("Time from pulse onset (ms)")
    ax.set_ylabel("ME change per 100%\ncoherence change")
    ax.legend(loc="upper right", handlelength=1)


def main():
    apply_style()
    trials, me = load_me()
    fig, axs = plt.subplot_mosaic([["A", "B", "C"], ["D", "E", "E"]], figsize=(FULL_WIDTH, 110 * MM),
                                  layout="constrained")
    panel_filter(axs["A"])
    for rig, key in zip(RIGS, "BC"):
        panel_timecourse(axs[key], trials, me, rig)
    axs["C"].sharey(axs["B"])
    axs["C"].legend(title="Coherence (%)", fontsize=5.5, title_fontsize=6, loc="center left", bbox_to_anchor=(1, 0.5),
                    handlelength=1)
    panel_linearity(axs["D"], trials, me)
    panel_pulse(axs["E"], trials, me)
    for letter, ax in axs.items():
        label_panel(ax, letter, x=-0.12 if letter == "E" else -0.3)
    save(fig, "fig2_motion_energy")


if __name__ == "__main__":
    main()
