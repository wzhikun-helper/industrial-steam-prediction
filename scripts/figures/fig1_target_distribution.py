"""Generate Fig. 1: target distribution and data overview."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 85
FIG_HEIGHT_MM = 62
EXPECTED_N = 2888
VALIDATION_CONTEXT = "target data overview"
UNCERTAINTY_AVAILABLE = False
SIGNIFICANCE_INFERENCE = False
SINGLE_SERIES = True
REQUIRED_COLUMNS = {"target"}


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "results" / "paper_fig1_target_distribution.csv"
    output_stem = project_root / "figures" / "paper" / "fig1_target_distribution"

    df = pd.read_csv(data_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(df) != EXPECTED_N:
        raise ValueError(f"Expected {EXPECTED_N} samples, found {len(df)}.")

    target = pd.to_numeric(df["target"], errors="raise").to_numpy()
    if not np.isfinite(target).all():
        raise ValueError("Target data contain non-finite values.")

    sample_count = len(target)
    mean_value = float(np.mean(target))
    median_value = float(np.median(target))
    bin_edges = np.histogram_bin_edges(target, bins="fd")

    paper_style(font="sans")
    fig, ax = plt.subplots(
        figsize=(FIG_WIDTH_MM * MM_TO_INCH, FIG_HEIGHT_MM * MM_TO_INCH)
    )

    bar_color = PALETTE[0]
    mean_color = "#4E4E4E"
    median_color = "#686868"
    counts, used_edges, _ = ax.hist(
        target,
        bins=bin_edges,
        density=False,
        color=bar_color,
        alpha=0.72,
        edgecolor="white",
        linewidth=0.35,
        zorder=2,
    )
    if int(np.sum(counts)) != sample_count:
        raise RuntimeError("Histogram counts do not include every target sample.")
    if not np.array_equal(used_edges, bin_edges):
        raise RuntimeError("Histogram did not use the computed FD bin edges.")

    ax.axvline(
        mean_value,
        color=mean_color,
        linewidth=0.8,
        linestyle=(0, (4, 2.5)),
        zorder=3,
    )
    ax.axvline(
        median_value,
        color=median_color,
        linewidth=0.8,
        linestyle=(0, (4, 2, 1, 2)),
        zorder=3,
    )

    legend_handles = [
        Line2D(
            [0],
            [0],
            color=mean_color,
            linewidth=0.8,
            linestyle=(0, (4, 2.5)),
            label=f"Mean = {mean_value:.3f}",
        ),
        Line2D(
            [0],
            [0],
            color=median_color,
            linewidth=0.8,
            linestyle=(0, (4, 2, 1, 2)),
            label=f"Median = {median_value:.3f}",
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper left",
        frameon=False,
        fontsize=6.2,
        handlelength=2.3,
        handletextpad=0.6,
        borderaxespad=0.3,
        labelspacing=0.35,
    )
    ax.text(
        0.985,
        0.97,
        f"N = {sample_count:,}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=5.8,
        color="#949494",
    )

    data_min = float(np.min(target))
    data_max = float(np.max(target))
    data_span = data_max - data_min
    x_padding = 0.03 * data_span
    x_limits = (data_min - x_padding, data_max + x_padding)
    ax.set_xlim(x_limits)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Target value")
    ax.set_ylabel("Count")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax.grid(False)

    fig.subplots_adjust(left=0.17, right=0.97, top=0.95, bottom=0.20)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"N={sample_count}; mean={mean_value}; median={median_value}; "
        f"fd_bins={len(bin_edges) - 1}; x_limits={x_limits}; "
        f"histogram_count={int(np.sum(counts))}"
    )


if __name__ == "__main__":
    main()
