"""Held-out-style NLL of the fitted common model (control fit) on real vs within-coherence-shuffled motion-energy noise."""
import numpy as np
from pathlib import Path
from config import dir_config
from scripts.ddm import primacy
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, select, heldout_nll
P = Path(dir_config.data.processed)
inp = responded_only(load_inputs(P / 'ddm/ddm_inputs_global.npz'))
rng = np.random.default_rng(0)
for mouse in ['DBM12', 'PSUIM5', 'PSUIM7']:
    rows = np.flatnonzero((inp['subject_id'] == mouse) & (inp['sched_pulse_type'] == 0))
    rig = str(np.unique(inp['data_source'][rows]).item())
    params = primacy.load_fit(P / 'ddm/fits_resp_final', mouse, 'L0U0V1Z0G1', 'control', False, responded=True)['parameters']
    model = primacy.make_model('L0U0V1Z0G1', rig, responded=True)
    data, stim = select(inp, rows)
    coh = inp['signed_coherence'][rows]
    out = {}
    for label in ['real', 'shuffled', 'real_seed2']:
        x = dict(inp)
        if label == 'shuffled':
            noise = x['noise'].copy()
            for c in np.unique(coh):
                r = rows[coh == c]
                noise[r] = noise[rng.permutation(r)]
            x['noise'] = noise
        _, s = select(x, rows)
        out[label] = heldout_nll(model, params, data, s, 15, seed=2 if label == 'real_seed2' else 0)
        model.likelihood_calc.rt_nllh_weight = 0.0
        out[label + '_choice'] = heldout_nll(model, params, data, s, 15, seed=2 if label == 'real_seed2' else 0)
        model.likelihood_calc.rt_nllh_weight = 1.0
    print(mouse, len(rows), {k: round(v, 1) for k, v in out.items()}, flush=True)
