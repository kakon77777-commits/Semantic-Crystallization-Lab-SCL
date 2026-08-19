from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .adaptive_admission import AdmissionDecision


@dataclass(frozen=True)
class TrustDynamicsConfig:
    alpha0: float = 2.0
    beta0: float = 2.0
    fixed_decay: float = 0.90
    adaptive_base_decay: float = 0.96
    volatility_decay_strength: float = 0.38
    min_decay: float = 0.55
    max_decay: float = 0.995
    surprise_ema: float = 0.55
    betrayal_boost: float = 2.4
    recovery_boost: float = 1.8


class TrustDynamicsLedger:
    """Beta-style provenance trust with cumulative/fixed/adaptive memory dynamics."""

    MODES = {"cumulative", "fixed", "adaptive"}

    def __init__(self, mode: str, config: TrustDynamicsConfig | None = None) -> None:
        if mode not in self.MODES:
            raise ValueError(f"unknown trust dynamics mode: {mode}")
        self.mode = mode
        self.config = config or TrustDynamicsConfig()
        if self.config.alpha0 <= 0 or self.config.beta0 <= 0:
            raise ValueError("beta prior parameters must be positive")
        self._state: dict[str, dict[str, float]] = {}

    def _entry(self, root: str) -> dict[str, float]:
        key = str(root)
        if key not in self._state:
            self._state[key] = {"alpha": float(self.config.alpha0), "beta": float(self.config.beta0), "volatility": 0.0, "observations": 0.0}
        return self._state[key]

    def mean(self, root: str) -> float:
        row = self._entry(root)
        return float(row["alpha"] / (row["alpha"] + row["beta"]))

    def volatility(self, root: str) -> float:
        return float(self._entry(root)["volatility"])

    def _decay_factor(self, root: str) -> float:
        if self.mode == "cumulative":
            return 1.0
        if self.mode == "fixed":
            return float(self.config.fixed_decay)
        value = self.config.adaptive_base_decay - self.config.volatility_decay_strength * self.volatility(root)
        return float(min(self.config.max_decay, max(self.config.min_decay, value)))

    def advance(self) -> None:
        a0 = float(self.config.alpha0)
        b0 = float(self.config.beta0)
        for root, row in self._state.items():
            factor = self._decay_factor(root)
            if factor >= 1.0:
                continue
            row["alpha"] = a0 + (row["alpha"] - a0) * factor
            row["beta"] = b0 + (row["beta"] - b0) * factor
            if self.mode == "adaptive":
                row["volatility"] *= factor

    def observe(self, roots: list[str], *, genuine: bool, weight: float = 1.0) -> None:
        if weight <= 0:
            raise ValueError("feedback weight must be positive")
        label = 1.0 if genuine else 0.0
        for root in sorted({str(r) for r in roots if r}):
            row = self._entry(root)
            prior = self.mean(root)
            applied = float(weight)
            if self.mode == "adaptive":
                surprise = abs(label - prior)
                ema = float(self.config.surprise_ema)
                row["volatility"] = (1.0 - ema) * row["volatility"] + ema * surprise
                if genuine:
                    applied *= 1.0 + self.config.recovery_boost * (1.0 - prior)
                else:
                    applied *= 1.0 + self.config.betrayal_boost * prior
            row["alpha" if genuine else "beta"] += applied
            row["observations"] += 1.0

    def snapshot(self) -> dict[str, dict[str, float]]:
        return {root: {"mean": self.mean(root), "volatility": self.volatility(root), "alpha": float(row["alpha"]), "beta": float(row["beta"]), "observations": float(row["observations"])} for root, row in sorted(self._state.items())}


@dataclass(frozen=True)
class TrustAdmissionConfig:
    dynamics: TrustDynamicsConfig = TrustDynamicsConfig()
    min_distinct_origins: int = 2
    base_required_support: float = 0.85
    risk_weight: float = 0.50
    novelty_weight: float = 4.0
    recent_pollution_weight: float = 0.45
    recent_window: int = 4


class TrustDynamicsAdmissionPolicy:
    """Shared admission law with interchangeable trust-memory dynamics."""

    def __init__(self, mode: str, config: TrustAdmissionConfig | None = None) -> None:
        self.config = config or TrustAdmissionConfig()
        self.trust = TrustDynamicsLedger(mode, self.config.dynamics)
        self.mode = mode
        self._recent_truth: deque[bool] = deque(maxlen=self.config.recent_window)

    @property
    def recent_pollution_rate(self) -> float:
        if not self._recent_truth:
            return 0.0
        return float(sum(1 for genuine in self._recent_truth if not genuine) / len(self._recent_truth))

    def start_event(self) -> None:
        self.trust.advance()

    def observe_delayed_feedback(self, roots: list[str], *, genuine: bool, weight: float = 1.0) -> None:
        self.trust.observe(roots, genuine=genuine, weight=weight)
        self._recent_truth.append(bool(genuine))

    def required_support(self, *, risk: float, novelty_js: float) -> float:
        risk = min(1.0, max(0.0, float(risk)))
        novelty_js = max(0.0, float(novelty_js))
        return float(self.config.base_required_support + self.config.risk_weight * risk + self.config.novelty_weight * novelty_js + self.config.recent_pollution_weight * self.recent_pollution_rate)

    def decide(self, evidence: list[dict], *, risk: float, novelty_js: float) -> AdmissionDecision:
        roots = sorted({str(row.get("origin_root")) for row in evidence if row.get("origin_root")})
        agents = sorted({str(row.get("source_agent")) for row in evidence if row.get("source_agent")})
        required = self.required_support(risk=risk, novelty_js=novelty_js)
        reliabilities = [self.trust.mean(root) for root in roots]
        support = float(sum(reliabilities))
        mean_rel = float(sum(reliabilities) / len(reliabilities)) if reliabilities else 0.0
        if len(roots) < self.config.min_distinct_origins:
            return AdmissionDecision(False, "insufficient_independent_origins", len(roots), len(agents), support, required, mean_rel, self.recent_pollution_rate)
        accepted = support >= required
        return AdmissionDecision(accepted, f"accepted_{self.mode}_trust_dynamics" if accepted else "insufficient_trust_weighted_support", len(roots), len(agents), support, required, mean_rel, self.recent_pollution_rate)
