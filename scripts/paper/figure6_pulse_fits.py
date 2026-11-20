"""Tentative Figure 6: saved full-pulse-fit predictions on pulse trials only."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scripts.paper.build_paper_2026_11_15 import plt,STYLE,BLUE,ORANGE
from src.utils.pmf_utils import fit_psychometric_function
SOURCE=Path('dissemination/figures/qc/fit_browser_2026-11-12_v7.json')
MODELS={'pulse_norm_ugm_no_sv':('Predictive winner: normalized UGM, no sᵥ','-'), 'pulse_linear_leak':('BIC winner: linear leak, with sᵥ','--')}


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
    d=json.loads(SOURCE.read_text());parts=[]
    for family,tables in [('data',d['data'])]+[(f,d['families'][f]) for f in MODELS]:
        for mouse in d['mice']:
            rows=pd.DataFrame(tables[mouse]['rows'],columns=d['columns']);rows=rows[rows.cond!='control'].copy()
            rows['mouse']=mouse;rows['family']=family;parts.append(rows)
    cells=pd.concat(parts,ignore_index=True)
    data=cells[cells.family=='data'];keys=['mouse','cond','coh']
    observed_keys=data[keys].drop_duplicates()
    for f in MODELS:
        z=cells[cells.family==f];missing=observed_keys.merge(z[keys],on=keys,how='left',indicator=True)
        assert (missing._merge=='both').all(),f
    # Match model support to observed mouse/condition/coherence cells before equal-mouse averaging.
    cells=cells.merge(observed_keys,on=keys,how='inner',validate='many_to_one')
    group=cells.groupby(['family','cond','coh'],as_index=False).agg(p=('p','mean'),sem_p=('p','sem'),rt=('rt','mean'),sem_rt=('rt','sem'),n_mice=('mouse','nunique'),n_rows=('n','sum'))
    cells.to_csv(out/'mouse_cells.csv',index=False);group.to_csv(out/'group_summaries.csv',index=False)
    parameters=[];curves=[]
    for (family,cond),z in group.groupby(['family','cond']):
        z=z.sort_values('coh');fit=fit_psychometric_function(z.coh.to_numpy(),z.p.to_numpy(),None,'logit_4')
        x=np.linspace(z.coh.min(),z.coh.max(),401);y=fit.predict(x)
        assert np.isfinite(y).all() and ((y>=0)&(y<=1)).all()
        parameters.append({'family':family,'cond':cond,**fit.coefs_})
        curves.extend({'family':family,'cond':cond,'coh':float(xx),'p':float(yy)} for xx,yy in zip(x,y))
    curves=pd.DataFrame(curves);curves.to_csv(out/'psychometric_display_curves.csv',index=False);pd.DataFrame(parameters).to_csv(out/'psychometric_display_parameters.csv',index=False)
    def render(families,stem):
        with plt.rc_context(STYLE):
            fig,axes=plt.subplots(2,3,figsize=(220/25.4,145/25.4));fig.subplots_adjust(left=.08,right=.98,bottom=.22,top=.85,wspace=.32,hspace=.48)
            for col,stage in enumerate(['early','middle','late']):
                mice=data[data.cond.str.startswith(stage)].mouse.nunique()
                axes[0,col].set_title(f'{stage.capitalize()} pulses ({mice} mice)',loc='left',fontsize=8)
                for direction,color,marker in [('left',BLUE,'v'),('right',ORANGE,'^')]:
                    cond=f'{stage} {direction}';obs=group[(group.family=='data')&(group.cond==cond)].sort_values('coh')
                    axes[0,col].errorbar(obs.coh,obs.p,yerr=obs.sem_p,fmt=marker,color=color,ms=3,capsize=1.5,ls='none')
                    z=curves[(curves.family=='data')&(curves.cond==cond)]
                    axes[0,col].plot(z.coh,z.p,':',color=color,lw=.9,alpha=.8)
                    axes[1,col].errorbar(obs.coh,obs.rt,yerr=obs.sem_rt,fmt=marker,color=color,ms=3,ls='none',capsize=1.5)
                    axes[1,col].fill_between(obs.coh,obs.rt-obs.sem_rt,obs.rt+obs.sem_rt,color=color,alpha=.12,linewidth=0)
                    for family in families:
                        name,style=MODELS[family];z=curves[(curves.family==family)&(curves.cond==cond)]
                        axes[0,col].plot(z.coh,z.p,style,color=color,lw=1.3)
                        z=group[(group.family==family)&(group.cond==cond)].sort_values('coh')
                        axes[1,col].plot(z.coh,z.rt,style,color=color,lw=1.3)
                for row in range(2):
                    axes[row,col].set(xlim=(-110,110),xticks=[-100,-36,0,36,100],xlabel='Signed baseline coherence (%)')
                axes[0,col].set(ylim=(0,1));axes[0,col].axhline(.5,color='.85',lw=.5)
                axes[1,col].set_ylim(.3,2.5)
            # Common mean-RT axis limits include every displayed value and data SEM.
            vals=group[group.family.isin(['data',*families])]
            low=min(.3,float((vals.rt-vals.sem_rt.fillna(0)).min())-.08);high=max(2.,float((vals.rt+vals.sem_rt.fillna(0)).max())+.12)
            for ax in axes[1]:ax.set_ylim(low,high)
            axes[0,0].set_ylabel('P(right response)');axes[1,0].set_ylabel('Mean RT, all responses (s)')
            for row,letter in [(0,'A'),(1,'B')]:axes[row,0].text(-.19,1.08,letter,transform=axes[row,0].transAxes,fontweight='bold',fontsize=10)
            fig.text(.035,.97,'Tentative Figure 6 | Pulse-only psychometric and chronometric fits',fontsize=10,va='top')
            handles=[Line2D([],[],c=BLUE,marker='v',ls='none',label='Left pulse: data ± mouse SEM'),Line2D([],[],c=ORANGE,marker='^',ls='none',label='Right pulse: data ± mouse SEM'),Line2D([],[],c='.4',ls=':',label='Data psychometric fit')]
            handles += [Line2D([],[],c='.2',ls=MODELS[f][1],label=MODELS[f][0]) for f in families]
            fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.53,.045),ncol=2,fontsize=6.3)
            fig.text(.08,.018,'Full-pulse-fit descriptive predictions; no control points or endpoint borrowing. Not held-out validation.',fontsize=6,color='.3')
            for ext in ['png','pdf','svg']:fig.savefig(out/f'{stem}.{ext}',dpi=300)
            plt.close(fig)
    render(list(MODELS),'figure6_comparison')
    for family in MODELS:render([family],f'figure6_{family}')
    counts=data.groupby('cond').agg(n=('n','sum'),n_mice=('mouse','nunique')).reset_index()
    counts.to_csv(out/'observed_counts.csv',index=False)
    (out/'verification.json').write_text(json.dumps({'all_prediction_cells_match_observed_support':True,'n_models':2,'control_rows_displayed':0,'coherence_endpoints_borrowed':False,'new_decision_fits':False,'new_simulations':False,'data_precision':'Saved browser per-mouse probabilities and RT means rounded to 4 decimals'},indent=2)+'\n')
    (out/'caption.md').write_text('''Tentative Figure 6. Saved pulse-only fitted predictions from the best held-out candidate (normalized input, urgency-gating region, no persistent drift variability; solid) and lowest-BIC candidate (linear-input leaky accumulator with drift variability; dashed). Columns distinguish early, middle and late pulse schedules. Blue downward triangles and orange upward triangles show physical left- and right-pulse observations. Points and SEM are equal-mouse means and between-mouse SEM over available mice, computed from saved per-mouse condition/coherence summaries. Models are averaged over exactly the same available mouse/condition/coherence cells. (A) Right-choice proportions, with separate descriptive author logit_4 psychometric fits to data (dotted) and each model's group probabilities (solid/dashed). Display fits use unweighted least squares across coherence, actual observed endpoints only, and do not re-estimate decision-model parameters. (B) Arithmetic mean RT across both response choices; shaded regions and error bars show observed between-mouse SEM. Model RT lines connect predictions at actual tested coherences, not chronometric-function fits. All models use saved full-pulse-fit parameters and previously simulated outputs; these curves are descriptive rather than held-out validation. Controls, including control observations previously borrowed by the browser to anchor psychometric endpoints, are omitted. Population is the browser's responded-trial symmetric scheduled-pulse selection, including all onset stages; it is not the narrower post-pulse-end selection of Figure 4. Simulations used each mouse's responded input schedules, 30 repetitions and seed 0, as documented in build_fit_browser.py and pulse_joint_signatures.py. Original browser trial-level SEs and model Monte Carlo SEs are not treated as group uncertainty. Source summaries have four-decimal precision. Independent criteria winners are shown for visual assessment, not to establish model adequacy.\n''')
    (out/'manifest.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'models':MODELS,'population_counts':counts.to_dict('records'),'scope':'Tentative Figure6; saved full-pulse-fit outputs; descriptive psychometric display fits only.'},indent=2)+'\n')
    print(counts.to_string(index=False))

if __name__=='__main__':main()
