"""Unpack the saved ordinal pulse-influence model into left/right alpha curves."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.pulse_time_continuous import TAIL
from scripts.paper.style import RC,LEFT_COLOR,RIGHT_COLOR


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    coefficients=pd.read_csv(a.source/'coefficients.csv');prior_tests=pd.read_csv(a.source/'slope_tests.csv');rows=[];interaction=[];slopes=[]
    for case in ['all_available_10','matched_6','early_middle_10']:
        for objective in ['wls','binomial']:
            z=coefficients[(coefficients.comparison==case)&(coefficients.objective==objective)].set_index('parameter');baseline=sorted(z.index[z.index.str.startswith('baseline_')]);M=len(baseline);names=baseline+TAIL;theta=z.loc[names].estimate.to_numpy();V=np.load(a.source/f'{case}_{objective}_covariance.npy');df=M-1;crit=stats.t.ppf(.975,df)
            c=np.zeros(len(theta));c[M+3]=2;difference=float(c@theta);se=float(np.sqrt(c@V@c));t=difference/se;pvalue=2*stats.t.sf(abs(t),df)
            prior=prior_tests[(prior_tests.comparison==case)&(prior_tests.objective==objective)&(prior_tests.uncertainty=='trial_count_mouse_cluster_CR1')].iloc[0]
            assert np.isclose(difference,2*prior.slope_per_stage) and np.isclose(pvalue,prior.p_two_sided)
            interaction.append({'comparison':case,'objective':objective,'right_minus_left_slope_difference':difference,'se':se,'ci_lo':difference-crit*se,'ci_hi':difference+crit*se,'df':df,'p_two_sided':pvalue,'same_as_existing_time_influence_test':True})
            for direction in [-1,1]:
                slope=np.zeros(len(theta));slope[M+1]=1;slope[M+3]=direction;value=float(slope@theta);slope_se=float(np.sqrt(slope@V@slope));slopes.append({'comparison':case,'objective':objective,'direction':direction,'alpha_slope_per_stage':value,'se':slope_se,'ci_lo':value-crit*slope_se,'ci_hi':value+crit*slope_se})
                for stage in np.linspace(1,2 if case=='early_middle_10' else 3,101):
                    x=stage-2;c=np.zeros(len(theta));c[:M]=1/M;c[M:M+4]=[1,x,direction,direction*x];estimate=float(c@theta);err=float(np.sqrt(c@V@c));beta=np.zeros(len(theta));beta[M+5:M+9]=[1,x,direction,direction*x]
                    rows.append({'comparison':case,'objective':objective,'stage_index':stage,'direction':direction,'alpha_full':estimate,'alpha_ci_lo':estimate-crit*err,'alpha_ci_hi':estimate+crit*err,'beta_change':float(beta@theta)})
            if objective!='wls':continue
            curves=pd.DataFrame([row for row in rows if row['comparison']==case and row['objective']==objective]);jack=prior_tests[(prior_tests.comparison==case)&(prior_tests.uncertainty=='cluster_jackknife')].iloc[0]
            with plt.rc_context(RC):
                fig,ax=plt.subplots(figsize=(5.1,3.65),layout='constrained')
                for d,color,text in [(-1,LEFT_COLOR,'Leftward pulse'),(1,RIGHT_COLOR,'Rightward pulse')]:
                    q=curves[curves.direction==d].sort_values('stage_index');ax.fill_between(q.stage_index,q.alpha_ci_lo,q.alpha_ci_hi,color=color,alpha=.12,lw=0);ax.plot(q.stage_index,q.alpha_full,c=color,lw=1.3,label=text)
                    points=q[q.stage_index.isin([1,2,3])];ax.plot(points.stage_index,points.alpha_full,'o',c=color,ms=3.5)
                stages=[1,2] if case=='early_middle_10' else [1,2,3];ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=stages,xticklabels=[{1:'1: Early',2:'2: Middle',3:'3: Late'}[s] for s in stages],xlabel='Pulse time coded as stage index',ylabel='α: full additive coherence offset (% coherence)',title='Direction × pulse-time interaction')
                ax.legend(loc='upper right');ax.text(.03,.04,f'Right − left slope difference: {difference:.2f}/stage\nInteraction p = {pvalue:.3f}; jackknife p = {jack.p_two_sided:.3f}',transform=ax.transAxes,fontsize=7)
                support={'all_available_10':'10 mouse baseline offsets; late support in 6','matched_6':'Same 6 mice across all three times','early_middle_10':'Same 10 mice across early/middle'}[case];fig.suptitle('Selected joint model: '+support+'\nFitted full α offsets ± pointwise 95% mouse-cluster intervals',fontsize=8)
                for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{case}_direction_interaction.{ext}',dpi=250)
                plt.close(fig)
    pd.DataFrame(rows).to_csv(a.output/'direction_curves.csv',index=False);pd.DataFrame(interaction).to_csv(a.output/'interaction_test.csv',index=False);pd.DataFrame(slopes).to_csv(a.output/'direction_slopes.csv',index=False)
    (a.output/'manifest.json').write_text(json.dumps({'source_model':str(a.source),'refitted':False,'definition':'Full additive alpha follows notebook coh+A; population display uses mean categorical mouse baseline offset.','interaction':'Right slope minus left slope =2*direction_time_offset; same t and p as existing primary directional-influence slope test.','uncertainty':'Full score-Hessian trial-count CR1 mouse-cluster covariance; pointwise t(G-1)95% intervals. Curves are model estimates, not stage-wise raw observations.','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.source/'coefficients.csv',a.source/'slope_tests.csv',Path(__file__)]}},indent=2)+'\n');print(pd.DataFrame(interaction).to_string(index=False),flush=True);print(pd.DataFrame(slopes).to_string(index=False),flush=True)

if __name__=='__main__':main()
