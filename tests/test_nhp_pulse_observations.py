"""Checks shared/free EM emissions against the original fork likelihood."""
import numpy as np
from scipy import optimize
from scripts.behavior.nhp_pulse_observations import PulseObservations,independent_expected_loss


def run():
    rng=np.random.default_rng(115)
    X=np.column_stack([np.ones(180),rng.normal(size=(180,4))])
    y0=rng.integers(0,2,180).astype(float);gamma=rng.dirichlet([2,3],180)
    for shared in [[],[2,4]]:
        obs=PulseObservations(2,1,5,shared_columns=shared,prior_sigma=2.)
        q=rng.normal(0,.2,obs.n_unique)
        loss,grad,hess=obs.expected_objective(q,X,y0,gamma)
        ref=independent_expected_loss(obs,q,X,y0,gamma)
        np.testing.assert_allclose(loss,ref,atol=1e-10)
        ng=optimize._numdiff.approx_derivative(lambda a:independent_expected_loss(obs,a,X,y0,gamma),q,method='3-point').ravel()
        nh=optimize._numdiff.approx_derivative(lambda a:obs.expected_objective(a,X,y0,gamma)[1],q,method='3-point')
        np.testing.assert_allclose(grad,ng,atol=1e-7)
        np.testing.assert_allclose(hess,nh,atol=1e-7)
        obs.params=obs.expand(q)
        y=(1-y0).astype(int)[:,None];mask=np.ones_like(y,dtype=bool);mask[::7]=False
        observed=mask[:,0]
        ref=optimize.minimize(lambda a:obs.expected_objective(a,X[observed],y0[observed],gamma[observed])[:2],
            q,jac=True,method='BFGS',options={'gtol':1e-9})
        obs.m_step([(gamma,None,None)],[y],[X],[mask],[None])
        np.testing.assert_allclose(obs.collapse(obs.params),ref.x,atol=1e-6)
        if shared:np.testing.assert_array_equal(obs.params[0,0,shared],obs.params[1,0,shared])
        masked_y=y.copy();masked_y[~mask]=1-masked_y[~mask]
        start=obs.params.copy();obs.m_step([(gamma,None,None)],[masked_y],[X],[mask],[None])
        np.testing.assert_allclose(obs.params,start,atol=1e-7)
    print('PASS: inherited likelihood, analytic gradients/Hessian, constrained optimum, exact sharing, masks')


if __name__=='__main__':run()
