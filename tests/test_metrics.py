import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sar_baseline.metrics import bidirectional_recall, recall_from_scores, stable_ranking


class RetrievalMetricsTest(unittest.TestCase):
    def test_stable_tie_break_uses_candidate_index(self):
        self.assertEqual(stable_ranking([0.5, 0.7, 0.7, 0.1]), [1, 2, 0, 3])

    def test_recall_at_k(self):
        metrics, ranks, _ = recall_from_scores(
            [[0.9, 0.2, 0.1], [0.8, 0.7, 0.1]],
            [{0}, {1}],
            candidate_count=3,
            ks=(1, 2),
        )
        self.assertEqual(ranks, [1, 2])
        self.assertEqual(metrics["R@1"], 0.5)
        self.assertEqual(metrics["R@2"], 1.0)

    def test_bidirectional_multi_caption_positives(self):
        result = bidirectional_recall(
            [[0.9, 0.1], [0.8, 0.2], [0.1, 0.9]], [0, 0, 1], ks=(1, 2)
        )
        self.assertEqual(result["text_to_image"]["R@1"], 1.0)
        self.assertEqual(result["image_to_text"]["R@1"], 1.0)
        self.assertEqual(result["image_to_text"]["query_count"], 2)


if __name__ == "__main__":
    unittest.main()
