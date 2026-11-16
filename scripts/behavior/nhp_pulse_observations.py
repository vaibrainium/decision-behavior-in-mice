"""Binary NHP-fork emissions with auditable coefficient-sharing constraints.

Inherits the pinned fork's input-driven likelihood. Only the EM M-step and
unique-parameter Gaussian prior are specialized. Positive stored W favors
class 0 (left), following the fork convention. This class supports EM only.
"""
import numpy as np
from scipy import linalg,special
from ssm.observations import InputDrivenObservations


class PulseObservations(InputDrivenObservations):
    def __init__(self,K,D,M,shared_columns=(),prior_sigma=2.):
        if D!=1:raise ValueError('Binary scalar choice only')
        super().__init__(K,D,M,C=2,prior_sigma=prior_sigma)
        self.shared_columns=np.asarray(sorted(set(shared_columns)),int)
        self.index=np.empty((K,M),int);next_index=0
        for j in range(M):
            if j in self.shared_columns:
                self.index[:,j]=next_index;next_index+=1
            else:
                self.index[:,j]=np.arange(next_index,next_index+K);next_index+=K
        self.n_unique=next_index
        self.Wk=self.expand(self.collapse(self.Wk))
        self.mstep_records=[]

    def collapse(self,W):
        W=np.asarray(W)[:,0,:];flat=np.zeros(self.n_unique);n=np.zeros(self.n_unique)
        np.add.at(flat,self.index.ravel(),W.ravel());np.add.at(n,self.index.ravel(),1)
        return flat/n

    def expand(self,q):return np.asarray(q)[self.index][:,None,:]

    @property
    def params(self):return self.Wk

    @params.setter
    def params(self,value):
        self.Wk=self.expand(self.collapse(value))

    def log_prior(self):
        q=self.collapse(self.Wk);s=self.prior_sigma
        return -.5*np.dot(q,q)/s**2-len(q)*np.log(s*np.sqrt(2*np.pi))

    def expected_objective(self,q,X,y0,gamma):
        W=np.asarray(q)[self.index]
        eta=X@W.T;p=special.expit(eta)
        lam=1/self.prior_sigma**2
        loss=np.sum(gamma*(np.logaddexp(0,eta)-y0[:,None]*eta))+.5*lam*np.dot(q,q)
        grad=lam*np.asarray(q).copy();hess=np.eye(self.n_unique)*lam
        for k in range(self.K):
            ix=self.index[k]
            grad[ix]+=X.T@(gamma[:,k]*(p[:,k]-y0))
            h=X.T@((gamma[:,k]*p[:,k]*(1-p[:,k]))[:,None]*X)
            hess[np.ix_(ix,ix)]+=h
        return float(loss),grad,hess

    def m_step(self,expectations,datas,inputs,masks,tags,**kwargs):
        X=[];y0=[];gamma=[]
        for e,y,x,mask in zip(expectations,datas,inputs,masks):
            valid=mask[:,0]if mask is not None else np.ones(len(y),bool)
            X.append(x[valid]);y0.append((y[valid,0]==0).astype(float));gamma.append(e[0][valid])
        X=np.concatenate(X);y0=np.concatenate(y0);gamma=np.concatenate(gamma)
        q=self.collapse(self.Wk);success=False
        for iteration in range(60):
            loss,grad,hess=self.expected_objective(q,X,y0,gamma)
            if np.max(np.abs(grad))<1e-7:success=True;break
            step=linalg.solve(hess,grad,assume_a='pos');scale=1.
            while scale>1e-8:
                proposed=q-scale*step
                new_loss=self.expected_objective(proposed,X,y0,gamma)[0]
                if new_loss<=loss+1e-10:break
                scale*=.5
            q=proposed
            if np.max(np.abs(scale*step))<1e-9:success=True;break
        self.Wk=self.expand(q)
        loss,grad,_=self.expected_objective(q,X,y0,gamma)
        self.mstep_records.append(dict(converged=success,iterations=iteration+1,
            max_abs_gradient=float(np.max(np.abs(grad))),expected_objective=loss))


def independent_expected_loss(obs,q,X,y0,gamma):
    """Reference through inherited fork likelihood and unique Gaussian prior."""
    old=obs.params.copy();obs.params=obs.expand(q)
    y=(1-y0).astype(int)[:,None];mask=np.ones_like(y,dtype=bool)
    ll=obs.log_likelihoods(y,X,mask,None)
    value=-np.sum(gamma*ll)+.5*np.dot(q,q)/obs.prior_sigma**2
    obs.params=old
    return float(value)
