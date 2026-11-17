# Report: Basso RT display precedents
Date: 2026-11-17   Agent: Codex   Commit: ffc97d1 (base; current figure edits uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Author accepts Figure 1C; how should D display mean RT, informed by Michele Basso papers?

## Summary
Focused narrative lookup, not an exhaustive review. The closest verified template is Jun et al. 2021, DOI 10.1038/s41593-021-00878-6. Primary captions/full text and published Figure 2/5 renders inspected. Recommend signed-coherence chronometric means with subject-level uncertainty. Current D contains means of mouse medians and is not a mean-trial-RT display. No artwork or statistics changed in this lookup.

## Findings
- VERIFIED: Jun Figure 2g–h shows correct-trial mean RT by signed coherence with separate linear fits on each side; individual experiment traces are faint and pooled summaries prominent. Figure 5s–t/w–x separates correct and error mean RTs and overlays HDDM predictions. Source: public Europe PMC fullTextXML, fig IDs F2 and F5, and publisher image renders below.
- VERIFIED: the inspected caption does not define SEM error bars for those RT panels; do not invent an uncertainty definition for their figure.
- VERIFIED: Crapse, Lau and Basso 2018 DOI 10.1016/j.neuron.2017.12.006 identified/read through indexed primary text; its main emphasis is criterion manipulation, not the best RT template here. No claim to inspecting all Basso publications.
- RECOMMENDATION: D should use within-mouse arithmetic means of retained control RTs, then an unweighted mean and SEM across mice. Use signed coherence aligned with C, correct/error markers and clear line conventions. A correct/error split is an alternative if one panel becomes crowded. Keep zero coherence separately labeled; no correctness assignment inferred from physical coherence.
- RECOMMENDATION: descriptive connecting lines need explicit caption identification; smooth lines should come from an identified model, not arbitrary cosmetic fitting. No assumption of a peak or symmetry is warranted before computing means.
- RECOMMENDATION: individual-mouse summaries remain available alongside a cleaner main display. This differs from pooling experiments in the example source; animal remains the group inference unit.

## What didn't work
Broad searches returned unrelated Basso names and swimming results; those were discarded. Direct PMC open triggered a browser challenge and direct Nature article/figure HTML was inaccessible; Europe PMC full text and publisher image endpoints succeeded. No external AI service or unpublished-data upload.

## How to reproduce
Search date 2026-11-17. Relevant successful discovery query: `"Causal role for the primate superior colliculus"`; companion query `"A Role for the Superior Colliculus in Decision Criteria" PMC`. Read https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8338902/fullTextXML and inspect fig elements F2/F5. Public XML retrieved at /tmp/basso-jun2021.xml during review. Render URLs:
- https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41593-021-00878-6/MediaObjects/41593_2021_878_Fig2_HTML.png
- https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41593-021-00878-6/MediaObjects/41593_2021_878_Fig5_HTML.png
Primary records: https://pmc.ncbi.nlm.nih.gov/articles/PMC8338902/ and https://pmc.ncbi.nlm.nih.gov/articles/PMC7266089/.
Current D source: draft_2026-11-15/figure1_revision_2026-11-17_v2/source_data/fig1_D_rt_mouse.csv and scripts/paper/build_paper_2026_11_15.py figure1.

## Caveats
This is a plotting-precedent lookup, not an endorsement of the source's inferential unit or a new analysis. Full mean RTs cannot be reconstructed from saved medians. The existing response window and accepted-session selection must be retained and disclosed. Main manuscript Word packet and HTML viewer are older than the current static export.

## Open questions and next steps
- [x] Recompute control mean RTs from retained trial-level data if adopting the recommendation.
- [x] Preview signed-coherence correct/error mean RT layout; retain C as author accepted.

## Implemented preview after author authorization
2026-11-17: Author requested trying the recommendation. Export: dissemination/paper_accumulation/draft_2026-11-15/figure1_revision_2026-11-17_v3/. D now shows within-mouse arithmetic mean control RTs by signed coherence/outcome, then equal-mouse mean ± SEM. Correct circles and error squares use descriptive solid/dashed connecting lines separately on either side of zero; zero coherence is a separate diamond. Main panel omits individual traces; all mouse summaries are exported. C data and fitted curves remain numerically identical to the approved v2. Caption/Methods/figure-linked Results updated; prior versions preserved. No new inferential test or decision-model fit. Render visually inspected.

VERIFIED: same 14,015 controls/10 mice as C; filter exactly agrees with the original scheduled_pulse function. Existing minimum of 10 trials per mouse/coherence/outcome cell retained. Splitting by signed coherence makes 10 error cells (67 trials) ineligible for the display; these remain in the source data. Correct/zero points include 10 mice; error points include 7–10. Group means and SEM independently checked from exported subject summaries. Source: v3/verification.json and source_data/fig1_D_rt_mouse.csv / fig1_D_rt_group.csv. Base commit ffc97d1, current edits uncommitted.

Reproduce: `.venv/bin/python -m scripts.paper.review_figure1 --output <fresh-directory>`. Trial input /mnt/data/processed/valid_data.csv is hashed in figure_manifest.json. The older HTML viewer and packaged Word draft have not been refreshed. Next: author assess preview and select or adjust D.

## Choice-direction revision
2026-11-17 author requested left/right choices instead of correct/error. Current export is figure1_revision_2026-11-17_v4. D groups recorded choice 1 (right) versus 0 (left), including zero coherence in both series. Orange solid circles and blue dashed squares match physical direction colors elsewhere. Verified all exported mouse means against the trial-level choice subsets, subject mean/SEM calculations, total control count, and unchanged C data/fit exports. Source: v4/verification.json and fig1_D_rt_*.csv. Right-choice points include 8–10 mice; left-choice points 7–10 under the existing minimum of 10 trials per cell. No new statistical inference. Render inspected. Caption, Methods and descriptive Results updated. Reproduce with scripts.paper.review_figure1 and a fresh output directory. Older exports and Word/HTML packets preserved. Author assessment pending; base commit ffc97d1.

## SEM shading revision
2026-11-17: Author requested solid RT traces and translucent SEM bands. Export figure1_revision_2026-11-17_v5 uses solid lines for both choices, keeps observed markers, and replaces error bars with pointwise mean ±1 SEM shading (alpha 0.18), linearly interpolated between sampled coherences. This is not a simultaneous confidence band. VERIFIED: every source CSV is identical to v4; verification.json records this. Render inspected. Caption/Methods updated. Reproduce with the same review_figure1 command and a fresh output directory. Base ffc97d1; changes uncommitted. No statistical changes; earlier exports preserved.
