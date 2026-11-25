"""Render model C psychometric and choice-conditioned mean RT fit overlays."""
import argparse
import hashlib
import json
import logging
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from scripts.paper.style import RC
from scripts.paper.figure3B_control_fits import BLUE, ORANGE


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    tables={}
    for name in ['psychometric_group','rt_group','psychometric_mouse','rt_mouse','fit_inventory']:
        frame=pd.read_csv(a.input/(name+'.csv'))
        tables[name]=frame[frame.model.isin(['data','C'])].copy()
        tables[name].to_csv(a.output/(name+'.csv'),index=False)
    pg=tables['psychometric_group'];rg=tables['rt_group']
    logging.getLogger('fontTools').setLevel(logging.WARNING)
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig,axes=plt.subplots(1,2,figsize=(180/25.4,88/25.4))
        fig.subplots_adjust(left=.09,right=.98,bottom=.20,top=.73,wspace=.32)
        fig.text(.025,.98,'B',fontsize=12,fontweight='bold',va='top')
        fig.text(.09,.98,'Model C fits to control behavior',fontsize=9.5,va='top')
        fig.text(.09,.89,'Filled points: data   |   Open diamonds + lines: saved model predictions   |   Shading: data SEM',fontsize=7,color='.3')
        p,t=axes
        d=pg[pg.model=='data'];m=pg[pg.model=='C']
        p.fill_between(d.coh,d['mean']-d['sem'],d['mean']+d['sem'],color='.4',alpha=.15,lw=0)
        p.plot(d.coh,d['mean'],'o',c='.15',ms=3.5)
        p.plot(m.coh,m['mean'],'-D',c='.15',mfc='white',mec='.15',mew=.8,ms=3.0,lw=1.1,label='Model C predictions')
        p.legend(frameon=False,fontsize=6.1,loc='upper left')
        p.set(ylabel='P(right choice)',ylim=(-.04,1.04),yticks=[0,.25,.5,.75,1],title='Psychometric')
        for choice,color,marker in [(1,ORANGE,'o'),(0,BLUE,'s')]:
            d=rg[(rg.model=='data')&(rg.choice==choice)]
            m=rg[(rg.model=='C')&(rg.choice==choice)]
            t.fill_between(d.coh,d['mean']-d['sem'],d['mean']+d['sem'],color=color,alpha=.15,lw=0)
            t.plot(d.coh,d['mean'],marker,c=color,ms=3.2)
            t.plot(m.coh,m['mean'],'-',c=color,lw=1.1,label='Right choice' if choice==1 else 'Left choice')
        t.set(ylabel='Mean RT (s)',title='Chronometric')
        t.legend(frameon=False,fontsize=6.5,loc='upper right')
        for ax in axes:
            ax.set(xlabel='Signed coherence (%)',xticks=[-100,-36,0,36,100],xlim=(-110,110))
            ax.axvline(0,c='.85',ls=':',lw=.5,zorder=0)
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'figure3B_model_C.{ext}',dpi=300,facecolor='white')
        plt.close(fig)
    (a.output/'caption.md').write_text(
        'Panel B. Model C fits to control psychometric and chronometric functions. '
        'Left: probability of a right choice versus signed coherence. Right: arithmetic mean RT '
        'conditional on right choice (orange circles) or left choice (blue squares). Points are '
        'equal-mouse observed means; shaded bands are pointwise SEM across contributing mice. '
        + 'Psychometric panel: filled circles are observed probabilities and open diamonds are saved model probabilities at the same tested coherences; straight segments join only adjacent tested coherences. No psychometric function is fitted to either series for display. Chronometric solid lines show predictions at tested coherences from each mouse’s saved full-control '
        + 'model C parameters, pooled across 20 simulations per input within mouse before averaging '
        'mice. Curves describe fits to the control data used for parameter estimation; unseen-control '
        'prediction is assessed separately by panel A’s held-out scores. RT model/data curves use '
        'identical mouse/coherence/choice cells with at least 10 observed trials; 7–10 mice contribute '
        'per RT cell. The population contains 14,014 modeled controls. Figure 1 contains one additional '
        'PSUIM7 trial with missing pulse-duration metadata absent from model inputs. No new DDM fitting, '
        'simulation, scoring or significance tests. No pulse trials analyzed.\n')
    sources={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.input/(n+'.csv') for n in tables]}
    (a.output/'manifest.json').write_text(json.dumps({'model':'C','scope':'Verified full-control predictions displayed directly at tested coherences',
        'psychometric_display':'observed points with SEM; saved model points joined across tested coherences; no logistic display fit',
        'source_directory':str(a.input.resolve()),'source_hashes':sources,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'control_prediction_assessment':'Panel A held-out scores','parameter_and_curve_source':'Saved full-control model C fits',
        'pulse_scope':'Deferred by author'},indent=2)+'\n')
    print(a.output/'figure3B_model_C.png')


if __name__=='__main__':main()
