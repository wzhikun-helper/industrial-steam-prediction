import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from src.models import build_ridge_model
from src.validation import make_folds, evaluate_ridge, run_ridge_stage
from src.evaluation import summarize_cv_scores
from src.runtime import create_run_dir


class ValidationTests(unittest.TestCase):
    def test_time_boundaries(self):
        folds = make_folds(2888, "TimeSeriesSplit")
        self.assertEqual(len(folds), 5)
        for i, (tr, va) in enumerate(folds):
            self.assertEqual(len(tr), 483 + i * 481)
            self.assertEqual(len(va), 481)
            self.assertLess(tr[-1], va[0])
            self.assertEqual(len(set(tr) & set(va)), 0)
        self.assertEqual(folds[-1][1][-1], 2887)

    def test_kfold_seed(self):
        actual = make_folds(60, "KFold")
        expected = list(KFold(5, shuffle=True, random_state=42).split(np.arange(60)))
        for (tr, va), (et, ev) in zip(actual, expected):
            np.testing.assert_array_equal(tr, et)
            np.testing.assert_array_equal(va, ev)
        self.assertEqual(sorted(np.concatenate([v for _, v in actual]).tolist()), list(range(60)))

    def test_fold_local_pipeline(self):
        X = pd.DataFrame({"x": np.arange(60, dtype=float) ** 2})
        y = pd.Series(np.arange(60, dtype=float))
        folds = make_folds(60, "TimeSeriesSplit")
        fitted = []
        def factory(alpha):
            model = build_ridge_model(alpha)
            fitted.append(model)
            return model
        with patch("src.validation.build_ridge_model", side_effect=factory):
            rows, summary = evaluate_ridge(X, y, 1.0, folds)
        self.assertEqual(len(fitted), 5)
        for model, (tr, _) in zip(fitted, folds):
            np.testing.assert_allclose(model.named_steps["scaler"].mean_, X.iloc[tr].mean())
            self.assertEqual(model.named_steps["scaler"].n_samples_seen_, len(tr))
        self.assertAlmostEqual(summary["rmse"], np.mean([r["rmse"] for r in rows]))

    def test_rmse_aggregation(self):
        result = summarize_cv_scores({"test_mse": np.array([-1., -9.]),
                                      "test_mae": np.array([-1., -2.]),
                                      "test_r2": np.array([0., 0.])})
        self.assertEqual(result["rmse"], 2.)
        self.assertNotAlmostEqual(result["rmse"], np.sqrt(5.))

    def test_fixed_alphas(self):
        self.assertEqual(build_ridge_model(1.).named_steps["ridge"].alpha, 1.)
        self.assertEqual(build_ridge_model(5.).named_steps["ridge"].alpha, 5.)

    def test_existing_run_no_fit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_run_dir(root, "staging/run")
            with patch("src.validation.evaluate_ridge") as fit:
                with self.assertRaises(FileExistsError):
                    run_ridge_stage(None, None, {}, root, "staging/run")
                fit.assert_not_called()

    def test_stage_dry_run_no_fit(self):
        from scripts.run_experiment import main
        from test_foundation import FoundationTests
        fixture = FoundationTests()
        fixture.setUp()
        try:
            fixture.setup_config()
            with patch("src.validation.run_ridge_stage") as stage:
                self.assertEqual(main(["--config", "config.yaml", "--output-dir", "staging/check",
                                       "--stage", "ridge-baseline", "--dry-run"], fixture.root), 0)
                stage.assert_not_called()
            self.assertFalse((fixture.root / "staging").exists())
        finally:
            fixture.doCleanups()
