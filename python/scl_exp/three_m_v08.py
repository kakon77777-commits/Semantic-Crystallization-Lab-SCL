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


def export_three_m_v08(result: dict, root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    feature_ids = list(result["feature_ids"])

    final_feature_rows: list[dict] = []
    metric_rows: list[dict] = []
    trust_rows: list[dict] = []
    route_rows: list[dict] = []
    ledger_rows: list[dict] = []

    for policy_name, arm in sorted(result["arms"].items()):
        for key, value in sorted(arm["summary"].items()):
            if isinstance(value, (int, float, bool)) and value is not None:
                metric_rows.append({"policy": policy_name, "metric": key, "value": value})

        final_pkg = arm["final_state"]["active_package"]
        for fid, value in zip(feature_ids, dense_signature(final_pkg, feature_ids)):
            final_feature_rows.append({"policy": policy_name, "feature": fid, "value": float(value), "package_sha256": final_pkg["sha256"]})

        for index, event in enumerate(arm["events"], start=1):
            ledger_rows.append({"policy": policy_name, "sequence": index, **event})
            route_rows.append({"route": "trust-dynamics-admission", "policy": policy_name, "sequence": index, "event_id": event["event_id"], "phase": event["phase"], "truth_effect": event["truth_effect"], "accepted": event["accepted"], "reason": event["reason"], "risk": event["risk"], "novelty_js": event["novelty_js"]})

        if policy_name != "Oracle":
            for row in arm["trust_trajectory"]:
                for origin_root, trust in sorted(row["trust"].items()):
                    trust_rows.append({"policy": policy_name, "event_id": row["event_id"], "phase": row["phase"], "origin_root": origin_root, "mean": trust["mean"], "volatility": trust["volatility"], "alpha": trust["alpha"], "beta": trust["beta"], "required_support": row["required_support"], "effective_support": row["effective_support"], "recent_pollution_rate": row["recent_pollution_rate"]})

    manifest = {
        "schema": "scl-3m-bounded/v0.8",
        "experiment_id": "EXP-0008",
        "conformance": "bounded-profile-not-formal-mlf-1.0",
        "roles": {
            "MLF": "policy/event/root/trust-dynamics coordinates, provenance and checksums",
            "MMR": "policy↔event↔origin-root↔trust-state↔feature multidirectional projections",
            "MMLC": "deterministic delayed-feedback, decay, volatility, admission and loss calculations",
            "AI_Board": "append-only trust/admission event compatibility ledger",
            "CTCL": "deterministic logical event order only; no live verified time call",
        },
        "feature_count": len(feature_ids),
        "policies": sorted(result["arms"]),
        "hypotheses": result["hypotheses"],
    }
    substrate = {"feature_ids": feature_ids, "event_fixtures": result["event_fixtures"], "boundaries": result["boundaries"], "reference_package_sha256": result["reference_sha256"], "feedback_mode": result["boundaries"]["feedback_mode"], "shared_admission_threshold_formula": True}
    projection_loss = {"policy_summaries": {name: row["summary"] for name, row in sorted(result["arms"].items())}, "trust_brier": {name: row.get("trust_brier") for name, row in sorted(result["arms"].items()) if name != "Oracle"}, "hypotheses": result["hypotheses"]}

    _dump_json(root / "manifest.json", manifest)
    _dump_json(root / "substrate.json", substrate)
    _dump_jsonl(root / "matrices/policy_final_feature.cells.jsonl", final_feature_rows)
    _dump_jsonl(root / "matrices/policy_metrics.cells.jsonl", metric_rows)
    _dump_jsonl(root / "matrices/root_trust_dynamics.cells.jsonl", trust_rows)
    _dump_jsonl(root / "graphs/routes.jsonl", route_rows)
    _dump_jsonl(root / "ledgers/trust_dynamics_events.jsonl", ledger_rows)
    _dump_jsonl(root / "provenance/events.jsonl", [{"event": "export", "experiment_id": "EXP-0008", "feedback_mode": "one_event_delayed", "current_truth_visible_to_policy": False, "shared_admission_threshold_formula": True, "public_ai_board_write": False, "live_ctcl_call": False, "neural_retraining": False}])
    _dump_json(root / "reports/projection_loss.json", projection_loss)

    checksums = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {"checksums.json", "verification.json"} and not path.name.startswith("GITHUB_"):
            checksums[str(path.relative_to(root)).replace("\\", "/")] = hashlib.sha256(path.read_bytes()).hexdigest()
    _dump_json(root / "checksums.json", checksums)


def verify_three_m_v08(root: Path) -> dict:
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
