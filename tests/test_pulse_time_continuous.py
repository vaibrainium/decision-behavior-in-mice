"""Continuous-time pulse model: units, centering, controls, derivatives and curvature."""
import unittest
import numpy as np
import pandas as pd
from scipy.special import logit
from scripts.paper.pulse_time_continuous import prepare,model,residual_jac,covariance,CENTER,SCALE


class ContinuousPulseTimeChecks(unittest.TestCase):
    def setUp(self):
        self.mice=['a','b','c','d'];rows=[]
        for mouse in self.mice:
            for d,t in [(0,0)]+[(d,t) for d in [-1,1] for t in [.05,.08,.23]]:
                for c in [-100,-36,-9,0,9,36,100]:rows.append((mouse,d,t,c))
        self.cells=pd.DataFrame(rows,columns=['mouse','direction','onset_s','coherence_pct']);self.cells['n']=80;self.cells['k']=40;self.cells['y']=.5
        self.theta=np.r_[[-5,0,5,10],[1,.3,8,-2,.05,.002,-.003,.001,-.0005,.1,.12]]
        initial=prepare(self.cells,self.mice);p,_=model(self.theta,initial);self.cells['k']=np.random.default_rng(61).binomial(80,p);self.cells['y']=self.cells.k/80;self.data=prepare(self.cells,self.mice)

    def numeric_jac(self,fn):
        columns=[]
        for j in range(len(self.theta)):
            h=1e-6*max(1,abs(self.theta[j]));up=self.theta.copy();down=self.theta.copy();up[j]+=h;down[j]-=h;columns.append((fn(up)-fn(down))/(2*h))
        return np.column_stack(columns)

    def test_probability_and_residual_derivatives(self):
        _,J=model(self.theta,self.data);np.testing.assert_allclose(J,self.numeric_jac(lambda q:model(q,self.data)[0]),rtol=2e-5,atol=1e-7)
        for objective in ['wls','binomial']:
            _,J=residual_jac(self.theta,self.data,objective);numeric=self.numeric_jac(lambda q:residual_jac(q,self.data,objective)[0]);np.testing.assert_allclose(J,numeric,rtol=2e-3,atol=2e-4)

    def test_time_center_changes_parameterization_not_predictions(self):
        M=len(self.mice);new_center=.10;shift=(CENTER-new_center)/SCALE;q=self.theta.copy()
        for intercept,slope in [(M,M+1),(M+2,M+3),(M+5,M+6),(M+7,M+8)]:q[intercept]-=q[slope]*shift
        other=prepare(self.cells,self.mice,center=new_center)
        np.testing.assert_allclose(model(self.theta,self.data)[0],model(q,other)[0],atol=1e-14)

    def test_control_does_not_receive_pulse_time_or_presence_effect(self):
        cells=self.cells.copy();cells.loc[cells.direction==0,'onset_s']=1.23
        np.testing.assert_array_equal(model(self.theta,self.data)[0],model(self.theta,prepare(cells,self.mice))[0])
        q=self.theta.copy();q[4:8]+=[3,2,1,.5];p,_=model(q,self.data);original,_=model(self.theta,self.data)
        np.testing.assert_allclose(p[self.cells.direction==0],original[self.cells.direction==0])

    def test_primacy_slope_is_half_direction_difference_not_common_bias(self):
        M=len(self.mice);choose=self.cells[(self.cells.mouse=='a')&(self.cells.coherence_pct==0)&self.cells.direction.ne(0)].copy()
        data=prepare(choose,self.mice);p,_=model(self.theta,data);B=data.XB@self.theta[M+4:M+9];A=logit((p-self.theta[-2])/(1-self.theta[-2]-self.theta[-1]))/B
        choose['recovered_A']=A;wide=choose.pivot(index='onset_s',columns='direction',values='recovered_A');w=(wide[1]-wide[-1])/2
        np.testing.assert_allclose(w,self.theta[M+2]+self.theta[M+3]*(w.index-CENTER)/SCALE,atol=1e-10)
        self.assertAlmostEqual((w.loc[.23]-w.loc[.05])/(.23-.05),self.theta[M+3]/SCALE,places=10)

    def test_objective_and_observed_hessian_at_expected_counts(self):
        p,J=model(self.theta,self.data);r,_=residual_jac(self.theta,self.data,'wls');self.assertAlmostEqual(r@r,np.sum(self.data.n*(p-self.data.y)**2),places=10)
        cells=self.cells.copy();cells['k']=cells.n*p;cells['y']=p;data=prepare(cells,self.mice)
        for objective in ['wls','binomial']:
            _,H,_=covariance(self.theta,data,objective);weight=data.n if objective=='wls' else data.n/(p*(1-p));expected=J.T@(weight[:,None]*J);np.testing.assert_allclose(H,expected,rtol=1e-3,atol=5e-3)

    def test_cluster_covariance_is_invariant_to_frequency_aggregation(self):
        rows=[]
        for _,r in self.cells.iterrows():
            for outcome in [1]*int(r.k)+[0]*int(r.n-r.k):rows.append((r.mouse,r.direction,r.onset_s,r.coherence_pct,1,outcome,outcome))
        expanded=pd.DataFrame(rows,columns=['mouse','direction','onset_s','coherence_pct','n','k','y'])
        for objective in ['wls','binomial']:
            collapsed,H,_=covariance(self.theta,self.data,objective)
            individual,HI,_=covariance(self.theta,prepare(expanded,self.mice),objective)
            np.testing.assert_allclose(H,HI,rtol=2e-4,atol=1e-3)
            np.testing.assert_allclose(collapsed,individual,rtol=2e-4,atol=1e-5)

    def test_unknown_mouse_fails_explicitly(self):
        with self.assertRaisesRegex(ValueError,'Unknown mouse'):prepare(self.cells,['a','b','c'])

if __name__=='__main__':unittest.main()
