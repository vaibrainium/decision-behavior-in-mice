"""Regression checks for psychometric local solutions and the shared fitting API.

Run: .venv/bin/python -m unittest tests.test_psychometric_multistart
Real-data fixtures are aggregated left-pulse cells exported in the 2026-11-18 audit:
figure4_revision_2026-11-18_v4/source_data/fig4_A_psychometric_mouse.csv.
Tests compare errors/predictions rather than weakly identified coefficients.
"""
import unittest
from unittest.mock import patch
import warnings
import numpy as np
from scipy.optimize import curve_fit
from sklearn.base import clone
from src.utils.pmf_utils import PsychometricFunction, fit_psychometric_function

FIXTURES = {
    'DBM12': ([-18,-9,0,9,18,100], [23/38,28/40,19/33,28/45,20/31,24/38], [38,40,33,45,31,38], .295463979),
    'DBM13': ([-36,-9,0,9,36,100], [6/18,5/15,11/16,5/9,10/17,9/12], [18,15,16,9,17,12], .287445534),
}

class PsychometricMultistartTests(unittest.TestCase):
    def test_real_local_solutions_and_weighted_selection(self):
        for mouse,(xx,yy,nn,target) in FIXTURES.items():
            with self.subTest(mouse=mouse):
                x,y,n=map(np.asarray,(xx,yy,nn))
                legacy=fit_psychometric_function(x,y,n,'logit_4',multistart=False)
                improved=fit_psychometric_function(x,y,n,'logit_4')
                self.assertLess(improved.weighted_sse_,legacy.weighted_sse_-.03)
                self.assertAlmostEqual(improved.weighted_sse_,target,places=6)
                self.assertAlmostEqual(improved.weighted_sse_,np.sum(n*(improved.predict(x)-y)**2),places=12)
                attempts=improved.fit_diagnostics_['attempts']
                self.assertEqual(improved.weighted_sse_,min(a['weighted_sse'] for a in attempts if a['success']))
                self.assertEqual(improved.covar_.shape,(4,4))
                self.assertEqual(set(improved.coefs_),{'mean','var','lapse_rate','guess_rate'})

    def test_legacy_opt_out_matches_original_solver(self):
        x,y,n=map(np.asarray,FIXTURES['DBM13'][:3])
        fitted=fit_psychometric_function(x,y,n,'logit_4',multistart=False)
        params,cov=curve_fit(fitted.logit_4,x,y,p0=[0,1e-5,1e-5,1e-5],
                           bounds=([-100,1e-5,1e-5,1e-5],[100,30,.4,.4]),sigma=1/np.sqrt(n),absolute_sigma=False)
        np.testing.assert_array_equal(list(fitted.coefs_.values()),params)
        np.testing.assert_array_equal(fitted.covar_,cov)
        self.assertEqual(fitted.fit_diagnostics_['n_starts'],1)

    def test_supported_models_custom_bounds_and_missing_response(self):
        x=np.linspace(-1,1,13)
        for model in ['logit_2','logit_3','logit_4']:
            with self.subTest(model=model):
                f=PsychometricFunction(model,mean_lims=(-.8,.8),var_lims=(.1,20),lapse_rate_lims=(0,.2),guess_rate_lims=(0,.2))
                params=[.1,4]+([.05] if model=='logit_3' else [.03,.07] if model=='logit_4' else [])
                y=getattr(f,model)(x,*params);y[2]=np.nan
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    self.assertIs(f.fit(x,y),f)
                self.assertLess(f.weighted_sse_,1e-10)
                np.testing.assert_allclose(f.predict(x),getattr(f,model)(x,*params),atol=1e-5)
                self.assertEqual(clone(f).get_params(),f.get_params())

    def test_failed_start_is_skipped(self):
        x,y,n=map(np.asarray,FIXTURES['DBM13'][:3])
        count=0
        def sometimes(*args,**kwargs):
            nonlocal count
            count+=1
            if count==1:raise RuntimeError('deliberate failure')
            return curve_fit(*args,**kwargs)
        with patch('src.utils.pmf_utils.curve_fit',side_effect=sometimes):
            f=fit_psychometric_function(x,y,n,'logit_4')
        self.assertFalse(f.fit_diagnostics_['attempts'][0]['success'])
        self.assertGreater(f.fit_diagnostics_['n_success'],0)
        with patch('src.utils.pmf_utils.curve_fit',side_effect=RuntimeError('all failed')):
            with self.assertRaisesRegex(RuntimeError,'All .* attempts failed'):
                fit_psychometric_function(x,y,n,'logit_4')

    def test_bad_input_rejected(self):
        for counts in [[1,0,2],[1,-1,2],[1,np.nan,2],[1,2]]:
            with self.subTest(counts=counts),self.assertRaises(ValueError):
                PsychometricFunction().fit([0,1,2],[.2,.5,.8],counts)
        with self.assertRaises(ValueError):PsychometricFunction().fit([0,1],[np.nan,np.nan])
        with self.assertRaises(ValueError):PsychometricFunction().fit([0,1],[.2])

if __name__=='__main__':unittest.main()
