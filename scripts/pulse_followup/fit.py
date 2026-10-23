"""Package F3: the tau_p pilot, scored exactly as frozen in <run>/models/f2_spec_tau_pilot.json (EXPLORATORY).

For PSUIM6 and PSUIM7 (primary baseline, control parameters frozen at the amendment 6 revised fits), simulate every
pulse trial of the corrected v2 inputs on the frozen (tau_p, w) grid with common random numbers (models.py), decompose
the CensoredQMLE objective as in package E (diagnostics.decompose), and evaluate the frozen criteria:
  P0  control-trial inputs identical across tau_p (pulse component 0 on controls; tau_p = 0 is the identity)
  P1  in-sample best (w, tau_p) has tau_p > 0, beats the best tau_p = 0 point by >= 10 NLL and by > 2x the
      seed-to-seed SD of that improvement (second CRN seed at both points); held-out total NLL better in >= 4/5 folds
  P2  w_choice_only / w_joint <= 1.5 at the best tau_p
  P3  model directional contrast in the 2-4.58 s window (D cell weights) >= -1.0 pp at the best (w, tau_p)
Decision: PASS (all, both mice) / MIXED (one mouse) / FAIL. No grid expansion.

Fold membership: the stored amendment 6 folds for trials present in v1; the 38 trials added in v2 (relabelled
pulses) get fold = their order within the mouse's added trials modulo 5 (deterministic, outcome-independent).
Ties and ambiguities resolve against the candidate (a train-fold optimum at tau_p = 0 counts as no improvement).

Usage: NUMBA_NUM_THREADS=8 python -B -m scripts.pulse_followup.fit --run-id <run_id>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.pulse_followup import io
from scripts.pulse_followup.models import RUN_SUB, CandidateSimulator, exp_kernel, load_spec

SPEC_SHA = "4c1995cac6fb21b0cc17164061107f73acf346508db054f89b68fba57c97fb64"
SEED, SECOND_SEED = 50, 51  # E's base seed (fit_pulse_gain all-trial profile: seed + 50); second CRN seed
WINDOW = (2.0, 4.58)


def folds_for(inputs, rows, pr, N_FOLDS):
    """Stored fold per v1 trial; added v2 trials cycle through folds in trial order."""
    v1_codes = np.load(io.PROCESSED / "ddm" / "ddm_inputs_global.npz")["agg_code"]  # stored folds are keyed by v1 row
    stored = dict(zip(v1_codes[pr["trials"].row.to_numpy()], pr["trials"].fold))
    codes = inputs["agg_code"][rows]
    folds = np.array([stored.get(c, -1) for c in codes])
    added = np.flatnonzero(folds < 0)
    folds[added] = np.arange(len(added)) % N_FOLDS
    return folds, len(added)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    timer = io.Timer()
    from scripts.ddm import primacy
    from scripts.ddm.fit_mouse_ddm import LIKELIHOOD_PARAMS, N_FOLDS, load_inputs
    from scripts.pulse_followup import diagnostics as dg
    from scripts.pulse_followup import response_time as rtm
    from src.ddm.likelihood_calculator_censored import CensoredQMLE

    run = io.run_dir(a.run_id)
    spec = load_spec(run, SPEC_SHA)
    t, _ = io.load_trials(run)
    out = io.stage_dir(run, "models") / RUN_SUB
    out.mkdir(exist_ok=True)
    if (out / "COMPLETE").exists():
        raise FileExistsError(out)
    inputs = load_inputs(Path(spec["inputs"]["ddm_inputs"]))
    lik = CensoredQMLE(nbins=LIKELIHOOD_PARAMS["nbins"], rt_nllh_weight=LIKELIHOOD_PARAMS["rt_nllh_weight"])
    taus, ws = spec["grid"]["tau_p_ms"], spec["grid"]["w"]
    reps = spec["simulation"]["reps"]
    pc = spec["pass_criteria_each_mouse"]
    tt = t.set_index("trial_id")
    checks, prof_rows, crit, curve_rows, seed_rows = {}, [], [], [], []

    # P0: control inputs identical across tau_p; tau_p = 0 is the identity; unit area
    p0 = {}
    for m in spec["mice"]:
        crow = np.flatnonzero((inputs["subject_id"] == m) & (inputs["sched_pulse_type"] == 0))
        _, pulse_c = primacy.gain_stimuli(inputs, crow[:200])
        prow = primacy.pulse_rows(inputs, m)
        _, pulse_p = primacy.gain_stimuli(inputs, prow[:200])
        p0[m] = {"control_pulse_component_all_zero": bool(np.all(pulse_c == 0)),
                 "control_filtered_identical_all_tau": bool(all(np.array_equal(exp_kernel(pulse_c, tau), pulse_c) for tau in taus)),
                 "tau0_identity": bool(np.array_equal(exp_kernel(pulse_p, 0), pulse_p)),
                 "unit_area_max_rel_err_tau100": float(np.max(np.abs(exp_kernel(pulse_p[:, :3000], 100).sum(1) - pulse_p[:, :3000].sum(1))
                                                           / (np.abs(pulse_p[:, :3000]).sum(1) + 1e-12)))}
    io.write_json(out / "p0_checks.json", p0)

    for m in spec["mice"]:
        pr = dg.load_revised("primary", m)
        rows = primacy.pulse_rows(inputs, m)
        rt_d, ch_d, cond = inputs["rt"][rows], inputs["choice"][rows], inputs["condition"][rows]
        folds, n_added = folds_for(inputs, rows, pr, N_FOLDS)
        scopes = {"in_sample": np.ones(len(rows), bool)}
        for k in range(N_FOLDS):
            scopes[f"train{k}"], scopes[f"test{k}"] = folds != k, folds == k
        # D-weighted cells for the window contrast (same construction as diagnostics E4a)
        codes = inputs["agg_code"][rows]
        sel = tt.loc[codes]
        keep = (sel.signs_scheduled_symmetric & (sel.coherence_pct.abs() <= 36) & sel.pulse_category.isin(["positive", "negative"])).to_numpy()
        dset = pd.DataFrame({"trial_id": codes[keep], "mouse": m, "session": sel.session.to_numpy()[keep],
                             "coherence_pct": sel.coherence_pct.to_numpy()[keep], "onset_stratum": sel.onset_stratum.to_numpy()[keep],
                             "arm": sel.pulse_category.to_numpy()[keep], "onset": sel.recorded_onset_s.to_numpy()[keep],
                             "side": sel.response_side.to_numpy()[keep], "rt": sel.rt_s.to_numpy()[keep], "pos": np.flatnonzero(keep)})
        dset["u"] = dset.rt - dset.onset
        aw = rtm.cell_weights(dset, ("positive", "negative"))
        U = dg.U_GRID

        def window_contrast(cur):
            p, n = cur[(m, "positive")], cur[(m, "negative")]
            d = ((p["cif_R"] - n["cif_R"]) - (p["cif_L"] - n["cif_L"])) / 2
            at = lambda u: d[int(np.argmin(np.abs(U - u)))]
            return 100 * (at(WINDOW[1]) - at(WINDOW[0])), d

        obs = {arm: rtm.curves_for(g, U) for arm, g in aw.groupby("arm")}
        obs_late, _ = window_contrast({(m, k): v for k, v in obs.items()})

        def model_late(rt_s, ch_s):
            idx = aw.pos.to_numpy()
            R = rt_s.shape[0]
            r, c = rt_s[:, idx].astype(float), ch_s[:, idx]
            df = pd.DataFrame({"mouse": m, "arm": np.tile(aw.arm.to_numpy(), R),
                               "u": np.where(c.ravel() >= 0, r.ravel() - np.tile(aw.onset.to_numpy(), R), np.nan),
                               "side": np.where(c.ravel() == 1, "R", np.where(c.ravel() == 0, "L", "none")),
                               "wt": np.tile(aw.wt.to_numpy(), R) / R})
            return window_contrast({(m, arm): rtm.curves_for(g, U) for arm, g in df.groupby("arm")})

        def score(rt_s, ch_s):
            R = rt_s.shape[0]
            rp, cp, cc = rt_s.ravel(), ch_s.ravel().astype(int), np.tile(cond, R)
            res = {}
            for sc, s in scopes.items():
                sp = np.tile(s, R)
                res[sc] = dg.decompose(lik, rp[sp], cp[sp], cc[sp], rt_d[s], ch_d[s], cond[s])
            return res

        sim = CandidateSimulator(inputs, rows, pr["params"], pr["variant"], pr["rig"], seed=SEED, n_reps=reps)
        late = {}
        for tau in taus:
            for w in ws:
                rt_s, ch_s = sim.simulate(tau, w)
                late[(tau, w)] = model_late(rt_s, ch_s)[0]
                for sc, d in score(rt_s, ch_s).items():
                    prof_rows.append({"mouse": m, "seed": SEED, "tau_ms": tau, "w": w, "scope": sc, **d, "late_window_pp": late[(tau, w)]})
        del sim
        prof = pd.DataFrame([r for r in prof_rows if r["mouse"] == m])
        ins = prof[prof.scope == "in_sample"]
        best = ins.loc[ins.total.idxmin()]
        best0 = ins[ins.tau_ms == 0].loc[ins[ins.tau_ms == 0].total.idxmin()]
        bestp = ins[ins.tau_ms > 0].loc[ins[ins.tau_ms > 0].total.idxmin()]

        # second CRN seed at the best tau_p > 0 point and the best tau_p = 0 point
        sim2 = CandidateSimulator(inputs, rows, pr["params"], pr["variant"], pr["rig"], seed=SECOND_SEED, n_reps=reps)
        tot2 = {}
        for lab, pt in (("best_tau0", best0), ("best_taupos", bestp)):
            r2, c2 = sim2.simulate(pt.tau_ms, pt.w)
            tot2[lab] = score(r2, c2)["in_sample"]["total"]
            seed_rows.append({"mouse": m, "point": lab, "tau_ms": pt.tau_ms, "w": pt.w, "total_seed50": pt.total, "total_seed51": tot2[lab]})
        del sim2
        imp = np.array([best0.total - bestp.total, tot2["best_tau0"] - tot2["best_taupos"]])
        imp_sd = float(np.std(imp, ddof=1))

        # held-out folds: train optimum over all (tau, w) vs over tau = 0 only; score on the test fold
        fold_rows = []
        for k in range(N_FOLDS):
            tr, te = prof[prof.scope == f"train{k}"], prof[prof.scope == f"test{k}"]
            c_all, c_0 = tr.loc[tr.total.idxmin()], tr[tr.tau_ms == 0].loc[tr[tr.tau_ms == 0].total.idxmin()]
            pick = lambda c: te[(te.tau_ms == c.tau_ms) & (te.w == c.w)].total.iloc[0]
            fold_rows.append({"fold": k, "train_best_tau": c_all.tau_ms, "train_best_w": c_all.w, "train_best_w_tau0": c_0.w,
                              "test_total_candidate": pick(c_all), "test_total_tau0": pick(c_0),
                              "improves": bool(c_all.tau_ms > 0 and pick(c_all) < pick(c_0))})
        fr = pd.DataFrame(fold_rows)
        io.write_csv(out / f"heldout_folds_{m}.csv", fr)

        at_tau = ins[ins.tau_ms == best.tau_ms]
        wj, wc = at_tau.loc[at_tau.total.idxmin()].w, at_tau.loc[at_tau.choice_given_resp.idxmin()].w
        at0 = ins[ins.tau_ms == 0]
        wj0, wc0 = at0.loc[at0.total.idxmin()].w, at0.loc[at0.choice_given_resp.idxmin()].w
        c = {
            "mouse": m, "n_trials": len(rows), "n_added_v2_trials": n_added,
            "best_tau_ms": best.tau_ms, "best_w": best.w, "best_total": best.total,
            "best_tau0_w": best0.w, "best_tau0_total": best0.total, "best_taupos_tau_ms": bestp.tau_ms, "best_taupos_w": bestp.w,
            "improvement_seed50": imp[0], "improvement_seed51": imp[1], "improvement_mean": imp.mean(), "improvement_seed_sd": imp_sd,
            "heldout_folds_improved": int(fr.improves.sum()),
            "P0": all(v for k, v in p0[m].items() if isinstance(v, bool)) and p0[m]["unit_area_max_rel_err_tau100"] < 1e-3,
            "P1": bool(best.tau_ms > 0 and imp.mean() >= 10 and imp.mean() > 2 * imp_sd and fr.improves.sum() >= 4),
            "w_joint_at_best_tau": wj, "w_choice_at_best_tau": wc, "ratio_at_best_tau": wc / wj,
            "w_joint_tau0_v2": wj0, "w_choice_tau0_v2": wc0, "ratio_tau0_v2": wc0 / wj0,
            "P2": bool(wc / wj <= 1.5),
            "late_window_model_pp_at_best": late[(best.tau_ms, best.w)], "late_window_model_pp_best_tau0": late[(best0.tau_ms, best0.w)],
            "late_window_observed_pp": obs_late,
            "P3": bool(late[(best.tau_ms, best.w)] >= -1.0),
        }
        c["all_pass"] = bool(c["P0"] and c["P1"] and c["P2"] and c["P3"])
        crit.append(c)
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in c.items()}, flush=True)

    prof = pd.DataFrame(prof_rows)
    crit = pd.DataFrame(crit)
    n_pass = int(crit.all_pass.sum())
    decision = "PASS" if n_pass == len(crit) else ("MIXED" if n_pass > 0 else "FAIL")
    if not crit.P0.all():
        decision = "INVALID (P0 failed: implementation error)"
    # v1 (package E) vs v2 at tau_p = 0, same gains where E's grid overlaps
    eprof = pd.read_csv(run / "diagnostics" / "e2_e3_profiles.csv.gz")
    eprof = eprof[(eprof.baseline == "primary") & eprof.mouse.isin(spec["mice"]) & (eprof.seed == SEED) & (eprof.scope == "in_sample")]
    v = prof[(prof.tau_ms == 0) & (prof.scope == "in_sample")].merge(eprof[["mouse", "gain", "total", "choice_given_resp"]].rename(
        columns={"gain": "w", "total": "total_v1", "choice_given_resp": "choice_v1"}), on=["mouse", "w"], how="inner")
    v["total_v2_minus_v1"] = v.total - v.total_v1
    io.write_csv(out / "profiles.csv.gz", prof, compression="gzip")
    io.write_csv(out / "criteria.csv", crit)
    io.write_csv(out / "second_seed.csv", pd.DataFrame(seed_rows))
    io.write_csv(out / "v1_vs_v2_tau0.csv", v[["mouse", "w", "total", "total_v1", "total_v2_minus_v1", "choice_given_resp", "choice_v1"]])
    summary = {"decision": decision, "spec_sha256": SPEC_SHA, "criteria": crit.to_dict("records"),
               "v1_vs_v2_tau0_max_abs_total_diff": float(v.total_v2_minus_v1.abs().max()) if len(v) else None,
               "note": "exploratory pilot; in-sample grid plus fold held-out scoring on the same trials; 2 mice of one rig"}
    io.write_json(out / "summary.json", summary)
    checks = {"P0_all": bool(crit.P0.all()), "profiles_complete": len(prof) == len(spec["mice"]) * len(taus) * len(ws) * (1 + 2 * N_FOLDS),
              "no_empty_cells": bool((prof.empty_penalty == 0).all())}
    manifest = io.stage_manifest("models/tau_pilot", " ".join(["python -B -m scripts.pulse_followup.fit", *(argv or sys.argv[1:])]),
                                 {"spec": SPEC_SHA, "ddm_inputs_v2": spec["inputs"]["ddm_inputs_sha256"]},
                                 sorted(out.glob("*")), checks, timer.seconds, extra={"decision": decision})
    io.mark_complete(out, manifest, all(checks.values()))
    print(f"DECISION: {decision}; {timer.seconds} s")


if __name__ == "__main__":
    main()
