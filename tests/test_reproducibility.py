import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sar_baseline.reproducibility import _git_snapshot


class ReproducibilityTest(unittest.TestCase):
    def test_non_repository_has_unknown_git_state(self):
        with tempfile.TemporaryDirectory() as directory:
            commit, dirty = _git_snapshot(directory)
            self.assertIsNone(commit)
            self.assertIsNone(dirty)


if __name__ == "__main__":
    unittest.main()
