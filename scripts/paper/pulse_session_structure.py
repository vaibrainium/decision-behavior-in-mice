"""Are pulse and control trials interleaved within sessions, or separated by session / training stage? (author request
2026-11-20, possible session/engagement confound behind PSUIM6/7's pulse-vs-control mismatch.)
Uses the DDM inputs (responded trials only, RT <= 5 s), session = idx_session, trial order = last field of agg_code.
Per mouse: sessions with only control / only pulse / both; share of pulse trials in mixed sessions; within mixed
sessions the observed number of control<->pulse switches vs its expectation under random order (Wald-Wolfowitz runs);
mean normalised trial position of pulse vs control trials; and control accuracy (|coh| > 0) in control-only vs mixed
sessions.
Usage: PYTHONPATH=/src .venv/bin/python -m scripts.paper.pulse_session_structure --output <new dir>"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.rescore_fits import inputs


def main(out):
    out.mkdir(parents=True, exist_ok=False)
    x = inputs()
    t = pd.DataFrame({"mouse": x["subject_id"], "session": x["idx_session"], "pulse": x["sched_pulse_type"] != 0,
                      "coh": x["signed_coherence"], "choice": x["choice"],
                      "trial": [int(a.rsplit("_", 1)[1]) for a in x["agg_code"]]})
    t["correct"] = np.where(t.coh != 0, (t.choice == (t.coh > 0)).astype(float), np.nan)
    t = t.sort_values(["mouse", "session", "trial"])
    s = t.groupby(["mouse", "session"]).agg(n=("pulse", "size"), n_pulse=("pulse", "sum"), first_trial=("trial", "min"),
                                            last_trial=("trial", "max")).reset_index()
    s["kind"] = np.select([s.n_pulse == 0, s.n_pulse == s.n], ["control_only", "pulse_only"], "mixed")
    s["session_rank"] = s.groupby("mouse").session.rank().astype(int)
    s.to_csv(out / "sessions.csv", index=False)

    rows = []
    for mouse, g in t.groupby("mouse"):
        ss = s[s.mouse == mouse].set_index("session")
        mixed = ss.index[ss.kind == "mixed"]
        gm = g[g.session.isin(mixed)].copy()
        switches = expected = 0.0
        for _, h in gm.groupby("session"):
            p = h.pulse.to_numpy(); n1, n = p.sum(), len(p)
            switches += np.sum(p[1:] != p[:-1]); expected += 2 * n1 * (n - n1) / n
        gm["pos"] = gm.groupby("session").trial.rank(pct=True)
        acc = lambda kinds: t[(t.mouse == mouse) & ~t.pulse & t.session.isin(ss.index[ss.kind.isin(kinds)])].correct.mean()
        pulse_sessions = ss[ss.n_pulse > 0]
        rows.append(dict(
            mouse=mouse, sessions=len(ss), control_only=int((ss.kind == "control_only").sum()), mixed=len(mixed),
            pulse_only=int((ss.kind == "pulse_only").sum()), trials=len(g), pulse_trials=int(g.pulse.sum()),
            pulse_share_in_mixed=g[g.session.isin(mixed)].pulse.sum() / max(g.pulse.sum(), 1),
            pulse_frac_in_mixed_sessions=gm.pulse.mean() if len(gm) else np.nan,
            switches_obs=switches, switches_exp_random=expected,
            pos_pulse=gm[gm.pulse].pos.mean() if len(gm) else np.nan, pos_control=gm[~gm.pulse].pos.mean() if len(gm) else np.nan,
            first_pulse_session_rank=int(pulse_sessions.session_rank.min()) if len(pulse_sessions) else np.nan,
            control_only_ranks=",".join(map(str, ss[ss.kind == "control_only"].session_rank)),
            ctrl_acc_control_only_sessions=acc(["control_only"]), ctrl_acc_mixed_sessions=acc(["mixed"])))
    r = pd.DataFrame(rows)
    r.to_csv(out / "by_mouse.csv", index=False)
    pd.set_option("display.width", 250)
    print(r.round(3).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    main(ap.parse_args().output)
