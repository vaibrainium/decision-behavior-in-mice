"""Positive, mean-one trial gain applied after the sensory front end.

Gain scales the complete mapped evidence stream (baseline and every pulse
channel) while leaving directional drift bias and internal diffusion unchanged.
The independent unit_sv normal is reused only with additive sv disabled.
"""
from __future__ import annotations
import numpy as np
import torch
from src.ddm.simulator import (
    CHANNEL_WEIGHTS,DriftDiffusionSimulator,_TorchSimulator,
    front_end_active,front_end_numpy,front_end_torch,
)


def evidence_gains(sigma,normal):
    sigma=float(sigma)
    if not np.isfinite(sigma)or sigma<0:raise ValueError('gain_sigma must be finite and nonnegative')
    z=np.asarray(normal,dtype=np.float64)
    if not np.isfinite(z).all():raise ValueError('Gain normal draws must be finite')
    return np.exp(sigma*z-.5*sigma*sigma)


class EvidenceGainSimulator(DriftDiffusionSimulator):
    def simulate_trials(self,stimulus,params,unit_noise=None,unit_sv=None,unit_sz=None,labels=None):
        sigma=float(params.get('gain_sigma',0.))
        if not np.isfinite(sigma)or sigma<0:raise ValueError('gain_sigma must be finite and nonnegative')
        if sigma==0.:
            return super().simulate_trials(stimulus,params,unit_noise,unit_sv,unit_sz,labels)
        if float(params.get('sv',0.))!=0.:
            raise ValueError('Positive gain replaces additive sv; do not correlate them through the same draw')
        parts=stimulus if isinstance(stimulus,tuple)else(stimulus,)
        if len(parts)>len(CHANNEL_WEIGHTS)+1:raise ValueError('Too many evidence channels')
        if labels is None:
            if isinstance(stimulus,tuple):raise ValueError('labels are required for tuple stimuli')
            labels=stimulus[:,0]
        n=parts[0].shape[0]
        z=np.random.standard_normal(n)if unit_sv is None else np.asarray(unit_sv)
        if z.shape!=(n,):raise ValueError(f'Expected {n} independent gain draws, received {z.shape}')
        gain=evidence_gains(sigma,z).astype(np.float32)
        if isinstance(self._backend,_TorchSimulator):
            values=[p.to(self.device,dtype=torch.float32)if isinstance(p,torch.Tensor)
                    else self._backend._to_device(p,f'stimulus_{i}'if len(parts)>1 else'stimulus')
                    for i,p in enumerate(parts)]
            mapped=values[0]
            for name,channel in zip(CHANNEL_WEIGHTS,values[1:]):mapped=mapped+float(params.get(name,1.))*channel
            if front_end_active(params):mapped=front_end_torch(mapped,params)
            mapped=mapped*torch.as_tensor(gain,device=self.device)[:,None]
        else:
            mapped=np.asarray(parts[0],dtype=np.float32)
            for name,channel in zip(CHANNEL_WEIGHTS,parts[1:]):mapped=mapped+float(params.get(name,1.))*np.asarray(channel,dtype=np.float32)
            if front_end_active(params):mapped=front_end_numpy(mapped,params)
            mapped=mapped*gain[:,None]
        # The front end has already acted before gain; never apply it twice.
        return super().simulate_trials(mapped,{**params,'fe_gamma':1.,'fe_beta':0.,'fe_h':0.},
            unit_noise,unit_sv,unit_sz,labels)
