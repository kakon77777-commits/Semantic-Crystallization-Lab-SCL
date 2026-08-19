from __future__ import annotations

from dataclasses import dataclass

from .epistemic_decision import BeliefStateDecisionPolicy, EvidenceReport, aggregate_belief
from .reflexive_artifact import ReflexiveRulePack


@dataclass(frozen=True)
class ReflexiveDecision:
    action: str
    reason: str
    base_action: str
    reflexive_order: int
    prospective_challenge: bool
    second_order_challenge: bool
    challenge_score: float
    a1_action: str | None
    candidate_probability: float
    uncertainty: float
    disagreement: float


class ReflexiveChallengePolicy:
    """Order-1 policy: use prior experiment artifacts to challenge confident accepts.

    The base decision remains the EXP-0009 Belief-State policy. The artifact pack
    only adds a *prospective* challenge gate for failure signatures that earlier
    experiments explicitly recorded (false consensus, reputation hysteresis and
    reactive-uncertainty latency).
    """

    def __init__(self, rule_pack: ReflexiveRulePack) -> None:
        self.rule_pack = rule_pack
        self.base = BeliefStateDecisionPolicy()

    def challenge_score(
        self,
        evidence: list[EvidenceReport],
        trust_snapshot: dict[str, dict[str, float]],
        *,
        risk: float,
        novelty_js: float,
    ) -> float:
        belief = aggregate_belief(evidence, trust_snapshot)
        roots = sorted({report.origin_root for report in evidence})
        means = [float(trust_snapshot.get(root, {}).get("mean", 0.5)) for root in roots]
        mean_trust = sum(means) / len(means) if means else 0.5
        trusted_consensus = mean_trust if len(roots) >= 2 and belief.disagreement <= 0.18 else 0.0
        low_disagreement = 1.0 - belief.disagreement
        hysteresis = 1.0 if self.rule_pack.reputation_hysteresis_warning and mean_trust >= 0.72 else 0.0
        return float(
            self.rule_pack.risk_weight * max(0.0, min(1.0, risk))
            + self.rule_pack.novelty_weight * max(0.0, novelty_js)
            + self.rule_pack.trusted_consensus_weight * trusted_consensus
            + self.rule_pack.low_disagreement_weight * low_disagreement
            + self.rule_pack.hysteresis_weight * hysteresis
        )

    def decide(
        self,
        evidence: list[EvidenceReport],
        trust_snapshot: dict[str, dict[str, float]],
        *,
        risk: float,
        novelty_js: float,
        evidence_available: bool,
        seek_count: int,
    ) -> ReflexiveDecision:
        base = self.base.decide(
            evidence,
            trust_snapshot,
            risk=risk,
            novelty_js=novelty_js,
            evidence_available=evidence_available,
            seek_count=seek_count,
        )
        score = self.challenge_score(evidence, trust_snapshot, risk=risk, novelty_js=novelty_js)
        challenge = base.action == "accept" and score >= self.rule_pack.prospective_challenge_threshold
        if challenge:
            action = "seek_evidence" if evidence_available and seek_count < self.base.config.max_seek else "defer"
            reason = "artifact_conditioned_prospective_challenge"
        else:
            action = base.action
            reason = base.reason
        return ReflexiveDecision(
            action=action,
            reason=reason,
            base_action=base.action,
            reflexive_order=1,
            prospective_challenge=challenge,
            second_order_challenge=False,
            challenge_score=score,
            a1_action=None,
            candidate_probability=base.candidate_probability,
            uncertainty=base.uncertainty,
            disagreement=base.disagreement,
        )


class SecondOrderReflexivePolicy:
    """Order-2 policy: model how an adversary can target the order-1 rule itself."""

    def __init__(self, rule_pack: ReflexiveRulePack) -> None:
        self.rule_pack = rule_pack
        self.a1 = ReflexiveChallengePolicy(rule_pack)
        self.slow_roll_drift_threshold = 0.010
        self.min_coalition_streak = 2
        self.boundary_margin = 0.08

    def decide(
        self,
        evidence: list[EvidenceReport],
        trust_snapshot: dict[str, dict[str, float]],
        *,
        risk: float,
        novelty_js: float,
        evidence_available: bool,
        seek_count: int,
        coalition_signature: str,
        coalition_streak: int,
        cumulative_drift_js: float,
    ) -> ReflexiveDecision:
        first = self.a1.decide(
            evidence,
            trust_snapshot,
            risk=risk,
            novelty_js=novelty_js,
            evidence_available=evidence_available,
            seek_count=seek_count,
        )
        near_boundary = (
            first.challenge_score < self.rule_pack.prospective_challenge_threshold
            and first.challenge_score >= self.rule_pack.prospective_challenge_threshold - self.boundary_margin
        )
        repeated_slow_roll = coalition_streak >= self.min_coalition_streak and cumulative_drift_js >= self.slow_roll_drift_threshold
        boundary_skimming = near_boundary and coalition_streak >= self.min_coalition_streak and risk >= 0.40
        second_order = first.action == "accept" and (repeated_slow_roll or boundary_skimming)
        if second_order:
            action = "seek_evidence" if evidence_available and seek_count < self.a1.base.config.max_seek else "defer"
            reason = "second_order_challenge_of_challenge_rule"
        else:
            action = first.action
            reason = first.reason
        return ReflexiveDecision(
            action=action,
            reason=reason,
            base_action=first.base_action,
            reflexive_order=2,
            prospective_challenge=first.prospective_challenge,
            second_order_challenge=second_order,
            challenge_score=first.challenge_score,
            a1_action=first.action,
            candidate_probability=first.candidate_probability,
            uncertainty=first.uncertainty,
            disagreement=first.disagreement,
        )
