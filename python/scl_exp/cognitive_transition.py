from __future__ import annotations

import copy
from dataclasses import dataclass, field

import numpy as np

from .grid import js_divergence
from .sci import dense_signature
from .sci_protocol import verify_package


@dataclass(frozen=True)
class TransitionPolicy:
    name: str
    mode: str
    quorum: int = 0
    max_evidence_js: float = 0.02
    max_candidate_median_js: float = 0.01

    @classmethod
    def rigid(cls) -> "TransitionPolicy":
        return cls(name="Rigid", mode="rigid")

    @classmethod
    def permissive(cls) -> "TransitionPolicy":
        return cls(name="Permissive", mode="permissive")

    @classmethod
    def adaptive(
        cls,
        *,
        quorum: int,
        max_evidence_js: float = 0.02,
        max_candidate_median_js: float = 0.01,
    ) -> "TransitionPolicy":
        if quorum < 2:
            raise ValueError("adaptive quorum must be >= 2")
        return cls(
            name=f"Adaptive-Q{quorum}",
            mode="adaptive",
            quorum=int(quorum),
            max_evidence_js=float(max_evidence_js),
            max_candidate_median_js=float(max_candidate_median_js),
        )


@dataclass
class TransitionState:
    symbol: str
    active_package: dict
    generation: int
    history: list[dict] = field(default_factory=list)


@dataclass
class TransitionOutcome:
    state: TransitionState
    accepted: bool
    reason: str
    evidence_consumed: int
    independent_origins: int
    independent_agents: int
    candidate_median_js: float | None = None


def build_transition_request(
    state: TransitionState,
    candidate_package: dict,
    *,
    source_agent: str,
    event_type: str,
    provenance: dict,
) -> dict:
    return {
        "schema": "sci-transition-request/v0.1",
        "symbol": state.symbol,
        "generation": state.generation + 1,
        "parent_sha256": state.active_package["sha256"],
        "candidate_package": copy.deepcopy(candidate_package),
        "source_agent": source_agent,
        "event_type": event_type,
        "provenance": copy.deepcopy(provenance),
    }


def _validate_request(state: TransitionState, request: dict) -> str | None:
    if request.get("schema") != "sci-transition-request/v0.1":
        return "invalid_request_schema"
    if request.get("symbol") != state.symbol:
        return "symbol_mismatch"
    if int(request.get("generation", -1)) != state.generation + 1:
        return "non_monotonic_generation"
    if request.get("parent_sha256") != state.active_package.get("sha256"):
        return "parent_mismatch"
    if not isinstance(request.get("provenance"), dict) or not request["provenance"]:
        return "missing_provenance"
    candidate = request.get("candidate_package")
    if not isinstance(candidate, dict) or not verify_package(candidate):
        return "invalid_candidate_package"
    if candidate.get("symbol") != state.symbol:
        return "symbol_mismatch"
    return None


def _evidence_supports_candidate(evidence: dict, candidate: dict, feature_ids: list[str], max_js: float) -> bool:
    package = evidence.get("package")
    if not isinstance(package, dict) or not verify_package(package):
        return False
    if package.get("symbol") != candidate.get("symbol"):
        return False
    if not evidence.get("source_agent") or not evidence.get("origin_root"):
        return False
    return js_divergence(dense_signature(package, feature_ids), dense_signature(candidate, feature_ids)) <= max_js


def _median_js(evidence: list[dict], candidate: dict, feature_ids: list[str]) -> float:
    matrix = np.stack([dense_signature(row["package"], feature_ids) for row in evidence])
    median = np.median(matrix, axis=0)
    return js_divergence(median, dense_signature(candidate, feature_ids))


def _accepted_state(state: TransitionState, request: dict, policy: TransitionPolicy, evidence_consumed: int) -> TransitionState:
    new = copy.deepcopy(state)
    new.active_package = copy.deepcopy(request["candidate_package"])
    new.generation = int(request["generation"])
    new.history.append({
        "event": "imprint.transition.accept",
        "policy": policy.name,
        "generation": new.generation,
        "package_sha256": new.active_package["sha256"],
        "evidence_consumed": evidence_consumed,
        "source_agent": request.get("source_agent"),
    })
    return new


def process_transition(
    state: TransitionState,
    request: dict,
    evidence_stream: list[dict],
    policy: TransitionPolicy,
    feature_ids: list[str],
) -> TransitionOutcome:
    structural_error = _validate_request(state, request)
    if structural_error:
        return TransitionOutcome(copy.deepcopy(state), False, structural_error, 0, 0, 0, None)

    if policy.mode == "rigid":
        return TransitionOutcome(copy.deepcopy(state), False, "rigid_semantic_lock", 0, 0, 0, None)

    if policy.mode == "permissive":
        if not evidence_stream:
            return TransitionOutcome(copy.deepcopy(state), False, "missing_evidence", 0, 0, 0, None)
        first = evidence_stream[0]
        roots = {first.get("origin_root")} if first.get("origin_root") else set()
        agents = {first.get("source_agent")} if first.get("source_agent") else set()
        return TransitionOutcome(
            _accepted_state(state, request, policy, 1),
            True,
            "accepted_permissive",
            1,
            len(roots),
            len(agents),
            None,
        )

    if policy.mode != "adaptive":
        raise ValueError(f"unknown transition policy mode: {policy.mode}")

    candidate = request["candidate_package"]
    supporting: list[dict] = []
    roots: set[str] = set()
    agents: set[str] = set()
    last_median_js: float | None = None

    for idx, row in enumerate(evidence_stream, start=1):
        if not _evidence_supports_candidate(row, candidate, feature_ids, policy.max_evidence_js):
            continue
        supporting.append(row)
        roots.add(str(row["origin_root"]))
        agents.add(str(row["source_agent"]))
        if len(roots) >= policy.quorum and len(agents) >= policy.quorum:
            last_median_js = _median_js(supporting, candidate, feature_ids)
            if last_median_js <= policy.max_candidate_median_js:
                return TransitionOutcome(
                    _accepted_state(state, request, policy, idx),
                    True,
                    "accepted_adaptive",
                    idx,
                    len(roots),
                    len(agents),
                    last_median_js,
                )

    if supporting:
        last_median_js = _median_js(supporting, candidate, feature_ids)
    return TransitionOutcome(
        copy.deepcopy(state),
        False,
        "insufficient_independent_evidence" if len(roots) < policy.quorum or len(agents) < policy.quorum else "evidence_disagrees_with_candidate",
        len(evidence_stream),
        len(roots),
        len(agents),
        last_median_js,
    )
