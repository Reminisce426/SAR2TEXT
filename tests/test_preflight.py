import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sar_baseline.config import load_config
from sar_baseline.preflight import check_offline_inputs


class PreflightTest(unittest.TestCase):
    def _fixture(self, root, expected_sha256=None):
        config_dir = root / "configs"
        data_dir = config_dir / "data"
        image_dir = data_dir / "images"
        weight_dir = config_dir / "weights"
        image_dir.mkdir(parents=True)
        weight_dir.mkdir()
        (image_dir / "a.png").write_bytes(b"placeholder image")
        weight_path = weight_dir / "model.pt"
        weight_path.write_bytes(b"offline weights")
        actual_hash = hashlib.sha256(b"offline weights").hexdigest()

        manifest_path = data_dir / "manifest.csv"
        with manifest_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=("image_id", "image_path", "caption_id", "caption", "split"),
            )
            writer.writeheader()
            writer.writerow(
                {
                    "image_id": "a",
                    "image_path": "a.png",
                    "caption_id": "a0",
                    "caption": "harbor",
                    "split": "test",
                }
            )

        config = {
            "experiment_name": "preflight-test",
            "seed": 1,
            "deterministic": True,
            "model": {
                "name": "ViT-B-32",
                "pretrained_path": "weights/model.pt",
                "expected_sha256": expected_sha256 if expected_sha256 is not None else actual_hash,
                "device": "cpu",
                "precision": "fp32",
            },
            "data": {
                "manifest": "data/manifest.csv",
                "image_root": "data/images",
                "split": "test",
            },
            "evaluation": {
                "batch_size": 1,
                "num_workers": 0,
                "query_batch_size": 1,
                "recall_ks": [1],
                "case_top_k": 1,
                "case_count_each": 1,
            },
            "output_dir": "results/run",
        }
        config_path = config_dir / "test.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        return config_path, actual_hash

    def test_preflight_checks_manifest_images_weight_and_output(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path, actual_hash = self._fixture(Path(directory))
            _, report = check_offline_inputs(load_config(config_path))
            self.assertEqual(report["image_count"], 1)
            self.assertEqual(report["caption_count"], 1)
            self.assertEqual(report["weight_sha256"], actual_hash)
            self.assertEqual(len(report["config_sha256"]), 64)
            self.assertFalse(report["model_runtime_initialized"])

    def test_preflight_rejects_weight_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path, _ = self._fixture(Path(directory), "0" * 64)
            with self.assertRaisesRegex(ValueError, "Weight SHA256 mismatch"):
                check_offline_inputs(load_config(config_path))


if __name__ == "__main__":
    unittest.main()
