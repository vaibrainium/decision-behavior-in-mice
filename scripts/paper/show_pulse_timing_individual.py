"""Display saved per-mouse early midpoints and the DBM12 boundary solution."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.style import RC,LEFT_COLOR,RIGHT_COLOR


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    fits=pd.read_csv(a.source/'fits.csv');cells=pd.read_csv(a.source/'mouse_cells.csv')
    f=fits[(fits.method=='free4')&(fits.stage=='early')&(fits.direction!=0)]
    pair=f.pivot(index='mouse',columns='direction',values='alpha').sort_index();assert pair.shape==(10,2) and pair.notna().all().all()
    pair.rename(columns={-1:'left_alpha',1:'right_alpha'}).to_csv(a.output/'early_mouse_alpha_pairs.csv')
    z=cells[(cells.mouse=='DBM12')&(cells.onset_stratum=='early')&(cells.direction==-1)].sort_values('coherence_pct')
    q=f[(f.mouse=='DBM12')&(f.direction==-1)].iloc[0]
    assert np.isclose(q.alpha,-100) and z['size'].sum()==105
    observed_sse=np.sum(z['size']*(q.lower_asymptote+(q.upper_asymptote-q.lower_asymptote)*expit(q.beta*(z.coherence_pct-q.alpha))-z['mean'])**2)
    assert np.isclose(observed_sse,q.weighted_sse)
    with plt.rc_context(RC):
        fig,axes=plt.subplots(1,2,figsize=(8,3.8),layout='constrained',gridspec_kw={'width_ratios':[1,1.3]})
        ax=axes[0];yy=np.arange(len(pair))
        for i,(_,row) in enumerate(pair.iterrows()):ax.plot([row[-1],row[1]],[i,i],c='.8',lw=.8,zorder=1)
        ax.scatter(pair[-1],yy,c=LEFT_COLOR,s=20,label='Left pulse',zorder=2);ax.scatter(pair[1],yy,c=RIGHT_COLOR,s=20,label='Right pulse',zorder=2)
        ax.axvline(0,c='.7',ls=':',lw=.7)
        ax.set(yticks=yy,yticklabels=pair.index,ylim=(len(pair)-.5,-.8),xlim=(-108,43),xlabel='Individual α (% coherence)',title='Early pulses: one paired fit per mouse')
        ax.legend(loc='lower left',fontsize=6)
        ax=axes[1];grid=np.linspace(-100,100,501);pred=q.lower_asymptote+(q.upper_asymptote-q.lower_asymptote)*expit(q.beta*(grid-q.alpha))
        ax.plot(grid,pred,ls='--',c=LEFT_COLOR,lw=1,label='Extrapolated fit')
        support=(grid>=z.coherence_pct.min())&(grid<=z.coherence_pct.max());ax.plot(grid[support],pred[support],c=LEFT_COLOR,lw=1.4,label='Fit within observed range')
        ax.scatter(z.coherence_pct,z['mean'],c=LEFT_COLOR,s=22,zorder=3,label='Observed choices')
        for _,row in z.iterrows():ax.annotate(f'n={int(row["size"])}',(row.coherence_pct,row['mean']),xytext=(0,7),textcoords='offset points',ha='center',fontsize=6)
        ax.axvline(-100,c='.5',ls=':',lw=.8);ax.axhline(.5,c='.8',ls=':',lw=.6)
        ax.text(.02,.96,'α = −100: lower fitting bound\nObserved coherence range: −18 to +100%',transform=ax.transAxes,va='top',fontsize=7)
        ax.set(xlim=(-108,108),ylim=(0,1),xlabel='Signed baseline coherence (%)',ylabel='P(right choice)',title='DBM12: early left pulse, 105 trials')
        ax.legend(loc='lower right',fontsize=6)
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'individual_fits.{ext}',dpi=250)
        plt.close(fig)
    z.to_csv(a.output/'DBM12_early_left_observed.csv',index=False)
    summary={'analysis':'Original timing plot fits each mouse/time/direction separately, then reports across-mouse mean and SEM; no timing-effect tests performed','DBM12':{'alpha':float(q.alpha),'beta':float(q.beta),'lower_asymptote':float(q.lower_asymptote),'upper_asymptote':float(q.upper_asymptote),'weighted_sse':float(q.weighted_sse),'n_trials':int(z['size'].sum()),'coherence_range':[float(z.coherence_pct.min()),float(z.coherence_pct.max())]},'n_mice':len(pair),'mean_early_left_alpha':float(pair[-1].mean()),'mean_early_right_alpha':float(pair[1].mean()),'refitted':False,'all_mice_retained':True,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.source/'fits.csv',a.source/'mouse_cells.csv',Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
