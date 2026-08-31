"""Generate the Chinese Fig. 6 prediction-diagnostics master for ZJU Engineering Science."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea
from matplotlib.ticker import MaxNLocator

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 164
FIG_HEIGHT_MM = 74
EXPECTED_N = 481
VALIDATION_CONTEXT = "independent fusion validation set"
UNCERTAINTY_AVAILABLE = False
SIGNIFICANCE_INFERENCE = False
SINGLE_SERIES = True
REQUIRED_COLUMNS = {
    "true_value",
    "predicted_value",
    "residual",
    "absolute_error",
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


def panel_label_box(label, chinese_font, latin_font):
    return HPacker(
        children=[
            TextArea(
                "（",
                textprops={"fontproperties": chinese_font, "fontsize": 7.0, "color": "#222222"},
            ),
            TextArea(
                label,
                textprops={"fontproperties": latin_font, "fontsize": 7.0, "color": "#222222"},
            ),
            TextArea(
                "）",
                textprops={"fontproperties": chinese_font, "fontsize": 7.0, "color": "#222222"},
            ),
        ],
        align="center",
        pad=0,
        sep=0,
    )


def padded_limits(values, fraction=0.04):
    lower = float(np.min(values))
    upper = float(np.max(values))
    span = upper - lower
    if span <= 0:
        span = max(abs(lower), 1.0)
    pad = fraction * span
    return lower - pad, upper + pad


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "results" / "paper_fig6_prediction_diagnostics.csv"
    output_stem = project_root / "figures" / "paper" / "fig6_prediction_diagnostics_zh"

    df = pd.read_csv(data_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(df) != EXPECTED_N:
        raise ValueError(f"Expected {EXPECTED_N} samples, found {len(df)}.")

    df = df.copy()
    for column in REQUIRED_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="raise")
    if not np.isfinite(df[list(REQUIRED_COLUMNS)].to_numpy()).all():
        raise ValueError("Diagnostic data contain non-finite values.")

    calculated_residual = df["true_value"] - df["predicted_value"]
    if not np.allclose(calculated_residual, df["residual"], rtol=1e-10, atol=1e-12):
        raise ValueError("Residual values are inconsistent with observed minus predicted.")
    if not np.allclose(
        np.abs(df["residual"]), df["absolute_error"], rtol=1e-10, atol=1e-12
    ):
        raise ValueError("absolute_error is inconsistent with the residual column.")

    observed = df["true_value"].to_numpy()
    predicted = df["predicted_value"].to_numpy()
    residual = df["residual"].to_numpy()
    joint_limits = padded_limits(np.concatenate((observed, predicted)), fraction=0.04)
    predicted_limits = padded_limits(predicted, fraction=0.04)
    residual_limits = padded_limits(residual, fraction=0.04)

    chinese_font, chinese_family, chinese_path = first_available_font(
        ("SimSun", "NSimSun", "Source Han Serif SC", "Noto Serif CJK SC")
    )
    latin_font, latin_family, latin_path = first_available_font(
        ("Times New Roman", "STIX Two Text", "Liberation Serif", "DejaVu Serif")
    )

    paper_style(font="sans")
    fig = plt.figure(figsize=(FIG_WIDTH_MM * MM_TO_INCH, FIG_HEIGHT_MM * MM_TO_INCH))
    outer_grid = fig.add_gridspec(
        1,
        2,
        width_ratios=(1.65, 1.35),
        wspace=0.30,
    )
    residual_grid = outer_grid[0, 1].subgridspec(
        1,
        2,
        width_ratios=(1.00, 0.35),
        wspace=0.14,
    )
    ax_a = fig.add_subplot(outer_grid[0, 0])
    ax_b = fig.add_subplot(residual_grid[0, 0])
    ax_c = fig.add_subplot(residual_grid[0, 1], sharey=ax_b)

    point_color = PALETTE[0]
    reference_color = "#696969"
    histogram_color = "#A9C8D8"
    scatter_style = {
        "s": 10,
        "color": point_color,
        "alpha": 0.43,
        "edgecolors": "none",
        "rasterized": False,
        "zorder": 2,
    }

    # Panel （a）: all 481 samples on an honest 1:1 scale.
    scatter_a = ax_a.scatter(observed, predicted, **scatter_style)
    ax_a.plot(
        joint_limits,
        joint_limits,
        color=reference_color,
        linewidth=0.8,
        linestyle=(0, (3, 2.5)),
        zorder=1,
    )
    ax_a.set_xlim(joint_limits)
    ax_a.set_ylim(joint_limits)
    ax_a.set_aspect("equal", adjustable="box")
    ax_a.set_xlabel("观测值", fontproperties=chinese_font, fontsize=8.0)
    ax_a.set_ylabel("预测值", fontproperties=chinese_font, fontsize=8.0)
    ax_a.text(
        0.04,
        0.94,
        f"N = {len(df)}",
        transform=ax_a.transAxes,
        ha="left",
        va="top",
        fontsize=6.2,
        color="#808080",
        fontproperties=latin_font,
    )

    # Panel （b）: all 481 residuals; no smoother or trend line.
    scatter_b = ax_b.scatter(predicted, residual, **scatter_style)
    ax_b.axhline(
        0,
        color=reference_color,
        linewidth=0.75,
        linestyle=(0, (3, 2.5)),
        zorder=1,
    )
    ax_b.set_xlim(predicted_limits)
    ax_b.set_ylim(residual_limits)
    ax_b.set_xlabel("预测值", fontproperties=chinese_font, fontsize=8.0)
    ax_b.set_ylabel("残差", fontproperties=chinese_font, fontsize=8.0)

    # Panel （c）: subordinate horizontal histogram sharing panel （b）'s y-range.
    histogram_counts, _, _ = ax_c.hist(
        residual,
        bins=24,
        orientation="horizontal",
        color=histogram_color,
        edgecolor="white",
        linewidth=0.35,
    )
    ax_c.axhline(
        0,
        color=reference_color,
        linewidth=0.75,
        linestyle=(0, (3, 2.5)),
        zorder=2,
    )
    ax_c.set_ylim(residual_limits)
    ax_c.set_xlabel("频数", fontproperties=chinese_font, fontsize=8.0)
    ax_c.tick_params(axis="y", labelleft=False, left=False)
    ax_c.spines["left"].set_visible(False)
    ax_c.xaxis.set_major_locator(MaxNLocator(nbins=2, integer=True))

    for label, axis in zip(("a", "b", "c"), (ax_a, ax_b, ax_c)):
        box = panel_label_box(label, chinese_font, latin_font)
        axis.add_artist(
            AnnotationBbox(
                box,
                (0.0, 0.995),
                xycoords=axis.transAxes,
                box_alignment=(0, 1),
                frameon=False,
                pad=0,
            )
        )

    ax_a.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_a.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_b.xaxis.set_major_locator(MaxNLocator(nbins=4))
    ax_b.yaxis.set_major_locator(MaxNLocator(nbins=5))
    for axis in (ax_a, ax_b, ax_c):
        axis.tick_params(axis="both", direction="in")
        for tick in (*axis.get_xticklabels(), *axis.get_yticklabels()):
            tick.set_fontproperties(latin_font)
        axis.grid(False)

    if len(scatter_a.get_offsets()) != EXPECTED_N:
        raise RuntimeError("Panel （a） does not contain all 481 samples.")
    if len(scatter_b.get_offsets()) != EXPECTED_N:
        raise RuntimeError("Panel （b） does not contain all 481 samples.")
    if int(np.sum(histogram_counts)) != EXPECTED_N:
        raise RuntimeError("Panel （c） histogram does not contain all 481 residuals.")
    if not np.allclose(ax_a.get_xlim(), ax_a.get_ylim()):
        raise RuntimeError("Panel （a） does not use identical x/y limits.")
    if ax_a.get_aspect() != 1.0:
        raise RuntimeError("Panel （a） does not use equal aspect.")
    if not np.allclose(ax_b.get_ylim(), ax_c.get_ylim()):
        raise RuntimeError("Panels （b） and （c） do not share the residual y-range.")

    fig.subplots_adjust(left=0.075, right=0.985, top=0.94, bottom=0.19)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"N={len(df)}; panel_a_points={len(scatter_a.get_offsets())}; "
        f"panel_b_points={len(scatter_b.get_offsets())}; "
        f"histogram_count={int(np.sum(histogram_counts))}; "
        f"joint_limits={joint_limits}; predicted_limits={predicted_limits}; "
        f"residual_limits={residual_limits}; equal_aspect=True; shared_residual_range=True; "
        "panel_labels=（a）,（b）,（c）; ticks=in; "
        f"chinese_font={chinese_family}:{chinese_path}; "
        f"latin_font={latin_family}:{latin_path}"
    )


if __name__ == "__main__":
    main()
