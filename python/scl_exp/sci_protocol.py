from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field


def _canonical(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash_without_sha(value: dict) -> str:
    payload = {k: v for k, v in value.items() if k != "sha256"}
    return hashlib.sha256(_canonical(payload)).hexdigest()


def verify_package(package: dict) -> bool:
    sha = package.get("sha256")
    return isinstance(sha, str) and sha == _hash_without_sha(package)


def build_envelope(
    package: dict,
    *,
    version: int,
    parent_sha256: str | None,
    source_agent: str,
    event_type: str,
    provenance: dict,
) -> dict:
    if version < 1:
        raise ValueError("version must be >= 1")
    payload = {
        "schema": "sci-protocol-envelope/v0.1",
        "symbol": package.get("symbol"),
        "version": int(version),
        "parent_sha256": parent_sha256,
        "package": copy.deepcopy(package),
        "package_sha256": package.get("sha256"),
        "source_agent": source_agent,
        "event_type": event_type,
        "provenance": copy.deepcopy(provenance),
    }
    payload["sha256"] = _hash_without_sha(payload)
    return payload


def verify_envelope(envelope: dict) -> bool:
    if envelope.get("schema") != "sci-protocol-envelope/v0.1":
        return False
    if not isinstance(envelope.get("package"), dict) or not verify_package(envelope["package"]):
        return False
    if envelope.get("package_sha256") != envelope["package"].get("sha256"):
        return False
    return envelope.get("sha256") == _hash_without_sha(envelope)


@dataclass
class ProtocolState:
    symbol: str
    active_package: dict
    version: int
    accepted_hashes: set[str] = field(default_factory=set)
    superseded_hashes: set[str] = field(default_factory=set)
    history: list[dict] = field(default_factory=list)

    @property
    def active_package_sha256(self) -> str:
        return self.active_package["sha256"]

    @classmethod
    def from_package(cls, package: dict, *, version: int, superseded: set[str] | None = None) -> "ProtocolState":
        return cls(
            symbol=package["symbol"],
            active_package=copy.deepcopy(package),
            version=int(version),
            accepted_hashes={package["sha256"]},
            superseded_hashes=set(superseded or set()),
            history=[],
        )


@dataclass
class ProtocolBatchResult:
    state: ProtocolState
    accepted: list[dict]
    rejected: list[dict]


def _reject(envelope: dict, reason: str) -> dict:
    return {
        "status": "rejected",
        "reason": reason,
        "source_agent": envelope.get("source_agent"),
        "version": envelope.get("version"),
        "package_sha256": envelope.get("package_sha256"),
        "event_type": envelope.get("event_type"),
    }


def _accept(envelope: dict, status: str) -> dict:
    return {
        "status": status,
        "source_agent": envelope.get("source_agent"),
        "version": envelope.get("version"),
        "package_sha256": envelope.get("package_sha256"),
        "event_type": envelope.get("event_type"),
    }


def process_protocol_batch(state: ProtocolState, envelopes: list[dict]) -> ProtocolBatchResult:
    current = copy.deepcopy(state)
    accepted: list[dict] = []
    rejected: list[dict] = []

    prelim_valid: list[dict] = []
    for env in envelopes:
        if not isinstance(env.get("provenance"), dict) or not env.get("provenance"):
            rejected.append(_reject(env, "missing_provenance"))
            continue
        if not verify_envelope(env):
            rejected.append(_reject(env, "invalid_envelope_or_package_hash"))
            continue
        if env.get("symbol") != current.symbol or env.get("package", {}).get("symbol") != current.symbol:
            rejected.append(_reject(env, "symbol_mismatch"))
            continue
        prelim_valid.append(env)

    # Detect forward forks before applying any competing correction.
    groups: dict[tuple, list[dict]] = {}
    for env in prelim_valid:
        key = (env.get("symbol"), env.get("version"), env.get("parent_sha256"))
        groups.setdefault(key, []).append(env)
    conflicted_ids: set[int] = set()
    for rows in groups.values():
        hashes = {row.get("package_sha256") for row in rows}
        versions = {int(row.get("version", -1)) for row in rows}
        if len(rows) > 1 and len(hashes) > 1 and min(versions) > current.version:
            for row in rows:
                conflicted_ids.add(id(row))
                rejected.append(_reject(row, "conflicting_correction"))

    candidates = [env for env in prelim_valid if id(env) not in conflicted_ids]
    candidates.sort(key=lambda env: (int(env["version"]), env.get("source_agent", ""), env.get("sha256", "")))

    for env in candidates:
        version = int(env["version"])
        pkg_sha = env["package_sha256"]
        if version < current.version:
            rejected.append(_reject(env, "stale_version"))
            continue
        if version == current.version:
            if pkg_sha == current.active_package_sha256:
                accepted.append(_accept(env, "idempotent"))
                continue
            rejected.append(_reject(env, "same_version_conflict"))
            continue
        if pkg_sha in current.superseded_hashes:
            rejected.append(_reject(env, "rollback_to_superseded"))
            continue
        if env.get("provenance", {}).get("operation") == "rollback":
            rejected.append(_reject(env, "rollback_to_superseded" if pkg_sha in current.superseded_hashes else "rollback_not_allowed"))
            continue
        if version != current.version + 1:
            rejected.append(_reject(env, "non_monotonic_version"))
            continue
        if env.get("parent_sha256") != current.active_package_sha256:
            rejected.append(_reject(env, "parent_mismatch"))
            continue

        old_sha = current.active_package_sha256
        current.superseded_hashes.add(old_sha)
        current.active_package = copy.deepcopy(env["package"])
        current.version = version
        current.accepted_hashes.add(pkg_sha)
        row = _accept(env, "accepted")
        accepted.append(row)
        current.history.append(row)

    return ProtocolBatchResult(state=current, accepted=accepted, rejected=rejected)
