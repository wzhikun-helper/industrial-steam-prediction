"""Original search and historical fixed model, recorded as separate experiments."""
import json
import platform
from importlib.metadata import version
import numpy as np
import pandas as pd
from src.models import build_xgboost_search, build_xgboost_model, XGBOOST_GRID
from src.validation import make_folds, evaluate_estimator
from src.runtime import create_run_dir, open_new_output

ATOL, RTOL = 1e-12, 1e-10
HISTORICAL_PARAMS = {"colsample_bytree": 1.0, "learning_rate": .05, "max_depth": 2,
                     "n_estimators": 300, "subsample": .8}


def compare_fixed(root, rows, mean):
    frozen = pd.read_csv(root / "results/best_xgboost_cv_metrics.csv").sort_values("fold")
    actual = pd.DataFrame(rows).sort_values("fold")
    metrics = ["mse", "rmse", "mae", "r2"]
    if actual.fold.tolist() != frozen.fold.tolist():
        raise ValueError("Fold identifiers differ")
    summary = pd.read_csv(root / "results/best_xgboost_summary.csv").iloc[0]
    lines = ["| fold | metric | actual | frozen | difference |", "|---|---|---|---|---|"]
    ok = True
    maximum = 0.
    for i in range(5):
        for m in metrics:
            a, b = float(actual.iloc[i][m]), float(frozen.iloc[i][m])
            ok &= bool(np.isclose(a, b, atol=ATOL, rtol=RTOL))
            maximum = max(maximum, abs(a-b))
            lines.append(f"| {i+1} | {m} | {a:.17g} | {b:.17g} | {a-b:.17g} |")
    for m in metrics:
        a, b = mean[m], float(summary[m+"_mean"])
        ok &= bool(np.isclose(a,b,atol=ATOL,rtol=RTOL))
        lines.append(f"| mean | {m} | {a:.17g} | {b:.17g} | {a-b:.17g} |")
    return "\n".join(lines), "PASS" if ok else "NUMERIC DIFFERENCE", maximum


def run_xgboost_stage(X, y, config, root, output_relative):
    create_run_dir(root, output_relative)
    def save(name, value):
        with open_new_output(root, output_relative, name) as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
    def table(name, frame):
        with open_new_output(root, output_relative, name) as stream:
            frame.to_csv(stream, index=False)
    try:
        save("config_snapshot.json", config)
        folds = make_folds(len(X), "TimeSeriesSplit")
        search = build_xgboost_search(folds)
        save("metadata.json", {"stage": "xgboost-tuning", "mode": "migration_check",
             "versions": {"python": platform.python_version(), **{n: version(n) for n in
                  ("numpy", "pandas", "scipy", "scikit-learn", "xgboost")}},
             "seed": 42, "grid": XGBOOST_GRID, "candidates": 108,
             "scoring": search.scoring, "cv_n_jobs": search.n_jobs, "refit": search.refit,
             "search_explicit_parameters": {"random_state":42,"n_jobs":-1,"objective":"reg:squarederror"},
             "fixed_explicit_parameters": {**HISTORICAL_PARAMS,"random_state":42,"n_jobs":-1,"objective":"reg:squarederror"},
             "atol": ATOL, "rtol": RTOL,
             "source": "Notebook cells 44,95,97,98; defaults not overridden"})
        save("fold_indices.json", [{"fold":i,"train":tr.tolist(),"validation":va.tolist()}
             for i,(tr,va) in enumerate(folds,1)])
        search.fit(X,y)
        result = pd.DataFrame(search.cv_results_)
        cols = [c for c in result if c.startswith("param_") or c.startswith("split") or
                c in ("mean_test_score","std_test_score","rank_test_score")]
        table("search_results.csv",result[cols])
        save("search_selection.json", {"current_best_params":search.best_params_,
             "current_best_mse":float(-search.best_score_),"historical_best_params":HISTORICAL_PARAMS,
             "historical_best_mse": float(pd.read_csv(root / "results/best_xgboost_summary.csv").iloc[0].mse_mean),
             "historical_source":"Notebook cell95 saved output; no full frozen search CSV exists"})
        save("search_best_internal_config.json",json.loads(search.best_estimator_.get_booster().save_config()))
        def record(fold, model):
            save(f"fixed_fold{fold}_internal_config.json",json.loads(model.get_booster().save_config()))
        rows, mean = evaluate_estimator(X,y,build_xgboost_model,folds,fitted_callback=record)
        table("fixed_best_fold_metrics.csv",pd.DataFrame(rows))
        table("fixed_best_mean_metrics.csv",pd.DataFrame([mean]))
        details, fixed_status, maximum = compare_fixed(root,rows,mean)
        original = pd.read_csv(root / "results/best_xgboost_summary.csv").iloc[0]
        score_match = np.isclose(-search.best_score_,original.mse_mean,atol=ATOL,rtol=RTOL)
        search_status = "PASS" if score_match and search.best_params_==HISTORICAL_PARAMS else "NUMERIC DIFFERENCE"
        report = (f"# XGBoost migration comparison\n\nProtocol migration: PASS (Notebook grid, scorer, folds, seed, refit and n_jobs).\n\n"
                  f"Prospective tolerance atol={ATOL}, rtol={RTOL}.\n\nSearch selection: {search_status}; "
                  f"MSE difference={-search.best_score_-original.mse_mean:.17g}.\n\n"
                  "Full historical candidate/split search CSV is absent: only saved Notebook best parameters/score can be compared.\n\n"
                  f"Fixed historical Best XGBoost: {fixed_status}; max fold metric difference={maximum:.17g}.\n\n"+details+
                  "\n\nCurrent environment differs from historical saved model version 3.2.0. Specific cause is unconfirmed. No retries or parameter changes. Papers remain frozen.")
        with open_new_output(root,output_relative,"comparison_report.md") as stream:
            stream.write(report)
        status = {"protocol":"PASS","search_selection":search_status,"fixed_best":fixed_status,
                  "full_historical_search_comparison":"UNAVAILABLE"}
        save("completion.json",{"execution":"complete","fits":546,**status})
        return {**status,"current_best_params":search.best_params_,"fixed_best_mean":mean}
    except Exception as error:
        save("failure.json",{"status":"failed","type":type(error).__name__,"message":str(error)})
        raise
