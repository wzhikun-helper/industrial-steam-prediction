"""Generate the Chinese Fig. 1 target-distribution master for ZJU Engineering Science."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea, HPacker, TextArea, VPacker
from matplotlib.ticker import MaxNLocator

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 78
FIG_HEIGHT_MM = 57
EXPECTED_N = 2888
VALIDATION_CONTEXT = "target data overview"
UNCERTAINTY_AVAILABLE = False
SIGNIFICANCE_INFERENCE = False
SINGLE_SERIES = True
REQUIRED_COLUMNS = {"target"}


def first_available_font(families):
    """Return a deterministic installed font from the approved fallback chain."""
    for family in families:
        try:
            path = font_manager.findfont(
                font_manager.FontProperties(family=family),
                fallback_to_default=False,
            )
        except ValueError:
            continue
        return font_manager.FontProperties(family=family), family, path
    raise RuntimeError(f"None of the required fonts are installed: {families}")


def mixed_font_legend(ax, mean_value, median_value, chinese_font, latin_font):
    """Draw two compact legend rows with separate Chinese and numeric fonts."""
    rows = []
    specifications = (
        ("均值", mean_value, "#4E4E4E", (0, (4, 2.5))),
        ("中位数", median_value, "#686868", (0, (4, 2, 1, 2))),
    )
    for label, value, color, linestyle in specifications:
        swatch = DrawingArea(18, 7, 0, 0)
        swatch.add_artist(
            Line2D([0, 17], [3.5, 3.5], color=color, linewidth=0.8, linestyle=linestyle)
        )
        label_area = TextArea(
            label,
            textprops={"fontproperties": chinese_font, "fontsize": 6.2, "color": "#333333"},
        )
        value_area = TextArea(
            f" = {value:.3f}",
            textprops={"fontproperties": latin_font, "fontsize": 6.2, "color": "#333333"},
        )
        rows.append(HPacker(children=[swatch, label_area, value_area], align="center", pad=0, sep=3))

    legend_box = VPacker(children=rows, align="left", pad=0, sep=2)
    anchored = AnchoredOffsetbox(
        loc="upper left",
        child=legend_box,
        frameon=False,
        pad=0,
        borderpad=0.25,
    )
    ax.add_artist(anchored)


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "results" / "paper_fig1_target_distribution.csv"
    output_stem = project_root / "figures" / "paper" / "fig1_target_distribution_zh"

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

    chinese_font, chinese_family, chinese_path = first_available_font(
        ("SimSun", "NSimSun", "Source Han Serif SC", "Noto Serif CJK SC")
    )
    latin_font, latin_family, latin_path = first_available_font(
        ("Times New Roman", "STIX Two Text", "Liberation Serif", "DejaVu Serif")
    )

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

    mixed_font_legend(ax, mean_value, median_value, chinese_font, latin_font)
    ax.text(
        0.985,
        0.97,
        f"N = {sample_count:,}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=5.8,
        color="#949494",
        fontproperties=latin_font,
    )

    data_min = float(np.min(target))
    data_max = float(np.max(target))
    data_span = data_max - data_min
    x_padding = 0.03 * data_span
    x_limits = (data_min - x_padding, data_max + x_padding)
    ax.set_xlim(x_limits)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("目标值", fontproperties=chinese_font, fontsize=8.0)
    ax.set_ylabel("频数", fontproperties=chinese_font, fontsize=8.0)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax.tick_params(axis="both", direction="in")
    for tick in (*ax.get_xticklabels(), *ax.get_yticklabels()):
        tick.set_fontproperties(latin_font)
    ax.grid(False)

    fig.subplots_adjust(left=0.18, right=0.97, top=0.95, bottom=0.20)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"N={sample_count}; mean={mean_value}; median={median_value}; "
        f"fd_bins={len(bin_edges) - 1}; x_limits={x_limits}; "
        f"histogram_count={int(np.sum(counts))}; "
        f"chinese_font={chinese_family}:{chinese_path}; "
        f"latin_font={latin_family}:{latin_path}; ticks=in"
    )


if __name__ == "__main__":
    main()
