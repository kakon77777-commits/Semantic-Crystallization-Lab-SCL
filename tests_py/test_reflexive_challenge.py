from pathlib import Path

from python.scl_exp.epistemic_decision import EvidenceReport
from python.scl_exp.reflexive_artifact import compile_reflexive_rule_pack
from python.scl_exp.reflexive_challenge import (
    ReflexiveChallengePolicy,
    SecondOrderReflexivePolicy,
)


def _trusted_snapshot():
    return {
        "R1": {"mean": 0.86, "alpha": 7.0, "beta": 1.2, "volatility": 0.05},
        "R2": {"mean": 0.83, "alpha": 6.5, "beta": 1.3, "volatility": 0.04},
        "R3": {"mean": 0.82, "alpha": 6.2, "beta": 1.4, "volatility": 0.05},
        "R4": {"mean": 0.72, "alpha": 5.0, "beta": 2.0, "volatility": 0.08},
    }


def test_a1_prospectively_challenges_high_confidence_high_risk_consensus():
    repo = Path(__file__).resolve().parents[1]
    pack = compile_reflexive_rule_pack(repo)
    policy = ReflexiveChallengePolicy(pack)
    evidence = [
        EvidenceReport("a", "R1", 1),
        EvidenceReport("b", "R2", 1),
        EvidenceReport("c", "R3", 1),
    ]
    decision = policy.decide(
        evidence,
        _trusted_snapshot(),
        risk=0.92,
        novelty_js=0.021,
        evidence_available=True,
        seek_count=0,
    )
    assert decision.base_action == "accept"
    assert decision.action == "seek_evidence"
    assert decision.reflexive_order == 1
    assert decision.prospective_challenge


def test_a2_challenges_subthreshold_repeated_slow_roll_that_a1_accepts():
    repo = Path(__file__).resolve().parents[1]
    pack = compile_reflexive_rule_pack(repo)
    a1 = ReflexiveChallengePolicy(pack)
    a2 = SecondOrderReflexivePolicy(pack)
    evidence = [EvidenceReport("a", "R1", 1), EvidenceReport("b", "R2", 1), EvidenceReport("c", "R3", 1)]
    kwargs = dict(
        evidence=evidence,
        trust_snapshot=_trusted_snapshot(),
        risk=0.46,
        novelty_js=0.0015,
        evidence_available=True,
        seek_count=0,
    )
    first = a1.decide(**kwargs)
    assert first.action == "accept"
    second = a2.decide(
        **kwargs,
        coalition_signature="R1|R2|R3",
        coalition_streak=3,
        cumulative_drift_js=0.012,
    )
    assert second.a1_action == "accept"
    assert second.action == "seek_evidence"
    assert second.reflexive_order == 2
    assert second.second_order_challenge
