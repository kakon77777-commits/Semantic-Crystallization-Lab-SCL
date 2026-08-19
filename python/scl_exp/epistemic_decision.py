from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class EvidenceReport:
    source_agent: str
    origin_root: str
    stance: int  # +1 supports candidate, -1 opposes candidate

    def __post_init__(self) -> None:
        if self.stance not in {-1, 1}:
            raise ValueError("stance must be +1 or -1")


@dataclass(frozen=True)
class BeliefSummary:
    candidate_probability: float
    support_weight: float
    oppose_weight: float
    disagreement: float
    trust_uncertainty: float
    volatility: float
    scarcity: float
    uncertainty: float
    distinct_origins: int


@dataclass(frozen=True)
class DecisionConfig:
    base_accept_probability: float = 0.64
    risk_accept_weight: float = 0.12
    novelty_accept_weight: float = 2.0
    uncertainty_band_weight: float = 0.14
    max_seek: int = 2
    evidence_cost: float = 0.0008
    defer_cost: float = 0.0012
    seek_value_scale: float = 0.22
    seek_disagreement_weight: float = 0.16
    min_seek_signal: float = 0.045


@dataclass(frozen=True)
class EpistemicDecision:
    action: str
    reason: str
    candidate_probability: float
    uncertainty: float
    disagreement: float
    accept_threshold: float
    reject_threshold: float
    lower_bound: float
    upper_bound: float
    seek_signal: float


def _beta_variance(alpha: float, beta: float) -> float:
    a = max(1e-9, float(alpha))
    b = max(1e-9, float(beta))
    return float((a * b) / (((a + b) ** 2) * (a + b + 1.0)))


def aggregate_belief(evidence: list[EvidenceReport], trust_snapshot: dict[str, dict[str, float]]) -> BeliefSummary:
    roots: dict[str, EvidenceReport] = {}
    for report in evidence:
        roots.setdefault(str(report.origin_root), report)

    support = 0.0
    oppose = 0.0
    variances: list[float] = []
    volatilities: list[float] = []
    for root, report in sorted(roots.items()):
        row = trust_snapshot.get(root, {"mean": 0.5, "alpha": 2.0, "beta": 2.0, "volatility": 0.0})
        mean = min(1.0, max(0.0, float(row.get("mean", 0.5))))
        if report.stance > 0:
            support += mean
        else:
            oppose += mean
        variances.append(_beta_variance(float(row.get("alpha", 2.0)), float(row.get("beta", 2.0))))
        volatilities.append(min(1.0, max(0.0, float(row.get("volatility", 0.0)))))

    total = support + oppose
    probability = (0.5 + support) / (1.0 + total) if total > 0 else 0.5
    disagreement = 0.0 if total <= 0 else 1.0 - abs(support - oppose) / total
    trust_uncertainty = min(1.0, (sum(variances) / len(variances)) / 0.05) if variances else 1.0
    volatility = sum(volatilities) / len(volatilities) if volatilities else 0.0
    scarcity = 1.0 / (1.0 + len(roots))
    uncertainty = min(
        1.0,
        0.28 * scarcity + 0.28 * trust_uncertainty + 0.24 * volatility + 0.20 * disagreement,
    )
    return BeliefSummary(
        candidate_probability=float(probability),
        support_weight=float(support),
        oppose_weight=float(oppose),
        disagreement=float(disagreement),
        trust_uncertainty=float(trust_uncertainty),
        volatility=float(volatility),
        scarcity=float(scarcity),
        uncertainty=float(uncertainty),
        distinct_origins=len(roots),
    )


class _BaseDecisionPolicy:
    def __init__(self, config: DecisionConfig | None = None) -> None:
        self.config = config or DecisionConfig()

    def thresholds(self, *, risk: float, novelty_js: float) -> tuple[float, float]:
        r = min(1.0, max(0.0, float(risk)))
        n = max(0.0, float(novelty_js))
        accept = self.config.base_accept_probability + self.config.risk_accept_weight * r + self.config.novelty_accept_weight * n
        accept = min(0.90, max(0.55, accept))
        reject = 1.0 - accept
        return float(accept), float(reject)

    def _bounds(self, belief: BeliefSummary) -> tuple[float, float]:
        half = self.config.uncertainty_band_weight * belief.uncertainty
        return max(0.0, belief.candidate_probability - half), min(1.0, belief.candidate_probability + half)

    def _seek_signal(self, belief: BeliefSummary, risk: float) -> float:
        return float(
            self.config.seek_value_scale * min(1.0, max(0.0, float(risk))) * belief.uncertainty
            + self.config.seek_disagreement_weight * belief.disagreement
        )


class ScalarThresholdPolicy(_BaseDecisionPolicy):
    def decide(
        self,
        evidence: list[EvidenceReport],
        trust_snapshot: dict[str, dict[str, float]],
        *,
        risk: float,
        novelty_js: float,
        evidence_available: bool,
        seek_count: int,
    ) -> EpistemicDecision:
        belief = aggregate_belief(evidence, trust_snapshot)
        accept_t, reject_t = self.thresholds(risk=risk, novelty_js=novelty_js)
        accepted = belief.candidate_probability >= accept_t
        lower, upper = self._bounds(belief)
        return EpistemicDecision(
            "accept" if accepted else "reject",
            "scalar_threshold_accept" if accepted else "scalar_threshold_reject",
            belief.candidate_probability,
            belief.uncertainty,
            belief.disagreement,
            accept_t,
            reject_t,
            lower,
            upper,
            self._seek_signal(belief, risk),
        )


class PosteriorMeanActivePolicy(_BaseDecisionPolicy):
    def decide(
        self,
        evidence: list[EvidenceReport],
        trust_snapshot: dict[str, dict[str, float]],
        *,
        risk: float,
        novelty_js: float,
        evidence_available: bool,
        seek_count: int,
    ) -> EpistemicDecision:
        belief = aggregate_belief(evidence, trust_snapshot)
        accept_t, reject_t = self.thresholds(risk=risk, novelty_js=novelty_js)
        lower, upper = self._bounds(belief)
        signal = self._seek_signal(belief, risk)
        if belief.candidate_probability >= accept_t:
            action, reason = "accept", "posterior_mean_accept"
        elif belief.candidate_probability <= reject_t:
            action, reason = "reject", "posterior_mean_reject"
        elif evidence_available and seek_count < self.config.max_seek:
            action, reason = "seek_evidence", "posterior_mean_margin_uncertain"
        else:
            action, reason = "defer", "posterior_mean_defer"
        return EpistemicDecision(action, reason, belief.candidate_probability, belief.uncertainty, belief.disagreement, accept_t, reject_t, lower, upper, signal)


class BeliefStateDecisionPolicy(_BaseDecisionPolicy):
    def decide(
        self,
        evidence: list[EvidenceReport],
        trust_snapshot: dict[str, dict[str, float]],
        *,
        risk: float,
        novelty_js: float,
        evidence_available: bool,
        seek_count: int,
    ) -> EpistemicDecision:
        belief = aggregate_belief(evidence, trust_snapshot)
        accept_t, reject_t = self.thresholds(risk=risk, novelty_js=novelty_js)
        lower, upper = self._bounds(belief)
        signal = self._seek_signal(belief, risk)
        if lower >= accept_t:
            action, reason = "accept", "belief_lower_bound_accept"
        elif upper <= reject_t:
            action, reason = "reject", "belief_upper_bound_reject"
        elif evidence_available and seek_count < self.config.max_seek and signal >= self.config.min_seek_signal:
            action, reason = "seek_evidence", "belief_uncertainty_requests_evidence"
        else:
            action, reason = "defer", "belief_uncertainty_defer"
        return EpistemicDecision(action, reason, belief.candidate_probability, belief.uncertainty, belief.disagreement, accept_t, reject_t, lower, upper, signal)
