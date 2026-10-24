"""Offline synthetic-only tests; never open the real frozen registry or raw data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from build_demo_report import build, ensure_same_protocol, preflight, read_csv, PROTOCOL

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from src import frozen, runtime


class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/'results').mkdir()
        self.path=self.root/'results/metrics.csv'
        self.path.write_text('model,mse_mean,mse_std\nRidge,0.25,0.02\n',encoding='utf8')
        self.registry={'results/metrics.csv':hashlib.sha256(self.path.read_bytes()).hexdigest()}

    def tearDown(self):
        self.temp.cleanup()

    def read(self):
        return read_csv(self.root,'results/metrics.csv',self.registry,frozen)

    def test_valid_registered_csv(self):
        self.assertEqual(self.read()[0]['mse_mean'],.25)

    def test_hash_drift(self):
        self.path.write_text('changed')
        with self.assertRaises(ValueError):self.read()

    def test_unregistered(self):
        with self.assertRaises(ValueError):read_csv(self.root,'results/metrics.csv',{},frozen)

    def test_bad_numbers(self):
        for value in ('NaN','Inf','no-number','-0.1'):
            self.path.write_text('model,mse_mean,mse_std\nRidge,'+value+',.1\n')
            self.registry['results/metrics.csv']=hashlib.sha256(self.path.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):self.read()

    def test_duplicate_columns(self):
        self.path.write_text('model,mse_mean,mse_mean\nRidge,.1,.2\n')
        self.registry['results/metrics.csv']=hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):self.read()

    def test_same_protocol(self):ensure_same_protocol([PROTOCOL,dict(PROTOCOL)])

    def test_mixed_protocol(self):
        with self.assertRaises(ValueError):ensure_same_protocol([PROTOCOL,{'name':'fusion','n':481}])

    def test_existing_output(self):
        runtime.create_run_dir(self.root,'staging/run')
        with self.assertRaises(FileExistsError):runtime.create_run_dir(self.root,'staging/run')

    def test_illegal_paths(self):
        for p in ('results/new','staging/../results/new','paper/new','../outside'):
            with self.assertRaises(ValueError):runtime.validate_output_dir(self.root,p)

    def test_unauthorized_does_not_write(self):
        with self.assertRaises(PermissionError):build(self.root,'staging/run')
        self.assertFalse((self.root/'staging').exists())

    def test_default_is_check_only(self):
        import build_demo_report as b
        with patch.object(sys,'argv',['builder','--project-root',str(self.root),'--output-dir','staging/a']),patch.object(b,'preflight',return_value=([],)),patch.object(b,'build') as writer:
            self.assertEqual(b.main(),0)
            writer.assert_not_called()

    def test_training_flag_refused(self):
        p=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('build_demo_report.py')),'--train'],capture_output=True)
        self.assertNotEqual(p.returncode,0)
        self.assertFalse((self.root/'staging').exists())

    def test_failure_no_completion(self):
        import build_demo_report as b
        original=b.write_json
        def writer(root,output,name,data,guard):
            if name=='input_manifest.json':raise RuntimeError('synthetic failure')
            original(root,output,name,data,guard)
        with patch('build_demo_report.preflight',return_value=(self.root,frozen,runtime,{}, {},[])),patch('build_demo_report.write_json',side_effect=writer):
            with self.assertRaises(RuntimeError):build(self.root,'staging/fail',True)
        self.assertFalse((self.root/'staging/fail/completion.json').exists())
        self.assertEqual(json.loads((self.root/'staging/fail/failure.json').read_text())['status'],'FAIL')

    def test_missing_artifacts_not_success(self):
        from verify_demo_report import verify
        runtime.create_run_dir(self.root,'staging/missing')
        with patch.object(frozen,'verify_registry',return_value={}):
            with self.assertRaises(FileNotFoundError):verify(self.root,'staging/missing')
        self.assertFalse((self.root/'staging/missing/completion.json').exists())

    def test_source_artifact_mapping(self):
        from build_demo_report import ADAPTER
        from verify_demo_report import validate_mapping
        rows=[{'figure':n,'source':a[0],'outputs':[f'demo_{n}.{e}' for e in ('pdf','svg','png')],'protocol':PROTOCOL} for n,a in ADAPTER.items()]
        validate_mapping(rows)
        rows[0]['source']='results/not-the-source.csv'
        with self.assertRaises(ValueError):validate_mapping(rows)

    def test_duplicate_mapping(self):
        from verify_demo_report import validate_mapping
        with self.assertRaises(ValueError):validate_mapping([{'figure':'models'},{'figure':'models'}])


if __name__=='__main__':unittest.main()
