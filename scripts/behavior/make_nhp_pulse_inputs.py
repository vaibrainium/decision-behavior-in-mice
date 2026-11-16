"""Export the requested NHP GLM-HMM session/input/mask contract for mouse pulses.

No fitting dependencies imported. All original saved records in accepted
sessions stay in sequence; only the matched DDM responded outcomes emit a
choice. Scheduled pulse labels come from the audited follow-up table, never
from response-dependent legacy pulse_type or current RT.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.behavior.history_dynamics import OUT,DATA,TABLE,sha,write_json


def pulse_features(schedule,baseline,encoding,target=None):
    schedule=np.asarray(schedule,int);baseline=np.asarray(baseline,float)
    if encoding not in ['direction','congruency','target_congruency']:raise ValueError(encoding)
    if encoding=='target_congruency':
        if target is None:raise ValueError('Task-assigned target is required')
        side=np.asarray(target,float)
        if side.shape!=schedule.shape:raise ValueError('Target/schedule shape mismatch')
        if np.any((schedule!=0)&~np.isin(side,[-1.,1.])):
            raise ValueError('Every active pulse needs a known task-assigned target')
        side=np.where(np.isin(side,[-1.,1.]),side,0.)
    else:
        side=np.sign(baseline)
        if encoding=='congruency'and np.any((schedule!=0)&(side==0)):
            raise ValueError('Congruency is undefined at zero baseline coherence')
    values=[];names=[];mapping={}
    for stage in [1,2,3]:
        if encoding=='direction':
            for sign,direction in [(-1,'left'),(1,'right')]:
                code=sign*stage;name=f'pulse_{direction}_stage{stage}'
                names.append(name);mapping[str(code)]=name
                values.append((schedule==code).astype(float))
        else:
            for congruency in ['congruent','incongruent']:
                direction='target'if encoding=='target_congruency'else'baseline'
                name=f'pulse_{congruency}_stage{stage}_{direction}_signed'
                relation=np.sign(schedule)*side
                match=(np.abs(schedule)==stage)&(relation==(1 if congruency=='congruent'else-1))
                names.append(name);values.append(side*match)
                mapping[name]=f'{direction} direction (+1 right / -1 left) when active, otherwise 0'
    return np.column_stack(values),names,mapping


def run(encoding='direction',output=None):
    prefix={'direction':'nhp_pulse6','congruency':'nhp_congruency6',
            'target_congruency':'nhp_target_congruency6'}[encoding]
    destination=OUT if output is None else Path(output)
    (destination/'cache').mkdir(parents=True,exist_ok=True)
    path=destination/f'cache/{prefix}_inputs.pkl'
    if path.exists():raise FileExistsError(path)
    raw=pd.read_csv(DATA/'aggregate_data.csv',low_memory=False);raw['aggregate_row']=np.arange(len(raw))
    g=pd.read_pickle(OUT/'cache/aligned_trials.pkl')
    raw=raw[raw.idx_session.isin(g.idx_session.unique())].copy()
    t=pd.read_csv(TABLE,low_memory=False).set_index('aggregate_row')
    schedule=t.ddm_sched_pulse_type.reindex(raw.aggregate_row).to_numpy(float)
    raw['schedule_known']=np.isfinite(schedule)
    schedule=np.nan_to_num(schedule).astype(int)
    raw['scheduled_pulse']=schedule
    prev=raw.groupby('idx_session')[['choice','outcome','reaction_time','signed_coherence','is_correction_trial']].shift()
    side=prev.choice.map({0.:-1.,1.:1.}).fillna(0.)
    raw['h_win']=side*(prev.outcome==1);raw['h_loss']=side*(prev.outcome==0)
    raw['prev_missing']=prev.choice.isna().astype(float)
    raw['prev_logrt']=np.log(prev.reaction_time.where(prev.reaction_time>0)).fillna(0.)
    raw['prev_coherence']=prev.signed_coherence.fillna(0.)/100
    raw['prev_correction']=prev.is_correction_trial.fillna(False).astype(float)
    raw['prev_late']=(prev.reaction_time>5).astype(float)
    raw['intercept']=1.
    # Flexible coherence basis, with 0%-coherence as the reference if present.
    cohs=sorted(raw.signed_coherence.dropna().astype(int).unique())
    reference=0 if 0 in cohs else cohs[0]
    coh_names=[]
    for coh in cohs:
        if coh==reference:continue
        name=f'coherence_{coh}';coh_names.append(name);raw[name]=(raw.signed_coherence==coh).astype(float)
    # Six separate treatment indicators, with controls all zero. Do not force
    # physical-direction effects to share a coefficient. The alternative
    # congruency coding carries baseline sign for right-versus-left outcomes.
    target_known=raw.target.isin([-1.,1.]).to_numpy()
    raw['target_known']=target_known
    main_observed=raw.aggregate_row.isin(g.aggregate_row).to_numpy()
    if encoding=='target_congruency':assert target_known[main_observed].all()
    feature_schedule=np.where(target_known,schedule,0)if encoding=='target_congruency'else schedule
    values,pulse_names,type_map=pulse_features(feature_schedule,raw.signed_coherence.to_numpy(),
                                              encoding,raw.target.to_numpy())
    raw[pulse_names]=values
    names=['intercept']+coh_names+pulse_names+['h_win','h_loss','prev_missing','prev_logrt',
        'prev_coherence','prev_correction','prev_late']
    mask=raw.aggregate_row.isin(g.aggregate_row).to_numpy()
    assert mask.sum()==len(g)
    assert raw.loc[mask,'schedule_known'].all()
    expected=g.set_index('aggregate_row').scheduled_pulse.loc[raw.loc[mask,'aggregate_row']].to_numpy()
    assert np.array_equal(raw.loc[mask,'scheduled_pulse'],expected)
    assert np.array_equal(raw[pulse_names].abs().sum(axis=1).to_numpy(),(feature_schedule!=0).astype(int))
    raw['mask']=mask
    collections={};audit=[]
    for mouse,z in raw.groupby('subject_id',sort=True):
        item=dict(observations=[],inputs=[],masks=[],aggregate_rows=[],session_ids=[],feature_names=names,
                  scheduled_pulse_types=[],baseline_directions=[],task_target_directions=[],
                  pulse_type_indicators=[],pulse_feature_names=pulse_names)
        for session,v in z.groupby('idx_session',sort=False):
            choices=v.choice.fillna(0.).to_numpy(int)[:,None]
            observed=v['mask'].to_numpy(bool)[:,None]
            choices[~observed]=0 # ignored placeholder, no random invented outcome
            item['observations'].append(choices);item['inputs'].append(v[names].to_numpy(float))
            item['masks'].append(observed);item['aggregate_rows'].append(v.aggregate_row.to_numpy(int))
            item['session_ids'].append(int(session))
            item['scheduled_pulse_types'].append(v.scheduled_pulse.to_numpy(int))
            item['baseline_directions'].append(np.sign(v.signed_coherence.to_numpy()))
            item['task_target_directions'].append(v.target.to_numpy(float))
            item['pulse_type_indicators'].append(v[pulse_names].abs().to_numpy(float))
            assert np.isfinite(item['inputs'][-1]).all()
            audit.append(dict(mouse=mouse,idx_session=session,n_rows=len(v),n_observed=int(observed.sum()),
                n_masked=int((~observed).sum()),n_unknown_schedule_masked=int((~v.schedule_known).sum())))
        collections[mouse]=item
    pd.to_pickle(collections,path)
    pd.DataFrame(audit).to_csv(destination/f'{prefix}_input_audit.csv',index=False)
    counts=[]
    for mouse,v in raw[raw['mask']].groupby('subject_id'):
        for zero,label in [(False,'nonzero_coherence'),(True,'zero_coherence')]:
            z=v[(v.signed_coherence==0)==zero]
            for pulse in pulse_names:
                counts.append(dict(mouse=mouse,subset=label,pulse_type=pulse,n=int(z[pulse].abs().sum())))
    pd.DataFrame(counts).to_csv(destination/f'{prefix}_counts.csv',index=False)
    write_json(destination/f'{prefix}_input_manifest.json',dict(source_sha256=sha(__file__),
        nhp_repository='https://github.com/vaibrainium/prior-encoding-in-nhp-sc',
        nhp_commit='b42fb00ed243ace8dc831a6c72caca7c7494d8d2',
        contract='Lists of session observations (T,1), inputs (T,M), masks (T,1); Bernoulli C=2',
        feature_names=names,pulse_features=pulse_names,pulse_type_map=type_map,
        pulse_encoding=('Six one-hot indicators: -1,+1,-2,+2,-3,+3'if encoding=='direction'else
            'Six target-signed indicators: onset stage x congruent/incongruent'if encoding=='target_congruency'else
            'Six baseline-signed indicators: onset stage x congruent/incongruent'),
        outcome='Right versus left choice in both exports; control is the all-zero pulse reference',
        congruency_definition=('Scheduled pulse direction relative to task-assigned correct side'if encoding=='target_congruency'else
            'Scheduled pulse direction relative to signed baseline coherence'),
        zero_coherence=('Retained, classified using task target'if encoding=='target_congruency'else
                        'Physical direction retained; baseline-motion congruency is undefined'),
        n_observed_unknown_target=int((main_observed&~target_known).sum()),
        target_provenance='UW: target in original log; UCLA: existing target reconstructed from Response/Correct, not independently logged',
        unknown_masked_target='Keep saved record and mask; no target-dependent emission on unobserved unknown-target rows',
        coherence_reference=reference,
        history='Shift original saved records; do not compress excluded records into previous trial',
        population='Accepted sessions; masks exactly reproduce 25,493 DDM responded choices',
        missing_dependency=['ssm','autograd'],fitted=False,
        warnings=['Scheduled assignment, not response-dependent delivered-pulse labels',
            'No current RT or realized exposure in choice inputs; target-relative encoding uses the recorded task-side definition',
            'UCLA target reconstruction assumes Correct reflects the preassigned target; task-source audit must distinguish this from independent target logging',
            'Current choice must update filter only after predicting that choice',
            'Masking preserves ordering but does not model selection/missingness']))
    print('EXPORTED',sum(len(v['observations'])for v in collections.values()),'sessions;',
          sum(a['n_rows']for a in audit),'saved rows;',sum(a['n_observed']for a in audit),'observed choices;',len(names),'features')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--encoding',choices=['direction','congruency','target_congruency'],default='direction')
    p.add_argument('--output',type=Path)
    args=p.parse_args();run(args.encoding,args.output)
