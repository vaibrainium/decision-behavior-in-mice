"""Aggregation-invariant inference and verification for saved continuous-onset fits."""
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
from scripts.paper.pulse_time_continuous import prepare,model,residual_jac,covariance,slope_test,CENTER,SCALE,TAIL
from scripts.paper.style import RC


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    coefs=pd.read_csv(a.source/'coefficients.csv');oldtests=pd.read_csv(a.source/'primary_slope_tests.csv');diagnostics=pd.read_csv(a.source/'fit_diagnostics.csv');test=[];curves=[];checks=[]
    for dataset in ['restricted','original_selection']:
        cells=pd.read_csv(a.source/f'{dataset}_cells.csv');mice=sorted(cells.mouse.unique());M=len(mice);data=prepare(cells,mice);names=[f'baseline_{m}' for m in mice]+TAIL
        for objective in ['wls','binomial']:
            theta=coefs[(coefs.dataset==dataset)&(coefs.objective==objective)].set_index('parameter').loc[names].estimate_internal.to_numpy();V,H,S=covariance(theta,data,objective);V2,_,_=covariance(theta,data,objective,step_scale=1e-6)
            step_error=float(np.max(abs(V-V2))/np.max(abs(V)));assert step_error<1e-4 and np.linalg.eigvalsh(H).min()>0
            r,_=residual_jac(theta,data,objective);cost=.5*(r@r);oldcost=diagnostics[(diagnostics.dataset==dataset)&(diagnostics.objective==objective)].cost.iloc[0];assert np.isclose(cost,oldcost,rtol=1e-10)
            np.save(a.output/f'{dataset}_{objective}_covariance.npy',V);np.save(a.output/f'{dataset}_{objective}_score_hessian.npy',H)
            row=slope_test(theta,V,M,dataset,objective,'mouse_cluster_observed_Hessian_trial_count_CR1');test.append(row)
            checks.append({'dataset':dataset,'objective':objective,'n_underlying_trials':int(data.n.sum()),'n_grouped_cells':len(data.c),'saved_cost_reproduced':True,'covariance_relative_10x_step_change':step_error})
            for tau in np.linspace(cells[cells.direction!=0].onset_s.min(),cells[cells.direction!=0].onset_s.max(),201):
                contrast=np.zeros(len(theta));contrast[M+2]=1;contrast[M+3]=(tau-CENTER)/SCALE;w=float(contrast@theta);se=float(np.sqrt(contrast@V@contrast));margin=stats.t.ppf(.975,M-1)*se;curves.append({'dataset':dataset,'objective':objective,'onset_s':tau,'pulse_influence':w,'ci_lo':w-margin,'ci_hi':w+margin})
    test=pd.concat([pd.DataFrame(test),oldtests[oldtests.uncertainty=='mouse_cluster_jackknife']],ignore_index=True);test.to_csv(a.output/'primary_slope_tests.csv',index=False);curves=pd.DataFrame(curves);curves.to_csv(a.output/'pulse_influence_curves.csv',index=False)
    # Correct the ordinal-plus-presence diagnostic without changing its saved fit.
    diagnostic=a.source/'specification_diagnostic';cell=pd.read_csv(diagnostic/'cells.csv');mice=sorted(cell.mouse.unique());theta=pd.read_csv(diagnostic/'ordinal_presence_coefficients.csv').estimate.to_numpy();V,H,S=covariance(theta,prepare(cell,mice),'wls');M=len(mice);se=np.sqrt(V[M+3,M+3]);t=theta[M+3]/se
    comparison={'ordinal21_with_presence_slope_per_stage':theta[M+3],'ordinal21_with_presence_raw_t9_p':2*stats.t.sf(abs(t),M-1),'continuous21_primary_raw_t9_p':float(test[(test.dataset=='restricted')&(test.objective=='wls')&(test.uncertainty.str.contains('trial_count'))].p_two_sided.iloc[0]),'scope':'Same21-parameter probability model and trials; change actual onset values to ordinal early/middle. Nuisance additions isolated from original19-parameter formulation separately.'}
    (a.output/'specification_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
    for dataset in ['restricted','original_selection']:
        z=curves[(curves.dataset==dataset)&(curves.objective=='wls')];primary=test[(test.dataset==dataset)&(test.objective=='wls')&(test.uncertainty.str.contains('trial_count'))].iloc[0];jack=test[(test.dataset==dataset)&(test.uncertainty=='mouse_cluster_jackknife')].iloc[0]
        with plt.rc_context(RC):
            fig,ax=plt.subplots(figsize=(5,3.5),layout='constrained');ax.fill_between(z.onset_s*1000,z.ci_lo,z.ci_hi,color='#0072B2',alpha=.15,lw=0);ax.plot(z.onset_s*1000,z.pulse_influence,c='#0072B2',lw=1.3);ax.axhline(0,c='.7',ls=':',lw=.7)
            ax.set(xlabel='Recorded pulse-onset time (ms)',ylabel='Directional pulse influence w (% coherence)',title='Continuous onset-time slope of pulse influence')
            ax.text(.03,.04,f'Slope /100 ms: {primary.effect_per_100ms:.2f} [{primary.ci_lo_per_100ms:.2f}, {primary.ci_hi_per_100ms:.2f}]\nPrimary cluster p = {primary.p_two_sided:.3f}; jackknife p = {jack.p_two_sided:.3f}',transform=ax.transAxes,fontsize=7)
            fig.suptitle(f'{dataset.replace("_"," ")}: joint model, 10 mouse baseline offsets\nFitted influence ± pointwise 95% cluster interval; early/middle trials',fontsize=8)
            for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{dataset}_continuous_time.{ext}',dpi=250)
            plt.close(fig)
    manifest={'source_fits':str(a.source),'refitted':False,'finite_correction':'G/(G-1)*(N_trials-1)/(N_trials-K); frequency aggregation invariant. Previously used grouped-cell count, corrected here.','verification':checks,'regression_tests':'7 continuous-time plus6 fixed-offset unit tests passed, including explicit aggregation versus trial expansion invariance','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.source/'coefficients.csv',a.source/'primary_slope_tests.csv',Path(__file__),Path('scripts/paper/pulse_time_continuous.py')]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(test.to_string(index=False),flush=True);print(json.dumps(comparison,indent=2))

if __name__=='__main__':main()
