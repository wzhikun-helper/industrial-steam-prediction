"""Notebook feature-processing and Ridge search reproduction, isolated outputs."""
import csv
import json
import platform
from importlib.metadata import version
import numpy as np
import pandas as pd
from src.models import build_feature_pipeline, build_ridge_search, RIDGE_ALPHA_GRID
from src.validation import make_folds, evaluate_estimator
from src.runtime import create_run_dir, open_new_output

ATOL, RTOL = 1e-12, 1e-10
METRICS = ["mse", "rmse", "mae", "r2"]
FEATURE_SOURCES = {"Ridge": "ridge_baseline_cv_metrics.csv",
                   "KBest20 + Ridge": "kbest20_ridge_cv_metrics.csv",
                   "PCA95 + Ridge": "pca95_ridge_cv_metrics.csv"}


def comparison(root, stage, rows, means):
    lines = [f"# {stage} comparison", f"Prospective tolerance: atol={ATOL}, rtol={RTOL}.",
             "| item | maximum absolute difference | match |", "|---|---:|---|"]
    matches = []
    def check(label, actual, frozen):
        a, b = np.asarray(actual, dtype=float), np.asarray(frozen, dtype=float)
        ok = a.shape == b.shape and np.allclose(a, b, atol=ATOL, rtol=RTOL)
        matches.append(ok)
        lines.append(f"| {label} | {np.max(np.abs(a-b)):.17g} | {ok} |")
    if stage == "feature-processing":
        frozen_mean = pd.read_csv(root / "results/feature_method_comparison.csv")
        for name, source in FEATURE_SOURCES.items():
            a = pd.DataFrame([r for r in rows if r["model"] == name]).sort_values("fold")
            b = pd.read_csv(root / "results" / source).sort_values("fold")
            if a.fold.tolist() != b.fold.tolist():
                raise ValueError("Fold IDs differ")
            for metric in METRICS:
                check(f"{name} folds {metric}", a[metric], b[metric])
            am = next(m for m in means if m["model"] == name)
            bm = frozen_mean[frozen_mean.model == name].iloc[0]
            check(name + " means", [am[m] for m in METRICS], [bm[m+"_mean"] for m in METRICS])
    else:
        a = pd.DataFrame(rows).sort_values("param_ridge__alpha")
        b = pd.read_csv(root / "results/ridge_alpha_tuning.csv").sort_values("param_ridge__alpha")
        for col in ("param_ridge__alpha", "mean_test_score", "mean_mse", "std_test_score", "rank_test_score"):
            check(col, a[col], b[col])
        lines.append("Original frozen tuning CSV has no individual split scores; migration split scores are retained in tuning_results.csv.")
    lines.append("No protocol adjustment or retry; differences are retained. Current defaults and software versions may differ from historical runtime. See metadata.json.")
    return "\n\n".join(lines), "PASS" if all(matches) else "NUMERIC DIFFERENCE"


def run_feature_stage(X, y, config, root, output_relative, stage):
    if stage not in ("feature-processing", "ridge-tuning"):
        raise ValueError("Unsupported stage")
    create_run_dir(root, output_relative)
    def save(name, value):
        with open_new_output(root, output_relative, name) as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
    def save_csv(name, records):
        with open_new_output(root, output_relative, name) as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    try:
        save("config_snapshot.json", config)
        save("metadata.json", {"stage": stage, "mode": "migration_consistency_check",
             "random_state": 42, "versions": {"python": platform.python_version(), **{
                 n: version(n) for n in ("numpy", "pandas", "scipy", "scikit-learn")}},
             "tolerance": {"atol": ATOL, "rtol": RTOL}, "alpha_grid": RIDGE_ALPHA_GRID,
             "search": {"scoring": "neg_mean_squared_error", "refit": True, "n_jobs": -1},
             "pipelines": {"Ridge": "StandardScaler -> Ridge(alpha=1)",
                 "KBest20 + Ridge": "SelectKBest(f_regression,k=20) -> StandardScaler -> Ridge(alpha=1)",
                 "PCA95 + Ridge": "StandardScaler -> PCA(n_components=0.95) -> Ridge(alpha=1)"}})
        folds = make_folds(len(X), "TimeSeriesSplit")
        save("fold_indices.json", [{"fold": i, "train": tr.tolist(), "validation": va.tolist()}
             for i, (tr, va) in enumerate(folds, 1)])
        rows, means = [], []
        if stage == "feature-processing":
            for name in FEATURE_SOURCES:
                metrics, mean = evaluate_estimator(X, y, lambda: build_feature_pipeline(name), folds)
                rows.extend({"model": name, **r} for r in metrics)
                means.append({"model": name, **mean})
            save_csv("fold_metrics.csv", rows)
            save_csv("mean_metrics.csv", means)
        else:
            search = build_ridge_search(folds)
            search.fit(X, y)
            result = pd.DataFrame(search.cv_results_)
            cols = ["param_ridge__alpha", "mean_test_score", "std_test_score", "rank_test_score"]
            cols += [f"split{i}_test_score" for i in range(5)]
            result = result[cols].copy()
            result["mean_mse"] = -result["mean_test_score"]
            rows = result.to_dict("records")
            save_csv("tuning_results.csv", rows)
            means = {"selected_alpha": float(search.best_params_["ridge__alpha"]),
                     "best_mean_mse": float(-search.best_score_), "refit": True}
            save("selection.json", means)
        report, status = comparison(root, stage, rows, means)
        with open_new_output(root, output_relative, "comparison_report.md") as stream:
            stream.write(report)
        save("completion.json", {"execution": "complete", "comparison": status,
                                 "fits": 15 if stage == "feature-processing" else 51})
        return means
    except Exception as error:
        save("failure.json", {"status": "failed", "type": type(error).__name__, "message": str(error)})
        raise
