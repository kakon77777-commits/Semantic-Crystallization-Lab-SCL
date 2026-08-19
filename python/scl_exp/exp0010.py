from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from .epistemic_decision import BeliefStateDecisionPolicy, DecisionConfig, EvidenceReport
from .grid import js_divergence
from .reflexive_artifact import compile_reflexive_rule_pack
from .reflexive_challenge import ReflexiveChallengePolicy, SecondOrderReflexivePolicy
from .sci import build_sci_package, dense_signature
from .trust_dynamics import TrustDynamicsConfig, TrustDynamicsLedger


@dataclass(frozen=True)
class Exp0010Config:
    feature_space: str = "SCL-F01-F19-v0.2"
    risk_loss_weight: float = 3.0
    decision: DecisionConfig = DecisionConfig(
        base_accept_probability=0.64,
        risk_accept_weight=0.12,
        novelty_accept_weight=2.0,
        uncertainty_band_weight=0.14,
        max_seek=2,
        evidence_cost=0.0008,
        defer_cost=0.0012,
        seek_value_scale=0.22,
        seek_disagreement_weight=0.16,
        min_seek_signal=0.045,
    )
    trust: TrustDynamicsConfig = TrustDynamicsConfig(
        fixed_decay=0.90,
        adaptive_base_decay=0.97,
        volatility_decay_strength=0.42,
        min_decay=0.52,
        max_decay=0.995,
        surprise_ema=0.58,
        betrayal_boost=2.8,
        recovery_boost=2.2,
    )


POLICY_NAMES = ("A0-Reactive", "A1-Artifact-Reflexive", "A2-Second-Order", "Oracle")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_reference(repo_root: Path) -> tuple[list[str], dict]:
    metrics = _load_json(repo_root / "experiments/EXP-0004/results/metrics.json")
    return list(metrics["feature_ids"]), copy.deepcopy(metrics["packages"]["merged_qevra"])


def _clip(value: float) -> float:
    return float(min(1.0, max(0.0, value)))


def _reweight(package: dict, feature_ids: list[str], adjustments: dict[str, float], *, label: str) -> dict:
    values = dense_signature(package, feature_ids)
    idx = {fid: i for i, fid in enumerate(feature_ids)}
    for fid, delta in adjustments.items():
        values[idx[fid]] = _clip(float(values[idx[fid]]) + float(delta))
    return build_sci_package(
        package["symbol"],
        values,
        feature_ids,
        "exp0010-reflexive-fixture",
        top_k=len(feature_ids),
        expansion=package.get("expansion", []),
        provenance={"exp0010_fixture": label, "from": package.get("sha256")},
    )


def _reports(*items: tuple[str, str, int]) -> list[dict]:
    return [{"source_agent": str(a), "origin_root": str(r), "stance": int(s)} for a, r, s in items]


def _target_js(package: dict, target: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(package, feature_ids), dense_signature(target, feature_ids))


def _candidate_novelty(active: dict, candidate: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(active, feature_ids), dense_signature(candidate, feature_ids))


def _all_reports(event: dict) -> list[dict]:
    return list(event["initial_reports"]) + list(event["reserve_reports"])


def _feedback_roots(event: dict) -> tuple[list[str], list[str]]:
    correct: set[str] = set()
    incorrect: set[str] = set()
    genuine = event["truth_effect"] == "genuine"
    for row in _all_reports(event):
        supports = int(row["stance"]) > 0
        is_correct = supports if genuine else not supports
        (correct if is_correct else incorrect).add(str(row["origin_root"]))
    overlap = correct & incorrect
    if overlap:
        raise ValueError(f"conflicting audit labels: {sorted(overlap)}")
    return sorted(correct), sorted(incorrect)


def _prior_hash_tokens(repo_root: Path) -> set[str]:
    token_re = re.compile(r"\b[0-9a-f]{64}\b")
    out: set[str] = set()
    for index in range(1, 10):
        root = repo_root / f"experiments/EXP-{index:04d}"
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".md", ".txt"}:
                continue
            try:
                out.update(token_re.findall(path.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                continue
    return out


def _prior_text(repo_root: Path) -> str:
    chunks: list[str] = []
    for index in range(1, 10):
        root = repo_root / f"experiments/EXP-{index:04d}"
        for path in root.rglob("*.md") if root.exists() else []:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
        for path in root.rglob("*.jsonl") if root.exists() else []:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def _calibration_events(reference: dict, feature_ids: list[str]) -> list[dict]:
    truth = copy.deepcopy(reference)
    events: list[dict] = []

    def add(event_id: str, genuine: bool, reports: list[dict], adjustments: dict[str, float]) -> None:
        nonlocal truth
        candidate = _reweight(truth, feature_ids, adjustments, label=event_id)
        if genuine:
            truth = copy.deepcopy(candidate)
        events.append({
            "event_id": event_id,
            "truth_effect": "genuine" if genuine else "pollution",
            "initial_reports": reports,
            "reserve_reports": [],
            "candidate": candidate,
        })

    add("R10C01_PQR_good", True, _reports(("cp", "P", 1), ("cq", "Q", 1), ("cr", "R", 1)), {"F18": +0.035})
    add("R10C02_PQR_good", True, _reports(("cp2", "P", 1), ("cq2", "Q", 1), ("cr2", "R", 1)), {"F05": +0.030})
    add("R10C03_STU_good", True, _reports(("cs", "S", 1), ("ct", "T", 1), ("cu", "U", 1)), {"F12": +0.035})
    add("R10C04_STU_good", True, _reports(("cs2", "S", 1), ("ct2", "T", 1), ("cu2", "U", 1)), {"F15": +0.030})
    add("R10C05_X_bad", False, _reports(("cx", "X", 1), ("cp3", "P", -1)), {"F19": +0.18})
    add("R10C06_PST_good", True, _reports(("cp4", "P", 1), ("cs3", "S", 1), ("ct3", "T", 1)), {"F17": +0.025})
    return events


def build_exp0010_events(repo_root: Path) -> tuple[list[str], dict, list[dict], dict]:
    repo_root = Path(repo_root)
    feature_ids, reference = _load_reference(repo_root)
    truth = copy.deepcopy(reference)
    events: list[dict] = []

    def add(
        event_id: str,
        phase: str,
        truth_effect: str,
        risk: float,
        initial: list[dict],
        reserve: list[dict],
        adjustments: dict[str, float],
        *,
        meta_attack: str | None = None,
    ) -> None:
        nonlocal truth
        before = copy.deepcopy(truth)
        candidate = _reweight(truth, feature_ids, adjustments, label=event_id)
        if truth_effect == "genuine":
            truth = copy.deepcopy(candidate)
        events.append({
            "event_id": event_id,
            "phase": phase,
            "truth_effect": truth_effect,
            "risk": float(risk),
            "initial_reports": initial,
            "reserve_reports": reserve,
            "candidate": candidate,
            "truth_before": before,
            "truth_after": copy.deepcopy(truth),
            "meta_attack": meta_attack,
        })

    # Phase I: novel homologues of prior failure classes; no event/candidate is copied.
    add("R10N01_trusted_consensus_pollution", "novel_transfer", "pollution", 0.92,
        _reports(("n1p", "P", 1), ("n1q", "Q", 1), ("n1r", "R", 1)),
        _reports(("n1s", "S", -1), ("n1t", "T", -1)), {"F19": +0.40, "F16": -0.08})
    add("R10N02_trusted_consensus_genuine", "novel_transfer", "genuine", 0.80,
        _reports(("n2p", "P", 1), ("n2q", "Q", 1), ("n2r", "R", 1)),
        _reports(("n2s", "S", -1)), {"F06": +0.05, "F17": +0.03})
    add("R10N03_minority_novelty", "novel_transfer", "genuine", 0.55,
        _reports(("n3s", "S", 1), ("n3t", "T", 1), ("n3p", "P", -1)),
        _reports(("n3u", "U", 1)), {"F04": +0.05, "F14": +0.03})
    add("R10N04_correlated_echo", "novel_transfer", "pollution", 0.48,
        _reports(("n4x1", "X", 1), ("n4x2", "X", 1), ("n4x3", "X", 1)),
        _reports(("n4p", "P", -1)), {"F19": +0.25, "F07": -0.06})
    add("R10N05_structured_split", "novel_transfer", "genuine", 0.65,
        _reports(("n5p", "P", 1), ("n5q", "Q", -1)),
        _reports(("n5s", "S", 1), ("n5t", "T", 1)), {"F08": +0.05, "F18": +0.025})
    add("R10N06_reputation_rebound_attack", "novel_transfer", "pollution", 0.82,
        _reports(("n6p", "P", 1), ("n6q", "Q", 1), ("n6r", "R", 1)),
        _reports(("n6s", "S", -1), ("n6u", "U", -1)), {"F19": +0.34, "F10": -0.08})
    add("R10N07_STU_bridge", "novel_transfer", "genuine", 0.25,
        _reports(("n7s", "S", 1), ("n7t", "T", 1), ("n7u", "U", 1)),
        _reports(("n7p", "P", -1)), {"F02": +0.04, "F15": +0.025})

    # Phase II: attacks are conditioned on the published A1 challenge rule.
    add("R10M01_boundary_skimming_attack", "meta_adversarial", "pollution", 0.46,
        _reports(("m1s", "S", 1), ("m1t", "T", 1), ("m1u", "U", 1)),
        _reports(("m1p", "P", -1), ("m1q", "Q", -1)), {"F19": +0.060}, meta_attack="boundary_skimming")
    add("R10M02_boundary_skimming_genuine", "meta_adversarial", "genuine", 0.44,
        _reports(("m2s", "S", 1), ("m2t", "T", 1), ("m2u", "U", 1)),
        _reports(("m2p", "P", -1)), {"F11": +0.030}, meta_attack="challenge_bait")
    add("R10M03_slow_roll_attack", "meta_adversarial", "pollution", 0.42,
        _reports(("m3s", "S", 1), ("m3t", "T", 1), ("m3u", "U", 1)),
        _reports(("m3p", "P", -1), ("m3r", "R", -1)), {"F19": +0.085}, meta_attack="slow_roll")
    add("R10M04_false_disagreement_attack", "meta_adversarial", "pollution", 0.58,
        _reports(("m4s", "S", 1), ("m4t", "T", 1), ("m4u", "U", -1)),
        _reports(("m4p", "P", -1), ("m4q", "Q", -1)), {"F19": +0.18, "F03": -0.04}, meta_attack="false_disagreement")
    add("R10M05_rule_bait_genuine", "meta_adversarial", "genuine", 0.62,
        _reports(("m5s", "S", 1), ("m5t", "T", 1), ("m5u", "U", 1)),
        _reports(("m5p", "P", -1)), {"F09": +0.035, "F13": +0.025}, meta_attack="challenge_bait")
    add("R10M06_low_signal_slow_roll", "meta_adversarial", "pollution", 0.36,
        _reports(("m6s", "S", 1), ("m6t", "T", 1), ("m6u", "U", 1)),
        _reports(("m6p", "P", -1), ("m6q", "Q", -1)), {"F19": +0.11}, meta_attack="slow_roll")
    add("R10M07_final_recovery", "meta_adversarial", "genuine", 0.70,
        _reports(("m7p", "P", 1), ("m7s", "S", 1), ("m7u", "U", 1)),
        _reports(("m7q", "Q", 1)), {"F10": +0.04, "F17": +0.03})

    prior_hashes = _prior_hash_tokens(repo_root)
    candidate_hashes = [event["candidate"]["sha256"] for event in events]
    overlap = sorted(set(candidate_hashes) & prior_hashes)
    prior_text = _prior_text(repo_root)
    guard = {
        "candidate_hash_overlap_count": len(overlap),
        "candidate_hash_overlaps": overlap,
        "all_event_ids_new": all(event["event_id"] not in prior_text for event in events),
        "prior_hash_token_count": len(prior_hashes),
    }
    return feature_ids, reference, events, guard


def _apply_feedback(ledger: TrustDynamicsLedger, event: dict) -> None:
    good, bad = _feedback_roots(event)
    if good:
        ledger.observe(good, genuine=True)
    if bad:
        ledger.observe(bad, genuine=False)


def _shared_trust_snapshots(reference: dict, feature_ids: list[str], events: list[dict], cfg: Exp0010Config) -> list[dict]:
    ledger = TrustDynamicsLedger("adaptive", cfg.trust)
    previous = None
    for event in _calibration_events(reference, feature_ids):
        ledger.advance()
        if previous is not None:
            _apply_feedback(ledger, previous)
        previous = event
    ledger.advance()
    if previous is not None:
        _apply_feedback(ledger, previous)

    snapshots: list[dict] = []
    previous_eval = None
    for event in events:
        if previous_eval is not None:
            ledger.advance()
            _apply_feedback(ledger, previous_eval)
        snapshots.append(ledger.snapshot())
        previous_eval = event
    return snapshots


def _snapshot_hash(snapshot: dict) -> str:
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _positive_coalition(event: dict) -> str:
    roots = sorted({str(row["origin_root"]) for row in event["initial_reports"] if int(row["stance"]) > 0})
    return "|".join(roots)


def _observable_meta_context(events: list[dict], feature_ids: list[str], reference: dict) -> list[dict]:
    anchor = copy.deepcopy(reference)
    previous: dict | None = None
    last_signature = ""
    streak = 0
    contexts: list[dict] = []
    for event in events:
        if previous is not None and previous["truth_effect"] == "genuine":
            anchor = copy.deepcopy(previous["candidate"])
        signature = _positive_coalition(event)
        streak = streak + 1 if signature and signature == last_signature else 1
        last_signature = signature
        contexts.append({
            "coalition_signature": signature,
            "coalition_streak": streak,
            "cumulative_drift_js": _candidate_novelty(anchor, event["candidate"], feature_ids),
        })
        previous = event
    return contexts


def _simulate_policy(
    name: str,
    reference: dict,
    feature_ids: list[str],
    events: list[dict],
    snapshots: list[dict],
    meta_contexts: list[dict],
    cfg: Exp0010Config,
    artifact_pack,
) -> dict:
    state = copy.deepcopy(reference)
    pending: dict | None = None
    rows: list[dict] = []
    action_counts: Counter[str] = Counter()
    prospective_challenges = 0
    second_order_challenges = 0
    if name == "A0-Reactive":
        policy = BeliefStateDecisionPolicy(cfg.decision)
    elif name == "A1-Artifact-Reflexive":
        policy = ReflexiveChallengePolicy(artifact_pack)
        policy.base.config = cfg.decision  # keep the same downstream action costs/limits
    elif name == "A2-Second-Order":
        policy = SecondOrderReflexivePolicy(artifact_pack)
        policy.a1.base.config = cfg.decision
    else:
        policy = None

    for event, trust_snapshot, meta_ctx in zip(events, snapshots, meta_contexts):
        pending_resolution = None
        if pending is not None:
            if pending["truth_effect"] == "genuine":
                state = copy.deepcopy(pending["candidate"])
                pending_resolution = "accepted_after_delayed_validation"
            else:
                pending_resolution = "discarded_after_delayed_validation"
            pending = None

        evidence = [EvidenceReport(**row) for row in event["initial_reports"]]
        reserve = [EvidenceReport(**row) for row in event["reserve_reports"]]
        novelty = _candidate_novelty(state, event["candidate"], feature_ids)
        seek_count = 0
        trace: list[str] = []
        challenge_scores: list[float] = []
        candidate_probability = 0.0
        uncertainty = 0.0
        disagreement = 0.0
        reason = ""
        event_prospective = False
        event_second_order = False

        if name == "Oracle":
            final_action = "accept" if event["truth_effect"] == "genuine" else "reject"
            trace = [final_action]
            action_counts[final_action] += 1
            candidate_probability = 1.0 if final_action == "accept" else 0.0
            reflexive_order = 99
        else:
            while True:
                available = seek_count < len(reserve)
                if name == "A0-Reactive":
                    decision = policy.decide(
                        evidence, trust_snapshot, risk=event["risk"], novelty_js=novelty,
                        evidence_available=available, seek_count=seek_count,
                    )
                    action = decision.action
                    reason = decision.reason
                    candidate_probability = decision.candidate_probability
                    uncertainty = decision.uncertainty
                    disagreement = decision.disagreement
                    reflexive_order = 0
                elif name == "A1-Artifact-Reflexive":
                    decision = policy.decide(
                        evidence, trust_snapshot, risk=event["risk"], novelty_js=novelty,
                        evidence_available=available, seek_count=seek_count,
                    )
                    action = decision.action
                    reason = decision.reason
                    candidate_probability = decision.candidate_probability
                    uncertainty = decision.uncertainty
                    disagreement = decision.disagreement
                    challenge_scores.append(decision.challenge_score)
                    event_prospective = event_prospective or decision.prospective_challenge
                    reflexive_order = 1
                else:
                    decision = policy.decide(
                        evidence, trust_snapshot, risk=event["risk"], novelty_js=novelty,
                        evidence_available=available, seek_count=seek_count,
                        coalition_signature=meta_ctx["coalition_signature"],
                        coalition_streak=meta_ctx["coalition_streak"],
                        cumulative_drift_js=meta_ctx["cumulative_drift_js"],
                    )
                    action = decision.action
                    reason = decision.reason
                    candidate_probability = decision.candidate_probability
                    uncertainty = decision.uncertainty
                    disagreement = decision.disagreement
                    challenge_scores.append(decision.challenge_score)
                    event_prospective = event_prospective or decision.prospective_challenge
                    event_second_order = event_second_order or decision.second_order_challenge
                    reflexive_order = 2
                trace.append(action)
                action_counts[action] += 1
                if action != "seek_evidence":
                    final_action = action
                    break
                evidence.append(reserve[seek_count])
                seek_count += 1

        prospective_challenges += int(event_prospective)
        second_order_challenges += int(event_second_order)
        if final_action == "accept":
            state = copy.deepcopy(event["candidate"])
        elif final_action == "defer":
            pending = {"candidate": copy.deepcopy(event["candidate"]), "truth_effect": event["truth_effect"], "event_id": event["event_id"]}

        target_js = _target_js(state, event["truth_after"], feature_ids)
        target_loss = target_js * (1.0 + cfg.risk_loss_weight * event["risk"])
        evidence_cost = seek_count * cfg.decision.evidence_cost if name != "Oracle" else 0.0
        defer_cost = cfg.decision.defer_cost * (1.0 + event["risk"]) if final_action == "defer" and name != "Oracle" else 0.0
        total_loss = target_loss + evidence_cost + defer_cost
        wrong = (event["truth_effect"] == "genuine" and final_action == "reject") or (event["truth_effect"] == "pollution" and final_action == "accept")
        rows.append({
            "event_id": event["event_id"],
            "phase": event["phase"],
            "truth_effect": event["truth_effect"],
            "meta_attack": event.get("meta_attack"),
            "risk": event["risk"],
            "action_trace": trace,
            "final_action": final_action,
            "reason": reason,
            "candidate_probability": float(candidate_probability),
            "uncertainty": float(uncertainty),
            "disagreement": float(disagreement),
            "novelty_js": float(novelty),
            "target_js": float(target_js),
            "risk_weighted_target_loss": float(target_loss),
            "evidence_cost": float(evidence_cost),
            "defer_cost": float(defer_cost),
            "total_loss": float(total_loss),
            "evidence_queries": seek_count,
            "wrong_immediate": bool(wrong),
            "prospective_challenge": bool(event_prospective),
            "second_order_challenge": bool(event_second_order),
            "challenge_score": max(challenge_scores) if challenge_scores else None,
            "coalition_signature": meta_ctx["coalition_signature"],
            "coalition_streak": meta_ctx["coalition_streak"],
            "cumulative_drift_js": meta_ctx["cumulative_drift_js"],
            "trust_snapshot_sha256": _snapshot_hash(trust_snapshot),
            "pending_resolution_before_event": pending_resolution,
        })

    phases = ("novel_transfer", "meta_adversarial")
    phase_loss = {phase: float(sum(row["total_loss"] for row in rows if row["phase"] == phase)) for phase in phases}
    pollution = [row for row in rows if row["truth_effect"] == "pollution"]
    genuine = [row for row in rows if row["truth_effect"] == "genuine"]
    summary = {
        "events": len(rows),
        "total_loss": float(sum(row["total_loss"] for row in rows)),
        "phase_loss": phase_loss,
        "risk_weighted_target_loss": float(sum(row["risk_weighted_target_loss"] for row in rows)),
        "evidence_cost": float(sum(row["evidence_cost"] for row in rows)),
        "defer_cost": float(sum(row["defer_cost"] for row in rows)),
        "false_accepts": int(sum(row["final_action"] == "accept" for row in pollution)),
        "false_rejects": int(sum(row["final_action"] == "reject" for row in genuine)),
        "evidence_queries": int(sum(row["evidence_queries"] for row in rows)),
        "prospective_challenges": int(prospective_challenges),
        "second_order_challenges": int(second_order_challenges),
        "action_counts": dict(sorted(action_counts.items())),
    }
    return {"reflexive_order": reflexive_order, "summary": summary, "events": rows}


def run_exp0010(repo_root: Path, config: Exp0010Config | None = None) -> dict:
    repo_root = Path(repo_root)
    cfg = config or Exp0010Config()
    artifact_pack = compile_reflexive_rule_pack(repo_root)
    feature_ids, reference, events, guard = build_exp0010_events(repo_root)
    snapshots = _shared_trust_snapshots(reference, feature_ids, events, cfg)
    meta_contexts = _observable_meta_context(events, feature_ids, reference)
    policies = {
        name: _simulate_policy(name, reference, feature_ids, events, snapshots, meta_contexts, cfg, artifact_pack)
        for name in POLICY_NAMES
    }

    a0 = {row["event_id"]: row for row in policies["A0-Reactive"]["events"]}
    a1 = {row["event_id"]: row for row in policies["A1-Artifact-Reflexive"]["events"]}
    a2 = {row["event_id"]: row for row in policies["A2-Second-Order"]["events"]}
    caught = [
        event["event_id"] for event in events
        if event["phase"] == "novel_transfer"
        and event["truth_effect"] == "pollution"
        and a0[event["event_id"]]["final_action"] == "accept"
        and a0[event["event_id"]]["candidate_probability"] >= 0.75
        and a1[event["event_id"]]["final_action"] != "accept"
    ]
    a1_meta_exploits = [
        event["event_id"] for event in events
        if event["phase"] == "meta_adversarial"
        and event.get("meta_attack")
        and event["truth_effect"] == "pollution"
        and a1[event["event_id"]]["final_action"] == "accept"
    ]
    a2_meta_catches = [eid for eid in a1_meta_exploits if a2[eid]["final_action"] != "accept"]

    hypotheses = {
        "H1_artifact_pack_compiles_prior_failure_chain": (
            artifact_pack.report_count == 9
            and artifact_pack.false_consensus_warning
            and artifact_pack.reactive_uncertainty_too_late
        ),
        "H2_a1_reduces_novel_transfer_loss_vs_a0": policies["A1-Artifact-Reflexive"]["summary"]["phase_loss"]["novel_transfer"] < policies["A0-Reactive"]["summary"]["phase_loss"]["novel_transfer"],
        "H3_a1_catches_at_least_one_a0_high_confidence_error": len(caught) > 0,
        "H4_meta_adversary_exploits_a1_rule": len(a1_meta_exploits) > 0,
        "H5_a2_reduces_meta_phase_loss_vs_a1": policies["A2-Second-Order"]["summary"]["phase_loss"]["meta_adversarial"] < policies["A1-Artifact-Reflexive"]["summary"]["phase_loss"]["meta_adversarial"],
        "H6_no_exact_candidate_reuse_from_prior_experiments": guard["candidate_hash_overlap_count"] == 0 and guard["all_event_ids_new"],
        "H7_a2_is_not_oracle": policies["A2-Second-Order"]["summary"]["total_loss"] > policies["Oracle"]["summary"]["total_loss"],
    }

    return {
        "schema": "scl-exp0010/v0.1",
        "experiment_id": "EXP-0010",
        "title": "Reflexive Epistemic Challenge / X-Order Cognitive Lift",
        "feature_ids": feature_ids,
        "config": asdict(cfg),
        "boundaries": {
            "artifact_exposure_is_experimental_factor": True,
            "current_truth_visible_to_non_oracle_policy": False,
            "shared_trust_memory_across_non_oracle_policies": True,
            "new_fixture_candidate_hash_overlap_required_zero": True,
            "phase_2_environment_conditioned_on_a1_rule": True,
            "oracle_is_evaluation_ceiling_only": True,
            "neural_retraining": False,
            "public_ai_board_write": False,
            "live_ctcl_call": False,
        },
        "artifact_pack": asdict(artifact_pack),
        "memorization_guard": guard,
        "events": [
            {k: v for k, v in event.items() if k not in {"candidate", "truth_before", "truth_after"}}
            for event in events
        ],
        "shared_trust_snapshot_hashes": [_snapshot_hash(snapshot) for snapshot in snapshots],
        "observable_meta_context": meta_contexts,
        "policies": policies,
        "a1_caught_a0_high_confidence_errors": caught,
        "a1_meta_exploits": a1_meta_exploits,
        "a2_meta_catches": a2_meta_catches,
        "hypotheses": hypotheses,
    }
