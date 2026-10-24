import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from src.data_utils import load_steam_data, validate_steam_data
from src.runtime import validate_output_dir, create_run_dir, open_new_output
from scripts.run_experiment import main, load_config, ROOT


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.features = [f"V{i}" for i in range(38)]
        self.train = pd.DataFrame(np.zeros((2, 39)), columns=self.features + ["target"])
        self.test = self.train.drop(columns="target")

    def validate(self, train=None, test=None):
        validate_steam_data(self.train if train is None else train,
                            self.test if test is None else test,
                            self.features, "target", [2, 39], [2, 38])

    def test_valid_schema(self):
        self.validate()

    def test_missing_target(self):
        with self.assertRaises(ValueError):
            self.validate(self.test)

    def test_missing_feature(self):
        with self.assertRaises(ValueError):
            self.validate(test=self.test.drop(columns="V0"))

    def test_wrong_order(self):
        with self.assertRaises(ValueError):
            self.validate(test=self.test[self.features[::-1]])

    def test_nonfinite(self):
        for value in (np.nan, np.inf, -np.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                frame = self.train.copy()
                frame.iloc[0, 0] = value
                self.validate(frame)

    def test_nonnumeric(self):
        with self.assertRaises(ValueError):
            self.validate(self.train.astype(str))

    def test_duplicate_columns(self):
        frame = self.train.copy()
        frame.columns = ["V0"] * 39
        with self.assertRaises(ValueError):
            self.validate(frame)
        (self.root / "train.txt").write_text("V0\tV0\n1\t2\n")
        with self.assertRaises(ValueError):
            load_steam_data(self.root, "train.txt", "test.txt")

    def test_existing_output(self):
        create_run_dir(self.root, "staging/run")
        with self.assertRaises(FileExistsError):
            validate_output_dir(self.root, "staging/run")

    def test_frozen_and_traversal(self):
        for path in ("results/run", "models/run", "figures/paper/run", "paper/run",
                     "staging/../results/run", "../outside", str(self.root / "outside")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_output_dir(self.root, path)

    def test_symlink_escape(self):
        (self.root / "staging").mkdir()
        try:
            (self.root / "staging/link").symlink_to(self.root, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Symlink privilege unavailable: {error}")
        with self.assertRaises(ValueError):
            validate_output_dir(self.root, "staging/link/run")

    def test_exclusive_file(self):
        create_run_dir(self.root, "reproduction/run")
        with open_new_output(self.root, "reproduction/run", "note.txt") as stream:
            stream.write("test")
        with self.assertRaises(FileExistsError):
            open_new_output(self.root, "reproduction/run", "note.txt")

    def test_link_detection_rejected(self):
        original = Path.is_symlink
        link = self.root / "staging" / "link"
        with patch.object(Path, "is_symlink", lambda path: path == link or original(path)):
            with self.assertRaises(ValueError):
                validate_output_dir(self.root, "staging/link/run")

    def setup_config(self):
        config = json.loads((ROOT / "configs/experiment.yaml").read_text())
        config["data"]["train"] = "train.txt"
        config["data"]["test"] = "test.txt"
        pd.DataFrame(np.zeros((2888, 39)), columns=self.features + ["target"]).to_csv(
            self.root / "train.txt", sep="\t", index=False)
        pd.DataFrame(np.zeros((1925, 38)), columns=self.features).to_csv(
            self.root / "test.txt", sep="\t", index=False)
        (self.root / "config.yaml").write_text(json.dumps(config))
        return config

    def test_config_protocol(self):
        config = self.setup_config()
        self.assertEqual(load_config(self.root, "config.yaml"), config)
        config["random_state"] = 99
        (self.root / "config.yaml").write_text(json.dumps(config))
        with self.assertRaises(ValueError):
            load_config(self.root, "config.yaml")

    def test_dry_run_no_writes(self):
        self.setup_config()
        before = set(self.root.rglob("*"))
        self.assertEqual(main(["--config", "config.yaml", "--output-dir",
                               "staging/check", "--dry-run"], self.root), 0)
        self.assertEqual(set(self.root.rglob("*")), before)

    def test_training_disabled(self):
        self.setup_config()
        self.assertEqual(main(["--config", "config.yaml", "--output-dir",
                               "staging/check"], self.root), 2)
        self.assertFalse((self.root / "staging").exists())


if __name__ == "__main__":
    unittest.main()
