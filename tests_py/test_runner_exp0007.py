import json
import subprocess
import sys
import unittest
from pathlib import Path


class RunnerExp0007Tests(unittest.TestCase):
    def test_runner_generates_report_metrics_trust_ledger_and_3m_verification(self):
        repo = Path(__file__).resolve().parents[1]
        subprocess.run([sys.executable, "scripts/run_exp0007.py"], cwd=repo, check=True)
        base = repo / "experiments/EXP-0007"
        required = [
            base / "results/metrics.json",
            base / "results/per_event_summary.jsonl",
            base / "results/trust_trajectory.jsonl",
            base / "results/report.md",
            base / "ledger/admission_events.jsonl",
            base / "3m/checksums.json",
            base / "3m/verification.json",
        ]
        for path in required:
            self.assertTrue(path.exists(), str(path))
        metrics = json.loads((base / "results/metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(metrics["experiment_id"], "EXP-0007")
        self.assertTrue(metrics["hypotheses"]["H3_learned_tracks_provenance_drift"])
        verification = json.loads((base / "3m/verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])


if __name__ == "__main__":
    unittest.main()
