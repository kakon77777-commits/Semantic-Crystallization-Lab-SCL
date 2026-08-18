from __future__ import annotations

import copy
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .grid import js_divergence
from .persistent_cognition import CognitionState, restart_cognition
from .sci import dense_signature
from .sci_ledger import SciLedger
from .sci_protocol import ProtocolState, build_envelope, process_protocol_batch
from .stability import mean_pairwise_js


@dataclass(frozen=True)
class Exp0005Config:
    feature_space: str = "SCL-F01-F19-v0.2"
    protocol_schema: str = "sci-protocol-envelope/v0.1"
    accepted_version: int = 2
    fault_next_version: int = 3
    logical_restart_label: str = "session-2-restart"


ARM_FACTORS = {
    "A00": {"protocol": False, "persistence": False},
    "A01": {"protocol": False, "persistence": True},
    "A10": {"protocol": True, "persistence": False},
    "A11": {"protocol": True, "persistence": True},
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_exp0004_packages(repo_root: Path) -> tuple[list[str], dict[str, dict], dict, dict]:
    metrics = _load_json(repo_root / "experiments/EXP-0004/results/metrics.json")
    feature_ids = list(metrics["feature_ids"])
    independent = {name: copy.deepcopy(pkg) for name, pkg in metrics["packages"]["qevra"].items()}
    accepted = copy.deepcopy(metrics["packages"]["merged_qevra"])
    contaminated = copy.deepcopy(metrics["packages"]["contaminated_qevra"])
    return feature_ids, independent, accepted, contaminated


def _target(feature_ids: list[str]) -> np.ndarray:
    return np.array([1.0 if fid != "F19" else 0.0 for fid in feature_ids], dtype=float)


def _package_js(a: dict, b: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(a, feature_ids), dense_signature(b, feature_ids))


def _target_js(package: dict, feature_ids: list[str], target: np.ndarray) -> float:
    return js_divergence(dense_signature(package, feature_ids), target)


def _new_session1_state(agent: str, independent: dict, accepted: dict, cfg: Exp0005Config) -> CognitionState:
    return CognitionState(
        agent=agent,
        independent_package=copy.deepcopy(independent),
        active_package=copy.deepcopy(accepted),
        version=cfg.accepted_version,
        accepted_hashes=[independent["sha256"], accepted["sha256"]],
        superseded_hashes=[independent["sha256"]],
        history=[{
            "event": "imprint.correction",
            "version": cfg.accepted_version,
            "package_sha256": accepted["sha256"],
            "source": "EXP-0004-board-median-merge",
        }],
    )


def _bare_apply(state: CognitionState, package: dict, *, label: str) -> None:
    old = state.active_package["sha256"]
    if old != package["sha256"]:
        state.superseded_hashes.append(old)
    state.active_package = copy.deepcopy(package)
    state.version += 1
    state.accepted_hashes.append(package["sha256"])
    state.history.append({"event": "untyped-last-write-wins", "label": label, "package_sha256": package["sha256"]})


def _bootstrap_protocol(state: CognitionState, accepted: dict, cfg: Exp0005Config) -> tuple[CognitionState, dict]:
    pstate = ProtocolState(
        symbol="qevra",
        active_package=copy.deepcopy(state.active_package),
        version=state.version,
        accepted_hashes=set(state.accepted_hashes),
        superseded_hashes=set(state.superseded_hashes),
        history=copy.deepcopy(state.history),
    )
    env = build_envelope(
        accepted,
        version=cfg.accepted_version,
        parent_sha256=state.active_package["sha256"] if state.version < cfg.accepted_version else state.independent_package["sha256"],
        source_agent="board-median-merge",
        event_type="imprint.correction",
        provenance={"reason": "session-rebootstrap", "source_experiment": "EXP-0004"},
    )
    out = process_protocol_batch(pstate, [env])
    new = CognitionState(
        agent=state.agent,
        independent_package=copy.deepcopy(state.independent_package),
        active_package=copy.deepcopy(out.state.active_package),
        version=out.state.version,
        accepted_hashes=sorted(out.state.accepted_hashes),
        superseded_hashes=sorted(out.state.superseded_hashes),
        history=copy.deepcopy(out.state.history),
    )
    return new, {"accepted": out.accepted, "rejected": out.rejected, "envelope": env}


def _protocol_faults(state: CognitionState, donor: dict, contaminated: dict, accepted: dict, cfg: Exp0005Config) -> tuple[CognitionState, list[dict]]:
    pstate = ProtocolState(
        symbol="qevra",
        active_package=copy.deepcopy(state.active_package),
        version=state.version,
        accepted_hashes=set(state.accepted_hashes),
        superseded_hashes=set(state.superseded_hashes),
        history=copy.deepcopy(state.history),
    )
    records: list[dict] = []

    stale = build_envelope(
        donor, version=1, parent_sha256=None, source_agent="agent-A", event_type="imprint.proposal",
        provenance={"reason": "stale-version-fault"},
    )
    missing = build_envelope(
        contaminated, version=cfg.fault_next_version, parent_sha256=accepted["sha256"], source_agent="fault-source",
        event_type="imprint.correction", provenance={"reason": "missing-provenance-fault"},
    )
    missing["provenance"] = {}
    rollback = build_envelope(
        state.independent_package, version=cfg.fault_next_version, parent_sha256=accepted["sha256"], source_agent=state.agent,
        event_type="imprint.correction", provenance={"reason": "rollback-fault", "operation": "rollback"},
    )
    fork_good = build_envelope(
        accepted, version=cfg.fault_next_version, parent_sha256=accepted["sha256"], source_agent="agent-B",
        event_type="imprint.correction", provenance={"reason": "conflict-good"},
    )
    fork_bad = build_envelope(
        contaminated, version=cfg.fault_next_version, parent_sha256=accepted["sha256"], source_agent="agent-C",
        event_type="imprint.correction", provenance={"reason": "conflict-bad"},
    )

    for fault_name, batch in (
        ("stale_version", [stale]),
        ("missing_provenance", [missing]),
        ("rollback", [rollback]),
        ("conflicting_correction", [fork_good, fork_bad]),
    ):
        out = process_protocol_batch(pstate, batch)
        pstate = out.state
        records.append({"fault": fault_name, "accepted": out.accepted, "rejected": out.rejected})

    new = CognitionState(
        agent=state.agent,
        independent_package=copy.deepcopy(state.independent_package),
        active_package=copy.deepcopy(pstate.active_package),
        version=pstate.version,
        accepted_hashes=sorted(pstate.accepted_hashes),
        superseded_hashes=sorted(pstate.superseded_hashes),
        history=copy.deepcopy(pstate.history),
    )
    return new, records


def _untyped_faults(state: CognitionState, donor: dict, contaminated: dict, accepted: dict) -> list[dict]:
    records = []
    sequence = [
        ("stale_version", donor),
        ("missing_provenance", contaminated),
        ("rollback", state.independent_package),
        ("conflicting_correction:first", accepted),
        ("conflicting_correction:last", contaminated),
    ]
    for label, package in sequence:
        _bare_apply(state, package, label=label)
        records.append({"fault": label, "status": "accepted_untyped_last_write_wins", "package_sha256": package["sha256"]})
    return records


def _arm_summary(agent_rows: dict[str, dict], accepted: dict, feature_ids: list[str], target: np.ndarray, protocol: bool, persistence: bool) -> dict:
    restart_js = [row["restart_js"] for row in agent_rows.values()]
    finals = [dense_signature(row["final_state"]["active_package"], feature_ids) for row in agent_rows.values()]
    reason_counts = Counter()
    for row in agent_rows.values():
        for fault in row.get("fault_records", []):
            for rej in fault.get("rejected", []):
                reason_counts[rej["reason"]] += 1
    return {
        "protocol": protocol,
        "persistence": persistence,
        "mean_restart_js": float(np.mean(restart_js)),
        "max_restart_js": float(np.max(restart_js)),
        "prebootstrap_correction_retention": float(np.mean([row["prebootstrap_retained"] for row in agent_rows.values()])),
        "postbootstrap_correction_retention": float(np.mean([row["postbootstrap_retained"] for row in agent_rows.values()])),
        "final_correction_retention": float(np.mean([row["final_retained"] for row in agent_rows.values()])),
        "final_cross_agent_js": mean_pairwise_js(finals),
        "mean_final_target_js": float(np.mean([_target_js(row["final_state"]["active_package"], feature_ids, target) for row in agent_rows.values()])),
        "mean_final_js_from_accepted": float(np.mean([_package_js(row["final_state"]["active_package"], accepted, feature_ids) for row in agent_rows.values()])),
        "protocol_rejection_reasons": dict(sorted(reason_counts.items())),
        "mean_history_events_after_restart": float(np.mean([row["restart_history_count"] for row in agent_rows.values()])),
        "mean_history_events_final": float(np.mean([len(row["final_state"]["history"]) for row in agent_rows.values()])),
    }


def _state_dict(state: CognitionState) -> dict:
    return {
        "agent": state.agent,
        "active_package": copy.deepcopy(state.active_package),
        "version": state.version,
        "accepted_hashes": list(state.accepted_hashes),
        "superseded_hashes": list(state.superseded_hashes),
        "history": copy.deepcopy(state.history),
        "history_digest": state.history_digest(),
    }


def run_exp0005(repo_root: Path, config: Exp0005Config | None = None) -> dict:
    repo_root = Path(repo_root)
    cfg = config or Exp0005Config()
    feature_ids, independent, accepted, contaminated = _load_exp0004_packages(repo_root)
    donor = independent["agent-A"]
    target = _target(feature_ids)
    accepted_target_js = _target_js(accepted, feature_ids, target)
    arms: dict[str, dict] = {}

    for arm, factors in ARM_FACTORS.items():
        protocol = factors["protocol"]
        persistence = factors["persistence"]
        ledger = SciLedger(topic=f"scl-exp0005-{arm.lower()}")
        agent_rows: dict[str, dict] = {}

        for agent in sorted(independent):
            session1 = _new_session1_state(agent, independent[agent], accepted, cfg)
            ledger.append("imprint.correction", "board-median-merge", {
                "agent": agent, "session": 1, "version": cfg.accepted_version,
                "package_sha256": accepted["sha256"], "mode": "accepted-session1-reference",
            })
            restarted = restart_cognition(session1, persistent=persistence)
            restart_js = _package_js(session1.active_package, restarted.active_package, feature_ids)
            prebootstrap_retained = restarted.active_package["sha256"] == accepted["sha256"]
            ledger.append("imprint.transfer", agent, {
                "session": 2, "mode": "persistent-restore" if persistence else "nonpersistent-reset",
                "restart_js": restart_js, "active_package_sha256": restarted.active_package["sha256"],
            })

            if protocol:
                booted, bootstrap_record = _bootstrap_protocol(restarted, accepted, cfg)
                for row in bootstrap_record["accepted"]:
                    ledger.append("imprint.correction", "protocol", {"agent": agent, "session": 2, "bootstrap": row})
                for row in bootstrap_record["rejected"]:
                    ledger.append("imprint.objection", "protocol", {"agent": agent, "session": 2, "bootstrap": row})
            else:
                booted = copy.deepcopy(restarted)
                _bare_apply(booted, accepted, label="session2-bootstrap")
                bootstrap_record = {"accepted": [{"status": "accepted_untyped_last_write_wins", "package_sha256": accepted["sha256"]}], "rejected": []}
                ledger.append("imprint.transfer", "untyped-channel", {"agent": agent, "session": 2, "mode": "bootstrap-last-write-wins", "package_sha256": accepted["sha256"]})

            postbootstrap_retained = booted.active_package["sha256"] == accepted["sha256"]

            if protocol:
                final_state, fault_records = _protocol_faults(booted, donor, contaminated, accepted, cfg)
                for record in fault_records:
                    for row in record["accepted"]:
                        ledger.append("imprint.correction", "protocol", {"agent": agent, "fault": record["fault"], "result": row})
                    for row in record["rejected"]:
                        ledger.append("imprint.objection", "protocol", {"agent": agent, "fault": record["fault"], "result": row})
            else:
                final_state = copy.deepcopy(booted)
                fault_records = _untyped_faults(final_state, donor, contaminated, accepted)
                for record in fault_records:
                    ledger.append("imprint.transfer", "untyped-channel", {"agent": agent, "fault": record})

            final_retained = final_state.active_package["sha256"] == accepted["sha256"]
            agent_rows[agent] = {
                "restart_js": restart_js,
                "prebootstrap_retained": prebootstrap_retained,
                "postbootstrap_retained": postbootstrap_retained,
                "final_retained": final_retained,
                "restart_history_count": len(restarted.history),
                "session1_state": _state_dict(session1),
                "restart_state": _state_dict(restarted),
                "bootstrap_record": bootstrap_record,
                "fault_records": fault_records,
                "final_state": _state_dict(final_state),
                "final_target_js": _target_js(final_state.active_package, feature_ids, target),
                "final_js_from_accepted": _package_js(final_state.active_package, accepted, feature_ids),
            }

        summary = _arm_summary(agent_rows, accepted, feature_ids, target, protocol, persistence)
        arms[arm] = {"factors": factors, "agents": agent_rows, "summary": summary, "ledger": ledger.events}

    hypotheses = {
        "H1_persistence_reduces_restart_drift": arms["A01"]["summary"]["mean_restart_js"] < arms["A00"]["summary"]["mean_restart_js"] and arms["A11"]["summary"]["mean_restart_js"] < arms["A10"]["summary"]["mean_restart_js"],
        "H2_protocol_preserves_correction_under_faults": arms["A10"]["summary"]["final_correction_retention"] > arms["A00"]["summary"]["final_correction_retention"] and arms["A11"]["summary"]["final_correction_retention"] > arms["A01"]["summary"]["final_correction_retention"],
        "H3_joint_protocol_persistence_dominates_continuity": arms["A11"]["summary"]["mean_restart_js"] < 1e-12 and arms["A11"]["summary"]["final_correction_retention"] == 1.0,
        "H4_persistence_alone_insufficient_against_overwrite": arms["A01"]["summary"]["prebootstrap_correction_retention"] == 1.0 and arms["A01"]["summary"]["final_correction_retention"] == 0.0,
        "H5_protocol_alone_recovers_but_restart_discontinuity_remains": arms["A10"]["summary"]["prebootstrap_correction_retention"] == 0.0 and arms["A10"]["summary"]["postbootstrap_correction_retention"] == 1.0 and arms["A10"]["summary"]["final_correction_retention"] == 1.0 and arms["A10"]["summary"]["mean_restart_js"] > 0.0,
        "H6_consensus_is_not_truth_signal": arms["A00"]["summary"]["final_cross_agent_js"] < 1e-12 and arms["A00"]["summary"]["mean_final_target_js"] > accepted_target_js,
    }

    return {
        "schema": "scl-exp0005/v0.5",
        "experiment_id": "EXP-0005",
        "title": "Protocol–Persistent Cognition Continuity",
        "sci_definition": "Symbolic Cognitive Imprint (SCI) / 符號認知印刻",
        "config": asdict(cfg),
        "feature_ids": feature_ids,
        "reference": {
            "accepted_package": accepted,
            "accepted_target_js": accepted_target_js,
            "contaminated_package": contaminated,
            "contaminated_target_js": _target_js(contaminated, feature_ids, target),
            "donor_package": donor,
            "donor_target_js": _target_js(donor, feature_ids, target),
        },
        "arms": arms,
        "hypotheses": hypotheses,
        "boundaries": {
            "neural_retraining": False,
            "cross_agent_coordinate": "shared F01-F19 feature space only",
            "public_ai_board_write": False,
            "live_ctcl_call": False,
            "ctcl_mode": "deterministic-logical-instant-compatibility-only",
        },
    }
