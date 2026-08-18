import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_exp0005 import run_and_write


class Exp0005RunnerTests(unittest.TestCase):
    def test_runner_writes_report_metrics_ledger_and_valid_three_m(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "EXP-0005"
            summary = run_and_write(repo, out)
            self.assertTrue(all(summary["hypotheses"].values()))
            self.assertTrue(summary["three_m"]["valid"])
            self.assertTrue((out / "results/report.md").exists())
            self.assertTrue((out / "results/metrics.json").exists())
            self.assertTrue((out / "ledger/ai_board_sci.jsonl").exists())
            self.assertTrue((out / "results/per_arm_summary.jsonl").exists())
            metrics = json.loads((out / "results/metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["schema"], "scl-exp0005/v0.5")


if __name__ == "__main__":
    unittest.main()
