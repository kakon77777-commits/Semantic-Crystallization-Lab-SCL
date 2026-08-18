from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .cognitive_transition import (
    TransitionPolicy,
    TransitionState,
    build_transition_request,
    process_transition,
)
from .grid import js_divergence
from .sci import build_sci_package, dense_signature


@dataclass(frozen=True)
class Exp0006Config:
    feature_space: str = "SCL-F01-F19-v0.2"
    evidence_noise: float = 0.008
    adaptive_max_evidence_js: float = 0.02
    adaptive_max_candidate_median_js: float = 0.01


POLICIES = {
    "Rigid": TransitionPolicy.rigid(),
    "Permissive": TransitionPolicy.permissive(),
    "Adaptive-Q2": TransitionPolicy.adaptive(quorum=2),
    "Adaptive-Q3": TransitionPolicy.adaptive(quorum=3),
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_reference(repo_root: Path) -> tuple[list[str], dict]:
    metrics = _load_json(repo_root / "experiments/EXP-0004/results/metrics.json")
    return list(metrics["feature_ids"]), copy.deepcopy(metrics["packages"]["merged_qevra"])


def _clip(v: float) -> float:
    return float(min(1.0, max(0.0, v)))


def _reweight(package: dict, feature_ids: list[str], adjustments: dict[str, float], *, source_agent: str, label: str) -> dict:
    values = dense_signature(package, feature_ids)
    idx = {fid: i for i, fid in enumerate(feature_ids)}
    for fid, delta in adjustments.items():
        values[idx[fid]] = _clip(float(values[idx[fid]]) + float(delta))
    return build_sci_package(
        package["symbol"],
        values,
        feature_ids,
        source_agent,
        top_k=len(feature_ids),
        expansion=package.get("expansion", []),
        provenance={"transition_fixture": label, "from": package.get("sha256")},
    )


def _target_js(package: dict, target: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(package, feature_ids), dense_signature(target, feature_ids))


def _evidence(candidate: dict, feature_ids: list[str], roots: list[str], *, prefix: str, noise: float) -> list[dict]:
    base = dense_signature(candidate, feature_ids)
    rows: list[dict] = []
    for i, root in enumerate(roots):
        sign = 0.0 if i % 3 == 2 else (1.0 if i % 3 == 0 else -1.0)
        values = base.copy()
        for j in range(len(values)):
            if j % 3 == i % 3:
                values[j] = _clip(float(values[j]) + sign * noise)
        pkg = build_sci_package(
            candidate["symbol"], values, feature_ids, f"{prefix}-observer-{i+1}", top_k=len(feature_ids),
            expansion=candidate.get("expansion", []),
            provenance={"origin_root": root, "supports": candidate["sha256"], "fixture": prefix},
        )
        rows.append({"source_agent": f"{prefix}-observer-{i+1}", "origin_root": root, "package": pkg})
    return rows


def _build_event_fixtures(reference: dict, feature_ids: list[str], cfg: Exp0006Config) -> list[dict]:
    # Genuine shifts represent an explicit synthetic changing ground truth for transition-law testing.
    t1 = _reweight(reference, feature_ids, {"F18": +0.36, "F16": +0.08, "F17": +0.05}, source_agent="truth-fixture", label="T1")
    a1 = _reweight(t1, feature_ids, {"F19": +0.46, "F07": -0.18, "F16": -0.14, "F01": -0.10}, source_agent="attack-fixture", label="A1")
    t2 = _reweight(t1, feature_ids, {"F05": +0.18, "F03": +0.10, "F04": +0.08, "F14": -0.08}, source_agent="truth-fixture", label="T2")
    a2 = _reweight(t2, feature_ids, {"F19": +0.36, "F10": -0.20, "F17": -0.18, "F06": -0.10}, source_agent="attack-fixture", label="A2")
    t3 = _reweight(t2, feature_ids, {"F18": +0.10, "F15": +0.05, "F16": +0.04, "F13": +0.03}, source_agent="truth-fixture", label="T3")
    return [
        {"event_id": "G1_three_origin_shift", "truth_effect": "genuine", "candidate": t1, "new_truth": t1, "roots": ["g1-root-a", "g1-root-b", "g1-root-c"]},
        {"event_id": "A1_correlated_echo", "truth_effect": "pollution", "candidate": a1, "new_truth": None, "roots": ["echo-root", "echo-root", "echo-root"]},
        {"event_id": "G2_two_origin_novelty", "truth_effect": "genuine", "candidate": t2, "new_truth": t2, "roots": ["g2-root-a", "g2-root-b"]},
        {"event_id": "A2_two_origin_attack", "truth_effect": "pollution", "candidate": a2, "new_truth": None, "roots": ["attack-root-a", "attack-root-b"]},
        {"event_id": "G3_three_origin_recovery", "truth_effect": "genuine", "candidate": t3, "new_truth": t3, "roots": ["g3-root-a", "g3-root-b", "g3-root-c"]},
    ]


def _harmonic(a: float, b: float) -> float:
    return 0.0 if a <= 0.0 or b <= 0.0 else float(2 * a * b / (a + b))


def _run_policy(reference: dict, feature_ids: list[str], events: list[dict], policy: TransitionPolicy, cfg: Exp0006Config) -> dict:
    state = TransitionState(symbol="qevra", active_package=copy.deepcopy(reference), generation=2)
    truth = copy.deepcopy(reference)
    rows: list[dict] = []
    genuine_total = 0
    genuine_accepted = 0
    attack_total = 0
    attack_accepted = 0
    genuine_lags: list[int] = []

    for event in events:
        if event["new_truth"] is not None:
            truth = copy.deepcopy(event["new_truth"])
        candidate = event["candidate"]
        request = build_transition_request(
            state,
            candidate,
            source_agent="board-transition-proposal",
            event_type="imprint.transition",
            provenance={"event_id": event["event_id"], "truth_blind": True},
        )
        evidence = _evidence(candidate, feature_ids, list(event["roots"]), prefix=event["event_id"], noise=cfg.evidence_noise)
        out = process_transition(state, request, evidence, policy, feature_ids)
        state = out.state

        if event["truth_effect"] == "genuine":
            genuine_total += 1
            if out.accepted:
                genuine_accepted += 1
                genuine_lags.append(out.evidence_consumed)
        else:
            attack_total += 1
            if out.accepted:
                attack_accepted += 1

        rows.append({
            "event_id": event["event_id"],
            "truth_effect": event["truth_effect"],
            "accepted": out.accepted,
            "reason": out.reason,
            "evidence_consumed": out.evidence_consumed,
            "independent_origins": out.independent_origins,
            "independent_agents": out.independent_agents,
            "candidate_median_js": out.candidate_median_js,
            "structurally_valid": True,
            "active_package_sha256": state.active_package["sha256"],
            "truth_package_sha256": truth["sha256"],
            "target_js": _target_js(state.active_package, truth, feature_ids),
            "generation": state.generation,
        })

    plasticity = genuine_accepted / genuine_total
    pollution_acceptance = attack_accepted / attack_total
    integrity = 1.0 - pollution_acceptance
    return {
        "policy": asdict(policy),
        "events": rows,
        "summary": {
            "plasticity": float(plasticity),
            "integrity": float(integrity),
            "pollution_acceptance_rate": float(pollution_acceptance),
            "false_reject_rate": float(1.0 - plasticity),
            "balanced_harmonic": _harmonic(plasticity, integrity),
            "mean_target_js": float(np.mean([row["target_js"] for row in rows])),
            "cumulative_target_js": float(np.sum([row["target_js"] for row in rows])),
            "max_target_js": float(np.max([row["target_js"] for row in rows])),
            "final_target_js": float(rows[-1]["target_js"]),
            "mean_accepted_genuine_evidence": float(np.mean(genuine_lags)) if genuine_lags else None,
            "genuine_accepted": genuine_accepted,
            "genuine_total": genuine_total,
            "pollution_accepted": attack_accepted,
            "pollution_total": attack_total,
        },
        "final_state": {"generation": state.generation, "active_package": state.active_package, "history": state.history},
    }


def run_exp0006(repo_root: Path, config: Exp0006Config | None = None) -> dict:
    repo_root = Path(repo_root)
    cfg = config or Exp0006Config()
    feature_ids, reference = _load_reference(repo_root)
    events = _build_event_fixtures(reference, feature_ids, cfg)
    arms = {name: _run_policy(reference, feature_ids, events, policy, cfg) for name, policy in POLICIES.items()}

    rigid = arms["Rigid"]["summary"]
    permissive = arms["Permissive"]["summary"]
    q2 = arms["Adaptive-Q2"]["summary"]
    q3 = arms["Adaptive-Q3"]["summary"]
    hypotheses = {
        "H1_rigid_integrity_without_plasticity": rigid["integrity"] == 1.0 and rigid["plasticity"] == 0.0,
        "H2_permissive_plasticity_without_integrity": permissive["plasticity"] == 1.0 and permissive["integrity"] == 0.0,
        "H3_q2_accepts_minority_novelty_but_exposes_two_origin_attack": q2["plasticity"] == 1.0 and q2["integrity"] == 0.5,
        "H4_q3_blocks_two_origin_attack_but_false_rejects_minority_novelty": abs(q3["plasticity"] - 2.0 / 3.0) < 1e-12 and q3["integrity"] == 1.0,
        "H5_static_quorum_tradeoff_exists": q2["plasticity"] > q3["plasticity"] and q2["integrity"] < q3["integrity"],
        "H6_structural_protocol_is_not_semantic_admissibility": permissive["pollution_acceptance_rate"] == 1.0,
        "H7_supported_recovery_outperforms_rigid_staleness": all(arms[name]["summary"]["final_target_js"] < rigid["final_target_js"] for name in ("Permissive", "Adaptive-Q2", "Adaptive-Q3")),
    }

    return {
        "schema": "scl-exp0006/v0.6",
        "experiment_id": "EXP-0006",
        "title": "Admissible Cognitive Transition Law / Plasticity–Integrity Tradeoff",
        "sci_definition": "Symbolic Cognitive Imprint (SCI) / 符號認知印刻",
        "config": asdict(cfg),
        "feature_ids": feature_ids,
        "reference": reference,
        "event_fixtures": [{
            "event_id": row["event_id"],
            "truth_effect": row["truth_effect"],
            "candidate_sha256": row["candidate"]["sha256"],
            "new_truth_sha256": row["new_truth"]["sha256"] if row["new_truth"] is not None else None,
            "origin_roots": list(row["roots"]),
        } for row in events],
        "arms": arms,
        "hypotheses": hypotheses,
        "boundaries": {
            "neural_retraining": False,
            "source_of_sci": "canonical EXP-0004 merged qevra package",
            "structural_protocol_precondition": True,
            "semantic_transition_ground_truth": "synthetic explicit benchmark fixtures",
            "public_ai_board_write": False,
            "live_ctcl_call": False,
        },
    }
