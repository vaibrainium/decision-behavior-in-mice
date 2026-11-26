import math
import unittest

from scripts.ddm.fit_mouse_ddm import fit_likelihood_params


class ChoiceRTWeightTests(unittest.TestCase):
    def test_default_likelihood_configuration_is_unchanged(self):
        self.assertEqual(fit_likelihood_params(False), {
            "method": "qmle_censored", "nbins": 9, "rt_nllh_weight": 1.0
        })
        self.assertEqual(fit_likelihood_params(True), {
            "method": "qmle_censored", "nbins": 9, "rt_nllh_weight": 1.0,
            "include_censored": False,
        })

    def test_exploratory_rt_weight_is_recorded(self):
        for weight in [0.0, 0.125, 0.25, 0.5, 1.0]:
            with self.subTest(weight=weight):
                result = fit_likelihood_params(True, weight)
                self.assertEqual(result["rt_nllh_weight"], weight)
                self.assertIs(result["include_censored"], False)

    def test_invalid_rt_weight_rejected(self):
        for weight in [-1.0, math.nan, math.inf]:
            with self.subTest(weight=weight):
                with self.assertRaisesRegex(ValueError, "finite and nonnegative"):
                    fit_likelihood_params(True, weight)


if __name__ == "__main__":
    unittest.main()
