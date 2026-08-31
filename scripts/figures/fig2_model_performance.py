"""Generate Fig. 2: model performance under 5-fold TimeSeriesSplit."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 85
FIG_HEIGHT_MM = 62
REQUIRED_COLUMNS = {"model", "mse_mean", "mse_std"}
TUNED_MODELS = {"Best Ridge", "Best XGBoost"}
CAPTION = (
    "Error bars denote ±1 standard deviation across five TimeSeriesSplit "
    "validation folds."
)


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "results" / "paper_fig2_model_performance.csv"
    output_stem = project_root / "figures" / "paper" / "fig2_model_performance"

    df = pd.read_csv(data_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df.copy()
    for column in ("mse_mean", "mse_std"):
        df[column] = pd.to_numeric(df[column], errors="raise")
    if df["model"].duplicated().any():
        raise ValueError("Model names must be unique.")
    if (df["mse_std"] < 0).any():
        raise ValueError("mse_std must be non-negative.")
    df = df.sort_values("mse_mean", ascending=True, kind="stable").reset_index(drop=True)

    paper_style(font="sans")
    fig, ax = plt.subplots(
        figsize=(FIG_WIDTH_MM * MM_TO_INCH, FIG_HEIGHT_MM * MM_TO_INCH)
    )

    y = np.arange(len(df))
    neutral = "#555555"
    whisker = "#777777"
    accent = PALETTE[0]

    # Whiskers show fold-to-fold standard deviations.
    ax.errorbar(
        df["mse_mean"],
        y,
        xerr=df["mse_std"],
        fmt="none",
        ecolor=whisker,
        elinewidth=0.8,
        capsize=2.0,
        capthick=0.8,
        zorder=1,
    )

    for index, row in df.iterrows():
        tuned = row["model"] in TUNED_MODELS
        best = row["model"] == "Best Ridge"
        marker = "D" if tuned else "o"
        edgecolor = accent if best else neutral
        facecolor = accent if best else ("white" if tuned else neutral)
        ax.scatter(
            row["mse_mean"],
            index,
            marker=marker,
            s=30 if best else 21,
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=0.9,
            zorder=3,
        )

    left = float((df["mse_mean"] - df["mse_std"]).min())
    right = float((df["mse_mean"] + df["mse_std"]).max())
    span = right - left
    x_min = left - 0.035 * span
    x_max = right + 0.38 * span

    for index, value in enumerate(df["mse_mean"]):
        ax.annotate(
            f"{value:.4f}",
            xy=(value, index),
            xytext=(5, -6),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=6.3,
            color="#555555",
            zorder=4,
        )

    header_y = -0.82
    ax.text(
        x_min,
        header_y,
        "Error bars: ±1 SD",
        ha="left",
        va="center",
        fontsize=6.2,
        color="#666666",
    )
    ax.set_yticks(y)
    ax.set_yticklabels(df["model"])
    ax.invert_yaxis()
    for tick in ax.get_yticklabels():
        if tick.get_text() == "Best Ridge":
            tick.set_color(accent)
            tick.set_fontweight("normal")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(len(df) - 0.5, -1.15)
    ax.set_xlabel("Mean squared error (MSE)")
    ax.set_ylabel("")
    ax.xaxis.grid(True, color="#E1E1E1", linewidth=0.45)
    ax.yaxis.grid(False)

    fig.subplots_adjust(left=0.31, right=0.98, top=0.95, bottom=0.19)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
