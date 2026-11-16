"""Check latent-bias likelihood, gradients, time gaps and pre-choice filtering."""
import itertools
import numpy as np
import pandas as pd
from scipy import optimize,special
from scripts.behavior.predictive_bias_states import (
    dynamics,filter_predictions,forward_backward,layout,objective,rouwenhorst,
)
from scripts.behavior.refine_discrete_bias_states import scaled_objective


def run():
    for n in [3,15,31]:
        for rho in [.2,.95,.998]:
            a,z,pi=rouwenhorst(n,rho)
            np.testing.assert_allclose(a.sum(1),1,atol=1e-13)
            np.testing.assert_allclose(pi@a,pi,atol=1e-13)
            np.testing.assert_allclose(pi@z,0,atol=1e-13)
            np.testing.assert_allclose(pi@(z*z),1,atol=1e-13)
            np.testing.assert_allclose(a@z,rho*z,atol=1e-12)
    g=pd.DataFrame({'idx_session':[1,1,2,2],'position':[0,2,0,1]})
    lay=layout(g);X=np.array([[1.,-.4],[1.,.8],[1.,-.6],[1.,.1]])
    y=np.array([0.,1.,1.,0.]);eta=X@np.array([.1,.5])
    a,bias,pi=dynamics('discrete',np.array([.8,.9,.7]))
    ll,post,probs,counts,ic=forward_backward(eta,y,*lay,a,bias,pi)
    # Enumerate every possible hidden path, independently of the recursion.
    total=0.
    for rows in [[0,1],[2,3]]:
        length=int(g.iloc[rows].position.max())+1;prob=0.
        for states in itertools.product([0,1],repeat=length):
            weight=pi[states[0]]
            for t in range(1,length):weight*=a[states[t-1],states[t]]
            for i in rows:
                p=special.expit(eta[i]+bias[states[g.position.iloc[i]]])
                weight*=p if y[i] else 1-p
            prob+=weight
        total+=np.log(prob)
    np.testing.assert_allclose(ll,total,atol=1e-12)
    np.testing.assert_allclose(post.sum(1),1,atol=1e-12)
    np.testing.assert_allclose(counts.sum(),3,atol=1e-12)
    for kind,theta in [('discrete',[.8,.9,.7]),('continuous',np.log([.7,12.]))]:
        par=np.r_[.1,.5,theta]
        loss,grad=objective(par,X,y,lay,kind)
        ref=optimize._numdiff.approx_derivative(lambda q:objective(q,X,y,lay,kind)[0],par,method='3-point').ravel()
        np.testing.assert_allclose(grad,ref,rtol=2e-5,atol=1e-7)
    q=np.r_[.1,.5,.8,special.logit([.995,.98])]
    loss,grad=scaled_objective(q,X,y,lay)
    ref=optimize._numdiff.approx_derivative(lambda p:scaled_objective(p,X,y,lay)[0],q,method='3-point').ravel()
    np.testing.assert_allclose(grad,ref,rtol=2e-5,atol=1e-7)
    pred=filter_predictions(eta,y,g.position.to_numpy(),g.idx_session.to_numpy(),a,bias,pi)
    flipped=y.copy();flipped[1]=1-y[1]
    alt=filter_predictions(eta,flipped,g.position.to_numpy(),g.idx_session.to_numpy(),a,bias,pi)
    np.testing.assert_allclose(pred[:2],alt[:2],atol=0)
    np.testing.assert_allclose(pred[2:],alt[2:],atol=0) # next session resets
    # Missing row advances twice; it does not update with an invented choice.
    p0=special.expit(eta[0]+bias);posterior=pi*(1-p0);posterior/=posterior.sum()
    prior=posterior@a@a
    np.testing.assert_allclose(pred[1,0],prior@special.expit(eta[1]+bias),atol=1e-12)
    print('PASS: AR1 moments; brute-force path likelihood; analytic gradient; no current-choice leakage; gaps/session resets')


if __name__=='__main__':run()
