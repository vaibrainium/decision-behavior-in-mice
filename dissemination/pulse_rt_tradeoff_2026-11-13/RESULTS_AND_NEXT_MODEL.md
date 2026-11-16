# Diagnosing the likelihood and pulse response tradeoff

Date: November 13, 2026. Repository commit: `b63c9d919edc85e48446be48a8399ba6304b8df0`; new analysis scripts are uncommitted.

The next modeling question should be what supplies the RT variation currently absorbed by persistent drift variability. The exact held-out decomposition shows that this issue is concentrated in one mouse and in central portions of the RT distribution, especially correct high-coherence responses. It is not primarily a failure of the no-sv model to fit the slowest responses, and it is not a uniform requirement across mice.

[Diagnostic figure](rt_tradeoff_diagnostic.pdf).

## A matched comparison separates the components

The earlier 503.71 held-out NLL gap compared a power-law leak/urgency model with an onset-weighted linear-input model without sv. Those models differ in several respects. The existing onset-weighted models with and without sv provide a closer comparison: the presence of persistent drift variability is the changed component, while the other parameters are refitted within each family.

| Held-out comparison | Choice NLL difference | RT NLL difference | Total difference |
|---|---:|---:|---:|
| Onset weights without sv minus power/leak/urgency | -11.68 | 515.39 | 503.71 |
| Onset weights without sv minus onset weights with sv | -49.29 | 360.22 | 310.93 |
| Onset weights with sv minus power/leak/urgency | 37.61 | 155.17 | 192.78 |

Negative differences favor the first model. These are held-out scores, not the full-data rescored terms quoted in the earlier comparison. The matched no-sv model predicts choices better but loses through RTs. The remaining difference to the power/leak/urgency benchmark includes other model components and cannot all be attributed to sv.

All 150 original fold scores were reproduced exactly using the original five folds, simulation seed, repetitions, nine quantile bins, smoothing, response conditioning, and fitted parameters. RT-bin and choice contributions reconstruct the original objective. No model was refitted and no likelihood weights changed.

Sources: `fold_scores_seed12345.csv`, `cell_differences_seed12345.csv`, `rt_bin_differences_seed12345.csv`; original fit paths are stored in the cache fingerprints and script model definitions.

## The matched disadvantage is concentrated in PSUIM7

PSUIM7 contributes 280.17 of the 310.93 total held-out disadvantage of removing sv, about 90%. Without that mouse, the summed difference is 30.76; without PSUIM6 and PSUIM7 it is 22.89. These omissions are diagnostics, not a reason to exclude mice from the paper.

An independent simulation seed preserves the large PSUIM7 difference: 269.32 instead of 280.17. PSUIM6 changes from a small disadvantage of 7.87 to an advantage of 24.83 for the no-sv model. Its small score difference is therefore not numerically resolved at the working simulation resolution. Do not frame the original two-model gap as robust evidence that every mouse needs persistent drift variability.

Sources: `difference_by_mouse_seed12345.csv`, `dominant_mouse_seed_check.csv`, `diagnostic_summary.json`.

## Correct responses and central RTs drive the cost

For the matched pair, removing sv costs 226.62 RT NLL on controls and 133.60 on pulse trials. Correct-response RTs account for 292.17 of the 360.22 RT disadvantage; errors contribute 51.98 and zero-coherence responses 16.07. Baseline coherence magnitudes of 100% and 36% contribute 179.92 and 138.61 RT NLL, respectively. The no-sv model slightly improves the 18% RT score.

The RT quantiles give an especially useful diagnosis:

| RT quantile third within condition and choice | RT NLL difference, no sv minus sv |
|---|---:|
| Fastest three bins | 213.19 |
| Middle three bins | 538.70 |
| Slowest three bins | -391.67 |

Thus the no-sv model gains on the slowest quantiles but loses more in the center. The same qualitative pattern holds under the second seed in PSUIM6/7. These are relative quantiles within each scored coherence/pulse/choice cell; they do not define one common physical RT range.

The largest individual condition/choice contribution is PSUIM7's correct control responses at -100% coherence. The figure illustrates its observed RT distribution and pooled fold predictions. This condition was selected descriptively because it contributes the largest penalty, not as a new independent test. It shows that neither matched model captures every feature of the distribution, even though one has the better likelihood.

Sources: `difference_by_{trial_type,correctness,coherence,quantile}_seed12345.csv`; `rt_histograms_seed12345.csv`; `largest_matched_rt_contributions.csv`. There are no penalties from empty simulated condition cells in the reported pairwise total reconstruction.

## Check response timing and session variation before assigning a new mechanism

A further descriptive check shows session variation even within high-coherence correct controls. Among PSUIM7 sessions with at least ten responses in a signed-coherence cell, median RT ranges from 0.68 to 1.16 s at -100% and from 0.62 to 0.96 s at +100% (11 sessions for each side). The current decision fits pool sessions and use one fixed nondecision delay per mouse.

Those shifts could arise from sensory encoding, decision policy, engagement, response execution, or sampling variation. They do not measure motor latency directly. They nevertheless make a constant response-time mapping a concrete assumption to test. The pulse readout and the RT deficit should also be displayed per mouse and session, so a common mechanistic claim does not rest on an unexplained PSUIM7 pattern.

Source: `high_coherence_correct_rt_by_session.csv`, derived from the audited trial table. This is descriptive and does not establish a session effect after correction or identify its origin.

## The next focused model comparison

Keep the joint generative objective and the existing pulse readouts as complementary adequacy checks. Treating the pulse summary as an additional independent likelihood term would count the same outcomes twice. Arbitrary choice/RT weights would change the question rather than explain the discrepancy.

The first pilot should compare the current persistent additive drift-variability account with a model that allows **variable postdecision response delay**, using the same input mapping, bound dynamics, pulse weights, guesses, and trial population. Replace the sv variance parameter with one delay-spread parameter while retaining the existing mean delay parameter. A positive distribution such as a mean-preserving lognormal delay can recover the fixed-delay model when its spread is zero. It must be specified as postdecision delay; varying sensory-onset latency instead changes which time-varying evidence is accumulated and is a different model.

The motivation is that the central RT spread and session timing shifts may currently be absorbed by sv. This is a hypothesis, not a finding that response delay caused the mismatch. The pilot should start with PSUIM7, where the scoring constraint is large, and PSUIM6, where pulse sensitivity is informative but the matched sv advantage is unresolved. Refit the common parameters in each model, rather than adding delay noise at fixed parameters and treating that counterfactual as a fair model comparison.

If timing variation does not explain both constraints, a second targeted alternative is **positive gain variability**: trials differ in sensitivity to the entire evidence stream rather than receiving a persistent signed drift offset. In the current code sv enters as `g * evidence(t) + bias + sv * Z`. A gain alternative would use `g * G * evidence(t) + bias`, with positive, mean-one G and one variability parameter. The distinction predicts different relationships among coherence, RT and pulse sensitivity. It is another testable computational account, not a demonstrated sensory mechanism. Session-dependent timing/gain and history should be checked when interpreting either account.

For either candidate, the required evidence is improved prediction of the relevant RT distributions together with the sustained directional pulse profile, including both signs and the coherence sensitivity. Compare on common held-out folds and simulation seeds, inspect absolute fit, propagate uncertainty, and establish recovery against the competing mechanisms before interpreting the new parameter. These fits are proposed and were not launched in this diagnostic task.

## Reproduction

```bash
cd /src
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.diagnose_pulse_rt_tradeoff --run --collect
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.diagnose_pulse_rt_tradeoff --run --collect --mice PSUIM6 PSUIM7 --seed 23456
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.plot_pulse_rt_tradeoff
```

The second seed covers only PSUIM6 and PSUIM7; do not compare its total directly with the first seed's full-cohort total. Folds hold out trials from the same mice and sessions, not new animals. The diagnostics are exploratory and condition on existing fits; they do not propagate model-fitting uncertainty or provide new population significance tests.
