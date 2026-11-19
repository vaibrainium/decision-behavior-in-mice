# Corrected finite-sample factor: current ordinal mouse-ID inference

All fitted parameters and point estimates unchanged. Frequency weights represent individual trials, so CR1 uses total trial count rather than count of grouped cells: G/(G-1)*(N_trials-1)/(N_trials-K). This preserves covariance under equivalent frequency aggregation. Prior observed_hessian_inference/ retained for provenance; source_initial_inference.py preserves its original code.

Restricted ordinal WLS alpha omnibus Holm2p=2.625942499746293e-05;beta=0.09195426886830577. Directional alpha conclusion unchanged; beta/timing decline still inconclusive. Cluster jackknife unchanged. Current files in this directory supersede earlier covariance-based p values only. No fit or Figure4 change.

Reproduce: `.venv/bin/python -m scripts.paper.refine_mouse_fixed_effects_inference --source dissemination/paper_accumulation/draft_2026-11-15/pulse_time_mouse_fixed_effects_2026-11-18 --output <new-directory>`.
