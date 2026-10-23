# Common-model parameters (L0U0V1Z0G1, fast-only guesses, guess bias free; all trials, 50 repetitions)

Source: `/mnt/data/processed/ddm/fits_final`; script `scripts/ddm/parameter_table.py`. Recovery r from `ddm/recovery/summary_parameters.csv`.

| mouse | non-decision time (s) | bound separation | starting point (fraction of a) | drift gain | drift offset | drift variability (sv) | fast-guess probability | fast-guess bias (P right) | fast-guess delay (s) |
|---|---|---|---|---|---|---|---|---|---|
| DBM12 | 0.178 | 5.977 | 0.255 | 2.942 | -0.027 | 2.948 | 0.349 | 0.762 | 0.297 |
| DBM13 | 0.135 | 7.847 | 0.297 | 2.538 | 0.104 | 2.847 | 0.216 | 0.585 | 0.245 |
| DBM14 | 0.002 | 3.575 | 0.511 | 0.728 | -0.068 | 0.399 | 0.204 | 0.488 | 0.178 |
| DBM15 | 0.009 | 9.466 | 0.355 | 1.804 | -0.043 | 2.250 | 0.185 | 0.639 | 0.297 |
| DBM5 | 0.221 | 8.528 | 0.474 | 3.444 | -0.206 | 2.862 | 0.287 | 0.510 | 0.287 |
| DBM6 | 0.097 | 7.990 | 0.411 | 3.584 | 0.507 | 2.470 | 0.224 | 0.632 | 0.298 |
| PSUIM10 | 0.492 | 6.965 | 0.691 | 2.828 | 0.338 | 2.202 | 0.115 | 0.644 | 0.027 |
| PSUIM5 | 0.026 | 8.216 | 0.589 | 2.882 | -0.150 | 1.667 | 0.120 | 0.427 | 0.298 |
| PSUIM6 | 0.003 | 9.490 | 0.662 | 3.972 | -0.360 | 2.270 | 0.115 | 0.446 | 0.295 |
| PSUIM7 | 0.198 | 6.142 | 0.605 | 5.702 | 1.048 | 2.992 | 0.245 | 0.371 | 0.288 |

| parameter | median | min | max | recovery_r | note |
|---|---|---|---|---|---|
| non-decision time (s) | 0.116 | 0.002 | 0.492 | 0.936 |  |
| bound separation | 7.918 | 3.575 | 9.490 | 0.813 |  |
| starting point (fraction of a) | 0.492 | 0.255 | 0.691 | 0.968 |  |
| drift gain | 2.912 | 0.728 | 5.702 | 0.924 |  |
| drift offset | -0.035 | -0.360 | 1.048 | 0.892 |  |
| drift variability (sv) | 2.370 | 0.399 | 2.992 | 0.848 |  |
| fast-guess probability | 0.210 | 0.115 | 0.349 | 0.933 |  |
| fast-guess bias (P right) | 0.547 | 0.371 | 0.762 | 0.867 |  |
| fast-guess delay (s) | 0.292 | 0.027 | 0.298 | 0.181 | not recovered in model recovery (r = 0.18) |

Parameters at a bound:
- DBM12 guess_tau = 0.297 at its upper bound [0.01, 0.3]
- DBM14 ndt = 0.0018 at its lower bound [0, 0.8]
- DBM15 a = 9.47 at its upper bound [0.3, 9.5]
- DBM6 guess_tau = 0.298 at its upper bound [0.01, 0.3]
- PSUIM5 guess_tau = 0.298 at its upper bound [0.01, 0.3]
- PSUIM6 ndt = 0.0032 at its lower bound [0, 0.8]
- PSUIM6 a = 9.49 at its upper bound [0.3, 9.5]
- PSUIM7 sv = 2.99 at its upper bound [0, 3]
