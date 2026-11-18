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
import numpy as np
from src.utils.pmf_utils import fit_psychometric_function
from scripts.paper.style import RC
from scripts.paper.figure3B_control_fits import BLUE, ORANGE


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--psychometric',choices=['joined','logit4'],default='joined')
    a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    tables={}
    for name in ['psychometric_group','rt_group','psychometric_mouse','rt_mouse','fit_inventory']:
        frame=pd.read_csv(a.input/(name+'.csv'))
        tables[name]=frame[frame.model.isin(['data','C'])].copy()
        tables[name].to_csv(a.output/(name+'.csv'),index=False)
    pg=tables['psychometric_group'];rg=tables['rt_group']
    logging.getLogger('fontTools').setLevel(logging.WARNING)
    fits={};parameters=[];curves=[]
    grid=np.linspace(-100,100,401)
    if a.psychometric=='logit4':
        for source in ['data','C']:
            z=pg[pg.model==source].sort_values('coh')
            fit=fit_psychometric_function(z.coh.to_numpy(),z['mean'].to_numpy(),None,'logit_4')
            pred=fit.predict(grid)
            assert np.isfinite(pred).all() and ((pred>=0)&(pred<=1)).all() and (np.diff(pred)>=-1e-12).all()
            fits[source]=pred
            parameters.append({'source':source,'weighting':'unweighted least squares on equal-mouse mean proportions',**fit.coefs_})
            curves.extend({'source':source,'signed_coherence':float(x),'p_right':float(y)} for x,y in zip(grid,pred))
        pd.DataFrame(parameters).to_csv(a.output/'psychometric_logit4_parameters.csv',index=False)
        pd.DataFrame(curves).to_csv(a.output/'psychometric_logit4_curves.csv',index=False)
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig,axes=plt.subplots(1,2,figsize=(180/25.4,88/25.4))
        fig.subplots_adjust(left=.09,right=.98,bottom=.20,top=.73,wspace=.32)
        fig.text(.025,.98,'B',fontsize=12,fontweight='bold',va='top')
        fig.text(.09,.98,'Model C fits to control behavior',fontsize=9.5,va='top')
        fig.text(.09,.89,('Points: data   |   Psychometric curves: 4-parameter fits   |   Shading: data SEM' if fits else 'Points: data   |   Lines: full-control fit   |   Shading: data SEM'),fontsize=7,color='.3')
        p,t=axes
        d=pg[pg.model=='data'];m=pg[pg.model=='C']
        p.fill_between(d.coh,d['mean']-d['sem'],d['mean']+d['sem'],color='.4',alpha=.15,lw=0)
        p.plot(d.coh,d['mean'],'o',c='.15',ms=3.5)
        if fits:
            p.plot(grid,fits['data'],'--',c='.5',lw=1.1,label='Data: 4-parameter fit')
            p.plot(grid,fits['C'],'-',c='.1',lw=1.2,label='Model C: 4-parameter fit')
            p.legend(frameon=False,fontsize=6.1,loc='upper left')
        else:
            p.plot(m.coh,m['mean'],'-',c='.15',lw=1.1)
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
        + ('Psychometric panel: dashed gray and solid black curves are separate descriptive four-parameter logistic fits to the equal-mouse observed and model-predicted proportions, respectively. The exact author equation is p(x) = lapse_rate + (1 − guess_rate − lapse_rate)/(1 + exp[−var(x − mean)]); fitting uses the same helper/default bounds as Figure 1 and unweighted least squares on group proportions. Model C logistic smoothing is not an analytical DDM prediction or a new DDM fit. Chronometric solid lines show predictions at tested coherences from each mouse’s saved full-control ' if fits else 'Solid lines show predictions at tested coherences from each mouse’s saved full-control ')
        + 'model C parameters, pooled across 20 simulations per input within mouse before averaging '
        'mice. Curves describe fits to the control data used for parameter estimation; unseen-control '
        'prediction is assessed separately by panel A’s held-out scores. RT model/data curves use '
        'identical mouse/coherence/choice cells with at least 10 observed trials; 7–10 mice contribute '
        'per RT cell. The population contains 14,014 modeled controls. Figure 1 contains one additional '
        'PSUIM7 trial with missing pulse-duration metadata absent from model inputs. No new DDM fitting, '
        'simulation, scoring or significance tests. No pulse trials analyzed.\n')
    sources={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.input/(n+'.csv') for n in tables]}
    (a.output/'manifest.json').write_text(json.dumps({'model':'C','scope':'Verified full-control predictions with optional descriptive four-parameter psychometric fits',
        'psychometric_display':a.psychometric, 'psychometric_helper_sha256':hashlib.sha256((Path(__file__).resolve().parents[2]/'src/utils/pmf_utils.py').read_bytes()).hexdigest(),
        'source_directory':str(a.input.resolve()),'source_hashes':sources,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'control_prediction_assessment':'Panel A held-out scores','parameter_and_curve_source':'Saved full-control model C fits',
        'pulse_scope':'Deferred by author'},indent=2)+'\n')
    print(a.output/'figure3B_model_C.png')


if __name__=='__main__':main()
