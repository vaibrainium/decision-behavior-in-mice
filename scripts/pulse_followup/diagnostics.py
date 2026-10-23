"""Package E: diagnose the existing model's pulse-trial failure (EXPLORATORY; plan section E, E1-E5).

Nothing here refits shared control parameters, reruns the closed primacy procedure as a test, or edits existing modules:
the control-only fits (ddm/fits_final), the amendment 6 pulse-gain pickles (ddm/primacy_revised) and the simulator /
likelihood are only called. The pulse gain w enters exactly as in scripts/ddm/fit_pulse_gain.py (two-channel
stimulus, noise_weight = w; w = 0 removes the pulse, w = 1 is the original model).

Sub-commands:
  simulate  --baseline B --seeds S [S ...] [--mice M ...]
            Re-simulate every pulse trial of each mouse on a gain grid with common random numbers, mirroring
            fit_pulse_gain.gain_nll_function (seed 50 = the stored all-trial profile seed, so the stored profile is
            reproduced exactly; other seeds are Monte Carlo replicates). Also simulates the mouse's control trials once
            (seed 12345) from the control fit. Writes <run>/diagnostics/sims/*.npz (refuses existing files).
  analyze   E1 checks, E2 decomposition and verification, E3 gain profiles / choice-only vs joint optima (in-sample and
            fold held-out), E4 comparison with packages C and D and control psychometric errors, E5 ranked mismatch
            summary, figures, manifest and (only if every check passes) COMPLETE.

Gain-profile labels: "in-sample" = all of a mouse's pulse trials; "fold-train" / "fold-test" = the stored amendment 6
folds (fold membership preserved from the pickles), with gains chosen on the training folds of this re-simulation.
All of it is exploratory.

Usage:
  NUMBA_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.diagnostics simulate \
      --run-id <RUN_ID> --baseline primary --seeds 50 1050 2050
  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.diagnostics analyze --run-id <RUN_ID>
"""

import argparse
import json
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import logit

from scripts.pulse_followup import io

STAGE = "diagnostics"
PROCESSED = Path("/mnt/data/processed")
DDM_INPUTS = PROCESSED / "ddm" / "ddm_inputs_global.npz"
FITS_FINAL = PROCESSED / "ddm" / "fits_final"
REVISED = PROCESSED / "ddm" / "primacy_revised"
EXTRA_GAINS = [0.25, 2.5, 6.0, 8.0, 12.0, 17.0, 24.0]
FIT_REPS = 50
STORED_SEED_OFFSET = 50  # fit_pulse_gain: all-trial profile uses seed + 50 with seed = 0
CONTROL_SEED = 12345
CONTROL_REPS = 50
MAX_ABS_COH = 0.36
U_GRID = np.round(np.arange(0, 4.58 + 1e-9, 0.02), 10)
DELTA = 1.92  # indicative only (QMLE, not a calibrated likelihood)
COMPONENTS = ["resp_censor", "choice_given_resp", "rt_left", "rt_right", "empty_penalty"]


def _ddm_imports():
    from scripts.ddm import fit_pulse_gain as fpg
    from scripts.ddm import primacy
    from scripts.ddm.fit_mouse_ddm import N_FOLDS, cv_folds, load_inputs, to_ms
    return primacy, fpg, N_FOLDS, cv_folds, load_inputs, to_ms


def load_revised(baseline, mouse):
    with open(REVISED / baseline / f"{mouse}.pkl", "rb") as f:
        return pickle.load(f)


def gain_grid(fpg, w_all):
    return np.array(sorted(set(map(float, fpg.GRID)) | set(EXTRA_GAINS) | {float(w_all)}))


# ------------------------------------------------------------------------------------------------------- simulate
def simulate(run_id, baseline, seeds, mice=None, control_only=False):
    primacy, fpg, _, _, load_inputs, to_ms = _ddm_imports()
    run = io.run_dir(run_id)
    io.load_config(run)
    sims = io.stage_dir(run, STAGE) / "sims"
    sims.mkdir(exist_ok=True)
    inputs = load_inputs(DDM_INPUTS)
    mice = mice or sorted(np.unique(inputs["subject_id"]))
    log = []
    for mouse in mice:
        pr = load_revised(baseline, mouse)
        params, variant, rig = pr["params"], pr["variant"], pr["rig"]
        rows = primacy.pulse_rows(inputs, mouse)
        gains = gain_grid(fpg, pr["pulse_gain_all"])
        for seed in ([] if control_only else seeds):
            path = sims / f"{baseline}_{mouse}_s{seed}.npz"
            if path.exists():
                raise FileExistsError(f"refusing to overwrite {path}")
            t0 = time.time()
            model = primacy.make_model(variant, rig)
            without, pulse = primacy.gain_stimuli(inputs, rows)
            cond = inputs["condition"][rows]
            np.random.seed(seed)  # identical sequence to fit_pulse_gain.gain_nll_function
            model.simulator.clear_cache()
            model._labels = cond
            model.precompute(*without.shape, n_reps=FIT_REPS)
            t_pre = time.time() - t0
            n = len(rows)
            rt = np.empty((len(gains), FIT_REPS, n), np.float32)
            ch = np.empty((len(gains), FIT_REPS, n), np.int8)
            t_sim = []
            for gi, w in enumerate(gains):
                t1 = time.time()
                res = model._simulate_condition((without, pulse), {**params, "noise_weight": float(w)}, FIT_REPS)
                if res is None or len(res) != FIT_REPS * n:
                    raise RuntimeError(f"{mouse} w={w}: simulation returned {None if res is None else len(res)} rows")
                lab = res["signed_coherence"].to_numpy().reshape(FIT_REPS, n)
                if not (lab == cond[None, :]).all():
                    raise RuntimeError("simulated label order differs from the trial order")
                rt[gi] = res["rt"].to_numpy().reshape(FIT_REPS, n)
                ch[gi] = res["choice"].to_numpy().reshape(FIT_REPS, n)
                t_sim.append(time.time() - t1)
            model.simulator.clear_cache()
            del model
            np.savez_compressed(path, gains=gains, rt=rt, choice=ch, rows=rows, seed=seed, n_reps=FIT_REPS)
            rec = {"baseline": baseline, "mouse": mouse, "seed": seed, "n_trials": n, "n_gains": len(gains),
                   "precompute_s": round(t_pre, 2), "sim_s_per_gain_mean": round(float(np.mean(t_sim)), 3),
                   "total_s": round(time.time() - t0, 2)}
            log.append(rec)
            print(json.dumps(rec), flush=True)
        # control trials, once per baseline and mouse (independent of seeds argument)
        cpath = sims / f"control_{baseline}_{mouse}.npz"
        if not cpath.exists():
            t0 = time.time()
            crow = np.flatnonzero((inputs["subject_id"] == mouse) & (inputs["sched_pulse_type"] == 0))
            model = primacy.make_model(variant, rig)
            stim = to_ms(inputs["signal"][crow] + inputs["noise"][crow], int(inputs["frame_rate"]))
            sim = primacy.simulate_outcomes(model, params, stim, inputs["condition"][crow], CONTROL_REPS, CONTROL_SEED)
            sim = sim.sort_values(["rep", "trial"])
            if len(sim) != CONTROL_REPS * len(crow):
                raise RuntimeError("control simulation lost rows")
            np.savez_compressed(cpath, rows=crow, rt=sim.rt.to_numpy(np.float32).reshape(CONTROL_REPS, -1),
                                choice=sim.choice.to_numpy().astype(np.int8).reshape(CONTROL_REPS, -1), seed=CONTROL_SEED)
            rec = {"baseline": baseline, "mouse": mouse, "control_trials": len(crow), "control_sim_s": round(time.time() - t0, 2)}
            log.append(rec)
            print(json.dumps(rec), flush=True)
    io.write_json(sims / f"timing_{baseline}_{'-'.join(map(str, seeds))}_{len(mice)}mice_{int(time.time())}.json", log)


# ------------------------------------------------------------------------------------------------- decomposition
def decompose(lik, rt_pred, ch_pred, cond_pred, rt_data, ch_data, cond_data):
    """CensoredQMLE.compute_nll split into exact parts (same smoothing, bins, <nbins rule, empty-cell penalty and
    weight). The three-outcome multinomial term is split by the chain rule on the same smoothed probabilities:
    -sum n_k log p_k = -[n_resp log(p0+p1) + n_c log p_c] - [n0 log(p0/(p0+p1)) + n1 log(p1/(p0+p1))]."""
    from src.ddm.likelihood_calculator_censored import CENSORED, EMPTY_CELL_PENALTY

    out = dict.fromkeys(COMPONENTS, 0.0)
    a = lik.alpha
    for c in np.unique(cond_data):
        d, m = cond_data == c, cond_pred == c
        n = np.array([(ch_data[d] == k).sum() for k in (0, 1, CENSORED)], float)
        mc = np.array([(ch_pred[m] == k).sum() for k in (0, 1, CENSORED)], float)
        if mc.sum() == 0:
            out["empty_penalty"] += EMPTY_CELL_PENALTY * n.sum()
            continue
        p = (mc + a) / (mc.sum() + a * 3)
        pr = p[0] + p[1]
        out["resp_censor"] += -((n[0] + n[1]) * np.log(pr) + n[2] * np.log(p[2]))
        out["choice_given_resp"] += -(n[0] * np.log(p[0] / pr) + n[1] * np.log(p[1] / pr))
        for k, name in ((0, "rt_left"), (1, "rt_right")):
            rt_d = rt_data[d & (ch_data == k)]
            if len(rt_d):
                out[name] += lik.rt_nllh_weight * lik._rt_nll(rt_d, rt_pred[m & (ch_pred == k)])
    out["total"] = sum(out[k] for k in COMPONENTS)
    return out


# ------------------------------------------------------------------------------------------------------- analyze
def analyze(run_id):
    timer = io.Timer()
    primacy, fpg, N_FOLDS, cv_folds, load_inputs, _ = _ddm_imports()
    from src.ddm.likelihood_calculator_censored import CensoredQMLE
    from scripts.ddm.fit_mouse_ddm import LIKELIHOOD_PARAMS
    from scripts.pulse_followup import response_time as rtm

    run = io.run_dir(run_id)
    t, cfg = io.load_trials(run)
    out = io.stage_dir(run, STAGE)
    sims_dir = out / "sims"
    inputs = load_inputs(DDM_INPUTS)
    lik = CensoredQMLE(nbins=LIKELIHOOD_PARAMS["nbins"], rt_nllh_weight=LIKELIHOOD_PARAMS["rt_nllh_weight"])
    mice = sorted(np.unique(inputs["subject_id"]))
    checks, outputs = {}, []
    import re
    sim_files = sorted(p.name for p in sims_dir.glob("*.npz") if re.fullmatch(r"(primary|secondary)_[A-Za-z0-9]+_s\d+\.npz", p.name))
    avail = {}
    for name in sim_files:
        b, m, s = name[:-4].rsplit("_", 2)
        avail.setdefault(b, {}).setdefault(m, []).append(int(s[1:]))
    baselines = sorted(avail)
    checks["simulations_present"] = {b: {m: sorted(v) for m, v in avail[b].items()} for b in baselines}
    checks["all_mice_simulated_seed50"] = all(set(mice) <= {m for m, v in avail[b].items() if 50 in v} for b in baselines)

    # ------------------------------------------------------------------------------------------------------ E1
    tt = t.set_index("trial_id")
    e1 = {}
    ddm = pd.DataFrame({"trial_id": inputs["agg_code"], "mouse": inputs["subject_id"], "sched": inputs["sched_pulse_type"],
                        "choice": inputs["choice"], "rt": inputs["rt"], "coh": inputs["signed_coherence"]})
    ddm = ddm.join(tt[["pulse_category", "pulse_sign", "onset_stratum", "rig", "signs_scheduled_symmetric", "in_ddm_input",
                       "response_side", "rt_s", "recorded_onset_s", "session", "coherence_pct"]], on="trial_id")
    e1["ddm_rows_all_in_A_table"] = bool(ddm.pulse_category.notna().all())
    e1["ddm_rows_equal_A_in_ddm_input"] = int(ddm.in_ddm_input.sum()) == len(ddm) == int(t.in_ddm_input.sum())
    e1["ddm_outcomes_match_A"] = bool(((ddm.choice.map({1: "R", 0: "L", -1: "none"}) == ddm.response_side)).all()
                                      and np.allclose(ddm.rt[ddm.choice >= 0], ddm.rt_s[ddm.choice >= 0]))
    xt = pd.crosstab([ddm.rig, ddm.pulse_category], ddm.sched)
    outputs.append(io.write_csv(out / "e1_label_crosstab.csv", xt.reset_index()))
    mis = ddm[(ddm.sched == 0) & ddm.pulse_category.isin(["positive", "negative", "pulse_direction_unknown"])]
    e1["mislabelled_as_control_in_ddm"] = mis.groupby(["mouse", "pulse_category"]).size().rename("n").reset_index().to_dict("records")
    e1["mislabelled_all_unresponded"] = bool((mis.choice == -1).all())
    e1["ddm_sign_and_timing_agree_with_A_where_pulse"] = bool(
        ((np.sign(ddm.sched) == ddm.pulse_sign) | (ddm.sched == 0)).all()
        and (ddm[ddm.sched != 0].onset_stratum.to_numpy() == np.array(["early", "middle", "late"])[np.abs(ddm[ddm.sched != 0].sched) - 1]).all())
    # impact of the mislabel on the two comparisons
    imp = []
    for m in mice:
        dm = ddm[ddm.mouse == m]
        pul = dm[dm.sched != 0]
        ctl = dm[dm.sched == 0]
        k = (mis.mouse == m).sum()
        kg = ((mis.mouse == m) & mis.pulse_category.isin(["positive", "negative"])).sum()
        imp.append({"mouse": m, "n_pulse_rows_ddm": len(pul), "n_mislabelled": int(k), "n_genuine_mislabelled": int(kg),
                    "pulse_censored_frac_ddm": float((pul.choice == -1).mean()),
                    "pulse_censored_frac_corrected": float(((pul.choice == -1).sum() + kg) / (len(pul) + kg)) if len(pul) else np.nan,
                    "control_censored_frac_ddm": float((ctl.choice == -1).mean()),
                    "control_censored_frac_corrected": float(((ctl.choice == -1).sum() - k) / (len(ctl) - k))})
    imp = pd.DataFrame(imp)
    outputs.append(io.write_csv(out / "e1_mislabel_impact.csv", imp))
    e1["max_abs_change_pulse_censored_frac"] = float((imp.pulse_censored_frac_corrected - imp.pulse_censored_frac_ddm).abs().max())
    e1["max_abs_change_control_censored_frac"] = float((imp.control_censored_frac_corrected - imp.control_censored_frac_ddm).abs().max())
    # asymmetric UW cells in the ddm pulse rows
    e1["ddm_pulse_rows_in_asymmetric_cells"] = int(((ddm.sched != 0) & ~ddm.signs_scheduled_symmetric).sum())
    # stored predictions: same rows, folds, parameters
    rows_ok, folds_ok, params_ok, commits = True, True, True, set()
    fold_of = {}
    for b in ("primary", "secondary"):
        for m in mice:
            pr = load_revised(b, m)
            rows = primacy.pulse_rows(inputs, m)
            rows_ok &= bool((pr["trials"].row.to_numpy() == rows).all() and pr["trials"].row.is_unique)
            f = cv_folds(inputs["condition"][rows], N_FOLDS)
            folds_ok &= bool((pr["trials"].fold.to_numpy() == f).all())
            fit = primacy.load_fit(FITS_FINAL, m, pr["variant"], "control", False)
            params_ok &= all(np.isclose(fit["parameters"][k], v) for k, v in pr["params"].items() if k != "noise_weight")
            commits.add(pr["commit"])
            fold_of[(b, m)] = f
    e1.update({"stored_pred_rows_equal_pulse_rows": rows_ok, "stored_folds_reproduced_by_cv_folds": folds_ok,
               "stored_params_equal_fits_final_control": params_ok, "stored_prediction_commits": sorted(commits)})
    for k in ("ddm_rows_all_in_A_table", "ddm_rows_equal_A_in_ddm_input", "ddm_outcomes_match_A", "mislabelled_all_unresponded",
              "ddm_sign_and_timing_agree_with_A_where_pulse", "stored_pred_rows_equal_pulse_rows", "stored_folds_reproduced_by_cv_folds",
              "stored_params_equal_fits_final_control"):
        checks[f"e1_{k}"] = e1[k]
    outputs.append(io.write_json(out / "e1_checks.json", e1))

    # ------------------------------------------------------------------------------------------- E2 / E3 profiles
    prof_rows, summ_rows = [], []
    sims_cache = {}
    for b in baselines:
        for m in mice:
            pr = load_revised(b, m)
            rows = primacy.pulse_rows(inputs, m)
            rt_d, ch_d, cond = inputs["rt"][rows], inputs["choice"][rows], inputs["condition"][rows]
            folds = fold_of[(b, m)]
            direction = np.sign(inputs["sched_pulse_type"][rows])
            coh = inputs["signed_coherence"][rows]
            low = np.abs(coh) <= MAX_ABS_COH + 1e-9
            for seed in sorted(avail[b].get(m, [])):
                z = np.load(sims_dir / f"{b}_{m}_s{seed}.npz")
                gains, rt_s, ch_s = z["gains"], z["rt"], z["choice"]
                R = rt_s.shape[1]
                sims_cache[(b, m, seed)] = (gains, rt_s, ch_s)
                scopes = {"in_sample": np.ones(len(rows), bool)}
                for k in range(N_FOLDS):
                    scopes[f"train{k}"] = folds != k
                    scopes[f"test{k}"] = folds == k
                for gi, w in enumerate(gains):
                    rp, cp = rt_s[gi].ravel(), ch_s[gi].ravel().astype(int)
                    cp_cond = np.tile(cond, R)
                    for sc, sel in scopes.items():
                        selp = np.tile(sel, R)
                        dcp = decompose(lik, rp[selp], cp[selp], cp_cond[selp], rt_d[sel], ch_d[sel], cond[sel])
                        rec = {"baseline": b, "mouse": m, "seed": seed, "scope": sc, "gain": w, **dcp}
                        if sc == "in_sample":
                            rec["compute_nll"] = lik.compute_nll(rp, cp, rt_d, ch_d, cp_cond, cond)
                            rec["stored_profile_all"] = pr["profile_all"].get(float(w), np.nan) if seed == STORED_SEED_OFFSET else np.nan
                        prof_rows.append(rec)
                    # E3 summaries vs gain (pulse trials, |coh| <= 36)
                    toward = (ch_s[gi] == 1) == (direction[None, :] > 0)
                    resp = ch_s[gi] >= 0
                    tow_rt = np.where(resp & toward & low[None, :], rt_s[gi], np.nan)
                    ag_rt = np.where(resp & ~toward & low[None, :], rt_s[gi], np.nan)
                    corr = (ch_s[gi] == 1) == (coh[None, :] > 0)
                    nz = low & (coh != 0)
                    summ_rows.append({
                        "baseline": b, "mouse": m, "seed": seed, "gain": w, "source": "model",
                        "p_toward_given_resp": float((resp & toward)[:, low].sum() / resp[:, low].sum()),
                        "p_censored": float(1 - resp[:, low].mean()),
                        **{f"rt_toward_q{int(q * 100)}": float(np.nanquantile(tow_rt, q)) for q in (0.1, 0.5, 0.9)},
                        **{f"rt_against_q{int(q * 100)}": float(np.nanquantile(ag_rt, q)) for q in (0.1, 0.5, 0.9)},
                        "rt_correct_mean": float(np.nanmean(np.where(resp & corr & nz[None, :], rt_s[gi], np.nan))),
                        "rt_error_mean": float(np.nanmean(np.where(resp & ~corr & nz[None, :], rt_s[gi], np.nan))),
                    })
            # observed summaries (once per baseline/mouse)
            resp_o = ch_d >= 0
            tow_o = (ch_d == 1) == (direction > 0)
            corr_o = (ch_d == 1) == (coh > 0)
            nz = low & (coh != 0)
            summ_rows.append({
                "baseline": b, "mouse": m, "seed": -1, "gain": np.nan, "source": "observed",
                "p_toward_given_resp": float((resp_o & tow_o & low).sum() / (resp_o & low).sum()),
                "p_censored": float(1 - resp_o[low].mean()),
                **{f"rt_toward_q{int(q * 100)}": float(np.quantile(rt_d[resp_o & tow_o & low], q)) for q in (0.1, 0.5, 0.9)},
                **{f"rt_against_q{int(q * 100)}": float(np.quantile(rt_d[resp_o & ~tow_o & low], q)) for q in (0.1, 0.5, 0.9)},
                "rt_correct_mean": float(rt_d[resp_o & corr_o & nz].mean()), "rt_error_mean": float(rt_d[resp_o & ~corr_o & nz].mean()),
            })
    prof = pd.DataFrame(prof_rows)
    summ = pd.DataFrame(summ_rows)
    outputs.append(io.write_csv(out / "e2_e3_profiles.csv.gz", prof, compression="gzip"))
    outputs.append(io.write_csv(out / "e3_summaries_vs_gain.csv", summ))
    ins = prof[prof.scope == "in_sample"]
    checks["e2_components_sum_to_compute_nll_max_abs"] = float((ins.total - ins.compute_nll).abs().max())
    checks["e2_components_sum_to_compute_nll"] = checks["e2_components_sum_to_compute_nll_max_abs"] < 1e-6
    st = ins[ins.stored_profile_all.notna()]
    checks["e2_stored_profile_points_compared"] = int(len(st))
    checks["e2_stored_profile_reproduced_max_abs"] = float((st.total - st.stored_profile_all).abs().max()) if len(st) else np.nan
    checks["e2_stored_profile_exact_fraction"] = float(((st.total - st.stored_profile_all).abs() < 1e-6).mean()) if len(st) else np.nan
    # Stored profiles were computed with the GPU torch backend on Hyak; this CPU numba backend can move a few bound
    # crossings by one step. Tolerance 0.5 NLL (below the 1.92 band) set after attempt 1 (see attempt1_superseded/).
    checks["e2_stored_profile_reproduced_within_0.5"] = bool(len(st) > 0 and checks["e2_stored_profile_reproduced_max_abs"] < 0.5)
    # fold scopes: train + test must sum? (no: smoothing per subset) -> only check in-sample identity
    checks["e2_no_empty_cells"] = bool((prof.empty_penalty == 0).all())
    # how much of the data the RT term actually sees: (cell, choice) groups with < nbins data RTs score 0 for every model
    cov = []
    for m in mice:
        rows = primacy.pulse_rows(inputs, m)
        dfc = pd.DataFrame({"cond": inputs["condition"][rows], "ch": inputs["choice"][rows]})
        dfc = dfc[dfc.ch >= 0]
        n = dfc.groupby(["cond", "ch"]).size()
        cov.append({"mouse": m, "n_cells": int(dfc.cond.nunique()), "n_responded": int(n.sum()),
                    "frac_responded_in_rt_term": float(n[n >= lik.nbins].sum() / n.sum()),
                    "n_cell_choice_groups": int(len(n)), "n_groups_scored": int((n >= lik.nbins).sum())})
    cov = pd.DataFrame(cov)
    outputs.append(io.write_csv(out / "e2_rt_term_coverage.csv", cov))

    # ---------------------------------------------------------------------------------------------- E3 optima
    prof["rest"] = prof.resp_censor + prof.rt_left + prof.rt_right + prof.empty_penalty
    prof["rt"] = prof.rt_left + prof.rt_right
    opt_rows = []
    for (b, m, seed, sc), g in prof[~prof.scope.str.startswith("test")].groupby(["baseline", "mouse", "seed", "scope"]):
        g = g.sort_values("gain")
        wj = g.gain.iloc[g.total.argmin()]
        wc = g.gain.iloc[g.choice_given_resp.argmin()]
        wr = g.gain.iloc[g.rt.argmin()]
        wrc = g.gain.iloc[g.resp_censor.argmin()]
        gj, gc = g[g.gain == wj].iloc[0], g[g.gain == wc].iloc[0]
        rec = {"baseline": b, "mouse": m, "seed": seed, "scope": sc, "w_joint": wj, "w_choice_only": wc, "w_rt_only": wr, "w_resp_only": wrc,
               "choice_gain_at_wc_vs_wj": gj.choice_given_resp - gc.choice_given_resp,
               "rest_cost_at_wc_vs_wj": gc.rest - gj.rest, "rt_cost_at_wc_vs_wj": gc.rt - gj.rt,
               "resp_cost_at_wc_vs_wj": gc.resp_censor - gj.resp_censor,
               "choice_at_w1_minus_min": g[g.gain == 1.0].choice_given_resp.iloc[0] - g.choice_given_resp.min(),
               "total_at_w1_minus_min": g[g.gain == 1.0].total.iloc[0] - g.total.min()}
        if sc.startswith("train"):
            k = int(sc[5:])
            te = prof[(prof.baseline == b) & (prof.mouse == m) & (prof.seed == seed) & (prof.scope == f"test{k}")]
            tj, tc = te[te.gain == wj].iloc[0], te[te.gain == wc].iloc[0]
            rec.update({"test_choice_at_wj_minus_wc": tj.choice_given_resp - tc.choice_given_resp,
                        "test_rest_at_wc_minus_wj": tc.rest - tj.rest, "test_total_at_wc_minus_wj": tc.total - tj.total,
                        "stored_fold_gain": load_revised(b, m)["fold_gain"][k]})
        opt_rows.append(rec)
    opt = pd.DataFrame(opt_rows)
    outputs.append(io.write_csv(out / "e3_optima.csv", opt))

    # per-mouse tradeoff verdict (rule fixed in code before results were seen; indicative QMLE units)
    verdict = []
    for (b, m), g in opt[opt.scope == "in_sample"].groupby(["baseline", "mouse"]):
        f = opt[(opt.baseline == b) & (opt.mouse == m) & opt.scope.str.startswith("train")]
        seeds_dir = (g.w_choice_only > g.w_joint).all()
        demonstrated = bool(seeds_dir and (g.choice_gain_at_wc_vs_wj > DELTA).all() and (g.rest_cost_at_wc_vs_wj > DELTA).all()
                            and f.test_choice_at_wj_minus_wc.groupby(f.seed).sum().gt(0).all()
                            and f.test_rest_at_wc_minus_wj.groupby(f.seed).sum().gt(0).all())
        verdict.append({"baseline": b, "mouse": m, "n_seeds": len(g),
                        "w_joint_seeds": ";".join(f"{x:.2f}" for x in g.w_joint), "w_choice_seeds": ";".join(f"{x:.2f}" for x in g.w_choice_only),
                        "choice_gain_mean": g.choice_gain_at_wc_vs_wj.mean(), "rest_cost_mean": g.rest_cost_at_wc_vs_wj.mean(),
                        "rt_cost_mean": g.rt_cost_at_wc_vs_wj.mean(), "resp_cost_mean": g.resp_cost_at_wc_vs_wj.mean(),
                        "heldout_choice_gain_sum_mean": f.test_choice_at_wj_minus_wc.groupby(f.seed).sum().mean(),
                        "heldout_rest_cost_sum_mean": f.test_rest_at_wc_minus_wj.groupby(f.seed).sum().mean(),
                        "heldout_total_cost_sum_mean": f.test_total_at_wc_minus_wj.groupby(f.seed).sum().mean(),
                        "fold_w_joint_range": f"{f.w_joint.min():.2f}-{f.w_joint.max():.2f}",
                        "fold_w_choice_range": f"{f.w_choice_only.min():.2f}-{f.w_choice_only.max():.2f}",
                        "stored_fold_gain_range": f"{f.stored_fold_gain.min():.2f}-{f.stored_fold_gain.max():.2f}",
                        "tradeoff": "demonstrated" if demonstrated else ("suspected" if seeds_dir else "not_supported")})
    verdict = pd.DataFrame(verdict)
    outputs.append(io.write_csv(out / "e3_tradeoff_verdict.csv", verdict))

    # MC stability of the in-sample profile (seed SD of total and components at each gain, relative to the min)
    mc = []
    for (b, m), g in ins.groupby(["baseline", "mouse"]):
        if g.seed.nunique() < 2:
            continue
        rel = g.assign(**{c: g[c] - g.groupby("seed")[c].transform("min") for c in ["total", "choice_given_resp"]})
        s = rel.groupby("gain")[["total", "choice_given_resp"]].std()
        mc.append({"baseline": b, "mouse": m, "n_seeds": g.seed.nunique(), "max_seed_sd_rel_total": s.total.max(),
                   "median_seed_sd_rel_total": s.total.median(), "max_seed_sd_rel_choice": s.choice_given_resp.max()})
    mc = pd.DataFrame(mc)
    outputs.append(io.write_csv(out / "e4_mc_stability.csv", mc))

    # ------------------------------------------------------------------------------- E4a: model vs D curves
    dset = ddm[(ddm.sched != 0) & ddm.signs_scheduled_symmetric & (ddm.coherence_pct.abs() <= 36)
               & ddm.pulse_category.isin(["positive", "negative"])].copy()
    dset["row"] = dset.index.to_numpy()
    a = pd.DataFrame({"trial_id": dset.trial_id.to_numpy(), "mouse": dset.mouse.to_numpy(), "session": dset.session.to_numpy(),
                      "coherence_pct": dset.coherence_pct.to_numpy(), "onset_stratum": dset.onset_stratum.to_numpy(),
                      "arm": dset.pulse_category.to_numpy(), "onset": dset.recorded_onset_s.to_numpy(), "row": dset.row.to_numpy(),
                      "side": dset.response_side.to_numpy(), "rt": dset.rt_s.to_numpy()})
    a["u"] = a.rt - a.onset
    aw = rtm.cell_weights(a, ("positive", "negative"))

    def curves_obs(df):
        res = {}
        for (m, arm), g in df.groupby(["mouse", "arm"]):
            res[(m, arm)] = rtm.curves_for(g, U_GRID)
        return res

    def direction_common(cur, cur0=None):
        out_ = {}
        for m in sorted({k[0] for k in cur}):
            p, n = cur[(m, "positive")], cur[(m, "negative")]
            d_ = {"direction": ((p["cif_R"] - n["cif_R"]) - (p["cif_L"] - n["cif_L"])) / 2,
                  "d_survival": p["survival"] - n["survival"]}
            if cur0 is not None:
                p0, n0 = cur0[(m, "positive")], cur0[(m, "negative")]
                d_["common_responded"] = ((p0["survival"] + n0["survival"]) - (p["survival"] + n["survival"])) / 2
            out_[m] = d_
        return out_

    obs_dc = direction_common(curves_obs(aw))
    # D's official values for comparison (includes the recovered trials)
    dcon = pd.read_csv(run / "response_time" / "contrast_curves_per_mouse.csv.gz")
    dcon = dcon[(dcon.summary == "all_scheduled") & (dcon.onset_stratum == "all")]
    curve_rows = []
    for m, d_ in obs_dc.items():
        for qn, v in d_.items():
            curve_rows.append(pd.DataFrame({"source": "observed_ddm_rows", "baseline": "", "gain_label": "", "gain": np.nan, "mouse": m,
                                            "quantity": qn, "u": U_GRID, "value": v}))
    for b in baselines:
        for m in mice:
            if (b, m, STORED_SEED_OFFSET) not in sims_cache:
                continue
            gains, rt_s, ch_s = sims_cache[(b, m, STORED_SEED_OFFSET)]
            rows = primacy.pulse_rows(inputs, m)
            pos = {r: i for i, r in enumerate(rows)}
            am = aw[aw.mouse == m]
            idx = am.row.map(pos).to_numpy()
            R = rt_s.shape[1]
            g_ins = opt[(opt.baseline == b) & (opt.mouse == m) & (opt.scope == "in_sample") & (opt.seed == STORED_SEED_OFFSET)].iloc[0]
            labels = {"w0": 0.0, "w1": 1.0, "w_all_stored": float(load_revised(b, m)["pulse_gain_all"]),
                      "w_choice_only": float(g_ins.w_choice_only), "w10": 10.0, "w20": 20.0}

            def model_cur(gi):
                rtm_ = rt_s[gi][:, idx].astype(float)
                chm = ch_s[gi][:, idx]
                df = pd.DataFrame({"mouse": m, "arm": np.tile(am.arm.to_numpy(), R),
                                   "u": np.where(chm.ravel() >= 0, rtm_.ravel() - np.tile(am.onset.to_numpy(), R), np.nan),
                                   "side": np.where(chm.ravel() == 1, "R", np.where(chm.ravel() == 0, "L", "none")),
                                   "wt": np.tile(am.wt.to_numpy(), R) / R})
                return curves_obs(df)
            c0 = model_cur(int(np.argmin(np.abs(gains - 0.0))))
            for lab, w in labels.items():
                gi = int(np.argmin(np.abs(gains - w)))
                dc = direction_common(model_cur(gi), c0)[m]
                for qn, v in dc.items():
                    curve_rows.append(pd.DataFrame({"source": "model", "baseline": b, "gain_label": lab, "gain": gains[gi], "mouse": m,
                                                    "quantity": qn, "u": U_GRID, "value": v}))
    mcurves = pd.concat(curve_rows, ignore_index=True)
    outputs.append(io.write_csv(out / "e4_model_vs_D_curves.csv.gz", mcurves, compression="gzip"))

    # summary at key times / windows, mean across mice with t-interval
    def tci(x):
        x = np.asarray(x, float)
        x = x[~np.isnan(x)]
        n = len(x)
        if n < 2:
            return n, np.nan, np.nan, np.nan
        h = stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)
        return n, x.mean(), x.mean() - h, x.mean() + h

    keyrows = []
    def at(v, u):
        return v[int(np.argmin(np.abs(U_GRID - u)))]
    for (src, b, lab, qn), g in mcurves.groupby(["source", "baseline", "gain_label", "quantity"]):
        per = {m: gm.value.to_numpy() for m, gm in g.groupby("mouse")}
        feats = {}
        for u in (0.5, 1.0, 2.0, 4.58):
            feats[f"@{u:g}"] = {m: at(v, u) for m, v in per.items()}
        for lo, hi in ((0.0, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 4.58)):
            feats[f"window_{lo:g}-{hi:g}"] = {m: at(v, hi) - at(v, lo) for m, v in per.items()}
        feats["peak_u"] = {m: U_GRID[int(np.argmax(v))] for m, v in per.items()}
        for fn, vals in feats.items():
            n, mu, lo_, hi_ = tci(list(vals.values()))
            keyrows.append({"source": src, "baseline": b, "gain_label": lab, "quantity": qn, "feature": fn, "n_mice": n,
                            "mean": mu, "ci_low": lo_, "ci_high": hi_, **{f"mouse_{m}": v for m, v in vals.items()}})
    keytab = pd.DataFrame(keyrows)
    outputs.append(io.write_csv(out / "e4_model_vs_D_summary.csv", keytab))
    # agreement of the restricted observed set with D's official per-mouse curves (E1 impact on D's comparison)
    off = dcon[dcon.comparison == "pos_vs_neg"].pivot_table(index="mouse", columns="t", values="d_direction")
    mine = {m: at(v["direction"], 4.58) for m, v in obs_dc.items()}
    e1_d = {m: float(mine[m] - off.loc[m, off.columns[np.argmin(np.abs(off.columns - 4.58))]]) for m in mine}
    checks["e4_observed_ddm_rows_vs_D_official_direction@4.58_max_abs_diff"] = float(np.max(np.abs(list(e1_d.values()))))

    # ------------------------------------------------------------------------- E4b: control psychometric errors
    ctl_rows = []
    for b in baselines:
        for m in mice:
            cp = sims_dir / f"control_{b}_{m}.npz"
            if not cp.exists():
                continue
            z = np.load(cp)
            crow, rt_c, ch_c = z["rows"], z["rt"], z["choice"]
            coh = inputs["signed_coherence"][crow]
            ch_o, rt_o = inputs["choice"][crow], inputs["rt"][crow]
            for c in np.unique(coh):
                s = coh == c
                ro, rp = ch_o[s] >= 0, ch_c[:, s] >= 0
                ctl_rows.append({"baseline": b, "mouse": m, "coh": c, "n": int(s.sum()),
                                 "obs_p_right_given_resp": (ch_o[s] == 1).sum() / max(ro.sum(), 1),
                                 "pred_p_right_given_resp": (ch_c[:, s] == 1).sum() / max(rp.sum(), 1),
                                 "obs_p_censored": 1 - ro.mean(), "pred_p_censored": 1 - rp.mean(),
                                 "obs_mean_rt": rt_o[s][ro].mean() if ro.any() else np.nan,
                                 "pred_mean_rt": float(np.nanmean(np.where(rp, rt_c[:, s], np.nan)))})
    ctl = pd.DataFrame(ctl_rows)
    outputs.append(io.write_csv(out / "e4_control_psychometric.csv", ctl))

    # pulse-trial departures with/against coherence from the stored out-of-fold predictions (held-out gains)
    dep_rows = []
    eps = 1e-3
    for b in ("primary", "secondary"):
        for m in mice:
            tr = load_revised(b, m)["trials"]
            tr = tr.assign(ch=inputs["choice"][tr.row], y=lambda x: np.where(x.ch >= 0, ((x.ch == 1) == (x.direction > 0)).astype(float), np.nan))
            tr = tr[(tr.ch >= 0) & (tr.coh.abs() <= MAX_ABS_COH + 1e-9)]
            rel = np.where(tr.coh == 0, "zero", np.where(np.sign(tr.coh) == tr.direction, "with", "against"))
            for r in ("zero", "with", "against"):
                g = tr[rel == r]
                dep_rows.append({"baseline": b, "mouse": m, "relation": r, "n": len(g),
                                 "obs_p_toward": g.y.mean(), "pred_p_toward_oof": g.p_hat.mean(),
                                 "pred_p_toward_nopulse": g.nopulse_p_hat.mean(),
                                 "departure_logit": logit(np.clip(g.y.mean(), eps, 1 - eps)) - logit(np.clip(g.p_hat.mean(), eps, 1 - eps))})
    dep = pd.DataFrame(dep_rows)
    # control-trial coherence-slope departure (toward the coherence direction), |coh| in 9, 18, 36
    cs = []
    for (b, m), g in ctl.groupby(["baseline", "mouse"]):
        g = g[(g.coh.abs() > 0) & (g.coh.abs() <= MAX_ABS_COH + 1e-9)]
        po = np.where(g.coh > 0, g.obs_p_right_given_resp, 1 - g.obs_p_right_given_resp)
        pp = np.where(g.coh > 0, g.pred_p_right_given_resp, 1 - g.pred_p_right_given_resp)
        w = g.n.to_numpy()
        cs.append({"baseline": b, "mouse": m, "control_coh_departure_logit":
                   float(logit(np.clip(np.average(po, weights=w), eps, 1 - eps)) - logit(np.clip(np.average(pp, weights=w), eps, 1 - eps)))})
    cs = pd.DataFrame(cs)
    dw = dep.pivot_table(index=["baseline", "mouse"], columns="relation", values="departure_logit").reset_index()
    dw = dw.merge(cs, on=["baseline", "mouse"], how="left")
    dw["pulse_excess_additive"] = (dw["with"] + dw["against"]) / 2  # coherence-slope misfit cancels in the average
    dw["coh_slope_excess_pulse_trials"] = (dw["with"] - dw["against"]) / 2
    outputs.append(io.write_csv(out / "e4_departure_decomposition.csv", dw))
    outputs.append(io.write_csv(out / "e4_departure_by_relation.csv", dep))

    # ---------------------------------------------------------------------------------------------- E5 summary
    ks = keytab.set_index(["source", "baseline", "gain_label", "quantity", "feature"])

    def kv(src, b, lab, q, f):
        try:
            r = ks.loc[(src, b, lab, q, f)]
            return {"mean": float(r["mean"]), "ci_low": float(r.ci_low), "ci_high": float(r.ci_high), "n_mice": int(r.n_mice)}
        except KeyError:
            return None
    e5 = {"status": "EXPLORATORY", "units": "probabilities (x100 = pp); QMLE NLL units (indicative); seconds",
          "observed_same_rows": {f: kv("observed_ddm_rows", "", "", "direction", f) for f in ("@1", "@4.58", "window_0.5-1", "window_1-2", "window_2-4.58")},
          "observed_same_rows_d_survival@4.58": kv("observed_ddm_rows", "", "", "d_survival", "@4.58"),
          "model": {}}
    for b in baselines:
        e5["model"][b] = {}
        for lab in ("w1", "w_all_stored", "w_choice_only", "w10", "w20"):
            e5["model"][b][lab] = {
                "direction@4.58": kv("model", b, lab, "direction", "@4.58"),
                "direction_window_0-0.5": kv("model", b, lab, "direction", "window_0-0.5"),
                "direction_window_0.5-1": kv("model", b, lab, "direction", "window_0.5-1"),
                "direction_window_1-2": kv("model", b, lab, "direction", "window_1-2"),
                "direction_peak_u": kv("model", b, lab, "direction", "peak_u"),
                "common_responded@1": kv("model", b, lab, "common_responded", "@1"),
                "common_responded@4.58": kv("model", b, lab, "common_responded", "@4.58"),
                "d_survival@4.58": kv("model", b, lab, "d_survival", "@4.58")}
    vs = verdict.groupby(["baseline", "tradeoff"]).size().unstack(fill_value=0)
    e5["tradeoff_counts"] = vs.reset_index().to_dict("records")
    e5["departure_decomposition_means"] = dw.groupby("baseline")[["zero", "with", "against", "pulse_excess_additive",
                                                                  "coh_slope_excess_pulse_trials", "control_coh_departure_logit"]].mean().to_dict("index")
    corr = {}
    for b, g in dw.groupby("baseline"):
        g = g.dropna(subset=["coh_slope_excess_pulse_trials", "control_coh_departure_logit"])
        if len(g) > 2:
            r, p = stats.pearsonr(g.coh_slope_excess_pulse_trials, g.control_coh_departure_logit)
            corr[b] = {"pearson_r": float(r), "n_mice": len(g), "p_descriptive": float(p)}
    e5["corr_pulse_coh_slope_excess_vs_control_coh_departure"] = corr
    outputs.append(io.write_json(out / "e5_summary.json", e5))

    outputs += figures(run_id, prof, summ, opt, mcurves, baselines, mice)

    checks_bool = {k: v for k, v in checks.items() if isinstance(v, bool)}
    passed = all(checks_bool.values())
    print(json.dumps(checks, indent=1, default=str))
    inputs_h = {"ddm_inputs": io.sha256_file(DDM_INPUTS), "trial_table": cfg["hashes"]["trial_table"],
                **{f"revised_{b}_{m}": io.sha256_file(REVISED / b / f"{m}.pkl") for b in ("primary", "secondary") for m in mice},
                "d_contrast_curves_per_mouse": io.sha256_file(run / "response_time" / "contrast_curves_per_mouse.csv.gz")}
    timing = [json.loads(p.read_text()) for p in sorted(sims_dir.glob("timing_*.json"))]
    man = io.stage_manifest(STAGE, "PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.diagnostics " + " ".join(sys.argv[1:]),
                            inputs_h, outputs + sorted(sims_dir.glob("*.npz")), checks, timer.seconds,
                            extra={"run_id": run_id, "status": "exploratory", "code_sha256_diagnostics": io.sha256_file(__file__),
                                   "simulation_timing": timing,
                                   "labels": "in_sample = all pulse trials of a mouse (exploratory, in-sample); trainK/testK = stored "
                                             "amendment 6 folds (gains chosen on train folds of this re-simulation, scored on the held-out fold)"})
    io.mark_complete(out, man, passed)
    return passed


# ------------------------------------------------------------------------------------------------------ figures
def figures(run_id, prof, summ, opt, mcurves, baselines, mice):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fdir = io.figure_dir(run_id)
    paths = []
    for b in baselines:
        ins = prof[(prof.scope == "in_sample") & (prof.baseline == b) & (prof.seed == STORED_SEED_OFFSET)]
        fig, axes = plt.subplots(2, 5, figsize=(14, 6), sharex=True, layout="constrained")
        for ax, m in zip(axes.ravel(), mice):
            g = ins[ins.mouse == m].sort_values("gain")
            if g.empty:
                continue
            for col, lab, sty in (("total", "joint (total)", "k-"), ("choice_given_resp", "choice | response", "-"),
                                  ("rt", "RT bins (L+R)", "--"), ("resp_censor", "response vs censored", ":")):
                ax.plot(g.gain, g[col] - g[col].min(), sty, lw=1.3, label=lab, marker=".", ms=3)
            ax.set_xscale("symlog", linthresh=1)
            ax.set_ylim(-1, 40)
            ax.set_title(m, fontsize=9)
            ax.axhline(DELTA, color="grey", lw=0.5)
        axes[0, 0].legend(fontsize=7, frameon=False)
        for ax in axes[1]:
            ax.set_xlabel("pulse gain w (symlog)")
        for ax in axes[:, 0]:
            ax.set_ylabel("NLL minus its minimum (QMLE units)")
        fig.suptitle(f"{b}: decomposed CensoredQMLE gain profile, all pulse trials (in-sample, seed 50, 50 reps). "
                     "Grey line = 1.92 (indicative only). EXPLORATORY", fontsize=9)
        paths.append(io.savefig(fig, fdir / f"diagnostics_profile_components_{b}.png", dpi=180))
        plt.close(fig)

        sm = summ[(summ.baseline == b) & (summ.source == "model") & (summ.seed == STORED_SEED_OFFSET)]
        so = summ[(summ.baseline == b) & (summ.source == "observed")]
        qs = [("p_toward_given_resp", "P(toward pulse | response)"), ("p_censored", "P(censored)"),
              ("rt_toward_q50", "median RT toward pulse (s)"), ("rt_against_q50", "median RT against pulse (s)"),
              ("rt_correct_mean", "mean RT correct (s)"), ("rt_error_mean", "mean RT error (s)")]
        fig, axes = plt.subplots(len(qs), 10, figsize=(18, 11), sharex=True, sharey="row", layout="constrained")
        for j, m in enumerate(mice):
            g = sm[sm.mouse == m].sort_values("gain")
            if g.empty:
                continue
            o = so[so.mouse == m].iloc[0]
            oj = opt[(opt.baseline == b) & (opt.mouse == m) & (opt.scope == "in_sample") & (opt.seed == STORED_SEED_OFFSET)].iloc[0]
            for i, (q, lab) in enumerate(qs):
                ax = axes[i, j]
                ax.plot(g.gain, g[q], "-", color="#0072B2", lw=1.2, marker=".", ms=3, label="model")
                ax.axhline(o[q], color="#D55E00", lw=1.2, ls="--", label="observed")
                ax.axvline(oj.w_joint, color="k", lw=0.7, ls="-")
                ax.axvline(oj.w_choice_only, color="k", lw=0.7, ls=":")
                ax.set_xscale("symlog", linthresh=1)
                if i == 0:
                    ax.set_title(m, fontsize=8)
                if j == 0:
                    ax.set_ylabel(lab, fontsize=7)
                if i == len(qs) - 1:
                    ax.set_xlabel("gain w", fontsize=7)
        axes[0, 0].legend(fontsize=6, frameon=False)
        fig.suptitle(f"{b}: pulse-trial summaries (|coh| <= 36%) against gain; solid vertical = joint optimum, dotted = "
                     "choice-only optimum (in-sample, seed 50). EXPLORATORY", fontsize=9)
        paths.append(io.savefig(fig, fdir / f"diagnostics_summaries_vs_gain_{b}.png", dpi=150))
        plt.close(fig)

    # model vs observed direction and common-effect curves (group mean across mice)
    fig, axes = plt.subplots(len(baselines), 3, figsize=(13, 3.6 * len(baselines)), squeeze=False, layout="constrained")
    obs = mcurves[mcurves.source == "observed_ddm_rows"]
    cols = {"w1": "#999999", "w_all_stored": "#0072B2", "w_choice_only": "#009E73", "w10": "#CC79A7", "w20": "#E69F00"}
    for i, b in enumerate(baselines):
        for j, (q, lab) in enumerate((("direction", "(dR - dL)/2, pos - neg (pp)"), ("d_survival", "S_pos - S_neg (pp)"),
                                      ("common_responded", "model: P(responded) with pulse - without (pp)"))):
            ax = axes[i, j]
            if q != "common_responded":
                go = obs[obs.quantity == q].groupby("u").value.mean()
                ax.plot(go.index, 100 * go.values, "k-", lw=2, label="observed (same trials, D weights)")
            for lab_, c in cols.items():
                gm = mcurves[(mcurves.source == "model") & (mcurves.baseline == b) & (mcurves.gain_label == lab_) & (mcurves.quantity == q)]
                if len(gm):
                    gg = gm.groupby("u").value.mean()
                    ax.plot(gg.index, 100 * gg.values, color=c, lw=1.2, label=f"model {lab_}")
            ax.axhline(0, color="k", lw=0.5)
            ax.set_title(f"{b}: {lab}", fontsize=8)
            ax.set_xlabel("time since onset u (s)")
        axes[i, 0].legend(fontsize=6, frameon=False)
    n_obs = obs.mouse.nunique()
    n_mod = mcurves[mcurves.source == "model"].groupby("baseline").mouse.nunique().to_dict()
    fig.suptitle(f"Mean of per-mouse curves (observed {n_obs} mice; model {n_mod} mice), primary coherence set, sign-symmetric "
                 "cells, all scheduled trials. Model gains in-sample (seed 50). EXPLORATORY", fontsize=9)
    paths.append(io.savefig(fig, fdir / "diagnostics_model_vs_observed_curves.png", dpi=180))
    plt.close(fig)
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["simulate", "analyze"])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--baseline", choices=["primary", "secondary"], help="simulate only")
    ap.add_argument("--seeds", type=int, nargs="+", default=[STORED_SEED_OFFSET], help="simulate only")
    ap.add_argument("--mice", nargs="*", help="simulate only (default: all)")
    ap.add_argument("--control-only", action="store_true", help="simulate only: control trials only (skips pulse-gain seeds)")
    a = ap.parse_args(argv)
    if a.command == "simulate":
        if not a.baseline:
            ap.error("simulate needs --baseline")
        simulate(a.run_id, a.baseline, a.seeds, a.mice, a.control_only)
    else:
        sys.exit(0 if analyze(a.run_id) else 1)


if __name__ == "__main__":
    main()
