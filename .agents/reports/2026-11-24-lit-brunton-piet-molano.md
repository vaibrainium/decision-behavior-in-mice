# Report: Brunton 2013, Piet 2018, Molano-Mazón 2024 against the accumulation paper
Date: 2026-11-24   Agent: Claude (Opus 5.5)   Commit: 886d3d1
Plan: plans/2026-10-26-paper-accumulation-variant.md (step G: Introduction/Discussion)

## Question
How do three author-supplied papers bear on the current story (Figures 1–6, results.md), and what could we add?

## Summary
None of the three changes the core story: Figure 2/3 favours accumulation, and pulses have a lasting directional effect. Brunton 2013 is cited in the spine for more than it shows. It tests burst- and precedence-detector regimes of one model, not a separate snapshot or extrema model. Its click-depression model is the closest precedent for our divisive front end, and it suggests a mechanistic reading of the Figure 4C onset-stage decline. Piet 2018 gives the method for calibrating the descriptive Figure 4D exponential (τ = 1.11 s) against simulations with known leak, and gives the normative argument against leak in a stationary task. Molano-Mazón 2024 mainly supports Discussion points: the action-initiation process as an alternative to fast guesses, tachometric curves, and a history-based starting point.

## Sources read (VERIFIED: full text read)
- Brunton, Botvinick & Brody 2013, Science 340:95, doi 10.1126/science.1233912. Main text and supplement were supplied as PDFs by the author.
- Piet, El Hady & Brody 2018, Nat Commun 9:4265, doi 10.1038/s41467-018-06561-y, PMC6189050. Europe PMC full-text XML.
- Molano-Mazón et al. 2024, Nat Commun 15:10583, doi 10.1038/s41467-024-53586-7, PMC11618783. Europe PMC full-text XML; code on GitHub (alexgarciaduran/rapid-updating-of-movement-by-evidence), data at osf.io/794vk.
- Extracted text is in the session scratchpad only, which is not durable. Re-fetch from Europe PMC with the PMCIDs above.

## Findings
- VERIFIED: Brunton Fig. 2A and Fig. S4 compare accumulator, burst-detector (λ = −20, B = 2), precedence-detector, leaky and unstable regimes of one 9-parameter model. They do not fit a snapshot or extrema model. The spine sentence "integration favored over extrema or snapshot models in rats (brunton2013rats, hyafil2023temporal)" should lean on Hyafil for extrema/snapshot.
- VERIFIED: Brunton rats have |λ| = 0.91 ± 0.15 s⁻¹ (mean ± SE), with σa² ≈ 0 in 13/19. The restricted σa² = 0, B → ∞ model wins on AIC in 15/19 rats. Depression is strong: φ = 0.17 ± 0.021, and τφ = 0.080 ± 0.024 s in the text (the Fig. 2 caption says 0.040 s, which is inconsistent). Across-stream adaptation fits better than within-stream adaptation (Fig. S18). The reverse-correlation kernel is flat. The task is fixed-duration and the analysis uses the longest quartile of trials.
- VERIFIED: Brunton Fig. S1. Without a stereo first click, rats used a first-click strategy and did better on the shortest trials. Brunton S2.3.8 reports that the onset kernel is slightly weaker in data than in the model. Our PSUIM6/7 deviate in the opposite direction, with excess early sensitivity.
- VERIFIED (code): our norm front end, x' = x / (1 + fe_beta · p), has p a causal low-pass of |x| that starts at 0 at stimulus onset (`src/ddm/simulator.py` front_end_numpy). It is a continuous, across-direction divisive analogue of Brunton's depression, with C starting unadapted. Early pulses therefore meet lower normalization than later pulses. Fitted fe_tau is 0.75 s in PSUIM7 (fe_beta 19.93, at the bound of 20) and 0.80 s in PSUIM6 (fe_beta 4.4), per plans/2026-11-20-transient-channel.md. That is about 10× slower than Brunton's click recovery.
- VERIFIED: Piet 2018. The optimal leak is set by the hazard rate and by noise on each sample, and is 0 when h = 0. Rats trained on the static task have small λ. Simulated linear-leak agents recover λ from an exponential fit to the reverse-correlation kernel (Fig. 3c–d).
- VERIFIED: Molano-Mazón 2024. A PSIAM model in which an independent action-initiation diffusion produces express responses. The prior enters as a starting-point offset taken from a history GLM. There are an afferent delay and two read-outs. Fitting uses MNLE and PyBADS. They report that rats used only about 100 ms of stimulus.
- INTERPRETATION: our Figure 3D conditional accuracy is a tachometric curve in the sense of Molano Fig. 1d. Our fast-guess component (17–20% of responses < 0.6 s, near chance, per `scripts/ddm/fit_mouse_ddm.py` header) plays the role of their action-initiation process.

## Recommendations (none run)
Writing only:
1. Reword the spine/Introduction citation: Brunton for burst/precedence regimes, Hyafil for extrema/snapshot. Needs a decisions.md entry and the author's OK, because of the lock.
2. Methods: present the per-trial motion-energy input as the continuous-stimulus counterpart of trial-by-trial pulse models (Brunton, Piet). Cite Brunton's across-stream depression as precedent for normalizing by |x|.
3. Results, Figure 2B (most discrimination comes from RT): cite Brunton Fig. S4, which shows that choice and duration curves alone don't separate mechanisms.
4. Discussion:
   - Piet's normative argument: in a stationary task, forgetting has no benefit.
   - Brunton's flat fixed-duration kernel against our inconclusive RT kernel (2026-10-26 fluctuation-kernel report).
   - Molano's action-initiation process and history-offset prior as alternatives we didn't model.
   - Brunton's first-click strategy as precedent for onset-weighted behaviour in PSUIM6/7.

Cheap analyses (existing fits and simulator, CPU, no Hyak):
5. Calibrate the Figure 4D exponential (Piet Fig. 3c–d and Brunton Fig. S9 logic). Simulate the accumulator at fixed known leak (for example 0, 0.5, 1, 2, 5 /s) with each mouse's other fitted parameters and actual schedules. Apply the exact γT plus exponential readout, then plot readout τ against generative λ. This shows whether τ = 1.11 s (0.45–3.73) bounds leak at all. A zero-leak model already declines (results.md), so the mapping may be flat. If it is, that is a clean, reportable non-identifiability.
6. Adaptation account of the Figure 4C onset-stage decline. From the fitted norm front end, compute the effective gain 1/(1 + fe_beta · p) at the early, middle and late pulse onsets on each mouse's actual inputs. Compare it with each mouse's observed stage pattern (descriptive, n = 10). This links the Brunton mechanism to the PSUIM6/7 deviation without new fits.

New fits (need the author's approval and Hyak; lower priority):
7. Per-sample multiplicative sensory noise (Brunton σs) in place of across-trial sv. Partly covered already: the iid evidence-gain pilot in reports/2026-11-14-history-state-gain.md reduced the PSUIM7 RT loss but missed early pulse amplitude. Wait for the transient-channel fits (plans/2026-11-20-transient-channel.md), which already test a fast change-sensitive input.
8. History-based starting-point offset (Molano) in the control model. Serial bias is documented (2026-11-14 report). This is likely a Discussion limitation rather than a new fit.

Not recommended:
- Brunton's within-group duration test for σa. In an RT task the animal chooses the duration, so it is confounded.
- MNLE. Our likelihood is already tractable.
- Movement vigor. No kinematics are recorded.

## Caveats
Recommendations 5 and 6 are descriptive and underpowered (10 mice). Mice must not be split or interpreted by rig location. Brunton numbers are from rats and humans on auditory and visual click tasks with fixed durations, so they are not directly comparable with RT motion decisions in mice.

## Open questions and next steps
- [ ] Author: approve the spine rewording (item 1)?
- [ ] Author: run item 5 and/or item 6?
- [ ] Add Piet 2018 and Molano-Mazón 2024 to evidence/reference_metadata.json after a DOI check.
