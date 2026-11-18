# Proposed Figure 3A. Direct held-out negative log likelihood

**(A)** Total held-out NLL for C, E, ES, DDMx and ESx, shown as horizontal bars separately for each mouse. Each bar sums the saved test NLLs across five cross-validation folds. Lower values indicate better prediction under this scoring procedure. The number of control trials (n) appears above each mouse; each mouse's five candidates are evaluated on the same trial count. All bars start at zero. NLL axes have independently labeled scales, and absolute levels should be compared within a mouse because trial counts and response distributions differ across mice. No reference subtraction or trial-count normalization is applied. Bar-end labels are rounded to two decimals; full-precision values accompany the artwork. No error bars or significance tests are added; cross-validation folds are not treated as independent biological replicates. These saved simulation-based scores do not quantify parameter or Monte Carlo uncertainty.

Layout inspiration: Stine et al. (2020), Figure 7B (https://doi.org/10.7554/eLife.55365), which uses subject-level horizontal bars for ΔBIC, not direct NLL. Our metric remains the author-requested raw held-out NLL.

Sources: absolute_nll.csv and fold_scores.csv; hashes/checks in figure_manifest.json and verification.json. Only A is revised; B onward remain pending author review.
