"""Isolated baseline reproduction with fixed, prospective comparison tolerances."""
import csv
import json
import platform
from importlib.metadata import version
import numpy as np
import pandas as pd
from src.models import TREE_BASELINE_PARAMS, build_tree_baseline
from src.validation import make_folds, evaluate_estimator
from src.runtime import create_run_dir, open_new_output

ATOL, RTOL = 1e-12, 1e-10
METRICS = ["mse", "rmse", "mae", "r2"]
SOURCES = dict(zip(TREE_BASELINE_PARAMS, ["random_forest_cv_metrics.csv",
    "gbdt_cv_metrics.csv", "xgboost_cv_metrics.csv", "lightgbm_cv_metrics.csv"]))


def compare_results(root, fold_rows, summaries):
    actual = pd.DataFrame(fold_rows)
    means = pd.DataFrame(summaries)
    frozen_means = pd.read_csv(root / "results/final_model_comparison.csv")
    report = [f"# Tree baseline comparison\n\nProspective tolerance: atol={ATOL}, rtol={RTOL}.",
              "Model order: Random Forest, GBDT, XGBoost, LightGBM. Raw features; no scaler.",
              "Indices are zero-based source row positions; identical TimeSeriesSplit folds for all models."]
    statuses = {}
    for name, source in SOURCES.items():
        a = actual[actual.model == name].sort_values("fold")
        b = pd.read_csv(root / "results" / source).sort_values("fold")
        if a.fold.tolist() != b.fold.tolist():
            raise ValueError(f"Fold identifiers differ for {name}")
        delta = a[METRICS].to_numpy() - b[METRICS].to_numpy()
        am = means[means.model == name].iloc[0]
        bm = frozen_means[frozen_means.model == name].iloc[0]
        md = np.array([am[m] - bm[m + "_mean"] for m in METRICS])
        ok = np.allclose(a[METRICS], b[METRICS], atol=ATOL, rtol=RTOL) and np.allclose(
            [am[m] for m in METRICS], [bm[m+"_mean"] for m in METRICS], atol=ATOL, rtol=RTOL)
        statuses[name] = "PASS" if ok else "NUMERIC DIFFERENCE"
        report.extend([f"\n## {name}: {statuses[name]}", f"Frozen source: results/{source}",
                       "| fold | metric | actual | frozen | difference |", "|---|---|---|---|---|"])
        for i, fold in enumerate(a.fold):
            for j, m in enumerate(METRICS):
                report.append(f"| {fold} | {m} | {a.iloc[i][m]:.17g} | {b.iloc[i][m]:.17g} | {delta[i,j]:.17g} |")
        for j, m in enumerate(METRICS):
            report.append(f"| mean | {m} | {am[m]:.17g} | {bm[m+'_mean']:.17g} | {md[j]:.17g} |")
        report.append(f"Maximum absolute fold difference: {np.abs(delta).max():.17g}; mean difference: {np.abs(md).max():.17g}.")
    report.append("Original per-fold index artifacts and full original runtime package versions are unavailable; original indices are reconstructed from Notebook's TimeSeriesSplit(5). Compare metadata.json with environment.yml; version differences do not establish the cause of numerical differences. No retries or parameter changes were used.")
    return "\n\n".join(report), statuses


def run_tree_stage(X, y, config, root, output_relative):
    # Preflight imports before creating a run. No installs or fallback estimators.
    models = {name: build_tree_baseline(name) for name in TREE_BASELINE_PARAMS}
    create_run_dir(root, output_relative)
    def save(name, value):
        with open_new_output(root, output_relative, name) as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
    save("config_snapshot.json", config)
    save("metadata.json", {"stage": "tree-baselines", "mode": "migration_consistency_check",
         "random_state": 42, "preprocessing": "raw 38 features; no scaler",
         "versions": {"python": platform.python_version(), **{n: version(n) for n in
             ("numpy", "pandas", "scipy", "scikit-learn", "xgboost", "lightgbm")}},
         "explicit_parameters": TREE_BASELINE_PARAMS,
         "resolved_parameters": {n: m.get_params() for n, m in models.items()},
         "tolerance": {"atol": ATOL, "rtol": RTOL}})
    try:
        folds = make_folds(len(X), "TimeSeriesSplit")
        save("fold_indices.json", [{"fold": i, "train": tr.tolist(), "validation": va.tolist()}
             for i, (tr, va) in enumerate(folds, 1)])
        rows, summaries = [], []
        for name in models:
            metrics, mean = evaluate_estimator(X, y, lambda: build_tree_baseline(name), folds)
            rows.extend({"model": name, **r} for r in metrics)
            summaries.append({"model": name, **mean})
        for filename, records in (("fold_metrics.csv", rows), ("mean_metrics.csv", summaries)):
            with open_new_output(root, output_relative, filename) as stream:
                writer = csv.DictWriter(stream, fieldnames=list(records[0]))
                writer.writeheader()
                writer.writerows(records)
        report, statuses = compare_results(root, rows, summaries)
        with open_new_output(root, output_relative, "comparison_report.md") as stream:
            stream.write(report)
        save("completion.json", {"execution": "complete", "fits": 20, "comparison": statuses})
        return summaries
    except Exception as error:
        save("failure.json", {"status": "failed", "type": type(error).__name__, "message": str(error)})
        raise
