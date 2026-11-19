"""Standalone descriptive exponential for compensated pulse influence; no decision-model refits."""
import argparse, hashlib, json, subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scripts.paper.build_paper_2026_11_15 import plt, STYLE
from scripts.behavior.huk_shadlen_replication import load, TRIAL_TABLE
from scripts.behavior.pulse_decomposition import design


def fit_exp(x,y):
    ref=float(x.min())
    def evaluate(log_tau):
        basis=np.exp(-(x-ref)/np.exp(log_tau))
        amplitude=max(0.,float(basis@y/(basis@basis)))
        return float(np.sum((y-amplitude*basis)**2)),amplitude
    grid=np.linspace(-5,7,241)
    losses=np.array([evaluate(z)[0] for z in grid]);best=int(np.argmin(losses))
    lo=grid[max(0,best-1)];hi=grid[min(len(grid)-1,best+1)]
    opt=minimize_scalar(lambda z:evaluate(z)[0],bounds=(lo,hi),method='bounded')
    loss,amp=evaluate(opt.x)
    return {'amplitude':amp,'tau_s':float(np.exp(opt.x)),'sse':loss,'log_tau':float(opt.x),
            'boundary':bool(opt.x < -4.99 or opt.x > 6.99),'reference_s':ref}


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;out.mkdir(parents=True,exist_ok=False)
    root=Path('dissemination/pulse_dynamics_2026-11-13')
    obs=pd.read_csv(root/'data_readouts.csv');obs=obs[(obs.scope=='all_coherences')&(obs.lo_s>=.3)].sort_values('bin').copy()
    bootstrap=pd.read_csv(root/'data_bootstrap_readouts.csv');bootstrap=bootstrap[(bootstrap.scope=='all_coherences')&(bootstrap.lo_s>=.3)]
    u,_,_=design(load());coords=u.groupby('bin').rel_rt_s.agg(mean_delay_s='mean',n_trials='size').reset_index()
    obs=obs.merge(coords,on='bin',validate='one_to_one')
    assert (obs['n']==obs.n_trials).all()
    x=obs.mean_delay_s.to_numpy();y=obs.gammaT.to_numpy();fit=fit_exp(x,y)
    fits=[];curves=[];grid=np.linspace(x.min(),x.max(),301)
    for rep,g in bootstrap.groupby('rep'):
        g=g.set_index('bin').reindex(obs.bin)
        if not np.isfinite(g.gammaT).all(): continue
        f=fit_exp(x,g.gammaT.to_numpy());fits.append({'rep':int(rep),**f})
        curves.append(f['amplitude']*np.exp(-(grid-f['reference_s'])/f['tau_s']))
    fitted=pd.DataFrame(fits);fitted.to_csv(out/'bootstrap_parameters.csv',index=False)
    lo,hi=np.percentile(curves,[2.5,97.5],axis=0)
    prediction=fit['amplitude']*np.exp(-(grid-fit['reference_s'])/fit['tau_s'])
    pd.DataFrame({'delay_s':grid,'fit':prediction,'ci_lo':lo,'ci_hi':hi}).to_csv(out/'curve.csv',index=False)
    intervals=bootstrap.groupby('bin').gammaT.quantile([.025,.975]).unstack()
    obs['ci_lo']=obs.bin.map(intervals[.025]);obs['ci_hi']=obs.bin.map(intervals[.975])
    obs['fit']=fit['amplitude']*np.exp(-(x-fit['reference_s'])/fit['tau_s']);obs['residual']=y-obs['fit']
    obs.to_csv(out/'observations.csv',index=False)
    tau_ci=np.percentile(fitted.tau_s,[2.5,97.5])
    with plt.rc_context(STYLE):
        fig,ax=plt.subplots(figsize=(145/25.4,103/25.4));fig.subplots_adjust(left=.16,right=.96,bottom=.21,top=.77)
        ax.vlines(x,obs.ci_lo,obs.ci_hi,color='black',lw=1)
        ax.plot(x,y,'o',color='black',label='Observed; mouse-bootstrap 95% CI')
        ax.fill_between(grid,lo,hi,color='#0072B2',alpha=.17,linewidth=0)
        ax.plot(grid,prediction,color='#0072B2',lw=1.5,label='Exponential description; pointwise 95% band')
        ax.axhline(0,color='.7',lw=.7)
        ax.set(xlabel='Mean time from pulse to response (s)',ylabel='Dilution-adjusted pulse influence\n(% coherence · s)')
        ax.legend(loc='upper right',fontsize=6)
        fig.text(.08,.96,'Exponential description of compensated pulse influence',fontsize=9,va='top')
        fig.text(.16,.85,f'τ = {fit["tau_s"]:.2f} s; fixed zero asymptote',fontsize=7)
        fig.text(.16,.04,'Exploratory descriptive fit; τ is not an intrinsic forgetting time constant.',fontsize=6)
        for ext in ['png','pdf','svg']:fig.savefig(out/f'exponential_preview.{ext}',dpi=300)
        plt.close(fig)
    metadata={'fit':fit,'tau_percentile_interval_s':tau_ci.tolist(),'bootstrap_fits':len(fitted),
              'boundary_fits':int(fitted.boundary.sum()),'n_mice':int(u.mouse.nunique()),
              'scope':'Descriptive unweighted least squares across six displayed bins; zero asymptote fixed, amplitude nonnegative. Negative observations retained. No p value or mechanistic model comparison.',
              'time_coordinates':'Observed mean pulse-to-response latency per bin, fixed across bootstrap fits; timing-coordinate uncertainty not propagated.',
              'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'source_sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'data_readouts.csv',root/'data_bootstrap_readouts.csv',TRIAL_TABLE,Path(__file__)]}}
    (out/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (out/'caption.md').write_text('Standalone exploratory exponential description of the existing dilution-adjusted pulse readout. Black points and intervals are the unchanged estimates and percentile mouse-bootstrap 95% intervals for the six bins shown in Figure 4D. Horizontal positions are the actual mean pulse-to-response latencies; unequal bin widths are not represented as ordinal steps. The blue curve fits y=A exp[−(t−t_ref)/τ], with a fixed zero asymptote and nonnegative amplitude, by unweighted least squares across bins. All six bins and the negative late estimate are retained. Blue shading propagates the saved whole-mouse bootstrap readouts through the fit, conditional on the observed time coordinates. This curve is a descriptive approximation to a plateau followed by a decline, not a fitted decision process or a direct intrinsic forgetting-time estimate. Figure 4 remains unchanged.\n')
    print(json.dumps({'tau_s':fit['tau_s'],'tau_ci':tau_ci.tolist(),'bootstrap_fits':len(fitted),'boundary_fits':int(fitted.boundary.sum()),'residuals':obs.residual.tolist()}))

if __name__=='__main__':main()
