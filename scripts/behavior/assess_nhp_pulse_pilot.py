"""Audit/evaluate fixed outer-test predictions; no model or prior selection.

Per-mouse block intervals condition on fitted models; they do not propagate
training uncertainty or establish a population result from two animals.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import linalg

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'dissemination/nhp_pulse_hmm_2026-11-15'
HISTORY=ROOT/'dissemination/history_dynamics_2026-11-14'
B=600


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def block_weights(g,rng):
    w=np.zeros(len(g))
    for _,ix in g.groupby('idx_session',sort=False).indices.items():
        blocks=(g.iloc[ix].position.to_numpy()//50).astype(int);unique=np.unique(blocks)
        counts=np.bincount(rng.integers(0,len(unique),len(unique)),minlength=len(unique))
        w[ix]=counts[np.searchsorted(unique,blocks)]
    return w


def regression(g):
    d=pd.get_dummies(g[['condition','idx_session','coherence_pct']].astype(str),drop_first=True,dtype=float)
    coh=pd.get_dummies(g.coherence_pct.astype(str),drop_first=True,dtype=float)
    choice=g.choice.to_numpy();pos=g.position_frac.to_numpy()-.5
    return np.column_stack([np.ones(len(g)),d.to_numpy(),choice,
        coh.to_numpy()*choice[:,None],pos,pos*pos,
        g[['h_win','h_loss','prev_logrt','prev_missing','prev_late','prev_correction','prev_coherence']].to_numpy(float)])


def ols(Z,y,w):
    penalty=np.eye(Z.shape[1])*.1;penalty[0,0]=0.
    return linalg.solve(Z.T@(w[:,None]*Z)+penalty,Z.T@(w*y),assume_a='pos')


def pulse_contrasts(g,prob,w):
    # Signed directions remain the inputs; this accuracy view uses only nonzero
    # coherence and matches controls separately at the same signed coherence.
    coh=g.coherence_pct.to_numpy();pulse=g.scheduled_pulse.to_numpy()
    correct=np.where(coh>0,prob,1-prob)
    rows=[]
    for stage in [1,2,3]:
        for relation,label in [(1,'congruent'),(-1,'incongruent')]:
            mask=(np.abs(coh)<=36)&(coh!=0)&(np.abs(pulse)==stage)&(np.sign(pulse)*np.sign(coh)==relation)
            deltas=[];weights=[];ns=0
            for c in np.unique(coh[mask]):
                pi=mask&(coh==c);ci=(pulse==0)&(coh==c)
                pn=w[pi].sum();cn=w[ci].sum()
                if pn==0 or cn==0:continue
                deltas.append(100*(np.average(correct[pi],weights=w[pi])-np.average(correct[ci],weights=w[ci])))
                weights.append(pn);ns+=int(pi.sum())
            rows.append(dict(stage=stage,congruency=label,n_pulse=ns,
                effect_pp=np.average(deltas,weights=weights)if weights else np.nan))
    return rows


def coefficients(selected):
    rows=[];state_rows=[]
    for (mouse,fold,family),item in selected.items():
        fit=item['result'];W=fit['state']['weights'][:,0,:];names=item['names'];K=len(W)
        templates=np.zeros((2,len(names)));templates[:,0]=1.
        for j,c in enumerate([-36,36]):templates[j,names.index(f'coherence_{c}')]=1.
        right=1/(1+np.exp(templates@W.T));contrast=right[1]-right[0]
        high=int(np.argmax(contrast))
        for k in range(K):
            state_rows.append(dict(mouse=mouse,fold=fold,family=family,state=k,
                baseline_coherence_contrast=contrast[k],is_higher_contrast=(k==high),
                initial_probability=fit['state']['initial'][k],
                self_transition=fit['state']['transition'][k,k],
                mean_dwell_saved_rows=1/(1-fit['state']['transition'][k,k])if K>1 else np.nan))
            for j,name in enumerate(names):
                late=name in ['pulse_left_stage3','pulse_right_stage3']
                rows.append(dict(mouse=mouse,fold=fold,family=family,state=k,feature=name,
                    coefficient_right_logodds=-W[k,j]if not late else np.nan,
                    stored_weight=W[k,j],estimable=not late,is_higher_contrast=(k==high)))
    return pd.DataFrame(rows),pd.DataFrame(state_rows)


def run(version=1):
    suffix=''if version==1 else'_v2'
    destination=OUT if version==1 else OUT/'assessment_v2'
    (destination/'cache').mkdir(parents=True,exist_ok=True)
    pred=pd.read_csv(OUT/f'heldout_predictions{suffix}.csv');models=pd.read_pickle(OUT/f'cache/selected_models{suffix}.pkl')
    g=pd.read_pickle(HISTORY/'cache/aligned_trials.pkl').set_index('aggregate_row',drop=False)
    signature=json.loads((OUT/'pilot_manifest.json').read_text())
    for path,digest in signature['sources'].items():assert sha(ROOT/path)==digest,path
    assert sha(ROOT/'dissemination/history_dynamics_2026-11-14/cache/nhp_pulse6_inputs.pkl')==signature['input_sha256']
    assert not pred.duplicated(['mouse','family','aggregate_row']).any()
    matches=g.loc[pred.aggregate_row]
    np.testing.assert_array_equal(pred.choice,matches.choice)
    np.testing.assert_array_equal(pred.fold,matches.fold)
    ll=-(pred.choice*np.log(pred.p_right)+(1-pred.choice)*np.log1p(-pred.p_right))
    np.testing.assert_allclose(ll,pred.nll,atol=1e-10)
    coef,states=coefficients(models);coef.to_csv(destination/'coefficients.csv',index=False)
    states.to_csv(destination/'state_parameters.csv',index=False)
    scores=[];differences=[];rt=[];pulse=[];rt_models={};rng=np.random.default_rng(115321)
    for mouse,v in pred.groupby('mouse',sort=True):
        pivot=v.pivot(index='aggregate_row',columns='family',values='nll').sort_index()
        assert pivot.notna().all().all()
        z=g.loc[pivot.index].reset_index(drop=True)
        expected=g[(g.mouse==mouse)&(g.fold>=2)]
        assert set(pivot.index)==set(expected.aggregate_row)
        boot=np.array([block_weights(z,rng)for _ in range(B)])
        for family in ['static','tied','free']:
            scores.append(dict(mouse=mouse,family=family,n=len(z),nll=pivot[family].sum(),
                bits_per_trial=pivot[family].mean()/np.log(2)))
        for better,baseline in [('tied','static'),('free','static'),('free','tied')]:
            gain=(pivot[baseline]-pivot[better]).to_numpy()/np.log(2)
            bs=(boot@gain)/boot.sum(1);ci=np.quantile(bs,[.025,.975])
            differences.append(dict(mouse=mouse,candidate=better,baseline=baseline,n=len(z),
                gain_bits_per_trial=gain.mean(),lo=ci[0],hi=ci[1],
                nll_difference=float(pivot[better].sum()-pivot[baseline].sum()),
                interval='Conditional on fitted models; within-session 50-saved-record blocks'))
        base=regression(z);logrt=np.log(z.rt.to_numpy())
        for family in ['tied','free']:
            p=v[v.family==family].set_index('aggregate_row').loc[pivot.index]
            q=p.prior_higher_coherence_contrast.to_numpy()
            X=np.column_stack([base,q]);point=ols(X,logrt,np.ones(len(z)))
            bs=np.array([ols(X,logrt,w)[-1]for w in boot]);ci=np.quantile(bs,[.025,.975])
            rt.append(dict(mouse=mouse,family=family,coefficient_logrt=point[-1],lo=ci[0],hi=ci[1],
                ratio_rt_state0_to1=np.exp(point[-1]),q10=np.quantile(q,.1),q90=np.quantile(q,.9),
                effective_higher_state_count=q.sum(),
                interval='Descriptive conditional association, fixed fitted q; no population test'))
            rt_models[(mouse,family)]=dict(coefficients=point,bootstrap_state_slopes=bs)
        for family in ['observed','static','tied','free']:
            prob=z.choice.to_numpy(float)if family=='observed'else v[v.family==family].set_index('aggregate_row').loc[pivot.index,'p_right'].to_numpy()
            point=pulse_contrasts(z,prob,np.ones(len(z)))
            resamples=np.array([[r['effect_pp']for r in pulse_contrasts(z,prob,w)]for w in boot])
            for j,row in enumerate(point):
                if np.isfinite(row['effect_pp']):ci=np.nanquantile(resamples[:,j],[.025,.975])
                else:ci=[np.nan,np.nan]
                pulse.append(dict(mouse=mouse,family=family,**row,lo=ci[0],hi=ci[1],
                    window='All retained response times; no current-RT stratification'))
    pd.DataFrame(scores).to_csv(destination/'heldout_scores.csv',index=False)
    pd.DataFrame(differences).to_csv(destination/'heldout_differences.csv',index=False)
    pd.DataFrame(rt).to_csv(destination/'rt_external_validation.csv',index=False)
    pd.DataFrame(pulse).to_csv(destination/'pulse_congruency_validation.csv',index=False)
    pd.to_pickle(rt_models,destination/'cache/rt_validation_models.pkl')
    audit=pd.read_csv(OUT/'fit_audit.csv')
    selected=[r['result']for r in models.values()]
    record=dict(n_all_fits=len(audit),n_selected_models=len(models),n_selected_converged=sum(r['converged']for r in selected),
        n_selected_with_mstep_failure=sum(r['mstep_failures']>0 for r in selected),
        n_outer_choice_predictions=len(pred),n_distinct_test_trials=int(pred.aggregate_row.nunique()),
        source_and_input_hashes_verified=True,likelihood_recomputed=True,trial_identity_and_folds_verified=True,
        n_bootstrap=B,block_length_saved_rows=50,source_sha256=sha(__file__),
        version=version,
        limitations=['Two-mouse pilot; no population p-value','Condition on selected/responded trials',
            'Block intervals condition on trained models','Not a joint RT model; no RT-conditioned pulse prediction',
            'No late pulse observations in pilot mice'])
    if version==2:
        search=pd.read_csv(OUT/'search_check.csv')
        record['n_additional_training_search_fits']=int((search.stage!='selection_summary').sum())
    (destination/'assessment_audit.json').write_text(json.dumps(record,indent=2)+'\n')
    print(pd.DataFrame(differences).round(5).to_string(index=False))
    print(pd.DataFrame(rt).round(5).to_string(index=False))
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',type=int,choices=[1,2],default=1)
    run(p.parse_args().version)
