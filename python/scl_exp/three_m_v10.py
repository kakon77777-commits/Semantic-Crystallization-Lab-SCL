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


def export_three_m_v10(result: dict, root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    metric_rows: list[dict] = []
    decision_rows: list[dict] = []
    route_rows: list[dict] = []
    ledger_rows: list[dict] = []
    artifact_rows = [
        {"artifact_type": "report", "experiment": exp_id, "sha256": sha}
        for exp_id, sha in sorted(result["artifact_pack"]["report_sha256"].items())
    ] + [
        {"artifact_type": "validation", "experiment": exp_id, "sha256": sha}
        for exp_id, sha in sorted(result["artifact_pack"]["validation_sha256"].items())
    ]
    trust_rows = [
        {"sequence": i + 1, "event_id": event["event_id"], "trust_snapshot_sha256": sha}
        for i, (event, sha) in enumerate(zip(result["events"], result["shared_trust_snapshot_hashes"]))
    ]

    for policy_name, arm in sorted(result["policies"].items()):
        for key, value in sorted(arm["summary"].items()):
            if isinstance(value, (int, float, bool)) and value is not None:
                metric_rows.append({"policy": policy_name, "metric": key, "value": value})
        for phase, value in sorted(arm["summary"]["phase_loss"].items()):
            metric_rows.append({"policy": policy_name, "metric": f"phase_loss:{phase}", "value": value})
        for sequence, event in enumerate(arm["events"], start=1):
            row = {"policy": policy_name, "sequence": sequence, **event}
            decision_rows.append(row)
            ledger_rows.append({
                "logical_instant": f"EXP0010-{policy_name}-{sequence:02d}",
                "event_type": f"imprint.reflexive-decision.{event['final_action']}",
                **row,
            })
            for step, action in enumerate(event["action_trace"], start=1):
                route_rows.append({
                    "route": "reflexive-epistemic-challenge",
                    "policy": policy_name,
                    "reflexive_order": arm["reflexive_order"],
                    "sequence": sequence,
                    "step": step,
                    "event_id": event["event_id"],
                    "phase": event["phase"],
                    "action": action,
                    "truth_effect": event["truth_effect"],
                    "prospective_challenge": event["prospective_challenge"],
                    "second_order_challenge": event["second_order_challenge"],
                    "challenge_score": event["challenge_score"],
                    "coalition_streak": event["coalition_streak"],
                    "cumulative_drift_js": event["cumulative_drift_js"],
                })

    manifest = {
        "schema": "scl-3m-bounded/v0.10",
        "experiment_id": "EXP-0010",
        "conformance": "bounded-profile-not-formal-mlf-1.0",
        "roles": {
            "MLF": "artifact/order/phase/policy/event/action/loss coordinates and hashes",
            "MMR": "artifact↔meta-rule↔policy↔event↔action↔loss multidirectional projections",
            "MMLC": "deterministic artifact compilation, prospective challenge, second-order challenge and loss calculations",
            "AI_Board": "append-only reflexive decision compatibility ledger",
            "CTCL": "deterministic logical event order only; no live verified time call",
        },
        "policies": sorted(result["policies"]),
        "hypotheses": result["hypotheses"],
        "memorization_guard": result["memorization_guard"],
    }
    substrate = {
        "feature_ids": result["feature_ids"],
        "boundaries": result["boundaries"],
        "artifact_pack": result["artifact_pack"],
        "event_fixtures": result["events"],
        "observable_meta_context": result["observable_meta_context"],
        "shared_trust_snapshot_hashes": result["shared_trust_snapshot_hashes"],
    }
    projection_loss = {
        "policy_summaries": {name: arm["summary"] for name, arm in sorted(result["policies"].items())},
        "a1_caught_a0_high_confidence_errors": result["a1_caught_a0_high_confidence_errors"],
        "a1_meta_exploits": result["a1_meta_exploits"],
        "a2_meta_catches": result["a2_meta_catches"],
        "hypotheses": result["hypotheses"],
    }

    _dump_json(root / "manifest.json", manifest)
    _dump_json(root / "substrate.json", substrate)
    _dump_jsonl(root / "matrices/policy_metrics.cells.jsonl", metric_rows)
    _dump_jsonl(root / "matrices/policy_event_reflexive_decision.cells.jsonl", decision_rows)
    _dump_jsonl(root / "matrices/artifact_rule_sources.cells.jsonl", artifact_rows)
    _dump_jsonl(root / "matrices/shared_trust_snapshots.cells.jsonl", trust_rows)
    _dump_jsonl(root / "graphs/routes.jsonl", route_rows)
    _dump_jsonl(root / "ledgers/reflexive_decisions.jsonl", ledger_rows)
    _dump_jsonl(root / "provenance/events.jsonl", [{
        "event": "export",
        "experiment_id": "EXP-0010",
        "artifact_exposure_is_experimental_factor": True,
        "phase_2_environment_conditioned_on_a1_rule": True,
        "new_fixture_candidate_hash_overlap_required_zero": True,
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


def verify_three_m_v10(root: Path) -> dict:
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
