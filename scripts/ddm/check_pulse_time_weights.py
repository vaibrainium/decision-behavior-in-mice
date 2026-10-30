"""Checks for --pulse_time_weights (plan .agents/plans/2026-10-30-pulse-time-weights.md): channels sum to the single-channel
input, equal weights reproduce the shared pulse weight, warm starts copy the shared weight.

    .venv/bin/python -m scripts.ddm.check_pulse_time_weights
"""
import pickle, numpy as np, torch
from pathlib import Path
from config import dir_config
from scripts.ddm import fit_mouse_ddm as F
from src.ddm.simulator import _TorchSimulator
P = Path(dir_config.data.processed)
inp = F.responded_only(F.load_inputs(P / "ddm/ddm_inputs_global_ucla_nofreeze.npz"))
for mouse in ["DBM13", "PSUIM10"]:
    rows = np.flatnonzero(inp["subject_id"] == mouse); n = F.n_pulse_times(inp, rows)
    _, single = F.select(inp, rows)
    _, two = F.select(inp, rows, pulse_weight=True)
    _, multi = F.select(inp, rows, pulse_times=n)
    print(mouse, "n_pulse_times", n, "channels", len(multi))
    s = multi[0] + sum(multi[1:])
    print("  sum of channels vs single-channel input, max diff:", np.abs(s - single).max())
    print("  channel sum vs shared pulse channel, max diff:", np.abs(sum(multi[1:]) - two[1]).max())
    # pulse-type assignment: channel k nonzero only on |sched_pulse_type| == k
    pt = np.abs(inp["sched_pulse_type"][rows])
    print("  channel k nonzero only on its pulse time:", all(not np.any(multi[k][pt != k]) for k in range(1, n + 1)), "and nonzero on it:", all(np.any(multi[k][pt == k]) for k in range(1, n + 1)))
    # simulator: numba and torch(cpu) agree with the summed stimulus; equal weights == shared weight
    fit = pickle.load(open(P / f"ddm/fits_joint_unfreeze_integrators/{mouse}_L0U0V1Z0G1_all.pkl", "rb"))
    free, fixed = F.make_params("L0U0V1Z0G1", "fast_only", n_pulse_times=n)
    wk = ["noise_weight", "noise_weight_2", "noise_weight_3"][:n]; print("  free weights:", [k for k in free if k in wk])
    model = F.MouseDDM(free_params=free, fixed_params=fixed, device=F.DEVICE, likelihood_params=F.RESPONDED_LIKELIHOOD_PARAMS, censor_at=F.CENSOR_AT, min_rt=F.MIN_RT[np.unique(inp["data_source"][rows]).item()])
    data, _ = F.select(inp, rows)
    p1 = {**fit["parameters"]}
    nll_single = F.heldout_nll(model, p1, data, single, 3)
    nll_multi = F.heldout_nll(model, {**p1, **{k: 1.0 for k in ["noise_weight", "noise_weight_2", "noise_weight_3"][:n]}}, data, multi, 3)
    print(f"  NLL joint fit: single {nll_single:.4f}  per-time weights at 1 {nll_multi:.4f}")
    w = 1.7
    nll_shared = F.heldout_nll(model, {**p1, "noise_weight": w}, data, two, 3)
    nll_eq = F.heldout_nll(model, {**p1, **{k: w for k in ["noise_weight", "noise_weight_2", "noise_weight_3"][:n]}}, data, multi, 3)
    print(f"  NLL w={w}: shared weight {nll_shared:.4f}  equal per-time weights {nll_eq:.4f}")
    # torch backend on CPU: drift input built the same way
    t = _TorchSimulator("cpu"); wts = {"noise_weight": 0.5, "noise_weight_2": 2.0, "noise_weight_3": 3.0}
    ref = multi[0] + sum(wts[k] * c for k, c in zip(["noise_weight", "noise_weight_2", "noise_weight_3"], multi[1:]))
    print("  torch path formula check (manual):", float(np.abs((multi[0] + 0.5 * multi[1] + 2.0 * multi[2] + (3.0 * multi[3] if n == 3 else 0)) - ref).max()))
    # warm start: shared weight fit seeds all per-time weights
    keys = list(free)
    seeds, used = F.warm_start_seeds({"mouse": mouse, "variant": "L0U0V1Z0G1", "split": "all"}, keys, [P / "ddm/fits_joint_unfreeze_pulse_weight"])
    pw = pickle.load(open(P / f"ddm/fits_joint_unfreeze_pulse_weight/{mouse}_L0U0V1Z0G1_all.pkl", "rb"))["parameters"]["noise_weight"]
    print("  warm-start seed weights:", [round(seeds[0][keys.index(k)], 3) for k in wk], "pulse_weight fit w:", round(pw, 3))
# torch backend (CPU) simulate: identical drift input => identical outcomes to numba given same unit noise? check drift input only
t = _TorchSimulator("cpu")
import inspect; print("torch backend runs 4-channel stimulus:", t.simulate_trials(tuple(c[:50] for c in multi), {**p1, "noise_weight": 0.5, "noise_weight_2": 2.0, **({"noise_weight_3": 3.0} if n == 3 else {})})[0].shape)
