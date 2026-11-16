"""Checks the scientific meaning of multiplicative evidence variability."""
import numpy as np
import pandas as pd
import torch
from src.ddm.evidence_gain import EvidenceGainSimulator,evidence_gains
from src.ddm.simulator import DriftDiffusionSimulator,front_end_numpy
from tests.test_response_delay import fixture


def run():
    stimulus,free,fixed,p,draws=fixture()
    p={**p,'fe_gamma':.6,'fe_beta':.3,'fe_tau':.2}
    rng=np.random.default_rng(124)
    channels=(stimulus,.2*rng.normal(size=stimulus.shape).astype(np.float32))
    p['noise_weight']=1.7
    reference={}
    for device in ['cpu']+(['cuda']if torch.cuda.is_available()else[]):
        old=DriftDiffusionSimulator(device);new=EvidenceGainSimulator(device)
        a=old.simulate_trials(channels,p,**draws)
        b=new.simulate_trials(channels,{**p,'gain_sigma':0.},**draws)
        pd.testing.assert_frame_equal(a,b,check_exact=True)
        sigma=.7;g=evidence_gains(sigma,draws['unit_sv']).astype(np.float32)
        mapped=front_end_numpy(channels[0]+p['noise_weight']*channels[1],p)*g[:,None]
        ref=old.simulate_trials(mapped,{**p,'fe_gamma':1.,'fe_beta':0.},**draws)
        actual=new.simulate_trials(channels,{**p,'gain_sigma':sigma},**draws)
        pd.testing.assert_series_equal(ref.choice,actual.choice)
        np.testing.assert_allclose(ref.rt,actual.rt,atol=2e-6)
        pd.testing.assert_frame_equal(actual,new.simulate_trials(channels,{**p,'gain_sigma':sigma},**draws),check_exact=True)
        # Zero input cannot be made informative by gain; bias stays unscaled.
        zero=np.zeros_like(stimulus)
        c=old.simulate_trials(zero,p,**draws)
        d=new.simulate_trials(zero,{**p,'gain_sigma':sigma},**draws)
        pd.testing.assert_frame_equal(c,d,check_exact=True)
        reference[device]=actual
        print('PASS',device,': exact zero limit, all channels/front end before gain, unscaled bias/diffusion, deterministic')
    if 'cuda'in reference:
        pd.testing.assert_series_equal(reference['cpu'].choice,reference['cuda'].choice)
        np.testing.assert_allclose(reference['cpu'].rt,reference['cuda'].rt,atol=2e-6)
    z=rng.normal(size=500000);g=evidence_gains(.8,z)
    assert(g>0).all()and abs(g.mean()-1)<.005
    assert abs(g.var()-np.expm1(.8**2))<.015
    try:EvidenceGainSimulator('cpu').simulate_trials(stimulus,{**p,'sv':.3,'gain_sigma':.2},**draws)
    except ValueError:pass
    else:raise AssertionError('Same normal reused for gain and additive drift')
    print('PASS: positive mean-one gains, expected variance, incompatible variability rejected')


if __name__=='__main__':run()
