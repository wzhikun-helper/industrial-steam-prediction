"""Generate Fig. 4: fusion-model comparison on one validation set."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 85
FIG_HEIGHT_MM = 52
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


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "results" / "paper_fig4_fusion_comparison.csv"
    output_stem = project_root / "figures" / "paper" / "fig4_fusion_comparison"

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
            label_va = "center"
        elif model == "Best XGBoost":
            label_offset = (-3, 0)
            label_ha = "right"
            label_va = "center"
        else:
            label_offset = (5, 0)
            label_ha = "left"
            label_va = "center"
        ax.annotate(
            f"{value:.4f}",
            xy=(value, index),
            xytext=label_offset,
            textcoords="offset points",
            ha=label_ha,
            va=label_va,
            fontsize=6.3,
            color="#404040",
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
    )

    ax.annotate(
        "Best Ridge reference",
        xy=(reference_mse, -0.25),
        xytext=(3, 4),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=5.7,
        color="#8A8A8A",
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df["model"])
    ax.invert_yaxis()
    for tick in ax.get_yticklabels():
        if tick.get_text() == HIGHLIGHT_MODEL:
            tick.set_color(accent)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(len(df) - 0.5, -0.9)
    ax.set_xlabel("Mean squared error (MSE)")
    ax.set_ylabel("")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    fig.subplots_adjust(left=0.35, right=0.97, top=0.93, bottom=0.24)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
