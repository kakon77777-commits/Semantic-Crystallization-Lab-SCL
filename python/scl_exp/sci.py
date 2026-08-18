from __future__ import annotations

import hashlib
import json
from typing import Iterable

import numpy as np


def _canonical_payload(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _with_hash(payload: dict) -> dict:
    out = dict(payload)
    out["sha256"] = hashlib.sha256(_canonical_payload(payload)).hexdigest()
    return out


def build_sci_package(
    symbol: str,
    signature: Iterable[float],
    feature_ids: list[str],
    source_agent: str,
    *,
    top_k: int = 12,
    expansion: list[str] | None = None,
    namespace: str = "scl.sci",
    version: str = "0.1",
    provenance: dict | None = None,
) -> dict:
    values = np.asarray(list(signature), dtype=float)
    if values.shape != (len(feature_ids),):
        raise ValueError("signature width must match feature_ids")
    if top_k <= 0 or top_k > len(feature_ids):
        raise ValueError("top_k out of range")
    order = sorted(range(len(feature_ids)), key=lambda i: (-float(values[i]), feature_ids[i]))[:top_k]
    weights = {feature_ids[i]: float(values[i]) for i in order}
    payload = {
        "schema": "sci-package/v0.1",
        "namespace": namespace,
        "version": version,
        "symbol": symbol,
        "source_agent": source_agent,
        "feature_space": "SCL-F01-F19-v0.2",
        "weights": weights,
        "expansion": list(expansion if expansion is not None else (["narel", "vek", "vesh"] if symbol == "qevra" else [])),
        "provenance": dict(provenance or {}),
    }
    return _with_hash(payload)


def dense_signature(package: dict, feature_ids: list[str]) -> np.ndarray:
    return np.array([float(package.get("weights", {}).get(fid, 0.0)) for fid in feature_ids], dtype=float)


def robust_merge_packages(packages: list[dict], feature_ids: list[str], *, source_agent: str = "multi-agent-median") -> dict:
    if not packages:
        raise ValueError("packages required")
    symbol = packages[0]["symbol"]
    if any(p.get("symbol") != symbol for p in packages):
        raise ValueError("cannot merge different symbols")
    matrix = np.stack([dense_signature(p, feature_ids) for p in packages])
    median = np.median(matrix, axis=0)
    return build_sci_package(
        symbol,
        median,
        feature_ids,
        source_agent,
        top_k=len(feature_ids),
        expansion=packages[0].get("expansion", []),
        provenance={"merge": "coordinatewise-median", "inputs": [p.get("sha256") for p in packages]},
    )


def objection_records(proposal: dict, local: dict, feature_ids: list[str], *, threshold: float = 0.15) -> list[dict]:
    p = dense_signature(proposal, feature_ids)
    l = dense_signature(local, feature_ids)
    rows = []
    for fid, pv, lv in zip(feature_ids, p, l):
        delta = float(lv - pv)
        if abs(delta) + 1e-12 >= float(threshold):
            rows.append({
                "feature": fid,
                "proposal": float(pv),
                "local": float(lv),
                "delta": delta,
                "direction": "raise" if delta > 0 else "lower",
            })
    return rows


def contaminate_package(
    package: dict,
    feature_ids: list[str],
    *,
    boost: dict[str, float] | None = None,
    suppress: dict[str, float] | None = None,
    source_agent: str = "shared-correlated-contamination",
) -> dict:
    values = dense_signature(package, feature_ids)
    index = {fid: i for i, fid in enumerate(feature_ids)}
    for fid, value in (boost or {}).items():
        values[index[fid]] = max(float(values[index[fid]]), float(value))
    for fid, value in (suppress or {}).items():
        values[index[fid]] = min(float(values[index[fid]]), float(value))
    return build_sci_package(
        package["symbol"],
        values,
        feature_ids,
        source_agent,
        top_k=len(feature_ids),
        expansion=package.get("expansion", []),
        provenance={"contaminated_from": package.get("sha256"), "boost": boost or {}, "suppress": suppress or {}},
    )
