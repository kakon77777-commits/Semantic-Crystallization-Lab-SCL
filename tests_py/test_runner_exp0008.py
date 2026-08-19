import json
import subprocess
import sys
import unittest
from pathlib import Path


class RunnerExp0008Tests(unittest.TestCase):
    def test_runner_generates_core_artifacts(self):
        repo = Path(__file__).resolve().parents[1]
        proc = subprocess.run([sys.executable, 'scripts/run_exp0008.py'], cwd=repo, check=True, capture_output=True, text=True)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload['experiment'], 'EXP-0008')
        self.assertTrue(payload['three_m']['valid'])
        base = repo / 'experiments/EXP-0008'
        for rel in ['results/metrics.json', 'results/per_event_summary.jsonl', 'results/trust_trajectory.jsonl', 'results/report.md', 'ledger/trust_dynamics_events.jsonl', '3m/checksums.json', '3m/verification.json']:
            self.assertTrue((base / rel).exists(), rel)


if __name__ == '__main__':
    unittest.main()
