"""Shared style, data loading and saving for the paper figures.

Provisional layout: 180 mm full width (no journal chosen yet). Colours are Okabe-Ito; rigs are also told apart by
marker (UCLA circles, UW squares) so colour is never the only cue.
"""

from datetime import date
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.build_ddm_inputs import scheduled_pulse

MM = 1 / 25.4
FULL_WIDTH = 180 * MM
OUT_DIR = Path(__file__).resolve().parents[2] / "dissemination" / "paper" / "figures"
PROCESSED = Path(dir_config.data.processed)

RIGS = ("ucla", "uw")
RIG_LABEL = {"ucla": "UCLA", "uw": "UW"}
# Keep experimental-site colours distinct from stimulus direction throughout the
# final figure set.  Direction uses the Okabe-Ito vermillion/blue pair; sites use
# green/purple and always retain different markers.
RIG_COLOR = {"ucla": "#009E73", "uw": "#CC79A7"}
RIG_MARKER = {"ucla": "o", "uw": "s"}
RIGHT_COLOR = "#D55E00"
LEFT_COLOR = "#0072B2"
NEUTRAL_COLOR = "#4D4D4D"
TIMING_LABEL = {1: "Early", 2: "Middle", 3: "Late"}
ABS_COHERENCES = (0, 9, 18, 36, 100)

RC = {
    "font.family": "sans-serif",
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 7.5,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5,
    "legend.frameon": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "lines.linewidth": 1.0,
    "lines.markersize": 3.5,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
}


def apply_style():
    mpl.rcParams.update(RC)


def coherence_colors():
    """Sequential colours for |coherence| (light = weak, dark = strong); legends always name the level."""
    cmap = mpl.colormaps["viridis_r"]
    return {c: cmap(0.15 + 0.8 * i / (len(ABS_COHERENCES) - 1)) for i, c in enumerate(ABS_COHERENCES)}


def load_trials():
    """Responded (0.3-5 s) and censored (no response by 5 s) trials, with the scheduled pulse condition.

    `sched_pulse_type` = sign(pulse coherence) x onset bin (1 early, 2 middle, 3 late), 0 if no pulse was scheduled.
    Preprocessing's `pulse_type` is not used: it is set to 0 when the response came before the pulse ended.
    """
    valid = pd.read_csv(PROCESSED / "valid_data.csv").assign(censored=False)
    censored = pd.read_csv(PROCESSED / "censored_trials.csv").assign(censored=True)
    data = pd.concat([valid, censored], ignore_index=True)
    data["sched_pulse_type"] = scheduled_pulse(data)
    data["abs_coherence"] = data["signed_coherence"].abs()
    return data


def mouse_mean_sem(table):
    """Mean and SEM across mice (rows = mice); NaN where fewer than 2 mice contribute."""
    n = table.notna().sum(axis=0)
    mean = table.mean(axis=0)
    sem = table.std(axis=0, ddof=1) / np.sqrt(n)
    return mean.where(n >= 2), sem.where(n >= 2), n


def label_panel(ax, letter, x=-0.28, y=1.08):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom", ha="left")


def save(fig, stem):
    """Write <stem>_<date>.pdf/.png; never overwrite (adds _v2, _v3, ... if that date's files exist)."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = f"{stem}_{date.today().isoformat()}"
    name, k = base, 1
    while any((OUT_DIR / f"{name}.{ext}").exists() for ext in ("pdf", "png")):
        k += 1
        name = f"{base}_v{k}"
    for ext in ("pdf", "png"):
        fig.savefig(OUT_DIR / f"{name}.{ext}", dpi=600 if ext == "png" else None)
    print(f"saved {OUT_DIR / name}.pdf/.png")
    return OUT_DIR / name


def save_publication(fig, stem, dpi=300):
    """Write versioned PDF/SVG/PNG exports for publication figures.

    The vector files retain editable text/lines; the PNG is a 300-dpi review
    rendering.  A common basename is reserved across all three formats.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = f"{stem}_{date.today().isoformat()}"
    name, k = base, 1
    while any((OUT_DIR / f"{name}.{ext}").exists() for ext in ("pdf", "svg", "png")):
        k += 1
        name = f"{base}_v{k}"
    for ext in ("pdf", "svg", "png"):
        fig.savefig(OUT_DIR / f"{name}.{ext}", dpi=dpi if ext == "png" else None)
    print(f"saved {OUT_DIR / name}.pdf/.svg/.png")
    return OUT_DIR / name
