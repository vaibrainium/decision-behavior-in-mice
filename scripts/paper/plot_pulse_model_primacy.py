"""Plot observed and fixed-model Figure4C readouts, including matched-cohort sensitivity."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.paper.build_paper_2026_11_15 import plt,STYLE,BLUE,ORANGE,GREEN
from scripts.paper.pulse_time_ordinal import prepare_ordinal
from scripts.paper.pulse_time_continuous import residual_jac
from scripts.ddm.pulse_dynamics_bridge import INPUT,TIMING

BASE=Path('dissemination/paper_accumulation/draft_2026-11-15')
ORDINAL=BASE/'pulse_time_ordinal_2026-11-18'
LABELS={'pulse_norm_ugm_no_sv':'Normalized UGM, no drift variability','pulse_linear_leak':'Linear leak (BIC winner)','pulse_linear_primary':'Linear integrator, drift variability','pulse_linear_urgency':'Linear urgency, drift variability'}


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--source',type=Path,required=True);a=p.parse_args();out=a.source
    observed=pd.read_csv(ORDINAL/'influence_curves.csv');coeffs=pd.read_csv(ORDINAL/'coefficients.csv')
    records=[];ranking=[]
    for suffix,case in [('', 'all_available_10'),('_matched6','matched_6')]:
        table=pd.read_csv(out/f'model_readout{suffix}_by_seed.csv');assert len(table)==44 and table.family.nunique()==22
        assert (table.n_success==10).all() and table.bound_parameters.isna().all() and (table.min_observed_psychometric_slope>0).all()
        rank=pd.read_csv(out/f'model_primacy_ranking{suffix}.csv');ranking.append(rank)
        for row in table.itertuples():
            for stage in [1,2,3]:records.append({'comparison':case,'family':row.family,'seed':row.seed,'stage':stage,'influence':row.w_middle+row.slope_per_stage*(stage-2)})
    points=pd.DataFrame(records);points.to_csv(out/'model_stage_readouts.csv',index=False)
    with plt.rc_context(STYLE):
        fig,axes=plt.subplots(1,2,figsize=(190/25.4,100/25.4));fig.subplots_adjust(left=.09,right=.98,bottom=.29,top=.79,wspace=.35)
        for ax,case,title in zip(axes,['all_available_10','matched_6'],['Figure 4C population: 10 mice, late in 6','Sensitivity: same 6 mice at all stages']):
            z=observed[(observed.comparison==case)&(observed.objective=='wls')]
            ax.fill_between(z.stage_index,z.ci_lo,z.ci_hi,color='black',alpha=.10,linewidth=0)
            ax.plot(z.stage_index,z.influence,c='black',lw=1.4,label='Observed regression; 95% cluster interval')
            q=z[z.stage_index.isin([1,2,3])];ax.plot(q.stage_index,q.influence,'o',c='black',ms=3)
            families=['pulse_norm_ugm_no_sv','pulse_linear_leak']+(['pulse_linear_primary'] if case=='matched_6' else [])
            for family,color,style in zip(families,[BLUE,ORANGE,GREEN],['--',':','-.']):
                q=points[(points.comparison==case)&(points.family==family)].groupby('stage').influence.agg(['mean','min','max'])
                ax.plot(q.index,q['mean'],style,color=color,lw=1.3,label=LABELS[family])
                ax.fill_between(q.index,q['min'],q['max'],color=color,alpha=.15,linewidth=0)
            ax.axhline(0,color='.7',lw=.5)
            ax.set(xticks=[1,2,3],xticklabels=['Early','Middle','Late'],xlabel='Pulse onset stage (coded 1, 2, 3)',title=title,ylim=(-10,23))
        axes[0].set_ylabel('Directional pulse influence w (% coherence)')
        fig.text(.045,.96,'Which pulse-only models reproduce onset-dependent influence?',fontsize=9.5,va='top')
        h,l=axes[1].get_legend_handles_labels();fig.legend(h,l,loc='lower center',bbox_to_anchor=(.54,.035),ncol=2,fontsize=6)
        fig.text(.09,.015,'Model bands: range across two simulation seeds, not biological confidence intervals.',fontsize=6,color='.3')
        for ext in ['png','pdf','svg']:fig.savefig(out/f'primacy_comparison.{ext}',dpi=300)
        plt.close(fig)
    # Repetition scaling changes residual magnitude, not the optimum of the readout objective.
    pilot=json.loads((out/'readout_pulse_norm_ugm_no_sv_seed0.json').read_text())
    paths=sorted((out/'simulation_cells').glob('pulse_norm_ugm_no_sv_*_seed0_r30.csv'));cells=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
    data=prepare_ordinal(cells,sorted(cells.mouse.unique()));theta=np.array(pilot['theta']);r,J=residual_jac(theta,data,'wls')
    raw=cells.copy();raw['n']=raw.n_raw;raw['k']=raw.k_raw;rawdata=prepare_ordinal(raw,data.mice);rr,JJ=residual_jac(theta,rawdata,'wls')
    np.testing.assert_allclose(rr,r*np.sqrt(30),atol=1e-10);np.testing.assert_allclose(JJ,J*np.sqrt(30),atol=1e-9)
    sourcepaths=[Path(__file__),Path('scripts/paper/pulse_model_primacy.py'),INPUT,TIMING,ORDINAL/'coefficients.csv',ORDINAL/'influence_curves.csv']
    metadata={'all_candidates':22,'independent_simulation_seeds':2,'repetitions_per_input_per_seed':30,'simulation_mouse_jobs':len(list((out/'simulation_cells').glob('*.json'))),'readout_fits':88,'starts_per_fit':10,'all_starts_successful':True,'all_readout_parameters_interior':True,'all_observed_coherence_slopes_positive':True,'replicate_scaling_invariance_checked':True,'best_full_curve_all_available':ranking[0].iloc[0].family,'best_full_curve_matched6':ranking[1].iloc[0].family,'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sourcepaths},'scope':'Fixed full-pulse-fit parameters; exploratory conditional readout ranking. Data and model response eligibility matched; model parameters not refitted. No biological significance tests on model simulations.'}
    (out/'verification.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (out/'caption.md').write_text('''Existing full-pulse-fit parameters from all22 candidates were simulated on the22,437 reconstructable symmetric control/pulse input schedules, including late pulses and matched virtual controls. Each mouse received30 simulation repetitions at each of two independently seeded runs. Control responses are model predictions, not training observations used to refit parameters. The original observed post-offset, minimum0.1s after onset and5s response rules reproduce exactly21,725 Figure4C observations and their regression cells; identical outcome rules were applied to simulated RTs. The same21-parameter ordinal psychometric WLS regression was fitted to pooled simulated choices, using eligible simulation counts divided by30 to preserve expected trial weights. No decision-model parameters were re-estimated. Black lines/bands show the saved observed regression and pointwise95% mouse-cluster intervals. Colored lines show mean model-generated ordinal readouts across seeds; colored bands show only seed range, not parameter or animal-population uncertainty. All22 models were ranked descriptively by three-stage curve RMSE against the corresponding observed readout, with slope error reported separately. Left retains all10 mouse baselines with late pulses supported by6; right refits the same descriptive readout within those6 mice, using17 parameters and the saved matched6 observed reference. The matched-cohort observed slope is inconclusive, and model ranking changes. These are conditional in-sample model checks, not new out-of-sample scores or calibrated model rejection tests.\n''')
    print(json.dumps({k:v for k,v in metadata.items() if k!='source_sha256'},indent=2))

if __name__=='__main__':main()
