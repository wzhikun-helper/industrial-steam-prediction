"""Fixed folds and fold-local Ridge evaluation; no parameter selection."""
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, KFold
from src.evaluation import evaluate_regression, summarize_cv_scores
from src.models import build_ridge_model


def make_folds(n_samples, protocol):
    if protocol == "TimeSeriesSplit":
        splitter = TimeSeriesSplit(n_splits=5)
    elif protocol == "KFold":
        splitter = KFold(n_splits=5, shuffle=True, random_state=42)
    else:
        raise ValueError("Unknown validation protocol")
    return list(splitter.split(np.arange(n_samples)))


def evaluate_ridge(X, y, alpha, folds):
    return evaluate_estimator(X, y, lambda: build_ridge_model(alpha=alpha), folds)


def evaluate_estimator(X, y, factory, folds, fitted_callback=None):
    rows = []
    for fold, (train, validation) in enumerate(folds, 1):
        model = factory()
        model.fit(X.iloc[train], y.iloc[train])
        if fitted_callback is not None:
            fitted_callback(fold, model)
        metrics = evaluate_regression(y.iloc[validation], model.predict(X.iloc[validation]))
        rows.append({"fold": fold, **metrics})
    scores = {
        "test_mse": -np.array([r["mse"] for r in rows]),
        "test_mae": -np.array([r["mae"] for r in rows]),
        "test_r2": np.array([r["r2"] for r in rows]),
    }
    return rows, summarize_cv_scores(scores)


def run_ridge_stage(X, y, config, root, output_relative):
    import csv
    import json
    import platform
    from datetime import datetime, timezone
    from importlib.metadata import version
    from src.runtime import create_run_dir, open_new_output

    create_run_dir(root, output_relative)

    def save_json(name, value):
        with open_new_output(root, output_relative, name) as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)

    try:
        save_json("config_snapshot.json", config)
        save_json("metadata.json", {
            "stage": "ridge-baseline", "mode": "migration_consistency_check",
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "random_state": config["random_state"],
            "ridge_random_state": None,
            "ridge_solver": "auto (deterministic)",
            "versions": {"python": platform.python_version(), **{
                name: version(name) for name in ("numpy", "pandas", "scipy", "scikit-learn")}},
            "models": {"Ridge": {"alpha": 1.0}, "Best Ridge": {"alpha": 5.0}},
            "rmse_aggregation": config["rmse_aggregation"],
            "status": "see completion.json or failure.json",
        })
        all_rows, summaries = [], []
        for protocol in ("TimeSeriesSplit", "KFold"):
            folds = make_folds(len(X), protocol)
            save_json(f"{protocol}_fold_indices.json", [
                {"fold": i, "train": tr.tolist(), "validation": va.tolist()}
                for i, (tr, va) in enumerate(folds, 1)])
            for name, alpha in (("Ridge", 1.0), ("Best Ridge", 5.0)):
                rows, summary = evaluate_ridge(X, y, alpha, folds)
                all_rows.extend({"protocol": protocol, "model": name, "alpha": alpha, **r} for r in rows)
                summaries.append({"protocol": protocol, "model": name, "alpha": alpha, **summary})
        for filename, rows in (("fold_metrics.csv", all_rows), ("mean_metrics.csv", summaries)):
            with open_new_output(root, output_relative, filename) as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        save_json("completion.json", {"status": "complete", "fits": len(all_rows),
                                      "purpose": "migration check, not new paper results"})
    except Exception as error:
        import traceback
        try:
            save_json("failure.json", {"status": "failed", "type": type(error).__name__,
                                      "message": str(error), "traceback": traceback.format_exc()})
        except OSError:
            pass  # Keep the original exception if failure recording itself is unavailable.
        raise
    return summaries
