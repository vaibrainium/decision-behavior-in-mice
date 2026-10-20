"""Write processed/censored_trials.csv: trials with no response by 5 s, for the DDM's censored outcome.

valid_data.csv keeps responses at 0.3-5 s. In the same accepted sessions, non-correction trials with RT > 5 s (the
stimulus kept running, 25-60 s) or no response at all are taken from aggregate_data.csv. They get
reaction_time = 5 (the stimulus is replayed for 5 s, as for every DDM trial), the recorded RT in censored_rt, and an
agg_code built from their row in aggregate_data.csv (idx_valid_trial is not unique for non-accepted trials).

Next: replay their motion energy with
    python -m scripts.compute_motion_energy_full --trials censored_trials.csv --out-dir motion_energy_mouse_censored
then python -m scripts.ddm.build_ddm_inputs.

Usage: python -m scripts.ddm.make_censored_trials
"""

from pathlib import Path

import pandas as pd

from config import dir_config

CENSOR_AT = 5.0


def main():
    processed = Path(dir_config.data.processed)
    aggregate = pd.read_csv(processed / "aggregate_data.csv")
    valid = pd.read_csv(processed / "valid_data.csv")
    sessions = pd.MultiIndex.from_frame(valid[["subject_id", "session_id"]].drop_duplicates())
    in_valid_session = pd.MultiIndex.from_frame(aggregate[["subject_id", "session_id"]]).isin(sessions)
    no_response_by_censor = aggregate.reaction_time.isna() | (aggregate.reaction_time > CENSOR_AT)
    censored = aggregate[in_valid_session & ~aggregate.is_correction_trial.astype(bool) & no_response_by_censor].copy()
    censored["agg_code"] = censored.subject_id + "_" + censored.session_id.astype(str) + "_censored" + censored.index.astype(str)
    assert censored.agg_code.is_unique and not censored.agg_code.isin(valid.agg_code).any()
    censored["censored_rt"] = censored["reaction_time"]
    censored["reaction_time"] = CENSOR_AT
    censored.to_csv(processed / "censored_trials.csv", index=False)
    print(f"{len(censored)} censored trials ({censored.data_source.value_counts().to_dict()}) -> {processed / 'censored_trials.csv'}")


if __name__ == "__main__":
    main()
