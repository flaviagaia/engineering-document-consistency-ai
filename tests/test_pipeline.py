from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import run_pipeline


class PipelineTest(unittest.TestCase):
    def test_pipeline_generates_inconsistencies(self):
        summary = run_pipeline()
        self.assertGreaterEqual(summary["documents"], 5)
        self.assertGreater(summary["clauses"], 0)
        self.assertGreater(summary["similar_pairs"], 0)
        self.assertGreater(summary["inconsistencies"], 0)


if __name__ == "__main__":
    unittest.main()

