"""Independent mathematical checks for history/serial diagnostics."""
import numpy as np
import pandas as pd
from scipy import optimize,special
import statsmodels.api as sm
from scripts.behavior.history_dynamics import logistic,acf_table


def run():
    rng=np.random.default_rng(12)
    X=np.column_stack([np.ones(600),rng.normal(size=(600,4))])
    y=rng.binomial(1,special.expit(X@np.array([.1,.2,-.4,.8,-.2])))
    b,ok=logistic(X,y,penalty=0.)
    ref=sm.GLM(y,X,family=sm.families.Binomial()).fit()
    assert ok
    np.testing.assert_allclose(b,ref.params,atol=1e-7)
    b,ok=logistic(X,y,penalty=.1)
    lam=np.r_[0.,np.full(4,.1)]
    result=optimize.minimize(lambda z: np.sum(np.logaddexp(0,X@z)-y*(X@z))+.5*np.dot(lam*z,z),
        np.zeros(5),jac=lambda z:X.T@(special.expit(X@z)-y)+lam*z,method='BFGS',options={'gtol':1e-8})
    assert ok
    np.testing.assert_allclose(b,result.x,atol=1e-6)
    g=pd.DataFrame({'idx_session':[1,1,1,2,2],'position':[0,2,5,0,1]})
    z=acf_table(g,np.array([1.,-1.,.5,-1.,1.]),lags=[1,2,3,5])
    assert z.n_pairs.tolist()==[1,1,1,1],z
    # With no consecutive retained rows, lag-one support must stay zero.
    h=pd.DataFrame({'idx_session':[1,1,1],'position':[0,2,5]})
    z=acf_table(h,np.array([1.,-1.,.5]),lags=[1])
    assert z.n_pairs.iloc[0]==0 and np.isnan(z.acf.iloc[0])
    print('PASS: logistic estimates agree with statsmodels/BFGS; lag pairs preserve gaps and session boundaries')


if __name__=='__main__':run()
