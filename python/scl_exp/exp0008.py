from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .grid import js_divergence
from .sci import build_sci_package, dense_signature
from .trust_dynamics import TrustAdmissionConfig, TrustDynamicsAdmissionPolicy, TrustDynamicsConfig


@dataclass(frozen=True)
class Exp0008Config:
    feature_space: str = "SCL-F01-F19-v0.2"
    risk_loss_weight: float = 3.0
    admission: TrustAdmissionConfig = TrustAdmissionConfig(
        dynamics=TrustDynamicsConfig(fixed_decay=0.90, adaptive_base_decay=0.97, volatility_decay_strength=0.42, min_decay=0.52, max_decay=0.995, surprise_ema=0.58, betrayal_boost=2.8, recovery_boost=2.2),
        min_distinct_origins=2,
        base_required_support=0.85,
        risk_weight=0.50,
        novelty_weight=4.0,
        recent_pollution_weight=0.45,
        recent_window=4,
    )

POLICY_NAMES = ("Cumulative-History", "Fixed-Decay", "Adaptive-Dynamics", "Oracle")
MODE_BY_POLICY = {"Cumulative-History": "cumulative", "Fixed-Decay": "fixed", "Adaptive-Dynamics": "adaptive"}


def _load_reference(repo_root: Path) -> tuple[list[str], dict]:
    metrics = json.loads((repo_root / "experiments/EXP-0004/results/metrics.json").read_text(encoding="utf-8"))
    return list(metrics["feature_ids"]), copy.deepcopy(metrics["packages"]["merged_qevra"])


def _clip(v: float) -> float:
    return float(min(1.0, max(0.0, v)))


def _reweight(package: dict, feature_ids: list[str], adjustments: dict[str, float], *, label: str, source_agent: str) -> dict:
    values = dense_signature(package, feature_ids)
    idx = {fid: i for i, fid in enumerate(feature_ids)}
    for fid, delta in adjustments.items():
        values[idx[fid]] = _clip(float(values[idx[fid]]) + float(delta))
    return build_sci_package(package["symbol"], values, feature_ids, source_agent, top_k=len(feature_ids), expansion=package.get("expansion", []), provenance={"exp0008_fixture": label, "from": package.get("sha256")})


def _target_js(package: dict, target: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(package, feature_ids), dense_signature(target, feature_ids))


def _candidate_novelty(active: dict, candidate: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(active, feature_ids), dense_signature(candidate, feature_ids))


def _evidence(roots: list[str], *, event_id: str) -> list[dict]:
    return [{"source_agent": f"{event_id}-observer-{i + 1}", "origin_root": str(root)} for i, root in enumerate(roots)]


def _build_event_fixtures(reference: dict, feature_ids: list[str]) -> list[dict]:
    truth = copy.deepcopy(reference)
    events: list[dict] = []

    def genuine(event_id: str, phase: str, roots: list[str], risk: float, adjustments: dict[str, float]) -> None:
        nonlocal truth
        candidate = _reweight(truth, feature_ids, adjustments, label=event_id, source_agent="truth-fixture")
        truth = copy.deepcopy(candidate)
        events.append({"event_id": event_id, "phase": phase, "truth_effect": "genuine", "risk": float(risk), "roots": list(roots), "candidate": candidate, "new_truth": copy.deepcopy(candidate)})

    def pollution(event_id: str, phase: str, roots: list[str], risk: float, adjustments: dict[str, float]) -> None:
        candidate = _reweight(truth, feature_ids, adjustments, label=event_id, source_agent="pollution-fixture")
        events.append({"event_id": event_id, "phase": phase, "truth_effect": "pollution", "risk": float(risk), "roots": list(roots), "candidate": candidate, "new_truth": None})

    genuine("E01_calib_ABC", "calibration", ["A", "B", "C"], 0.20, {"F18": +0.14, "F16": +0.04})
    genuine("E02_calib_AB", "calibration", ["A", "B"], 0.35, {"F05": +0.10, "F03": +0.05})
    pollution("E03_echo_X", "calibration", ["X", "X", "X"], 0.20, {"F19": +0.30, "F07": -0.10})
    genuine("E04_calib_ABC", "calibration", ["A", "B", "C"], 0.50, {"F17": +0.07, "F13": +0.04})
    genuine("E05_calib_AB_high", "calibration", ["A", "B"], 0.65, {"F01": +0.05, "F06": +0.04})
    genuine("E06_DE_coldstart", "cold_start", ["D", "E"], 0.35, {"F04": +0.07, "F14": -0.04})
    genuine("E07_ADE_bridge", "cold_start", ["A", "D", "E"], 0.45, {"F15": +0.06, "F10": +0.04})
    genuine("E08_DE_followup", "cold_start", ["D", "E"], 0.25, {"F12": +0.07, "F02": +0.04})
    pollution("E09_BC_betrayal_1", "betrayal", ["B", "C"], 0.80, {"F19": +0.40, "F16": -0.13, "F06": -0.08})
    pollution("E10_BC_betrayal_2", "betrayal", ["B", "C"], 0.70, {"F19": +0.36, "F10": -0.12, "F17": -0.09})
    pollution("E11_BX_betrayal_3", "betrayal", ["B", "X"], 0.55, {"F19": +0.32, "F05": -0.10})
    genuine("E12_BD_rehab_1", "recovery", ["B", "D"], 0.35, {"F11": +0.06, "F03": +0.03})
    genuine("E13_BE_rehab_2", "recovery", ["B", "E"], 0.30, {"F08": +0.05, "F18": +0.03})
    genuine("E14_ABD_rehab_3", "recovery", ["A", "B", "D"], 0.50, {"F07": +0.05, "F13": +0.03})
    pollution("E15_AC_drift_attack_1", "concept_drift", ["A", "C"], 0.85, {"F19": +0.42, "F01": -0.10, "F18": -0.08})
    pollution("E16_AX_drift_attack_2", "concept_drift", ["A", "X"], 0.60, {"F19": +0.34, "F12": -0.10})
    genuine("E17_FG_new_sources", "concept_drift", ["F", "G"], 0.30, {"F09": +0.07, "F14": +0.04})
    genuine("E18_DFG_convergence", "concept_drift", ["D", "F", "G"], 0.55, {"F06": +0.05, "F16": +0.04})
    genuine("E19_FG_followup", "concept_drift", ["F", "G"], 0.25, {"F02": +0.05, "F15": +0.04})
    genuine("E20_BDE_final_recovery", "concept_drift", ["B", "D", "E"], 0.70, {"F10": +0.05, "F17": +0.04})
    return events


def _summary(rows: list[dict], *, cfg: Exp0008Config) -> dict:
    genuine = [r for r in rows if r["truth_effect"] == "genuine"]
    pollution = [r for r in rows if r["truth_effect"] == "pollution"]
    g_accept = sum(bool(r["accepted"]) for r in genuine)
    p_accept = sum(bool(r["accepted"]) for r in pollution)
    target_losses = [float(r["target_js"]) for r in rows]
    weighted = [float(r["target_js"]) * (1.0 + cfg.risk_loss_weight * float(r["risk"])) for r in rows]

    def phase_count(phase: str, truth_effect: str, accepted: bool) -> int:
        return sum(1 for r in rows if r["phase"] == phase and r["truth_effect"] == truth_effect and bool(r["accepted"]) == accepted)

    def first_accept_lag(phase: str, truth_effect: str) -> int | None:
        matches = [r for r in rows if r["phase"] == phase and r["truth_effect"] == truth_effect]
        for i, row in enumerate(matches):
            if row["accepted"]:
                return i
        return None

    plasticity = g_accept / len(genuine)
    false_accept = p_accept / len(pollution)
    return {
        "plasticity": float(plasticity), "integrity": float(1.0 - false_accept), "false_accept_rate": float(false_accept), "false_reject_rate": float(1.0 - plasticity),
        "mean_target_js": float(np.mean(target_losses)), "cumulative_target_js": float(np.sum(target_losses)), "risk_weighted_cumulative_target_js": float(np.sum(weighted)), "max_target_js": float(np.max(target_losses)), "final_target_js": float(target_losses[-1]),
        "genuine_accepted": int(g_accept), "genuine_total": int(len(genuine)), "pollution_accepted": int(p_accept), "pollution_total": int(len(pollution)),
        "cold_start_false_rejects": int(phase_count("cold_start", "genuine", False)), "betrayal_pollution_accepts": int(phase_count("betrayal", "pollution", True)), "recovery_false_rejects": int(phase_count("recovery", "genuine", False)),
        "concept_drift_pollution_accepts": int(phase_count("concept_drift", "pollution", True)), "concept_drift_genuine_rejects": int(phase_count("concept_drift", "genuine", False)),
        "cold_start_accept_lag": first_accept_lag("cold_start", "genuine"), "recovery_accept_lag": first_accept_lag("recovery", "genuine"),
    }


def _run_arm(reference: dict, feature_ids: list[str], events: list[dict], name: str, cfg: Exp0008Config) -> dict:
    state = copy.deepcopy(reference)
    truth = copy.deepcopy(reference)
    policy = None if name == "Oracle" else TrustDynamicsAdmissionPolicy(MODE_BY_POLICY[name], cfg.admission)
    previous: dict | None = None
    rows: list[dict] = []
    trust_trajectory: list[dict] = []
    calibration_pairs: list[tuple[float, float]] = []

    for event in events:
        if policy is not None:
            policy.start_event()
            if previous is not None:
                prior_roots = sorted(set(previous["roots"]))
                truth_label = previous["truth_effect"] == "genuine"
                for root in prior_roots:
                    calibration_pairs.append((policy.trust.mean(root), 1.0 if truth_label else 0.0))
                policy.observe_delayed_feedback(prior_roots, genuine=truth_label)

        if event["new_truth"] is not None:
            truth = copy.deepcopy(event["new_truth"])
        novelty = _candidate_novelty(state, event["candidate"], feature_ids)
        evidence = _evidence(event["roots"], event_id=event["event_id"])

        if name == "Oracle":
            accepted = event["truth_effect"] == "genuine"
            reason = "oracle_accept_genuine" if accepted else "oracle_reject_pollution"
            required = support = recent_pollution = None
        else:
            assert policy is not None
            trust_before = policy.trust.snapshot()
            decision = policy.decide(evidence, risk=event["risk"], novelty_js=novelty)
            accepted, reason = decision.accepted, decision.reason
            required, support, recent_pollution = float(decision.required_support), float(decision.effective_support), float(decision.recent_pollution_rate)
            trust_trajectory.append({"event_id": event["event_id"], "phase": event["phase"], "trust": trust_before, "required_support": required, "effective_support": support, "recent_pollution_rate": recent_pollution})

        if accepted:
            state = copy.deepcopy(event["candidate"])
        rows.append({"event_id": event["event_id"], "phase": event["phase"], "truth_effect": event["truth_effect"], "risk": event["risk"], "roots": list(event["roots"]), "accepted": bool(accepted), "reason": reason, "novelty_js": float(novelty), "required_support": required, "effective_support": support, "recent_pollution_rate": recent_pollution, "candidate_sha256": event["candidate"]["sha256"], "truth_sha256": truth["sha256"], "active_sha256": state["sha256"], "target_js": _target_js(state, truth, feature_ids)})
        previous = event

    if policy is not None and previous is not None:
        policy.start_event()
        final_roots = sorted(set(previous["roots"]))
        final_label = previous["truth_effect"] == "genuine"
        for root in final_roots:
            calibration_pairs.append((policy.trust.mean(root), 1.0 if final_label else 0.0))
        policy.observe_delayed_feedback(final_roots, genuine=final_label)
        final_trust = policy.trust.snapshot()
        brier = float(np.mean([(p - y) ** 2 for p, y in calibration_pairs])) if calibration_pairs else 0.0
    else:
        final_trust, brier = {}, 0.0

    return {"events": rows, "summary": _summary(rows, cfg=cfg), "trust_trajectory": trust_trajectory, "final_trust": final_trust, "trust_brier": brier, "final_state": {"active_package": copy.deepcopy(state), "truth_package": copy.deepcopy(truth)}}


def run_exp0008(repo_root: Path, config: Exp0008Config | None = None) -> dict:
    repo_root = Path(repo_root)
    cfg = config or Exp0008Config()
    feature_ids, reference = _load_reference(repo_root)
    events = _build_event_fixtures(reference, feature_ids)
    arms = {name: _run_arm(reference, feature_ids, events, name, cfg) for name in POLICY_NAMES}
    cumulative = arms["Cumulative-History"]["summary"]
    fixed = arms["Fixed-Decay"]["summary"]
    adaptive = arms["Adaptive-Dynamics"]
    adaptive_summary = adaptive["summary"]
    oracle = arms["Oracle"]["summary"]
    final_trust = adaptive["final_trust"]

    hypotheses = {
        "H1_no_forgetting_exhibits_reputation_hysteresis": cumulative["betrayal_pollution_accepts"] > 0,
        "H2_fixed_decay_reduces_hysteresis_vs_cumulative": fixed["betrayal_pollution_accepts"] <= cumulative["betrayal_pollution_accepts"],
        "H3_adaptive_dynamics_tracks_betrayal_and_recovery": final_trust.get("B", {}).get("mean", 0.5) > 0.45 and any(row["trust"].get("B", {}).get("volatility", 0.0) > 0.15 for row in adaptive["trust_trajectory"]),
        "H4_adaptive_risk_loss_beats_cumulative": adaptive_summary["risk_weighted_cumulative_target_js"] < cumulative["risk_weighted_cumulative_target_js"],
        "H5_adaptive_is_not_oracle": adaptive_summary["risk_weighted_cumulative_target_js"] > oracle["risk_weighted_cumulative_target_js"],
        "H6_cold_start_and_betrayal_cannot_both_be_zero_cost": adaptive_summary["cold_start_false_rejects"] + adaptive_summary["betrayal_pollution_accepts"] > 0,
        "H7_trust_learning_rate_is_state_dependent": len({round(row["trust"].get("B", {}).get("volatility", 0.0), 6) for row in adaptive["trust_trajectory"] if "B" in row["trust"]}) > 3,
    }
    exploratory_observations = {
        "E1_better_trust_calibration_without_better_admission": adaptive["trust_brier"] < min(arms["Cumulative-History"]["trust_brier"], arms["Fixed-Decay"]["trust_brier"]) and [row["accepted"] for row in adaptive["events"]] == [row["accepted"] for row in arms["Cumulative-History"]["events"]],
        "E2_fixed_decay_dominates_this_fixture": fixed["risk_weighted_cumulative_target_js"] < min(cumulative["risk_weighted_cumulative_target_js"], adaptive_summary["risk_weighted_cumulative_target_js"]),
    }
    return {
        "schema": "scl-exp0008/v0.8", "experiment_id": "EXP-0008", "title": "Adaptive Trust Dynamics / Reputation Decay–Recovery", "sci_definition": "Symbolic Cognitive Imprint (SCI) / 符號認知印刻",
        "config": {"feature_space": cfg.feature_space, "risk_loss_weight": cfg.risk_loss_weight, "admission": asdict(cfg.admission)}, "feature_ids": feature_ids, "reference_sha256": reference["sha256"],
        "event_fixtures": [{"event_id": row["event_id"], "phase": row["phase"], "truth_effect": row["truth_effect"], "risk": row["risk"], "origin_roots": list(row["roots"]), "candidate_sha256": row["candidate"]["sha256"], "new_truth_sha256": row["new_truth"]["sha256"] if row["new_truth"] is not None else None} for row in events],
        "arms": arms, "hypotheses": hypotheses, "exploratory_observations": exploratory_observations,
        "boundaries": {"neural_retraining": False, "source_of_sci": "canonical EXP-0004 merged qevra package", "structural_protocol_precondition": True, "semantic_ground_truth": "synthetic explicit online benchmark", "feedback_mode": "one_event_delayed", "current_truth_visible_to_policy": False, "oracle_is_evaluation_ceiling_only": True, "shared_admission_threshold_formula": True, "only_trust_memory_dynamics_differs_between_non_oracle_arms": True, "public_ai_board_write": False, "live_ctcl_call": False},
    }
