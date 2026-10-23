"""Frozen analysis contract for the exploratory pulse follow-up (package A, plan section A4).

Every choice below was fixed from metadata, task configuration and the plan, before any new pulse effect estimate
was computed. Downstream stages read the written analysis_config.json through io.load_config and must not redefine
these choices. A change requires a new CONFIG_VERSION, a dated plan Log line and explicit invalidation of the
affected outputs.

None of this transfers to the closed primacy procedure (primacy-analysis-plan.md, amendment 6 item 8).
"""

CONFIG_VERSION = 2  # v1 runs 20261023T190856Z/191004Z_fa8de8b superseded before release (no signs_scheduled_symmetric)
MASTER_SEED = 20261023

DEADLINE_S = 5.0  # analytical deadline of the DDM inputs; responses after it are censored at it
MIN_VIEWING_S = 0.3  # task rule in both rigs: no response is registered before 0.3 s
FRAME_RATE = 60
UW_ONSET_FRAMES = {3: "early", 14: "middle", 25: "late"}  # UW task configs, `pulse_onset` (frames of 1/60 s)
UCLA_ONSET_BOUNDARIES_S = [0.16, 0.32]  # existing onset-bin boundaries (build_ddm_inputs.PULSE_BINS_S)
STRATUM_NAMES = ["early", "middle", "late"]

CONFIG = {
    "config_version": CONFIG_VERSION,
    "status": "exploratory",
    "closed_procedure_note": "The original primacy procedure is closed under amendment 6 item 8. Nothing here reopens "
    "or retunes it; retrospective CV does not restore confirmatory status.",
    "units": {
        "coherence": "signed nominal coherence in percent (positive = rightward), column coherence_pct",
        "time": "seconds from stimulus onset (fixation offset); UW raw response_time + 0.3 s min viewing",
        "choice": "response_side: 'R', 'L' or 'none' (no response by the deadline)",
        "probabilities": "contrasts reported in percentage points",
    },
    "deadline_s": DEADLINE_S,
    "min_viewing_s": MIN_VIEWING_S,
    "frame_rate": FRAME_RATE,
    "censoring": {
        "rule": "Trials with no response by 5 s (recorded RT > 5 s or no response) are unresponded at the deadline "
        "(event = 0, follow-up = 5 s). censored_trials.csv reaction_time = 5 is a replay placeholder and is never an "
        "event. The recorded late RT is kept in rt_recorded_late_s for reference only.",
        "competing_events": "A left response is a competing event for a right response (and vice versa), never "
        "independent censoring. Administrative censoring only at the 5 s deadline.",
    },
    "scheduled_assignment": {
        "rule": "pulse_category from the scheduled pulse, never from the RT-dependent pulse_type column. "
        "'positive'/'negative' = scheduled pulse whose coherence differs from the base coherence, by the sign of the "
        "pulse coherence (rightward = positive). 'pulse_direction_unknown' = UCLA 0% pulse on a trial without any "
        "response (direction not recoverable; excluded from signed arms). 'null_pulse' = scheduled UCLA pulse whose coherence equals the base "
        "(same-sign 100% pulse on a 100% stimulus): no physical change. 'control' = no scheduled pulse. UW records "
        "same-sign 100% pulses identically to controls, so at |coherence| = 100 UW 'control' may contain null pulses.",
        "pre_onset_responses": "Retained in the assignment (all-scheduled) analysis.",
    },
    "analysis_sets": {
        "ddm_retained": "in_ddm_input: the 30,030 retained DDM input trials (responded 0.3-5 s plus censored), default "
        "set for comparability with the existing models.",
        "primary_coherence": "ddm_retained & abs(coherence_pct) <= 36 (new exploratory design choice; not transferred "
        "to the historical protocol)",
        "sensitivity_all_coherences": "ddm_retained, all coherences. At |coherence| = 100 one scheduled sign is "
        "physically null (UCLA) or recorded as control (UW); the common-support rule then drops UW 100% cells and "
        "UCLA 100% cells compare a genuine opposite pulse with a null pulse. Report separately.",
        "sensitivity_zero_coherence": "ddm_retained & coherence_pct == 0 (contains seed-specific hidden coherence)",
        "broader_behaviour": "not defined; needs its own ID and exclusion ledger if used",
    },
    "strata": {
        "cell": ["mouse", "session", "coherence_pct", "onset_stratum"],
        "uw_onset_stratum": {"source": "scheduled onset frame (task config, assigned before the trial)", "frames": UW_ONSET_FRAMES},
        "ucla_onset_stratum": {
            "source": "recorded BurstTime of displayed pulses, binned at the existing 0.16/0.32 s boundaries",
            "boundaries_s": UCLA_ONSET_BOUNDARIES_S,
            "provenance": "scheduled_category_measured_time: the task draws burst time before the trial from N(60, 15) "
            "or N(240, 15) ms (RDK-Task Burst_Experiment.py); the recorded onsets form the two matching separated "
            "clusters, so the cluster is the scheduled category. Within a category the exact scheduled draw is not "
            "logged; recorded times include stimulus-loop latency. Named early/middle to align with the existing "
            "sched_pulse_type codes (UCLA 240 ms ~ UW middle 233 ms).",
        },
        "controls": "UW controls have a recorded scheduled sham onset. UCLA controls have none; they receive a "
        "pseudo-onset (control_alignment) and their stratum is derived from it.",
    },
    "weighting": {
        "rule": "Within each mouse, keep cells with >= 1 positive and >= 1 negative genuine pulse; weight each cell by "
        "min(n_positive, n_negative) and normalize the weights to sum to 1 within the mouse. Mice are then weighted "
        "equally. This estimates the effect on an explicit common-support population, not on all trials. No "
        "outcome-driven merging of sparse cells.",
        "pulse_vs_control": "Same rule with control in place of the opposite sign, on cells matched by the control "
        "onset stratum (recorded sham onset for UW, pseudo-onset stratum for UCLA), restricted to "
        "signs_scheduled_symmetric so that positive-vs-control and control-vs-negative describe the same population.",
        "uw_asymmetric_schedule": "In every UW session one |coherence| (18% in 12 sessions, 36% in 6) schedules only "
        "rightward middle/late pulses and late shams (task config). Those cells have no negative arm: they drop out of "
        "positive-vs-negative contrasts by the support rule and are excluded from pulse-vs-control contrasts. They may "
        "be shown descriptively, labelled.",
    },
    "estimands": {
        "per_mouse": {
            "Delta_R": "P(R by 5 s | positive) - P(R by 5 s | negative), cell-standardized",
            "Delta_L": "P(L by 5 s | positive) - P(L by 5 s | negative)",
            "Delta_unresponded": "P(none by 5 s | positive) - P(none by 5 s | negative)",
            "Delta_direction": "(Delta_R - Delta_L) / 2, percentage points; primary endpoint. Not accuracy and not the "
            "fraction of right choices among responders. Delta_R + Delta_L + Delta_unresponded = 0.",
        },
        "group": "Unweighted mean of per-mouse endpoints (mice weighted equally).",
    },
    "inference": {
        "primary_interval": "two-sided 95% Student-t interval across per-mouse estimates (df = n_mice - 1)",
        "sensitivity": ["mouse-level bootstrap (10,000 resamples, percentile)", "leave-one-mouse-out estimates"],
        "bootstrap_resamples": 10000,
        "multiplicity": {
            "family": ["primary Delta_direction (positive vs negative)",
                       "Delta_direction positive vs timing-matched control",
                       "Delta_direction timing-matched control vs negative"],
            "correction": "Holm",
            "note": "Other stratified results are descriptive with pointwise intervals. Record which family members "
            "were estimable.",
        },
        "forbidden_adjustments": ["realised RT", "post-pulse ME", "trial-average ME that contains the pulse"],
        "responder_only_logistic": "optional, secondary, always next to response probabilities, with selection caveat",
    },
    "control_alignment": {
        "uw": "recorded scheduled sham onset (pulse_onset on control trials; pulse_coherence == base coherence)",
        "ucla": "one pseudo-onset per control trial: a draw, with a fixed seed, from the recorded onsets of scheduled "
        "pulse trials (positive, negative or null) in the same mouse x session x abs(coherence); if that pool has "
        "fewer than 5 onsets, from the same mouse x session at any coherence. Uses no outcome of any trial.",
        "seed": MASTER_SEED,
        "sensitivity_seeds": [MASTER_SEED + k for k in range(1, 6)],
        "min_pool": 5,
        "note": "Pseudo-onset seeds are a sensitivity, never extra observations. Package D (D1) confirms or proposes a "
        "versioned change before viewing contrasts.",
    },
    "time_grid": {
        "stimulus_clock_s": {"start": 0.0, "stop": DEADLINE_S, "step": 0.01},
        "since_onset_s": {"start": 0.0, "stop": 4.58, "step": 0.01,
                          "note": "each trial is followed for at most 5 s - onset; use a common supported range per "
                          "comparison (UW late onset 0.41675 s leaves 4.583 s)"},
    },
    "causal_language": "Set by the assignment audit (assignment_verdict in this file). Without verified randomized, "
    "unannounced assignment, describe adjusted associations.",
    "output_schema": {
        "per_mouse_table": ["analysis_set", "contrast", "mouse", "rig", "n_cells", "n_trials_pos", "n_trials_neg",
                            "Delta_R", "Delta_L", "Delta_unresponded", "Delta_direction"],
        "group_table": ["analysis_set", "contrast", "n_mice", "estimate", "ci_low", "ci_high", "method", "p_value",
                        "p_holm"],
        "curves": ["analysis_set", "comparison", "onset_stratum", "arm", "mouse", "t", "cif_R", "cif_L", "survival",
                   "n_at_risk"],
    },
}
