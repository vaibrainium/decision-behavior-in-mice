from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm, gridspec

# Set paths
BASE_DIR = Path(__file__).parent
STYLE_FILE = BASE_DIR / "scientific.mplstyle"

# Constants
TEXTWIDTH = 7.2  # in inches, updated for scientific standard
FONTSIZE = 12
CMAP = cm.viridis
CMAP_R = cm.viridis_r
COLORS = [CMAP(i / 4.0) for i in range(5)]


# Function to scale elements proportionally
def scale_property_to_figure(property_value, figure_size, base_size=TEXTWIDTH):
    """Scale a property value (like font size, line width, etc.) proportionally to the figure size."""
    scale_factor = figure_size[0] / base_size  # Assuming figure width is the reference size
    return property_value * scale_factor


# Seaborn setup
def setup(style_file=STYLE_FILE) -> None:
    """Apply general Matplotlib and Seaborn style and settings."""
    if style_file.exists():
        plt.style.use(str(style_file))
    else:
        print(f"Warning: Style file {style_file} not found. Using default matplotlib style.")

    sns.set_theme(
        style="whitegrid",
        rc={
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.facecolor": "white",
            "grid.color": "#eeeeee",
            "xtick.direction": "out",
            "ytick.direction": "out",
            "axes.prop_cycle": mpl.cycler(color=["#d11149", "#1a8fe3", "#1ccd6a", "#e6c229", "#6610f2", "#f17105", "#65e5f3", "#bd8ad5", "#b16b57"]),
        },
    )
    mpl.rcParams.update(
        {
            "font.size": FONTSIZE,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "axes.labelsize": FONTSIZE,
            "axes.titlesize": FONTSIZE + 2,
            "legend.fontsize": FONTSIZE - 2,
            "xtick.labelsize": FONTSIZE,
            "ytick.labelsize": FONTSIZE,
        }
    )


# Helper functions
def _calculate_margins(large_margin, small_margin, left_margin_large, right_margin_large, top_margin_large, bottom_margin_large):
    """Calculate margins for plots."""
    return {
        "left": large_margin if left_margin_large else small_margin,
        "right": large_margin if right_margin_large else small_margin,
        "top": large_margin if top_margin_large else small_margin,
        "bottom": large_margin if bottom_margin_large else small_margin,
    }


def _calculate_figure_size(width, height, aspect_ratio=1.0):
    """Calculate figure size based on aspect ratio."""
    if width is not None:
        height = width / aspect_ratio
    elif height is not None:
        width = height * aspect_ratio
    return width, height


# Figure setup
def figure(width=TEXTWIDTH, height=None, aspect_ratio=1.0, make3d=False):
    """Create a figure."""
    width, height = _calculate_figure_size(width, height, aspect_ratio)
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_subplot(111, projection="3d") if make3d else fig.add_subplot(111)
    return fig, ax


def figure_with_cbar(width=TEXTWIDTH, height=None, aspect_ratio=1.0, cbar_width=0.05, cbar_pad=0.02):
    """Create figure with colorbar space."""
    width, height = _calculate_figure_size(width, height, aspect_ratio)
    fig, ax = plt.subplots(figsize=(width, height))
    cax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    return fig, (ax, cax)


def grid(nx=2, ny=2, width=TEXTWIDTH, aspect_ratio=1.0):
    """Create a grid of plots."""
    width, height = _calculate_figure_size(width, None, aspect_ratio)
    fig = plt.figure(figsize=(width, height))
    gs = gridspec.GridSpec(ny, nx)
    return fig, gs


# Plot functions with scaling based on figure size
def plot_scatter(xs, ys, **kwargs):
    """Scatter plot with proportional scaling based on figure size."""
    fig = kwargs.pop("fig", plt.gcf())  # Use current figure if fig is not passed
    scaled_size = scale_property_to_figure(50, fig.get_size_inches())
    scaled_linewidth = scale_property_to_figure(0.5, fig.get_size_inches())
    defaults = {"alpha": 0.7, "s": scaled_size, "edgecolors": "k", "linewidths": scaled_linewidth}
    kwargs = {**defaults, **kwargs}
    plt.scatter(xs, ys, **kwargs)
    return fig


def plot_line(xs, ys, **kwargs):
    """Line plot with proportional scaling based on figure size."""
    fig = kwargs.pop("fig", plt.gcf())  # Use current figure if fig is not passed
    scaled_linewidth = scale_property_to_figure(2, fig.get_size_inches())
    defaults = {"linewidth": scaled_linewidth}
    kwargs = {**defaults, **kwargs}
    plt.plot(xs, ys, **kwargs)
    return fig


def plot_errorbar(xs, ys, yerr, xerr, **kwargs):
    """Errorbar plot with proportional scaling based on figure size."""
    fig = kwargs.pop("fig", plt.gcf())  # Use current figure if fig is not passed
    scaled_capsize = scale_property_to_figure(3, fig.get_size_inches())
    scaled_elinewidth = scale_property_to_figure(1.5, fig.get_size_inches())
    defaults = {"fmt": "o", "capsize": scaled_capsize, "elinewidth": scaled_elinewidth}
    kwargs = {**defaults, **kwargs}
    plt.errorbar(xs, ys, yerr=yerr, xerr=xerr, **kwargs)
    return fig
