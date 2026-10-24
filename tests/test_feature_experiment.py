import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.feature_selection import f_regression
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from src.models import build_feature_pipeline, build_ridge_search, RIDGE_ALPHA_GRID
from src.validation import evaluate_estimator, make_folds
from src.feature_experiment import run_feature_stage


class FeatureTests(unittest.TestCase):
    def data(self):
        rng = np.random.RandomState(42)
        X = pd.DataFrame(rng.normal(size=(180, 38)) + np.arange(180)[:, None] / 10)
        return X, pd.Series(X[0] + rng.normal(size=180))

    def test_pipeline_structure(self):
        expected = {"Ridge": ["scaler", "ridge"], "KBest20 + Ridge": ["kbest", "scaler", "ridge"],
                    "PCA95 + Ridge": ["scaler", "pca", "ridge"]}
        for name, steps in expected.items():
            model = build_feature_pipeline(name)
            self.assertEqual(list(model.named_steps), steps)
            self.assertEqual(model.named_steps["ridge"].alpha, 1.)
        self.assertIs(build_feature_pipeline("KBest20 + Ridge").named_steps["kbest"].score_func, f_regression)
        self.assertEqual(build_feature_pipeline("KBest20 + Ridge").named_steps["kbest"].k, 20)
        self.assertEqual(build_feature_pipeline("PCA95 + Ridge").named_steps["pca"].n_components, .95)

    def test_fold_local_transforms(self):
        X, y = self.data()
        folds = make_folds(len(X), "TimeSeriesSplit")
        for name in ("Ridge", "KBest20 + Ridge", "PCA95 + Ridge"):
            fitted = []
            def factory():
                model = build_feature_pipeline(name)
                fitted.append(model)
                return model
            rows, mean = evaluate_estimator(X, y, factory, folds)
            self.assertEqual(len({id(m) for m in fitted}), 5)
            self.assertAlmostEqual(mean["rmse"], np.mean([r["rmse"] for r in rows]))
            for model, (tr, va) in zip(fitted, folds):
                training = X.iloc[tr]
                if "kbest" in model.named_steps:
                    selector = model.named_steps["kbest"]
                    np.testing.assert_allclose(selector.scores_, f_regression(training, y.iloc[tr])[0])
                    training = selector.transform(training)
                scaler = model.named_steps["scaler"]
                self.assertEqual(scaler.n_samples_seen_, len(tr))
                np.testing.assert_allclose(scaler.mean_, np.asarray(training).mean(axis=0))
                if "pca" in model.named_steps:
                    pca = model.named_steps["pca"]
                    expected = PCA(n_components=.95).fit(scaler.transform(training))
                    self.assertEqual(pca.n_samples_, len(tr))
                    np.testing.assert_allclose(pca.explained_variance_, expected.explained_variance_)

    def test_search_protocol(self):
        X, y = self.data()
        folds = make_folds(len(X), "TimeSeriesSplit")
        search = build_ridge_search(folds)
        self.assertEqual(RIDGE_ALPHA_GRID, [.01, .1, .5, 1, 2, 5, 10, 20, 50, 100])
        self.assertEqual(search.param_grid, {"ridge__alpha": RIDGE_ALPHA_GRID})
        self.assertEqual(search.scoring, "neg_mean_squared_error")
        self.assertIs(search.refit, True)
        self.assertEqual(search.n_jobs, -1)
        self.assertIs(search.cv, folds)
        self.assertLess(folds[0][0][-1], folds[0][1][0])

    def test_failure_and_existing_protection(self):
        X, y = self.data()
        for stage in ("feature-processing", "ridge-tuning"):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with patch("src.feature_experiment.make_folds", side_effect=RuntimeError("synthetic failure")):
                    with self.assertRaises(RuntimeError):
                        run_feature_stage(X, y, {}, root, "staging/run", stage)
                self.assertTrue((root / "staging/run/failure.json").exists())
                self.assertFalse((root / "staging/run/completion.json").exists())
                with self.assertRaises(FileExistsError):
                    run_feature_stage(X, y, {}, root, "staging/run", stage)
