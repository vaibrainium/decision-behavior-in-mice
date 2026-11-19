# Direction × ordinal pulse-time interaction

Current preview: all_available_10_direction_interaction.png/pdf/svg. This unpacks the author-preferred ordinal model into left/right full alpha offsets, using the same fitted coefficients, trials, covariance and existing slope test. No refits or new exclusions.10 mouse baselines, late trials only6 mice. Matched6 and early/middle10 companions retained.

A_m(d,t)=u_m+aP+aT*(t−2)+d*(w0+wT*(t−2)) on pulse trials. Plotted alpha uses mean mouse baseline and full additive coherence-offset convention. Left slope=aT−wT=+3.046159/stage; right slope=aT+wT=−7.755207/stage. Their difference=2*wT=−10.801366,95%cluster-t9CI[−19.693530,−1.909203],p.022556. Same interaction already tested by prior directional-influence slope wT; doubling coefficient and SE leaves t/p unchanged. Existing jackknife p.044027. Do not count this as a new independent result.

Bands are pointwise95% mouse-cluster intervals, not SEM. Points/lines are fitted ordinal model estimates, not raw observations. Full alpha offsets are not necessarily P(right)=.5 thresholds. Alpha direct values shown without subtracting control, consistent author preference. Beta change values exported descriptively, with no additional test. Matched6 interaction remains inconclusive; full model assumes shared pulse/slope/asymptote terms across cohorts.

Sources: direction_curves.csv, direction_slopes.csv, interaction_test.csv, manifest.json and verification.json. Checked half(left/right offset difference) equals original selected w curve, and interaction p equals original slope p.

Reproduce in fresh output:
`.venv/bin/python -m scripts.paper.plot_pulse_time_direction_interaction --source dissemination/paper_accumulation/draft_2026-11-15/pulse_time_ordinal_2026-11-18 --output <new-directory>`
