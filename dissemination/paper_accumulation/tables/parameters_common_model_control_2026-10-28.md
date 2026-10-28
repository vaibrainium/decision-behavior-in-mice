# Common-model parameters (L0U0V1Z0G1, fast-only guesses, guess bias free; control trials, [50] repetitions)

Source: `/mnt/data/processed/ddm/fits_resp_final`; script `scripts/ddm/parameter_table.py`. Recovery r from `ddm/recovery/summary_parameters.csv`.

| mouse | non-decision time (s) | bound separation | starting point (fraction of a) | drift gain | drift offset | drift variability (sv) | fast-guess probability | fast-guess bias (P right) | fast-guess delay (s) |
|---|---|---|---|---|---|---|---|---|---|
| DBM12 | 0.113 | 5.868 | 0.286 | 3.468 | -0.111 | 2.832 | 0.321 | 0.737 | 0.293 |
| DBM13 | 0.157 | 7.293 | 0.399 | 1.970 | -0.208 | 2.683 | 0.193 | 0.537 | 0.156 |
| DBM14 | 0.182 | 3.959 | 0.422 | 1.118 | 0.030 | 0.477 | 0.293 | 0.558 | 0.276 |
| DBM15 | 0.109 | 7.775 | 0.393 | 2.075 | -0.179 | 2.305 | 0.175 | 0.601 | 0.293 |
| DBM5 | 0.334 | 7.105 | 0.467 | 3.380 | -0.156 | 2.724 | 0.288 | 0.515 | 0.293 |
| DBM6 | 0.169 | 6.779 | 0.399 | 3.489 | 0.294 | 2.310 | 0.207 | 0.673 | 0.289 |
| PSUIM10 | 0.415 | 9.121 | 0.661 | 4.084 | 0.819 | 2.834 | 0.094 | 0.448 | 0.084 |
| PSUIM5 | 0.088 | 7.435 | 0.583 | 3.006 | -0.256 | 1.521 | 0.119 | 0.467 | 0.299 |
| PSUIM6 | 0.014 | 5.296 | 0.650 | 2.287 | -0.223 | 1.001 | 0.099 | 0.397 | 0.300 |
| PSUIM7 | 0.222 | 6.026 | 0.622 | 6.035 | 0.522 | 2.940 | 0.277 | 0.435 | 0.272 |

| parameter | median | mean | min | max | recovery_r | note |
|---|---|---|---|---|---|---|
| non-decision time (s) | 0.163 | 0.180 | 0.014 | 0.415 | 0.936 |  |
| bound separation | 6.942 | 6.666 | 3.959 | 9.121 | 0.813 |  |
| starting point (fraction of a) | 0.444 | 0.488 | 0.286 | 0.661 | 0.968 |  |
| drift gain | 3.193 | 3.091 | 1.118 | 6.035 | 0.924 |  |
| drift offset | -0.133 | 0.053 | -0.256 | 0.819 | 0.892 |  |
| drift variability (sv) | 2.497 | 2.163 | 0.477 | 2.940 | 0.848 |  |
| fast-guess probability | 0.200 | 0.207 | 0.094 | 0.321 | 0.933 |  |
| fast-guess bias (P right) | 0.526 | 0.537 | 0.397 | 0.737 | 0.867 |  |
| fast-guess delay (s) | 0.291 | 0.256 | 0.084 | 0.300 | 0.181 | not recovered in model recovery (r = 0.18) |

Parameters at a bound:
- PSUIM5 guess_tau = 0.299 at its upper bound [0.01, 0.3]
- PSUIM6 guess_tau = 0.3 at its upper bound [0.01, 0.3]
