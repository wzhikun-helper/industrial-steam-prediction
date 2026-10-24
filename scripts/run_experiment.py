"""Data validation and explicit fixed-parameter baseline migration checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_utils import load_steam_data, validate_steam_data
from src.runtime import project_path, validate_output_dir


def load_config(root, relative, *, require_data=True):
    # JSON is a YAML 1.2 subset, avoiding an additional YAML dependency.
    config = json.loads(project_path(root, relative).read_text(encoding="utf-8"))
    data = config["data"]
    expected = {
        "primary": {"name": "TimeSeriesSplit", "n_splits": 5},
        "comparison": {"name": "KFold", "n_splits": 5, "shuffle": True, "random_state": 42},
    }
    if (data["features"] != [f"V{i}" for i in range(38)]
        or data["target"] != "target"
        or data["train_shape"] != [2888, 39]
        or data["test_shape"] != [1925, 38]
        or config["random_state"] != 42
        or config["validation"] != expected
        or config["rmse_aggregation"] != "mean_of_fold_rmse"
        or config["output_roots"] != ["staging", "reproduction"]):
        raise ValueError("Configuration differs from frozen protocol")
    for key in ("train", "test"):
        if require_data and not project_path(root, data[key]).is_file():
            raise ValueError(f"Missing data file: {data[key]}")
    return config


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/experiment.yaml")
    parser.add_argument("--output-dir", required=True)
    checks=parser.add_mutually_exclusive_group()
    checks.add_argument("--dry-run", action="store_true")
    checks.add_argument("--check-only",action="store_true",help="Config/output preflight without requiring or reading raw data; never trains")
    parser.add_argument("--stage", choices=["ridge-baseline", "tree-baselines", "feature-processing", "ridge-tuning", "xgboost-tuning", "fusion", "shap", "final-prediction"])
    args = parser.parse_args(argv)
    try:
        config = load_config(root, args.config,require_data=not args.check_only)
        output = validate_output_dir(root, args.output_dir)
        if args.check_only:
            available={k:project_path(root,config["data"][k]).is_file() for k in ("train","test")}
            print(json.dumps({"mode":"check-only","stage":args.stage,"config":"PASS","output_safety":"PASS",
                              "data_available":available,"raw_schema_checked":False,"training_executed":False,
                              "output_created":False}))
            return 0
        if not args.dry_run and args.stage is None:
            raise ValueError("Select an explicit --stage or use --dry-run")
        if args.stage in ("shap", "final-prediction"):
            if not args.dry_run:
                raise ValueError(f"Real {args.stage} execution is disabled")
            print(f"{args.stage}: precheck PASS; real execution disabled; no data loaded, output not created")
            return 0
        if args.stage == "fusion":
            from src.fusion_experiment import protocol_precheck, run_real_fusion
            if not args.dry_run:
                run_real_fusion()
            print(json.dumps(protocol_precheck(config["data"]["train_shape"][0]), indent=2))
            print(f"Output safety PASS: {output} (not created); no data loaded or models fitted")
            return 0
        data = config["data"]
        train_path = project_path(root, data["train"])
        test_path = project_path(root, data["test"])
        train, test = load_steam_data(root, train_path, test_path)
        validate_steam_data(train, test, data["features"], data["target"],
                            data["train_shape"], data["test_shape"])
        if not args.dry_run:
            from src.data_utils import split_features_target
            from src.validation import run_ridge_stage
            X, y, _ = split_features_target(train, test)
            if args.stage == "tree-baselines":
                from src.tree_experiment import run_tree_stage
                summaries = run_tree_stage(X, y, config, root, args.output_dir)
            elif args.stage in ("feature-processing", "ridge-tuning"):
                from src.feature_experiment import run_feature_stage
                summaries = run_feature_stage(X, y, config, root, args.output_dir, args.stage)
            elif args.stage == "xgboost-tuning":
                from src.xgboost_experiment import run_xgboost_stage
                summaries = run_xgboost_stage(X, y, config, root, args.output_dir)
            else:
                summaries = run_ridge_stage(X, y, config, root, args.output_dir)
            print(json.dumps(summaries, indent=2))
            print(f"{args.stage} migration check complete: {output}")
            return 0
        print(f"DRY-RUN PASS: train={train.shape}, test={test.shape}, features=38")
        print(f"Output safety PASS: {output} (not created)")
        print("No experiment executed. Training requires an explicit baseline stage.")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
