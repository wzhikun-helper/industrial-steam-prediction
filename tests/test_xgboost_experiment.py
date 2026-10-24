import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.model_selection import ParameterGrid
from src.models import XGBOOST_GRID, build_xgboost_search, build_xgboost_model
from src.validation import make_folds, evaluate_estimator
from src.xgboost_experiment import run_xgboost_stage


class XGBoostTests(unittest.TestCase):
    def test_original_search(self):
        self.assertEqual(XGBOOST_GRID, {"n_estimators":[200,300,500],"learning_rate":[.03,.05,.1],
            "max_depth":[2,3,4],"subsample":[.8,1.],"colsample_bytree":[.8,1.]})
        self.assertEqual(len(list(ParameterGrid(XGBOOST_GRID))),108)
        folds=make_folds(60,"TimeSeriesSplit")
        search=build_xgboost_search(folds)
        self.assertIs(search.cv,folds)
        self.assertEqual(search.scoring,"neg_mean_squared_error")
        self.assertEqual(search.n_jobs,-1)
        self.assertTrue(search.refit)
        self.assertEqual(search.estimator.random_state,42)
        self.assertEqual(search.estimator.objective,"reg:squarederror")

    def test_fixed_distinct_and_fresh(self):
        X=pd.DataFrame({"x":np.arange(60.)})
        y=X.x
        fitted=[]
        def factory():
            model=build_xgboost_model()
            self.assertEqual(model.max_depth,2)
            self.assertEqual(model.colsample_bytree,1.)
            model.set_params(n_estimators=2,n_jobs=1)
            fitted.append(model)
            return model
        configs=[]
        rows,mean=evaluate_estimator(X,y,factory,make_folds(60,"TimeSeriesSplit"),
                    fitted_callback=lambda fold,model:configs.append(model.get_booster().save_config()))
        self.assertEqual(len({id(m) for m in fitted}),5)
        self.assertEqual(len(configs),5)
        self.assertAlmostEqual(mean["rmse"],np.mean([r["rmse"] for r in rows]))

    def test_failure_and_frozen_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with patch("src.xgboost_experiment.make_folds",side_effect=RuntimeError("synthetic")):
                with self.assertRaises(RuntimeError):
                    run_xgboost_stage(pd.DataFrame({"x":range(60)}),None,{},root,"staging/fail")
            self.assertTrue((root/"staging/fail/failure.json").exists())
            self.assertFalse((root/"staging/fail/completion.json").exists())
            with self.assertRaises(FileExistsError):
                run_xgboost_stage(None,None,{},root,"staging/fail")
            for forbidden in ("results/run","models/run","paper/run","figures/paper/run"):
                with self.assertRaises(ValueError):
                    run_xgboost_stage(None,None,{},root,forbidden)

    def test_search_and_fixed_outputs_separate(self):
        import inspect
        source=inspect.getsource(run_xgboost_stage)
        self.assertIn('"search_results.csv"',source)
        self.assertIn('"fixed_best_fold_metrics.csv"',source)
        self.assertIn('evaluate_estimator(X,y,build_xgboost_model',source)
