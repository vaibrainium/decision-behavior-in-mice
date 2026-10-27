# Common-model parameters (L0U0V1Z0G1, fast-only guesses, guess bias free; all trials, 50 repetitions)

Source: `/mnt/data/processed/ddm/fits_resp_final`; script `scripts/ddm/parameter_table.py`. Recovery r from `ddm/recovery/summary_parameters.csv`.

| mouse | non-decision time (s) | bound separation | starting point (fraction of a) | drift gain | drift offset | drift variability (sv) | fast-guess probability | fast-guess bias (P right) | fast-guess delay (s) |
|---|---|---|---|---|---|---|---|---|---|
| DBM12 | 0.200 | 5.652 | 0.256 | 3.443 | 0.506 | 2.849 | 0.387 | 0.635 | 0.292 |
| DBM13 | 0.055 | 7.846 | 0.312 | 2.213 | 0.215 | 2.763 | 0.193 | 0.524 | 0.208 |
| DBM14 | 0.021 | 3.511 | 0.446 | 0.850 | 0.008 | 0.108 | 0.196 | 0.565 | 0.227 |
| DBM15 | 0.116 | 8.215 | 0.391 | 2.163 | -0.305 | 2.567 | 0.179 | 0.607 | 0.279 |
| DBM5 | 0.326 | 7.053 | 0.478 | 3.432 | -0.048 | 2.877 | 0.289 | 0.524 | 0.290 |
| DBM6 | 0.114 | 7.793 | 0.424 | 3.614 | 0.396 | 2.351 | 0.217 | 0.631 | 0.290 |
| PSUIM10 | 0.462 | 7.044 | 0.681 | 3.304 | 0.365 | 2.017 | 0.128 | 0.496 | 0.204 |
| PSUIM5 | 0.229 | 4.444 | 0.583 | 1.939 | -0.122 | 0.736 | 0.117 | 0.431 | 0.296 |
| PSUIM6 | 0.042 | 4.611 | 0.646 | 2.041 | -0.171 | 0.804 | 0.096 | 0.384 | 0.291 |
| PSUIM7 | 0.269 | 5.283 | 0.607 | 6.093 | 0.865 | 2.996 | 0.261 | 0.416 | 0.261 |

| parameter | median | min | max | recovery_r | note |
|---|---|---|---|---|---|
| non-decision time (s) | 0.158 | 0.021 | 0.462 | 0.936 |  |
| bound separation | 6.348 | 3.511 | 8.215 | 0.813 |  |
| starting point (fraction of a) | 0.462 | 0.256 | 0.681 | 0.968 |  |
| drift gain | 2.758 | 0.850 | 6.093 | 0.924 |  |
| drift offset | 0.112 | -0.305 | 0.865 | 0.892 |  |
| drift variability (sv) | 2.459 | 0.108 | 2.996 | 0.848 |  |
| fast-guess probability | 0.195 | 0.096 | 0.387 | 0.933 |  |
| fast-guess bias (P right) | 0.524 | 0.384 | 0.635 | 0.867 |  |
| fast-guess delay (s) | 0.284 | 0.204 | 0.296 | 0.181 | not recovered in model recovery (r = 0.18) |

Parameters at a bound:
- PSUIM7 sv = 3 at its upper bound [0, 3]
