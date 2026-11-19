"""Error hazard aligned to pulse onset vs control trials at matched pseudo-onsets (pre-registered: plan
2026-11-19-choice-misfit-followup.md, criteria B).

Pulse trials: given |coherence| and pulse congruence (100% incongruent primary; 36% congruent check). Error = choice
against coherence. Control trials of the same mouse and signed coherence get N_PSEUDO pseudo-onsets drawn from that
mouse's pulse-onset distribution in the selected pulse trials. At risk at tau = RT >= onset + tau (still undecided).
Window hazard = errors with RT - onset in [a, b) / at risk at a. Ratio pulse/control, counts pooled over mice.
Bootstrap: mice with replacement, then trials within mouse (control trials keep their pseudo-onsets).
Usage: python -m scripts.paper.pulse_onset_error_hazard --output <new dir> [--n_boot 2000]"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.ddm.rescore_fits import inputs

N_PSEUDO, WINDOW, OUTSIDE = 20, (0.150, 0.400), (0.400, 1.500)
BINS = np.round(np.arange(0, 1.501, 0.05), 3)
GROUPS = {"all": None, "PSUIM6_7": ["PSUIM6", "PSUIM7"], "other_8": "rest"}


def table():
    x = inputs()
    t = pd.DataFrame({"mouse": x["subject_id"], "coh": np.round(100 * x["signed_coherence"]).astype(int), "pulse": x["sched_pulse_type"],
                      "onset": x["pulse_onset_frame0"] / x["frame_rate"], "rt": x["rt"], "choice": x["choice"]})
    t["err"] = ((t.choice == 1) != (t.coh > 0)).astype(float)
    return t


def intervals():
    edges = [(a, b) for a, b in zip(BINS[:-1], BINS[1:])]
    return [WINDOW, OUTSIDE] + edges


def per_trial(rt, onset, err, w):
    """(at_risk, events) matrices, trials x intervals, weighted."""
    iv = intervals(); risk = np.zeros((len(rt), len(iv))); ev = np.zeros_like(risk)
    for j, (a, b) in enumerate(iv):
        r = rt >= onset + a
        risk[:, j] = w * r; ev[:, j] = w * (r & (rt < onset + b) & (err > 0))
    return risk, ev


def build(t, abs_coh, congruent, rng):
    """Per mouse: pulse (risk, ev) and control (risk, ev) per-trial arrays (control rows = trials, pseudo-onsets summed)."""
    out = {}
    for m, d in t[t.coh.abs() == abs_coh].groupby("mouse"):
        p = d[d.pulse != 0]; p = p[(np.sign(p.pulse) == np.sign(p.coh)) == congruent]
        c = d[d.pulse == 0]
        if len(p) == 0 or len(c) == 0:
            continue
        pr, pe = per_trial(p.rt.to_numpy(), p.onset.to_numpy(), p.err.to_numpy(), 1.0)
        on = rng.choice(p.onset.to_numpy(), (len(c), N_PSEUDO))
        cr, ce = per_trial(np.repeat(c.rt.to_numpy(), N_PSEUDO), on.ravel(), np.repeat(c.err.to_numpy(), N_PSEUDO), 1.0 / N_PSEUDO)
        k = len(c)
        out[m] = (pr, pe, cr.reshape(k, N_PSEUDO, -1).sum(1), ce.reshape(k, N_PSEUDO, -1).sum(1))
    return out


def ratio(parts):
    pr, pe, cr, ce = (np.sum([q[i].sum(0) for q in parts], axis=0) for i in range(4))
    with np.errstate(invalid="ignore", divide="ignore"):
        hp, hc = pe / pr, ce / cr
    return hp, hc, hp / hc, pe, pr


def boot(data, mice, n_boot, rng):
    res = []
    for _ in range(n_boot):
        parts = []
        for m in rng.choice(mice, len(mice)):
            pr, pe, cr, ce = data[m]
            i, j = rng.integers(len(pr), size=len(pr)), rng.integers(len(cr), size=len(cr))
            parts.append((pr[i], pe[i], cr[j], ce[j]))
        res.append(ratio(parts)[2])
    return np.array(res)


def analyse(t, abs_coh, congruent, tag, out, n_boot, rng):
    data = build(t, abs_coh, congruent, rng)
    names = ["window_150_400", "outside_400_1500"] + [f"bin_{int(1000*a)}_{int(1000*b)}" for a, b in zip(BINS[:-1], BINS[1:])]
    rows = []
    for g, sel in GROUPS.items():
        mice = sorted(data) if sel is None else ([m for m in sorted(data) if m not in GROUPS["PSUIM6_7"]] if sel == "rest" else [m for m in sel if m in data])
        if not mice:  # e.g. PSUIM6/7 have no late pulses
            continue
        hp, hc, r, pe, pr = ratio([data[m] for m in mice])
        b = boot(data, np.array(mice), n_boot, rng)
        lo, hi = np.nanpercentile(b, [2.5, 97.5], axis=0)
        logdiff = np.log(b[:, 0]) - np.log(b[:, 1])
        for j, n in enumerate(names):
            rows.append(dict(analysis=tag, group=g, mice=len(mice), interval=n, pulse_events=pe[j], pulse_at_risk=pr[j],
                             hazard_pulse=hp[j], hazard_control=hc[j], ratio=r[j], lo=lo[j], hi=hi[j],
                             log_ratio_window_minus_outside_lo=np.nanpercentile(logdiff, 2.5) if j == 0 else np.nan,
                             log_ratio_window_minus_outside_hi=np.nanpercentile(logdiff, 97.5) if j == 0 else np.nan))
    df = pd.DataFrame(rows); df.to_csv(out / f"hazard_{tag}.csv", index=False)
    show = df[df.interval.isin(names[:2])][["group", "mice", "interval", "pulse_events", "pulse_at_risk", "hazard_pulse", "hazard_control", "ratio", "lo", "hi",
                                            "log_ratio_window_minus_outside_lo", "log_ratio_window_minus_outside_hi"]]
    print(f"\n== {tag} ==\n{show.round(3).to_string(index=False)}")
    prof = df[df.interval.str.startswith("bin_") & (df.group == "all")][["interval", "pulse_events", "pulse_at_risk", "ratio", "lo", "hi"]]
    print(f"profile (all mice):\n{prof.head(16).round(2).to_string(index=False)}")


def main(out, n_boot):
    out.mkdir(parents=True, exist_ok=False); rng = np.random.default_rng(20261119)
    t = table()
    analyse(t, 100, False, "coh100_incongruent", out, n_boot, rng)
    for k, name in ((1, "early"), (2, "middle"), (3, "late")):
        analyse(t[(t.pulse == 0) | (t.pulse.abs() == k)], 100, False, f"coh100_incongruent_{name}", out, n_boot, rng)
    analyse(t, 36, True, "coh36_congruent_check", out, n_boot, rng)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path); ap.add_argument("--n_boot", type=int, default=2000)
    a = ap.parse_args(); main(a.output, a.n_boot)
