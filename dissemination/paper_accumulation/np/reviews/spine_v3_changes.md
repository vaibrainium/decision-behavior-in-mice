<!-- np-contract
stage: S1 ; section: spine_v3_changes ; agent: np-architect ; version: v1
thesis: "In mice performing a reaction-time random-dot motion task, a bounded accumulator with drift variability and fast guesses predicted held-out control-trial choices and response times better than a tested rapid-forgetting model, in a comparison that rarely favored the accumulator when the rapid-forgetting model generated the data."
claims: C001, C002, C004, C005, C006, C007, C008, C009, C010, C011, C013, C014, C015
numbers: N006, N018, N019, N020, N021, N083, N095, N105
sources: none
-->
# Spine v2 -> v3 changes (2026-10-27)

No analysis was run. All claims stay `proposed`. The spine is not locked.

## D002 (G1 answers, route c)
| Item | Change |
|---|---|
| 1 Route (c) | Temporal weighting removed from THESIS_A, THESIS_B and THESIS_B-rate and from title options. Moved to a secondary Challenge question, H4 (secondary), C009/C010, Figure 6 and Discussion D3/D5. Scope line added: not in title or abstract headline. |
| 2 F1a rule | Rule fixed in D002 copied inside the lock as the THESIS selection rule: k <= 2 -> THESIS_A (active line); k >= 5 -> THESIS_B; k = 3-4 -> THESIS_B-rate with {k}. Precondition added: the responded-only refit must still favor the accumulator, else G1 reopens. New claim C015 and Figure 3D. Old conditional-thesis table (F1b/F1c rows) deleted: D002 item 4 runs no analysis beyond the refits. |
| 3 Mislabeled trials | Superseded by D003: the 48 trials all lack a response and drop out. Key-control caveat (ii), glossary note and Methods promise on the 38 trials removed. |
| 4 Other analyses | F1b, F1c, M3, M5 dropped from the spine. H5 kept as open, partly tested by F1a. Figure 2 status no longer conditional on F1c. |
| 5 Kernel | Left as a G1 option (open items); C013 marked G1 OPTION and pending re-run if included. |
| 6 Scheduled | "Scheduled" throughout; the provenance condition for "randomized" is dropped; scope bars "randomized". |
| 7 Figure 2 | A-C main (model input); D-E to Figure 2-figure supplement 1. |
| 8 Title | Options below. |

## D003 (responded trials only, 0.3-5 s)
| Change | Where |
|---|---|
| Responded-trial rule and conditional likelihood stated in Action 1 and 3, Key control (i)-(ii), glossary ("responded trial", "held-out control score", "control trial"), first scope line, Methods promise. | spine |
| Removed: glossary "no response by 5 s"; Figure 1 panel E (P(no response)); Figure 5 cumulative panel (non-responder denominators); gate 3 (censored fraction) and every no-response coverage panel in Figure 6; "censoring" from H5 predictions; N006 kept only as the Methods exclusion count; N058, N100, N106, N108 dropped. | spine, C002 |
| Model numbers N014-N017, N045-N050, N110-N116, N118, N026-N041, N063-N066 removed from the header and replaced by [PENDING: responded-only refit] in C004, C005, C006, C009, C010, C011, C014. Also treated as pending (same pipeline): N042-N044 (pulse gains, revised zero-coherence prediction), N024/N025/N097 (strategy sensitivity, re-run in amendment 9 item 6). | claims |
| Pulse contrast: C008 now cites the responders-only re-estimate (about 7.5 pp) by report path `/src/.agents/reports/2026-10-27-pulse-contrast-responders-only.md`; no ids invented; N051-N058 and N088 superseded. Selection caveat added to Key control and scope. | C008, spine |
| Point 3: scope states it is a responded-only sensitivity re-analysis of a closed procedure (amendment 9) with the original results reported side by side; glossary "sensitivity re-analysis"; Figure 6 supplement carries the original results. | spine, C009-C011 |
| Relative wording kept; "4/10 did not distinguish" retained only as a superseded-fit fact in the Resolution, with counts pending. | spine Resolution, C004 |

## Title options (no temporal weighting)
| # | Title | Fits |
|---|---|---|
| T1 | Mouse motion decisions are better predicted by bounded accumulation than by rapid forgetting | THESIS_A only |
| T2 | Joint choice and response-time prediction favors a bounded accumulator over rapid forgetting in mice | THESIS_A only |
| T3 | Comparing bounded accumulation and rapid forgetting in mouse reaction-time motion decisions | THESIS_A or B |

## Items not covered by D002/D003 (need an author call)
- C007 (variant recovery N018-N021) and N117 (synthetic kernel check) used the censored likelihood; not in the refit list.
- C014 (amendment 7) used censored fits; not in the refit list.
- C013 (kernel) references came from censored fits.
- The pulse response-rate check (+2.07 pp) analyses no-response as an outcome, which D003 bars.
