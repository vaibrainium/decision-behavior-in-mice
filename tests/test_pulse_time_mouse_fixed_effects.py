"""Derivative/objective checks for nonlinear mouse-fixed-offset pulse regression."""
import unittest
import numpy as np
import pandas as pd
from scipy.special import xlogy
from scipy import stats
from scripts.paper.pulse_time_mouse_fixed_effects import model,residual_jac,infer
from scripts.paper.refine_mouse_fixed_effects_inference import observed_cluster_cov


class MouseFixedEffectsChecks(unittest.TestCase):
    def setUp(self):
        self.mice=['a','b','c','d'];rows=[]
        for mouse in self.mice:
            for direction,stage in [(0,0),(-1,1),(1,1),(-1,2),(1,2)]:
                for coherence in [-100,-36,-9,0,9,36,100]:rows.append((mouse,direction,stage,coherence))
        self.cells=pd.DataFrame(rows,columns=['mouse','direction','stage','coherence_pct'])
        self.theta=np.array([-5.,0.,5.,10.,8.,2.,-1.,.05,.002,-.002,.001,.1,.12])
        p,_=model(self.theta,self.cells,self.mice);self.cells['n']=80;self.cells['k']=np.random.default_rng(17).binomial(80,p);self.cells['y']=self.cells.k/self.cells.n

    def numeric_jac(self,fn):
        out=[]
        for j in range(len(self.theta)):
            h=1e-6*max(1,abs(self.theta[j]));up=self.theta.copy();down=self.theta.copy();up[j]+=h;down[j]-=h;out.append((fn(up)-fn(down))/(2*h))
        return np.column_stack(out)

    def test_probability_jacobian(self):
        _,J=model(self.theta,self.cells,self.mice)
        np.testing.assert_allclose(J,self.numeric_jac(lambda q:model(q,self.cells,self.mice)[0]),rtol=2e-5,atol=1e-7)

    def test_both_residual_derivatives(self):
        for objective in ['wls','binomial']:
            with self.subTest(objective=objective):
                _,J=residual_jac(self.theta,self.cells,self.mice,objective)
                numeric=self.numeric_jac(lambda q:residual_jac(q,self.cells,self.mice,objective)[0])
                np.testing.assert_allclose(J,numeric,rtol=2e-3,atol=2e-4)

    def test_objectives_match_weighted_sse_and_binomial_deviance(self):
        p,_=model(self.theta,self.cells,self.mice);n=self.cells.n.to_numpy();k=self.cells.k.to_numpy();y=k/n
        r,_=residual_jac(self.theta,self.cells,self.mice,'wls')
        self.assertAlmostEqual(r@r,np.sum(n*(p-y)**2),places=10)
        r,_=residual_jac(self.theta,self.cells,self.mice,'binomial')
        expected=2*np.sum(xlogy(k,k/(n*p))+xlogy(n-k,(n-k)/(n*(1-p))))
        self.assertAlmostEqual(r@r,expected,places=9)

    def test_mouse_id_is_categorical_and_direction_contrast(self):
        # Changing only mouse a's intercept cannot change any other mouse prediction.
        original,_=model(self.theta,self.cells,self.mice);new=self.theta.copy();new[0]+=2;changed,_=model(new,self.cells,self.mice)
        np.testing.assert_array_equal(original[self.cells.mouse!='a'],changed[self.cells.mouse!='a'])
        M=len(self.mice)
        for t in [1,2]:
            right=self.theta[0]+self.theta[M]+self.theta[M+1]*t+self.theta[M+2]*t
            left=self.theta[0]-self.theta[M]+self.theta[M+1]*t-self.theta[M+2]*t
            self.assertAlmostEqual(right-left,2*(self.theta[M]+t*self.theta[M+2]))

    def test_observed_bread_matches_information_at_expected_counts(self):
        cells=self.cells.copy();prob,J=model(self.theta,cells,self.mice);cells['k']=cells.n*prob;cells['y']=prob
        for objective in ['wls','binomial']:
            with self.subTest(objective=objective):
                _,bread,_=observed_cluster_cov(self.theta,cells,self.mice,objective)
                weight=cells.n.to_numpy() if objective=='wls' else cells.n.to_numpy()/(prob*(1-prob))
                expected=J.T@(weight[:,None]*J)
                np.testing.assert_allclose(bread,expected,rtol=1e-3,atol=5e-3)

    def test_wald_block_and_cluster_degrees_of_freedom(self):
        cov=np.eye(len(self.theta));rows=infer(self.theta,cov,len(self.mice),10,'toy','toy','wls')
        row=next(r for r in rows if r['test']=='alpha_directional');expected=(8**2+(-1)**2)/2
        self.assertEqual(row['statistic_F'],expected)
        self.assertEqual(row['df_denom'],9)
        self.assertAlmostEqual(row['p_raw'],stats.f.sf(expected,2,9))

if __name__=='__main__':unittest.main()
