import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from src.frozen import load_registry, verify_registry
from src.runtime import create_run_dir, open_new_binary_output
from src.validation import run_ridge_stage
from src.diagnostics import error_analysis, shap_importance
from src.final_prediction import final_fit_predict, save_synthetic_prediction
from scripts.export_paper_results import export
from scripts.run_experiment import main, ROOT
from release_fixtures import register


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'results').mkdir()
        (self.root/'results/input.csv').write_bytes(b'a,b\n1,2\n')
        register(self.root)

    def test_valid_registry(self):
        self.assertEqual(len(verify_registry(self.root)),89)

    def test_bad_registry_variants(self):
        path=self.root/'results/frozen_artifacts_sha256.md'
        original=path.read_text(encoding='utf-8')
        lines=original.splitlines()
        variants=[original+'\n'+lines[-1], '\n'.join(lines[:-1]),
                  original.replace('results/input.csv','../outside'),
                  original.replace(lines[-1].split('|')[2].strip(),'z'*64)]
        for text in variants:
            with self.subTest(text=text[-100:]):
                path.write_text(text,encoding='utf-8')
                with self.assertRaises(ValueError):
                    load_registry(self.root)
        path.write_text(original,encoding='utf-8')
        (self.root/'results/input.csv').unlink()
        with self.assertRaises(ValueError):
            load_registry(self.root)

    def test_optimized_python_does_not_bypass(self):
        (self.root/'results/frozen_artifacts_sha256.md').write_text('',encoding='utf-8')
        command='from src.frozen import load_registry; import sys; load_registry(sys.argv[1])'
        run=subprocess.run([sys.executable,'-B','-O','-c',command,str(self.root)],cwd=ROOT,capture_output=True)
        self.assertNotEqual(run.returncode,0)

    def test_export_source_identity(self):
        (self.root/'results/input.csv').write_bytes(b'a,b\n1,999\n')
        for dry in (False,True):
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):
                export(self.root,'staging/export',sources={'x':['results/input.csv']},dry_run=dry)
        self.assertFalse((self.root/'staging').exists())

    def test_export_unregistered(self):
        (self.root/'results/unregistered.csv').write_bytes(b'a\n1\n')
        with self.assertRaisesRegex(ValueError,'Unregistered'):
            export(self.root,'staging/export',sources={'x':['results/unregistered.csv']})

    def test_ridge_failure_status(self):
        config={'random_state':42,'rmse_aggregation':'mean_of_fold_rmse'}
        X=pd.DataFrame({'x':range(12)})
        with patch('src.validation.evaluate_ridge',side_effect=RuntimeError('injected failure')):
            with self.assertRaisesRegex(RuntimeError,'injected failure'):
                run_ridge_stage(X,X.x,config,self.root,'staging/ridge')
        failure=json.loads((self.root/'staging/ridge/failure.json').read_text())
        self.assertEqual(failure['status'],'failed')
        self.assertIn('injected failure',failure['traceback'])
        self.assertFalse((self.root/'staging/ridge/completion.json').exists())

    def test_ridge_success_marker_after_results(self):
        cfg={'random_state':42,'rmse_aggregation':'mean_of_fold_rmse'}
        row={'fold':1,'mse':1.,'rmse':1.,'mae':1.,'r2':0.}
        mean={k:row[k] for k in ('mse','rmse','mae','r2')}
        with patch('src.validation.evaluate_ridge',return_value=([row],mean)):
            run_ridge_stage(pd.DataFrame({'x':range(12)}),pd.Series(range(12)),cfg,self.root,'staging/success')
        self.assertTrue((self.root/'staging/success/mean_metrics.csv').is_file())
        self.assertEqual(json.loads((self.root/'staging/success/completion.json').read_text())['fits'],4)
        self.assertFalse((self.root/'staging/success/failure.json').exists())

    def test_row_ids_nonfinite_fractional_negative(self):
        for ids in ([0,np.inf],[0,np.nan],[0,.5],[0,-1],[True,False]):
            with self.subTest(ids=ids),self.assertRaises(ValueError):
                error_analysis([1,2],[1,2],ids)

    def test_fit_input_shape_and_index_before_training(self):
        X=pd.DataFrame({'x':[1.,2.]})
        for y in (pd.Series([1.,2.],index=[1,0]),np.array([[1.],[2.]])):
            with self.assertRaises(ValueError):
                final_fit_predict(X,y,X,synthetic=True,factories=(None,None))
        with self.assertRaises(ValueError):
            shap_importance(None,X.iloc[:0],explained_model='Best XGBoost',synthetic=True,explainer_factory=lambda m:None)

    def test_binary_exclusive_and_link_guard(self):
        create_run_dir(self.root,'staging/bin')
        with open_new_binary_output(self.root,'staging/bin','model.bin') as stream:
            stream.write(b'synthetic')
        with self.assertRaises(FileExistsError):
            open_new_binary_output(self.root,'staging/bin','model.bin')
        target=self.root/'staging/bin/linked.bin'
        original=Path.is_symlink
        with patch.object(Path,'is_symlink',lambda p:p==target or original(p)):
            with self.assertRaises(ValueError):
                open_new_binary_output(self.root,'staging/bin','linked.bin')

    def test_save_model_keys_and_formula(self):
        f=pd.DataFrame({'ridge_prediction':[1.,2.],'xgboost_prediction':[3.,4.],'weighted_prediction':[1.6,2.6]})
        with self.assertRaises(ValueError):
            save_synthetic_prediction(self.root,'staging/no_model',f,{'ridge':object()})
        f.loc[0,'weighted_prediction']=99
        with self.assertRaises(ValueError):
            save_synthetic_prediction(self.root,'staging/formula',f,{'ridge':object(),'xgboost':object()})
        self.assertFalse(list(self.root.rglob('completion.json')))

    def test_check_only_without_private_data(self):
        cfg=json.loads((ROOT/'configs/experiment.yaml').read_text())
        (self.root/'config.yaml').write_text(json.dumps(cfg))
        with patch('scripts.run_experiment.load_steam_data',side_effect=AssertionError('No raw read')):
            for stage in ('ridge-baseline','tree-baselines','feature-processing','ridge-tuning','xgboost-tuning','fusion','shap','final-prediction'):
                self.assertEqual(main(['--config','config.yaml','--stage',stage,'--output-dir','staging/check','--check-only'],self.root),0)
        self.assertFalse((self.root/'staging').exists())
