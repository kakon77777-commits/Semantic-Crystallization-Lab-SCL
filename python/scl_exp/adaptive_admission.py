from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class AdaptiveAdmissionConfig:
    alpha0: float = 2.0
    beta0: float = 2.0
    min_distinct_origins: int = 2
    base_required_support: float = 0.85
    risk_weight: float = 0.50
    novelty_weight: float = 4.0
    recent_pollution_weight: float = 0.45
    recent_window: int = 4


class RootTrustLedger:
    def __init__(self, *, alpha0: float = 2.0, beta0: float = 2.0) -> None:
        if alpha0 <= 0 or beta0 <= 0:
            raise ValueError("beta prior parameters must be positive")
        self.alpha0 = float(alpha0)
        self.beta0 = float(beta0)
        self._posterior: dict[str, list[float]] = {}

    def _params(self, root: str) -> list[float]:
        key = str(root)
        if key not in self._posterior:
            self._posterior[key] = [self.alpha0, self.beta0]
        return self._posterior[key]

    def mean(self, root: str) -> float:
        alpha, beta = self._params(root)
        return float(alpha / (alpha + beta))

    def observe(self, roots: list[str], *, genuine: bool, weight: float = 1.0) -> None:
        if weight <= 0:
            raise ValueError("feedback weight must be positive")
        for root in sorted({str(r) for r in roots if r}):
            params = self._params(root)
            params[0 if genuine else 1] += float(weight)

    def snapshot(self) -> dict[str, float]:
        return {root: self.mean(root) for root in sorted(self._posterior)}


@dataclass(frozen=True)
class AdmissionDecision:
    accepted: bool
    reason: str
    distinct_origins: int
    distinct_agents: int
    effective_support: float
    required_support: float
    mean_reliability: float
    recent_pollution_rate: float


class AdaptiveAdmissionPolicy:
    def __init__(self, config: AdaptiveAdmissionConfig | None = None) -> None:
        self.config = config or AdaptiveAdmissionConfig()
        self.trust = RootTrustLedger(alpha0=self.config.alpha0, beta0=self.config.beta0)
        self._recent_truth: deque[bool] = deque(maxlen=self.config.recent_window)

    @property
    def recent_pollution_rate(self) -> float:
        if not self._recent_truth:
            return 0.0
        return float(sum(1 for genuine in self._recent_truth if not genuine) / len(self._recent_truth))

    def required_support(self, *, risk: float, novelty_js: float) -> float:
        risk = min(1.0, max(0.0, float(risk)))
        novelty_js = max(0.0, float(novelty_js))
        return float(
            self.config.base_required_support
            + self.config.risk_weight * risk
            + self.config.novelty_weight * novelty_js
            + self.config.recent_pollution_weight * self.recent_pollution_rate
        )

    def observe_feedback(self, roots: list[str], *, genuine: bool, weight: float = 1.0) -> None:
        self.trust.observe(roots, genuine=genuine, weight=weight)
        self._recent_truth.append(bool(genuine))

    def decide(self, evidence: list[dict], *, risk: float, novelty_js: float) -> AdmissionDecision:
        roots = sorted({str(row.get("origin_root")) for row in evidence if row.get("origin_root")})
        agents = sorted({str(row.get("source_agent")) for row in evidence if row.get("source_agent")})
        required = self.required_support(risk=risk, novelty_js=novelty_js)
        reliabilities = [self.trust.mean(root) for root in roots]
        support = float(sum(reliabilities))
        mean_rel = float(sum(reliabilities) / len(reliabilities)) if reliabilities else 0.0

        if len(roots) < self.config.min_distinct_origins:
            return AdmissionDecision(
                False,
                "insufficient_independent_origins",
                len(roots),
                len(agents),
                support,
                required,
                mean_rel,
                self.recent_pollution_rate,
            )
        accepted = support >= required
        return AdmissionDecision(
            accepted,
            "accepted_learned_adaptive" if accepted else "insufficient_trust_weighted_support",
            len(roots),
            len(agents),
            support,
            required,
            mean_rel,
            self.recent_pollution_rate,
        )
