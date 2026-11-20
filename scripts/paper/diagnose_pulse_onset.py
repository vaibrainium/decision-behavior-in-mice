"""Compare saved pulse predictions with observed choices and response timing on matched support."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("dissemination/paper_accumulation/draft_2026-11-15")
PRIMACY = BASE / "pulse_model_primacy_2026-11-18"
CACHE = Path("dissemination/pulse_dynamics_2026-11-13/cache")
MODELS = ("pulse_norm_ugm_no_sv", "pulse_linear_leak")
CELL = ["mouse", "stage_index", "coherence_pct", "direction"]


def compare_cells(cells, stages, arms, value):
    """One common set of signed coherences across arms, stages and predictions for each mouse."""
    wide = cells.pivot(index=["source", "mouse", "coherence_pct"],
                       columns=["stage_index", "direction"], values=value)
    cols = pd.MultiIndex.from_product([stages, arms])
    wide = wide.reindex(columns=cols).dropna()
    keep = wide.groupby(level=["mouse", "coherence_pct"]).size().eq(cells.source.nunique())
    wide = wide[wide.index.droplevel("source").isin(keep[keep].index)]
    if wide.empty:
        raise ValueError("No common coherence cells")
    return wide


def summarize(wide, stages, kind):
    group = wide.groupby(level=["source", "mouse"])
    rows = []
    for (source, mouse), subset in group:
        for s in stages:
            if kind == "any_minus_sham_pp":
                diff = (subset[s, 1] + subset[s, -1]) / 2 - subset[s, 0]
            else:
                diff = subset[s, 1] - subset[s, -1]
            rows.append(dict(source=source, mouse=mouse, stage=s, measure=kind,
                             n_coherences=len(subset), pp=100 * diff.mean()))
    return pd.DataFrame(rows)


def direct_choice(out):
    obs = pd.read_csv(PRIMACY / "observed_cells.csv").assign(source="data")
    assert obs.n.sum() == 21725
    parts = [obs]
    for family in MODELS:
        for seed in (0, 1):
            files = [PRIMACY / "simulation_cells" / f"{family}_{mouse}_seed{seed}_r30.csv"
                     for mouse in sorted(obs.mouse.unique())]
            assert len(files) == 10
            parts.extend(pd.read_csv(p).assign(source=f"{family}/{seed}") for p in files)
    cells = pd.concat(parts).query("direction != 0 and abs(coherence_pct) <= 36")
    assert not cells.duplicated(["source"] + CELL).any()
    pieces = []
    for stages in ((1, 2), (1, 2, 3)):
        wide = compare_cells(cells, stages, (-1, 1), "y")
        frame = summarize(wide, stages, "right_choice_difference_pp")
        frame["support"] = "early_middle" if len(stages) == 2 else "three_stages"
        pieces.append(frame)
        if len(stages) == 2:
            n = cells[cells.source == "data"].pivot(index=["mouse", "coherence_pct"],
                                                    columns=["stage_index", "direction"], values="n")
            n = n.reindex(columns=wide.columns).dropna()
            # One fixed observed overlap weight for each signed coherence, shared
            # across all four arms and all model predictions within a mouse.
            overlap = 4 / (1 / n).sum(axis=1)
            idx = wide.index.droplevel("source")
            weights = pd.Series(overlap.reindex(idx).to_numpy(), index=wide.index)
            weights /= weights.groupby(level=["source", "mouse"]).transform("sum")
            means = wide.mul(weights, axis=0).groupby(level=["source", "mouse"]).sum()
            contrasts = pd.DataFrame({s: 100 * (means[s, 1] - means[s, -1]) for s in stages})
            contrasts.to_csv(out / "overlap_weighted_mouse_by_seed.csv")
        support = wide.index[wide.index.get_level_values("source") == "data"].to_frame(index=False)
        support.to_csv(out / f"coherence_support_{len(stages)}stages.csv", index=False)
    return pd.concat(pieces).assign(horizon="eligible_responses")


def timed_cells(meta, outcomes):
    """Cumulative incidence among responses by deadline that were still pending at pulse onset."""
    t = outcomes.merge(meta, on="row", validate="many_to_one")
    t = t[(t.choice >= 0) & (t.rt >= t.onset_s) & (t.rt <= 5)].copy()
    delay = t.rt - t.onset_s
    for label, limit in (("0.5s", .5), ("1s", 1.), ("2s", 2.), ("deadline", np.inf)):
        occurred = delay <= limit
        t[f"any_{label}"] = occurred
        # Right responses score +1/2, left -1/2. A right-minus-left pulse
        # contrast at the deadline equals the difference in right-choice probability.
        t[f"signed_{label}"] = occurred * (t.choice - .5)
    columns = [c for c in t if c.startswith(("any_", "signed_"))]
    return t.groupby(CELL, as_index=False)[columns].mean()


def response_time(out):
    m = pd.read_pickle(CACHE / "metadata.pkl").reset_index(drop=True)
    assert len(m) == 19579 and m.row.is_unique
    schedule = pd.read_csv(PRIMACY / "preselection.csv")
    expected = schedule[schedule.onset_stratum.isin(["early", "middle"])]
    assert set(m.trial_id) == set(expected.trial_id)
    m = m[m.coherence_pct.abs() <= 36].copy()
    m["stage_index"] = m.onset_stratum.map({"early": 1, "middle": 2})
    m["direction"] = m.pulse
    parts = []
    for mouse, sub in m.groupby("mouse"):
        meta = sub[["row", "onset_s"] + CELL]
        obs = sub.assign(rt=sub.rt_s, choice=sub.response_side.eq("R").astype(int))
        parts.append(timed_cells(meta, obs[["row", "rt", "choice"]]).assign(source="data"))
        for family in MODELS:
            for seed in (0, 1):
                record = pd.read_pickle(CACHE / f"{family}_{mouse}_seed{seed}_r30.pkl")
                assert (record["family"], record["mouse"], record["master_seed"], record["reps"]) == (family, mouse, seed, 30)
                outcomes = record["outcomes"]
                outcomes = outcomes[outcomes.row.isin(meta.row)]
                assert len(outcomes) == len(meta) * 30
                parts.append(timed_cells(meta, outcomes).assign(source=f"{family}/{seed}"))
    cells = pd.concat(parts)
    frames = []
    for horizon in ("0.5s", "1s", "2s", "deadline"):
        for prefix, measure in (("signed", "directional_response_pp"), ("any", "any_minus_sham_pp")):
            wide = compare_cells(cells, (1, 2), (-1, 0, 1), f"{prefix}_{horizon}")
            frames.append(summarize(wide, (1, 2), measure).assign(horizon=horizon, support="early_middle"))
    result = pd.concat(frames)
    assert result.query("horizon == 'deadline' and measure == 'any_minus_sham_pp'").pp.abs().max() < 1e-9
    return result


def weighting_readout(out):
    from scripts.paper.pulse_time_continuous import TAIL, fit
    from scripts.paper.pulse_time_ordinal import prepare_ordinal

    ordinal = BASE / "pulse_time_ordinal_2026-11-18"
    coefs = pd.read_csv(ordinal / "coefficients.csv")
    ref = coefs.query("comparison == 'all_available_10' and objective == 'wls'").set_index("parameter").estimate
    obs = pd.read_csv(PRIMACY / "observed_cells.csv")
    mice = sorted(obs.mouse.unique())
    upper = MODELS[0]
    rigs = pd.read_csv(PRIMACY / "preselection.csv").groupby("mouse").rig.first()
    datasets = {"data": obs}
    for seed in (0, 1):
        datasets[f"{upper}/{seed}"] = pd.concat([
            pd.read_csv(PRIMACY / "simulation_cells" / f"{upper}_{m}_seed{seed}_r30.csv") for m in mice
        ])
    records = []
    for source, cells in datasets.items():
        for cohort in ("all", "ucla", "uw"):
            chosen = [m for m in mice if cohort == "all" or rigs[m] == cohort]
            start = ref.loc[[f"baseline_{m}" for m in chosen] + TAIL].to_numpy()
            for weighting in ("trial", "equal_mouse"):
                sample = cells[cells.mouse.isin(chosen)].copy()
                if weighting == "equal_mouse":
                    sample["n"] *= (sample.n.sum() / len(chosen)) / sample.groupby("mouse").n.transform("sum")
                    sample["k"] = sample.n * sample.y
                    assert np.ptp(sample.groupby("mouse").n.sum()) < 1e-8
                data = prepare_ordinal(sample, chosen)
                result = fit(data, "wls", start)
                theta = result.theta
                wmid, slope = theta[len(chosen)+2:len(chosen)+4]
                near_bound = np.isclose(theta, result.bounds[0], atol=1e-6) | np.isclose(theta, result.bounds[1], atol=1e-6)
                records.append(dict(source=source, cohort=cohort, weighting=weighting, early=wmid-slope,
                                    middle=wmid, late=wmid+slope if cohort != "ucla" else np.nan, slope=slope,
                                    n_success=sum(x["success"] for x in result.attempts), n_bound=near_bound.sum()))
                if cohort == "all" and weighting == "trial":
                    if source == "data":
                        assert np.isclose(slope, ref.loc["direction_time_offset"], atol=1e-5)
                    else:
                        saved = pd.read_csv(PRIMACY / "model_readout_by_seed.csv")
                        expected = saved[(saved.family == upper) & (saved.seed == int(source.split("/")[1]))]
                        assert np.isclose(slope, expected.slope_per_stage.item(), atol=1e-5)
    pd.DataFrame(records).to_csv(out / "ordinal_weighting.csv", index=False)


def single_dataset_variation(out):
    """Assess finite-trial variation for the two dense mice on their seven common coherences."""
    meta = pd.read_pickle(CACHE / "metadata.pkl").reset_index(drop=True)
    obs_cells = pd.read_csv(PRIMACY / "observed_cells.csv")
    family = MODELS[0]
    draws = []
    for mouse in ("PSUIM6", "PSUIM7"):
        m = meta[(meta.mouse == mouse) & (meta.pulse != 0) & (meta.coherence_pct.abs() <= 36)].copy()
        m["stage"] = m.onset_stratum.map({"early": 1, "middle": 2})
        for seed in (0, 1):
            raw = pd.read_pickle(CACHE / f"{family}_{mouse}_seed{seed}_r30.pkl")["outcomes"]
            t = raw.merge(m[["row", "stage", "coherence_pct", "pulse", "onset_s", "offset_s"]], on="row")
            t = t[(t.choice >= 0) & (t.rt <= 5) & (t.rt >= t.offset_s) & (t.rt - t.onset_s >= .1)]
            p = t.groupby(["rep", "stage", "coherence_pct", "pulse"]).choice.mean().unstack()
            assert len(p) == 30 * 2 * 7 and p.notna().all().all()
            wide = (100 * (p[1] - p[-1])).groupby(level=["rep", "stage"]).mean().unstack()
            wide.columns = ["early", "middle"]
            wide["early_minus_middle"] = wide.early - wide.middle
            draws.append(wide.reset_index().assign(seed=seed, mouse=mouse))
    draws = pd.concat(draws).melt(id_vars=["rep", "seed", "mouse"], var_name="measure", value_name="pp")
    draws.to_csv(out / "conditional_replicates.csv", index=False)
    stats = draws.groupby(["mouse", "measure"]).pp.agg(
        predicted_mean="mean", q025=lambda x: x.quantile(.025), q975=lambda x: x.quantile(.975),
        min_pp="min", max_pp="max").reset_index()
    actual = obs_cells[(obs_cells.mouse.isin(["PSUIM6", "PSUIM7"])) & (obs_cells.direction != 0) &
                       (obs_cells.coherence_pct.abs() <= 36)]
    y = actual.pivot(index=["mouse", "stage_index", "coherence_pct"], columns="direction", values="y")
    assert len(y) == 2 * 2 * 7
    obs = (100 * (y[1] - y[-1])).groupby(level=["mouse", "stage_index"]).mean().unstack()
    obs.columns = ["early", "middle"]
    obs["early_minus_middle"] = obs.early - obs.middle
    observed = obs.reset_index().melt(id_vars="mouse", var_name="measure", value_name="observed_pp")
    stats.merge(observed, on=["mouse", "measure"], validate="one_to_one").to_csv(
        out / "conditional_prediction_ranges.csv", index=False)


def session_residuals(out):
    """Compare the full-fit model on the same session schedules within the two densest mice."""
    m = pd.read_pickle(CACHE / "metadata.pkl").reset_index(drop=True)
    rows = []
    keys = ["session_id", "onset_stratum", "coherence_pct", "pulse"]
    for mouse in ("PSUIM6", "PSUIM7"):
        sub = m[(m.mouse == mouse) & (m.pulse != 0) & (m.coherence_pct.abs() <= 36)]
        data = sub[(sub.rt_s >= sub.offset_s) & (sub.rt_s - sub.onset_s >= .1)].copy()
        counts = data.assign(k=data.response_side.eq("R")).groupby(keys).k.agg(["sum", "size"])
        p = (counts["sum"] / counts["size"]).unstack("pulse")
        n = counts["size"].unstack("pulse")
        expected = []
        for seed in (0, 1):
            record = pd.read_pickle(CACHE / f"{MODELS[0]}_{mouse}_seed{seed}_r30.pkl")
            sim = record["outcomes"].merge(sub[["row", "onset_s", "offset_s"] + keys], on="row")
            sim = sim[(sim.choice >= 0) & (sim.rt <= 5) & (sim.rt >= sim.offset_s) & (sim.rt - sim.onset_s >= .1)]
            expected.append(sim.groupby(keys).choice.mean().unstack("pulse").reindex(p.index))
        model = (expected[0] + expected[1]) / 2
        complete = (p.notna().all(axis=1) & model.notna().all(axis=1))
        weight = 2 / (1/n.loc[complete, -1] + 1/n.loc[complete, 1])
        weight /= weight.groupby(level=["session_id", "onset_stratum"]).transform("sum")
        vals = pd.DataFrame(dict(observed=100 * (p[1]-p[-1]), predicted=100 * (model[1]-model[-1])))
        by_session = vals.loc[complete].mul(weight, axis=0).groupby(level=["session_id", "onset_stratum"]).sum()
        by_session["residual"] = by_session.observed - by_session.predicted
        by_session["coherence_cells"] = weight.groupby(level=["session_id", "onset_stratum"]).size()
        rows.append(by_session.reset_index().assign(mouse=mouse))
    pd.concat(rows, ignore_index=True).to_csv(out / "session_residuals.csv", index=False)


def main(out):
    out.mkdir(parents=True, exist_ok=False)
    session_residuals(out)
    single_dataset_variation(out)
    weighting_readout(out)
    schedules = pd.read_csv(PRIMACY / "preselection.csv")
    rigs = schedules[["mouse", "rig"]].drop_duplicates().set_index("mouse").rig
    eligible = pd.read_csv(BASE / "pulse_psychometric_timing_2026-11-18/eligible_trials.csv")
    eligible.query("direction != 0").groupby(["rig", "mouse", "onset_stratum"]).size().rename("n").to_csv(out / "pulse_support.csv")
    mouse = pd.concat([direct_choice(out), response_time(out)], ignore_index=True)
    mouse["rig"] = mouse.mouse.map(rigs)
    mouse.to_csv(out / "mouse_by_seed.csv", index=False)
    mouse["source"] = mouse.source.str.split("/").str[0]
    keys = ["source", "mouse", "rig", "support", "measure", "horizon", "stage"]
    mouse = mouse.groupby(keys, as_index=False).agg(pp=("pp", "mean"), n_coherences=("n_coherences", "first"))
    mouse.to_csv(out / "mouse.csv", index=False)
    grouped = pd.concat([mouse.assign(group="all"), mouse.assign(group=mouse.rig)])
    gkeys = ["source", "group", "support", "measure", "horizon", "stage"]
    grouped.groupby(gkeys).pp.agg(["mean", "median", "count"]).to_csv(out / "group.csv")
    paired = mouse.pivot(index=keys[:-1], columns="stage", values="pp")
    paired["early_minus_middle_pp"] = paired[1] - paired[2]
    paired.reset_index().to_csv(out / "mouse_paired_stages.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    main(parser.parse_args().output)
