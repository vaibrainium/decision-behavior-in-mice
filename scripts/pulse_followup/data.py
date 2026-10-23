"""Package A: shared trial table, assignment audit and frozen analysis contract.

Read-only with respect to every existing input. Joins
  valid_data.csv          responses at 0.3-5 s in accepted sessions (non-correction trials)
  censored_trials.csv     no response by 5 s in the same sessions (reaction_time = 5 is a replay placeholder)
  aggregate_data.csv      every trial of every session (source rows; trial history for balance checks)
  ddm/ddm_inputs_global.npz  the retained DDM trial set and its scheduled labels
by verified unique trial identity (agg_code), audits scheduled pulse labels, censoring and assignment, assigns the
UCLA control pseudo-onsets, and writes into <run>/data/:
  trial_table.csv, schema.json, exclusion_ledger.csv, assignment_audit.json, balance_tables.csv,
  analysis_config.json (with ready_for_behaviour), manifest.json, COMPLETE.
The original builders (make_censored_trials, build_ddm_inputs) are not rerun: their defaults overwrite outputs.

Usage:
    python -B -m scripts.pulse_followup.data --new-run           # creates a run ID and writes the data stage
    python -B -m scripts.pulse_followup.data --run-id <run_id>   # writes the data stage of an existing empty run
"""

import argparse
import copy
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from scripts.pulse_followup import io
from scripts.pulse_followup.config import (
    CONFIG,
    DEADLINE_S,
    FRAME_RATE,
    MIN_VIEWING_S,
    STRATUM_NAMES,
    UCLA_ONSET_BOUNDARIES_S,
    UW_ONSET_FRAMES,
)

INPUTS = {
    "valid": io.PROCESSED / "valid_data.csv",
    "censored": io.PROCESSED / "censored_trials.csv",
    "aggregate": io.PROCESSED / "aggregate_data.csv",
    "ddm_inputs": io.PROCESSED / "ddm" / "ddm_inputs_global.npz",
    "ucla_raw": Path("/mnt/data/raw/ucla_data.csv"),  # BurstCoh (pulse sign relative to the stimulus direction)
}
# task source code read for the assignment audit (public repositories named by the user, 2026-10-23)
TASK_CODE = {
    "uw": {"repo": "https://github.com/vaibrainium/NeuRPi", "commit": "fcfb603187068c080414677aba97dfb642da91c2",
           "files": ["protocols/random_dot_motion/rt_pulse/session_manager.py::generate_pulse_sequence",
                     "protocols/random_dot_motion/core/stimulus/stimulus_manager.py::update_stimulus",
                     "protocols/random_dot_motion/core/task/rt_task.py (min-viewing timer, response clock)"]},
    "ucla": {"repo": "https://github.com/vaibrainium/RDK-Task", "commit": "6fb38781a3696f80403531fcdf06a3b7236e61a6",
             "files": ["Burst_Experiment.py::setCoherence (burstBlock)", "Burst_Experiment.py::Burst_Coherence (burstTime, stimulus loop)"]},
}
# responded-only inventory of the research report (dissemination/reports/pulse-thesis-research-2026-10-23.md)
RESEARCH_INVENTORY = {
    "ucla": {"pulse": 6030, "control": 9257, "pre_onset": 0, "lag_500ms": 4830, "both_signs": 456, "plus_control": 220},
    "uw": {"pulse": 5449, "control": 4757, "pre_onset": 224, "lag_500ms": 3883, "both_signs": 0, "plus_control": 0},
}


def uw_asymmetric_coherences(sessions):
    """|coherence| at which a UW session's task config schedules only rightward pulses (probabilities 0 for the
    leftward categories, e.g. [0, 0, 0, 0, 0.3, 0.3, 0, 0, 0.4]: right middle/late pulses and late shams only).
    Read from /mnt/data/raw/<mouse>/<session>/<mouse>_config.txt (read-only)."""
    out, hashes = {}, {}
    for s in sorted(sessions):
        mouse, session = s.split("_", 1)
        path = Path("/mnt/data/raw") / mouse / session / f"{mouse}_config.txt"
        text = path.read_text()
        block = text[text.index('"pulse_probabilities"'):text.index('"pulse_duration"')]
        probs = {int(c): [float(x) for x in v.split(",")] for c, v in re.findall(r"(-?\d+): \[([^\]]*)\]", block)}
        assert probs and all(len(v) == 9 for v in probs.values()), path
        out[s] = sorted({abs(c) for c, v in probs.items() if sum(v[:3]) == 0 and sum(v[3:6]) > 0})
        hashes[str(path)] = io.sha256_file(path)
    return out, hashes


def frame_of(seconds):
    """Frame index used by the replay (compute_motion_energy_full.convert_to_frame_units), 1-based."""
    return np.round(seconds * 1000 / 16.67) + 1


def load_sources():
    valid = pd.read_csv(INPUTS["valid"], dtype={"session_id": str})
    censored = pd.read_csv(INPUTS["censored"], dtype={"session_id": str})
    aggregate = pd.read_csv(INPUTS["aggregate"], dtype={"session_id": str})
    z = np.load(INPUTS["ddm_inputs"])
    ddm = pd.DataFrame({k: z[k] for k in ("agg_code", "sched_pulse_type", "censored", "choice", "rt", "signed_coherence", "data_source")})
    # raw UCLA burst sign, keyed by aggregate row (aggregate idx_valid_trial / idx_correction = raw TrialNo / AttemptNo)
    raw = pd.read_csv(INPUTS["ucla_raw"], dtype={"session_id": str})
    key = ["subject_id", "session_id", "TrialNo", "AttemptNo"]
    ua = aggregate[aggregate.data_source == "ucla"].rename(columns={"idx_valid_trial": "TrialNo", "idx_correction": "AttemptNo"})
    j = ua[key].reset_index().merge(raw[[*key, "BurstCoh", "BurstTime", "Coherence"]], on=key, how="left", validate="one_to_one")
    assert j.BurstCoh.notna().all() and (j.Coherence.to_numpy() == ua.signed_coherence.to_numpy()).all()
    aggregate = aggregate.assign(burst_coh_raw=pd.Series(j.BurstCoh.to_numpy(), index=j["index"].to_numpy()))
    return valid, censored, aggregate, ddm


def source_rows(valid, censored, aggregate):
    """aggregate_data.csv row of every valid and censored trial (verified one-to-one)."""
    a = aggregate[~aggregate.is_correction_trial.astype(bool) & (aggregate.reaction_time <= DEADLINE_S)]
    key = a.subject_id + "_" + a.session_id + "_" + a.idx_valid_trial.astype(str)
    responded = pd.Series(a.index.to_numpy(), index=key.to_numpy())
    assert responded.index.is_unique
    rows_valid = responded.reindex(valid.agg_code).to_numpy()
    rows_censored = censored.agg_code.str.extract(r"_censored(\d+)$")[0].astype(int).to_numpy()
    return rows_valid, rows_censored


def build_table(valid, censored, aggregate, ddm):
    rows_valid, rows_censored = source_rows(valid, censored, aggregate)
    assert not np.isnan(rows_valid.astype(float)).any(), "valid trial without an aggregate row"
    v = valid.assign(source_file="valid_data.csv", source_row=np.arange(len(valid)), aggregate_row=rows_valid.astype(int),
                     is_censored=False, rt_recorded_late_s=np.nan)
    c = censored.assign(source_file="censored_trials.csv", source_row=np.arange(len(censored)), aggregate_row=rows_censored,
                        is_censored=True, rt_recorded_late_s=censored.censored_rt)
    d = pd.concat([v, c], ignore_index=True)
    assert d.agg_code.is_unique and d.aggregate_row.is_unique

    # agreement of the censored rows with their aggregate source row
    src = aggregate.loc[c.aggregate_row]
    for col in ("subject_id", "session_id", "signed_coherence", "stimulus_seed"):
        assert (src[col].to_numpy() == c[col].to_numpy()).all(), f"censored {col} differs from aggregate"

    t = pd.DataFrame({
        "trial_id": d.agg_code,
        "mouse": d.subject_id,
        "rig": d.data_source,
        "session_id": d.session_id,
        "session": d.subject_id + "_" + d.session_id,
        "idx_session": d.idx_session,
        "idx_valid_trial": d.idx_valid_trial,
        "aggregate_row": d.aggregate_row,
        "seed": d.stimulus_seed,
        "coherence_pct": d.signed_coherence.round().astype(int),
        "target": d.target,
    })
    t["abs_coherence_pct"] = t.coherence_pct.abs()

    # ---- scheduled pulse labels
    # UCLA: the task pulses toward sign(BurstCoh * coherence) (Burst_Experiment.py). Notebook 0.0 used the target,
    # which it infers from Correct/Response, so a pulse on a trial without any response lost its direction
    # (pulse_coherence NaN) and the DDM builder labelled it a control. Recover it from BurstCoh when the coherence is
    # nonzero; at 0% the stimulus sign (+-0.1) is only known through the target, so those stay unknown.
    has_pulse_field = d.is_pulse_trial.astype(bool)
    pc = d.pulse_coherence.copy()
    burst = aggregate.burst_coh_raw.reindex(d.aggregate_row).to_numpy()
    lost = (d.data_source == "ucla").to_numpy() & has_pulse_field.to_numpy() & pc.isna().to_numpy()
    recover = lost & (d.signed_coherence != 0).to_numpy()
    pc[recover] = np.sign(burst[recover]) * np.sign(d.signed_coherence[recover]) * 100
    unknown = lost & ~recover
    t["pulse_direction_recovered"] = recover
    t["burst_coh_raw"] = burst
    genuine = has_pulse_field & pc.notna() & (pc != d.signed_coherence)
    null_pulse = has_pulse_field & (pc == d.signed_coherence)  # UCLA only: UW sets is_pulse_trial = pc != coherence
    sign = np.sign(pc.fillna(0)).astype(int)
    t["pulse_category"] = np.select([genuine & (sign > 0), genuine & (sign < 0), null_pulse, unknown],
                                    ["positive", "negative", "null_pulse", "pulse_direction_unknown"], "control")
    t["pulse_sign"] = np.where(genuine, sign, 0)
    t["scheduled_pulse_sign_incl_null"] = np.where(has_pulse_field, sign, 0)  # scheduled sign, physical or not
    t["pulse_coherence_pct"] = pc
    t["pulse_delta_pct"] = np.where(genuine, pc - d.signed_coherence, 0.0)
    t["pulse_equals_baseline"] = null_pulse.to_numpy() | ((t.rig == "uw") & ~genuine & pc.notna()).to_numpy()

    # ---- timing: recorded and scheduled, kept separate
    t["recorded_onset_s"] = d.pulse_onset
    t["recorded_duration_s"] = d.pulse_duration
    t["recorded_offset_s"] = d.pulse_onset + d.pulse_duration
    t["onset_frame"] = frame_of(d.pulse_onset)
    t["offset_frame"] = t.onset_frame + np.round(d.pulse_duration * 1000 / 16.67)
    t["n_pulse_frames"] = t.offset_frame - t.onset_frame
    # UCLA logs burstEndTime only when the 50 ms pulse ends inside the stimulus loop and never resets it on pulse
    # trials, so a response during the pulse leaves a duration from an earlier trial (stale or invalid).
    t["response_before_pulse_end"] = (~d.is_censored).to_numpy() & has_pulse_field.to_numpy() & (d.reaction_time < d.pulse_onset + 0.05).to_numpy()
    uw = (t.rig == "uw").to_numpy()
    uw_frames = np.round(d.pulse_onset * 1000 / 16.67)
    t["scheduled_onset_frame"] = np.where(uw, uw_frames, np.nan)
    t["scheduled_onset_s"] = np.where(uw, uw_frames / FRAME_RATE, np.nan)
    t["scheduled_onset_provenance"] = np.where(uw, "uw_task_config_frames", "not_recorded")
    t["sham_onset_recorded"] = uw & (t.pulse_category == "control").to_numpy() & d.pulse_onset.notna().to_numpy()

    stratum = pd.Series(pd.NA, index=t.index, dtype="object")
    stratum[uw] = pd.Series(uw_frames[uw]).map(UW_ONSET_FRAMES).to_numpy()
    ucla_onset = ~uw & d.pulse_onset.notna().to_numpy()
    stratum[ucla_onset] = np.array(STRATUM_NAMES)[np.digitize(d.pulse_onset[ucla_onset], UCLA_ONSET_BOUNDARIES_S)]
    t["onset_stratum"] = stratum
    t["onset_stratum_provenance"] = np.select([uw, ucla_onset], ["scheduled_config", "scheduled_category_measured_time"], "none")

    # ---- outcome: response side, RT, event, deadline
    choice = d.choice
    t["response_side"] = np.where(d.is_censored, "none", np.where(choice == 1, "R", "L"))
    t["rt_s"] = np.where(d.is_censored, np.nan, d.reaction_time)
    t["event"] = (~d.is_censored).astype(int)
    t["followup_s"] = np.where(d.is_censored, DEADLINE_S, d.reaction_time)
    t["deadline_s"] = DEADLINE_S
    t["is_censored"] = d.is_censored.to_numpy()
    t["rt_recorded_late_s"] = d.rt_recorded_late_s
    t["no_response_recorded"] = d.is_censored.to_numpy() & d.rt_recorded_late_s.isna().to_numpy()
    onset_for_pre = np.where(t.pulse_category.isin(["positive", "negative", "null_pulse"]) | t.sham_onset_recorded, t.recorded_onset_s, np.nan)
    t["pre_onset_response"] = (t.event == 1) & (t.rt_s < onset_for_pre)
    t["source_file"] = d.source_file
    t["source_row"] = d.source_row
    t["pulse_type_rt_dependent"] = d.pulse_type  # reference only: depends on RT, never use for assignment

    # ---- join to the DDM input set
    m = t[["trial_id"]].merge(ddm.rename(columns={"agg_code": "trial_id"}), on="trial_id", how="left", validate="one_to_one", indicator=True)
    t["in_ddm_input"] = (m._merge == "both").to_numpy()
    t["ddm_sched_pulse_type"] = m.sched_pulse_type.to_numpy()
    return t, m


def assign_pseudo_onsets(t, seed, min_pool, column):
    """UCLA controls: one onset drawn from scheduled pulse onsets in the same mouse x session x |coherence| (fallback:
    mouse x session). Uses no outcomes. UW controls keep their recorded sham onset."""
    rng = np.random.default_rng(seed)
    out = pd.Series(np.nan, index=t.index)
    level = pd.Series("", index=t.index, dtype=object)
    uw_ctrl = t.sham_onset_recorded
    out[uw_ctrl] = t.recorded_onset_s[uw_ctrl]
    level[uw_ctrl] = "uw_recorded_sham"
    pulses = t[(t.rig == "ucla") & t.pulse_category.isin(["positive", "negative", "null_pulse"]) & t.recorded_onset_s.notna()]
    by_cell = {k: g.recorded_onset_s.to_numpy() for k, g in pulses.groupby(["session", "abs_coherence_pct"])}
    by_session = {k: g.recorded_onset_s.to_numpy() for k, g in pulses.groupby("session")}
    ctrl = t[(t.rig == "ucla") & (t.pulse_category == "control")].sort_values("trial_id")  # fixed order for the draw
    for i, s, a in zip(ctrl.index, ctrl.session, ctrl.abs_coherence_pct):
        pool, lev = by_cell.get((s, a), np.array([])), "session_x_abs_coherence"
        if len(pool) < min_pool:
            pool, lev = by_session.get(s, np.array([])), "session_any_coherence"
        if len(pool) == 0:
            level[i] = "no_pool"
            continue
        out[i] = rng.choice(np.sort(pool))
        level[i] = lev
    t[column] = out
    return level


def control_onset_columns(t, cfg):
    ca = cfg["control_alignment"]
    level = assign_pseudo_onsets(t, ca["seed"], ca["min_pool"], "control_onset_s")
    t["control_onset_rule"] = level.where(t.pulse_category == "control", "")
    for k, s in enumerate(ca["sensitivity_seeds"], start=1):
        assign_pseudo_onsets(t, s, ca["min_pool"], f"control_onset_s_seed{k}")
    ucla_ctrl = (t.rig == "ucla") & (t.pulse_category == "control") & t.control_onset_s.notna()
    t.loc[ucla_ctrl, "onset_stratum"] = np.array(STRATUM_NAMES)[np.digitize(t.control_onset_s[ucla_ctrl], UCLA_ONSET_BOUNDARIES_S)]
    t.loc[ucla_ctrl, "onset_stratum_provenance"] = "pseudo_onset"
    t["control_pre_onset_response"] = (t.pulse_category == "control") & (t.event == 1) & (t.rt_s < t.control_onset_s)


def analysis_flags(t, asym):
    t["signs_scheduled_symmetric"] = [rig == "ucla" or a not in asym.get(s, []) for rig, s, a in zip(t.rig, t.session, t.abs_coherence_pct)]
    t["in_primary_coherence"] = t.in_ddm_input & (t.abs_coherence_pct <= 36)
    t["in_all_coherences"] = t.in_ddm_input
    t["in_zero_coherence"] = t.in_ddm_input & (t.coherence_pct == 0)
    reason = np.where(t.in_ddm_input, "", "dropped_by_ddm_builder")
    t["exclusion_reason"] = reason


def exclusion_ledger(aggregate, valid, t):
    sessions = pd.MultiIndex.from_frame(valid[["subject_id", "session_id"]].drop_duplicates())
    in_session = pd.MultiIndex.from_frame(aggregate[["subject_id", "session_id"]]).isin(sessions)
    corr = aggregate.is_correction_trial.astype(bool)
    dropped = t[~t.in_ddm_input]
    rows = [
        ("aggregate_data.csv rows", len(aggregate), "all sessions, all trials", "", ""),
        ("not in an accepted session", int((~in_session).sum()), "session-level acceptance from preprocessing (notebook 0.1)", "session (pre-trial)", "no trial-level pulse dependence"),
        ("correction trials in accepted sessions", int((in_session & corr).sum()), "is_correction_trial (repeat after error)", "previous trial outcome (pre-treatment)", "pre-treatment"),
        ("non-correction trials in accepted sessions", int((in_session & ~corr).sum()), "= valid + censored", "", ""),
        ("  responded 0.3-5 s (valid_data.csv)", int((~t.is_censored).sum()), "", "", ""),
        ("  no response by 5 s (censored_trials.csv)", int(t.is_censored.sum()), "kept as unresponded at 5 s", "", ""),
        ("dropped by the DDM builder", len(dropped), "missing or non-positive recorded pulse duration (stimulus unknown); "
         "the UCLA task logs no fresh duration when the response comes during the 50 ms pulse",
         "response during the pulse (outcome-dependent)", f"treatment-dependent: {dropped.pulse_category.value_counts().to_dict()}"),
        ("retained DDM input trials", int(t.in_ddm_input.sum()), "default analysis set ddm_retained", "", ""),
        ("  of which pulse direction recovered", int((t.in_ddm_input & t.pulse_direction_recovered).sum()),
         "UCLA unresponded pulses labelled control in the DDM inputs; relabelled by sign(BurstCoh*coherence)", "raw BurstCoh", "label correction"),
        ("  of which pulse direction unknown", int((t.in_ddm_input & (t.pulse_category == "pulse_direction_unknown")).sum()),
         "UCLA 0% pulses with no response: direction relative to the screen unknowable; excluded from signed contrasts",
         "no response (outcome-dependent)", "kept in the table, out of positive/negative arms"),
    ]
    return pd.DataFrame(rows, columns=["step", "n_trials", "rule", "depends_on", "note"]), dropped


def previous_trial_history(aggregate, t):
    """Outcome and choice of the immediately preceding trial of the same session (any trial type): pre-treatment."""
    a = aggregate[["subject_id", "session_id", "choice", "outcome"]].copy()
    a["prev_choice"] = a.groupby(["subject_id", "session_id"]).choice.shift(1)
    a["prev_outcome"] = a.groupby(["subject_id", "session_id"]).outcome.shift(1)
    a["position"] = a.groupby(["subject_id", "session_id"]).cumcount()
    a["n_in_session"] = a.groupby(["subject_id", "session_id"]).choice.transform("size")
    h = a.loc[t.aggregate_row, ["prev_choice", "prev_outcome", "position", "n_in_session"]].reset_index(drop=True)
    return h


def chi2(table):
    table = table.loc[table.sum(axis=1) > 0, table.sum(axis=0) > 0]
    if table.shape[0] < 2 or table.shape[1] < 2:
        return None
    r = stats.chi2_contingency(table.to_numpy())
    n = table.to_numpy().sum()
    v = np.sqrt(r.statistic / (n * (min(table.shape) - 1)))
    return {"chi2": round(float(r.statistic), 3), "dof": int(r.dof), "p": float(r.pvalue), "cramers_v": round(float(v), 4), "n": int(n)}


def assignment_audit(t, h, aggregate):
    """Balance of scheduled categories against pre-treatment variables. Descriptive tests (no correction family):
    balanced counts are consistent with, not proof of, randomized assignment."""
    d = t[t.in_ddm_input]  # t already carries the history columns of h
    out, tables = {}, []
    for rig, g in d.groupby("rig"):
        r = {}
        cat = g.pulse_category
        r["category_counts"] = cat.value_counts().to_dict()
        # P(category) by coherence, compared with the UW task configuration where available
        ct = pd.crosstab(g.coherence_pct, cat, normalize="index").round(4)
        tables.append(ct.reset_index().melt(id_vars="coherence_pct", var_name="pulse_category", value_name="fraction").assign(rig=rig, table="category_by_coherence"))
        gp = g[cat.isin(["positive", "negative"])]
        r["sign_vs_coherence_sign"] = chi2(pd.crosstab(np.sign(gp.coherence_pct), gp.pulse_category))
        r["sign_vs_prev_choice"] = chi2(pd.crosstab(gp.prev_choice, gp.pulse_category))
        r["sign_vs_prev_outcome"] = chi2(pd.crosstab(gp.prev_outcome, gp.pulse_category))
        r["sign_vs_session_half"] = chi2(pd.crosstab(gp.position >= gp.n_in_session / 2, gp.pulse_category))
        r["pulse_vs_control_vs_prev_outcome"] = chi2(pd.crosstab(g.prev_outcome, cat.isin(["positive", "negative"])))
        r["sign_vs_onset_stratum"] = chi2(pd.crosstab(gp.onset_stratum, gp.pulse_category))
        # within-session: fraction positive among genuine pulses, per session
        per_session = gp.groupby("session").pulse_category.agg(lambda x: (x == "positive").mean())
        n_session = gp.groupby("session").size()
        binom_p = [stats.binomtest(int(round(f * n)), int(n), 0.5).pvalue for f, n in zip(per_session, n_session)]
        r["within_session_positive_fraction"] = {
            "n_sessions": int(len(per_session)),
            "median": round(float(per_session.median()), 4),
            "q05_q95": [round(float(per_session.quantile(0.05)), 4), round(float(per_session.quantile(0.95)), 4)],
            "sessions_binomial_p_below_0.05": int(np.sum(np.array(binom_p) < 0.05)),
            "expected_below_0.05_if_balanced": round(0.05 * len(per_session), 1),
        }
        per_mouse = gp.groupby(["mouse", "onset_stratum"]).pulse_category.value_counts().unstack(fill_value=0)
        tables.append(per_mouse.reset_index().melt(id_vars=["mouse", "onset_stratum"], var_name="pulse_category", value_name="n").assign(rig=rig, table="sign_by_mouse_stratum"))
        out[rig] = r
    return out, pd.concat(tables, ignore_index=True)


def support_summary(t):
    """Common-support coverage per mouse for the primary positive-vs-negative contrast (counts only; no outcomes)."""
    rows = []
    for name, flag in [("primary_coherence", "in_primary_coherence"), ("sensitivity_all_coherences", "in_all_coherences"), ("sensitivity_zero_coherence", "in_zero_coherence")]:
        g = t[t[flag] & t.pulse_category.isin(["positive", "negative"])]
        cells = g.groupby(["mouse", "session", "coherence_pct", "onset_stratum"]).pulse_category.value_counts().unstack(fill_value=0)
        for c in ("positive", "negative"):
            if c not in cells:
                cells[c] = 0
        cells["supported"] = (cells.positive > 0) & (cells.negative > 0)
        cells["weight_raw"] = np.minimum(cells.positive, cells.negative)
        for mouse, cm in cells.groupby(level="mouse"):
            s = cm[cm.supported]
            rows.append({"analysis_set": name, "mouse": mouse, "rig": t.loc[t.mouse == mouse, "rig"].iloc[0],
                         "n_cells_total": len(cm), "n_cells_supported": len(s),
                         "n_pulse_trials": int(cm.positive.sum() + cm.negative.sum()),
                         "n_pulse_trials_in_support": int(s.positive.sum() + s.negative.sum()),
                         "effective_pairs": int(s.weight_raw.sum())})
    return pd.DataFrame(rows)


def reconcile_research_inventory(t):
    """Reproduce the responded-only feasibility inventory of the research report from the trial table."""
    res, ok = {}, True
    d = t[t.in_ddm_input & (t.event == 1)]
    for rig, g in d.groupby("rig"):
        sched = g.ddm_sched_pulse_type
        q = g[sched != 0]
        cell = g.assign(direction=np.sign(sched)).groupby(["mouse", "seed", "coherence_pct"]).direction.agg(frozenset)
        got = {
            "pulse": len(q), "control": int((sched == 0).sum()),
            "pre_onset": int((q.rt_s < q.recorded_onset_s).sum()),
            "lag_500ms": int((q.rt_s >= q.recorded_onset_s + 0.5).sum()),
            "both_signs": int(sum({-1, 1}.issubset(x) for x in cell)),
            "plus_control": int(sum({-1, 0, 1}.issubset(x) for x in cell)),
        }
        res[rig] = {"computed": got, "research_report": RESEARCH_INVENTORY[rig], "match": got == RESEARCH_INVENTORY[rig]}
        ok &= got == RESEARCH_INVENTORY[rig]
    return res, ok


def run_checks(t, m, ddm):
    c = {}
    keep = t.in_ddm_input
    c["ddm_join_unique_and_complete"] = bool(m.trial_id.is_unique and (m._merge != "right_only").all() and keep.sum() == len(ddm))
    # scheduled labels: our genuine-pulse sign and stratum agree with the DDM builder's sched_pulse_type
    stratum_index = t.onset_stratum.map({n: i + 1 for i, n in enumerate(STRATUM_NAMES)})
    ours = np.where(t.pulse_sign != 0, t.pulse_sign * stratum_index.fillna(0), 0)
    differs = keep & (ours != t.ddm_sched_pulse_type)
    documented = t.pulse_direction_recovered & (t.pulse_sign != 0) & (t.ddm_sched_pulse_type == 0)  # recovered null pulses stay 0
    c["sched_pulse_type_matches_ddm_except_recovered"] = bool((differs == (keep & documented)).all())
    c["direction_unknown_only_unresponded_zero_coherence"] = bool((t.loc[t.pulse_category == "pulse_direction_unknown", "coherence_pct"] == 0).all()
                                                              and t.loc[t.pulse_category == "pulse_direction_unknown", "no_response_recorded"].all())
    mm = m[m._merge == "both"]
    tt = t[keep]
    c["censor_flag_matches_ddm"] = bool((mm.censored.to_numpy() == tt.is_censored.to_numpy()).all())
    c["ddm_choice_coding_right_is_1"] = bool(((mm.choice.to_numpy() == 1) == (tt.response_side.to_numpy() == "R")).all())
    c["ddm_rt_matches"] = bool(np.allclose(np.where(tt.event == 1, tt.rt_s, np.inf), mm.rt.to_numpy()))
    c["ddm_coherence_matches"] = bool(np.allclose(mm.signed_coherence.to_numpy() * 100, tt.coherence_pct))
    c["no_event_manufactured_for_censored"] = bool(t.loc[t.is_censored, "rt_s"].isna().all() and (t.loc[t.is_censored, "event"] == 0).all())
    c["responded_rt_within_window"] = bool(t.loc[t.event == 1, "rt_s"].between(MIN_VIEWING_S, DEADLINE_S).all())
    c["censored_recorded_rt_after_deadline_or_missing"] = bool((t.loc[t.is_censored, "rt_recorded_late_s"].isna() | (t.loc[t.is_censored, "rt_recorded_late_s"] > DEADLINE_S)).all())
    c["uw_onsets_are_three_scheduled_frames"] = bool(set(t.loc[t.rig == "uw", "scheduled_onset_frame"].dropna().astype(int)) <= set(UW_ONSET_FRAMES))
    c["uw_every_trial_has_scheduled_onset"] = bool(t.loc[t.rig == "uw", "recorded_onset_s"].notna().all())
    ucla_p = t[(t.rig == "ucla") & t.pulse_category.isin(["positive", "negative", "null_pulse"])]
    gap = ucla_p.recorded_onset_s.between(0.12, 0.18).sum()
    c["ucla_onset_clusters_separated"] = bool(gap == 0 and ucla_p.recorded_onset_s.max() < UCLA_ONSET_BOUNDARIES_S[1])
    c["ucla_no_response_before_onset"] = bool(not t.loc[t.rig == "ucla", "pre_onset_response"].any())
    c["every_kept_control_has_onset"] = bool(t.loc[keep & (t.pulse_category == "control"), "control_onset_s"].notna().all())
    c["pulse_sign_symmetric_delta"] = bool((np.sign(t.pulse_delta_pct) == t.pulse_sign).all())
    c["trial_id_unique"] = bool(t.trial_id.is_unique)
    asym = t[~t.signs_scheduled_symmetric]
    c["asymmetric_cells_have_no_negative_pulse"] = bool(len(asym) > 0 and not (asym.pulse_category == "negative").any())
    sym = t[t.in_ddm_input & t.signs_scheduled_symmetric & (t.abs_coherence_pct < 100) & t.pulse_category.isin(["positive", "negative"])]
    c["symmetric_cells_sign_balance_p_above_0.01"] = bool(all(stats.binomtest(int((g.pulse_category == "positive").sum()), len(g)).pvalue > 0.01 for _, g in sym.groupby("rig")))
    return c


def schema(t):
    desc = {
        "trial_id": "unique trial identity (agg_code of valid_data/censored_trials; DDM input key)",
        "mouse": "subject ID", "rig": "ucla / uw (covariate only; confounded with cohort)",
        "session_id": "session within mouse", "session": "mouse_session (unique session key)",
        "idx_session": "global session index (valid_data)", "idx_valid_trial": "within-session valid-trial index (not unique for censored)",
        "aggregate_row": "row of aggregate_data.csv (source row)", "seed": "stimulus seed",
        "coherence_pct": "signed nominal base coherence, percent", "abs_coherence_pct": "|coherence_pct|", "target": "rewarded side (+1 right, -1 left)",
        "pulse_category": "scheduled: positive / negative (genuine coherence change, by pulse sign), null_pulse (UCLA, pulse = base), "
        "pulse_direction_unknown (UCLA 0% pulse without any response: target unknowable), control",
        "pulse_direction_recovered": "UCLA pulse whose direction notebook 0.0 lost (no response); recovered as sign(BurstCoh*coherence). "
        "Labelled control in the DDM inputs",
        "burst_coh_raw": "UCLA raw BurstCoh (+1 toward / -1 against the stimulus direction, 0 none); NaN for UW",
        "response_before_pulse_end": "responded before recorded onset + 50 ms (UCLA: recorded duration may be stale)",
        "pulse_sign": "+1 / -1 for genuine pulses, else 0",
        "scheduled_pulse_sign_incl_null": "sign of any scheduled pulse field, incl. null pulses",
        "pulse_coherence_pct": "scheduled pulse coherence, percent (UW controls: equals base)",
        "pulse_delta_pct": "pulse_coherence - base coherence for genuine pulses, else 0",
        "pulse_equals_baseline": "pulse field present but equal to base (UCLA null pulse, UW control sham)",
        "recorded_onset_s": "recorded pulse/sham onset (UW: scheduled frames; UCLA: measured BurstTime)",
        "recorded_duration_s": "recorded pulse duration", "recorded_offset_s": "onset + duration",
        "onset_frame": "replay frame of onset (1-based; convert_to_frame_units)", "offset_frame": "replay frame of offset",
        "n_pulse_frames": "offset_frame - onset_frame",
        "scheduled_onset_frame": "UW scheduled onset frame (3/14/25); UCLA NaN (not recorded)",
        "scheduled_onset_s": "scheduled_onset_frame / 60", "scheduled_onset_provenance": "uw_task_config_frames / not_recorded",
        "sham_onset_recorded": "UW control with a recorded scheduled sham onset",
        "onset_stratum": "early / middle / late (UW scheduled; UCLA pulses measured cluster; UCLA controls pseudo-onset)",
        "onset_stratum_provenance": "scheduled_config / measured_cluster_proxy / pseudo_onset / none",
        "response_side": "R / L / none (none = no response by the deadline)",
        "rt_s": "observed response time (s from stimulus onset); NaN if unresponded", "event": "1 if a response by the deadline",
        "followup_s": "min(rt, deadline)", "deadline_s": "administrative follow-up deadline (5 s)",
        "is_censored": "no response by 5 s", "rt_recorded_late_s": "recorded RT > 5 s for censored trials (reference only); NaN = no response recorded",
        "no_response_recorded": "censored with no response at all",
        "pre_onset_response": "responded before the recorded pulse/sham onset (pulse never shown)",
        "source_file": "valid_data.csv / censored_trials.csv", "source_row": "row in source_file",
        "pulse_type_rt_dependent": "original pulse_type (RT-dependent). REFERENCE ONLY; never use for assignment",
        "in_ddm_input": "trial retained in ddm_inputs_global.npz", "ddm_sched_pulse_type": "sched_pulse_type of the DDM input",
        "control_onset_s": "control alignment: UW recorded sham onset; UCLA pseudo-onset (seed in config)",
        "control_onset_rule": "uw_recorded_sham / session_x_abs_coherence / session_any_coherence / no_pool",
        "control_pre_onset_response": "control responded before its (pseudo-)onset",
        "signs_scheduled_symmetric": "both pulse signs scheduled at this coherence in this session (False: UW asymmetric coherence, rightward pulses only)",
        "in_primary_coherence": "ddm_retained & |coh| <= 36", "in_all_coherences": "ddm_retained",
        "in_zero_coherence": "ddm_retained & coh == 0", "exclusion_reason": "empty if retained",
        "prev_choice": "choice of the preceding trial in the session (any trial type; pre-treatment)",
        "prev_outcome": "outcome of the preceding trial", "position": "trial position in session (aggregate order)",
        "n_in_session": "trials in the session (aggregate)",
    }
    for k in range(1, 6):
        desc[f"control_onset_s_seed{k}"] = f"pseudo-onset under sensitivity seed {k}"
    missing = [c for c in t.columns if c not in desc]
    assert not missing, f"undocumented columns {missing}"
    return {c: {"dtype": str(t[c].dtype), "description": desc[c], "n_missing": int(t[c].isna().sum())} for c in t.columns}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--new-run", action="store_true", help="create a new run ID and directory")
    g.add_argument("--run-id", help="existing run ID whose data stage is still empty")
    args = p.parse_args(argv)
    timer = io.Timer()

    if args.new_run:
        run_id = io.new_run_id()
        rd = io.OUTPUT_ROOT / run_id
        rd.mkdir(parents=True, exist_ok=False)
    else:
        run_id, rd = args.run_id, io.run_dir(args.run_id)
    out = io.stage_dir(rd, "data")
    print(f"run {run_id} -> {out}")

    input_hashes = {k: io.sha256_file(v) for k, v in INPUTS.items()}
    valid, censored, aggregate, ddm = load_sources()
    t, m = build_table(valid, censored, aggregate, ddm)
    cfg = copy.deepcopy(CONFIG)
    control_onset_columns(t, cfg)
    asym, config_hashes = uw_asymmetric_coherences(t.loc[t.rig == "uw", "session"].unique())
    input_hashes["uw_task_configs_combined"] = io.sha256_bytes("".join(f"{k}{v}" for k, v in sorted(config_hashes.items())).encode())
    analysis_flags(t, asym)
    h = previous_trial_history(aggregate, t)
    t = pd.concat([t.reset_index(drop=True), h], axis=1)

    checks = run_checks(t, m, ddm)
    inventory, inv_ok = reconcile_research_inventory(t)
    checks["research_inventory_reconciled"] = bool(inv_ok)
    audit, balance = assignment_audit(t, h, aggregate)
    ledger, dropped = exclusion_ledger(aggregate, valid, t)
    support = support_summary(t)
    for k, v in checks.items():
        print(f"  check {k}: {'PASS' if v else 'FAIL'}")

    files = {"trial_table": "trial_table.csv", "schema": "schema.json", "exclusion_ledger": "exclusion_ledger.csv",
             "assignment_audit": "assignment_audit.json", "balance_tables": "balance_tables.csv", "support_summary": "support_summary.csv"}
    io.write_csv(out / files["trial_table"], t)
    io.write_json(out / files["schema"], schema(t))
    io.write_csv(out / files["exclusion_ledger"], ledger)
    io.write_csv(out / files["balance_tables"], balance)
    io.write_csv(out / files["support_summary"], support)
    io.write_json(out / files["assignment_audit"], {
        "balance": audit, "research_inventory": inventory,
        "dropped_by_ddm_builder": dropped[["trial_id", "rig", "pulse_category", "onset_stratum", "recorded_duration_s", "is_censored"]].to_dict("records"),
        "control_onset_rules": t.loc[t.pulse_category == "control"].groupby(["rig", "control_onset_rule"]).size().rename("n").reset_index().to_dict("records"),
        "pre_onset_responses": t[t.in_ddm_input].groupby(["rig", "pulse_category", "onset_stratum"]).pre_onset_response.sum().rename("n").reset_index().query("n > 0").to_dict("records"),
    })
    passed = all(checks.values())
    cfg.update({
        "run_id": run_id,
        "ready_for_behaviour": passed,
        "files": files,
        "hashes": {k: io.sha256_file(out / v) for k, v in files.items()},
        "inputs_sha256": input_hashes,
        "assignment_verdict": ASSIGNMENT_VERDICT,
        "checks": checks,
    })
    io.write_json(out / "analysis_config.json", cfg)
    manifest = io.stage_manifest("data", " ".join(["python -B -m scripts.pulse_followup.data", *(argv or sys.argv[1:])]),
                                 input_hashes, [out / f for f in [*files.values(), "analysis_config.json"]], checks, timer.seconds,
                                 extra={"run_id": run_id, "n_trials": len(t), "n_ddm_retained": int(t.in_ddm_input.sum())})
    io.mark_complete(out, manifest, passed)
    print(f"{len(t)} trials, {int(t.in_ddm_input.sum())} retained; ready_for_behaviour = {passed}; {timer.seconds} s")
    return run_id, passed


# Written from task source code, per-session task configs and the compilation notebook (not outcomes). Sets wording.
ASSIGNMENT_VERDICT = {
    "uw": "VERIFIED FROM SOURCE (NeuRPi rt_pulse, HEAD commit; per-session config files hold the parameters used): "
    "generate_pulse_sequence draws one of 9 categories per trial with np.random.uniform from the config probabilities "
    "for the trial's signed coherence, in prepare_stimulus_stage before the stimulus starts. The draw depends only on "
    "the signed coherence, not on history or outcome. Pulses are applied by display frame counter (frames 3/14/25, "
    "4 frames) with no cue. Sham controls get a scheduled onset by the same draw. Caveat: the repository HEAD may "
    "postdate data collection; the config files match its parameter structure.",
    "ucla": "VERIFIED FROM SOURCE (RDK-Task Burst_Experiment.py, HEAD commit): permuted-block assignment. Each coherence "
    "block holds int(0.125 L) trials of each of {+early, +late, -early, -late} and the rest controls, shuffled with "
    "np.random.shuffle independently of the coherence order. Burst time is drawn before the trial, N(60, 15) ms or "
    "N(240, 15) ms; the logged BurstTime is the stimulus-loop time at which it was applied (scheduled draw plus loop "
    "latency); the scheduled draw itself is not logged. Pulse direction = sign(BurstCoh * coherence) x 100%, 50 ms by "
    "wall clock (displayed frames depend on the monitor rate, not in the repository). No cue. Repeat (correction) "
    "trials have no burst and are excluded upstream. Controls have no sham time.",
    "both": "Assignment is randomized and unannounced in the task code (UW independent draws, UCLA permuted blocks), "
    "conditional on coherence. Causal wording for the assignment (all-scheduled) contrast is supported, with two "
    "qualifications: (1) the code read is the repository HEAD, not a version pinned to each session; (2) small "
    "outcome-dependent exclusions exist (15 UCLA pulse trials dropped by the DDM builder because the response came "
    "during the pulse; 5 UCLA 0% pulses without any response have unknowable direction). Session acceptance is "
    "upstream and pulse-independent at trial level. Onset-eligible and pulse-vs-control contrasts carry their own "
    "conditions (pseudo-onsets for UCLA controls).",
}


if __name__ == "__main__":
    main()
