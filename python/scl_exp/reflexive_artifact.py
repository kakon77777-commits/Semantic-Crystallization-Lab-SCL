from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class ReflexiveRulePack:
    report_count: int
    report_sha256: dict[str, str]
    validation_sha256: dict[str, str]
    false_consensus_warning: bool
    structural_not_semantic_warning: bool
    static_quorum_tradeoff: bool
    reputation_hysteresis_warning: bool
    trust_state_decision_separation: bool
    reactive_uncertainty_too_late: bool
    prospective_challenge_threshold: float = 0.76
    risk_weight: float = 0.38
    novelty_weight: float = 5.5
    trusted_consensus_weight: float = 0.24
    low_disagreement_weight: float = 0.18
    hysteresis_weight: float = 0.18


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compile_reflexive_rule_pack(repo_root: Path) -> ReflexiveRulePack:
    repo_root = Path(repo_root)
    report_hashes: dict[str, str] = {}
    for index in range(1, 10):
        exp_id = f"EXP-{index:04d}"
        report = repo_root / f"experiments/{exp_id}/results/report.md"
        if not report.exists():
            raise FileNotFoundError(report)
        report_hashes[exp_id] = _sha256(report)

    validations: dict[str, dict] = {}
    validation_hashes: dict[str, str] = {}
    for index in range(4, 10):
        exp_id = f"EXP-{index:04d}"
        path = repo_root / f"VALIDATION_V{index:02d}.json"
        if not path.exists():
            raise FileNotFoundError(path)
        validations[exp_id] = _load_json(path)
        validation_hashes[exp_id] = _sha256(path)

    h4 = validations["EXP-0004"]["exp0004_hypotheses"]
    h5 = validations["EXP-0005"]["hypotheses"]
    h6 = validations["EXP-0006"]["hypotheses"]
    h7 = validations["EXP-0007"]["hypotheses"]
    h8 = validations["EXP-0008"]["hypotheses"]
    h9 = validations["EXP-0009"]["hypotheses"]

    false_consensus = bool(h4.get("E1_donor_induced_false_consensus_observed")) and bool(
        h5.get("H6_consensus_is_not_truth_signal")
    )
    structural_not_semantic = bool(h6.get("H6_structural_protocol_is_not_semantic_admissibility"))
    static_quorum_tradeoff = bool(h6.get("H5_static_quorum_tradeoff_exists"))
    reputation_hysteresis = bool(h7.get("H6_high_reputation_attack_can_still_bypass_learning"))
    trust_decision_separation = not bool(h8.get("H4_adaptive_risk_loss_beats_cumulative", True))
    reactive_too_late = (
        not bool(h9.get("H2_belief_state_reduces_total_loss_vs_scalar", True))
        and not bool(h9.get("H6_active_evidence_resolves_at_least_one_scalar_error", True))
    )

    return ReflexiveRulePack(
        report_count=len(report_hashes),
        report_sha256=report_hashes,
        validation_sha256=validation_hashes,
        false_consensus_warning=false_consensus,
        structural_not_semantic_warning=structural_not_semantic,
        static_quorum_tradeoff=static_quorum_tradeoff,
        reputation_hysteresis_warning=reputation_hysteresis,
        trust_state_decision_separation=trust_decision_separation,
        reactive_uncertainty_too_late=reactive_too_late,
    )
