"""Render saved restricted-trial joint per-mouse fits without refitting."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.style import RC,LEFT_COLOR,RIGHT_COLOR


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    groups=pd.read_csv(a.source/'group_parameters.csv');data=pd.read_csv(a.source/'mouse_stage_parameters.csv');dataset='scheduled_eligible_sensitivity';data=data[data.dataset==dataset]
    groups=groups[groups.dataset==dataset];groups.to_csv(a.output/'group_parameters.csv',index=False)
    tests=pd.read_csv(a.source/'group_tests.csv');tests=tests[tests.dataset==dataset];tests.to_csv(a.output/'group_tests.csv',index=False)
    for population,stages in [('all10_early_middle',[1,2]),('same6_all_times',[1,2,3])]:
        g=groups[groups.population==population];mice=sorted(data[data.stage==3].mouse.unique()) if len(stages)==3 else sorted(data.mouse.unique())
        for _,q in g.iterrows():
            z=data[data.mouse.isin(mice)&(data.stage==q.stage)&(data.direction==q.direction)]
            for par in ['alpha_full','beta_change']:
                assert len(z)==q[par+'_count']
                assert np.isclose(z[par].mean(),q[par+'_mean']) and np.isclose(z[par].sem(),q[par+'_sem'])
        with plt.rc_context(RC):
            fig,axes=plt.subplots(1,2,figsize=(7.5,3.25),layout='constrained')
            for ax,param,label in zip(axes,['alpha_full','beta_change'],['α: full additive coherence offset (% coherence)','Δβ: slope change from control (per % coherence)']):
                for direction,color,text in [(-1,LEFT_COLOR,'Leftward pulse'),(1,RIGHT_COLOR,'Rightward pulse')]:
                    q=g[g.direction==direction].sort_values('stage');ax.errorbar(q.stage,q[param+'_mean'],yerr=q[param+'_sem'],fmt='o-',c=color,capsize=3,label=text)
                ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=stages,xticklabels=[{1:'Early',2:'Middle',3:'Late'}[s] for s in stages],xlabel='Pulse stage',ylabel=label)
            axes[0].legend();fig.suptitle(f'Restricted trial set: joint model fitted per mouse, same {len(mice)} mice\nMean ± SEM; notebook offset convention; no individual fits excluded',fontsize=8)
            for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{population}.{ext}',dpi=250)
            plt.close(fig)
    manifest={'dataset':dataset,'original_source_trial_count':21725,'refitted':False,'means_sem_independently_verified':True,'primary':'all10_early_middle.png','companion':'same6_all_times.png','alpha':'Full additive offset, notebook coh+A convention','beta':'Change from mouse-specific control slope','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.source/'group_parameters.csv',a.source/'mouse_stage_parameters.csv',a.source/'group_tests.csv',Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
