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


def export_three_m_v05(result: dict, root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    feature_ids = list(result["feature_ids"])

    state_rows: list[dict] = []
    metric_rows: list[dict] = []
    routes: list[dict] = []
    ledger_rows: list[dict] = []

    for arm, arm_obj in sorted(result["arms"].items()):
        factors = arm_obj["factors"]
        summary = arm_obj["summary"]
        for key, value in sorted(summary.items()):
            if isinstance(value, (int, float, bool)):
                metric_rows.append({"arm": arm, "metric": key, "value": value, **factors})
        for agent, row in sorted(arm_obj["agents"].items()):
            for phase_key, phase in (("session1", row["session1_state"]), ("restart", row["restart_state"]), ("final", row["final_state"])):
                package = phase["active_package"]
                dense = dense_signature(package, feature_ids)
                for fid, value in zip(feature_ids, dense):
                    state_rows.append({
                        "arm": arm,
                        "agent": agent,
                        "phase": phase_key,
                        "protocol": factors["protocol"],
                        "persistence": factors["persistence"],
                        "feature": fid,
                        "value": float(value),
                        "package_sha256": package["sha256"],
                    })
                routes.append({
                    "route": "sci_continuity_transition",
                    "arm": arm,
                    "agent": agent,
                    "phase": phase_key,
                    "package_sha256": package["sha256"],
                    "version": phase["version"],
                })
            routes.append({
                "route": "restart_then_bootstrap_then_faults",
                "arm": arm,
                "agent": agent,
                "restart_js": row["restart_js"],
                "prebootstrap_retained": row["prebootstrap_retained"],
                "postbootstrap_retained": row["postbootstrap_retained"],
                "final_retained": row["final_retained"],
            })
        for event in arm_obj.get("ledger", []):
            ledger_rows.append({"arm": arm, **event})

    manifest = {
        "schema": "scl-3m-bounded/v0.5",
        "experiment_id": "EXP-0005",
        "conformance": "bounded-profile-not-formal-mlf-1.0",
        "roles": {
            "MLF": "arm/session/agent coordinates, provenance, hashes and correction state",
            "MMR": "arm↔agent↔session↔feature multidirectional projections",
            "MMLC": "deterministic restart JS, target JS, retention and protocol-fault calculations",
            "AI_Board": "append-only proposal/correction/objection/transfer compatibility ledger",
            "CTCL": "deterministic logical instants only; no live verified time call",
        },
        "feature_count": len(feature_ids),
        "arms": sorted(result["arms"]),
        "hypotheses": result["hypotheses"],
    }
    substrate = {
        "feature_ids": feature_ids,
        "factorial": {arm: obj["factors"] for arm, obj in sorted(result["arms"].items())},
        "boundaries": result["boundaries"],
        "reference_package_sha256": result["reference"]["accepted_package"]["sha256"],
    }
    projection_loss = {
        "accepted_target_js": result["reference"]["accepted_target_js"],
        "contaminated_target_js": result["reference"]["contaminated_target_js"],
        "arm_summaries": {arm: obj["summary"] for arm, obj in sorted(result["arms"].items())},
        "hypotheses": result["hypotheses"],
    }

    _dump_json(root / "manifest.json", manifest)
    _dump_json(root / "substrate.json", substrate)
    _dump_jsonl(root / "matrices/arm_agent_session_feature.cells.jsonl", state_rows)
    _dump_jsonl(root / "matrices/continuity_metrics.cells.jsonl", metric_rows)
    _dump_jsonl(root / "graphs/routes.jsonl", routes)
    _dump_jsonl(root / "ledgers/ai_board_sci.jsonl", ledger_rows)
    _dump_jsonl(root / "provenance/events.jsonl", [{
        "event": "export",
        "experiment_id": "EXP-0005",
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


def verify_three_m_v05(root: Path) -> dict:
    root = Path(root)
    checks_path = root / "checksums.json"
    if not checks_path.exists():
        return {"valid": False, "files_checked": 0, "failures": ["missing checksums.json"]}
    expected = json.loads(checks_path.read_text(encoding="utf-8"))
    failures = []
    for rel, expected_sha in expected.items():
        path = root / rel
        if not path.exists():
            failures.append(f"missing:{rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_sha:
            failures.append(f"sha256:{rel}")
    return {"valid": not failures, "files_checked": len(expected), "failures": failures}
