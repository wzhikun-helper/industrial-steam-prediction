import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from src.diagnostics import error_analysis, shap_importance
from src.final_prediction import final_fit_predict, save_synthetic_prediction
from scripts.export_paper_results import export


class RemainingTests(unittest.TestCase):
    def test_cli_real_stages_disabled(self):
        import json
        from scripts.run_experiment import ROOT, main
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            config=json.loads((ROOT/"configs/experiment.yaml").read_text())
            config["data"]["train"]="train.txt"; config["data"]["test"]="test.txt"
            (root/"config.yaml").write_text(json.dumps(config))
            (root/"train.txt").touch(); (root/"test.txt").touch()
            for stage in ("shap","final-prediction"):
                args=["--config","config.yaml","--output-dir","staging/run","--stage",stage]
                with patch("scripts.run_experiment.load_steam_data",side_effect=AssertionError("no real loading")):
                    self.assertEqual(main(args,root),2)
                    self.assertEqual(main(args+["--dry-run"],root),0)
            self.assertFalse((root/"staging").exists())

    def test_residual_and_481_identity(self):
        true=np.arange(481.)
        ids=np.arange(2407,2888)
        result,metrics=error_analysis(true,true+1,ids,expected_n=481)
        self.assertTrue((result.residual==-1).all())
        self.assertTrue((result.absolute_error==1).all())
        self.assertEqual(set(result.row_id),set(ids))
        self.assertEqual(metrics["mse"],1.)
        result,_=error_analysis([1,2,3],[1,4,2],[10,11,12])
        self.assertEqual(result.row_id.tolist(),[11,12,10])
        for values in ([np.nan,1],[np.inf,1]):
            with self.assertRaises(ValueError):
                error_analysis(values,[1,2],[0,1])
        with self.assertRaises(ValueError):
            error_analysis([1,2],[1,2],[0,0])

    def test_shap_boundary(self):
        X=pd.DataFrame({"V0":[1.,2.],"V1":[3.,4.]})
        class Explainer:
            def __init__(self,model): pass
            def shap_values(self,X): return np.array([[1.,-2.],[3.,-4.]])
        result=shap_importance(None,X,explained_model="Best XGBoost",synthetic=True,explainer_factory=Explainer)
        self.assertEqual(result.feature.tolist(),["V1","V0"])
        self.assertEqual(result.mean_abs_shap.tolist(),[3.,2.])
        for name in ("Weighted Blend","Best XGBoost"):
            with self.assertRaises(ValueError):
                shap_importance(None,X,explained_model=name)

    def test_prediction_and_saving(self):
        X=pd.DataFrame({"V0":[1.,2.,3.]})
        test=pd.DataFrame({"V0":[4.,5.]})
        with self.assertRaises(ValueError):
            final_fit_predict(X,X.V0,test)
        pred,models=final_fit_predict(X,X.V0,test,synthetic=True,
            factories=(lambda:DummyRegressor(),lambda:DummyRegressor(strategy="constant",constant=4)))
        self.assertEqual(pred.shape,(2,3))
        np.testing.assert_allclose(pred.weighted_prediction,.7*pred.ridge_prediction+.3*pred.xgboost_prediction)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            save_synthetic_prediction(root,"staging/test",pred,models)
            self.assertTrue((root/"staging/test/best_ridge_model.joblib").exists())
            with self.assertRaises(FileExistsError):
                save_synthetic_prediction(root,"staging/test",pred,models)
            bad=pred.copy(); bad.iloc[0,0]=np.inf
            with self.assertRaises(ValueError):
                save_synthetic_prediction(root,"staging/fail",bad,models)
            self.assertFalse((root/"staging/fail/completion.json").exists())

    def test_export_provenance_and_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"results").mkdir()
            raw=b"feature,value\nV0,0.1234567890123456\n"
            (root/"results/input.csv").write_bytes(raw)
            from release_fixtures import register
            register(root)
            mapping={"FigX":["results/input.csv"]}
            report=export(root,"staging/export",sources=mapping)
            self.assertEqual(report["files"][0]["rows"],1)
            self.assertEqual((root/"staging/export/input.csv").read_bytes(),raw)
            with self.assertRaises(FileExistsError):
                export(root,"staging/export",sources=mapping)
            with self.assertRaises(ValueError):
                export(root,"results/output",sources=mapping)
            with patch("scripts.export_paper_results.pd.read_csv",side_effect=ValueError("bad CSV")):
                with self.assertRaises(ValueError):
                    export(root,"staging/fail",sources=mapping)
            self.assertFalse((root/"staging/fail/completion.json").exists())
            self.assertTrue((root/"staging/fail/failure.json").exists())
