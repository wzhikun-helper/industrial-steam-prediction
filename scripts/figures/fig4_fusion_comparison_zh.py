"""Generate the Chinese Fig. 4 fusion-comparison master for ZJU Engineering Science."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea
from matplotlib.ticker import MaxNLocator

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 78
FIG_HEIGHT_MM = 48
REFERENCE_MODEL = "Best Ridge"
HIGHLIGHT_MODEL = "Weighted Blend"
VALIDATION_CONTEXT = "independent fusion validation set"
UNCERTAINTY_AVAILABLE = False
SIGNIFICANCE_INFERENCE = False
REQUIRED_COLUMNS = {
    "model",
    "mse",
    "mse_difference_vs_best_ridge",
    "mse_change_percent_vs_best_ridge",
}


def first_available_font(families):
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


def mixed_text_box(parts, sep=0):
    return HPacker(
        children=[
            TextArea(
                text,
                textprops={
                    "fontproperties": font,
                    "fontsize": size,
                    "color": color,
                },
            )
            for text, font, size, color in parts
        ],
        align="center",
        pad=0,
        sep=sep,
    )


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "results" / "paper_fig4_fusion_comparison.csv"
    output_stem = project_root / "figures" / "paper" / "fig4_fusion_comparison_zh"

    df = pd.read_csv(data_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df.copy()
    numeric_columns = (
        "mse",
        "mse_difference_vs_best_ridge",
        "mse_change_percent_vs_best_ridge",
    )
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")
    if len(df) != 4:
        raise ValueError(f"Expected 4 models, found {len(df)}.")
    if df["model"].duplicated().any():
        raise ValueError("Model names must be unique.")
    if REFERENCE_MODEL not in set(df["model"]):
        raise ValueError(f"Reference model not found: {REFERENCE_MODEL}")
    if HIGHLIGHT_MODEL not in set(df["model"]):
        raise ValueError(f"Highlight model not found: {HIGHLIGHT_MODEL}")

    reference_mse = float(df.loc[df["model"] == REFERENCE_MODEL, "mse"].iloc[0])
    calculated_difference = df["mse"] - reference_mse
    if not np.allclose(
        calculated_difference,
        df["mse_difference_vs_best_ridge"],
        rtol=1e-9,
        atol=1e-12,
    ):
        raise ValueError("CSV difference column is inconsistent with the Best Ridge MSE.")

    df = df.sort_values("mse", ascending=True, kind="stable").reset_index(drop=True)
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

    neutral = "#585858"
    reference_color = "#B5B5B5"
    accent = PALETTE[0]
    y = np.arange(len(df))

    mse_min = float(df["mse"].min())
    mse_max = float(df["mse"].max())
    data_span = mse_max - mse_min
    axis_padding = 0.065 * data_span
    x_min = mse_min - axis_padding
    x_max = mse_max + axis_padding

    ax.vlines(
        reference_mse,
        ymin=-0.25,
        ymax=len(df) - 0.65,
        color=reference_color,
        linewidth=0.6,
        linestyle=(0, (2.2, 2.2)),
        zorder=0,
    )

    for index, row in df.iterrows():
        value = float(row["mse"])
        model = row["model"]
        if model == HIGHLIGHT_MODEL:
            ax.scatter(
                value,
                index,
                marker="D",
                s=26,
                facecolor=accent,
                edgecolor=accent,
                linewidth=0.8,
                zorder=3,
            )
        else:
            ax.scatter(
                value,
                index,
                marker="o",
                s=23,
                facecolor=neutral,
                edgecolor=neutral,
                linewidth=0.7,
                zorder=3,
            )

        if model == HIGHLIGHT_MODEL:
            label_offset = (6, 0)
            label_ha = "left"
        elif model == "Best XGBoost":
            label_offset = (-3, 0)
            label_ha = "right"
        else:
            label_offset = (5, 0)
            label_ha = "left"
        ax.annotate(
            f"{value:.4f}",
            xy=(value, index),
            xytext=label_offset,
            textcoords="offset points",
            ha=label_ha,
            va="center",
            fontsize=6.3,
            color="#404040",
            fontproperties=latin_font,
        )

    highlight = df.loc[df["model"] == HIGHLIGHT_MODEL].iloc[0]
    highlight_y = int(df.index[df["model"] == HIGHLIGHT_MODEL][0])
    ax.annotate(
        f"{highlight['mse_change_percent_vs_best_ridge']:.2f}%",
        xy=(float(highlight["mse"]), highlight_y),
        xytext=(0, -6),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=5.7,
        color="#8A8A8A",
        fontproperties=latin_font,
    )

    reference_label = mixed_text_box(
        (
            ("Best Ridge", latin_font, 5.7, "#8A8A8A"),
            ("参考线", chinese_font, 5.7, "#8A8A8A"),
        ),
        sep=2.0,
    )
    ax.add_artist(
        AnnotationBbox(
            reference_label,
            (reference_mse, -0.25),
            xycoords="data",
            xybox=(3, 4),
            boxcoords="offset points",
            box_alignment=(0, 0),
            frameon=False,
            pad=0,
        )
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df["model"])
    ax.invert_yaxis()
    for tick in ax.get_yticklabels():
        tick.set_fontproperties(latin_font)
        if tick.get_text() == HIGHLIGHT_MODEL:
            tick.set_color(accent)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(len(df) - 0.5, -0.9)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax.tick_params(axis="both", direction="in")
    for tick in ax.get_xticklabels():
        tick.set_fontproperties(latin_font)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    xlabel = mixed_text_box(
        (
            ("均方误差（", chinese_font, 8.0, "#222222"),
            ("MSE", latin_font, 8.0, "#222222"),
            ("）", chinese_font, 8.0, "#222222"),
        )
    )
    ax.add_artist(
        AnnotationBbox(
            xlabel,
            (0.5, -0.19),
            xycoords=ax.transAxes,
            box_alignment=(0.5, 0.5),
            frameon=False,
            pad=0,
        )
    )

    fig.subplots_adjust(left=0.37, right=0.98, top=0.93, bottom=0.26)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"models={len(df)}; order={df['model'].tolist()}; "
        f"reference_mse={reference_mse}; x_limits=({x_min}, {x_max}); "
        "min_annotation_font_pt=5.7; ticks=in; "
        f"chinese_font={chinese_family}:{chinese_path}; "
        f"latin_font={latin_family}:{latin_path}"
    )


if __name__ == "__main__":
    main()
