from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from .grid import js_divergence
from .sci import dense_signature


def _dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _iter_packages(result: dict):
    p = result.get("packages", {})
    for group in ("qevra", "tivak"):
        value = p.get(group, {})
        if isinstance(value, dict):
            for name, package in value.items():
                if isinstance(package, dict) and package.get("weights") is not None:
                    yield f"{group}:{name}", package
    for key in ("merged_qevra", "merged_tivak", "contaminated_qevra"):
        package = p.get(key)
        if isinstance(package, dict) and package.get("weights") is not None:
            yield key, package


def export_three_m_v04(result: dict, root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    feature_ids = list(result.get("feature_ids", []))
    agent_feature_rows = []
    agent_distance_rows = []
    package_rows = []
    routes = []

    for phase, phase_obj in result.get("phases", {}).items():
        agents = phase_obj.get("agents", {})
        names = sorted(agents)
        for agent in names:
            for symbol in ("qevra", "tivak"):
                centroid = agents[agent].get(symbol, {}).get("centroid", [])
                for fid, value in zip(feature_ids, centroid):
                    agent_feature_rows.append({"phase": phase, "agent": agent, "symbol": symbol, "feature": fid, "value": float(value)})
                routes.append({"route": "agent_symbol_to_feature", "phase": phase, "agent": agent, "symbol": symbol, "features": feature_ids})
        for symbol in ("qevra", "tivak"):
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = names[i], names[j]
                    av = np.asarray(agents[a][symbol]["centroid"], dtype=float)
                    bv = np.asarray(agents[b][symbol]["centroid"], dtype=float)
                    agent_distance_rows.append({"phase": phase, "symbol": symbol, "agent_a": a, "agent_b": b, "js": js_divergence(av, bv)})
                    routes.append({"route": "agent_to_agent_feature_distance", "phase": phase, "symbol": symbol, "from": a, "to": b})

    for package_id, package in _iter_packages(result):
        dense = dense_signature(package, feature_ids)
        for fid, value in zip(feature_ids, dense):
            package_rows.append({"package_id": package_id, "symbol": package.get("symbol"), "source_agent": package.get("source_agent"), "feature": fid, "value": float(value)})
        routes.append({"route": "sci_package_to_feature", "package_id": package_id, "features": feature_ids})

    manifest = {
        "schema": "scl-3m-bounded/v0.4",
        "experiment_id": "EXP-0004",
        "conformance": "bounded-profile-not-formal-mlf-1.0",
        "roles": {
            "MLF": "coordinates/provenance/checksums/portable-SCI packages",
            "MMR": "agent↔feature, agent↔agent and package↔feature multidirectional projections",
            "MMLC": "deterministic JS, support, transfer, correction and contamination calculations",
            "AI_Board": "append-only SCI proposal/objection/correction/merge compatibility ledger",
            "CTCL": "logical instant compatibility only; no live verified instant",
        },
        "feature_count": len(feature_ids),
        "agent_count": len(result.get("seeds", [])),
        "phases": list(result.get("phases", {}).keys()),
    }
    _dump_json(root / "manifest.json", manifest)
    _dump_json(root / "substrate.json", {"features": feature_ids, "seeds": result.get("seeds", []), "boundaries": result.get("boundaries", {})})
    _dump_jsonl(root / "matrices/agent_feature.cells.jsonl", agent_feature_rows)
    _dump_jsonl(root / "matrices/agent_distance.cells.jsonl", agent_distance_rows)
    _dump_jsonl(root / "matrices/package_feature.cells.jsonl", package_rows)
    _dump_jsonl(root / "graphs/routes.jsonl", routes)
    _dump_jsonl(root / "ledgers/ai_board_sci.jsonl", list(result.get("ledger", [])))
    _dump_jsonl(root / "provenance/events.jsonl", [{"event": "export", "experiment_id": "EXP-0004", "seeds": result.get("seeds", []), "public_ai_board_write": False, "live_ctcl_call": False}])
    _dump_json(root / "reports/projection_loss.json", {"hypotheses": result.get("hypotheses", {}), "phase_summaries": {k: v.get("summary", {}) for k, v in result.get("phases", {}).items()}})

    checksums = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {"checksums.json", "verification.json"}:
            checksums[str(path.relative_to(root)).replace("\\", "/")] = hashlib.sha256(path.read_bytes()).hexdigest()
    _dump_json(root / "checksums.json", checksums)


def verify_three_m_v04(root: Path) -> dict:
    root = Path(root)
    checks_path = root / "checksums.json"
    if not checks_path.exists():
        return {"valid": False, "files_checked": 0, "failures": ["missing checksums.json"]}
    expected = json.loads(checks_path.read_text(encoding="utf-8"))
    failures = []
    for rel, sha in expected.items():
        path = root / rel
        if not path.exists():
            failures.append(f"missing:{rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != sha:
            failures.append(f"sha256:{rel}")
    return {"valid": not failures, "files_checked": len(expected), "failures": failures}
