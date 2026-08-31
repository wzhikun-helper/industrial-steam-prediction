"""Generate the Chinese Fig. 3 master for ZJU Engineering Science."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea
from matplotlib.ticker import FixedFormatter, FixedLocator, MaxNLocator, NullFormatter

from _style import PALETTE, paper_style, save


MM_TO_INCH = 1 / 25.4
FIG_WIDTH_MM = 164
FIG_HEIGHT_MM = 61
VALIDATION_CONTEXT = "5-fold TimeSeriesSplit"
UNCERTAINTY_KIND = "Panel (a): 1 SD across five folds; Panel (b): mean MSE only"
SIGNIFICANCE_INFERENCE = False
PANEL_A_COLUMNS = {"model", "mse_mean", "mse_std"}
PANEL_B_COLUMNS = {"param_ridge__alpha", "mean_mse", "std_test_score"}


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


def add_box(ax, box, xy, xycoords, alignment=(0.5, 0.5)):
    ax.add_artist(
        AnnotationBbox(
            box,
            xy,
            xycoords=xycoords,
            box_alignment=alignment,
            frameon=False,
            pad=0,
        )
    )


def limits_with_errors(mean, spread, fraction=0.06):
    lower = float(np.min(mean - spread))
    upper = float(np.max(mean + spread))
    span = upper - lower
    pad = fraction * span if span > 0 else max(abs(lower), 1.0) * fraction
    return lower - pad, upper + pad


def load_inputs(project_root):
    results_dir = project_root / "results"
    panel_a_path = results_dir / "paper_fig3_feature_method_comparison.csv"
    panel_b_path = results_dir / "paper_fig3_ridge_alpha_sensitivity.csv"
    if not panel_b_path.exists():
        raise FileNotFoundError(panel_b_path)
    return (
        pd.read_csv(panel_a_path),
        pd.read_csv(panel_b_path),
        panel_a_path,
        panel_b_path,
    )


def main():
    project_root = Path(__file__).resolve().parents[2]
    output_stem = project_root / "figures" / "paper" / "fig3_feature_ridge_sensitivity_zh"
    panel_a, panel_b, panel_a_path, panel_b_path = load_inputs(project_root)

    missing_a = PANEL_A_COLUMNS.difference(panel_a.columns)
    missing_b = PANEL_B_COLUMNS.difference(panel_b.columns)
    if missing_a:
        raise ValueError(f"Panel （a） missing columns: {sorted(missing_a)}")
    if missing_b:
        raise ValueError(f"Panel （b） missing columns: {sorted(missing_b)}")

    panel_a = panel_a.copy()
    panel_b = panel_b.copy()
    for column in ("mse_mean", "mse_std"):
        panel_a[column] = pd.to_numeric(panel_a[column], errors="raise")
    for column in ("param_ridge__alpha", "mean_mse", "std_test_score"):
        panel_b[column] = pd.to_numeric(panel_b[column], errors="raise")

    if panel_a["model"].duplicated().any():
        raise ValueError("Panel （a） model names must be unique.")
    if len(panel_a) != 3:
        raise ValueError(f"Expected 3 feature-processing methods, found {len(panel_a)}.")
    if len(panel_b) != 10:
        raise ValueError(f"Expected 10 alpha values, found {len(panel_b)}.")
    if (panel_a["mse_std"] < 0).any() or (panel_b["std_test_score"] < 0).any():
        raise ValueError("Standard deviations must be non-negative.")
    if (panel_b["param_ridge__alpha"] <= 0).any():
        raise ValueError("All alpha values must be positive for the log scale.")
    if not np.isfinite(panel_a[["mse_mean", "mse_std"]].to_numpy()).all():
        raise ValueError("Panel （a） contains non-finite values.")
    if not np.isfinite(
        panel_b[["param_ridge__alpha", "mean_mse", "std_test_score"]].to_numpy()
    ).all():
        raise ValueError("Panel （b） contains non-finite values.")

    panel_a = panel_a.sort_values("mse_mean", ascending=True, kind="stable").reset_index(drop=True)
    panel_b = panel_b.sort_values("param_ridge__alpha", kind="stable").reset_index(drop=True)
    selected_index = int(panel_b["mean_mse"].idxmin())
    selected = panel_b.loc[selected_index]

    chinese_font, chinese_family, chinese_path = first_available_font(
        ("SimSun", "NSimSun", "Source Han Serif SC", "Noto Serif CJK SC")
    )
    latin_font, latin_family, latin_path = first_available_font(
        ("Times New Roman", "STIX Two Text", "Liberation Serif", "DejaVu Serif")
    )
    math_font, math_family, math_path = first_available_font(
        ("STIXGeneral", "STIX Two Math", "Cambria Math")
    )

    paper_style(font="sans")
    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(FIG_WIDTH_MM * MM_TO_INCH, FIG_HEIGHT_MM * MM_TO_INCH),
        gridspec_kw={"width_ratios": (1.45, 1.00), "wspace": 0.34},
    )

    accent = PALETTE[0]
    neutral = "#595959"
    whisker = "#858585"

    # Panel （a）: feature-processing methods, mean MSE ±1 SD.
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
            fontproperties=latin_font,
        )

    panel_a_xlim = limits_with_errors(
        panel_a["mse_mean"].to_numpy(), panel_a["mse_std"].to_numpy()
    )
    ax_a.set_xlim(panel_a_xlim)
    ax_a.set_ylim(len(panel_a) - 0.5, -0.82)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(panel_a["model"])
    for tick in ax_a.get_yticklabels():
        tick.set_fontproperties(latin_font)
        if tick.get_text() == "Ridge":
            tick.set_color(accent)
    ax_a.set_xlabel("")
    ax_a.set_ylabel("")
    ax_a.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_a.xaxis.grid(True, color="#E8E8E8", linewidth=0.4)
    ax_a.yaxis.grid(False)

    panel_a_note = mixed_text_box(
        (
            ("误差棒：", chinese_font, 5.7, "#777777"),
            ("±1 SD", latin_font, 5.7, "#777777"),
        )
    )
    add_box(ax_a, panel_a_note, (0.01, 0.93), ax_a.transAxes, (0, 1))

    panel_a_xlabel = mixed_text_box(
        (
            ("均方误差（", chinese_font, 8.0, "#222222"),
            ("MSE", latin_font, 8.0, "#222222"),
            ("）", chinese_font, 8.0, "#222222"),
        )
    )
    add_box(ax_a, panel_a_xlabel, (0.5, -0.19), ax_a.transAxes)

    # Panel （b）: mean-MSE alpha sensitivity only; no SD bars or band.
    alpha = panel_b["param_ridge__alpha"].to_numpy()
    mean_mse = panel_b["mean_mse"].to_numpy()
    ax_b.scatter(alpha, mean_mse, marker="o", s=17, color=accent, zorder=2)
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

    optimum_note = mixed_text_box(
        (
            ("最低均值：", chinese_font, 5.5, "#8A8A8A"),
            (r"$\alpha$", math_font, 5.5, "#8A8A8A"),
            (f" = {selected['param_ridge__alpha']:g}", latin_font, 5.5, "#8A8A8A"),
        ),
        sep=0.5,
    )
    ax_b.add_artist(
        AnnotationBbox(
            optimum_note,
            (selected["param_ridge__alpha"], selected["mean_mse"]),
            xycoords="data",
            xybox=(3, 10),
            boxcoords="offset points",
            box_alignment=(0, 0),
            frameon=False,
            pad=0,
        )
    )

    panel_b_ylim = limits_with_errors(mean_mse, np.zeros_like(mean_mse), fraction=0.12)
    ax_b.set_xscale("log")
    ax_b.set_xlim(float(alpha.min()) * 0.8, float(alpha.max()) * 1.25)
    ax_b.set_ylim(panel_b_ylim)
    major_alpha = [0.01, 0.1, 1, 10, 100]
    ax_b.xaxis.set_major_locator(FixedLocator(major_alpha))
    ax_b.xaxis.set_major_formatter(FixedFormatter(["0.01", "0.1", "1", "10", "100"]))
    ax_b.xaxis.set_minor_formatter(NullFormatter())
    ax_b.set_xlabel("")
    ax_b.set_ylabel(
        r"均方误差（$\mathrm{MSE}$）",
        fontproperties=chinese_font,
        fontsize=8.0,
        labelpad=7,
    )
    ax_b.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax_b.grid(False)

    panel_b_xlabel = mixed_text_box(
        (
            ("Ridge", latin_font, 8.0, "#222222"),
            ("正则化参数", chinese_font, 8.0, "#222222"),
            (r"$\alpha$", math_font, 8.0, "#222222"),
        ),
        sep=1.0,
    )
    add_box(ax_b, panel_b_xlabel, (0.5, -0.19), ax_b.transAxes)

    for axis in (ax_a, ax_b):
        axis.tick_params(axis="both", direction="in")
        for tick in (*axis.get_xticklabels(), *axis.get_yticklabels()):
            if tick.get_text() not in set(panel_a["model"]):
                tick.set_fontproperties(latin_font)

    for label, axis in zip(("a", "b"), (ax_a, ax_b)):
        panel_label = mixed_text_box(
            (
                ("（", chinese_font, 7.0, "#222222"),
                (label, latin_font, 7.0, "#222222"),
                ("）", chinese_font, 7.0, "#222222"),
            )
        )
        add_box(axis, panel_label, (0.0, 0.995), axis.transAxes, (0, 1))

    fig.subplots_adjust(left=0.17, right=0.985, top=0.91, bottom=0.22)
    save(fig, output_stem, formats=("pdf", "svg", "png"), dpi=300)
    plt.close(fig)

    print(
        "[audit] "
        f"panel_a_source={panel_a_path.name}; panel_b_source={panel_b_path.name}; "
        f"methods={len(panel_a)}; alphas={len(panel_b)}; "
        f"selected_alpha={selected['param_ridge__alpha']:g}; "
        f"panel_a_xlim={panel_a_xlim}; panel_b_ylim={panel_b_ylim}; "
        "panel_a=mean_MSE_plus_minus_1_SD; panel_b=mean_MSE_only; "
        f"chinese_font={chinese_family}:{chinese_path}; "
        f"latin_font={latin_family}:{latin_path}; "
        f"math_font={math_family}:{math_path}; panel_labels=（a）,（b）; ticks=in"
    )


if __name__ == "__main__":
    main()
