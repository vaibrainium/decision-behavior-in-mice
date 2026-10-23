"""Reusable checks for the pulse follow-up validation harness (package G). Pure functions; no I/O."""

import numpy as np
from scipy import stats

TOL = 1e-9


def binom_ci(k, n, level=0.95):
    """Clopper-Pearson (exact) interval for a Monte Carlo rate k/n."""
    if n == 0:
        return np.nan, np.nan
    ci = stats.binomtest(int(k), int(n)).proportion_ci(confidence_level=level, method="exact")
    return float(ci.low), float(ci.high)


def components_sum_to_zero(pm):
    """C per-mouse table: Delta_R + Delta_L + Delta_unresponded = 0 (percentage points)."""
    if pm is None or len(pm) == 0:
        return False
    return bool(np.all(np.abs(pm.Delta_R + pm.Delta_L + pm.Delta_unresponded) < 1e-9))


def cif_checks(cur, summary):
    """D per-mouse curves (one summary): CIF nondecreasing, values in [0, 1], CIF_R + CIF_L + S = 1, and zero
    response mass at onset for the onset-eligible summary."""
    keys = ["arm", "mouse"]
    s = cur.sort_values(keys + ["t"])
    g = s.groupby(keys)
    mono = bool((g.cif_R.diff().fillna(0) >= -TOL).all() and (g.cif_L.diff().fillna(0) >= -TOL).all())
    v = s[["cif_R", "cif_L", "survival"]].to_numpy()
    unit = bool(((v >= -TOL) & (v <= 1 + TOL)).all())
    ident = float(np.abs(s.cif_R + s.cif_L + s.survival - 1).max())
    out = {"cif_nondecreasing": mono, "in_unit_interval": unit, "identity_max_err": ident, "identity_ok": ident < TOL}
    if summary == "onset_eligible":
        z = s[s.t == 0]
        out["eligible_zero_mass_at_onset"] = bool(((z.cif_R + z.cif_L).abs() <= TOL).all())
    return out


def pre_onset_unaffected(base_side, base_rt, side, rt, onset, sign):
    """Responses before onset, and every trial without a signed pulse, keep their base outcome exactly."""
    pre = ~np.isnan(base_rt) & (base_rt < onset)
    keep = pre | (sign == 0)
    same_side = np.all(base_side[keep] == side[keep])
    same_rt = np.all((base_rt[keep] == rt[keep]) | (np.isnan(base_rt[keep]) & np.isnan(rt[keep])))
    return bool(same_side and same_rt)


def censoring_ok(side, rt, deadline):
    """No event after the deadline; 'none' exactly when no RT; responded RTs within (0, deadline]."""
    none = side == "none"
    return bool(np.all(none == np.isnan(rt)) and np.all(rt[~none] <= deadline + 1e-12) and np.all(rt[~none] > 0))
