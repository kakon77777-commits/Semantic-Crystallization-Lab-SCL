import inspect

from python.scl_exp.epistemic_decision import (
    BeliefStateDecisionPolicy,
    DecisionConfig,
    EvidenceReport,
    PosteriorMeanActivePolicy,
    ScalarThresholdPolicy,
    aggregate_belief,
)


def _trust(mean, alpha=2.0, beta=2.0, volatility=0.0):
    return {"mean": mean, "alpha": alpha, "beta": beta, "volatility": volatility, "observations": alpha + beta - 4.0}


def test_aggregate_belief_tracks_disagreement_and_uncertainty():
    trust = {"A": _trust(0.8, alpha=8, beta=2, volatility=0.05), "B": _trust(0.8, alpha=8, beta=2, volatility=0.05)}
    aligned = aggregate_belief([EvidenceReport("a", "A", 1), EvidenceReport("b", "B", 1)], trust)
    split = aggregate_belief([EvidenceReport("a", "A", 1), EvidenceReport("b", "B", -1)], trust)
    assert aligned.candidate_probability > split.candidate_probability
    assert split.disagreement > aligned.disagreement
    assert split.uncertainty > aligned.uncertainty


def test_current_truth_is_not_an_admission_argument():
    for cls in (ScalarThresholdPolicy, PosteriorMeanActivePolicy, BeliefStateDecisionPolicy):
        params = inspect.signature(cls.decide).parameters
        assert "truth_effect" not in params
        assert "genuine" not in params
        assert "is_true" not in params


def test_belief_state_seeks_evidence_when_uncertain_and_risk_is_high():
    cfg = DecisionConfig(evidence_cost=0.0008); policy = BeliefStateDecisionPolicy(cfg)
    trust = {"D": _trust(0.55, alpha=2.2, beta=1.8, volatility=0.30), "E": _trust(0.55, alpha=2.2, beta=1.8, volatility=0.30)}
    decision = policy.decide([EvidenceReport("d", "D", 1), EvidenceReport("e", "E", -1)], trust, risk=0.85, novelty_js=0.012, evidence_available=True, seek_count=0)
    assert decision.action == "seek_evidence"
    assert decision.uncertainty > 0.4


def test_belief_state_can_accept_after_independent_corroboration():
    policy = BeliefStateDecisionPolicy(DecisionConfig())
    trust = {"A": _trust(0.82, alpha=9, beta=2, volatility=0.04), "D": _trust(0.72, alpha=6, beta=2.5, volatility=0.08), "F": _trust(0.78, alpha=7, beta=2, volatility=0.05)}
    evidence = [EvidenceReport("a", "A", 1), EvidenceReport("d", "D", 1), EvidenceReport("f", "F", 1)]
    decision = policy.decide(evidence, trust, risk=0.35, novelty_js=0.002, evidence_available=False, seek_count=1)
    assert decision.action == "accept"
    assert decision.candidate_probability > 0.7


def test_scalar_policy_never_requests_more_evidence():
    policy = ScalarThresholdPolicy(DecisionConfig()); trust = {"A": _trust(0.6), "B": _trust(0.6)}
    decision = policy.decide([EvidenceReport("a", "A", 1), EvidenceReport("b", "B", 1)], trust, risk=0.9, novelty_js=0.02, evidence_available=True, seek_count=0)
    assert decision.action in {"accept", "reject"}
