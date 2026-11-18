# Panel A alternatives

1. Dual axes: blue circles/solid line show equal-mouse mean total five-fold held-out LL (left, higher better; LL = −NLL); orange squares/dashed line show mean full-training QMLE-based BIC (right, lower better). Both include the same 10 mice. The axes have independently labeled nonzero ranges and different units; curve intersections/vertical alignment have no meaning. These are distinct test and training scores, not BIC calculated from the plotted test NLL.

2. Separate subpanels: left shows equal-mouse mean held-out joint choice/RT quantile log score in bits/trial (higher better); right shows the same absolute BIC as alternative 1 (lower better). Bits here are the existing joint score converted by −NLL/(n_test ln2), not choice-only information gain over a bias baseline.

Both alternatives: categorical means joined as visual guides, no error bars or significance tests. Existing seed-averaged independent training scores used for BIC; same QMLE approximation and caveats as earlier previews. No new fits or score evaluations. Publication styling is provisional.
