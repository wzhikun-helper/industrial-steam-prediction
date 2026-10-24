import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from src.models import build_tree_baseline, TREE_BASELINE_PARAMS
from src.validation import make_folds, evaluate_estimator
from src.tree_experiment import run_tree_stage


class TreeTests(unittest.TestCase):
    def test_parameters(self):
        for name, params in TREE_BASELINE_PARAMS.items():
            model = build_tree_baseline(name)
            for key, value in params.items():
                self.assertEqual(model.get_params()[key], value)
            self.assertFalse(hasattr(model, "steps"))
        self.assertEqual(build_tree_baseline("XGBoost").max_depth, 3)
        self.assertEqual(build_tree_baseline("XGBoost").colsample_bytree, .8)

    def test_fresh_estimators_shared_folds_metrics(self):
        X = pd.DataFrame({"x": np.arange(60.)})
        y = pd.Series(np.arange(60.))
        folds = make_folds(60, "TimeSeriesSplit")
        for name in TREE_BASELINE_PARAMS:
            models = []
            def factory():
                model = build_tree_baseline(name)
                model.set_params(n_estimators=2)
                if "n_jobs" in model.get_params():
                    model.set_params(n_jobs=1)
                models.append(model)
                return model
            rows, mean = evaluate_estimator(X, y, factory, folds)
            self.assertEqual(len({id(m) for m in models}), 5)
            self.assertEqual(len(rows), 5)
            self.assertAlmostEqual(mean["rmse"], np.mean([np.sqrt(r["mse"]) for r in rows]))
            self.assertTrue(all(np.isfinite(list(r.values())).all() for r in rows))

    def test_failure_no_success_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            X = pd.DataFrame({"x": np.arange(60.)})
            with patch("src.tree_experiment.evaluate_estimator", side_effect=RuntimeError("synthetic failure")):
                with self.assertRaises(RuntimeError):
                    run_tree_stage(X, X.x, {}, root, "staging/fail")
            self.assertTrue((root / "staging/fail/failure.json").exists())
            self.assertFalse((root / "staging/fail/completion.json").exists())

    def test_existing_directory_no_fit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "staging/existing").mkdir(parents=True)
            with patch("src.tree_experiment.evaluate_estimator") as fit:
                with self.assertRaises(FileExistsError):
                    run_tree_stage(None, None, {}, root, "staging/existing")
                fit.assert_not_called()
