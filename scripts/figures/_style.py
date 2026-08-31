"""Shared publication style for reproducible paper figures.

This local shim implements the paper_style/save interface specified by the
icarus-figures skill because the installed skill package contains no runtime.
"""

from pathlib import Path

import matplotlib as mpl


PALETTE = (
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#009E73",  # bluish green
    "#CC79A7",  # reddish purple
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
)
MARKERS = ("o", "D", "s", "^", "v", "P")
LINESTYLES = ("-", "--", "-.", ":")


def paper_style(font="sans"):
    """Apply the single shared journal-ready matplotlib style."""
    if font != "sans":
        raise ValueError("This project preset currently supports font='sans' only.")

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7.5,
            "axes.labelsize": 8.0,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 7.0,
            "axes.linewidth": 0.65,
            "axes.edgecolor": "#333333",
            "axes.labelcolor": "#222222",
            "xtick.color": "#333333",
            "ytick.color": "#222222",
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 2.5,
            "ytick.major.size": 0.0,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.axisbelow": True,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.bbox": None,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.unicode_minus": False,
        }
    )
    return PALETTE, MARKERS, LINESTYLES


def save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300):
    """Save one figure reproducibly in editable vector and print raster formats."""
    stem = Path(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    for extension in formats:
        kwargs = {"dpi": dpi} if extension == "png" else {}
        fig.savefig(stem.with_suffix(f".{extension}"), **kwargs)
    print(f"[fig] saved {stem}.{{pdf,svg,png}}")
