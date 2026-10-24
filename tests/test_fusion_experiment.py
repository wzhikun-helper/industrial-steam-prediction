import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from src.fusion import weighted_blend
from src.fusion_experiment import (oof_plan, generate_oof, split_oof, search_development_weights,
    fit_meta_model, evaluate_validation, protocol_precheck, run_real_fusion)
from scripts.run_experiment import main, ROOT


class FusionTests(unittest.TestCase):
    def fixture(self):
        X=pd.DataFrame({"x":np.arange(2888.)})
        y=X.x * .1
        return X,y

    def oof(self):
        X,y=self.fixture()
        return generate_oof(X,y,lambda:DummyRegressor(),lambda:DummyRegressor(strategy="median"))[0]

    def test_coverage_alignment_and_fresh_models(self):
        X,y=self.fixture()
        instances=[]
        def factory():
            m=DummyRegressor()
            instances.append(m)
            return m
        oof,uncovered=generate_oof(X,y,factory,factory)
        self.assertEqual(len({id(m) for m in instances}),10)
        np.testing.assert_array_equal(uncovered,np.arange(483))
        np.testing.assert_array_equal(oof.row_id,np.arange(483,2888))
        np.testing.assert_allclose(oof.true_value,y.iloc[oof.row_id])
        self.assertFalse(oof.row_id.duplicated().any())
        folds,_,_=oof_plan(2888)
        for fold,(tr,va) in enumerate(folds,1):
            np.testing.assert_allclose(oof[oof.fold==fold].ridge_pred,y.iloc[tr].mean())

    def test_split_rule_481(self):
        dev,val=split_oof(self.oof(),expected_validation_size=481)
        self.assertEqual(len(dev),1924)
        self.assertEqual(val.row_id.tolist(),list(range(2407,2888)))
        self.assertFalse(set(dev.row_id)&set(val.row_id))
        broken=self.oof()
        broken.loc[1,"row_id"]=broken.loc[0,"row_id"]
        with self.assertRaises(ValueError):
            split_oof(broken)
        with self.assertRaises(ValueError):
            split_oof(self.oof(),expected_validation_size=480)

    def test_selection_never_uses_validation_labels(self):
        dev,val=split_oof(self.oof())
        first,w=search_development_weights(dev)
        val.loc[:,"true_value"]=-99999.
        second,w2=search_development_weights(dev)
        pd.testing.assert_frame_equal(first,second)
        self.assertEqual(w,w2)
        self.assertEqual(len(first),21)

    def test_formula_meta_fit_scope_and_fair_metrics(self):
        np.testing.assert_allclose(weighted_blend([1,2],[3,4],.7),[1.6,2.6])
        dev,val=split_oof(self.oof())
        captured={}
        class Meta(DummyRegressor):
            def fit(self,X,y):
                captured["X"],captured["y"]=X.copy(),y.copy()
                return super().fit(X,y)
        meta=fit_meta_model(dev,lambda:Meta())
        pd.testing.assert_frame_equal(captured["X"],dev[["ridge_pred","xgb_pred"]])
        pd.testing.assert_series_equal(captured["y"],dev.true_value)
        real_meta=fit_meta_model(dev)
        self.assertEqual(real_meta.alpha,1.)
        self.assertEqual(real_meta.n_features_in_,2)
        pred,metrics,fixed=evaluate_validation(val,.7,meta)
        self.assertEqual(pred.row_id.tolist(),val.row_id.tolist())
        self.assertTrue((metrics.n_samples==481).all())
        self.assertEqual(len(metrics),4)
        self.assertAlmostEqual(fixed["mse"],metrics[metrics.model=="Weighted Blend"].iloc[0].mse)

    def test_real_execution_disabled_no_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            config=json.loads((ROOT/"configs/experiment.yaml").read_text())
            config["data"]["train"]="train.txt"
            config["data"]["test"]="test.txt"
            (root/"config.yaml").write_text(json.dumps(config))
            (root/"train.txt").touch()
            (root/"test.txt").touch()
            args=["--config","config.yaml","--output-dir","staging/check","--stage","fusion"]
            with patch("scripts.run_experiment.load_steam_data",side_effect=AssertionError("must not load")):
                self.assertEqual(main(args,root),2)
                self.assertEqual(main(args+["--dry-run"],root),0)
            self.assertFalse((root/"staging").exists())
            self.assertFalse(list(root.rglob("completion.json")))
            (root/"staging/check").mkdir(parents=True)
            self.assertEqual(main(args+["--dry-run"],root),2)
        with self.assertRaises(ValueError):
            run_real_fusion()

    def test_precheck(self):
        plan=protocol_precheck()
        self.assertEqual(plan["oof_count"],2405)
        self.assertEqual(plan["validation_count"],481)
        self.assertFalse(plan["training_enabled"])
