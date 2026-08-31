"""Generate the Chinese Fig. 2 model-performance master for ZJU Engineering Science."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 78
FIG_HEIGHT_MM = 57
REQUIRED_COLUMNS = {"model", "mse_mean", "mse_std"}
TUNED_MODELS = {"Best Ridge", "Best XGBoost"}
VALIDATION_CONTEXT = "five TimeSeriesSplit folds"
CAPTION = "误差棒表示5折 TimeSeriesSplit 验证结果的 ±1 个标准差。"
SIGNIFICANCE_INFERENCE = False


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


def mixed_text_box(parts):
    """Pack text fragments while retaining their explicitly assigned fonts."""
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
        sep=0,
    )


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "results" / "paper_fig2_model_performance.csv"
    output_stem = project_root / "figures" / "paper" / "fig2_model_performance_zh"

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
    if len(df) != 7:
        raise ValueError(f"Expected 7 models, found {len(df)}.")
    df = df.sort_values("mse_mean", ascending=True, kind="stable").reset_index(drop=True)

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

    y = np.arange(len(df))
    neutral = "#555555"
    whisker = "#777777"
    accent = PALETTE[0]

    # Whiskers denote ±1 standard deviation across the five validation folds.
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
            fontproperties=latin_font,
            zorder=4,
        )

    header = mixed_text_box(
        (
            ("误差棒：", chinese_font, 6.2, "#666666"),
            ("±1 SD", latin_font, 6.2, "#666666"),
        )
    )
    ax.add_artist(
        AnnotationBbox(
            header,
            (x_min, -0.82),
            xycoords="data",
            box_alignment=(0, 0.5),
            frameon=False,
            pad=0,
        )
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df["model"])
    ax.invert_yaxis()
    for tick in ax.get_yticklabels():
        tick.set_fontproperties(latin_font)
        tick.set_fontweight("normal")
        if tick.get_text() == "Best Ridge":
            tick.set_color(accent)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(len(df) - 0.5, -1.15)
    ax.set_xlabel("")
    ax.set_ylabel("")
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
            (0.5, -0.145),
            xycoords=ax.transAxes,
            box_alignment=(0.5, 0.5),
            frameon=False,
            pad=0,
        )
    )

    ax.tick_params(axis="both", direction="in")
    for tick in ax.get_xticklabels():
        tick.set_fontproperties(latin_font)
    ax.xaxis.grid(True, color="#E1E1E1", linewidth=0.45)
    ax.yaxis.grid(False)

    fig.subplots_adjust(left=0.31, right=0.98, top=0.95, bottom=0.19)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"models={len(df)}; order={df['model'].tolist()}; "
        f"x_limits=({x_min}, {x_max}); "
        f"chinese_font={chinese_family}:{chinese_path}; "
        f"latin_font={latin_family}:{latin_path}; ticks=in"
    )


if __name__ == "__main__":
    main()
