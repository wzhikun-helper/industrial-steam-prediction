"""Generate Fig. 3: feature-processing choice and Ridge alpha sensitivity."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, FixedFormatter, MaxNLocator, NullFormatter

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 178
FIG_HEIGHT_MM = 66
VALIDATION_CONTEXT = "5-fold TimeSeriesSplit"
UNCERTAINTY_KIND = "1 SD across five folds"
CAPTION_ALPHA_SD_NOTE = (
    "Five-fold SD is of similar magnitude across the tested alpha values."
)
SIGNIFICANCE_INFERENCE = False
PANEL_A_COLUMNS = {"model", "mse_mean", "mse_std"}
PANEL_B_COLUMNS = {"param_ridge__alpha", "mean_mse", "std_test_score"}


def limits_with_errors(mean, spread, fraction=0.06):
    """Cover every mean ± spread value with modest symmetric padding."""
    lower = float(np.min(mean - spread))
    upper = float(np.max(mean + spread))
    span = upper - lower
    pad = fraction * span if span > 0 else max(abs(lower), 1.0) * fraction
    return lower - pad, upper + pad


def load_inputs(project_root):
    results_dir = project_root / "results"
    panel_a_path = results_dir / "paper_fig3_feature_method_comparison.csv"
    preferred_b_path = results_dir / "paper_fig3_ridge_alpha_sensitivity.csv"
    fallback_b_path = results_dir / "ridge_alpha_tuning.csv"
    panel_b_path = preferred_b_path if preferred_b_path.exists() else fallback_b_path

    panel_a = pd.read_csv(panel_a_path)
    panel_b = pd.read_csv(panel_b_path)
    return panel_a, panel_b, panel_a_path, panel_b_path


def main():
    project_root = Path(__file__).resolve().parents[2]
    output_stem = project_root / "figures" / "paper" / "fig3_feature_ridge_sensitivity"
    panel_a, panel_b, panel_a_path, panel_b_path = load_inputs(project_root)

    missing_a = PANEL_A_COLUMNS.difference(panel_a.columns)
    missing_b = PANEL_B_COLUMNS.difference(panel_b.columns)
    if missing_a:
        raise ValueError(f"Panel (a) missing columns: {sorted(missing_a)}")
    if missing_b:
        raise ValueError(f"Panel (b) missing columns: {sorted(missing_b)}")

    panel_a = panel_a.copy()
    panel_b = panel_b.copy()
    for column in ("mse_mean", "mse_std"):
        panel_a[column] = pd.to_numeric(panel_a[column], errors="raise")
    for column in ("param_ridge__alpha", "mean_mse", "std_test_score"):
        panel_b[column] = pd.to_numeric(panel_b[column], errors="raise")

    if panel_a["model"].duplicated().any():
        raise ValueError("Panel (a) model names must be unique.")
    if (panel_a["mse_std"] < 0).any() or (panel_b["std_test_score"] < 0).any():
        raise ValueError("Standard deviations must be non-negative.")
    if (panel_b["param_ridge__alpha"] <= 0).any():
        raise ValueError("All alpha values must be positive for the log scale.")
    if not np.isfinite(
        panel_a[["mse_mean", "mse_std"]].to_numpy()
    ).all() or not np.isfinite(
        panel_b[["param_ridge__alpha", "mean_mse", "std_test_score"]].to_numpy()
    ).all():
        raise ValueError("Input data contain non-finite values.")

    panel_a = panel_a.sort_values("mse_mean", ascending=True, kind="stable").reset_index(
        drop=True
    )
    panel_b = panel_b.sort_values("param_ridge__alpha", kind="stable").reset_index(
        drop=True
    )
    selected_index = int(panel_b["mean_mse"].idxmin())
    selected = panel_b.loc[selected_index]

    paper_style(font="sans")
    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(FIG_WIDTH_MM * MM_TO_INCH, FIG_HEIGHT_MM * MM_TO_INCH),
        gridspec_kw={"width_ratios": (1.45, 1.00), "wspace": 0.38},
    )

    accent = PALETTE[0]
    neutral = "#595959"
    whisker = "#858585"

    # Panel (a): feature-processing methods.
    y = np.arange(len(panel_a))
    ax_a.errorbar(
        panel_a["mse_mean"],
        y,
        xerr=panel_a["mse_std"],
        fmt="none",
        ecolor=whisker,
        elinewidth=0.8,
        capsize=2.2,
        capthick=0.8,
        zorder=1,
    )
    for index, row in panel_a.iterrows():
        is_ridge = row["model"] == "Ridge"
        ax_a.scatter(
            row["mse_mean"],
            index,
            marker="D" if is_ridge else "o",
            s=28 if is_ridge else 22,
            facecolor=accent if is_ridge else neutral,
            edgecolor=accent if is_ridge else neutral,
            linewidth=0.8,
            zorder=3,
        )
        ax_a.annotate(
            f"{row['mse_mean']:.4f}",
            xy=(row["mse_mean"], index),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=6.1,
            color="#444444",
        )

    panel_a_xlim = limits_with_errors(
        panel_a["mse_mean"].to_numpy(), panel_a["mse_std"].to_numpy()
    )
    ax_a.set_xlim(panel_a_xlim)
    ax_a.set_ylim(len(panel_a) - 0.5, -0.82)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(panel_a["model"])
    for tick in ax_a.get_yticklabels():
        if tick.get_text() == "Ridge":
            tick.set_color(accent)
    ax_a.set_xlabel("Mean squared error (MSE)")
    ax_a.set_ylabel("")
    ax_a.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_a.xaxis.grid(True, color="#E8E8E8", linewidth=0.4)
    ax_a.yaxis.grid(False)
    ax_a.text(
        0.01,
        0.96,
        "Error bars: ±1 SD; 5 folds",
        transform=ax_a.transAxes,
        ha="left",
        va="top",
        fontsize=5.7,
        color="#777777",
    )

    # Panel (b): Ridge alpha sensitivity.
    alpha = panel_b["param_ridge__alpha"].to_numpy()
    mean_mse = panel_b["mean_mse"].to_numpy()
    std_mse = panel_b["std_test_score"].to_numpy()
    ax_b.scatter(
        alpha,
        mean_mse,
        marker="o",
        s=17,
        color=accent,
        zorder=2,
    )
    ax_b.plot(alpha, mean_mse, color=accent, linewidth=0.8, zorder=1)
    ax_b.scatter(
        selected["param_ridge__alpha"],
        selected["mean_mse"],
        marker="D",
        s=28,
        facecolor=accent,
        edgecolor=accent,
        linewidth=0.8,
        zorder=4,
    )
    ax_b.annotate(
        f"Lowest mean: α = {selected['param_ridge__alpha']:g}",
        xy=(selected["param_ridge__alpha"], selected["mean_mse"]),
        xytext=(5, 5),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=5.2,
        color="#777777",
    )

    panel_b_ylim = limits_with_errors(
        mean_mse, np.zeros_like(mean_mse), fraction=0.12
    )
    ax_b.set_xscale("log")
    ax_b.set_xlim(float(alpha.min()) * 0.8, float(alpha.max()) * 1.25)
    ax_b.set_ylim(panel_b_ylim)
    major_alpha = [0.01, 0.1, 1, 10, 100]
    ax_b.xaxis.set_major_locator(FixedLocator(major_alpha))
    ax_b.xaxis.set_major_formatter(FixedFormatter(["0.01", "0.1", "1", "10", "100"]))
    ax_b.xaxis.set_minor_formatter(NullFormatter())
    ax_b.set_xlabel("Ridge regularization α")
    ax_b.set_ylabel("Mean squared error (MSE)")
    ax_b.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_b.grid(False)

    for label, axis in zip(("(a)", "(b)"), (ax_a, ax_b)):
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

    fig.subplots_adjust(left=0.15, right=0.985, top=0.91, bottom=0.22)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"panel_a_source={panel_a_path.name}; panel_b_source={panel_b_path.name}; "
        f"methods={len(panel_a)}; alphas={len(panel_b)}; "
        f"selected_alpha={selected['param_ridge__alpha']:g}; "
        f"panel_a_xlim={panel_a_xlim}; panel_b_ylim={panel_b_ylim}"
    )


if __name__ == "__main__":
    main()
