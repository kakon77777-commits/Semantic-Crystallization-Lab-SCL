from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def export_three_m_v09(result: dict, root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    metric_rows: list[dict] = []
    decision_rows: list[dict] = []
    route_rows: list[dict] = []
    ledger_rows: list[dict] = []
    trust_hash_rows = [
        {"sequence": i + 1, "event_id": event["event_id"], "trust_snapshot_sha256": sha}
        for i, (event, sha) in enumerate(zip(result["events"], result["shared_trust_snapshot_hashes"]))
    ]

    for policy_name, arm in sorted(result["policies"].items()):
        for key, value in sorted(arm["summary"].items()):
            if isinstance(value, (int, float, bool)) and value is not None:
                metric_rows.append({"policy": policy_name, "metric": key, "value": value})
        for sequence, event in enumerate(arm["events"], start=1):
            row = {"policy": policy_name, "sequence": sequence, **event}
            decision_rows.append(row)
            ledger_rows.append({
                "logical_instant": f"EXP0009-{policy_name}-{sequence:02d}",
                "event_type": f"imprint.epistemic-decision.{event['final_action']}",
                **row,
            })
            for step, action in enumerate(event["action_trace"], start=1):
                route_rows.append({
                    "route": "uncertainty-aware-epistemic-decision",
                    "policy": policy_name,
                    "sequence": sequence,
                    "step": step,
                    "event_id": event["event_id"],
                    "action": action,
                    "truth_effect": event["truth_effect"],
                    "risk": event["risk"],
                    "candidate_probability": event["candidate_probability"],
                    "uncertainty": event["uncertainty"],
                    "disagreement": event["disagreement"],
                })

    manifest = {
        "schema": "scl-3m-bounded/v0.9",
        "experiment_id": "EXP-0009",
        "conformance": "bounded-profile-not-formal-mlf-1.0",
        "roles": {
            "MLF": "policy/event/action/cost/uncertainty coordinates, provenance and hashes",
            "MMR": "policy↔event↔belief-state↔action↔cost multidirectional projections",
            "MMLC": "deterministic belief aggregation, active evidence acquisition, defer resolution and loss calculations",
            "AI_Board": "append-only epistemic decision/action compatibility ledger",
            "CTCL": "deterministic logical event order only; no live verified time call",
        },
        "policies": sorted(result["policies"]),
        "hypotheses": result["hypotheses"],
    }
    substrate = {
        "feature_ids": result["feature_ids"],
        "event_fixtures": result["events"],
        "boundaries": result["boundaries"],
        "shared_trust_snapshot_hashes": result["shared_trust_snapshot_hashes"],
    }
    projection_loss = {
        "policy_summaries": {name: row["summary"] for name, row in sorted(result["policies"].items())},
        "active_evidence_scalar_errors_resolved": result["active_evidence_scalar_errors_resolved"],
        "hypotheses": result["hypotheses"],
    }

    _dump_json(root / "manifest.json", manifest)
    _dump_json(root / "substrate.json", substrate)
    _dump_jsonl(root / "matrices/policy_metrics.cells.jsonl", metric_rows)
    _dump_jsonl(root / "matrices/policy_event_decision.cells.jsonl", decision_rows)
    _dump_jsonl(root / "matrices/shared_trust_snapshots.cells.jsonl", trust_hash_rows)
    _dump_jsonl(root / "graphs/routes.jsonl", route_rows)
    _dump_jsonl(root / "ledgers/epistemic_decisions.jsonl", ledger_rows)
    _dump_jsonl(root / "provenance/events.jsonl", [{
        "event": "export",
        "experiment_id": "EXP-0009",
        "current_truth_visible_to_non_oracle_policy": False,
        "shared_trust_memory_across_non_oracle_policies": True,
        "seek_evidence_costed": True,
        "defer_resolution_mode": "one-event-delayed validation",
        "public_ai_board_write": False,
        "live_ctcl_call": False,
        "neural_retraining": False,
    }])
    _dump_json(root / "reports/projection_loss.json", projection_loss)

    checksums = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {"checksums.json", "verification.json"} and not path.name.startswith("GITHUB_"):
            checksums[str(path.relative_to(root)).replace("\\", "/")] = hashlib.sha256(path.read_bytes()).hexdigest()
    _dump_json(root / "checksums.json", checksums)


def verify_three_m_v09(root: Path) -> dict:
    root = Path(root)
    checks_path = root / "checksums.json"
    if not checks_path.exists():
        return {"valid": False, "files_checked": 0, "failures": ["missing checksums.json"]}
    expected = json.loads(checks_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for rel, expected_sha in expected.items():
        path = root / rel
        if not path.exists():
            failures.append(f"missing:{rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_sha:
            failures.append(f"sha256:{rel}")
    return {"valid": not failures, "files_checked": len(expected), "failures": failures}
