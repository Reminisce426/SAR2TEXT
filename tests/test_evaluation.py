import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sar_baseline.evaluation import _retained_ranking_depth


class EvaluationInterfaceTest(unittest.TestCase):
    def test_case_depth_is_independent_of_recall_cutoffs(self):
        self.assertEqual(_retained_ranking_depth(candidate_count=100, ranking_depth=3), 3)

    def test_case_depth_is_capped_by_candidate_count(self):
        self.assertEqual(_retained_ranking_depth(candidate_count=2, ranking_depth=10), 2)

    def test_case_depth_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, "ranking_depth"):
            _retained_ranking_depth(candidate_count=2, ranking_depth=0)


if __name__ == "__main__":
    unittest.main()
