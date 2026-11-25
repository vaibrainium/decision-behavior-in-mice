"""Apply the Figure4C ordinal readout to fixed model simulations.

The historical default remains the pulse-only candidate set.  Explicit
``--families`` may also name joint all-trial fits so the same Figure4C readout
can be compared across fit scopes without refitting either decision model.
"""
import argparse,gc,hashlib,json,pickle,subprocess,time,zlib
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.paper.pulse_time_ordinal import prepare_ordinal
from scripts.paper.pulse_time_continuous import fit,model,TAIL

BASE=Path('dissemination/paper_accumulation/draft_2026-11-15')
ORDINAL=BASE/'pulse_time_ordinal_2026-11-18'
ELIGIBLE=BASE/'pulse_psychometric_timing_2026-11-18/eligible_trials.csv'
SCORE=Path('dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv')
KEYS=['mouse','direction','stage_index','coherence_pct']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def get_inputs():
    from scripts.ddm.pulse_dynamics_bridge import inputs
    return inputs()

def prepare(out):
    from scripts.paper.pulse_psychometric_timing import SOURCE
    x=get_inputs();table=pd.read_csv(SOURCE,low_memory=False).set_index('trial_id').reindex(x['agg_code'].astype(str)).reset_index()
    assert table.trial_id.notna().all() and table.trial_id.is_unique
    table['row']=np.arange(len(table))
    t=table[table.in_ddm_input.astype(bool)&table.signs_scheduled_symmetric.astype(bool)&table.pulse_category.isin(['control','positive','negative'])].copy()
    pulse=t.pulse_category.ne('control');duration=t.recorded_duration_s.where(pulse)
    t['onset_s']=t.recorded_onset_s.where(pulse,t.control_onset_s)
    t['offset_s']=t.onset_s+duration.where(pulse,t.rig.map(duration.groupby(t.rig).median()))
    t['direction']=np.where(pulse,t.pulse_sign,0).astype(int)
    t['stage_index']=t.onset_stratum.map({'early':1,'middle':2,'late':3}).where(pulse,0).astype(int)
    assert t[['onset_s','offset_s']].notna().all().all()
    observed=t[(t.rt_s>=t.offset_s)&(t.rt_s-t.onset_s>=.1)&(t.rt_s<=5)].copy();observed['right']=observed.response_side.eq('R').astype(int)
    ref=pd.read_csv(ELIGIBLE);assert set(observed.trial_id)==set(ref.trial_id) and len(observed)==21725
    cells=observed.groupby(KEYS,as_index=False).right.agg(k='sum',n='size');cells['y']=cells.k/cells.n
    expected=pd.read_csv(ORDINAL/'all_available_10_cells.csv').sort_values(KEYS).reset_index(drop=True)
    pd.testing.assert_frame_equal(cells.sort_values(KEYS).reset_index(drop=True),expected,check_dtype=False,atol=1e-12)
    t[['row','trial_id','mouse','rig','direction','stage_index','coherence_pct','onset_s','offset_s','onset_stratum']].to_csv(out/'preselection.csv',index=False)
    cells.to_csv(out/'observed_cells.csv',index=False)
    (out/'preparation.json').write_text(json.dumps({'observed_eligible_reproduced':True,'n_observed':len(observed),'n_preselection':len(t),'source_sha256':{str(p):sha(p) for p in [SOURCE,ELIGIBLE,ORDINAL/'all_available_10_cells.csv',Path(__file__)]},'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},indent=2)+'\n')
    print('PREPARED',len(t),'schedules; observed21725 selection and cells exactly reproduced',flush=True)

def simulate(out,families,seeds,reps,mice=None):
    from scripts.ddm.fit_mouse_ddm import select
    from scripts.ddm.primacy import make_model,simulate_outcomes
    from scripts.ddm.pulse_joint_signatures import model_path,OPTIONS
    import torch
    x=get_inputs();meta=pd.read_csv(out/'preselection.csv').set_index('row',drop=False)
    cache=out/'simulation_cells';cache.mkdir(exist_ok=True)
    for family in families:
        for seed in seeds:
            for mouse,m in meta.groupby('mouse'):
                if mice and mouse not in mice:
                    continue
                target=cache/f'{family}_{mouse}_seed{seed}_r{reps}.csv'
                if target.exists():continue
                path=model_path(family)(mouse);r=pickle.load(path.open('rb'));opt=OPTIONS.get(family,{})
                expected_split = 'pulse' if family.startswith('pulse_') else 'all'
                if 'split' in r:
                    assert r['split'] == expected_split, (family, r['split'], expected_split)
                else:
                    assert str(path).endswith(f'_{expected_split}.pkl'), (family, path, expected_split)
                assert r.get('front_end')==opt.get('front_end') and bool(r.get('ugm'))==opt.get('ugm',False)
                ddm=make_model(r['variant'],m.rig.iloc[0],fixed_guess_bias=False,responded=True,front_end=opt.get('front_end'),ugm=opt.get('ugm',False))
                rows=m.row.to_numpy();data,stim=select(x,rows);seed_mouse=zlib.crc32(f'{mouse}|primacy|{seed}'.encode());start=time.monotonic()
                raw=simulate_outcomes(ddm,dict(r['parameters']),stim,data['condition'],reps,seed_mouse)
                assert len(raw)==len(rows)*reps
                raw['row']=rows[raw.trial.to_numpy()];u=raw.merge(m.reset_index(drop=True),on='row',validate='many_to_one')
                u=u[(u.choice>=0)&u.rt.notna()&(u.rt<=5)&(u.rt>=u.offset_s)&(u.rt-u.onset_s>=.1)].copy();u['right']=u.choice.eq(1).astype(int)
                c=u.groupby(KEYS,as_index=False).right.agg(k='sum',n='size');c['n_raw']=c.n;c['k_raw']=c.k;c['n']=c.n/reps;c['k']=c.k/reps;c['y']=c.k/c.n
                c.to_csv(target,index=False)
                target.with_suffix('.json').write_text(json.dumps({'family':family,'mouse':mouse,'seed':seed,'mouse_seed':seed_mouse,'reps':reps,'fit_path':str(path),'fit_sha256':sha(path),'n_input':len(rows),'n_raw_outcomes':len(raw),'n_eligible_simulated':len(u),'nonresponse_fraction':float((raw.choice<0).mean()),'seconds':time.monotonic()-start},indent=2)+'\n')
                ddm.simulator.clear_cache();del ddm,stim,raw,u;gc.collect()
                if torch.cuda.is_available():torch.cuda.empty_cache()
            print('SIMULATED',family,'seed',seed,flush=True)

def analyze(out,families,seeds,reps,comparison="all_available_10"):
    previous=pd.read_csv(ORDINAL/'coefficients.csv');old=previous[(previous.comparison==comparison)&(previous.objective=='wls')]
    observed=pd.read_csv(out/'observed_cells.csv')
    mice=sorted(observed.mouse.unique()) if comparison=='all_available_10' else sorted(observed[(observed.direction!=0)&(observed.stage_index==3)].mouse.unique())
    names=[f'baseline_{m}' for m in mice]+TAIL
    seed_theta=old.set_index('parameter').loc[names,'estimate'].to_numpy();M=len(mice)
    suffix='' if comparison=='all_available_10' else '_matched6'
    records=[];coef=[];attempts=[];curves=[]
    for family in families:
        for seed in seeds:
            target=out/f'readout{suffix}_{family}_seed{seed}.json'
            if target.exists():
                records.append(json.loads(target.read_text()));continue
            paths=[out/'simulation_cells'/f'{family}_{mouse}_seed{seed}_r{reps}.csv' for mouse in sorted(pd.read_csv(out/'observed_cells.csv').mouse.unique())]
            assert all(p.exists() for p in paths)
            cells=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
            cells=cells[cells.mouse.isin(mice)].copy()
            data=prepare_ordinal(cells,mice);r=fit(data,'wls',seed_theta)
            theta=r.theta;B=data.XB@theta[M+4:M+9];bounds=np.isclose(theta,r.bounds[0],atol=1e-5)|np.isclose(theta,r.bounds[1],atol=1e-5)
            w0=float(theta[M+2]);slope=float(theta[M+3]);obs0=seed_theta[M+2];obss=seed_theta[M+3]
            discrepancy=(w0+slope*(np.arange(1,4)-2))-(obs0+obss*(np.arange(1,4)-2))
            item={'family':family,'seed':seed,'w_middle':w0,'slope_per_stage':slope,'curve_rmse_coherence':float(np.sqrt(np.mean(discrepancy**2))),'slope_absolute_error':abs(slope-obss),'n_equivalent_selected':float(cells.n.sum()),'n_success':sum(a['success'] for a in r.attempts),'n_starts':len(r.attempts),'cost':r.cost,'bound_parameters':','.join(np.array(names)[bounds]),'min_observed_psychometric_slope':float(B.min()),'optimality':r.optimality,'theta':theta.tolist()}
            target.write_text(json.dumps(item,indent=2)+'\n');records.append(item)
            for j,a in enumerate(r.attempts):attempts.append({'family':family,'seed':seed,'start':j,**a})
            print('READOUT',family,seed,'slope',round(slope,4),'RMSE',round(item['curve_rmse_coherence'],4),flush=True)
    frame=pd.DataFrame(records);frame.drop(columns='theta').to_csv(out/f'model_readout{suffix}_by_seed.csv',index=False)
    summary=frame.groupby('family',as_index=False).agg(w_middle=('w_middle','mean'),slope_per_stage=('slope_per_stage','mean'),slope_seed_min=('slope_per_stage','min'),slope_seed_max=('slope_per_stage','max'),curve_rmse=('curve_rmse_coherence','mean'),slope_absolute_error=('slope_absolute_error','mean'),seeds=('seed','nunique'))
    summary=summary.sort_values('curve_rmse');summary.to_csv(out/f'model_primacy_ranking{suffix}.csv',index=False)
    (out/f'optimizer_attempts{suffix}.json').write_text(json.dumps(attempts)+'\n')
    print(summary.to_string(index=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--phase',choices=['prepare','simulate','analyze'],required=True);p.add_argument('--families',nargs='*');p.add_argument('--seeds',nargs='+',type=int,default=[0,1]);p.add_argument('--reps',type=int,default=30);p.add_argument('--mice',nargs='*');p.add_argument('--comparison',choices=['all_available_10','matched_6'],default='all_available_10');a=p.parse_args()
    if a.phase=='prepare':a.output.mkdir(parents=True,exist_ok=False);prepare(a.output)
    else:
        score=pd.read_csv(SCORE);families=a.families or score[score.kind=='pulse_only'].sort_values('heldout').family.tolist()
        assert set(families) <= set(score.family), sorted(set(families) - set(score.family))
        if a.phase=='simulate':simulate(a.output,families,a.seeds,a.reps,a.mice)
        else:analyze(a.output,families,a.seeds,a.reps,a.comparison)
