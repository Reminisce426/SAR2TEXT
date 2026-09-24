import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sar_baseline.config import load_config


def valid_config():
    return {
        "experiment_name": "test",
        "seed": 1,
        "deterministic": True,
        "model": {
            "name": "ViT-B-32",
            "pretrained_path": "weights/model.pt",
            "expected_sha256": "",
            "device": "cpu",
            "precision": "fp32",
        },
        "data": {
            "manifest": "data/manifest.csv",
            "image_root": "data/images",
            "split": "test",
        },
        "evaluation": {
            "batch_size": 2,
            "num_workers": 0,
            "query_batch_size": 4,
            "recall_ks": [1, 5],
            "case_top_k": 5,
            "case_count_each": 1,
        },
        "output_dir": "results/run",
    }


class ConfigTest(unittest.TestCase):
    def _write_config(self, root, config):
        path = root / "configs" / "test.json"
        path.parent.mkdir()
        path.write_text(json.dumps(config), encoding="utf-8")
        return path

    def test_relative_paths_resolve_from_config_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self._write_config(root, valid_config())
            loaded = load_config(path)
            self.assertEqual(
                loaded["model"]["pretrained_path"],
                str((path.parent / "weights/model.pt").resolve()),
            )
            self.assertEqual(
                loaded["data"]["manifest"],
                str((path.parent / "data/manifest.csv").resolve()),
            )
            self.assertEqual(
                loaded["output_dir"], str((path.parent / "results/run").resolve())
            )

    def test_zero_batch_size_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            config = valid_config()
            config["evaluation"]["batch_size"] = 0
            path = self._write_config(Path(directory), config)
            with self.assertRaisesRegex(ValueError, "evaluation.batch_size"):
                load_config(path)

    def test_malformed_expected_sha256_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            config = valid_config()
            config["model"]["expected_sha256"] = "not-a-hash"
            path = self._write_config(Path(directory), config)
            with self.assertRaisesRegex(ValueError, "expected_sha256"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
