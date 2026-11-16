"""Trace selected analysis trials to original trial CSV row order and exclusions."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.behavior.history_dynamics import OUT,DATA,INPUT,sha,write_json


def run():
    a=pd.read_csv(DATA/'aggregate_data.csv',low_memory=False)
    g=pd.read_pickle(OUT/'cache/aligned_trials.pkl');keep_sessions=set(g.idx_session)
    records=[];sources={}
    for session,z in a[a.idx_session.isin(keep_sessions)].groupby('idx_session',sort=False):
        mouse=z.subject_id.iloc[0];sid=z.session_id.iloc[0];rig=z.data_source.iloc[0]
        files=list((Path('/mnt/data/raw')/mouse/sid).glob('*_trial.csv'))
        if len(files)!=1:
            records.append(dict(mouse=mouse,idx_session=session,session_id=sid,n_processed=len(z),
                n_raw_files=len(files),verified=False,issue='Expected one original trial CSV'))
            continue
        p=files[0];r=pd.read_csv(p,low_memory=False);sources[str(p)]=sha(p)
        if rig=='ucla':columns=['TrialNo','AttemptNo'];choice=r.Response.map({-1.:0.,1.:1.}).to_numpy()
        else:columns=['idx_valid','idx_correction'];choice=r.choice.map({-1.:0.,1.:1.}).to_numpy()
        same_length=len(r)==len(z)
        counter=same_length and np.array_equal(r[columns].to_numpy(),z[['idx_valid_trial','idx_correction']].to_numpy())
        agreement=same_length and np.isclose(choice,z.choice.to_numpy(),equal_nan=True).all()
        records.append(dict(mouse=mouse,idx_session=session,session_id=sid,n_processed=len(z),
            n_raw_files=1,n_raw=len(r),verified=bool(same_length and counter and agreement),
            counters_and_order_match=bool(counter),choice_match=bool(agreement),raw_file=str(p)))
    tab=pd.DataFrame(records);tab.to_csv(OUT/'raw_session_alignment.csv',index=False)
    chosen=a[a.idx_session.isin(keep_sessions)].copy()
    reason=np.full(len(chosen),'eligible_response',dtype=object)
    # Report mutually exclusive record categories; these are not subject-level tests.
    reason[chosen.reaction_time.to_numpy()>5]='late_response'
    reason[chosen.reaction_time.to_numpy()<.15]='too_fast'
    reason[chosen.reaction_time.isna().to_numpy()]='missing_rt'
    reason[chosen.choice.isna().to_numpy()]='no_recorded_choice'
    reason[chosen.is_correction_trial.astype(bool).to_numpy()]='correction'
    chosen['record_category']=reason
    by=chosen.groupby(['subject_id','record_category']).size().rename('n_records').reset_index()
    by.to_csv(OUT/'selection_categories_by_mouse.csv',index=False)
    valid=pd.read_csv(DATA/'valid_data.csv',low_memory=False)
    with np.load(INPUT)as x:
        ids=set(x['agg_code'][x['choice']>=0].astype(str))
    absent=valid[~valid.agg_code.astype(str).isin(ids)]
    absent.to_csv(OUT/'valid_responses_absent_from_ddm.csv',index=False)
    meta=dict(n_accepted_sessions=len(keep_sessions),n_raw_sessions_verified=int(tab.verified.sum()),
        n_original_records_in_accepted_sessions=len(chosen),n_main_responded=len(g),
        n_valid_csv=len(valid),n_valid_absent_from_main=len(absent),
        categories=chosen.record_category.value_counts().to_dict(),raw_sha256=sources,
        processing_sources={p:sha(p)for p in ['notebooks/0.0-data-compilation.ipynb',
            'notebooks/0.1-preprocessing-data.ipynb','config/main.yaml','scripts/ddm/build_ddm_inputs.py']},
        source_sha256=sha(__file__),
        session_selection='>=300 noncorrection responses with RT 0.15-5s; control PMF lapse<0.25,guess<0.25,abs(mean)<25,var<0.5',
        compilation_selection='Subjects with fewer than two recorded sessions removed before aggregate export; per-session row order otherwise retained in inspected code',
        limitations=['Original trial CSV is the audit target; cannot reconstruct events never logged there',
            'Dynamics conditional on accepted sessions and responded choice subset',
            'Masked likelihood propagates transitions but does not model outcome-dependent missingness',
            'Reported timescales in saved record steps, not elapsed seconds or necessarily distinct stimulus presentations'])
    write_json(OUT/'selection_audit.json',meta)
    assert tab.verified.all(),tab[~tab.verified]
    print({k:v for k,v in meta.items()if k not in ['raw_sha256','processing_sources']})


if __name__=='__main__':run()
