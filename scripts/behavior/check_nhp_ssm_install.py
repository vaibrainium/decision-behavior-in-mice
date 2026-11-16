"""Post-install check for the exact NHP ssm fork. No package installation.

Run only in the new GLM-HMM environment. Tests source provenance, masks,
transition conventions, coefficient sign, and predictive filter semantics.
It is intentionally separate from the dependency-free adapter tests.
"""
import importlib.metadata as metadata
import json
import numpy as np

PIN='a109af369797d852904fd9496f3532524de8f15a'


def run():
    import ssm
    dist=metadata.distribution('ssm')
    origin=json.loads(dist.read_text('direct_url.json')or'{}')
    commit=origin.get('vcs_info',{}).get('commit_id')
    if commit!=PIN:raise RuntimeError(f'Expected NHP ssm commit {PIN}, found {commit}; origin={origin}')
    m=ssm.HMM(2,1,3,observations='input_driven_obs',
              observation_kwargs=dict(C=2,prior_sigma=2.),transitions='standard')
    a=np.array([[.95,.05],[.08,.92]]);pi=np.array([.4,.6])
    m.transitions.params=(np.log(a),)
    m.init_state_distn.params=(np.log(pi),)
    W=np.array([[[.6,-.4,.7]],[[-.5,.3,-.6]]]);m.observations.params=W
    X=np.array([[1.,.2,1.],[1.,-.4,-1.],[1.,.8,0.],[1.,-.5,1.],[1.,.1,0.],[1.,.3,-1.]])
    y=np.array([0,1,1,0,1,1])[:,None]
    mask=np.array([True,False,True,True,False,True])[:,None]
    np.testing.assert_allclose(m.transitions.transition_matrix,a,atol=1e-13)
    # This fork uses class 1 as zero-logit reference. Positive stored W raises
    # P(class 0 = left); a right-choice log-odds coefficient has opposite sign.
    p_right=1/(1+np.exp(X@W[:,0,:].T))
    logits=m.observations.calculate_logits(X)
    np.testing.assert_allclose(np.exp(logits[:,:,1]),p_right,atol=1e-13)
    em=np.where(y==1,p_right,1-p_right)
    em[~mask[:,0]]=1.
    np.testing.assert_allclose(np.exp(m.observations.log_likelihoods(y,X,mask,None)),em,atol=1e-13)
    prior=pi.copy();expected=[];ll=0.
    for t in range(len(y)):
        expected.append(prior.copy());weighted=prior*em[t]
        scale=weighted.sum();ll+=np.log(scale);prior=(weighted/scale)@a
    actual=m.filter(y,input=X,mask=mask)
    np.testing.assert_allclose(actual,expected,atol=1e-10)
    np.testing.assert_allclose(m.log_likelihood(y,inputs=X,masks=mask),ll,atol=1e-10)
    altered=y.copy();altered[~mask]=1-altered[~mask]
    np.testing.assert_allclose(m.filter(altered,input=X,mask=mask),actual,atol=1e-12)
    altered=y.copy();altered[3]=1-altered[3]
    changed=m.filter(altered,input=X,mask=mask)
    np.testing.assert_allclose(changed[:4],actual[:4],atol=1e-12)
    assert not np.allclose(changed[4],actual[4])
    # Exercise the NHP fitting interface, not just import and inference.
    trace=m.fit(y,inputs=X,masks=mask,method='em',num_iters=3,initialize=False,tolerance=1e-6)
    assert np.isfinite(trace).all()
    assert np.isfinite(m.log_likelihood(y,inputs=X,masks=mask))
    print('PASS: exact fork, input-driven emissions, mask invariance, log transitions, class sign, pre-choice filter, EM interface')


if __name__=='__main__':run()
