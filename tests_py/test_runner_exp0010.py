import json
import subprocess
import sys
from pathlib import Path


def test_runner_exp0010_generates_core_artifacts():
    repo = Path(__file__).resolve().parents[1]
    proc = subprocess.run([sys.executable, "scripts/run_exp0010.py"], cwd=repo, check=True, capture_output=True, text=True)
    payload = json.loads(proc.stdout)
    assert payload["experiment"] == "EXP-0010"
    assert payload["three_m"]["valid"]
    base = repo / "experiments/EXP-0010"
    for rel in [
        "results/metrics.json",
        "results/per_event_summary.jsonl",
        "results/report.md",
        "ledger/reflexive_decisions.jsonl",
        "3m/checksums.json",
        "3m/verification.json",
    ]:
        assert (base / rel).exists(), rel
