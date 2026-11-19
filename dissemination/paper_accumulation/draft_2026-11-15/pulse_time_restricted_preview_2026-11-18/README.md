# Restricted-trial joint-model preview

Saved joint per-mouse fits on21,725 of the author's filtered trials, with no refitting. Main all10_early_middle.png/pdf/svg uses all10 mice; same6_all_times retains6 UW mice at every time. Full additive alpha follows notebook sign convention; beta is relative to each mouse control slope. Mean±SEM across mice, all mice retained. Arithmetic rechecked against source mouse coefficients. No formal contrast passes the existing Holm correction. Early alpha right-left15.6550, Holm p.26953125; middle5.7663,p1. Some fits unstable, especially DBM12; non-significance does not establish no pulse effect.

Source fits, individual diagnostics, selection accounting and original-data comparison remain separate. Data-derived source hashes and current definitions: manifest.json. Group tests copied exactly from original fit output. Existing Figure4 unchanged.

Reproduce with fresh output:
`.venv/bin/python -m scripts.paper.preview_restricted_pulse_time --source dissemination/paper_accumulation/draft_2026-11-15/pulse_time_per_mouse_joint_2026-11-18 --output <new-directory>`
