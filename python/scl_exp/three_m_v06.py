from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .sci import dense_signature


def _dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def export_three_m_v06(result: dict, root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    feature_ids = list(result["feature_ids"])

    feature_rows: list[dict] = []
    metric_rows: list[dict] = []
    route_rows: list[dict] = []
    ledger_rows: list[dict] = []

    for arm, arm_obj in sorted(result["arms"].items()):
        summary = arm_obj["summary"]
        for key, value in sorted(summary.items()):
            if isinstance(value, (int, float, bool)) and value is not None:
                metric_rows.append({"policy": arm, "metric": key, "value": value})
        for index, event in enumerate(arm_obj["events"], start=1):
            ledger_rows.append({"policy": arm, "sequence": index, **event})
            route_rows.append({
                "route": "transition-law",
                "policy": arm,
                "sequence": index,
                "event_id": event["event_id"],
                "truth_effect": event["truth_effect"],
                "accepted": event["accepted"],
                "reason": event["reason"],
                "evidence_consumed": event["evidence_consumed"],
                "independent_origins": event["independent_origins"],
            })

        package = arm_obj["final_state"]["active_package"]
        dense = dense_signature(package, feature_ids)
        for fid, value in zip(feature_ids, dense):
            feature_rows.append({
                "policy": arm,
                "phase": "final",
                "feature": fid,
                "value": float(value),
                "package_sha256": package["sha256"],
            })

    manifest = {
        "schema": "scl-3m-bounded/v0.6",
        "experiment_id": "EXP-0006",
        "conformance": "bounded-profile-not-formal-mlf-1.0",
        "roles": {
            "MLF": "policy/event/feature coordinates, provenance and checksum ledger",
            "MMR": "policy↔event↔feature multidirectional projections",
            "MMLC": "deterministic plasticity/integrity/target-distortion calculations",
            "AI_Board": "append-only transition proposal/accept/reject compatibility events",
            "CTCL": "deterministic logical event order only; no live verified time call",
        },
        "feature_count": len(feature_ids),
        "policies": sorted(result["arms"]),
        "hypotheses": result["hypotheses"],
    }
    substrate = {
        "feature_ids": feature_ids,
        "event_fixtures": result["event_fixtures"],
        "boundaries": result["boundaries"],
        "reference_package_sha256": result["reference"]["sha256"],
    }
    projection_loss = {
        "policy_summaries": {name: row["summary"] for name, row in sorted(result["arms"].items())},
        "hypotheses": result["hypotheses"],
    }

    _dump_json(root / "manifest.json", manifest)
    _dump_json(root / "substrate.json", substrate)
    _dump_jsonl(root / "matrices/policy_final_feature.cells.jsonl", feature_rows)
    _dump_jsonl(root / "matrices/transition_metrics.cells.jsonl", metric_rows)
    _dump_jsonl(root / "graphs/routes.jsonl", route_rows)
    _dump_jsonl(root / "ledgers/transition_events.jsonl", ledger_rows)
    _dump_jsonl(root / "provenance/events.jsonl", [{
        "event": "export",
        "experiment_id": "EXP-0006",
        "public_ai_board_write": False,
        "live_ctcl_call": False,
        "neural_retraining": False,
        "synthetic_transition_ground_truth": True,
    }])
    _dump_json(root / "reports/projection_loss.json", projection_loss)

    checksums = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {"checksums.json", "verification.json"} and not path.name.startswith("GITHUB_"):
            checksums[str(path.relative_to(root)).replace("\\", "/")] = hashlib.sha256(path.read_bytes()).hexdigest()
    _dump_json(root / "checksums.json", checksums)


def verify_three_m_v06(root: Path) -> dict:
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
