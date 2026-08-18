from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .adaptive_admission import AdaptiveAdmissionConfig, AdaptiveAdmissionPolicy
from .grid import js_divergence
from .sci import build_sci_package, dense_signature


@dataclass(frozen=True)
class Exp0007Config:
    feature_space: str = "SCL-F01-F19-v0.2"
    risk_loss_weight: float = 3.0
    adaptive: AdaptiveAdmissionConfig = AdaptiveAdmissionConfig()


POLICY_NAMES = ("Static-Q2", "Static-Q3", "Learned-Adaptive", "Oracle")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_reference(repo_root: Path) -> tuple[list[str], dict]:
    metrics = _load_json(repo_root / "experiments/EXP-0004/results/metrics.json")
    return list(metrics["feature_ids"]), copy.deepcopy(metrics["packages"]["merged_qevra"])


def _clip(v: float) -> float:
    return float(min(1.0, max(0.0, v)))


def _reweight(package: dict, feature_ids: list[str], adjustments: dict[str, float], *, label: str, source_agent: str) -> dict:
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
        provenance={"exp0007_fixture": label, "from": package.get("sha256")},
    )


def _target_js(package: dict, target: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(package, feature_ids), dense_signature(target, feature_ids))


def _candidate_novelty(active: dict, candidate: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(active, feature_ids), dense_signature(candidate, feature_ids))


def _evidence(roots: list[str], *, event_id: str) -> list[dict]:
    return [
        {
            "source_agent": f"{event_id}-observer-{i + 1}",
            "origin_root": str(root),
        }
        for i, root in enumerate(roots)
    ]


def _build_event_fixtures(reference: dict, feature_ids: list[str]) -> list[dict]:
    truth = copy.deepcopy(reference)
    events: list[dict] = []

    def genuine(event_id: str, phase: str, roots: list[str], risk: float, adjustments: dict[str, float]) -> None:
        nonlocal truth
        candidate = _reweight(truth, feature_ids, adjustments, label=event_id, source_agent="truth-fixture")
        truth = copy.deepcopy(candidate)
        events.append({
            "event_id": event_id,
            "phase": phase,
            "truth_effect": "genuine",
            "risk": float(risk),
            "roots": list(roots),
            "candidate": candidate,
            "new_truth": copy.deepcopy(candidate),
        })

    def pollution(event_id: str, phase: str, roots: list[str], risk: float, adjustments: dict[str, float]) -> None:
        candidate = _reweight(truth, feature_ids, adjustments, label=event_id, source_agent="pollution-fixture")
        events.append({
            "event_id": event_id,
            "phase": phase,
            "truth_effect": "pollution",
            "risk": float(risk),
            "roots": list(roots),
            "candidate": candidate,
            "new_truth": None,
        })

    # Phase 1: calibration. A/B become strong; C is mixed; D and X are weak/unknown.
    genuine("E01_calib_ABC", "calibration", ["A", "B", "C"], 0.20, {"F18": +0.18, "F16": +0.05})
    genuine("E02_calib_AB", "calibration", ["A", "B"], 0.45, {"F05": +0.12, "F03": +0.06})
    pollution("E03_correlated_echo_X", "calibration", ["X", "X", "X"], 0.20, {"F19": +0.34, "F07": -0.12})
    pollution("E04_two_origin_CD_attack", "calibration", ["C", "D"], 0.75, {"F19": +0.42, "F10": -0.16, "F17": -0.12})
    genuine("E05_calib_ABC_high", "calibration", ["A", "B", "C"], 0.65, {"F17": +0.08, "F13": +0.05})

    # Phase 2: provenance drift. B becomes compromised; D/E carry real minority novelty.
    pollution("E06_BC_compromise", "drift", ["B", "C"], 0.60, {"F19": +0.36, "F16": -0.14, "F06": -0.08})
    genuine("E07_AD_minority_novelty", "drift", ["A", "D"], 0.40, {"F04": +0.08, "F14": -0.05})
    genuine("E08_DE_new_sources", "drift", ["D", "E"], 0.20, {"F15": +0.07, "F10": +0.04})
    genuine("E09_ADE_convergence", "drift", ["A", "D", "E"], 0.55, {"F06": +0.06, "F08": +0.04})
    pollution("E10_BD_mixed_attack", "drift", ["B", "D"], 0.50, {"F19": +0.30, "F05": -0.12, "F17": -0.10})
    genuine("E11_DE_reliable_minority", "drift", ["D", "E"], 0.30, {"F12": +0.08, "F02": +0.04})

    # Phase 3: a previously trusted coalition attacks, then newer provenance has to recover.
    pollution("E12_trusted_ABC_attack", "stress", ["A", "B", "C"], 0.85, {"F19": +0.44, "F07": -0.16, "F16": -0.12, "F01": -0.08})
    genuine("E13_DEF_high_risk_update", "stress", ["D", "E", "F"], 0.80, {"F18": +0.06, "F01": +0.05})
    pollution("E14_BC_followup_attack", "stress", ["B", "C"], 0.45, {"F19": +0.32, "F10": -0.12, "F15": -0.08})
    genuine("E15_ADE_recovery", "stress", ["A", "D", "E"], 0.70, {"F11": +0.07, "F16": +0.04})
    return events


def _static_decision(roots: list[str], quorum: int) -> tuple[bool, str, int]:
    distinct = len({str(root) for root in roots})
    accepted = distinct >= quorum
    return accepted, "accepted_static_quorum" if accepted else "insufficient_static_quorum", distinct


def _summary(rows: list[dict], *, cfg: Exp0007Config) -> dict:
    genuine = [row for row in rows if row["truth_effect"] == "genuine"]
    pollution = [row for row in rows if row["truth_effect"] == "pollution"]
    g_accept = sum(bool(row["accepted"]) for row in genuine)
    p_accept = sum(bool(row["accepted"]) for row in pollution)
    plasticity = g_accept / len(genuine)
    false_accept = p_accept / len(pollution)
    integrity = 1.0 - false_accept
    target_losses = [float(row["target_js"]) for row in rows]
    weighted = [float(row["target_js"]) * (1.0 + cfg.risk_loss_weight * float(row["risk"])) for row in rows]
    return {
        "plasticity": float(plasticity),
        "integrity": float(integrity),
        "false_accept_rate": float(false_accept),
        "false_reject_rate": float(1.0 - plasticity),
        "mean_target_js": float(np.mean(target_losses)),
        "cumulative_target_js": float(np.sum(target_losses)),
        "risk_weighted_cumulative_target_js": float(np.sum(weighted)),
        "max_target_js": float(np.max(target_losses)),
        "final_target_js": float(target_losses[-1]),
        "genuine_accepted": int(g_accept),
        "genuine_total": int(len(genuine)),
        "pollution_accepted": int(p_accept),
        "pollution_total": int(len(pollution)),
    }


def _run_arm(reference: dict, feature_ids: list[str], events: list[dict], name: str, cfg: Exp0007Config) -> dict:
    state = copy.deepcopy(reference)
    truth = copy.deepcopy(reference)
    learned = AdaptiveAdmissionPolicy(cfg.adaptive) if name == "Learned-Adaptive" else None
    previous: dict | None = None
    rows: list[dict] = []
    calibration_pairs: list[tuple[float, float]] = []
    b_phase1: float | None = None
    d_initial = learned.trust.mean("D") if learned is not None else None

    for event in events:
        # One-event delayed feedback: event t is decided only after feedback about t-1.
        if learned is not None and previous is not None:
            prior_roots = sorted(set(previous["roots"]))
            truth_label = previous["truth_effect"] == "genuine"
            for root in prior_roots:
                prediction = learned.trust.mean(root)
                calibration_pairs.append((prediction, 1.0 if truth_label else 0.0))
            learned.observe_feedback(prior_roots, genuine=truth_label)

        if event["new_truth"] is not None:
            truth = copy.deepcopy(event["new_truth"])
        evidence = _evidence(event["roots"], event_id=event["event_id"])
        novelty = _candidate_novelty(state, event["candidate"], feature_ids)
        trust_before = learned.trust.snapshot() if learned is not None else {}

        if name == "Oracle":
            accepted = event["truth_effect"] == "genuine"
            reason = "oracle_accept_genuine" if accepted else "oracle_reject_pollution"
            distinct = len(set(event["roots"]))
            required_support = None
            effective_support = None
            recent_pollution = None
        elif name == "Static-Q2":
            accepted, reason, distinct = _static_decision(event["roots"], 2)
            required_support = 2.0
            effective_support = float(distinct)
            recent_pollution = None
        elif name == "Static-Q3":
            accepted, reason, distinct = _static_decision(event["roots"], 3)
            required_support = 3.0
            effective_support = float(distinct)
            recent_pollution = None
        elif name == "Learned-Adaptive":
            assert learned is not None
            decision = learned.decide(evidence, risk=event["risk"], novelty_js=novelty)
            accepted = decision.accepted
            reason = decision.reason
            distinct = decision.distinct_origins
            required_support = decision.required_support
            effective_support = decision.effective_support
            recent_pollution = decision.recent_pollution_rate
        else:
            raise ValueError(f"unknown policy: {name}")

        if accepted:
            state = copy.deepcopy(event["candidate"])

        if learned is not None and event["event_id"] == "E06_BC_compromise":
            # E05 feedback has just been applied, so this is B's phase-1 posterior.
            b_phase1 = learned.trust.mean("B")

        rows.append({
            "event_id": event["event_id"],
            "phase": event["phase"],
            "truth_effect": event["truth_effect"],
            "risk": event["risk"],
            "roots": list(event["roots"]),
            "accepted": bool(accepted),
            "reason": reason,
            "distinct_origins": int(distinct),
            "novelty_js": float(novelty),
            "required_support": float(required_support) if required_support is not None else None,
            "effective_support": float(effective_support) if effective_support is not None else None,
            "recent_pollution_rate": float(recent_pollution) if recent_pollution is not None else None,
            "trust_before": trust_before,
            "candidate_sha256": event["candidate"]["sha256"],
            "truth_sha256": truth["sha256"],
            "active_sha256": state["sha256"],
            "target_js": _target_js(state, truth, feature_ids),
        })
        previous = event

    if learned is not None and previous is not None:
        final_roots = sorted(set(previous["roots"]))
        final_label = previous["truth_effect"] == "genuine"
        for root in final_roots:
            prediction = learned.trust.mean(root)
            calibration_pairs.append((prediction, 1.0 if final_label else 0.0))
        learned.observe_feedback(final_roots, genuine=final_label)

    summary = _summary(rows, cfg=cfg)
    out = {"events": rows, "summary": summary, "final_state": {"active_package": copy.deepcopy(state), "truth_package": copy.deepcopy(truth)}}
    if learned is not None:
        brier = float(np.mean([(p - y) ** 2 for p, y in calibration_pairs])) if calibration_pairs else 0.0
        final_trust = learned.trust.snapshot()
        out["trust_drift"] = {
            "B_phase1": float(b_phase1 if b_phase1 is not None else learned.trust.mean("B")),
            "B_final": float(learned.trust.mean("B")),
            "D_initial": float(d_initial if d_initial is not None else 0.5),
            "D_final": float(learned.trust.mean("D")),
            "A_final": float(learned.trust.mean("A")),
            "E_final": float(learned.trust.mean("E")),
            "F_final": float(learned.trust.mean("F")),
        }
        out["trust_final"] = final_trust
        out["trust_brier"] = brier
    return out


def run_exp0007(repo_root: Path, config: Exp0007Config | None = None) -> dict:
    repo_root = Path(repo_root)
    cfg = config or Exp0007Config()
    feature_ids, reference = _load_reference(repo_root)
    events = _build_event_fixtures(reference, feature_ids)
    arms = {name: _run_arm(reference, feature_ids, events, name, cfg) for name in POLICY_NAMES}

    q2 = arms["Static-Q2"]["summary"]
    q3 = arms["Static-Q3"]["summary"]
    learned = arms["Learned-Adaptive"]
    oracle = arms["Oracle"]["summary"]
    learned_summary = learned["summary"]
    drift = learned["trust_drift"]

    hypotheses = {
        "H1_static_quorum_tradeoff_persists": q2["plasticity"] > q3["plasticity"] and q2["integrity"] < q3["integrity"],
        "H2_learned_beats_both_static_risk_weighted_loss": learned_summary["risk_weighted_cumulative_target_js"] < min(q2["risk_weighted_cumulative_target_js"], q3["risk_weighted_cumulative_target_js"]),
        "H3_learned_tracks_provenance_drift": drift["B_final"] < drift["B_phase1"] and drift["D_final"] > drift["D_initial"],
        "H4_learned_rejects_correlated_alias_echo": not next(row for row in learned["events"] if row["event_id"] == "E03_correlated_echo_X")["accepted"],
        "H5_learned_is_not_oracle": learned_summary["risk_weighted_cumulative_target_js"] > oracle["risk_weighted_cumulative_target_js"],
        "H6_high_reputation_attack_can_still_bypass_learning": next(row for row in learned["events"] if row["event_id"] == "E12_trusted_ABC_attack")["accepted"],
        "H7_dynamic_threshold_varies_over_time": len({round(float(row["required_support"]), 6) for row in learned["events"]}) > 3,
    }

    return {
        "schema": "scl-exp0007/v0.7",
        "experiment_id": "EXP-0007",
        "title": "Adaptive Epistemic Admission / Learning When to Trust",
        "sci_definition": "Symbolic Cognitive Imprint (SCI) / 符號認知印刻",
        "config": {
            "feature_space": cfg.feature_space,
            "risk_loss_weight": cfg.risk_loss_weight,
            "adaptive": asdict(cfg.adaptive),
        },
        "feature_ids": feature_ids,
        "reference_sha256": reference["sha256"],
        "event_fixtures": [
            {
                "event_id": row["event_id"],
                "phase": row["phase"],
                "truth_effect": row["truth_effect"],
                "risk": row["risk"],
                "origin_roots": list(row["roots"]),
                "candidate_sha256": row["candidate"]["sha256"],
                "new_truth_sha256": row["new_truth"]["sha256"] if row["new_truth"] is not None else None,
            }
            for row in events
        ],
        "arms": arms,
        "hypotheses": hypotheses,
        "boundaries": {
            "neural_retraining": False,
            "source_of_sci": "canonical EXP-0004 merged qevra package",
            "structural_protocol_precondition": True,
            "semantic_ground_truth": "synthetic explicit online benchmark",
            "feedback_mode": "one_event_delayed",
            "current_truth_visible_to_policy": False,
            "oracle_is_evaluation_ceiling_only": True,
            "public_ai_board_write": False,
            "live_ctcl_call": False,
        },
    }
