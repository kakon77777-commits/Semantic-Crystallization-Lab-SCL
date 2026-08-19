# EXP-0009 — Uncertainty-Aware Epistemic Decision

This experiment isolates the decision layer above a fixed shared trust trajectory. Non-Oracle policies never see the current event truth label. `Seek Evidence` reveals one hidden report at a fixed cost; `Defer` waits for one-event-delayed validation before accepting/discarding the pending SCI update.

Policies: `Scalar-Threshold`, `Posterior-Mean`, `Belief-State`, and an evaluation-only `Oracle`.

Primary result: Belief-State uses richer uncertainty and reduces high-risk false accepts, but does not reduce total loss versus the scalar baseline in this fixture. See `results/report.md`.
