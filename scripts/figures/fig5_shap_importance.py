"""Generate Fig. 5: global SHAP feature importance for Best XGBoost."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 85
FIG_HEIGHT_MM = 96
EXPECTED_FEATURE_COUNT = 15
MODEL_CONTEXT = "Best XGBoost"
INTERPRETATION_SCOPE = "global contribution magnitude for Best XGBoost only"
UNCERTAINTY_AVAILABLE = False
SIGNIFICANCE_INFERENCE = False
SINGLE_SERIES = True
REQUIRED_COLUMNS = {"feature", "mean_abs_shap"}


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "results" / "paper_fig5_shap_importance.csv"
    output_stem = project_root / "figures" / "paper" / "fig5_shap_importance"

    df = pd.read_csv(data_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(df) != EXPECTED_FEATURE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_FEATURE_COUNT} features, found {len(df)}."
        )

    df = df.copy()
    df["feature"] = df["feature"].astype(str)
    df["mean_abs_shap"] = pd.to_numeric(df["mean_abs_shap"], errors="raise")
    if df["feature"].duplicated().any():
        raise ValueError("Feature names must be unique.")
    if not np.isfinite(df["mean_abs_shap"]).all():
        raise ValueError("SHAP importance contains non-finite values.")
    if (df["mean_abs_shap"] < 0).any():
        raise ValueError("Mean absolute SHAP values must be non-negative.")

    df = df.sort_values("mean_abs_shap", ascending=False, kind="stable").reset_index(
        drop=True
    )
    if df.loc[0, "feature"] != "V0":
        raise ValueError("V0 is expected to be the highest-ranked feature.")

    paper_style(font="sans")
    fig, ax = plt.subplots(
        figsize=(FIG_WIDTH_MM * MM_TO_INCH, FIG_HEIGHT_MM * MM_TO_INCH)
    )

    accent = PALETTE[0]
    neutral = "#858585"
    colors = [accent if feature == "V0" else neutral for feature in df["feature"]]
    y = np.arange(len(df))

    ax.barh(
        y,
        df["mean_abs_shap"],
        height=0.62,
        color=colors,
        edgecolor="none",
        zorder=2,
    )

    max_value = float(df["mean_abs_shap"].max())
    ax.set_xlim(0, max_value * 1.13)
    for feature in ("V0", "V1"):
        row = df.loc[df["feature"] == feature].iloc[0]
        row_index = int(df.index[df["feature"] == feature][0])
        value = float(row["mean_abs_shap"])
        ax.annotate(
            f"{value:.3f}",
            xy=(value, row_index),
            xytext=(3, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=6.3,
            color="#444444",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(df["feature"])
    ax.invert_yaxis()
    for tick in ax.get_yticklabels():
        if tick.get_text() == "V0":
            tick.set_color(accent)
            tick.set_fontweight("normal")

    ax.set_xlabel("Mean absolute SHAP value")
    ax.set_ylabel("")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.xaxis.grid(True, color="#E9E9E9", linewidth=0.4)
    ax.yaxis.grid(False)

    ax.text(
        0.0,
        1.025,
        "Explained model: Best XGBoost",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=5.4,
        color="#909090",
    )

    fig.subplots_adjust(left=0.20, right=0.97, top=0.94, bottom=0.10)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"features={len(df)}; top={df.loc[0, 'feature']}; "
        f"xlim=(0, {max_value * 1.13})"
    )


if __name__ == "__main__":
    main()
