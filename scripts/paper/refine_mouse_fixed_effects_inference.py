"""Full nonlinear score-Hessian cluster covariance for saved mouse-fixed-offset fits."""
import argparse
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.pulse_time_mouse_fixed_effects import model,SHARED,infer
from scripts.paper.style import RC,LEFT_COLOR,RIGHT_COLOR


def observed_cluster_cov(theta,cells,mice,objective,step_scale=1e-5):
    def score(q):
        p,J=model(q,cells,mice);scale=cells.n.to_numpy()*(p-cells.y.to_numpy())
        if objective=='binomial':scale/=p*(1-p)
        return scale[:,None]*J
    columns=[]
    for j in range(len(theta)):
        step=step_scale*max(1,abs(theta[j]));up=theta.copy();down=theta.copy();up[j]+=step;down[j]-=step;columns.append((score(up).sum(axis=0)-score(down).sum(axis=0))/(2*step))
    H=np.column_stack(columns);asym=np.max(np.abs(H-H.T))/np.max(np.abs(H));H=(H+H.T)/2
    S=pd.DataFrame(score(theta)).assign(mouse=cells.mouse.to_numpy()).groupby('mouse').sum().reindex(mice).to_numpy();G=len(mice);K=len(theta);N=int(cells.n.sum())
    influence=np.linalg.solve(H,S.T);cov=G/(G-1)*(N-1)/(N-K)*(influence@influence.T)
    return cov,H,asym


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    coefficients=pd.read_csv(a.source/'coefficients.csv');oldtests=pd.read_csv(a.source/'regression_tests.csv');tests=[];display=[];checks=[];newcoefs=[]
    for dataset in ['restricted','original_selection']:
        cells=pd.read_csv(a.source/f'{dataset}_cells.csv');mice=sorted(cells.mouse.unique());M=len(mice);names=[f'alpha_baseline_{m}' for m in mice]+SHARED
        for objective in ['wls','binomial']:
            frame=coefficients[(coefficients.dataset==dataset)&(coefficients.objective==objective)].set_index('parameter').loc[names];theta=frame.estimate.to_numpy()
            cov,H,asym=observed_cluster_cov(theta,cells,mice,objective);second,_,_=observed_cluster_cov(theta,cells,mice,objective,1e-6)
            relative=np.max(abs(cov-second))/np.max(abs(cov));assert relative<1e-4 and np.linalg.eigvalsh(H).min()>0
            np.save(a.output/f'{dataset}_{objective}_cluster_cov.npy',cov);np.save(a.output/f'{dataset}_{objective}_score_hessian.npy',H)
            tests.extend(infer(theta,cov,M,M,'observed_score_Hessian_CR1',dataset,objective))
            checks.append({'dataset':dataset,'objective':objective,'score_hessian_asymmetry_relative':asym,'min_hessian_eigenvalue':float(np.linalg.eigvalsh(H).min()),'covariance_relative_step_sensitivity':relative})
            for j,name in enumerate(names):
                se=np.sqrt(cov[j,j]);newcoefs.append({'dataset':dataset,'objective':objective,'parameter':name,'estimate':theta[j],'mouse_cluster_se':se,'df':M-1,'raw_t_p':2*stats.t.sf(abs(theta[j]/se),M-1)})
            for stage in [1,2]:
                for direction in [-1,1]:
                    ca=np.r_[np.repeat(1/M,M),direction,stage,direction*stage,0,0,0,0,0,0];cb=np.r_[np.zeros(M+3),0,direction,stage,direction*stage,0,0]
                    for parameter,c in [('alpha_full',ca),('beta_change',cb)]:
                        effect=float(c@theta);se=float(np.sqrt(c@cov@c));margin=stats.t.ppf(.975,M-1)*se;display.append({'dataset':dataset,'objective':objective,'parameter':parameter,'direction':direction,'stage':stage,'estimate':effect,'se':se,'ci_lo':effect-margin,'ci_hi':effect+margin})
    tests=pd.concat([pd.DataFrame(tests),oldtests[oldtests.uncertainty=='cluster_jackknife']],ignore_index=True);tests.to_csv(a.output/'regression_tests.csv',index=False);pd.DataFrame(newcoefs).to_csv(a.output/'coefficients.csv',index=False);display=pd.DataFrame(display);display.to_csv(a.output/'display_values.csv',index=False)
    for dataset in ['restricted','original_selection']:
        with plt.rc_context(RC):
            fig,axes=plt.subplots(1,2,figsize=(7.5,3.3),layout='constrained')
            for ax,param,label in zip(axes,['alpha_full','beta_change'],['α: full additive coherence offset (% coherence)','Δβ: slope change from control (per % coherence)']):
                for direction,color,text in [(-1,LEFT_COLOR,'Leftward pulse'),(1,RIGHT_COLOR,'Rightward pulse')]:
                    z=display[(display.dataset==dataset)&(display.objective=='wls')&(display.parameter==param)&(display.direction==direction)].sort_values('stage');ax.plot(z.stage,z.estimate,'o-',c=color,label=text);ax.vlines(z.stage,z.ci_lo,z.ci_hi,color=color);ax.plot(z.stage,z.ci_lo,'_',c=color);ax.plot(z.stage,z.ci_hi,'_',c=color)
                ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=[1,2],xticklabels=['Early','Middle'],xlabel='Pulse stage',ylabel=label)
            axes[0].legend();fig.suptitle(f'Joint model with categorical mouse baseline offsets: {dataset.replace("_"," ")}\nShared pulse coefficients; full mouse-cluster 95% intervals, t(9)',fontsize=8)
            for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{dataset}_mouse_fixed_effects.{ext}',dpi=250)
            plt.close(fig)
    manifest={'source_fits':str(a.source),'refitted':False,'final_inference':'Full observed nonlinear score-Hessian bread; mouse-cluster CR1 sandwich; t9/F2,9 approximations','gauss_newton_approximation':'Retained in parent, not final reported covariance','checks':checks,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.source/'coefficients.csv',a.source/'restricted_cells.csv',a.source/'original_selection_cells.csv',a.source/'regression_tests.csv',Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(tests[(tests.dataset=='restricted')&(tests.objective=='wls')].to_string(index=False),flush=True)

if __name__=='__main__':main()
