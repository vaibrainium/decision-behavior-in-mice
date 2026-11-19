"""Ordinal1/2/3 slope of directional pulse influence, preserving current joint model."""
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.pulse_time_continuous import fit,model,covariance,residual_jac,TAIL
from scripts.paper.style import RC


def prepare_ordinal(cells,mice,center=2.):
    mi=pd.Categorical(cells.mouse,categories=mice).codes
    if np.any(mi<0):raise ValueError('Unknown mouse label')
    d=cells.direction.to_numpy(dtype=float);P=(d!=0).astype(float);x=np.where(P,cells.stage_index.to_numpy()-center,0.)
    return SimpleNamespace(cells=cells,mice=mice,mi=mi,XA=np.column_stack([np.eye(len(mice))[mi],P,P*x,d,d*x]),XB=np.column_stack([np.ones(len(d)),P,P*x,d,d*x]),c=cells.coherence_pct.to_numpy(),n=cells.n.to_numpy(),k=cells.k.to_numpy(),y=cells.y.to_numpy(),M=len(mice))


def slope_test(theta,V,M,comparison,objective,method):
    effect=theta[M+3];se=np.sqrt(V[M+3,M+3]);margin=stats.t.ppf(.975,M-1)*se;t=effect/se
    return {'comparison':comparison,'objective':objective,'uncertainty':method,'n_mice':M,'slope_per_stage':effect,'se':se,'ci_lo':effect-margin,'ci_hi':effect+margin,'t':t,'df':M-1,'p_two_sided':2*stats.t.sf(abs(t),M-1)}


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--eligible',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    e=pd.read_csv(a.eligible);e['stage_index']=e.onset_stratum.map({'early':1,'middle':2,'late':3}).where(e.direction!=0,0).astype(int)
    previous=pd.read_csv(a.previous/'coefficients.csv');old=previous[(previous.dataset=='restricted')&(previous.objective=='wls')].set_index('parameter').estimate_internal
    late_mice=sorted(e[(e.direction!=0)&(e.stage_index==3)].mouse.unique());assert len(late_mice)==6
    cases=[('all_available_10',e,[1,2,3]),('matched_6',e[e.mouse.isin(late_mice)],[1,2,3]),('early_middle_10',e[e.onset_stratum.isin(['early','middle'])],[1,2])]
    tests=[];coefs=[];diagnostics=[];jack=[];curves=[];attempts=[];checks=[]
    for name,trials,stages in cases:
        cells=trials.groupby(['mouse','direction','stage_index','coherence_pct'],as_index=False).right.agg(k='sum',n='size');cells['y']=cells.k/cells.n;mice=sorted(cells.mouse.unique());M=len(mice);data=prepare_ordinal(cells,mice);cells.to_csv(a.output/f'{name}_cells.csv',index=False)
        # Warm start from continuous model; both time coding and nuisance terms are explicit.
        shift=(.23338-.15)/.2;factor=(.23338-.05001)/.2
        seed=np.r_[[old[f'baseline_{m}'] for m in mice],[old.common_pulse_offset+old.common_time_offset*shift,old.common_time_offset*factor,old.direction_offset+old.direction_time_offset*shift,old.direction_time_offset*factor,old.beta_control,old.common_pulse_slope+old.common_time_slope*shift,old.common_time_slope*factor,old.direction_slope+old.direction_time_slope*shift,old.direction_time_slope*factor,old.lapse,old.gamma]]
        for objective in ['wls','binomial']:
            r=fit(data,objective,seed);theta=r.theta;V,H,S=covariance(theta,data,objective);np.save(a.output/f'{name}_{objective}_covariance.npy',V);np.save(a.output/f'{name}_{objective}_score_hessian.npy',H)
            names=[f'baseline_{m}' for m in mice]+TAIL
            for j,param in enumerate(names):coefs.append({'comparison':name,'objective':objective,'parameter':param,'estimate':theta[j],'cluster_se':np.sqrt(V[j,j])})
            for j,row in enumerate(r.attempts):attempts.append({'comparison':name,'objective':objective,'start':j,**row})
            tests.append(slope_test(theta,V,M,name,objective,'trial_count_mouse_cluster_CR1'))
            pred,J=model(theta,data);res,_=residual_jac(theta,data,objective);assert np.isclose(.5*(res@res),r.cost,rtol=1e-10)
            cells.assign(predicted=pred).to_csv(a.output/f'{name}_{objective}_predictions.csv',index=False)
            V2,_,_=covariance(theta,data,objective,step_scale=1e-6);step=float(np.max(abs(V-V2))/np.max(abs(V)));assert step<1e-4
            checks.append({'comparison':name,'objective':objective,'cost_reproduced':True,'covariance_10x_step_relative_change':step})
            bound=np.isclose(theta,r.bounds[0],atol=1e-6)|np.isclose(theta,r.bounds[1],atol=1e-6);B=data.XB@theta[M+4:M+9]
            diagnostics.append({'comparison':name,'objective':objective,'n_trials':len(trials),'n_cells':len(cells),'n_mice':M,'n_parameters':len(theta),'cost':r.cost,'n_success':sum(row['success'] for row in r.attempts),'n_starts':len(r.attempts),'bound_parameters':','.join(np.array(names)[bound]),'all_observed_slopes_positive':bool((B>0).all()),'min_hessian_eigenvalue':float(np.linalg.eigvalsh(H).min())})
            if objective=='wls':
                samples=[]
                for omitted in mice:
                    ms=[m for m in mice if m!=omitted];z=cells[cells.mouse!=omitted];prepared=prepare_ordinal(z,ms);warm=np.r_[[theta[mice.index(m)] for m in ms],theta[M:]];jr=fit(prepared,objective,warm,quick=True);samples.append(jr.theta[len(ms):]);jack.append({'comparison':name,'omitted':omitted,'slope_per_stage':jr.theta[len(ms)+3]})
                samples=np.array(samples);center=samples-samples.mean(axis=0);C=(M-1)/M*(center.T@center);full=np.zeros_like(V);full[M:,M:]=C;tests.append(slope_test(theta,full,M,name,objective,'cluster_jackknife'));seed=theta
            for stage in np.linspace(min(stages),max(stages),101):
                c=np.zeros(len(theta));c[M+2]=1;c[M+3]=stage-2;value=float(c@theta);se=np.sqrt(c@V@c);margin=stats.t.ppf(.975,M-1)*se;curves.append({'comparison':name,'objective':objective,'stage_index':stage,'influence':value,'ci_lo':value-margin,'ci_hi':value+margin})
            print(name,objective,'slope/stage',theta[M+3],'complete',flush=True)
    tests=pd.DataFrame(tests);curves=pd.DataFrame(curves);tests.to_csv(a.output/'slope_tests.csv',index=False);pd.DataFrame(coefs).to_csv(a.output/'coefficients.csv',index=False);pd.DataFrame(diagnostics).to_csv(a.output/'fit_diagnostics.csv',index=False);pd.DataFrame(jack).to_csv(a.output/'leave_one_mouse_slopes.csv',index=False);curves.to_csv(a.output/'influence_curves.csv',index=False);(a.output/'optimizer_starts.json').write_text(json.dumps(attempts,indent=2)+'\n')
    for case in ['all_available_10','matched_6','early_middle_10']:
        z=curves[(curves.comparison==case)&(curves.objective=='wls')];primary=tests[(tests.comparison==case)&(tests.objective=='wls')&(tests.uncertainty=='trial_count_mouse_cluster_CR1')].iloc[0];j=tests[(tests.comparison==case)&(tests.uncertainty=='cluster_jackknife')].iloc[0];stages=[1,2] if case=='early_middle_10' else [1,2,3]
        with plt.rc_context(RC):
            fig,ax=plt.subplots(figsize=(5,3.4),layout='constrained');ax.fill_between(z.stage_index,z.ci_lo,z.ci_hi,color='#0072B2',alpha=.15,lw=0);ax.plot(z.stage_index,z.influence,c='#0072B2',lw=1.3)
            q=z[z.stage_index.isin(stages)];ax.plot(q.stage_index,q.influence,'o',c='#0072B2',ms=3);ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=stages,xticklabels=[{1:'1: Early',2:'2: Middle',3:'3: Late'}[s] for s in stages],xlabel='Pulse time coded as stage index',ylabel='Directional pulse influence w (% coherence)',title='Ordinal time slope of pulse influence')
            ax.text(.03,.04,f'Slope/stage: {primary.slope_per_stage:.2f} [{primary.ci_lo:.2f}, {primary.ci_hi:.2f}]\nCluster p = {primary.p_two_sided:.3f}; jackknife p = {j.p_two_sided:.3f}',transform=ax.transAxes,fontsize=7)
            support={'all_available_10':'10 mice; late pulses available in 6','matched_6':'Same 6 mice at all three times','early_middle_10':'Same 10 mice at early/middle'}[case];fig.suptitle('Same joint model; '+support+'\nFitted line ± pointwise 95% mouse-cluster interval',fontsize=8)
            for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{case}.{ext}',dpi=250)
            plt.close(fig)
    manifest={'time':'Pulse stages1/2/3, x=stage-2 for pulses; controlsP=d=x=0. Same probability equation and presence nuisance terms as continuous-time model.','units':'Directional influence slope per stage step, not per second or per100ms','comparisons':'All available10 mouse baselines with late supported6; matched6 all3 stages; same10 early/middle-only. No permanent exclusions beyond defining cohort/time support.','primary_test':'One exploratory two-sided slope=0 per stated comparison; sensitivity comparisons not independent confirmatory discoveries','uncertainty':'Full score-Hessian frequency-corrected mouse-cluster sandwich, t(G-1); cluster jackknife sensitivity','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.eligible,a.previous/'coefficients.csv',Path(__file__)]},'checks':checks}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(tests.to_string(index=False),flush=True)

if __name__=='__main__':main()
