import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sar_baseline.manifest import load_manifest


class ManifestTest(unittest.TestCase):
    def _write_manifest(self, root, rows):
        path = root / "manifest.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=("image_id", "image_path", "caption_id", "caption", "split"),
            )
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_first_appearance_order_and_split(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = self._write_manifest(root, [
                {"image_id": "b", "image_path": "b.png", "caption_id": "b0", "caption": "b", "split": "test"},
                {"image_id": "a", "image_path": "a.png", "caption_id": "a0", "caption": "a", "split": "test"},
                {"image_id": "b", "image_path": "b.png", "caption_id": "b1", "caption": "b2", "split": "test"},
                {"image_id": "x", "image_path": "x.png", "caption_id": "x0", "caption": "x", "split": "train"},
            ])
            loaded = load_manifest(manifest_path, root, "test", check_files=False)
            self.assertEqual(loaded.image_ids, ("b", "a"))
            self.assertEqual(loaded.caption_image_indices, (0, 1, 0))

    def test_duplicate_caption_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = self._write_manifest(root, [
                {"image_id": "a", "image_path": "a.png", "caption_id": "same", "caption": "a", "split": "test"},
                {"image_id": "b", "image_path": "b.png", "caption_id": "same", "caption": "b", "split": "test"},
            ])
            with self.assertRaisesRegex(ValueError, "Duplicate caption_id"):
                load_manifest(manifest_path, root, "test", check_files=False)


if __name__ == "__main__":
    unittest.main()
