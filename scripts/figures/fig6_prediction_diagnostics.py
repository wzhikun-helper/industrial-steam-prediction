"""Generate Fig. 6: Weighted Blend prediction diagnostics."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 178
FIG_HEIGHT_MM = 80
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


def padded_limits(values, fraction=0.04):
    """Return full-data limits with modest symmetric padding."""
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
    output_stem = project_root / "figures" / "paper" / "fig6_prediction_diagnostics"

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

    paper_style(font="sans")
    fig = plt.figure(
        figsize=(FIG_WIDTH_MM * MM_TO_INCH, FIG_HEIGHT_MM * MM_TO_INCH)
    )
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

    # Panel (a): all observations and predictions on an honest 1:1 scale.
    ax_a.scatter(observed, predicted, **scatter_style)
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
    ax_a.set_xlabel("Observed value")
    ax_a.set_ylabel("Predicted value")
    ax_a.text(
        0.04,
        0.94,
        f"N = {len(df)}",
        transform=ax_a.transAxes,
        ha="left",
        va="top",
        fontsize=6.2,
        color="#808080",
    )

    # Panel (b): full residual cloud; no smoother is included by default.
    ax_b.scatter(predicted, residual, **scatter_style)
    ax_b.axhline(
        0,
        color=reference_color,
        linewidth=0.75,
        linestyle=(0, (3, 2.5)),
        zorder=1,
    )
    ax_b.set_xlim(predicted_limits)
    ax_b.set_ylim(residual_limits)
    ax_b.set_xlabel("Predicted value")
    ax_b.set_ylabel("Residual")

    # Panel (c): subordinate tail witness sharing panel (b)'s residual range.
    ax_c.hist(
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
    ax_c.set_xlabel("Count")
    ax_c.tick_params(axis="y", labelleft=False, left=False)
    ax_c.spines["left"].set_visible(False)
    ax_c.xaxis.set_major_locator(MaxNLocator(nbins=2, integer=True))

    for label, axis in zip(("(a)", "(b)", "(c)"), (ax_a, ax_b, ax_c)):
        axis.text(
            0.01,
            1.025,
            label,
            transform=axis.transAxes,
            ha="left",
            va="bottom",
            fontsize=7.0,
            fontweight="normal",
            color="#222222",
        )

    ax_a.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_a.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_b.xaxis.set_major_locator(MaxNLocator(nbins=4))
    ax_b.yaxis.set_major_locator(MaxNLocator(nbins=5))
    for axis in (ax_a, ax_b, ax_c):
        axis.grid(False)

    fig.subplots_adjust(left=0.075, right=0.985, top=0.94, bottom=0.18)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"N={len(df)}; joint_limits={joint_limits}; "
        f"predicted_limits={predicted_limits}; residual_limits={residual_limits}"
    )


if __name__ == "__main__":
    main()
