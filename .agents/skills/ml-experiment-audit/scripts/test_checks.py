"""Offline synthetic tests; no project datasets, models, or frozen results read."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from check_hashes import check_hashes, manifest_pairs, project_file
from check_project import check_project, validate_config, validate_output


class Checks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'evidence.txt').write_text('synthetic evidence', encoding='utf-8')
        self.good = {'task': 'regression', 'metrics': ['mse', 'rmse'], 'required_files': ['evidence.txt']}

    def manifest(self, digest=None):
        digest = digest or hashlib.sha256((self.root/'evidence.txt').read_bytes()).hexdigest()
        (self.root/'hashes.json').write_text(json.dumps({'evidence.txt': digest}), encoding='utf-8')

    def test_skill_metadata(self):
        skill = (Path(__file__).parent.parent/'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(skill.startswith('---\n'))
        front = skill.split('---', 2)[1]
        self.assertRegex(front, r'(?m)^name: ml-experiment-audit$')
        self.assertRegex(front, r'(?m)^description: .+')

    def test_valid_regression(self):
        self.assertEqual(check_project(self.root, self.good)['status'], 'PARTIAL PASS')

    def test_classification(self):
        self.good.update(task='classification', metrics=['accuracy', 'macro_f1'])
        validate_config(self.good)

    def test_metric_task_mismatch_both_directions(self):
        for task, metric in [('regression', 'accuracy'), ('classification', 'mse')]:
            with self.subTest(task=task), self.assertRaises(ValueError):
                validate_config(dict(self.good, task=task, metrics=[metric]))

    def test_invalid_config(self):
        for value in [{}, [], dict(self.good, task='unknown'), dict(self.good, metrics=[]), dict(self.good, train=True)]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_config(value)

    def test_missing_file(self):
        report = check_project(self.root, dict(self.good, required_files=['missing.txt']))
        self.assertEqual(report['missing'], ['missing.txt'])
        self.assertEqual(report['status'], 'NEEDS ATTENTION')

    def test_hash_match(self):
        self.manifest()
        self.assertEqual(check_hashes(self.root, 'hashes.json')['matched'], 1)

    def test_hash_mismatch(self):
        self.manifest('0'*64)
        self.assertEqual(check_hashes(self.root, 'hashes.json')['changed'], ['evidence.txt'])

    def test_hash_missing(self):
        self.manifest()
        (self.root/'evidence.txt').unlink()
        self.assertEqual(check_hashes(self.root, 'hashes.json')['missing'], ['evidence.txt'])

    def test_empty_and_bad_hash(self):
        for value in ({}, {'evidence.txt': 'not a digest'}):
            (self.root/'hashes.json').write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                manifest_pairs(self.root, 'hashes.json')

    def test_markdown_hash(self):
        self.manifest()
        digest = json.loads((self.root/'hashes.json').read_text())['evidence.txt']
        (self.root/'hashes.md').write_text('| Path | SHA256 |\n|---|---|\n| `evidence.txt` | '+digest+' |\n')
        self.assertEqual(check_hashes(self.root, 'hashes.md')['status'], 'PASS')

    def test_nested_manifest(self):
        self.manifest()
        mapping = json.loads((self.root/'hashes.json').read_text())
        (self.root/'nested.json').write_text(json.dumps({'protected': mapping}))
        self.assertEqual(check_hashes(self.root, 'nested.json', 'protected')['matched'], 1)

    def test_invalid_output(self):
        for relative in ['results/new', 'models/new', 'figures/paper/new', 'paper/new', '../escape', 'staging/../escape', 'staging', 'C:/outside', '/outside']:
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                validate_output(self.root, relative)

    def test_existing_empty_output(self):
        (self.root/'staging/run').mkdir(parents=True)
        with self.assertRaises(FileExistsError):
            validate_output(self.root, 'staging/run')

    def test_no_output_created(self):
        before = set(self.root.rglob('*'))
        report = check_project(self.root, self.good, 'staging/future')
        self.assertFalse(report['training_supported'])
        self.assertFalse(report['output_created'])
        self.assertEqual(before, set(self.root.rglob('*')))

    def test_private_and_escape_inputs(self):
        for path in ['../escape', 'data/raw/private.csv', 'private/secrets.json', '.git/config', 'C:\\outside']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                project_file(self.root, path)

    def test_actual_symlink(self):
        try:
            (self.root/'linked').symlink_to(self.root/'evidence.txt')
        except OSError as exc:
            self.skipTest('Real symlink unavailable: '+str(exc))
        with self.assertRaises(ValueError):
            project_file(self.root, 'linked')

    def test_split_metadata_and_overlap(self):
        spec = dict(path='splits.csv', sample_column='id', group_column='person', split_column='split')
        cfg = dict(self.good, split_metadata=spec)
        (self.root/'splits.csv').write_text('id,person,split\na,P1,train\nb,P2,test\n')
        self.assertEqual(check_project(self.root, cfg)['splits']['overlaps'], {})
        (self.root/'splits.csv').write_text('id,person,split\na,P1,train\nb,P1,test\n')
        self.assertEqual(check_project(self.root, cfg)['status'], 'NEEDS ATTENTION')

    def test_cli_train_and_overwrite_rejected(self):
        script = str(Path(__file__).with_name('check_project.py'))
        for flag in ['--train', '--overwrite']:
            run = subprocess.run([sys.executable, '-B', script, '--project-root', str(self.root), '--config', 'none.json', flag], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('unrecognized arguments', run.stderr)

    def test_malformed_json_cli(self):
        (self.root/'bad.json').write_text('invalid JSON')
        run = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('check_project.py')), '--project-root', str(self.root), '--config', 'bad.json'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)['status'], 'NEEDS ATTENTION')


if __name__ == '__main__':
    unittest.main(verbosity=2)
